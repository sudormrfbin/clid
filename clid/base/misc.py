#!/usr/bin/env python3

"""Base classes for miscellaneous objects"""

import re

import npyscreen as npy


class ClidActionController(npy.ActionControllerSimple):
    """Base class for the command line at the bottom of the screen"""

    def create(self):
        self.add_action('^:q(uit)?$', lambda *args, **kwargs: exit(), live=False)
        self.add_action('^:bind .+', function=self.change_key, live=False)
        self.add_action('^:set .+', function=self.change_setting, live=False)

    def change_setting(self, command_line, widget_proxy, live):
        """Change a setting in the ini file.
           command_line will be of the form `:set option=value`
        """
        option, value = command_line[5:].split(sep='=')
        self.parent.prefdb.set_pref(option, value)
        # reload and display settings
        self.parent.parentApp.getForm("SETTINGS").load_pref()

    def change_key(self, command_line, widget_proxy, live):
        """Change a keybinding.
           command_line will be of the form `:bind action=key`
        """
        option, value = command_line[6:].split(sep='=')
        self.parent.prefdb.set_key(option, value)
        # reload and display settings
        self.parent.parentApp.getForm("SETTINGS").load_pref()


class ClidDataBase():
    """General structure of databases used by clid"""

    def __init__(self, app):
        self.app = app

    def get_values_to_display(self):
        """Return a list of strings that will be displayed on the screen"""
        pass

    def get_filtered_values(self, search):
        """Search the list of items returned by `get_values_to_display` for the
           substring `search`
        """
        if search == '':
            return self.get_values_to_display()
        search = search.lower()
        if self.app.prefdb.is_option_enabled('use_regex_in_search'):
            try:
                # check for invalid regex
                re.compile(search)
                return [item for item in self.get_values_to_display() if re.search(search, item)]
            except re.error:
                return self.get_values_to_display()
        return [item for item in self.get_values_to_display() if search in item.lower()]

    def parse_info_for_status(self, str_needing_info, *args, **kwargs):
        """Return a string that will be displayed on the status line, providing
           additional info on the item under the cursor
        """
        pass
