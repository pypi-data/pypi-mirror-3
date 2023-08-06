#!/usr/bin/env python
from optparse import OptionParser
import djangopipstarter
import shutil
import os

parser = OptionParser(usage="usage: %prog [options] directory",
                      version="%%prog %s" % djangopipstarter.get_version(),
                      description="Command line tool for creating django environment")
options, args = parser.parse_args()

try:
    directory = args[0]
except IndexError:
    parser.print_usage()
    exit()

src = os.path.join(djangopipstarter.__path__[0], 'template')
dst = directory

shutil.copytree(src, dst)
