#!/usr/bin/env python
# -*- mode:python; tab-width: 2; coding: utf-8 -*-

"""Sleipnir EIA Bank constants"""

from __future__ import absolute_import

__author__           = 'Carlos Martín <cmartin@liberalia.net>'
__version__          = '0.0.90'
__date__             = '2011-10-01'
__license__          = 'GNU General Public License, version 2'

__namespace__        = "sleipnir"
__modname__          = "bank"
__appname__          = __namespace__ + '.' + __modname__
__title__            = 'Sleipnir EIA Bank example'
__release__          = '1'
__summary__          = 'Sleipnir EIA Bank example'
__url__              = 'http://sleipnir.liberalia.net/'
__copyright__        = '© 2011 Carlos Martín'

__classifiers__      = [
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Topic :: Office/Business :: Financial',
    ]

__long_description__ = """\
Add Here a a description to this package
"""

__requires__ = [
    __namespace__ + '.transport >= 0.0.91',
    ]
__tests_requires__ = [
    __namespace__ + '.transport >= 0.0.91',
    __namespace__ + '.testing   >= 0.1rc6',
    ]
