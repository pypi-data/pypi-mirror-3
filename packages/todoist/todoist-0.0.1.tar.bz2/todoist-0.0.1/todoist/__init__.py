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

"""
todoist is a Python wrapper around the Todoist API
"""

# version_info is a four-tuple for programmatic comparison. The first
# three numbers are the components of the version number.  The fourth
# is zero for an official release, positive for a development branch,
# or negative for a release candidate (after the base version number
# has been incremented)
__version_info__ = {
    'major': 0,
    'minor': 0,
    'micro': 1,
    'releaselevel': 'final'
}


def get_version():
    """
    Returns the human readable version number.
    """
    vers = ["%(major)i.%(minor)i" % __version_info__, ]

    if __version_info__['micro']:
        vers.append(".%(micro)i" % __version_info__)
    if __version_info__['releaselevel'] != 'final':
        vers.append('%(releaselevel)s' % __version_info__)
    return ''.join(vers)

__version__ = get_version()
