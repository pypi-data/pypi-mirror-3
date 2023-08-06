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
import json
import unittest
from todoist.base import StandardAPI

dir_path = os.path.realpath(os.path.dirname(__file__))
data_file = os.path.join(dir_path, 'data.json')

if not os.path.exists(data_file):
    message = "Please rename it as data.json at same directory and edit" +\
              "informations:\n%s.example" % data_file
    exit(message)


class StandardAPITest(unittest.TestCase):
    def setUp(self):
        self.api = StandardAPI()
        self.data = json.loads(file(data_file).read())

    def test_user(self):
        results = [u'ALREADY_REGISTRED', u'TOO_SHORT_PASSWORD',
                   u'INVALID_EMAIL', u'INVALID_TIMEZONE',
                   u'INVALID_FULL_NAME', u'UNKNOWN_ERROR']
        data = self.data.get('user')
        result = self.api.register(**data)

        if type(result) == dict:
            # check user information.
            self.assertEqual(result.get('email'), data.get('email'))
            self.assertEqual(result.get('full_name'), data.get('full_name'))
            self.assertEqual(result.get('timezone'), data.get('timezone'))

            # try login and update user information.
            login = self.api.login(email=data.get('email'),
                                   password=data.get('password'))

            # check api token value.
            self.assertEqual(login.get('api_token'), unicode(self.api.token))

            # try update user information.
            user_new_data = dict(
                email='%sm' % login.get('email'),
                full_name='test update user',
                date_format=2,
                time_format=1,
                start_page='_blank')
            user_info = self.api.update_user(**user_new_data)

            # and check last information
            for key, value in user_new_data.items():
                self.assertEqual(user_info.get(key), value)

        else:
            # if result is not dictionary, the type is unicode probably.
            # the result should be in results list at this status.
            self.assertTrue(result in results)

    def test_user_login_fail(self):
        results = [u'LOGIN_ERROR']
        result = self.api.login(email='todoist+blablabla@todoist.com',
                                password='blablabla')

        self.assertTrue(result in results)

    def test_timezones(self):
        timezones = self.api.get_timezones()

        # test count of timezones.
        self.assertEqual(len(timezones), 175)

        # test a value of timezones.
        timezones = dict(timezones)
        self.assertEqual(timezones['Europe/Istanbul'], 'GMT+02:00 - Istanbul')

    def test_project(self):
        # register new account
        data = self.data.get('project')
        self.api.register(**data)

        # and login
        api_data = self.api.login(email=data.get('email'),
                                  password=data.get('password'))

        if type(api_data) != dict:
            # hmm registration is failed.
            results = [u'ALREADY_REGISTRED', u'TOO_SHORT_PASSWORD',
                       u'INVALID_EMAIL', u'INVALID_TIMEZONE',
                       u'INVALID_FULL_NAME', u'UNKNOWN_ERROR']
            self.assertTrue(api_data in results)
            return

        # if api_data is dictionary, continue to test.
        # our first test is about adding a project without name.
        result = self.api.add_project(name='')
        self.assertTrue(result, u'ERROR_NAME_IS_EMPTY')

        # the second test is about checking result information.
        project_name = 'tset1' #  i know, it's misspelling.
        new_project = self.api.add_project(name=project_name)
        self.assertEqual(new_project.get('name'), project_name)
        self.assertEqual(new_project.get('user_id'), api_data.get('id'))

        # new project info should be in projects list.
        projects = self.api.get_projects()
        self.assertTrue(len(projects), 1)

        # and new project should be equal to get_project() result.
        project = self.api.get_project(project_id=new_project.get('id'))
        self.assertEqual(project.get('id'), new_project.get('id'))

        # now, try to fix project name.
        project_name = 'test1'
        project = self.api.update_project(project_id=project.get('id'),
                                          name=project_name)
        self.assertEqual(project.get('name'), project_name)

        # and last, delete project
        result = self.api.delete_project(project_id=project.get('id'))
        self.assertEqual(result, u'ok')
