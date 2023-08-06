#!/usr/bin/env python3
#
# Copyright (c) 2011 David Townshend
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
# or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 675 Mass Ave, Cambridge, MA 02139, USA.

from distutils.core import setup
import sys

import swmmout

version = swmmout.__version__
author = 'David Townshend'

classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Topic :: Scientific/Engineering :: Information Analysis',
    'Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator',
]

def run_setup(*argv):
    if len(argv) > 0:
        sys.argv = [sys.argv[0]] + list(argv)

    setup(name='swmmout',
          version=version,
          description='Python module to read a SWMM "out" file.',
          author=author,
          author_email='aquavitae69@gmail.com',
          url='http://readthedocs.org/docs/swmmout/en/latest/',
          py_modules=['swmmout'],
          classifiers=classifiers
         )

if __name__ == '__main__':
    run_setup()
