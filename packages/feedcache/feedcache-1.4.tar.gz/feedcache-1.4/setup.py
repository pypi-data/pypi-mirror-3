#!/usr/bin/env python
#
# $Id: setup.py.in 527 2007-01-14 17:14:50Z dhellmann $
#
# Copyright 2006 Doug Hellmann.
#
#
#                         All Rights Reserved
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for any purpose and without fee is hereby
# granted, provided that the above copyright notice appear in all
# copies and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of Doug
# Hellmann not be used in advertising or publicity pertaining to
# distribution of the software without specific, written prior
# permission.
#
# DOUG HELLMANN DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE,
# INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS, IN
# NO EVENT SHALL DOUG HELLMANN BE LIABLE FOR ANY SPECIAL, INDIRECT OR
# CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
# OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
# CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#
"""Distutils setup file for FeedCache

"""

#
# Import system modules
#
from distutils.core import setup

#
# Import Local modules
#

#
# Module
#

PROJECT = 'feedcache'

setup (
    name = PROJECT,
    version = '1.4',

    description = "Wrapper for Mark Pilgrim's FeedParser module which caches feed content.",
    long_description = """
A class to wrap Mark Pilgrim's FeedParser module so that parameters
can be used to cache the feed results locally instead of fetching the
feed every time it is requested. Uses both etag and modified times for
caching.  The cache is parameterized to use different backend storage
options.
""",

    author = 'Doug Hellmann',
    author_email = 'doug.hellmann@gmail.com',

    url = 'http://www.doughellmann.com/projects/%s/' % PROJECT,
    #download_url = 'http://www.doughellmann.com/downloads/%s-1.4.tar.gz' % PROJECT,

    classifiers = [ 'Development Status :: 4 - Beta',
                    'License :: OSI Approved :: BSD License',
                    'Programming Language :: Python',
                    'Intended Audience :: Developers',
                    'Topic :: Internet :: WWW/HTTP',
                    ],

    packages = ['feedcache',
                ],
    package_dir = {'':'.'},

    platforms = ['Any'],
    keywords = ('syndication', 'atom', 'RSS'),

    requires=['feedparser'],
    )
