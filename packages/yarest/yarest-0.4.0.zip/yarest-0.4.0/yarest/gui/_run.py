## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

import errno, getopt, imp, inspect, os, sys, traceback, wx

from yarest import SupportExtender, SupportDirection, SupportRole
from yarest import __version__ as yarest_version

from ._constants import APP_NAME, UTF8
from ._main import MainWindow
from ._messages import (err_platform, extender_invalid_classes,
                        extender_invalid_module, extender_without_classes)


def getopts():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hv", ["help",
                                                        "version",
                                                        "encoding=",
                                                        "extender=",
                                                        "logfile=",
                                                        "profiles=",
                                                        "disable-edit",
                                                        "provider",
                                                        "forward",
                                                        "reverse"])
    except getopt.GetoptError as e:
        print str(e)
        _usage()
        sys.exit(1)

    class _Options(object):
        direction = None
        editable = True
        encoding = UTF8
        extender = None
        logfile = None
        profiles = None
        role = SupportRole.Consumer
    options = _Options()

    for o, a in opts:
        if o in ("-h", "--help"):
            _usage()
            sys.exit()
        elif o in ("-v", "--version"):
            print yarest_version
            sys.exit()
        elif o in ("--disable-edit"):
            options.editable = False
        elif o in ("--encoding"):
            options.encoding = a
        elif o in ("--extender"):
            options.extender = a
        elif o in ("--forward"):
            options.direction = SupportDirection.Forward
        elif o in ("--logfile"):
            options.logfile = a
        elif o in ("--profiles"):
            options.profiles = a
        elif o in ("--provider"):
            options.role = SupportRole.Provider
        elif o in ("--reverse"):
            options.direction = SupportDirection.Reverse
        else:
            assert False, "unhandled option"

    if options.direction is None:
        if options.role == SupportRole.Provider:
            options.direction = SupportDirection.Reverse
        else:
            options.direction = SupportDirection.Forward

    app_name = APP_NAME.lower()

    if sys.platform == "win32":
        user_dir = os.path.join(os.environ["APPDATA"], APP_NAME)
        log_dir = os.path.join(user_dir, "logs")
    elif sys.platform == "darwin":
        user_dir = os.path.join(os.path.expanduser("~"), "Library",
                                "Application Support", APP_NAME)
        log_dir = os.path.join(os.path.expanduser("~"), "Library",
                               "Logs", APP_NAME)
    elif os.name == "posix":
        user_dir = os.path.join(os.path.expanduser("~"), ".config", app_name)
        log_dir = os.path.join(os.path.expanduser("~"), ".cache", app_name)
    else:
        raise RuntimeError(err_platform)

    if options.extender is not None:
        # do we have an actual existing file?
        if os.path.isfile(options.extender):
            try:
                # do we have a valid python module?
                mod_info = inspect.getmoduleinfo(options.extender)
                if mod_info is None:
                    raise ValueError(extender_invalid_module %
                                     (options.extender))

                # can we import the module and does it have any classes?
                module = imp.load_source(mod_info.name, options.extender)
                classes = inspect.getmembers(module, inspect.isclass)
                if len(classes) == 0:
                    raise ValueError(extender_without_classes %
                                     (options.extender))

                # does one of the classes inherit from SupportExtender?
                found = False
                for class_name, class_obj in classes:
                    extender = class_obj()
                    if isinstance(extender, SupportExtender):
                        options.extender = extender
                        found = True
                        break
                if not found:
                    raise ValueError(extender_invalid_classes %
                                     (options.extender, len(classes)))
            except:
                print traceback.format_exc()
                options.extender = None
        else:
            options.extender = None

    if options.profiles is None:
        _create_dir(user_dir)
        options.profiles = os.path.join(user_dir, "profiles.ini")
    if options.logfile is None:
        _create_dir(log_dir)
        options.logfile = os.path.join(log_dir, "log.txt")
    return options


def run():
    app = _YarestApp()
    app.MainLoop()
    del app


def _create_dir(path):
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except OSError as e:
            if e.errno != errno.EEXIST: raise


def _usage():
    print """
 Usage: %s [OPTIONS]

 Options:
 --disable-edit               Disable editing of the connection profiles
                              configuration file from the interface, by
                              default editing functionality is enabled.

 --provider                   Initialize the interface to be the support
                              provider, defaults to being the consumer.

 --forward                    Initialize the interface for creating a forward
                              SSH tunnel for the support session (useful only
                              when initializing as the provider).

 --reverse                    Initialize the interface for creating a reverse
                              SSH tunnel for the support session (useful only
                              when initializing as the consumer).

 --extender <filepath>        Set the path of the file containing the support
                              extender class to use. The file must be a valid
                              python module that can be imported, and contain
                              a class that inherits from SupportExtender. If
                              such a class can be found upon inspection then
                              a new instance will be created and utilized.

 --profiles <filepath>        Set the path of the connection profiles config
                              file to use. By default the location is based
                              on the OS platform in use:

                              On Windows:
                              %%APPDATA%%/YAREST/profiles.ini

                              On MacOSX:
                              ~/Library/Application Support/YAREST/profiles.ini

                              On all other POSIX based systems:
                              ~/.config/yarest/profiles.ini

 --logfile <filepath>         Set the path of the log to use. By default the
                              location is based upon the OS platform in use:

                              On Windows:
                              %%APPDATA%%/YAREST/logs/log.txt

                              On MacOSX:
                              ~/Library/Logs/YAREST/log.txt

                              On all other POSIX based systems:
                              ~/.cache/yarest/log.txt

 --encoding <encoding name>   Set the encoding used for both the profiles
                              file and the log file, defaults to "utf-8".

 --version                    Print the current version number and exit.

 --help                       Print this help menu and exit.""" % (sys.argv[0])


class _YarestApp (wx.App):
    def MacReopenApp(self):
        self._raise_window()

    def OnActivate(self, event):
        if event.GetActive():
            self._raise_window()
        event.Skip()

    def OnInit(self):
        options = getopts()
        win = MainWindow(parent=None,
                         profiles=options.profiles,
                         logfile=options.logfile,
                         encoding=options.encoding,
                         editable=options.editable,
                         extender=options.extender,
                         role=options.role,
                         direction=options.direction)
        self.Bind(wx.EVT_ACTIVATE_APP, self.OnActivate)
        self.SetTopWindow(win)
        return True

    def _raise_window(self):
        self.GetTopWindow().Raise()
