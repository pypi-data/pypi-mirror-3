#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012 Adrien Kohlbecker
# Permission is hereby granted, free of
# charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom
# the Software is furnished to do so, subject to the following
# conditions:

# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
# BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

#from distutils.core import setup
from setuptools import setup

from cssmergemedialib import meta

setup(name='cssmergemedia',
    version=meta.__version__,
    author=meta.__author__,
    description='CSS Merge Media merges identical media queries in your CSS',
    scripts=['bin/cssmergemedia'],
    package_dir={'cssmergemedialib': 'cssmergemedialib'},
    packages=['cssmergemedialib'],
    install_requires=['cssutils >= 0.9.9']
)
