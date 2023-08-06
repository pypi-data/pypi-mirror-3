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

import inspect
import json
import urllib2
from todoist.settings import API_STANDARD_URL, API_SYNC_URL
from todoist.utils import get_url


class APIMixin(object):
    def __init__(self, token=''):
        self.token_key = 'token'
        self.token = token
        self.api_url = API_STANDARD_URL

    def __getattribute__(self, item):
        obj = object.__getattribute__(self, item)

        if item.startswith('_') or type(obj) == str:
            return obj

        def api(*args, **kwargs):
            result = self.__json(item, **kwargs)

            # we can specific code for any function. so..
            arg_count = len(inspect.getargspec(obj).args)
            if arg_count > 1:
                # the original function gets more arguments. so, run the
                # function with 'result' argument.
                obj_result = obj(result)

                # if obj_result is not None, return the result of the function,
                # else pass it.
                if obj_result:
                    return obj_result

            return result

        # get docstring from obj.
        api.__doc__ = obj.__doc__

        return api

    def __json(self, item, **kwargs):
        if self.token:
            kwargs.update({self.token_key: self.token})

        url_prefix = self.__to_camelcase(item)
        url = get_url(self.api_url, url_prefix, **kwargs)

        try:
            return json.loads(urllib2.urlopen(url).read())

        except urllib2.HTTPError, err:
            return unicode(err)

    def __to_camelcase(self, value):
        def camelcase():
            yield str.lower
            while True:
                yield str.capitalize

        c = camelcase()
        return ''.join(c.next()(x) if x else '_' for x in value.split('_'))


class StandardAPI(APIMixin):
    """ StandardAPI can be used to hook Todoist into other applications. """
    def login(self, result):
        """ Login user into Todoist to get a token.

        Required parameters: email, password
        """

        # if result dict, login is successful.
        if type(result) == dict:
            # after login, define self.token
            self.token = str(result.get('api_token'))

    def get_timezones(self):
        """ Returns the timezones Todoist supports."""
        pass

    def register(self):
        """ Registers new account.

        Required parameters: email, full_name, password, timezone
        """
        pass

    def update_user(self):
        """ Updates user information.

        Required parameters: token
        Optional parameters: email, full_name, password, timezone, date_format,
            time_format, start_page
        """
        pass

    def get_projects(self):
        """ Returns all of user's projects.

        Required parameters: token
        """
        pass

    def get_project(self):
        """ Return's data about a project.

        Required parameters: token, project_id
        """
        pass

    def add_project(self):
        """ Adds a new project.

        Required parameters: name, token
        Optional parameters: color, indent, order
        """
        pass

    def update_project(self):
        """ Updates an existing project.

        Required parameters: project_id, token
        Optional parameters: name, color, indent, order, collapsed
        """
        pass

    def update_project_orders(self):
        """ Updates how the projecta are ordered.

        Required parameters: token, item_id_list
        """
        pass

    def delete_project(self):
        """ Deletes an existing project.

        Required parameters: project_id, token
        """
        pass

    def get_labels(self):
        """ Returns all of user's labels.

        Required parameters: project_id, token
        Optional parameters: as_list
        """
        pass

    def update_label(self):
        """ Changes the name of an existing label.

        Required parameters: old_name, new_name, token
        """
        pass

    def update_label_color(self):
        """ Changes the color of an existing label.

        Required parameters: name, color, token
        """
        pass

    def delete_label(self):
        """ Deletes an existing label.

        Required parameters: name, token
        """
        pass

    def get_uncompleted_items(self):
        """ Returns a project's uncompleted items (tasks).

        Required parameters: project_id, token
        Optional parameters: js_date
        """
        pass

    def get_all_completed_items(self):
        """ Returns all user's completed items (tasks). Only available for
        Todoist Premium users.

        Required parameters: token
        Optional parameters: js_date, project_id, label, interval
        """
        pass

    def get_completed_items(self):
        """ Returns a project's completed items (tasks) - the tasks that are in
        history.

        Required parameters: project_id, token
        Optional parameters: js_date
        """
        pass

    def get_items_by_id(self):
        """ Returns items by ids.

        Required parameters: ids, token
        Optional parameters: js_date
        """
        pass

    def add_item(self):
        """ Adds an item to a project.

        Required parameters: proejct_id, content, token
        Optional parameters: date_string, priority, indent, js_date, item_order
        """
        pass

    def update_item(self):
        """ Updates an existing item.

        Required parameters: id, token
        Optional parameters: content, date_string, priority, indent,
            item_order, collapsed, js_date
        """
        pass

    def update_orders(self):
        """ Updates the order of a project's tasks.

        Required parameters: project_id, item_id_list, token
        """
        pass

    def move_items(self):
        """ Moves items from one project to another.

        Required parameters: project_items, to_project, token
        """
        pass

    def update_recurring_date(self):
        """ Updates recurring dates and set them to next date regarding an
        item's date_string.

        Required parameters: ids, token
        Optional parameters: js_date
        """
        pass

    def delete_items(self):
        """ Deletes existing items.

        Required parameters: ids, token
        """
        pass

    def complete_items(self):
        """ Completes items and move them to history.

        Required parameters: ids, token
        Optional parameters: in_history
        """
        pass

    def uncomplete_items(self):
        """ Uncompletes items and move them to the active projects.

        Required parameters: ids, token
        """
        pass

    def notes(self):
        """ Adds a note to an item.

        Required parameters: item_id, content, token
        """
        pass

    def update_note(self):
        """ Updates an existing note.

        Required parameters: note_id, content, token
        """
        pass

    def delete_note(self):
        """ Deletes an existing note.

        Required parameters: item_id, note_id, token
        """
        pass

    def get_notes(self):
        """ Returns all notes of an item.

        Required parameters: item_id, token
        """
        pass

    def query(self):
        """ Queries for notes and todos.

        Required parameters: queries, token
        Optional parameters: as_count, js_date
        """
        pass


class SyncAPI(APIMixin):
    """ Todoist Sync API makes it easy to retrieve and sync data with Todoist
    servers. It's great if you want to implement a client that stores all of
    the data locally and sync changes periodically.
    """
    def __init__(self, **kwargs):
        super(SyncAPI, self).__init__(**kwargs)
        self.api_url = API_SYNC_URL
        self.token_key = 'api_token'

    def get(self):
        """ Used to retrieve data (both all and only updated data).
        projects_timestamps can be used to only retrieve updated projects.
        Do note that at this time only Projects supports partially fetching,
        this is because only projects and items will grow a lot, the other data
        is small and does not change that much.

        Optional parameters: project_timestamps
        """
        pass

    def sync(self):
        """ Takes a list of JSON object commands which specify which changes
        should be done to the model. These changes could be adding projects,
        deleting tasks etc.

        Required parameters: items, token
        """
        pass