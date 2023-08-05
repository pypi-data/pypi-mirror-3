## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

import errno, os, select, socket, sys

from binascii import hexlify
from logging import FileHandler, Formatter, getLogger
from SocketServer import BaseRequestHandler, ThreadingTCPServer
from threading import Thread, Lock, RLock

from paramiko import (AutoAddPolicy, MissingHostKeyPolicy, BadHostKeyException,
                      BadAuthenticationType, PasswordRequiredException)
from paramiko import SSHClient as ParamikoSSHClient
from paramiko import SSHException as ParamikoSSHException
from paramiko import AuthenticationException as ParamikoAuthException
from paramiko import __version_info__ as ParamikoVersionInfo
from paramiko import __version__ as ParamikoVersion

from ._constants import (BLANK_LINES, DEFAULT_LOG_FORMAT,
                         DEFAULT_LOG_FORMAT_DATE, DEFAULT_LOG_LEVEL,
                         DEFAULT_SSH_PORT, DEFAULT_TCP_TIMEOUT, LOCALHOST,
                         TCP_BUFFER, UTF8)
from ._exceptions import (ConnectionException, InvalidOperationException,
                          SSHException, AuthenticationException,
                          HostKeyException, KeyfileException,
                          PasswordRequired, UnsupportedAuthenticationType,
                          AutoRejectedHostKey, UserRejectedHostKey)
from ._messages import (err_invalid_none, err_logger_initialized,
                        err_socket_fail_connect, err_socket_fail_init,
                        err_ssh_auth_failed, err_ssh_auth_password,
                        err_ssh_auth_type_bad, err_ssh_clientkeys_open,
                        err_ssh_connect_failed, err_ssh_connected,
                        err_ssh_exec_cmd_failed, err_ssh_forward_closing,
                        err_ssh_forward_exists, err_ssh_forward_failed,
                        err_ssh_forward_not_found, err_ssh_forward_rejected,
                        err_ssh_hostkey_invalid, err_ssh_hostkeys_create,
                        err_ssh_hostkeys_read, err_ssh_hostkeys_write,
                        err_ssh_invoke_shell_failed, err_ssh_not_connected,
                        err_ssh_reverse_closing, err_ssh_reverse_exists,
                        err_ssh_reverse_failed, err_ssh_reverse_not_found,
                        err_ssh_reverse_rejected, ssh_compress_na,
                        ssh_connect_closed, ssh_connect_starting,
                        ssh_connect_success, ssh_forward_tunnel_connected,
                        ssh_forward_tunnel_disconnected,
                        ssh_forward_tunnel_shutdown,
                        ssh_forward_tunnel_starting, ssh_host_key_added,
                        ssh_host_key_rejected_auto,
                        ssh_host_key_rejected_user, ssh_host_key_saved,
                        ssh_reverse_tunnel_connected,
                        ssh_reverse_tunnel_disconnected,
                        ssh_reverse_tunnel_shutdown,
                        ssh_reverse_tunnel_starting)


class AutoRejectPolicy (MissingHostKeyPolicy):
    """
    Policy for unknown SSH host keys that automatically rejects the key.
    """
    def __init__(self, logger):
        """
        Create a new AutoRejectPolicy instance.

        Args:
            logger (logging.Logger) : the Logger instance to use.
        """
        self.logger = logger

    def missing_host_key(self, client, hostname, key):
        """
        Called when connecting to an unknown SSH host.

        Raises:
            AutoRejectedHostKey   : always.
        """
        self.logger.info(ssh_host_key_rejected_auto %
                         (hostname, key.get_name(),
                          hexlify(key.get_fingerprint())))
        raise AutoRejectedHostKey(hostname, key.get_name(),
                                  hexlify(key.get_fingerprint()))


class PromptUserPolicy (AutoAddPolicy):
    """
    Policy for unknown SSH host keys that provides a callback mechanism allowing
    callers to prompt their user to decide whether to accept or reject the key.

    If the user accepts the key it is added and saved to the hostkeys file.
    """
    def __init__(self, logger, hostkeys, callback):
        """
        Create a new PromptUserPolicy instance.

        Args:
            logger (logging.Logger) : the Logger instance to use.
            hostkeys (str)          : the file containing known SSH host keys, or None.
            callback                : the callable which will actually prompt the user.

        **NOTES**

        callback(hostname, key_type, key_fingerprint) is passed those three string
        parameters and returns True to accept the key, or False to reject the key.
        """
        self.logger = logger
        self.hostkeys = hostkeys
        self.callback = callback

    def missing_host_key(self, client, hostname, key):
        """
        Called when connecting to an unknown SSH host.

        Raises:
            UserRejectedHostKey   : if the user rejects the new host key.
            KeyfileException      : if the hostkeys cannot be written to.
        """
        if not self.callback(hostname, key.get_name(),
                             hexlify(key.get_fingerprint())):
            self.logger.info(ssh_host_key_rejected_user %
                             (hostname, key.get_name(),
                              hexlify(key.get_fingerprint())))
            raise UserRejectedHostKey(hostname, key.get_name(),
                                      hexlify(key.get_fingerprint()))

        client.get_host_keys().add(hostname, key.get_name(), key)
        self.logger.info(ssh_host_key_added %
                         (key.get_name(), hostname,
                          hexlify(key.get_fingerprint())))

        if self.hostkeys is not None:
            try:
                client.save_host_keys(self.hostkeys)
            except IOError as e:
                self.logger.exception(err_ssh_hostkeys_write)
                raise KeyfileException(err_ssh_hostkeys_write + \
                                       BLANK_LINES + str(e))
            self.logger.info(ssh_host_key_saved % (self.hostkeys))


class SSHClient (object):
    """
    Functionality for controlling a client session with an SSH server.

    This class was started for internal needs but it eventually evolved
    into a basic wrapper around much of the `paramiko.SSHClient` class,
    thus it could prove useful to others as well.

    We defined a different `connect()` method so that we could integrate
    our basic hostkey requirements directly into the connection process.

    The added value comes in the form of some simple methods for creating
    and destroying arbitrary forward and reverse SSH tunnels, whereby all
    of the actual networking gets done automagically behind the scenes.

    Pseudo example below, see the sources of the SupportBase, SupportConsumer
    and SupportProvider classes for further usage examples.

    >>> from yarest import SSHClient
    >>>
    >>> client = SSHClient()
    >>>
    >>> # optionally initialize logging as desired
    >>> client.init_logger("my logger name", "/my/log/file/path")
    >>>
    >>> # connect the session
    >>> client.connect("my.support.server")
    >>>
    >>> # forward localhost port 8080 to remote server port 80
    >>> client.create_forward_tunnel(8080, 80)
    >>>
    >>> # reverse forward a random server port to localhost port 5500
    >>> allocated_server_port = client.create_reverse_tunnel(5500)
    >>>
    >>> while not time_to_stop_forward_tunnel:
    >>>     continue
    >>>
    >>> # destroy the forward tunnel
    >>> client.destroy_forward_tunnel(8080, 80)
    >>>
    >>> while not time_to_stop_session:
    >>>     continue
    >>>
    >>> # disconnect the session (also destroys any tunnels that exist)
    >>> client.disconnect()
    """
    def __del__(self):
        self.disconnect()

    def __init__(self):
        self.logger = None
        self._lock = Lock()
        self._logger_lock = RLock()
        self._tunnel_lock = Lock()
        self._set_internal_defaults()

    def connect(self, host, host_port=DEFAULT_SSH_PORT, client_username=None,
                host_keyfile=None, client_keyfile=None, client_password=None,
                missing_hostkey_policy=None, tcp_timeout=DEFAULT_TCP_TIMEOUT,
                ssh_compression=False):
        """
        Establishes an SSH connection to the given host.

        Args:
            host (str)                : the name or IP address of the server being connected to.

        Kwargs:
            host_port (int)           : the port on `host` to use for the connection, default: 22.
            client_username (str)     : the username to login as, default: None for the current local username.
            host_keyfile (str)        : the filename containing the known host key(s), default: None to look for OpenSSH known_hosts.
            client_keyfile (str)      : the filename containing the client's private key(s), default: None.
            client_password (str)     : the password used to login on the server or decrypt the client's private key, default: None.
            missing_hostkey_policy    : the paramiko.MissingHostKeyPolicy to use for unknown hosts, default: None for AutoRejectPolicy().
            tcp_timeout (float)       : the initial tcp connection timeout in seconds, default: 7.
            ssh_compression (bool)    : True to turn on SSH compression, default: False.

        Raises:
            InvalidOperationException : if the client is already connected.
            ValueError                : if `host` is None.
            KeyfileException          : if either `host_keyfile` or `client_keyfile` is given but not accessible.
            ConnectionException       : if there is a problem connecting to the specified `host`.
            HostKeyException          : if the returned server host key doesn't match the local host key.
            AutoRejectedHostKey       : if unknown hosts are not allowed and no local host key is available.
            AuthenticationException   : if the client authentication process fails for any reason.
            SSHException              : if there is any other error establishing the SSH session.

        *NOTES*

        The authentication method used is based on the arguments provided:

        If `client_keyfile` is provided it is tried first, after that private
        keys are searched for via an SSH agent if available, and finally the
        standard username/password authentication if a password is supplied.

        Compression only became part of the paramiko.SSHClient API at version
        1.7.7.1, the option is simply ignored if an earlier version is used.
        """
        if self.is_connected():
            raise InvalidOperationException(err_ssh_connected)
        if host is None:
            raise ValueError(err_invalid_none % ("host"))
        with self._lock:
            self._client = ParamikoSSHClient()
            self._client.set_log_channel(self.get_logger().name)
            self._server_name = str(host).lower()
            self._server_port = int(host_port)

            if missing_hostkey_policy is None:
                missing_hostkey_policy = AutoRejectPolicy(self.get_logger())
            self._client.set_missing_host_key_policy(missing_hostkey_policy)
            self._client.load_system_host_keys()

            if host_keyfile is not None:
                if os.path.exists(host_keyfile):
                    try:
                        self._client.load_host_keys(host_keyfile)
                    except IOError as e:
                        self.get_logger().exception(err_ssh_hostkeys_read)
                        self._set_internal_defaults()
                        exc = KeyfileException(err_ssh_hostkeys_read + \
                                               BLANK_LINES + str(e))
                        raise exc, None, sys.exc_info()[2]
                else:
                    try:
                        with open(host_keyfile, "a+"): pass
                    except IOError as e:
                        self.get_logger().exception(err_ssh_hostkeys_create)
                        self._set_internal_defaults()
                        exc = KeyfileException(err_ssh_hostkeys_create + \
                                               BLANK_LINES + str(e))
                        raise exc, None, sys.exc_info()[2]

            args = {"hostname": self._server_name,
                    "port": self._server_port,
                    "key_filename": client_keyfile,
                    "username": client_username,
                    "password": client_password,
                    "timeout": tcp_timeout,
                    "look_for_keys": False}

            # whether paramiko api supports compression or not
            if ParamikoVersionInfo < (1, 7, 7):
                self.get_logger().info(ssh_compress_na %
                                       (ParamikoVersion, ssh_compression))
            else:
                args["compress"] = ssh_compression

            self.get_logger().info(ssh_connect_starting %
                                   (self._server_name, self._server_port))

            try:
                self._client.connect(**args)
            except SSHException:
                self._set_internal_defaults()
                raise
            except socket.error as (err_code, err_message):
                self.get_logger().exception(err_ssh_connect_failed %
                                            (self._server_name,
                                             self._server_port))
                exc = ConnectionException(err_code, err_message,
                                          err_ssh_connect_failed %
                                          (self._server_name,
                                           self._server_port))
                self._set_internal_defaults()
                raise exc, None, sys.exc_info()[2]
            except IOError as e:
                self.get_logger().exception(err_ssh_clientkeys_open)
                exc = KeyfileException(err_ssh_clientkeys_open + \
                                       BLANK_LINES + str(e))
                self._set_internal_defaults()
                raise exc, None, sys.exc_info()[2]
            except PasswordRequiredException:
                self.get_logger().exception(err_ssh_auth_password)
                self._set_internal_defaults()
                raise PasswordRequired(), None, sys.exc_info()[2]
            except BadAuthenticationType as e:
                self.get_logger().exception(err_ssh_auth_type_bad)
                exc = UnsupportedAuthenticationType(e.allowed_types)
                self._set_internal_defaults()
                raise exc, None, sys.exc_info()[2]
            except ParamikoAuthException:
                self.get_logger().exception(err_ssh_auth_failed)
                exc = AuthenticationException(err_ssh_auth_failed)
                self._set_internal_defaults()
                raise exc, None, sys.exc_info()[2]
            except BadHostKeyException as e:
                self.get_logger().exception(err_ssh_hostkey_invalid %
                                            (e.expected_key, e.key))
                exc = HostKeyException(err_ssh_hostkey_invalid %
                                       (e.expected_key, e.key))
                self._set_internal_defaults()
                raise exc, None, sys.exc_info()[2]
            except ParamikoSSHException as e:
                self.get_logger().exception(err_ssh_connect_failed %
                                            (self._server_name,
                                             self._server_port))
                exc = SSHException(err_ssh_connect_failed %
                                   (self._server_name, self._server_port) + \
                                   BLANK_LINES + str(e))
                self._set_internal_defaults()
                raise exc, None, sys.exc_info()[2]
        self.get_logger().info(ssh_connect_success %
                               (self._server_name, self._server_port))

    def create_forward_tunnel(self, orig_port, dest_port, dest_host=None):
        """
        Creates a forward tunnel over the current SSH connection, similar
        to the OpenSSH "-L" option. An instance of this class supports
        opening multiple concurrent forward tunnels.

        Args:
            orig_port (int)           : the origin port number on the localhost.
            dest_port (int)           : the destination port number on `dest_host`.

        Kwargs:
            dest_host (str)           : the destination host, default: None for the SSH server.

        Raises:
            InvalidOperationException : if the client is not connected or `orig_port` is already forwarded.
        """
        if not self.is_connected():
            raise InvalidOperationException(err_ssh_not_connected)
        if dest_host is None:
            dest_host = LOCALHOST
        dest_host = dest_host.lower()
        dest_port = int(dest_port)
        orig_port = int(orig_port)
        with self._lock:
            if self._get_forward_by_port(orig_port) is not None:
                raise InvalidOperationException(err_ssh_forward_exists %
                                                (orig_port))

            class _OuterHandler (_ForwardHandler):
                begin_port = orig_port
                end_host = dest_host
                end_port = dest_port
                logger = self.get_logger()
                transport = self._client.get_transport()

            tunnel = ThreadingTCPServer((LOCALHOST, orig_port),
                                        _OuterHandler, False)
            tunnel.allow_reuse_address = True
            tunnel.daemon_threads = True
            tunnel.server_bind()
            tunnel.server_activate()
            self._forwardtunnels.append((tunnel, orig_port,
                                         (dest_host, dest_port)))

        t = Thread(target=tunnel.serve_forever)
        t.daemon = True
        t.start()
        self.get_logger().info(ssh_forward_tunnel_starting %
                               (orig_port, dest_host, dest_port))

    def create_reverse_tunnel(self, dest_port, orig_port=0, dest_host=LOCALHOST):
        """
        Creates a reverse tunnel over the current SSH connection, similar
        to the OpenSSH "-R" option. An instance of this class supports
        opening multiple concurrent reverse tunnels.

        Args:
            dest_port (int)           : the destination port number on `dest_host`.

        Kwargs:
            orig_port (int)           : the origin port number on the SSH server, default: 0 for a random port.
            dest_host (str)           : the destination host, default: "localhost".

        Returns: (int)
            The port number allocated on the server.

        Raises:
            ValueError                : if `dest_host` is None.
            InvalidOperationException : if the client is not connected or `orig_port` is already forwarded.
            SSHException              : if the tunnel request is rejected.
        """
        if not self.is_connected():
            raise InvalidOperationException(err_ssh_not_connected)
        if dest_host is None:
            raise ValueError(err_invalid_none % ("dest_host"))
        dest_host = dest_host.lower()
        dest_port = int(dest_port)
        orig_port = int(orig_port)
        with self._tunnel_lock:
            if self._get_reverse_by_port(orig_port) is not None:
                raise InvalidOperationException(err_ssh_reverse_exists %
                                                (orig_port))

            with self._lock:
                orig_host = self._server_name
                try:
                    s_port = self._invoke_reverse_request(orig_port)
                    # if we're requesting a random port then we have to use the
                    # workaround of cancelling the request and re-submitting it
                    # explicitly with the same port the server allocated to us.
                    # if we don't then we would never find the matching tunnel
                    # in our handler, because the source port provided to the
                    # handler would always be 0 and not the actual port used.
                    if orig_port == 0:
                        self._invoke_reverse_cancel(orig_port, True)
                        s_port = self._invoke_reverse_request(s_port)
                except ParamikoSSHException:
                    self.get_logger().exception(err_ssh_reverse_rejected %
                                                (orig_host, orig_port,
                                                 dest_host, dest_port))
                    exc = SSHException(err_ssh_reverse_rejected %
                                       (orig_host, orig_port,
                                        dest_host, dest_port))
                    raise exc, None, sys.exc_info()[2]

            tunnel = _ReverseHandler([orig_host, s_port,
                                      dest_host, dest_port],
                                     self.get_logger())
            self._reversetunnels.append((tunnel, s_port,
                                         (dest_host, dest_port)))

        self.get_logger().info(ssh_reverse_tunnel_starting %
                               (orig_host, s_port,
                                dest_host, dest_port))
        return s_port

    def destroy_forward_tunnel(self, orig_port, dest_port, dest_host=None):
        """
        Destroys a previously created forward tunnel.

        Args:
            orig_port (int)           : the origin port number on the localhost.
            dest_port (int)           : the destination port number on `dest_host`.

        Kwargs:
            dest_host (str)           : the destination host, default: None for the SSH server.

        Raises:
            InvalidOperationException : if no such tunnel was previously created.
        """
        if dest_host is None:
            dest_host = self._server_name
        dest_host = dest_host.lower()
        dest_port = int(dest_port)
        orig_port = int(orig_port)
        with self._lock:
            item = self._get_forward(orig_port, dest_host, dest_port)
            if item is None:
                raise InvalidOperationException(err_ssh_forward_not_found %
                                                (orig_port,
                                                 dest_host, dest_port))
            self._forwardtunnels.remove(item)
            self._shutdown_forward(item[0], item[1], item[2])

    def destroy_reverse_tunnel(self, dest_port, orig_port, dest_host=LOCALHOST):
        """
        Destroys a previously created reverse tunnel.

        Args:
            dest_port (int)           : the destination port number on `dest_host`.
            orig_port (int)           : the origin port number on the SSH server.

        Kwargs:
            dest_host (str)           : the destination host, default: "localhost".

        Raises:
            ValueError                : if `dest_host` is None.
            InvalidOperationException : if no such tunnel was previously created.
        """
        if dest_host is None:
            raise ValueError(err_invalid_none % ("dest_host"))
        dest_host = dest_host.lower()
        dest_port = int(dest_port)
        orig_port = int(orig_port)
        with self._tunnel_lock:
            item = self._get_reverse(orig_port, dest_host, dest_port)
            if item is None:
                raise InvalidOperationException(err_ssh_reverse_not_found %
                                                (self._server_name, orig_port,
                                                 dest_host, dest_port))
            self._reversetunnels.remove(item)
        with self._lock:
            self._shutdown_reverse(item[0], item[1], item[2])

    def disconnect(self):
        """
        Terminates the SSH connection and destroys any created tunnels.
        """
        with self._lock:
            for item in self._forwardtunnels:
                self._shutdown_forward(item[0], item[1], item[2])
            with self._tunnel_lock:
                for item in self._reversetunnels:
                    self._shutdown_reverse(item[0], item[1], item[2])
            if self._client is not None:
                self._client.close()
                self.get_logger().info(ssh_connect_closed %
                                       (self._server_name, self._server_port))
            self._set_internal_defaults()

    def exec_command(self, command, bufsize=-1):
        """
        Executes the given command on the SSH server and returns the
        stdin, stdout and stderr streams associated with the command.

        Args:
            command (str)             : the command to execute.

        Kwargs:
            bufsize (int)             : the buffering for the streams, default: -1 for system default.

        Returns: tuple(paramiko.ChannelFile, paramiko.ChannelFile, paramiko.ChannelFile)
            File-like objects representing the stdin, stdout, and stderr of the command.

        Raises:
            InvalidOperationException : if the client is not connected.
            ValueError                : if `command` is None or empty.
            SSHException              : if the server fails to execute the command.

        *NOTES*

        `bufsize` is interpreted as for the Python file() function:

        bufsize == 0  : unbuffered
        bufsize == 1  : line buffered
        bufsize > 1   : use a buffer of approximately that size
        """
        if not self.is_connected():
            raise InvalidOperationException(err_ssh_not_connected)
        if command is None or len(command) == 0:
            raise ValueError(err_invalid_none % ("command"))
        with self._lock:
            try:
                return self._client.exec_command(command, bufsize)
            except ParamikoSSHException as e:
                self.get_logger().exception(err_ssh_exec_cmd_failed %
                                            (command, bufsize))
                exc = SSHException(err_ssh_exec_cmd_failed %
                                   (command, bufsize) + BLANK_LINES + str(e))
                raise exc, None, sys.exc_info()[2]

    def get_logger(self):
        """
        Gets the logger object used by this instance.

        Returns: (logging.Logger)
            The logger object in use.

        If `init_logger()` has not already been called, and also the `logger`
        instance variable has not been assigned, then this method initializes
        the logger using a randomly named temp file ending in "SSHClient.log".
        """
        with self._logger_lock:
            if self.logger is None:
                from tempfile import mkstemp
                fd, name = mkstemp(suffix=self.__class__.__name__ + ".log")
                os.close(fd)
                self.init_logger(self.__class__.__name__ + os.urandom(8), name)
        return self.logger

    def init_logger(self, logger_name, log_file, log_file_encoding=UTF8,
                    log_format=DEFAULT_LOG_FORMAT,
                    log_format_date=DEFAULT_LOG_FORMAT_DATE,
                    log_level=DEFAULT_LOG_LEVEL):
        """
        Setup the logger object used by this instance.

        Args:
            logger_name (str)         : the name to assign the logger object.
            log_file (str)            : the full path of the log file to use.

        Kwargs:
            log_file_encoding (str)   : the encoding of the log file, default: "utf-8".
            log_format (str)          : the message format string for the formatter, default: "%(asctime)s - %(levelname)s - %(message)s".
            log_format_date (str)     : the date format string for the formatter, default: "%m/%d/%Y %I:%M:%S %p".
            log_level (int)           : the level to assign the logger, default: logging.DEBUG.

        Raises:
            ValueError                : if `logger_name` or `log_file_name` is None.
            InvalidOperationException : if the logger has already been initialized.
            IOError                   : if `log_file_name` is not writable.

        *NOTES*

        For other needs simply assign a Logger instance to the `logger` variable.

        >>> ssh_client = SSHClient()
        >>> ssh_client.logger = mycustomlogger
        """
        if logger_name is None:
            raise ValueError(err_invalid_none % ("logger_name"))
        if log_file is None:
            raise ValueError(err_invalid_none % ("log_file"))
        with self._logger_lock:
            if self.logger is not None:
                raise InvalidOperationException(err_logger_initialized)
            with open(log_file, "a+"): pass
            handler = FileHandler(log_file, "a", log_file_encoding)
            handler.setFormatter(Formatter(log_format, log_format_date))
            self.logger = getLogger(logger_name)
            self.logger.addHandler(handler)
            self.logger.setLevel(log_level)

    def invoke_shell(self, terminal="vt100", width=80, height=24):
        """
        Begins an interactive shell session on the SSH server that is
        connected to a pseudo-terminal of the requested type and size.

        Kwargs:
            terminal (str             : the terminal type to emulate, default: "vt100"
            width (int)               : the width in characters of the terminal, default: 80
            height (int)              : the height in characters of the terminal, default: 24

        Returns: (paramiko.Channel)
            A socket like object connected to the remote shell terminal.

        Raises:
            InvalidOperationException : if the client is not connected.
            ValueError                : if `terminal` is None or empty.
            SSHException              : if the server fails to invoke the shell.
        """
        if not self.is_connected():
            raise InvalidOperationException(err_ssh_not_connected)
        if terminal is None or len(terminal) == 0:
            raise ValueError(err_invalid_none % ("terminal"))
        with self._lock:
            try:
                return self._client.invoke_shell(terminal, width, height)
            except ParamikoSSHException as e:
                self.get_logger().exception(err_ssh_invoke_shell_failed %
                                            (terminal, width, height))
                exc = SSHException(err_ssh_invoke_shell_failed %
                                   (terminal, width, height) + \
                                   BLANK_LINES + str(e))
                raise exc, None, sys.exc_info()[2]

    def is_connected(self):
        """
        Returns True if the SSH session is connected, False otherwise.
        """
        with self._lock:
            return self._client is not None and \
                   self._client.get_transport().is_authenticated()

    def open_sftp(self):
        """
        Opens an SFTP session on the server using the current connection.

        Returns: (paramiko.SFTPClient)
            An SFTP object connected to the SSH server.

        Raises:
            InvalidOperationException : if the client is not connected.
        """
        if not self.is_connected():
            raise InvalidOperationException(err_ssh_not_connected)
        with self._lock:
            return self._client.open_sftp()

    def _get_forward(self, orig_port, dest_host, dest_port):
        dest_addr = (dest_host, dest_port)
        for item in self._forwardtunnels:
            if item[1] == orig_port and item[2] == dest_addr: return item
        return None

    def _get_forward_by_port(self, orig_port):
        for item in self._forwardtunnels:
            if item[1] == orig_port: return item
        return None

    def _get_reverse(self, orig_port, dest_host, dest_port):
        dest_addr = (dest_host, dest_port)
        for item in self._reversetunnels:
            if item[1] == orig_port and item[2] == dest_addr: return item
        return None

    def _get_reverse_by_port(self, orig_port):
        for item in self._reversetunnels:
            if item[1] == orig_port: return item
        return None

    def _invoke_reverse_cancel(self, port, wait):
        transport = self._client.get_transport()
        transport.global_request(kind="cancel-tcpip-forward",
                                 data=(LOCALHOST, port),
                                 wait=wait)

    def _invoke_reverse_request(self, port):
        r_forward = self._client.get_transport().request_port_forward
        return r_forward(address=LOCALHOST,
                         port=port,
                         handler=self._reverse_launcher)

    def _reverse_launcher(self, channel, (o_addr, o_port), (s_addr, s_port)):
        with self._tunnel_lock:
            item = self._get_reverse_by_port(s_port)
        assert item is not None
        tunnel = item[0]
        t = Thread(target=tunnel.start, args=[channel])
        t.setDaemon(True)
        t.start()

    def _set_internal_defaults(self):
        self._client = None
        self._forwardtunnels = []
        self._reversetunnels = []
        self._server_name = ""
        self._server_port = 0

    def _shutdown_forward(self, tunnel, orig_port, dest_addr):
        self.get_logger().info(ssh_forward_tunnel_shutdown %
                               (orig_port, dest_addr[0], dest_addr[1]))
        try:
            tunnel.shutdown()
            tunnel.socket.shutdown(socket.SHUT_RDWR)
            tunnel.socket.close()
        except socket.error as (err_code, err_message):
            # no need to log "transport endpoint is not connected"
            # errors that can be raised from the socket.shutdown()
            if err_code != errno.ENOTCONN:
                self.get_logger().exception(err_ssh_forward_closing %
                                            (orig_port,
                                             dest_addr[0], dest_addr[1]))

    def _shutdown_reverse(self, tunnel, orig_port, dest_addr):
        self.get_logger().info(ssh_reverse_tunnel_shutdown %
                               (self._server_name, orig_port,
                                dest_addr[0], dest_addr[1]))
        try:
            tunnel.shutdown()
        except socket.error as (err_code, err_message):
            # no need to log "transport endpoint is not connected"
            # errors that can be raised from the socket.shutdown()
            if err_code != errno.ENOTCONN:
                self.get_logger().exception(err_ssh_reverse_closing %
                                            (self._server_name, orig_port,
                                             dest_addr[0], dest_addr[1]))
        finally:
            self._invoke_reverse_cancel(orig_port, False)


class _ForwardHandler (BaseRequestHandler):
    """Handler implementation for forward tunnels."""
    def handle(self):
        origin_addr = self.request.getpeername()
        try:
            channel = self.transport.open_channel("direct-tcpip",
                                                  (self.end_host,
                                                  self.end_port),
                                                  origin_addr)
        except:
            self.logger.exception(err_ssh_forward_failed %
                                  (self.begin_port,
                                   self.end_host, self.end_port,
                                   _host_tuple_to_string(origin_addr)))
            return
        if channel is None:
            self.logger.error(err_ssh_forward_rejected %
                              (self.begin_port,
                               self.end_host, self.end_port,
                               _host_tuple_to_string(origin_addr)))
            return

        ssh_addr = _host_tuple_to_string(channel.getpeername())
        self.logger.info(ssh_forward_tunnel_connected %
                         (self.begin_port, ssh_addr,
                          self.end_host, self.end_port,
                          _host_tuple_to_string(origin_addr)))

        while True:
            r, w, x = select.select([self.request, channel], [], [])
            if self.request in r:
                data = self.request.recv(TCP_BUFFER)
                if len(data) == 0: break
                channel.sendall(data)
            if channel in r:
                data = channel.recv(TCP_BUFFER)
                if len(data) == 0: break
                self.request.sendall(data)

        self.logger.info(ssh_forward_tunnel_disconnected %
                         (self.begin_port, ssh_addr,
                          self.end_host, self.end_port,
                          _host_tuple_to_string(origin_addr)))
        channel.close()
        self.request.close()


class _ReverseHandler (object):
    """Handler implementation for reverse tunnels."""
    def __init__(self, endpoints, logger):
        self.orig_host = endpoints[0]
        self.orig_port = endpoints[1]
        self.dest_host = endpoints[2]
        self.dest_port = endpoints[3]
        self.channel = None
        self.logger = logger
        self.running = False
        self.socket = None
        self._lock = Lock()

    def start(self, channel):
        with self._lock:
            sock = None
            for (af, socktype, proto, canonname, sa) in \
                socket.getaddrinfo(self.dest_host, self.dest_port,
                                   socket.AF_UNSPEC, socket.SOCK_STREAM):
                try:
                    sock = socket.socket(af, socktype, proto)
                except socket.error:
                    self.logger.exception(err_socket_fail_init % (sa))
                    sock = None
                    continue
                try:
                    sock.connect(sa)
                except socket.error:
                    self.logger.exception(err_socket_fail_connect % (sa))
                    sock.close()
                    sock = None
                    continue
                break
            if sock is None:
                self.logger.error(err_ssh_reverse_failed %
                                  (self.orig_host, self.orig_port,
                                   self.dest_host, self.dest_port))
                return

            ssh_addr = _host_tuple_to_string(channel.getpeername())
            self.channel = channel
            self.socket = sock
            self.logger.info(ssh_reverse_tunnel_connected %
                             (self.orig_host, self.orig_port, ssh_addr,
                              self.dest_host, self.dest_port))
            self.running = True

        while self.running:
            r, w, x = select.select([channel, sock], [], [])
            if channel in r:
                data = channel.recv(TCP_BUFFER)
                if len(data) == 0: break
                sock.sendall(data)
            if sock in r:
                data = sock.recv(TCP_BUFFER)
                if len(data) == 0: break
                channel.sendall(data)

        self.running = False
        self.logger.info(ssh_reverse_tunnel_disconnected %
                         (self.orig_host, self.orig_port, ssh_addr,
                          self.dest_host, self.dest_port))
        sock.close()
        channel.close()

    def shutdown(self):
        with self._lock:
            if self.running:
                try:
                    self.channel.shutdown(socket.SHUT_RDWR)
                    self.socket.shutdown(socket.SHUT_RDWR)
                finally:
                    self.running = False


def _host_tuple_to_string(host_addr):
    if host_addr is None: return "UNKNOWN"
    return "%s:%d" % (host_addr[0], host_addr[1])
