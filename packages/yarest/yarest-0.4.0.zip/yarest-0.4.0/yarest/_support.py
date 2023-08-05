## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

from psutil import Popen, NoSuchProcess
from shlex import split
from threading import Thread

from ._constants import UTF8
from ._exceptions import (ConnectionException, InvalidOperationException,
                          SSHException)
from ._messages import (connectionprofile_used, err_extender_pre_connect,
                        err_extender_session_start, err_extender_session_stop,
                        err_invalid_direction, err_invalid_none,
                        err_unexpected, err_vnc_kill, extender_blocking_start,
                        extender_blocking_stop, extender_pre_connect,
                        extender_session_start, extender_session_stop,
                        vnc_started, vnc_terminated)
from ._profiles import ConnectionProfile
from ._ssh import SSHClient, AutoRejectPolicy, PromptUserPolicy


class SupportDirection (object):
    """The defined support tunnel directions."""
    Forward = "Forward"
    Reverse = "Reverse"


class SupportRole (object):
    """The defined support session roles."""
    Consumer = "Consumer"
    Provider = "Provider"


class SupportBase (object):
    """
    Base class for both the `SupportConsumer` and `SupportProvider`.
    """
    def __init__(self, profile, extender=None, logger=None,
                 callback=None, direction=SupportDirection.Forward):
        """
        Initializes an instance of the SupportBase class.

        Args:
            profile (ConnectionProfile)  : the connection profile to use.

        Kwargs:
            extender (SupportExtender)   : the extender instance to use, default: None.
            logger (logging.Logger)      : the logger instance to use, default: None.
            callback (callable)          : the callback used for an unknown SSH host prompt, default: None.
            direction (SupportDirection) : the support tunnel direction to use, default: SupportDirection.Forward.

        Raises:
            ValueError                   : if `profile` is None or any contained value is invalid.
            RuntimeError                 : if `callback` is None and `profile.ssh_allow_unknown` is True.
            RuntimeError                 : if `direction` is not `SupportDirection.Forward` or `SupportDirection.Reverse`.
            IOError                      : if `profile.log_file` is specified but not writable.

        *NOTES*

        If `logger` is None then the logger used comes from the `SSHClient` used
        internally, its logger will be created using the `profile.log_file` with
        utf-8 encoding if `profile.log_file` is specified, otherwise a temp file
        gets used as described in the documentation of `SSHClient.get_logger()`.
        """
        self.logger = logger
        self.profile = profile
        self.sshclient = None
        self._direction = direction
        self._extender = extender
        self._extender_thread = None
        self._unknownhost = None
        self._vncprocess = None

        if self._direction != SupportDirection.Forward and \
           self._direction != SupportDirection.Reverse:
            raise RuntimeError(err_invalid_direction)

        ConnectionProfile.prevalidate(self.profile, True)

        if self._extender is None:
            self._extender = SupportExtender()

        self.sshclient = SSHClient()
        if self.profile.log_file is not None:
            self.sshclient.init_logger(self.profile.name,
                                       self.profile.log_file)
        if self.logger is None:
            self.logger = self.sshclient.get_logger()
        elif self.sshclient.logger is None:
            self.sshclient.logger = self.logger

        if profile.ssh_allow_unknown:
            if callback is None:
                raise RuntimeError(err_invalid_none % ("callback"))
            self._unknownhost = PromptUserPolicy(self.sshclient.get_logger(),
                                                 self.profile.ssh_hostkeys,
                                                 callback)
        else:
            self._unknownhost = AutoRejectPolicy(self.sshclient.get_logger())

    def connect(self, password):
        """
        Runs the `SupportExtender.on_pre_connect()` and establishes the SSH session.

        Args:
            password (str)          : the password used to login on the server or decrypt the client's private key.

        Raises:
            KeyfileException        : if either `profile.ssh_hostkeys` or `profile.ssh_clientkeys` is given but not accessible.
            ConnectionException     : if there is a problem connecting to the `profile.ssh_host`.
            HostKeyException        : if the returned server host key doesn't match the locally stored host key.
            AutoRejectedHostKey     : if `profile.ssh_allow_unknown` is False and no local host key is available.
            UserRejectedHostKey     : if `profile.ssh_allow_unknown` is True and the user rejects the host key.
            AuthenticationException : if client authentication fails for any reason.
            SSHException            : if there is any other error establishing the session.

        *NOTES*

        This method can throw numerous exceptions, including custom exceptions
        from the extender, any exception thrown will be logged then re-raised.
        """
        self.logger.info(extender_pre_connect)
        try:
            self._extender.on_pre_connect(self.logger, self.profile,
                                          self._get_role(), self._direction)
        except:
            self.logger.exception(err_extender_pre_connect)
            raise

        self.logger.info(connectionprofile_used % (self.profile))
        try:
            self.sshclient.connect(host=self.profile.ssh_server,
                                   host_port=self.profile.ssh_port,
                                   client_username=self.profile.ssh_username,
                                   host_keyfile=self.profile.ssh_hostkeys,
                                   client_keyfile=self.profile.ssh_clientkeys,
                                   client_password=password,
                                   missing_hostkey_policy=self._unknownhost,
                                   tcp_timeout=self.profile.tcp_timeout,
                                   ssh_compression=self.profile.ssh_compression)
        except (ConnectionException, SSHException):
            raise
        except:
            self.logger.exception(err_unexpected)
            raise

    def start_session(self, access_code=None):
        """
        Creates the required SSH tunnel, starts the VNC process
        and then runs the `SupportExtender.on_session_start()`.

        Args:
            access_code (int)         : the remote port to forward the local VNC port to, default: None.

        Returns: (int)
            The access code for the other party to use when `SupportDirection.Reverse` is in use.

        Raises:
            TypeError                 : if `access_code` is None and `SupportDirection.Forward` is in use.
            InvalidOperationException : if the SSH session is not connected.
            SSHException              : if `SupportDirection.Reverse` is in use and the tunnel request is rejected by the server.
        """
        if self._direction == SupportDirection.Forward:
            try:
                self.sshclient.create_forward_tunnel(self.profile.vnc_port,
                                                     access_code)
                self._spawn_vnc()
            except (InvalidOperationException, TypeError):
                raise
            except:
                self.logger.exception(err_unexpected)
                raise
            self._spawn_on_session_start()
        else:
            try:
                port = self.sshclient.create_reverse_tunnel(self.profile.vnc_port)
                self._spawn_vnc()
            except (InvalidOperationException, SSHException):
                raise
            except:
                self.logger.exception(err_unexpected)
                raise
            self._spawn_on_session_start()
            return port

    def stop_session(self):
        """
        Waits for the `SupportExtender.on_session_start()` thread to finish,
        if found to be necessary, then terminates the VNC process, runs the
        `SupportExtender.on_session_stop()` and disconnects the SSH session.

        This method can be called to cleanup regardless of state, it determines
        what needs to be terminated/disconnected and whether `SupportExtender`
        calls are actually relevant. Once this method completes, the instance
        will be at the exact same state it was directly after initialization.
        """
        run_extender = False
        if self._extender_thread is not None:
            if self._extender_thread.is_alive():
                self.logger.info(extender_blocking_start)
                self._extender_thread.join()
                self.logger.info(extender_blocking_stop)
            self._extender_thread = None
            run_extender = True

        if self._vncprocess is not None:
            try:
                self._vncprocess.kill()
            except NoSuchProcess:
                pass
            except:
                self.logger.exception(err_vnc_kill)
            self.logger.info(vnc_terminated %
                             (self._vncprocess.name, self._vncprocess.pid))
            self._vncprocess = None

        if run_extender:
            self.logger.info(extender_session_stop)
            try:
                self._extender.on_session_stop(self.logger, self.sshclient)
            except:
                self.logger.exception(err_extender_session_stop)

        if self.sshclient.is_connected():
            self.sshclient.disconnect()

    def _run_on_session_start(self):
        self.logger.info(extender_session_start)
        try:
            self._extender.on_session_start(self.logger, self.sshclient)
        except:
            self.logger.exception(err_extender_session_start)

    def _spawn_on_session_start(self):
        self._extender_thread = Thread(target=self._run_on_session_start)
        self._extender_thread.setDaemon(True)
        self._extender_thread.start()

    def _spawn_vnc(self):
        if self.profile.vnc_args is None:
            args = []
        elif "%d" in self.profile.vnc_args:
            #Popen doesn't like unicode so we always encode to utf-8
            args_str = self.profile.vnc_args.encode(UTF8)
            args = split(args_str.replace("%d", str(self.profile.vnc_port)))
        else:
            args = split(self.profile.vnc_args.encode(UTF8))
        args.insert(0, self.profile.vnc_exec)
        self._vncprocess = Popen(args)
        self.logger.info(vnc_started %
                         (self._vncprocess.name, self._vncprocess.pid))


class SupportConsumer (SupportBase):
    """
    Represents a remote support consumer.

    When instantiated with SupportDirection.Forward (the default):

    A consumer session creates an SSH forward tunnel from the local VNC port
    to a specific port on the remote server, that specific port we label the
    "access code". When the tunnel is established a VNC server is started in
    reverse connection mode so that we connect to our `SupportProvider` that
    is already listening at the other end of the tunnel.

    When instantiated with SupportDirection.Reverse:

    A consumer session creates an SSH reverse tunnel from a random server port
    to the local VNC port and returns the server port in use so that it can be
    transmitted, by whatever medium, to the `SupportProvider` for use as their
    "access code". When the tunnel gets established a VNC server is started in
    listen mode and we simply await the connection request from our provider.

    Pseudo example below, see the yarest.gui source for a working example.

    >>> from yarest import ConnectionProfile, SupportConsumer
    >>>
    >>> profiles = ConnectionProfile.read_from_file(your_config_file)
    >>>
    >>> consumer = SupportConsumer(profiles[0])
    >>> consumer.connect(get_password_from_somewhere())
    >>> consumer.start_session(get_access_code_from_provider())
    >>>
    >>> while not time_to_stop:
    >>>     continue
    >>>
    >>> consumer.stop_session()
    """
    def __init__(self, profile, extender=None, logger=None,
                 callback=None, direction=SupportDirection.Forward):
        """
        Creates a new SupportConsumer object.

        Args:
            profile (ConnectionProfile)  : the connection profile to use.

        Kwargs:
            extender (SupportExtender)   : the extender instance to use, default: None.
            logger (logging.Logger)      : the logger instance to use, default: None.
            callback (callable)          : the callback used for an unknown SSH host prompt, default: None.
            direction (SupportDirection) : the support tunnel direction to use, default: SupportDirection.Forward.

        Raises:
            ValueError                   : if `profile` is None or otherwise not valid.
            RuntimeError                 : if `callback` is None and `profile.ssh_allow_unknown` is True.
            RuntimeError                 : if `direction` is not `SupportDirection.Forward` or `SupportDirection.Reverse`.
            IOError                      : if `profile.log_file` is specified but not writable.

        *NOTES*

        If `logger` is None then the logger used comes from the `SSHClient` used
        internally, its logger will be created using the `profile.log_file` with
        utf-8 encoding if `profile.log_file` is specified, otherwise a temp file
        gets used as described in the documentation of `SSHClient.get_logger()`.
        """
        SupportBase.__init__(self, profile, extender,
                             logger, callback, direction)

    def _get_role(self):
        return SupportRole.Consumer


class SupportProvider (SupportBase):
    """
    Represents a remote support provider.

    When instantiated with SupportDirection.Reverse (the default):

    A provider session creates an SSH reverse tunnel from a random server port
    to the local VNC port and returns the server port in use so that it can be
    transmitted, by whatever medium, to the `SupportConsumer` for use as their
    "access code". When the tunnel gets established a VNC client is started in
    listen mode and we simply await the connection request from our consumer.

    When instantiated with SupportDirection.Forward:

    A provider session creates an SSH forward tunnel from the local VNC port
    to a specific port on the remote server, that specific port we label the
    "access code". When the tunnel is established a VNC client is started in
    regular connection mode so that we connect to our `SupportConsumer` that
    is already listening at the other end of the tunnel.

    Pseudo example below, see the yarest.gui source for a working example.

    >>> from yarest import ConnectionProfile, SupportProvider
    >>>
    >>> profiles = ConnectionProfile.read_from_file(your_config_file)
    >>>
    >>> provider = SupportProvider(profiles[0])
    >>> provider.connect(get_password_from_somewhere())
    >>> consumer_access_code = provider.start_session()
    >>> print consumer_access_code
    >>>
    >>> while not time_to_stop:
    >>>     continue
    >>>
    >>> provider.stop_session()
    """
    def __init__(self, profile, extender=None, logger=None,
                 callback=None, direction=SupportDirection.Reverse):
        """
        Creates a new SupportProvider object.

        Args:
            profile (ConnectionProfile)  : the connection profile to use.

        Kwargs:
            extender (SupportExtender)   : the extender instance to use, default: None.
            logger (logging.Logger)      : the logger instance to use, default: None.
            callback (callable)          : the callback used for an unknown SSH host prompt, default: None.
            direction (SupportDirection) : the support tunnel direction to use, default: SupportDirection.Reverse.

        Raises:
            ValueError                   : if `profile` is None or otherwise not valid.
            RuntimeError                 : if `callback` is None and `profile.ssh_allow_unknown` is True.
            RuntimeError                 : if `direction` is not `SupportDirection.Forward` or `SupportDirection.Reverse`.
            IOError                      : if `profile.log_file` is specified but not writable.

        *NOTES*

        If `logger` is None then the logger used comes from the `SSHClient` used
        internally, its logger will be created using the `profile.log_file` with
        utf-8 encoding if `profile.log_file` is specified, otherwise a temp file
        gets used as described in the documentation of `SSHClient.get_logger()`.
        """
        SupportBase.__init__(self, profile, extender,
                             logger, callback, direction)

    def _get_role(self):
        return SupportRole.Provider


class SupportExtender (object):
    """
    Defines the interface used to extend support sessions with custom logic.

    Inherit from this class and pass an instance to either the `SupportConsumer`
    or `SupportProvider` to implement your own logic during the session process.

    The `on_pre_connect()` and `on_session_stop()` methods are both
    invoked synchronously and will block until you release control.

    The `on_session_start()` method runs in its own separate thread and will
    not block unless it hasn't completed by the time that a session stop is
    requested, in which case the thread blocks indefinitely until it joins.
    """
    def on_pre_connect(self, logger, profile, role, direction):
        """
        Called before a support session is connected.

        Args:
            logger (logging.Logger)      : the logger being used.
            profile (ConnectionProfile)  : the connection profile about to be used.
            role (SupportRole)           : SupportRole.Consumer or SupportRole.Provider.
            direction (SupportDirection) : SupportDirection.Forward or SupportDirection.Reverse.

        *NOTES*

        An exception raised here will be logged by the `SupportConsumer` or
        `SupportProvider`, the error message may be displayed to the user,
        and the connection process will be terminated.

        Implementors must cache the `profile`, `role` and `direction` if they
        are needed in either the `on_session_start()` or `on_session_stop()`.
        """
        pass

    def on_session_start(self, logger, sshclient):
        """
        Called when a support session is started.

        Args:
            logger (logging.Logger)     : the logger being used.
            sshclient (SSHClient)       : the SSHClient being used.

        *NOTES*

        This method is called directly after the VNC process is started.

        An exception raised here will be logged by the `SupportConsumer` or
        `SupportProvider`, however the error message will not be displayed,
        and the underlying support process will not be interrupted.
        """
        pass

    def on_session_stop(self, logger, sshclient):
        """
        Called when a support session is stopped.

        Args:
            logger (logging.Logger)     : the logger being used.
            sshclient (SSHClient)       : the SSHClient being used.

        *NOTES*

        This method is called directly after the VNC process is
        terminated, but before the SSH session is disconnected.

        An exception raised here will be logged by the `SupportConsumer` or
        `SupportProvider`, however the error message will not be displayed.
        """
        pass
