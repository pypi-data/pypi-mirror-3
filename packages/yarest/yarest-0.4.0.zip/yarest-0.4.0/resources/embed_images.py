#! /usr/bin/env python
## -*- coding: utf-8 -*-
# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>

import codecs, os
from wx.tools.img2py import img2py

def embed():
    file_encoding = "utf-8"
    lines_encoding = u"## -*- coding: %s -*-\n" % (file_encoding)
    lines_copyright = u"# Copyright © 2011-2012 Mike Fled <nonvenia@gmail.com>\n\n"
    lines_imports = u"import wx\nfrom wx.lib.embeddedimage import PyEmbeddedImage\n\n"
    lines_iconbundle = """def get_icon_bundle():
    bundle = wx.IconBundle()
    bundle.AddIcon(wx.IconFromBitmap(logo_256.GetBitmap()))
    bundle.AddIcon(wx.IconFromBitmap(logo_128.GetBitmap()))
    bundle.AddIcon(wx.IconFromBitmap(logo_64.GetBitmap()))
    bundle.AddIcon(wx.IconFromBitmap(logo_32.GetBitmap()))
    bundle.AddIcon(wx.IconFromBitmap(logo_16.GetBitmap()))
    return bundle\n\n"""
    images = {"logo-16" : "logo-16x16.png",
              "logo-32" : "logo-32x32.png",
              "logo-64" : "logo-64x64.png",
              "logo-128" : "logo-128x128.png",
              "logo-256" : "logo-256x256.png",
              "logo-512" : "logo-512x512.png"}

    cur_dir = os.path.dirname(os.path.realpath(__file__))
    gui_dir = os.path.join(cur_dir, "..", "yarest", "gui")

    output_file = os.path.join(gui_dir, "_images.py")

    with codecs.open(output_file, "w", file_encoding) as f:
        f.write(lines_encoding)
        f.write(lines_copyright)
        f.write(lines_imports)
        f.write(lines_iconbundle)

    for img_name, img_file in images.iteritems():
        img2py(os.path.join(cur_dir, img_file), output_file,
               append=True, imgName=img_name)

if __name__ == "__main__":
    embed()
