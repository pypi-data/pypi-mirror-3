## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

from ._messages import (err_socket_info, err_ssh_auth_password,
                        err_ssh_auth_type_bad, err_ssh_auth_type_info,
                        ssh_host_key_rejected_auto, ssh_host_key_rejected_user)


class ConnectionException (Exception):
    """
    Raised when there is a network connectivity problem.
    """
    def __init__(self, error_code, error_msg, exc_cause):
        """
        Initializes a new ConnectionException.

        Args:
            error_code (int)  : the socket error number that caused this exception.
            error_msg (str)   : the socket error message that caused this exception.
            exc_cause (str)   : additional information about why this exception occured.
        """
        Exception.__init__(self, exc_cause + err_socket_info %
                                             (error_code, error_msg))
        self.error_code = error_code


class InvalidOperationException (Exception):
    """
    Raised when an operation is invalid for the state of the object.
    """
    pass


class SSHException (Exception):
    """
    Raised when there is an SSH specific problem.
    """
    pass


class AuthenticationException (SSHException):
    """
    Raised when SSH client authentication fails.
    """
    pass


class HostKeyException (SSHException):
    """
    Raised when there is a problem with an SSH host key.
    """
    pass


class KeyfileException (SSHException):
    """
    Raised when there is a problem with an SSH keyfile.
    """
    pass


class PasswordRequired (AuthenticationException):
    """
    Raised when no password was provided but one was required.
    """
    def __init__(self):
        """
        Initializes a new PasswordRequired exception.
        """
        AuthenticationException.__init__(self, err_ssh_auth_password)


class UnsupportedAuthenticationType (AuthenticationException):
    """
    Raised when the SSH server does not support the authentication type used.
    """
    def __init__(self, valid_types):
        """
        Initializes a new UnsupportedAuthenticationType exception.

        Args:
            valid_types (list(str))  : list of supported authentication types.
        """
        AuthenticationException.__init__(self, err_ssh_auth_type_bad + \
                                               err_ssh_auth_type_info %
                                               (valid_types))
        self.valid_types = valid_types


class AutoRejectedHostKey (HostKeyException):
    """
    Raised when connecting to an unknown SSH host is prohibited.
    """
    def __init__(self, hostname, key_type, key_fingerprint):
        """
        Initializes a new AutoRejectedHostKey exception.

        Args:
            hostname (str)        : the host whose key was rejected.
            key_type (str)        : the type of key, "ssh-rsa" or "ssh-dsa"
            key_fingerprint (str) : the MD5 key fingerprint as a hex string.
        """
        HostKeyException.__init__(self, ssh_host_key_rejected_auto %
                                        (hostname, key_type, key_fingerprint))
        self.hostname = hostname
        self.key_type = key_type
        self.key_fingerprint = key_fingerprint


class UserRejectedHostKey (HostKeyException):
    """
    Raised when an unknown SSH host key is rejected by the user.
    """
    def __init__(self, hostname, key_type, key_fingerprint):
        """
        Initializes a new UserRejectedHostKey exception.

        Args:
            hostname (str)        : the host whose key was rejected.
            key_type (str)        : the type of key, "ssh-rsa" or "ssh-dsa"
            key_fingerprint (str) : the MD5 key fingerprint as a hex string.
        """
        HostKeyException.__init__(self, ssh_host_key_rejected_user %
                                        (hostname, key_type, key_fingerprint))
        self.hostname = hostname
        self.key_type = key_type
        self.key_fingerprint = key_fingerprint
