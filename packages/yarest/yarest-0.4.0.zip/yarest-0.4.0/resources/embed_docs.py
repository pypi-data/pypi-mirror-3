#! /usr/bin/env python
## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

import codecs, os

def embed():
    file_encoding = "utf-8"
    lines_encoding = u"## -*- coding: %s -*-\n" % (file_encoding)
    lines_copyright = u"# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>\n\n"

    lines_acknowledge = 'acknowledgements = u"""%s"""\n\n'
    lines_license = 'license = u"""%s"""'

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    gui_dir = os.path.join(cur_dir, "..", "yarest", "gui")

    acknowledge_file = os.path.join(cur_dir, "..", "ACKNOWLEDGE.txt")
    license_file = os.path.join(cur_dir, "..", "LICENSE.txt")

    output_file = os.path.join(gui_dir, "_docs.py")

    with codecs.open(acknowledge_file, "r", file_encoding) as f:
        acknowledge_text = f.read()

    with codecs.open(license_file, "r", file_encoding) as f:
        license_text = f.read()

    with codecs.open(output_file, "w", file_encoding) as f:
        f.write(lines_encoding)
        f.write(lines_copyright)
        f.write(lines_acknowledge % (acknowledge_text))
        f.write(lines_license % (license_text))

if __name__ == "__main__":
    embed()
