## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

from ._constants import BLANK_LINE, BLANK_LINES

app_exit = "%s application exited."
app_start = "%s application starting."

connectionprofile_config = "Using connection profile configuration file '%s'"
connectionprofile_list_added = "%s added profile '%s' to the connection profiles list."
connectionprofile_list_cleared = "%s cleared all items from the connection profiles list."
connectionprofile_list_created = "%s created the connection profiles list option for display."

err_access_code = "Invalid access code."
err_logfile = "Unable to open the logfile for writing."
err_platform = "Unknown platform, please contact the authors for support."
err_profile_file_create = "Unable to create the profiles configuration file."
err_profile_file_parse = "An error occurred while parsing the profiles configuration file."
err_profile_name = "There is already a connection profile named '%s'"
err_profile_none = "You do not have a connection profile but one is required." + \
                   BLANK_LINES + "Would you like to close and exit the program?" + \
                   BLANK_LINES + "Click *Yes* to close this message and exit the program." + \
                   BLANK_LINES + "Click *No* to close this message and re-open the profile editor."
err_role = "Invalid role specified, must be either SupportRole.Consumer or SupportRole.Provider."
err_unexpected = "An unexpected error has occurred."

extender_invalid_classes = "Custom extender file '%s' contains %d classes, none of which inherit from SupportExtender!...continuing without an extender."
extender_invalid_module = "Custom extender file '%s' is not recognized as a valid python module!...continuing without an extender"
extender_without_classes = "Custom extender file '%s' contains zero classes!...continuing without an extender."

iconify_hide = "Received an iconify event, hiding the window."
iconify_show = "Received an iconify event, showing the window."

inputs_connect_clicked = "Recieved a connect event, starting the connection process."
inputs_connect_enabled = "Enabled relevant input controls for connecting."
inputs_disabled = "Disabled all input controls."
inputs_disconnect_clicked = "Received a disconnect event, starting the disconnect process."
inputs_disconnect_enabled = "Enabled relevant input controls for disconnecting."

label_about = "About %s"
label_access_code = "Access Code:"
label_acknowledgements = "Acknowledgements"
label_browse = "Browse..."
label_connect_consumer = "Connect"
label_connect_provider = "Begin Session"
label_connection_profile = "Connection Profile:"
label_disconnect = "Disconnect"
label_disconnect_consumer = "Disconnect"
label_disconnect_provider = "End Session"
label_edit_window = "Connection Profile Editor"
label_error = "ERROR"
label_exit = "Exit"
label_license = "License"
label_password = "Password:"
label_profile_delete = "Delete Profile"
label_profile_name = "Profile Name:"
label_profile_new = "New Profile"
label_profile_save = "Save Profile"
label_show = "Show"
label_ssh_allow_unknown = "SSH Unknown Hosts?:"
label_ssh_clientkeys = "SSH Clientkeys:"
label_ssh_compression = "SSH Compression?:"
label_ssh_hostkeys = "SSH Hostkeys:"
label_ssh_port = "SSH Port:"
label_ssh_server = "SSH Server:"
label_ssh_username = "SSH Username:"
label_tcp_timeout = "TCP Connect Timeout:"
label_version = "Version"
label_versions = "Versions"
label_vnc_args = "VNC Arguments:"
label_vnc_exec = "VNC Executable:"
label_vnc_port = "VNC Port:"
label_website = "Website"

menu_edit_label = "&Edit"
menu_edit_profiles_desc = "Edit connection profiles"
menu_edit_profiles_label = "&Profiles\tCtrl+P"

menu_file_label = "&File"
menu_file_quit_desc = "Quit the program"
menu_file_quit_label = "&Quit\tCtrl+Q"

menu_help_label = "&Help"
menu_help_about_desc = "About %s"
menu_help_about_label = "&About\tCtrl+A"

profile_added = "Adding a new profile named '%s'."
profile_deleted = "Deleting the profile named '%s'."
profile_updated = "Updating existing profile named '%s'."
profile_updated_name = "Updating existing profile with changed name; old name - '%s', new name - '%s'"
profiles_edit_enabled = "Enabling option to edit connection profiles."
profiles_file_created = "Created the profiles configuration file '%s'."
profiles_saved = "Saved %d profiles to the configuration file '%s'."

prompt_close_main_logmsg = "Received a request to close while actively connected."
prompt_close_main_message = "You are currently connected to your support session." + \
                            BLANK_LINES + "Do you really want to close and exit the program?"
prompt_close_main_title = "Confirm Exit"
prompt_delete_profile_message = "Do you really want to delete the '%s' connection profile?"
prompt_delete_profile_title = "Confirm Delete"
prompt_unknown_host_message = "You are attempting to connect to an unknown SSH host." + \
                              BLANK_LINES + "For your security, please verify the information below." + \
                              BLANK_LINES + "Hostname:  %s" + \
                              BLANK_LINE + "Key Type:  %s" + \
                              BLANK_LINE + "Fingerprint:  %s" + \
                              BLANK_LINES + "Click *No* to decline the key and abort the connection." + \
                              BLANK_LINES + "Click *Yes* to accept the key and continue connecting."
prompt_unknown_host_title = "Unknown SSH Host"

tooltip_access_code = "Enter the numeric access code given to you"
tooltip_connect_consumer = "Connect to the selected support provider"
tooltip_connect_provider = "Begin your session with the remote client"
tooltip_disconnect_consumer = "Disconnect from your support provider"
tooltip_disconnect_provider = "End your session with the remote client"
tooltip_password = "Enter your password"
tooltip_profile_name = "The unique name to assign the connection profile" + \
                       BLANK_LINES + "This gets displayed in the dropdown menu of the main window"
tooltip_ssh_allow_unknown = "Check this box to allow connecting to unknown SSH hosts"
tooltip_ssh_clientkeys = "The full path of the SSH private key to use for authentication" + \
                         BLANK_LINES + \
                         "Leave this blank to use the default behavior of looking for an SSH agent first before trying regular password authentication"
tooltip_ssh_compression = "Check this box to enable SSH compression"
tooltip_ssh_hostkeys = "The full path of the SSH known hosts file" + \
                       BLANK_LINES + \
                       "Leave this blank to use the default behavior of looking for hosts in ~\.ssh first before continuing on without a hosts file"
tooltip_ssh_port = "The port number used by the SSH server" + \
                   BLANK_LINES + "You can simply leave this blank to use the default value"
tooltip_ssh_server = "The SSH server hostname or IP address to use"
tooltip_ssh_username = "The username to login as on the SSH server" + \
                       BLANK_LINES + "Leave this blank to use the logged on username at runtime"
tooltip_tcp_timeout = "The timeout, in seconds, for the initial TCP connection" + \
                      BLANK_LINES + "You can simply leave this blank to use the default value"
tooltip_vnc_args = "The command line arguments to supply the VNC executable" + \
                   BLANK_LINES + "This can contain one %d which will be replaced with the VNC port number at runtime"
tooltip_vnc_exec = "The full path of the VNC executable to launch"
tooltip_vnc_port = "The local port number for the VNC connection"
