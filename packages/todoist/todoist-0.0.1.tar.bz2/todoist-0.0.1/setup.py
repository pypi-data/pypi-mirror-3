#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Coded by Gökmen Görgen.
# Copyright (C) 2012, Todoist
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# Please read the LICENSE file.
#

import os
from setuptools import setup
from setuptools import find_packages
import todoist


def read_file(filename):
    """
    Read a file into a string
    """
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    try:
        return open(filepath).read()
    except IOError:
        return ''

setup(
    name='todoist',
    version=todoist.__version__,
    author='Gökmen Görgen',
    author_email='gokmen@alageek.com',
    packages=find_packages(),
    url='http://todoist.com/API/',
    license='GPLv3',
    description=u' '.join(todoist.__doc__.splitlines()).strip(),
    long_description=read_file('README.rst'),
    setup_requires=['nose>=1.1']
)
