## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

import wx

from configobj import __version__ as version_configobj
from Crypto import __version__ as version_pycrypto
from paramiko import __version__ as version_paramiko
from platform import python_version as version_python
from psutil import __version__ as version_psutil
from wx import __version__ as version_wxpython
from yarest import __version__ as version_yarest

from ._constants import APP_NAME, BLANK_LINES, NO_RESIZE, RESIZABLE, UTF8
from ._docs import license, acknowledgements
from ._images import logo_128
from ._messages import (label_about, label_acknowledgements, label_license,
                        label_version, label_versions, label_website)


# layout variables
header_flags = wx.ALIGN_CENTER | wx.ALL

logo_flags = wx.ALIGN_RIGHT | wx.ALL
logo_height = 128
logo_width = 128

tabs_height = 256
tabs_width = 512

url_flags = wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.LEFT | wx.RIGHT | wx.TOP
version_flags = wx.ALIGN_LEFT | wx.ALIGN_TOP | wx.LEFT | wx.RIGHT | wx.TOP
widget_padding = 7

class AboutWindow (wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, label_about % (APP_NAME),
                           style=wx.CLOSE_BOX | wx.MINIMIZE_BOX)
        self.Bind(wx.EVT_CLOSE, self._on_close)

        # inner layout sizers
        headersizer = wx.BoxSizer(wx.HORIZONTAL)
        header_textsizer = wx.BoxSizer(wx.VERTICAL)
        header_logosizer = wx.BoxSizer(wx.VERTICAL)
        tabsizer = wx.BoxSizer(wx.HORIZONTAL)
        footersizer = wx.BoxSizer(wx.HORIZONTAL)

        # header text
        desc = wx.StaticText(self, wx.ID_ANY, "Yet Another REmote Support Tool")
        self._set_font_bold(desc)
        header_textsizer.Add(desc, NO_RESIZE, header_flags, widget_padding)

        version = wx.StaticText(self, wx.ID_ANY,
                                label_version + " " + version_yarest)
        header_textsizer.Add(version, NO_RESIZE, header_flags, widget_padding)

        url = wx.HyperlinkCtrl(self, wx.ID_ANY, label_website,
                               "http://code.google.com/p/yarest/")
        header_textsizer.Add(url, NO_RESIZE, header_flags, widget_padding)

        headersizer.Add(header_textsizer, NO_RESIZE, wx.ALL, widget_padding)

        # header logo
        image = wx.StaticBitmap(self, wx.ID_ANY, logo_128.GetBitmap())
        header_logosizer.Add(image, NO_RESIZE, logo_flags, widget_padding)

        headersizer.Add(header_logosizer, NO_RESIZE, logo_flags, widget_padding)

        # notebook tabs
        notebook = wx.Notebook(self, size=(tabs_width, tabs_height))

        acknowledge_tab = _AcknowledgementsPanel(notebook)
        license_tab = _LicensePanel(notebook)
        versions_tab = _VersionsPanel(notebook)

        notebook.AddPage(acknowledge_tab, label_acknowledgements)
        notebook.AddPage(license_tab, label_license)
        notebook.AddPage(versions_tab, label_versions)

        tabsizer.Add(notebook, NO_RESIZE, wx.ALL, widget_padding)

        # footer
        okbutton = wx.Button(self, wx.ID_OK)
        wx.EVT_BUTTON(self, wx.ID_OK, self._on_close)
        footersizer.Add(okbutton, NO_RESIZE, wx.ALL, widget_padding)

        # add inner sizers to outer sizer
        outersizer = wx.BoxSizer(wx.VERTICAL)
        outersizer.Add(headersizer, NO_RESIZE, wx.ALIGN_CENTER)
        outersizer.Add(tabsizer, NO_RESIZE, wx.ALIGN_CENTER)
        outersizer.Add(footersizer, NO_RESIZE, wx.ALIGN_RIGHT)

        # resize and theme the window
        self.SetIcon(parent.GetIcon())
        self.SetSizerAndFit(outersizer)
        self.SetThemeEnabled(True)

    def _on_close(self, event):
        self.Destroy()

    def _set_font_bold(self, widget):
        font = widget.GetFont()
        font.SetWeight(wx.BOLD)
        widget.SetFont(font)


class _AcknowledgementsPanel (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        data = wx.TextCtrl(self, wx.ID_ANY, acknowledgements.encode(UTF8),
                           style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(data, RESIZABLE, wx.EXPAND)
        self.SetSizer(sizer)


class _LicensePanel (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        data = wx.TextCtrl(self, wx.ID_ANY, license.encode(UTF8),
                           style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(data, RESIZABLE, wx.EXPAND)
        self.SetSizer(sizer)


class _VersionsPanel (wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        gridsizer = wx.FlexGridSizer(rows=0, cols=2, vgap=0, hgap=0)

        url = wx.HyperlinkCtrl(self, wx.ID_ANY, "Python",
                               "http://www.python.org/")
        version = wx.StaticText(self, wx.ID_ANY, version_python())
        gridsizer.Add(url, NO_RESIZE, url_flags, widget_padding)
        gridsizer.Add(version, NO_RESIZE, version_flags, widget_padding)

        url = wx.HyperlinkCtrl(self, wx.ID_ANY, "wxPython",
                               "http://www.wxpython.org/")
        version = wx.StaticText(self, wx.ID_ANY, version_wxpython)
        gridsizer.Add(url, NO_RESIZE, url_flags, widget_padding)
        gridsizer.Add(version, NO_RESIZE, version_flags, widget_padding)

        url = wx.HyperlinkCtrl(self, wx.ID_ANY, "PyCrypto",
                               "http://www.pycrypto.org/")
        version = wx.StaticText(self, wx.ID_ANY, version_pycrypto)
        gridsizer.Add(url, NO_RESIZE, url_flags, widget_padding)
        gridsizer.Add(version, NO_RESIZE, version_flags, widget_padding)

        url = wx.HyperlinkCtrl(self, wx.ID_ANY, "Paramiko",
                               "http://www.lag.net/paramiko/")
        version = wx.StaticText(self, wx.ID_ANY, version_paramiko)
        gridsizer.Add(url, NO_RESIZE, url_flags, widget_padding)
        gridsizer.Add(version, NO_RESIZE, version_flags, widget_padding)

        url = wx.HyperlinkCtrl(self, wx.ID_ANY, "ConfigObj",
                               "http://www.voidspace.org.uk/python/configobj.html")
        version = wx.StaticText(self, wx.ID_ANY, version_configobj)
        gridsizer.Add(url, NO_RESIZE, url_flags, widget_padding)
        gridsizer.Add(version, NO_RESIZE, version_flags, widget_padding)

        url = wx.HyperlinkCtrl(self, wx.ID_ANY, "psutil",
                               "http://code.google.com/p/psutil/")
        version = wx.StaticText(self, wx.ID_ANY, version_psutil)
        gridsizer.Add(url, NO_RESIZE, url_flags, widget_padding)
        gridsizer.Add(version, NO_RESIZE, version_flags, widget_padding)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(gridsizer, RESIZABLE, wx.EXPAND)
        self.SetSizer(sizer)
