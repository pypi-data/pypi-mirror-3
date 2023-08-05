## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>
"""
The yarest.gui package provides a wxWindows interface
that can be launched in one of two manners. The first
and more common use is by calling the `run()` method,
which assumes that it is being called from the shell
and looks for various command line arguments to use.
In this case a wx.App object will be automatically
setup and configured for the main program window.

Example script:
===============
#! /usr/bin/env python
import yarest.gui
yarest.gui.run()

Assuming the above script was named "launch.py", invoking it as
"launch.py --help" will list the available command line options.

The other option available is direct use of the `MainWindow` class, and in
this case callers must use their own wx.App object. Please note that there
are a few methods which must be overriden within the wx.App object in order
for iconizing functionality to work as expected, an example is shown below:

import wx

class MyCustomApp (wx.App):
    def GetYarestWindow(self):
        # if you set it as the top window,
        # otherwise modify as necessary
        self.GetTopWindow()

    def MacReopenApp(self):
        self.GetYarestWindow().Raise()

    def OnActivate(self, event):
        if event.GetActive():
            self.GetYarestWindow().Raise()
        event.Skip()

    def OnInit(self):
        # init code here
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        return True
"""
from ._main import MainWindow
from ._run import getopts, run

__all__ = ["MainWindow", "getopts", "run"]
