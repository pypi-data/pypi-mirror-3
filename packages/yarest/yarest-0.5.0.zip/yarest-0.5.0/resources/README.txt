Rather than determining where the document and image resources are located
at runtime, and passing them around everywhere as filepaths, we decided to
simply embed such resources directly into the package and forget about it.

embed_docs.py
=============
This script takes the contents of the "ACKNOWLEDGE.txt" and "LICENSE.txt"
files from the root of the distribution and embeds them as usable python
source files within the yarest.gui package. If you change either of the
files simply re-run this script to update the gui package immediately,
otherwise the script gets executed whenever "setup.py sdist" runs.

Note that if you change the encoding of either file from its default UTF-8
then you must change the script variable "file_encoding" to your encoding.

embed_images.py
===============
This script expects to find exactly 6 images, named as follows:

logo-16x16.png    logo-32x32.png    logo-64x64.png
logo-128x128.png  logo-256x256.png  logo-512x512.png

It takes those images and uses the img2py tool to embed them, and also
creates the code to make an icon bundle with all sizes except for the
512x512 version. Assuming you keep the same names and sizes you won't
have to change anything for the script to work with different images,
however you probably should change the "lines_copyright" variable as
it is output to the source file that contains the image binary data.

This script also gets executed whenever "setup.py sdist" runs.
