Building the installer
======================

1. Open the "x86.nsh" file and change the version number appropriately, also
   review the download variables to ensure they are up-to-date and accurate.
   If this is the first build make sure the dependencies at the top are met.

2. Open the "consumer-x86.nsi" and "provider-x86.nsi" files and change the
   "RootSrcDir" definition at the very top to match the build environment.

   Also this is where you will probably want to start customizing for your
   environment. The functions defined in these files are intended to be a
   a very simple starting point for your own modifications; i.e. your own
   "profiles.ini", and perhaps also the install of your own VNC variant.

3. Open a terminal and change to the directory containing this file, then
   run "makensis consumer-x86.nsi" and/or "makensis provider-x86.nsi".

Notes
=====

The author does not have any 64-bit versions of Windows to test on, thus
he didn't create any x64 installers; for anyone with a working knowledge
of NSIS (like more than the 24 hours my brain could handle) it shouldn't
be too difficult to create another set of x64 consumer/provider scripts.

1. Copy "x86.nsh" to "x64.nsh", review and modify definitions appropriately.

2. Copy "consumer-x86.nsi" and "provider-x86.nsi" to "consumer-x64.nsi" and
   "provider-x64.nsi", open both and modify the main include as well as the
   AppOutputFile appropriately.
