## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>
"""
YAREST is a cross-platform support tool for tunneling various desktop sharing
programs via SSH. Most any desktop sharing program that can be invoked from a
shell, or is already running, and uses a TCP port for communication should in
theory work, though currently only VNC and RDP have been tested and verified.

The yarest package implements all of the basic functionality of the support
system and has no graphical dependencies so that the same functionality can
be incorporated into your own interface. Those looking for code examples of
how to utilize this package to such an extent should look at the yarest.gui
source for a fully functional wxPython implementation.

This package defines the `SupportEntity` class to represent each of the two
entities involved in the support process, internally we sometimes call them
the "consumer" (receiving support) and "provider" (giving support). Both of
them must have a `ConnectionProfile` defining the basic session properties,
and optionally either or both can utilize your own custom `SupportExtender`
implementation to execute additional logic during the support session. See
comments of the `SupportEntity`, `SupportExtender` and `ConnectionProfile`
classes for more information.

The SSH functionality of this package is defined in the `SSHClient` class,
which is basically just a simplified wrapper for the fabulous ssh/paramiko
library class of the same name. It was designed purely for internal needs,
but it may be useful to others because of its simple methods for creating
and destroying arbitrary forward and reverse tunnels.
"""
from sys import version_info
if version_info < (2, 6):
    from ._messages import err_python_version
    raise RuntimeError(err_python_version)
del version_info

from ._exceptions import (ConnectionException, InvalidOperationException,
                          SSHException, AuthenticationException,
                          HostKeyException, KeyfileException,
                          PasswordRequired, UnsupportedAuthenticationType,
                          AutoRejectedHostKey, UserRejectedHostKey)
from ._profiles import ConnectionProfile, TunnelDirection
from ._ssh import SSHClient, AutoRejectPolicy, PromptUserPolicy
from ._support import (SupportEntity, SupportExtender)

__all__ = [ "ConnectionProfile",
            "TunnelDirection",
            "SupportEntity",
            "SupportExtender",
            "SSHClient",
            "AutoRejectPolicy",
            "PromptUserPolicy",
            "ConnectionException",
            "InvalidOperationException",
            "SSHException",
            "AuthenticationException",
            "HostKeyException",
            "KeyfileException",
            "PasswordRequired",
            "UnsupportedAuthenticationType",
            "AutoRejectedHostKey",
            "UserRejectedHostKey" ]

__author__ = "Mike Fled <nonvenia@gmail.com>"
__date__ = "30 Jun 2012"
__version__ = "0.5.0"
__version_info__ = (0, 5, 0)
__license__ = "MIT License (MIT)"
