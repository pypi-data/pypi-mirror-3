#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import os
from commandwrapper import WrapCommand, WrapOnceCommand

release_notes = r"""
===============
Release Notes :
===============

Release 0.1:
============

First Version


Release 0.5:
============

Removed the destructor (__del__ method) because of:
    The Warning here:
        http://docs.python.org/reference/datamodel.html#object.__del__
    And becasue destroyed objects where not automaticaly removed by the
    garbage collector as described here:
        http://docs.python.org/library/gc.html#gc.garbage
    Which could cause memory usage increase.

Release 0.6:
============
Changed author's contact info
"""

setup(name='commandwrapper',
    version='0.6',
    author='Yves-Gwenael Bourhis',
    author_email='ygbourhis at gmail.com',
    description = 'Command Wrapper (make subprocess.Popen() easy)',
    license = 'GNU General Public License version 2.0',
    platforms = ['Windows','Linux','Mac OS',],
    long_description = str('\n'.join([WrapCommand.__doc__, WrapOnceCommand.__doc__, release_notes])),
    py_modules = ['commandwrapper']
)
