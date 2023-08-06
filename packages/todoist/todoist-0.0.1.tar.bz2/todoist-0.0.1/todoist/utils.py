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

import urllib


def get_url(*args, **kwargs):
    """ Returns api url. """
    url = '/'.join(args)

    # Remove null datas
    data = {}
    for key in kwargs:
        value = str(kwargs[key])
        if value:
            data[key] = value
    if len(kwargs):
        url = '%s?%s' % (url, urllib.urlencode(data))

    return url