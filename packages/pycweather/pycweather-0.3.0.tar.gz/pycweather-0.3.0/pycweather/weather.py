# -*- coding: utf-8 -*-
#
# This file is part of PycWeather
#
# Copyright (c) 2009-2011 Vlad Glagolev <enqlave@gmail.com>
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

""" pycweather/weather.py: Weather class """

from cStringIO import StringIO
from urllib2 import urlopen

from lxml.etree import parse, tostring, fromstring, XMLSyntaxError

from pycweather import __version__


# correct url to AccuWeather RSS service
RSS_URL = "http://rss.accuweather.com/rss/liveweather_rss.asp"


class Weather:

    def __init__(self):
        self.xsl = None

    def load(self, xsl_file):
        try:
            self.xsl = parse(xsl_file)
        except XMLSyntaxError:
            print "XML syntax error occured while parsing XSL stylesheet"
        except:
            print "Unable to read XSL file"

    def preview(self, code, metric):
        try:
            data = urlopen(RSS_URL + "?metric=%d&locCode=%s" % (metric, code))
        except:
            print "Unable to connect to %s" % RSS_URL

            return -1

        tree = data.read()

        try:
            xml = fromstring(tree)
        except XMLSyntaxError:
            print "XML syntax error occured while parsing content: ", tree

            return -1

        if xml.xpath("channel/description")[0].text == "Invalid Location":
            print "Wrong location code, get one at www.accuweather.com"
            exit(2)
        else:
            document = parse(StringIO(tostring(xml)))

            print document.xslt(self.xsl)
