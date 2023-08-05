======
YAREST
======

A simple system in Python to tunnel VNC over SSH.

YAREST was designed, and written, to help those who help others.

This software is geared primarily towards technical providers that are looking
for a customizable cross-platform solution. To use the system an SSH server is
required; if you can comfortably setup and manage one or more servers that are
used purely for authentication and TCP forwarding by both your technicians and
end-users, then this software may be of service to you.


Features
========

- Extremely simple GUI for both your end-users and technicians

- Core yarest package exports all of the functionality independent of the GUI

- Usable with absolutely any VNC variant

- Requires only outbound connectivity for both technician and end-user when the SSH server is on a 3rd machine

- Supports multiple "connection profiles" to enable use of multiple SSH servers

- Supports executing your own custom code during sessions via the "SupportExtender" interface

- Includes an NSIS installer for Windows that can download and install all the necessary Python dependencies


How It Works
============

- `Provider` = Person who is giving remote support
- `Consumer` = Person who is receiving remote support
- `Server`   = SSH server that both Provider and Consumer can connect to

Provider Initiated (default)
----------------------------

1. `Provider` connects to `Server`, reverse forwards random internal server port to
   local VNC port, starts VNC viewer in listen mode bound to "localhost:VNC port".

2. `Provider` gives random server port number ("access code") to `Consumer`.

3. `Consumer` connects to `Server`, forwards local VNC port to remote server port,
   starts VNC server in reverse connection mode bound to "localhost:VNC port".

4. `Server` receives the connection request from `Consumer`, forwards it over to
   `Provider`, then `Server` routes the VNC conversation between the two tunnels
   until either side ends the support session.

Consumer Initiated
------------------

1. `Consumer` connects to `Server`, reverse forwards random internal server port to
   local VNC port, starts VNC server in listen mode bound to "localhost:VNC port".

2. `Consumer` gives random server port number ("access code") to `Provider`.

3. `Provider` connects to `Server`, forwards local VNC port to remote server port,
   starts VNC client in regular connection mode bound to "localhost:VNC port".

4. `Server` receives the connection request from `Provider`, forwards it over to
   `Consumer`, then `Server` routes the VNC conversation between the two tunnels
   until either side ends the support session.


SSH Server Security Considerations
==================================

Only the main SSH port needs to be accessible on any server(s) used,
and ideally such is the only port open on any server(s) firewall(s).

Unless you have a need otherwise, the simplest option is usually
to chroot the entire SSH server to the bare-minimum environment.

If you do need the SSH server for other purposes, then setup groups for your
technicians and end-users and confine them to their own chroot environments.


Dependencies
============

- `Python`     >= 2.6    (Tested with 2.6 and 2.7, untested on 3.x)
- `Paramiko`   >= 1.7.4
- `pycrypto`             (Required by paramiko)
- `configObj`            (Tested with 4.7.2)
- `psutil`               (Tested with 0.4)
- `wxPython`             (Tested with 2.8.10) [Only required by the `yarest.gui` package]
- `setuptools`           [If you don't have it already we'll install the included `Distribute`]


Installation
============

Providers should consider creating their own simple installation package
to automate these steps and include their own pre-configured profile(s).
On Linux that could be done an infinite number of ways, for a countless
number of distros, so nothing is provided beyond this documentation. On
Windows the included NSIS installer should be a good starting point for
most needs.

Steps for a functionally complete installation are as follows:


On Linux:
---------
1. Install the desired VNC variant, if unsure use `x11vnc` if you're the
   consumer (getting remote help) or `vnc4viewer` if you're the provider
   (giving remote help); your distribution most likely has packages.

   On Debian (as root):

   `apt-get install x11vnc`

   -or-

   `apt-get install vnc4viewer`

2. Install the dependencies that `setuptools` cannot fulfill, these are
   `Python`, `pyCrypto` and `wxPython`; your distribution has packages.

   On Debian (as root):

   `apt-get install python2.6 python-crypto python-wxgtk2.8`

3. Optionally install additional dependencies so `setuptools` doesn't have to.

   On Debian ["Squeeze" or later] (as root):

   `apt-get install python-configobj python-paramiko`

4. Download the `yarest` source distribution zip and extract it somewhere,
   in the following we assume the extracted folder is "/tmp/yarest-0.3.0".

5. Open a root terminal and change to that folder: `cd /tmp/yarest-0.3.0`.

6. In the same terminal: `python setup.py install`.

7. Upon completion an executable script `yarest` is created.

   `yarest --help` will list the available command line options.

8. To use the program you need one or more "connection profiles", if
   you don't have a profile it will simply prompt you to create one.

   The "examples" folder in the source distribution contains a "profiles.ini"
   file with samples that you should be able to adapt for your own use.


On Windows:
-----------
1. Install a usable VNC variant, such as UltraVNC which you can download from:

   http://www.uvnc.com/downloads/ultravnc.html

   When installing you need the "VNC Viewer" if you're the provider (giving remote
   help), or the "VNC Server" if you're the consumer (getting remote help). Do not
   select the option to install the "VNC Server" as a service.

2. Download and install either the "consumer-win32.exe" or "provider-win32.exe"
   pre-built binary from the YAREST home page:

   http://code.google.com/p/yarest/

   The installer is made with NSIS and accomodates the most common scenarios;
   i.e. Windows computers with either 0 or 1 usable Python runtimes installed.
   If any runtime is found it's always used, otherwise we download and install.

   The installer has been tested with runtimes from the standard python.org
   distribution, whether it works with any other Python flavor is untested.

   Anyone willing to dive into NSIS should be able to modify it easily enough,
   see the included "README.txt" in the installer folder for the basic steps.

3. The installer creates a shortcut in the "Start Menu" to run `YAREST`.

   To use the program you need one or more "connection profiles", if
   you don't have a profile it will simply prompt you to create one.

   The installer creates an "examples" folder under the installation folder
   (default:"%PROGRAMFILES%\\YAREST\\examples") and within that folder is a
   "profiles.ini" file with samples that you can adapt for your own use, as
   well as an "ultravnc.ini" file that you can use as the configuration file
   for UltraVNC (To use the config file it needs to be moved to the UltraVNC
   installation folder, which is "%PROGRAMFILES%\\UltraVNC" by default).


Bugs
====

Can be submitted via the issue tracker.

http://code.google.com/p/yarest/issues
