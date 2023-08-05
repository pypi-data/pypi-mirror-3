#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
import os
from commandwrapper import WrapCommand, WrapOnceCommand

setup(name='commandwrapper',
    version='0.3',
    author='Yves-Gwenael Bourhis',
    author_email='ybourhis at mandriva.com',
    description = 'Command Wrapper (make subprocess.Popen() easy)',
    license = 'GNU General Public License version 2.0',
    platforms = ['Windows','Linux','Mac OS',],
    long_description = str('\n'.join([WrapCommand.__doc__, WrapOnceCommand.__doc__])),
    py_modules = ['commandwrapper']
)
