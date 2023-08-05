## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

import codecs, os, re, sys

# encoding used for the text files
_file_encoding = "utf-8"

# get current working directory
_cur_dir = os.path.dirname(os.path.realpath(__file__))

# get version string from the yarest package
_ver_file = os.path.join(_cur_dir, "yarest", "__init__.py")
_ver_pattern = r"^__version__ = ['\"]([^'\"]*)['\"]"

_ver_data = codecs.open(_ver_file, "r", _file_encoding).read()
_ver_matches = re.search(_ver_pattern, _ver_data, re.M)

if _ver_matches:
    _ver_string = _ver_matches.group(1)
else:
    raise RuntimeError("Couldn't find version info in '%s'" % (_ver_file))

# create the long description
_readme_file = os.path.join(_cur_dir, "README.txt")
_readme_data = codecs.open(_readme_file, "r", _file_encoding).read()

_change_file = os.path.join(_cur_dir, "CHANGELOG.txt")
_change_data = codecs.open(_change_file, "r", _file_encoding).read()

_long_description = _readme_data + "\n\n" + _change_data

# embed the gui resource files if creating a source distribution
if len(sys.argv) >= 2 and sys.argv[1] == "sdist":
    sys.path.append(os.path.join(_cur_dir, "resources"))
    import embed_docs
    embed_docs.embed()
    import embed_images
    embed_images.embed()
    sys.path.remove(os.path.join(_cur_dir, "resources"))

# in the event we want to package just the core API and
# can already guarantee dependencies are met, then the
# following should allow for distutils to do the setup
#
# from distutils.core import setup
# _packages = [ "yarest" ]
# _kw = {}
#
# the gui however depends on entry_points being available
# so we import setuptools if installed or use distribute
#
# we could also in theory use distutils with the gui, to
# do so we would have to supply our own launcher script;
# see the "yarest_ui.py" testing script for the example.
try:
    from setuptools import setup
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

_packages = [ "yarest", "yarest.gui" ]
_kw = { "entry_points": { "gui_scripts": ["yarest=yarest.gui:run"] },
        "install_requires": [ "paramiko >= 1.7.4",
                              "configobj",
                              "psutil" ],
        "zip_safe": False}

setup(name = "yarest",
      version = _ver_string,
      description = "Yet Another REmote Support Tool",
      long_description = _long_description,
      author = "Mike Fled",
      author_email = "nonvenia@gmail.com",
      url = "http://code.google.com/p/yarest/",
      packages = _packages,
      license = "MIT",
      platforms = "Posix; MacOS X; Windows",
      classifiers = [ "Development Status :: 4 - Beta",
                      "Intended Audience :: Information Technology",
                      "Intended Audience :: Developers",
                      "License :: OSI Approved :: MIT License",
                      "Operating System :: OS Independent",
                      "Programming Language :: Python :: 2.6",
                      "Programming Language :: Python :: 2.7",
                      "Topic :: Internet",
                      "Topic :: Security",
                      "Topic :: System :: Networking" ],
      **_kw
      )
