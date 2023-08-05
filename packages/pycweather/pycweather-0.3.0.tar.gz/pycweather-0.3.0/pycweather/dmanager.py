# -*- coding: utf-8 -*-
#
# This file is part of PycWeather
#
# Copyright (c) 2008-2011 Vlad Glagolev <enqlave@gmail.com>
# All rights reserved.
#
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

""" pycweather/dmanager.py: weather display manager """

import getopt
import os
import sys

from pycweather import __version__
from pycweather import weather


# default values stay for Moscow (RU) location and internal XSL stylesheet usage
_CODE = "ASI|RU|RS052|MOSCOW|"


def usage():
    print """Usage: %s [options]\n
    -h, --help		show this help
    -v, --version	version information
    -c, --code <code>	location ID code (default is %s)
    -m, --metric	use metric measurement system
    -x, --xsl <file>	custom XSL file\n""" % (sys.argv[0], _CODE)


def version():
    print """PycWeather version:
    %s. (major)
      %s. (minor)
        %s  (revision)""" % tuple(__version__.split("."))
    exit(0)


def main(template):
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvc:mx:", ["help", \
                                   "version", "code=", "metric", "xsl="])
    except getopt.error, msg:
        print msg
        usage()
        exit(2)

    forecast = weather.Weather()
    metric = 0

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            exit(0)
        elif o in ("-v", "--version"):
            version()
        elif o in ("-c", "--code"):
            code = a
        elif o in ("-m", "--metric"):
            metric = 1
        elif o in ("-x", "--xsl"):
            xsl = a

    try:
        code
    except NameError:
        code = _CODE

    try:
        xsl
    except NameError:
        xsl = template

    forecast.load(xsl)

    forecast.preview(code, metric)
