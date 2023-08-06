#! /usr/bin/env python

import os, sys

if sys.version_info < (2, 6):
    print ""
else:
    print os.path.dirname(os.path.realpath(sys.executable)).rstrip()
