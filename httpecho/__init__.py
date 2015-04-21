#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
httpecho
~~~~~~~~

HTTP echo server

:copyright: (c) 2015 by Alexandr Lispython (alex@obout.ru).
:license: , see LICENSE for more details.
:github: http://github.com/Lispython/httpecho
"""

__all__ = 'get_version',
__author__ = "GottWal team"
__license__ = "BSD, see LICENSE for more details"
__maintainer__ = "Alexandr Lispython"

try:
    __version__ = __import__('pkg_resources') \
        .get_distribution('httpecho').version
except Exception:
    __version__ = 'unknown'

if __version__ == 'unknown':
    __version_info__ = (0, 0, 1)
else:
    __version_info__ = __version__.split('.')
__build__ = 0x000001


def get_version():
    return __version__
