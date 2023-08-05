## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

import re, wx

from configobj import ConfigObj
from wx.lib.intctrl import IntCtrl
from yarest import ConnectionProfile

from ._constants import (BLANK_LINES, NO_RESIZE, PORT_NUMBER_MIN,
                         PORT_NUMBER_MAX, RESIZABLE)
from ._messages import (connectionprofile_list_added,
                        connectionprofile_list_cleared,
                        connectionprofile_list_created, err_profile_name,
                        err_unexpected, label_browse, label_error,
                        label_edit_window, label_profile_delete,
                        label_profile_name, label_profile_new,
                        label_profile_save, label_ssh_allow_unknown,
                        label_ssh_clientkeys, label_ssh_compression,
                        label_ssh_hostkeys, label_ssh_port,
                        label_ssh_server, label_ssh_username,
                        label_tcp_timeout, label_vnc_args, label_vnc_exec,
                        label_vnc_port, profile_added, profile_deleted,
                        profile_updated, profile_updated_name, profiles_saved,
                        prompt_delete_profile_message,
                        prompt_delete_profile_title,
                        tooltip_profile_name, tooltip_ssh_allow_unknown,
                        tooltip_ssh_clientkeys, tooltip_ssh_compression,
                        tooltip_ssh_hostkeys, tooltip_ssh_port,
                        tooltip_ssh_server, tooltip_ssh_username,
                        tooltip_tcp_timeout, tooltip_vnc_args,
                        tooltip_vnc_exec, tooltip_vnc_port)

# layout variables
input_int_height = -1
input_int_width = 65

input_text_height = -1
input_text_width = 225

profiles_height = -1
profiles_style = wx.LB_SINGLE | wx.LB_HSCROLL | wx.LB_SORT
profiles_width = 200

input_flags = wx.ALIGN_LEFT
label_flags = wx.ALIGN_RIGHT | wx.ALIGN_CENTER_VERTICAL

button_padding = 15
grid_padding = 5
widget_padding = 7

# widget identifiers
ID_CLIENTKEYS = 2000
ID_HOSTKEYS = 2001
ID_VNCEXEC = 2002


class EditProfilesDialog (wx.Dialog):
    def __init__(self, parent, filename, encoding, logger, profiles, multi):
        self._encoding = encoding
        self._filename = filename
        self._logger = logger
        self._multi = multi
        self._profile = None
        self._profiles = profiles
        self._updated = False
        wx.Dialog.__init__(self, parent, wx.ID_ANY, label_edit_window,
                           style=wx.CLOSE_BOX | wx.MINIMIZE_BOX)

        # init layout sizers
        outersizer = wx.BoxSizer(wx.VERTICAL)
        uppersizer = wx.BoxSizer(wx.HORIZONTAL)
        formsizer = wx.FlexGridSizer(rows=0, cols=3,
                                     vgap=grid_padding,
                                     hgap=grid_padding)
        lowersizer = wx.BoxSizer(wx.HORIZONTAL)

        # profile name
        label = wx.StaticText(self, wx.ID_ANY, label_profile_name)
        self._profile_name = wx.TextCtrl(self, wx.ID_ANY,
                                         size=(input_text_width,
                                               input_text_height))
        self._profile_name.SetToolTip(wx.ToolTip(tooltip_profile_name))
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._profile_name, RESIZABLE, input_flags)
        formsizer.Add(self._create_empty_grid_cell(), NO_RESIZE)

        # ssh server
        label = wx.StaticText(self, wx.ID_ANY, label_ssh_server)
        self._ssh_server = wx.TextCtrl(self, wx.ID_ANY,
                                       size=(input_text_width,
                                             input_text_height))
        self._ssh_server.SetToolTip(wx.ToolTip(tooltip_ssh_server))
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._ssh_server, RESIZABLE, input_flags)
        formsizer.Add(self._create_empty_grid_cell(), NO_RESIZE)

        # ssh port
        label = wx.StaticText(self, wx.ID_ANY, label_ssh_port)
        self._ssh_port = IntCtrl(self, wx.ID_ANY, value=None,
                                 size=(input_int_width,
                                       input_int_height),
                                 min=PORT_NUMBER_MIN,
                                 max=PORT_NUMBER_MAX,
                                 allow_none=True, oob_color=wx.BLACK)
        self._ssh_port.SetToolTip(wx.ToolTip(tooltip_ssh_port))
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._ssh_port, RESIZABLE, input_flags)
        formsizer.Add(self._create_empty_grid_cell(), NO_RESIZE)

        # ssh username
        label = wx.StaticText(self, wx.ID_ANY, label_ssh_username)
        self._ssh_username = wx.TextCtrl(self, wx.ID_ANY,
                                         size=(input_text_width,
                                               input_text_height))
        self._ssh_username.SetToolTip(wx.ToolTip(tooltip_ssh_username))
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._ssh_username, RESIZABLE, input_flags)
        formsizer.Add(self._create_empty_grid_cell(), NO_RESIZE)

        # ssh hostkeys
        label = wx.StaticText(self, wx.ID_ANY, label_ssh_hostkeys)
        self._ssh_hostkeys = wx.TextCtrl(self, wx.ID_ANY,
                                         size=(input_text_width,
                                               input_text_height))
        self._ssh_hostkeys.SetToolTip(wx.ToolTip(tooltip_ssh_hostkeys))
        b_hostkeys = wx.Button(self, ID_HOSTKEYS, label_browse)
        wx.EVT_BUTTON(self, ID_HOSTKEYS, self._on_browse_hostkeys)
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._ssh_hostkeys, RESIZABLE, input_flags)
        formsizer.Add(b_hostkeys, NO_RESIZE, input_flags)

        # ssh clientkeys
        label = wx.StaticText(self, wx.ID_ANY, label_ssh_clientkeys)
        self._ssh_clientkeys = wx.TextCtrl(self, wx.ID_ANY,
                                           size=(input_text_width,
                                                 input_text_height))
        self._ssh_clientkeys.SetToolTip(wx.ToolTip(tooltip_ssh_clientkeys))
        b_clientkeys = wx.Button(self, ID_CLIENTKEYS, label_browse)
        wx.EVT_BUTTON(self, ID_CLIENTKEYS, self._on_browse_clientkeys)
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._ssh_clientkeys, RESIZABLE, input_flags)
        formsizer.Add(b_clientkeys, NO_RESIZE, input_flags)

        # ssh allow unknown
        label = wx.StaticText(self, wx.ID_ANY, label_ssh_allow_unknown)
        self._ssh_allow_unknown = wx.CheckBox(self, wx.ID_ANY)
        self._ssh_allow_unknown.SetToolTip(wx.ToolTip(tooltip_ssh_allow_unknown))
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._ssh_allow_unknown, NO_RESIZE, input_flags)
        formsizer.Add(self._create_empty_grid_cell(), NO_RESIZE)

        # ssh compression
        label = wx.StaticText(self, wx.ID_ANY, label_ssh_compression)
        self._ssh_compression = wx.CheckBox(self, wx.ID_ANY)
        self._ssh_compression.SetToolTip(wx.ToolTip(tooltip_ssh_compression))
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._ssh_compression, NO_RESIZE, input_flags)
        formsizer.Add(self._create_empty_grid_cell(), NO_RESIZE)

        # tcp timeout
        label = wx.StaticText(self, wx.ID_ANY, label_tcp_timeout)
        self._tcp_timeout = IntCtrl(self, wx.ID_ANY, value=None,
                                    size=(input_int_width,
                                          input_int_height),
                                    allow_none=True, oob_color=wx.BLACK)
        self._tcp_timeout.SetToolTip(wx.ToolTip(tooltip_tcp_timeout))
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._tcp_timeout, RESIZABLE, input_flags)
        formsizer.Add(self._create_empty_grid_cell(), NO_RESIZE)

        # vnc executable
        label = wx.StaticText(self, wx.ID_ANY, label_vnc_exec)
        self._vnc_exec = wx.TextCtrl(self, wx.ID_ANY,
                                     size=(input_text_width,
                                           input_text_height))
        self._vnc_exec.SetToolTip(wx.ToolTip(tooltip_vnc_exec))
        b_vncexec = wx.Button(self, ID_VNCEXEC, label_browse)
        wx.EVT_BUTTON(self, ID_VNCEXEC, self._on_browse_vncexec)
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._vnc_exec, RESIZABLE, input_flags)
        formsizer.Add(b_vncexec, NO_RESIZE, input_flags)

        # vnc port
        label = wx.StaticText(self, wx.ID_ANY, label_vnc_port)
        self._vnc_port = IntCtrl(self, wx.ID_ANY, value=None,
                                 size=(input_int_width,
                                       input_int_height),
                                 min=PORT_NUMBER_MIN,
                                 max=PORT_NUMBER_MAX,
                                 allow_none=True, oob_color=wx.BLACK)
        self._vnc_port.SetToolTip(wx.ToolTip(tooltip_vnc_port))
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._vnc_port, RESIZABLE, input_flags)
        formsizer.Add(self._create_empty_grid_cell(), NO_RESIZE)

        # vnc arguments
        label = wx.StaticText(self, wx.ID_ANY, label_vnc_args)
        self._vnc_args = wx.TextCtrl(self, wx.ID_ANY,
                                     size=(input_text_width,
                                           input_text_height))
        self._vnc_args.SetToolTip(wx.ToolTip(tooltip_vnc_args))
        formsizer.Add(label, NO_RESIZE, label_flags)
        formsizer.Add(self._vnc_args, RESIZABLE, input_flags)
        formsizer.Add(self._create_empty_grid_cell(), NO_RESIZE)

        # save profile and close buttons
        b_save = wx.Button(self, wx.ID_SAVE, label_profile_save)
        wx.EVT_BUTTON(self, wx.ID_SAVE, self._on_click_save)

        b_close = wx.Button(self, wx.ID_CLOSE)
        wx.EVT_BUTTON(self, wx.ID_CLOSE, self._on_click_close)

        lowersizer.AddStretchSpacer()

        if self._multi:
            # setup delete and new profile buttons and add to lower sizer
            b_delete = wx.Button(self, wx.ID_DELETE, label_profile_delete)
            wx.EVT_BUTTON(self, wx.ID_DELETE, self._on_click_delete)
            lowersizer.Add(b_delete, NO_RESIZE)
            lowersizer.AddSpacer(button_padding)

            b_new = wx.Button(self, wx.ID_NEW, label_profile_new)
            wx.EVT_BUTTON(self, wx.ID_NEW, self._on_click_new)
            lowersizer.Add(b_new, NO_RESIZE)
            lowersizer.AddSpacer(button_padding)

            # setup profiles list control and add to upper sizer
            profilesizer = wx.BoxSizer(wx.HORIZONTAL)
            self._profiles_list = wx.ListBox(self, wx.ID_ANY,
                                             size=(profiles_width,
                                                   profiles_height),
                                             style=profiles_style)
            self._logger.debug(connectionprofile_list_created %
                               (self.__class__.__name__))
            self._populate_profiles_list()
            self._profiles_list.Bind(wx.EVT_LISTBOX, self._on_select_profile)
            profilesizer.Add(self._profiles_list, NO_RESIZE, wx.EXPAND)
            uppersizer.Add(profilesizer, NO_RESIZE,
                           wx.EXPAND | wx.ALL, widget_padding)

        # add form sizer to upper sizer
        uppersizer.Add(formsizer, RESIZABLE, wx.ALL, widget_padding)

        # add save profile and close buttons to lower sizer
        lowersizer.Add(b_save, NO_RESIZE)
        lowersizer.AddSpacer(button_padding)
        lowersizer.Add(b_close, NO_RESIZE)
        lowersizer.AddStretchSpacer()

        # add upper and lower sizers to outer sizer
        outersizer.Add(uppersizer, RESIZABLE, wx.ALL, widget_padding)
        outersizer.Add(lowersizer, NO_RESIZE,
                       wx.ALIGN_CENTER | wx.ALL, widget_padding)

        # resize and theme window
        self.SetIcon(parent.GetIcon())
        self.SetSizerAndFit(outersizer)
        self.SetThemeEnabled(True)

    def _browse_for_and_set_file(self, widget):
        dialog = wx.FileDialog(self, style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            widget.SetValue(dialog.GetPath())
        dialog.Destroy()

    def _create_empty_grid_cell(self):
        return wx.StaticText(self, wx.ID_ANY)

    def _display_error(self, error):
        msgbox = wx.MessageDialog(self, str(error), label_error,
                                  style=wx.OK | wx.ICON_ERROR)
        msgbox.ShowModal()
        msgbox.Destroy()

    def _get_form_profile(self):
        profile = ConnectionProfile(self._profile_name.GetValue())
        profile.ssh_server = self._ssh_server.GetValue()
        profile.ssh_port = self._ssh_port.GetValue()
        profile.ssh_username = self._ssh_username.GetValue()
        profile.ssh_hostkeys = self._ssh_hostkeys.GetValue()
        profile.ssh_clientkeys = self._ssh_clientkeys.GetValue()
        profile.ssh_allow_unknown = self._ssh_allow_unknown.GetValue()
        profile.ssh_compression = self._ssh_compression.GetValue()
        profile.tcp_timeout = self._tcp_timeout.GetValue()
        profile.vnc_exec = self._vnc_exec.GetValue()
        profile.vnc_port = self._vnc_port.GetValue()
        profile.vnc_args = self._vnc_args.GetValue()
        return profile

    def _on_browse_clientkeys(self, event):
        self._browse_for_and_set_file(self._ssh_clientkeys)

    def _on_browse_hostkeys(self, event):
        self._browse_for_and_set_file(self._ssh_hostkeys)

    def _on_browse_vncexec(self, event):
        self._browse_for_and_set_file(self._vnc_exec)

    def _on_click_close(self, event):
        self.Close(True)

    def _on_click_delete(self, event):
        name = self._profiles_list.GetStringSelection()
        if name != "":
            msgbox = wx.MessageDialog(self,
                                      prompt_delete_profile_message % (name),
                                      prompt_delete_profile_title,
                                      style=wx.YES_NO | wx.NO_DEFAULT |
                                            wx.ICON_QUESTION)
            retcode = msgbox.ShowModal()
            msgbox.Destroy()
            if retcode != wx.ID_YES: return

            new_profiles = []
            for profile in self._profiles:
                if profile.name != name:
                    new_profiles.append(profile)
            self._logger.info(profile_deleted % (name))
            self._save_profiles(new_profiles)

    def _on_click_new(self, event):
        self._profiles_list.DeselectAll()
        self._set_form_profile(None)

    def _on_click_save(self, event):
        profile = self._get_form_profile()
        if not self._profile_is_valid(profile): return

        new_profiles = []
        if self._multi:
            if self._profile is not None:
                existing_name = self._profile.name
                if profile.name == existing_name:
                    self._logger.info(profile_updated % (profile.name))
                elif not self._profile_name_exists(profile.name):
                    self._logger.info(profile_updated_name %
                                      (existing_name, profile.name))
                else:
                    self._display_error(err_profile_name % (profile.name))
                    return
                for p in self._profiles:
                    if p.name != existing_name:
                        new_profiles.append(p)
            elif not self._profile_name_exists(profile.name):
                self._logger.info(profile_added % (profile.name))
                for p in self._profiles:
                    new_profiles.append(p)
            else:
                self._display_error(err_profile_name % (profile.name))
                return
        new_profiles.append(profile)
        self._save_profiles(new_profiles)

    def _on_select_profile(self, event):
        if event.IsSelection():
            index = self._profiles_list.GetSelection()
            profile = self._profiles_list.GetClientData(index)
            self._set_form_profile(profile)

    def _populate_profiles_list(self):
        self._profiles_list.Clear()
        self._logger.debug(connectionprofile_list_cleared %
                           (self.__class__.__name__))
        for profile in self._profiles:
            self._profiles_list.Append(profile.name, profile)
            self._logger.debug(connectionprofile_list_added %
                               (self.__class__.__name__, profile.name))

    def _profile_is_valid(self, profile):
        try:
            ConnectionProfile.prevalidate(profile)
            return True
        except ValueError as e:
            self._display_error(e)
            return False
        except Exception as e:
            self._logger.exception(err_unexpected)
            self._display_error(err_unexpected + BLANK_LINES + str(e))
            return False

    def _profile_name_exists(self, name):
        pattern = r"^" + name + r"$"
        for p in self._profiles:
            if re.match(pattern, p.name, re.IGNORECASE) is not None:
                return True
        return False

    def _save_profiles(self, profiles):
        try:
            ConnectionProfile.write_to_file(profiles,
                                            self._filename,
                                            self._encoding)
        except Exception as e:
            self._logger.exception(err_unexpected)
            self._display_error(err_unexpected + BLANK_LINES + str(e))
            return

        self._logger.info(profiles_saved % (len(profiles), self._filename))
        self._profiles = profiles
        self._updated = True
        if self._multi:
            self._populate_profiles_list()
            self._on_click_new(None)

    def _set_form_profile(self, profile=None):
        # we use None here for a new profile, otherwise we cache the profile
        # so that we know when saving whether or not to update the existing
        if profile is not None:
            self._profile = profile
        else:
            self._profile = None
            profile = ConnectionProfile("")
        self._profile_name.SetValue(profile.name)
        self._ssh_server.SetValue(_cstr(profile.ssh_server))
        self._ssh_port.SetValue(profile.ssh_port)
        self._ssh_username.SetValue(_cstr(profile.ssh_username))
        self._ssh_hostkeys.SetValue(_cstr(profile.ssh_hostkeys))
        self._ssh_clientkeys.SetValue(_cstr(profile.ssh_clientkeys))
        self._ssh_allow_unknown.SetValue(_cbool(profile.ssh_allow_unknown))
        self._ssh_compression.SetValue(_cbool(profile.ssh_compression))
        self._tcp_timeout.SetValue(_cint(profile.tcp_timeout))
        self._vnc_exec.SetValue(_cstr(profile.vnc_exec))
        self._vnc_port.SetValue(profile.vnc_port)
        self._vnc_args.SetValue(_cstr(profile.vnc_args))

    def GetProfiles(self):
        return self._profiles

    def IsUpdated(self):
        return self._updated


def _cbool(value):
    return value is not None and value


def _cint(value):
    if value is None: return None
    return int(value)


def _cstr(value):
    if value is None: return ""
    return str(value)
