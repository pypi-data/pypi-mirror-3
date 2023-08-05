## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

import errno, os, wx

from logging import Formatter, getLogger
from logging.handlers import RotatingFileHandler
from wx.lib.intctrl import IntCtrl
from yarest import (SupportConsumer, SupportProvider, SupportDirection,
                    SupportRole, ConnectionProfile, ConnectionException,
                    SSHException, UserRejectedHostKey)

from ._about import AboutWindow
from ._constants import (ACCESS_CODE_MIN, ACCESS_CODE_MAX, APP_NAME,
                         BLANK_LINES, DEFAULT_LOG_FORMAT,
                         DEFAULT_LOG_FORMAT_DATE, DEFAULT_LOG_LEVEL,
                         LOG_ROTATE_COUNT, LOG_ROTATE_SIZE, NO_RESIZE, UTF8)
from ._edit import EditProfilesDialog
from ._images import get_icon_bundle
from ._messages import (app_exit, app_start, connectionprofile_config,
                        connectionprofile_list_added,
                        connectionprofile_list_cleared,
                        connectionprofile_list_created, err_access_code,
                        err_logfile, err_profile_file_create,
                        err_profile_file_parse, err_profile_none, err_role,
                        err_unexpected, iconify_hide, iconify_show,
                        inputs_disabled, inputs_connect_clicked,
                        inputs_connect_enabled, inputs_disconnect_clicked,
                        inputs_disconnect_enabled, label_access_code,
                        label_connection_profile, label_disconnect,
                        label_error, label_exit, label_password, label_show,
                        menu_edit_label, menu_edit_profiles_desc,
                        menu_edit_profiles_label, menu_file_label,
                        menu_file_quit_desc, menu_file_quit_label,
                        menu_help_label, menu_help_about_desc,
                        menu_help_about_label, profiles_edit_enabled,
                        profiles_file_created, prompt_close_main_logmsg,
                        prompt_close_main_message, prompt_close_main_title,
                        prompt_unknown_host_message, prompt_unknown_host_title,
                        tooltip_access_code, tooltip_password)

# layout variables
access_code_height = -1
access_code_width = 65

password_height = -1
password_width = 190

button_flags = wx.ALIGN_CENTER | wx.EXPAND
input_flags = wx.ALIGN_LEFT
label_flags = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL

sizer_padding = 15
widget_padding = 10

# widget identifiers
ID_CONNECT = 1000
ID_DISCONNECT = 1001


class MainWindow (wx.Frame):
    def __init__(self, parent, profiles, logfile, encoding=UTF8,
                 editable=True, extender=None, role=SupportRole.Consumer,
                 direction=SupportDirection.Forward):
        """
        Initializes and displays the main window.

        Args:
            parent (wx.Window)                  : the parent window to assign this window.
            profiles (str)                      : the connection profile(s) config file to use.
            logfile (str)                       : the logging output file to use.

        Kwargs:
            encoding (str)                      : the encoding of `profiles` and `logfile`, default: "utf-8".
            editable (bool)                     : False to disable editing of connection profiles, default: True.
            extender (yarest.SupportExtender)   : The custom support extender instance to use, default: None.
            role (yarest.SupportRole)           : SupportRole.Consumer or SupportRole.Provider, default: SupportRole.Consumer.
            direction (yarest.SupportDirection) : SupportDirection.Forward or SupportDirection.Reverse, default: SupportDirection.Forward.

        *NOTES*

        The following are considered fatal and will prevent the window from
        initializing, though an error message will always be displayed and
        when possible the relevant exception information will be logged.

        * If the file path specified by `logfile` can't be written to.
        * If the `profiles` file doesn't exist and can't be created.
        * If the `profiles` file configuration format is malformed.
        * If the `profiles` file contains any invalid values.
        * If `role` is not SupportRole.Consumer or SupportRole.Provider.
        """
        self._configfile = profiles
        self._direction = direction
        self._encoding = encoding
        self._extender = extender
        self._gridsizer = None
        self._logger = None
        self._logfile = logfile
        self._panel = None
        self._profile_chooser = None
        self._profiles = None
        self._role = role
        self._staticprofile = None
        self._support = None
        self._taskbaricon = None
        self.running = False

        # init window
        wx.Frame.__init__(self, parent=parent, id=wx.ID_ANY, title=APP_NAME,
                          style=wx.DEFAULT_FRAME_STYLE & ~ (wx.MAXIMIZE_BOX |
                                                            wx.RESIZE_BORDER))
        self.Bind(wx.EVT_CLOSE, self._on_close)

        # verify that the given role is valid
        if self._role != SupportRole.Consumer and \
           self._role != SupportRole.Provider:
            self._display_error(err_role)
            self.Destroy()
            return

        # init logger
        try:
            handler = RotatingFileHandler(filename=self._logfile,
                                          maxBytes=LOG_ROTATE_SIZE,
                                          backupCount=LOG_ROTATE_COUNT,
                                          encoding=self._encoding, delay=False)
        except IOError as e:
            self._display_error(err_logfile + BLANK_LINES + str(e))
            self.Destroy()
            return

        handler.setFormatter(Formatter(fmt=DEFAULT_LOG_FORMAT,
                                       datefmt=DEFAULT_LOG_FORMAT_DATE))
        self._logger = getLogger(APP_NAME)
        self._logger.addHandler(handler)
        self._logger.setLevel(DEFAULT_LOG_LEVEL)
        self._logger.info(app_start % (APP_NAME))

        # verify config file path is usable and parse connection profiles
        self._logger.info(connectionprofile_config % (self._configfile))
        try:
            self._profiles = ConnectionProfile.read_from_file(self._configfile,
                                                              self._encoding)
        except IOError:
            try:
                with open(self._configfile, "a"): pass
                self._logger.info(profiles_file_created % (self._configfile))
                self._profiles = []
            except IOError as e:
                self._logger.exception(err_profile_file_create)
                self._display_error(err_profile_file_create + \
                                    BLANK_LINES + str(e))
                self.Destroy()
                return
        except Exception as e:
            self._logger.exception(err_profile_file_parse)
            self._display_error(err_profile_file_parse + BLANK_LINES + str(e))
            self.Destroy()
            return

        # add menu bar
        menubar = wx.MenuBar()

        menu = wx.Menu()
        menu_quit = menu.Append(id=wx.ID_EXIT, text=menu_file_quit_label,
                                help=menu_file_quit_desc)
        self.Bind(wx.EVT_MENU, self._on_close, menu_quit)
        menubar.Append(menu, menu_file_label)

        if editable:
            self._logger.info(profiles_edit_enabled)
            menu = wx.Menu()
            menu_edit = menu.Append(id=wx.ID_EDIT, text=menu_edit_profiles_label,
                                    help=menu_edit_profiles_desc)
            self.Bind(wx.EVT_MENU, self._on_edit_profiles, menu_edit)
            menubar.Append(menu, menu_edit_label)

        menu = wx.Menu()
        menu_about = menu.Append(id=wx.ID_ABOUT, text=menu_help_about_label,
                                 help=menu_help_about_desc % (APP_NAME))
        self.Bind(wx.EVT_MENU, self._on_about, menu_about)
        menubar.Append(menu, menu_help_label)

        self.SetMenuBar(menubar)

        # add layout controls
        self._panel = wx.Panel(self)

        outersizer = wx.BoxSizer(wx.HORIZONTAL)
        self._gridsizer = wx.FlexGridSizer(rows=0, cols=2,
                                           vgap=widget_padding,
                                           hgap=widget_padding)
        buttonsizer = wx.BoxSizer(wx.VERTICAL)

        outersizer.Add(self._gridsizer, NO_RESIZE,
                       wx.EXPAND | wx.ALL, sizer_padding)
        outersizer.Add(buttonsizer, NO_RESIZE,
                       wx.EXPAND | wx.ALL, sizer_padding)

        # add connection profiles control
        if editable or len(self._profiles) > 1:
            self._add_profiles()

        # add access code control
        access_code_label = wx.StaticText(self._panel, wx.ID_ANY,
                                          label_access_code)
        self._gridsizer.Add(access_code_label, NO_RESIZE, label_flags)

        if self._direction == SupportDirection.Forward:
            self._access_code = IntCtrl(self._panel, wx.ID_ANY,
                                        value=None,
                                        size=(access_code_width,
                                              access_code_height),
                                        min=0, max=ACCESS_CODE_MAX,
                                        allow_none=True, oob_color=wx.BLACK)
            self._access_code.SetToolTip(wx.ToolTip(tooltip_access_code))
        else:
            self._access_code = wx.StaticText(self._panel, wx.ID_ANY)

        self._gridsizer.Add(self._access_code, NO_RESIZE, input_flags)

        # add password control
        password_label = wx.StaticText(self._panel, wx.ID_ANY, label_password)
        self._gridsizer.Add(password_label, NO_RESIZE, label_flags)

        self._password = wx.TextCtrl(self._panel, wx.ID_ANY,
                                     size=(password_width, password_height),
                                     style=wx.TE_PASSWORD)
        self._password.SetToolTip(wx.ToolTip(tooltip_password))
        self._gridsizer.Add(self._password, NO_RESIZE, input_flags)

        # provider/consumer init logic
        if self._role == SupportRole.Consumer:
            from ._messages import label_connect_consumer as l_connect
            from ._messages import label_disconnect_consumer as l_disconnect
            from ._messages import tooltip_connect_consumer as t_connect
            from ._messages import tooltip_disconnect_consumer as t_disconnect
        else:
            from ._messages import label_connect_provider as l_connect
            from ._messages import label_disconnect_provider as l_disconnect
            from ._messages import tooltip_connect_provider as t_connect
            from ._messages import tooltip_disconnect_provider as t_disconnect

        # add connect and disconnect buttons
        self._connect = wx.Button(self._panel, ID_CONNECT, l_connect)
        wx.EVT_BUTTON(self, ID_CONNECT, self._on_connect)
        self._connect.SetToolTip(wx.ToolTip(t_connect))

        self._disconnect = wx.Button(self._panel, ID_DISCONNECT, l_disconnect)
        wx.EVT_BUTTON(self, ID_DISCONNECT, self._on_disconnect)
        self._disconnect.SetToolTip(wx.ToolTip(t_disconnect))

        buttonsizer.AddStretchSpacer()
        buttonsizer.Add(self._connect, NO_RESIZE, button_flags)
        buttonsizer.AddSpacer(widget_padding)
        buttonsizer.Add(self._disconnect, NO_RESIZE, button_flags)
        buttonsizer.AddStretchSpacer()

        # setup the taskbar icon
        if "wxMac" in wx.PlatformInfo:
            # osx uses 128x128 for the dock
            from ._images import logo_128
            icon = wx.IconFromBitmap(logo_128.GetBitmap())
        else:
            # everyone else uses 16x16 until proven otherwise
            from ._images import logo_16
            icon = wx.IconFromBitmap(logo_16.GetBitmap())
        self._taskbaricon = _TaskBarIcon(self, icon)
        self.Bind(wx.EVT_ICONIZE, self._on_iconize)

        # resize and display the window
        self._panel.SetSizerAndFit(outersizer)
        self.SetIcons(get_icon_bundle())
        self.SetSizerAndFit(outersizer)
        self.SetThemeEnabled(True)
        self.CentreOnScreen()
        self.Show(True)

        # populate the connection profiles
        if editable:
            if len(self._profiles) != 0:
                self._load_profiles()
            else:
                self._edit_profiles(True, True)
        elif len(self._profiles) > 1:
            self._load_profiles()
        elif len(self._profiles) == 1:
            self._staticprofile = self._profiles[0]
        else:
            self._edit_profiles(False, True)

        self._enable_connect()

    def _add_profiles(self):
        profile_label = wx.StaticText(self._panel, wx.ID_ANY,
                                      label_connection_profile)
        self._gridsizer.Add(profile_label, NO_RESIZE, label_flags)

        self._profile_chooser = wx.ComboBox(self._panel, wx.ID_ANY,
                                            style=wx.CB_READONLY | wx.CB_SORT)
        self._gridsizer.Add(self._profile_chooser, NO_RESIZE, input_flags)
        self._logger.debug(connectionprofile_list_created %
                           (self.__class__.__name__))

    def _disable_inputs(self):
        if self._profile_chooser is not None:
            self._profile_chooser.Enable(False)
        self._access_code.Enable(False)
        self._password.Enable(False)
        self._connect.Enable(False)
        self._disconnect.Enable(False)
        self._logger.debug(inputs_disabled)

    def _display_error(self, error):
        msgbox = wx.MessageDialog(self, str(error), label_error,
                                  style=wx.OK | wx.ICON_ERROR)
        msgbox.ShowModal()
        msgbox.Destroy()

    def _edit_profiles(self, multiple, required=False):
        editwin = EditProfilesDialog(self, self._configfile, self._encoding,
                                     self._logger, self._profiles, multiple)
        editwin.Centre()
        editwin.ShowModal()

        if editwin.IsUpdated():
            self._profiles = editwin.GetProfiles()
            if multiple:
                self._load_profiles()
            else:
                self._staticprofile = self._profiles[0]
            editwin.Destroy()
        elif required:
            editwin.Destroy()
            msgbox = wx.MessageDialog(self, err_profile_none, label_error,
                                      style=wx.YES_NO | wx.NO_DEFAULT |
                                            wx.ICON_ERROR)
            result = msgbox.ShowModal()
            msgbox.Destroy()
            if result != wx.ID_YES:
                self._edit_profiles(multiple, required)
            else:
                wx.CallAfter(self.Close)

    def _enable_connect(self):
        if self._profile_chooser is not None:
            self._profile_chooser.Enable(True)
        self._access_code.Enable(True)
        if self._direction == SupportDirection.Reverse:
            self._access_code.SetLabel("")
        self._password.Enable(True)
        self._connect.Enable(True)
        self._disconnect.Enable(False)
        self._logger.debug(inputs_connect_enabled)
        self.running = False

    def _enable_disconnect(self):
        self._disconnect.Enable(True)
        self._logger.debug(inputs_disconnect_enabled)
        self.running = True

    def _load_profiles(self):
        self._profile_chooser.Clear()
        self._logger.debug(connectionprofile_list_cleared %
                           (self.__class__.__name__))
        for profile in self._profiles:
            self._profile_chooser.Append(profile.name)
            self._logger.debug(connectionprofile_list_added %
                               (self.__class__.__name__, profile.name))
        self._profile_chooser.SetSelection(0)

    def _on_about(self, event):
        about = AboutWindow(self)
        about.ShowModal()
        about.Destroy()

    def _on_close(self, event):
        if self.running:
            self._logger.debug(prompt_close_main_logmsg)
            msgbox = wx.MessageDialog(self, prompt_close_main_message,
                                      prompt_close_main_title,
                                      style=wx.YES_NO | wx.NO_DEFAULT |
                                            wx.ICON_QUESTION)
            result = msgbox.ShowModal()
            msgbox.Destroy()
            if result != wx.ID_YES: return

            self.disconnect()
        self._logger.info(app_exit % (APP_NAME))
        self._taskbaricon.Destroy()
        self.Destroy()

    def _on_connect(self, event):
        self._logger.debug(inputs_connect_clicked)
        self._disable_inputs()

        # determine the connection profile to use
        if self._staticprofile is None:
            profile_name = self._profile_chooser.GetValue()
            for p in self._profiles:
                if p.name == profile_name:
                    profile = p
                    break
        else:
            profile = self._staticprofile

        # validate the access code if applicable
        if self._direction == SupportDirection.Forward:
            access_code = self._access_code.GetValue()
            if access_code is None or \
               access_code < ACCESS_CODE_MIN or \
               access_code > ACCESS_CODE_MAX or \
               access_code == profile.ssh_port:
                self._enable_connect()
                self._display_error(err_access_code)
                return

        if self._role == SupportRole.Consumer:
            SupportObj = SupportConsumer
        else:
            SupportObj = SupportProvider

        # initialize the support object
        try:
            self._support = SupportObj(profile, self._extender, self._logger,
                                       self._prompt_unknown_host,
                                       self._direction)
        except IOError as e:
            self._logger.exception(err_logfile)
            self._enable_connect()
            self._display_error(err_logfile + BLANK_LINES + str(e))
            return
        except Exception as e:
            self._logger.exception(err_unexpected)
            self._enable_connect()
            self._display_error(err_unexpected + BLANK_LINES + str(e))
            return

        # establish the connection
        try:
            self._support.connect(self._password.GetValue())
        except UserRejectedHostKey:
            self._enable_connect()
            return
        except (ConnectionException, SSHException) as e:
            self._enable_connect()
            self._display_error(e)
            return
        except Exception as e:
            self._enable_connect()
            self._display_error(err_unexpected + BLANK_LINES + str(e))
            return

        # start the session
        try:
            if self._direction == SupportDirection.Reverse:
                access_code = self._support.start_session()
                self._access_code.SetLabel(str(access_code))
                self._access_code.Enable(True)
            else:
                self._support.start_session(access_code)
                self.Iconize(True)
        except (ConnectionException, SSHException) as e:
            self.disconnect()
            self._display_error(e)
            return
        except Exception as e:
            self.disconnect()
            self._display_error(err_unexpected + BLANK_LINES + str(e))
            return

        self._enable_disconnect()

    def _on_disconnect(self, event):
        self._logger.debug(inputs_disconnect_clicked)
        self.disconnect()

    def _on_edit_profiles(self, event):
        self._edit_profiles(True)

    def _on_iconize(self, event):
        if event.Iconized():
            self._logger.debug(iconify_hide)
            self.Iconize(True)
            self.Hide()
        else:
            self._logger.debug(iconify_show)
            self.Iconize(False)
            self.Show()
            self.Raise()

    def _prompt_unknown_host(self, hostname, keytype, fingerprint):
        msgbox = wx.MessageDialog(self, prompt_unknown_host_message %
                                        (hostname, keytype, fingerprint),
                                  prompt_unknown_host_title,
                                  style=wx.YES_NO | wx.NO_DEFAULT |
                                        wx.ICON_EXCLAMATION)
        result = msgbox.ShowModal()
        msgbox.Destroy()
        return result == wx.ID_YES

    def disconnect(self):
        if self._support is not None:
            self._support.stop_session()
            self._support = None
        self._enable_connect()


class _TaskBarIcon (wx.TaskBarIcon):
    def __init__(self, parent, icon):
        wx.TaskBarIcon.__init__(self)
        self.parent = parent
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self._show_window)
        self.Bind(wx.EVT_TASKBAR_RIGHT_UP, self._show_menu)
        self.SetIcon(icon, APP_NAME)

    def _disconnect(self, event):
        self.parent.disconnect()
        self._show_window(None)

    def _exit(self, event):
        self.parent.Close()

    def _show_menu(self, event):
        menu = wx.Menu()

        if not self.parent.IsShown():
            show = menu.Append(wx.ID_ANY, label_show)
            self.Bind(wx.EVT_MENU, self._show_window, show)
        if self.parent.running:
            disconnect = menu.Append(wx.ID_ANY, label_disconnect)
            self.Bind(wx.EVT_MENU, self._disconnect, disconnect)
        exit = menu.Append(wx.ID_ANY, label_exit)
        self.Bind(wx.EVT_MENU, self._exit, exit)

        self.PopupMenu(menu)
        menu.Destroy()

    def _show_window(self, event):
        if self.parent.IsIconized():
            self.parent.Iconize(False)
        if not self.parent.IsShown():
            self.parent.Show()
        self.parent.Raise()
