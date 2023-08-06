#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import os
from progbar import ProgBar

release_notes = r"""
    ===============
    Release Notes :
    ===============

    Release 0.1:
    ============

    First Version

    Release 0.2:
    ============

    Removed the destructor (__del__ method) because of:

    + The Warning here:
      http://docs.python.org/reference/datamodel.html#object.__del__

    + Destroyed objects where not automaticaly removed by
      the garbage collector as described here:
      http://docs.python.org/library/gc.html#gc.garbage
      Which could cause memory usage increase.

    Release 0.3:
    ============

    Changed author's contact info.
"""

setup(name='progbar',
    version='0.3',
    author='Yves-Gwenael Bourhis',
    author_email='ygbourhis at gmail.com',
    description = 'simple progression bar for shell scripts',
    license = 'GNU General Public License version 2.0',
    platforms = ['Windows','Linux','Mac OS',],
    long_description = str('\n'.join([ProgBar.__doc__, release_notes,])),
    py_modules = ['progbar']
)
