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
                        err_invalid_none, err_process_kill, err_unexpected,
                        extender_blocking_start, extender_blocking_stop,
                        extender_pre_connect, extender_session_start,
                        extender_session_stop, support_process_started,
                        support_process_stopped, support_started, support_stopped)
from ._profiles import ConnectionProfile, TunnelDirection
from ._ssh import SSHClient, AutoRejectPolicy, PromptUserPolicy


class SupportEntity (object):
    """
    Represents either the entity receiving support or the entity giving support.

    The `ConnectionProfile` in use dictates the specifics of any given session,
    however regardless of the configuration the general process is as follows:

    One `SupportEntity` initiates the process by creating an SSH reverse tunnel
    from a random server port to their pre-configured local port, specifically
    the local port used by their desktop sharing program. The allocated server
    port is then transmitted, by whatever medium, to the other `SupportEntity`
    for use as their "access code". The access code is then used by the other
    entity to create an SSH forward tunnel from the pre-configured local port
    of their desktop sharing program to the "access code" port on the server,
    which establishes a communications tunnel between the two entities using
    the server as an intermediary.

    Pseudo examples below, see the yarest.gui source for a working example.

    >>> from yarest import ConnectionProfile, SupportEntity
    >>>
    >>> profiles = ConnectionProfile.read_from_file(your_config_file_from_somewhere)
    >>>
    >>> supportconsumer = SupportEntity(profiles[0])
    >>> supportconsumer.connect(your_password_from_somewhere)
    >>>
    >>> access_code = supportconsumer.start_session()
    >>> send_access_code_to_your_supportprovider(access_code)
    >>>
    >>> while not time_to_stop:
    >>>     continue
    >>>
    >>> supportconsumer.stop_session()

    >>> from yarest import ConnectionProfile, SupportEntity
    >>>
    >>> profiles = ConnectionProfile.read_from_file(your_config_file_from_somewhere)
    >>>
    >>> supportprovider = SupportEntity(profiles[0])
    >>> supportprovider.connect(your_password_from_somewhere)
    >>>
    >>> access_code = access_code_received_from_your_supportconsumer()
    >>> supportprovider.start_session(access_code)
    >>>
    >>> user_clicked_disconnect = False
    >>> while not user_clicked_disconnect:
    >>>     continue
    >>>
    >>> supportprovider.stop_session()
    """
    def __init__(self, profile, extender=None, logger=None, callback=None):
        """
        Initializes an instance of the SupportEntity class.

        Args:
            profile (ConnectionProfile)  : the connection profile to use.

        Kwargs:
            extender (SupportExtender)   : the extender instance to use, default: None.
            logger (logging.Logger)      : the logger instance to use, default: None.
            callback (callable)          : the callback used for an unknown SSH host prompt, default: None.

        Raises:
            ValueError                   : if `profile` is None or any contained value is invalid.
            RuntimeError                 : if `callback` is None and `profile.ssh_allow_unknown` is True.
            IOError                      : if `profile.log_file` is specified but not writable.

        *NOTES*

        If `logger` is None then the logger used comes from the `SSHClient` used
        internally, its logger will be created using the `profile.log_file` with
        utf-8 encoding if `profile.log_file` is specified, otherwise a temp file
        gets used as described in the documentation of `SSHClient.get_logger()`.
        """
        self.logger = logger
        self.profile = profile
        self.remoteport = None
        self.sshclient = None
        self._extender = extender
        self._extender_thread = None
        self._unknownhost = None
        self._process = None

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

    def connect(self, password=None):
        """
        Runs the `SupportExtender.on_pre_connect()` and establishes the SSH session.

        Args:
            password (str)          : the password to login on the server or decrypt the private key, default: None.

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
            self._extender.on_pre_connect(self)
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
                                   ssh_compression=self.profile.ssh_compression,
                                   ssh_allow_agent=self.profile.ssh_allow_agent,
                                   ssh_search_keys=self.profile.ssh_search_keys)
        except (ConnectionException, SSHException):
            raise
        except:
            self.logger.exception(err_unexpected)
            raise

    def start_session(self, access_code=None):
        """
        Creates the appropriate SSH tunnel, starts the remote support process,
        if applicable, and then runs the `SupportExtender.on_session_start()`.

        When the current `SupportEntity.profile` has a `ConnectionProfile.support_tunnel`
        value of "forward" the `access_code` is required and this method returns the same
        value. When the `ConnectionProfile.support_tunnel` is "reverse" the `access_code`
        parameter gets ignored and this method returns the server port number allocated.

        Args:
            access_code (int)         : the remote port to forward the local support port to, default: None.

        Returns: (int)
            The access code for the other entity to use if `ConnectionProfile.support_tunnel` is "reverse",
            or the same `access_code` value supplied when `ConnectionProfile.support_tunnel` is "forward".

        Raises:
            ValueError                : if `access_code` is None and `ConnectionProfile.support_tunnel` is "forward".
            InvalidOperationException : if the SSH session is not connected.
            SSHException              : if `TunnelDirection.Reverse` is in use and the tunnelling request is rejected by the server.
        """
        if self.profile.support_tunnel == TunnelDirection.Forward:
            if access_code is None:
                raise ValueError(err_invalid_none % ("access_code"))
            try:
                self.sshclient.create_forward_tunnel(self.profile.support_port,
                                                     access_code)
                self.remoteport = access_code
                self._start_support_process()
            except (InvalidOperationException):
                raise
            except:
                self.logger.exception(err_unexpected)
                raise
        else:
            try:
                self.remoteport = self.sshclient.create_reverse_tunnel(self.profile.support_port)
                self._start_support_process()
            except (InvalidOperationException, SSHException):
                raise
            except:
                self.logger.exception(err_unexpected)
                raise

        self._spawn_on_session_start()
        return self.remoteport

    def stop_session(self):
        """
        Waits for the `SupportExtender.on_session_start()` thread to complete,
        if necessary, terminates the support process when applicable, runs the
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

        if self._process is not None:
            try:
                self._process.kill()
            except NoSuchProcess:
                pass
            except:
                self.logger.exception(err_process_kill)
            self.logger.info(support_process_stopped)
            self._process = None
        elif self.profile.support_exec is None and run_extender:
            self.logger.info(support_stopped)

        if run_extender:
            self.logger.info(extender_session_stop)
            try:
                self._extender.on_session_stop(self)
            except:
                self.logger.exception(err_extender_session_stop)

        if self.sshclient.is_connected():
            self.remoteport = None
            self.sshclient.disconnect()

    def _run_on_session_start(self):
        self.logger.info(extender_session_start)
        try:
            self._extender.on_session_start(self)
        except:
            self.logger.exception(err_extender_session_start)

    def _spawn_on_session_start(self):
        self._extender_thread = Thread(target=self._run_on_session_start)
        self._extender_thread.setDaemon(True)
        self._extender_thread.start()

    def _start_support_process(self):
        if self.profile.support_exec is not None:
            if self.profile.support_args is None:
                args = []
            elif "%d" in self.profile.support_args:
                #Popen doesn't like unicode so we always encode to utf-8
                args_str = self.profile.support_args.encode(UTF8)
                args = split(args_str.replace("%d", str(self.profile.support_port)))
            else:
                args = split(self.profile.support_args.encode(UTF8))

            args.insert(0, self.profile.support_exec)
            self._process = Popen(args)
            self.logger.info(support_process_started %
                             (self._process.name, self._process.pid))
        else:
            self.logger.info(support_started)


class SupportExtender (object):
    """
    Defines the interface used to extend support sessions with custom logic.

    Inherit from this class and pass an instance to the `SupportEntity`
    constructor to implement your own logic during the session process.

    The `on_pre_connect()` and `on_session_stop()` methods are both
    invoked synchronously and will block until you release control.

    The `on_session_start()` method runs in its own separate thread and will
    not block unless it hasn't completed by the time that a session stop is
    requested, in which case the thread blocks indefinitely until it joins.
    """
    def on_pre_connect(self, entity):
        """
        Called before a support session is connected.

        Args:
            entity (SupportEntity)     : the active support entity.

        *NOTES*

        An exception raised here will be logged by the `SupportEntity`,
        the connection process will be terminated and the error message
        may be displayed to the user.

        Implementors must cache the `profile` if it is desired
        in either `on_session_start()` or `on_session_stop()`.
        """
        pass

    def on_session_start(self, entity):
        """
        Called when a support session is started.

        Args:
            entity (SupportEntity)     : the active support entity.

        *NOTES*

        This method is called directly after the support process is started.

        An exception raised here will be logged by the `SupportEntity`,
        the error message will not be displayed to the user and the
        underlying remote support process will not be interrupted.
        """
        pass

    def on_session_stop(self, entity):
        """
        Called when a support session is stopped.

        Args:
            entity (SupportEntity)     : the active support entity.

        *NOTES*

        This method is called directly after the support process is stopped,
        but before the underlying SSH session has been disconnected.

        An exception raised here will be logged by the `SupportEntity`
        and the error message will not be displayed to the user.
        """
        pass
