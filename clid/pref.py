"""Window for editing preferences"""

#!/usr/bin/env python3

import npyscreen as npy

from . import database

class PrefCommandLine(npy.ActionControllerSimple):
    def create(self):
        self.add_action('^:set .+', self.change_setting, live=False)

    def change_setting(self, command_line, widget_proxy, live):
        setting = command_line[5:].split(sep='=')
        self.parent.value.change_setting(setting[0], setting[1])   # writes to the ini file

        # TODO: might wanna change this to something else after more choices for pref
        mainFm = self.parent.parentApp.getForm("MAIN")
        mainFm.value.load_files_and_set_values()
        mainFm.load_files()

        self.parent.load_pref()
# TODO: update the view if a setting is changed

class PrefMultiline(npy.MultiLine):
    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers['1'] = self.switch_to_main

    def switch_to_main(self, char):
        self.parent.parentApp.switchForm("MAIN")

    def h_select(self, char):
        current_setting = self.values[self.cursor_line].split(maxsplit=1)
        self.parent.wCommand.value = ':set ' + current_setting[0] + '=' + current_setting[1]

class PreferencesView(npy.FormMuttActiveTraditional):
    """View for editing preferences/settings"""
    MAIN_WIDGET_CLASS = PrefMultiline
    DATA_CONTROLER = database.SettingsDataBase
    ACTION_CONTROLLER = PrefCommandLine

    def create(self):
        super().create()
        self.set_value(self.DATA_CONTROLER())

        self.load_pref()

    def load_pref(self):
        self.value.make_strings()
        self.wMain.values = self.value.disp_strings

