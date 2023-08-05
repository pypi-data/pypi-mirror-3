## -*- coding: utf-8 -*-
# Copyright © 2011 Mike Fled <nonvenia@gmail.com>
"""
YAREST is a cross-platform support tool for securely tunneling VNC over SSH.

The yarest package implements all of the basic functionality of the support
system and has no graphical dependencies so that the same functionality can
be incorporated into your own interface. Those looking for code examples of
how to utilize this package to such an extent should look at the yarest.gui
source for a fully functional wxPython implementation.

This package defines the `SupportProvider` and `SupportConsumer` classes to
represent the two entities involved in the support process. The information
needed to connect the two of them comes from the `ConnectionProfile` used,
and optionally a `SupportExtender` can be defined to execute custom logic
during a support session.

A basic overview of the process, with some technical details, is as follows:

 1. The `SupportProvider` connects to the SSH server and starts a session.

    This allocates a random internal port number on the server and creates a
    reverse SSH tunnel which starts at the server port and ends at the local
    port number configured for VNC. The VNC viewer program is then launched
    in "listen" mode and simply waits for a VNC server connection request.

 2. The `SupportProvider` transmits the "access code" to the `SupportConsumer`.

    The "access code" is simply that random server port number allocated for
    the session. This exchange could be done over the phone, chat, e-mail, a
    custom software system, really fast courier pigeons, however you choose.

 3. The `SupportConsumer` connects to the SSH server and the provider session.

    This creates an SSH forward tunnel from their local VNC port number to the
    "access code" port number on the server, and then a VNC server is launched
    in "reverse connection" mode. The connection request gets transported over
    the tunnel to the server who then connects them with the support provider.

The SSH functionality of this package is defined in the `SSHClient` class,
which is essentially a simple wrapper around the fabulous Paramiko library
class of the same name. Its design was really only to meet internal needs,
but it may be useful to others because of its simple methods for creating
and destroying arbitrary forward and reverse tunnels.
"""
from sys import version_info
if version_info < (2, 6):
    from ._messages import err_version_python
    raise RuntimeError(err_version_python)
del version_info

from ._exceptions import (ConnectionException, InvalidOperationException,
                          SSHException, AuthenticationException,
                          HostKeyException, KeyfileException,
                          PasswordRequired, UnsupportedAuthenticationType,
                          AutoRejectedHostKey, UserRejectedHostKey)
from ._profiles import ConnectionProfile
from ._ssh import SSHClient, AutoRejectPolicy, PromptUserPolicy
from ._support import (SupportConsumer, SupportProvider,
                       SupportExtender, SupportRole)

__all__ = [ "ConnectionProfile",
            "SupportConsumer",
            "SupportProvider",
            "SupportExtender",
            "SupportRole",
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
__date__ = "17 Dec 2011"
__version__ = "0.3.0"
__version_info__ = (0, 3, 0)
__license__ = "MIT License (MIT)"
