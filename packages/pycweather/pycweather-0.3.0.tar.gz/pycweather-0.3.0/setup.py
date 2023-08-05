#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of PycWeather
#
# Copyright (c) 2008-2009 Vlad Glagolev <enqlave@gmail.com>
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

""" setup.py: PycWeather setup script """

from distutils.core import setup

from pycweather import __version__

setup(
    name = "pycweather",
    url = "http://pycweather.enqlave.net/",
    version = __version__,
    download_url = "http://pycweather.enqlave.net/releases/pycweather-%s.tar.gz" % __version__,
    author = "Vlad Glagolev",
    author_email = "enqlave@gmail.com",
    packages = ["pycweather"],
    scripts = ["bin/pycweather"],
    data_files = [('share/pycweather', ["share/template.xsl", "share/ConkyWeather.ttf"])],
    description = "Weather display manager for conky",
    platforms = ["Linux", "Unix"],
    long_description = "PycWeather is pure-pythonic weather display manager \
                        for Conky system monitor.",
    license = "ISC",
    classifiers = [
        "Topic :: Desktop Environment",
        "Programming Language :: Python",
        "Operating System :: POSIX",
        "License :: OSI Approved :: ISC License (ISCL)",
        "Natural Language :: English",
        "Intended Audience :: End Users/Desktop",
    ]
)
