## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

import os

from configobj import ConfigObj, ConfigObjError

from ._constants import DEFAULT_SSH_PORT, DEFAULT_TCP_TIMEOUT, UTF8
from ._messages import (err_invalid_none, err_invalid_profile_name,
                        err_invalid_ssh_port, err_invalid_ssh_server,
                        err_invalid_tcp_timeout, err_invalid_vnc_exec,
                        err_invalid_vnc_port)


class ConnectionProfile (object):
    """
    An individual connection profile which can be used
    by either a `SupportConsumer` or `SupportProvider`.

    This class can be instantiated and populated manually, or
    automatically populated from data in a configuration file.

    When populating an instance manually note that the attribute names in this
    class exactly match the corresponding name within the configuration file.

    Please note that the default "None" values listed below are the Python
    `None` value and *not* what should be put into the configuration file.
    Setting a value = None in the config simply yields the string "None".

    See the "profiles.ini" file in the "examples" subdirectory
    of this distribution for some deployable example profiles.

    The available configuration file entries are listed below, entries that
    are labeled OPTIONAL can simply be omitted to use their default values.

    *Configuration File Format*
    ===========================

    ; REQUIRED: Unique profile name, any number of profiles can be listed
    [My Profile Name]

    ; REQUIRED: Hostname or IP address of the SSH server
    ssh_server = "my.support.server"

    ; OPTIONAL: SSH server port number, default: 22
    ssh_port = 22

    ; OPTIONAL: Username to login as on the SSH server, default: None
    ; (None uses the currently logged on username at runtime)
    ssh_username = "john doe"

    ; OPTIONAL: Full path of the known SSH host keys, default: None
    ; (None looks for the user's OpenSSH style host keys in ~/.ssh)
    ;
    ; Environment variables and user "~" are expanded at runtime
    ssh_hostkeys = "~/.ssh/known_hosts"

    ; OPTIONAL: Full path of the user's SSH private key, default: None
    ; (None looks for an SSH agent then uses password authentication)
    ;
    ; Environment variables and user "~" are expanded at runtime
    ssh_clientkeys = "/path/to/clientkey"

    ; OPTIONAL: True to allow connecting to unknown SSH hosts, default: False
    ssh_allow_unknown = True

    ; OPTIONAL: True to enable SSH compression, default: False
    ; (Compression is only supported with Paramiko 1.7.7.1 or greater)
    ssh_compression = True

    ; OPTIONAL: Initial TCP connection timeout in seconds, default: 7
    tcp_timeout = 30

    ; REQUIRED: Full path of the VNC executable to use
    ;
    ; Environment variables and user "~" are expanded at runtime
    vnc_exec = "/usr/bin/x11vnc"

    ; REQUIRED: Local VNC port number to use
    vnc_port = 5900

    ; OPTIONAL: Arguments to supply the VNC executable
    ;
    ; These may contain one or more %d format specifiers which will be
    ; automatically substituted for the local VNC port number at runtime
    ;
    ; This field is optional because in theory one may wish to use their own
    ; VNC variant with a known port that wouldn't require any arguments, for
    ; all practical purposes however this field will almost always be needed
    vnc_args = "-localhost -bg -find -nopw -rfbport %d -connect localhost:%d"

    ; OPTIONAL: Full path of the log file to use, default: None
    ; None uses the log file of the SupportConsumer or SupportProvider
    log_file = "/path/to/my/debug/file"
    """
    def __init__(self, name, config=None):
        """
        Creates a new ConnectionProfile object.

        Args:
            name (str)                   : the name to assign the profile.

        Kwargs:
            config (configobj.ConfigObj) : the config file reader to use, default: None.

        Raises:
            ConfigObjError               : if `config` is specified and the file format is invalid.
            ValueError                   : if `config` is specified and any profile value is invalid.

        *NOTES*

        If `config` is not None then `name` must be a subsection in `config`,
        in such cases the section data will be used to populate the instance.
        """
        self.name = name
        if config is None:
            self.ssh_server = None
            self.ssh_port = None
            self.ssh_username = None
            self.ssh_hostkeys = None
            self.ssh_clientkeys = None
            self.ssh_allow_unknown = None
            self.ssh_compression = None
            self.tcp_timeout = None
            self.vnc_exec = None
            self.vnc_port = None
            self.vnc_args = None
            self.log_file = None
        else:
            self.ssh_server = config[name]["ssh_server"]
            self.ssh_port = config[name].get("ssh_port", None)
            self.ssh_username = config[name].get("ssh_username", None)
            self.ssh_hostkeys = config[name].get("ssh_hostkeys", None)
            self.ssh_clientkeys = config[name].get("ssh_clientkeys", None)
            self.ssh_allow_unknown = config[name].get("ssh_allow_unknown", None)
            self.ssh_compression = config[name].get("ssh_compression", None)
            self.tcp_timeout = config[name].get("tcp_timeout", None)
            self.vnc_exec = config[name]["vnc_exec"]
            self.vnc_port = int(config[name]["vnc_port"])
            self.vnc_args = config[name].get("vnc_args", None)
            self.log_file = config[name].get("log_file", None)
            ConnectionProfile.prevalidate(self)

    def __eq__(self, other):
        return isinstance(other, ConnectionProfile) and \
               self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        attributes = ("%s = %r" % (k, v) for k, v in self.__dict__.items())
        return "<%s.%s: {%s}>" % (self.__module__,
                                  self.__class__.__name__,
                                  ', '.join(attributes))

    @staticmethod
    def prevalidate(profile, runtime=False):
        """
        Checks the given profile to verify that required values are present.

        Args:
            profile (ConnectionProfile) : the profile object to use.

        Kwargs:
            runtime (bool)              : True to prepare the profile for runtime use, default: False

        Raises:
            ValueError                  : if `profile` is None or any contained value is invalid.

        *NOTES*

        When `runtime` is True defaults are set for all optional values
        that are None, and user and environment variables are expanded
        within all values that represent a filename.
        """
        if profile is None:
            raise ValueError(err_invalid_none % ("profile"))
        if _is_empty(profile.name):
            raise ValueError(err_invalid_profile_name)
        if _is_empty(profile.ssh_server):
            raise ValueError(err_invalid_ssh_server)
        if profile.ssh_port is not None:
            profile.ssh_port = int(profile.ssh_port)
            if not _is_port(profile.ssh_port):
                raise ValueError(err_invalid_ssh_port)
        if _is_empty(profile.vnc_exec):
            raise ValueError(err_invalid_vnc_exec)
        if not _is_port(profile.vnc_port):
            raise ValueError(err_invalid_vnc_port)
        if profile.ssh_allow_unknown is not None:
            profile.ssh_allow_unknown = _cbool(profile.ssh_allow_unknown)
        if profile.ssh_compression is not None:
            profile.ssh_compression = _cbool(profile.ssh_compression)
        if profile.tcp_timeout is not None:
            profile.tcp_timeout = float(profile.tcp_timeout)
            if profile.tcp_timeout <= 0:
                raise ValueError(err_invalid_tcp_timeout)

        if runtime:
            profile.vnc_exec = _expand(profile.vnc_exec)
            if not os.path.isfile(profile.vnc_exec):
                raise ValueError(err_invalid_vnc_exec)
            if profile.ssh_port is None:
                profile.ssh_port = DEFAULT_SSH_PORT
            if _is_empty(profile.ssh_username):
                profile.ssh_username = None
            if _is_empty(profile.ssh_hostkeys):
                profile.ssh_hostkeys = None
            else:
                profile.ssh_hostkeys = _expand(profile.ssh_hostkeys)
            if _is_empty(profile.ssh_clientkeys):
                profile.ssh_clientkeys = None
            else:
                profile.ssh_clientkeys = _expand(profile.ssh_clientkeys)
            if profile.ssh_allow_unknown is None:
                profile.ssh_allow_unknown = False
            if profile.ssh_compression is None:
                profile.ssh_compression = False
            if profile.tcp_timeout is None:
                profile.tcp_timeout = DEFAULT_TCP_TIMEOUT
            if _is_empty(profile.log_file):
                profile.log_file = None
            else:
                profile.log_file = _expand(profile.log_file)

    @staticmethod
    def read_from_file(filename, encoding=UTF8):
        """
        Reads ConnectionProfile objects from the given configuration file.

        Args:
            filename (str)          : the configuration file to use.

        Kwargs:
            encoding (str)          : the encoding of `filename`, default: "utf-8".

        Returns: list(ConnectionProfile)
            A list containing all of the parsed ConnectionProfile objects.

        Raises:
            IOError                 : if `filename` doesn't exist or can't be read.
            ConfigObjError          : if the configuration file format is invalid.
            ValueError              : if any connection profile value is invalid.
        """
        config = ConfigObj(infile=filename, encoding=encoding,
                           file_error=True, raise_errors=True)
        profiles = []
        for section in config.sections:
            profile = ConnectionProfile(section, config)
            profiles.append(profile)
        return profiles

    @staticmethod
    def write_to_file(profiles, filename, encoding=UTF8):
        """
        Writes ConnectionProfile objects to the given configuration file.

        *This method will completely overwrite any existing file contents.*

        Args:
            profiles list(ConnectionProfile) : the connection profiles to write.
            filename (str)                   : the configuration file to use.

        Kwargs:
            encoding (str)                   : the encoding of `filename`, default: "utf-8".

        Raises:
            IOError                          : if `filename` is not writable.
        """
        config = ConfigObj(encoding=encoding)
        for profile in profiles:
            name = profile.name
            config[name] = {}
            config[name]["ssh_server"] = profile.ssh_server
            if profile.ssh_port is not None:
                config[name]["ssh_port"] = profile.ssh_port
            if profile.ssh_username is not None:
                config[name]["ssh_username"] = profile.ssh_username
            if profile.ssh_hostkeys is not None:
                config[name]["ssh_hostkeys"] = profile.ssh_hostkeys
            if profile.ssh_clientkeys is not None:
                config[name]["ssh_clientkeys"] = profile.ssh_clientkeys
            if profile.ssh_allow_unknown is not None:
                config[name]["ssh_allow_unknown"] = profile.ssh_allow_unknown
            if profile.ssh_compression is not None:
                config[name]["ssh_compression"] = profile.ssh_compression
            if profile.tcp_timeout is not None:
                config[name]["tcp_timeout"] = profile.tcp_timeout
            config[name]["vnc_exec"] = profile.vnc_exec
            config[name]["vnc_port"] =  profile.vnc_port
            if profile.vnc_args is not None:
                config[name]["vnc_args"] = profile.vnc_args
            if profile.log_file is not None:
                config[name]["log_file"] = profile.log_file
        with open(filename, "wb") as f:
            config.write(f)


def _cbool(value):
    if isinstance(value, bool): return value
    return value is not None and \
           str(value).upper() in ["TRUE", "T", "YES", "Y", "1"]


def _expand(value):
    return os.path.expandvars(os.path.expanduser(value))


def _is_empty(value):
    return value is None or len(value) == 0


def _is_port(value):
    return isinstance(value, (int,long)) and value > 0 and value < 65536
