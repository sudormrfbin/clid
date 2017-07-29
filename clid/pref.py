#!/usr/bin/env python3

"""Window for editing preferences"""

import npyscreen as npy

from . import base
from . import database


class PrefCommandLine(base.ClidCommandLine):
    def create(self):
        super().create()
        self.add_action('^:set .+', self.change_setting, live=False)

    def change_setting(self, command_line, widget_proxy, live):
        setting = command_line[5:].split(sep='=')
        self.parent.value.change_setting(setting[0], setting[1])   # writes to the ini file
        self.parent.value.when_changed[setting[0]]()

        self.parent.load_pref()
        self.parent.wMain.display()


class PrefMultiline(npy.MultiLine):
    def set_up_handlers(self):
        super().set_up_handlers()
        
        self.handlers['1'] = self.switch_to_main

    def switch_to_main(self, char):
        self.parent.parentApp.switchForm("MAIN")

    def h_select(self, char):
        with open('sdf', 'a') as f:
            f.write('multiline: ' + repr(self.parent.value) + '\n')
        current_setting = self.values[self.cursor_line].split(maxsplit=1)
        self.parent.wCommand.value = ':set ' + current_setting[0] + '=' + current_setting[1]


class PreferencesView(npy.FormMuttActiveTraditional):
    """View for editing preferences/settings"""
    MAIN_WIDGET_CLASS = PrefMultiline
    ACTION_CONTROLLER = PrefCommandLine

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_value(database.SettingsDataBase())
        self.value.parent = self
        self.load_pref()


    def create(self):
        super().create()
        self.wStatus1.value = 'Preferences '

    def load_pref(self):
        self.value.make_strings()
        self.wMain.values = self.value.disp_strings

