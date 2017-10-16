#!/usr/bin/env python3

"""Window for editing preferences"""

import npyscreen as npy

from . import base
from . import database


class PrefMultiline(npy.MultiLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers.update({
            '1': self.h_switch_to_main
        })

    def h_switch_to_main(self, char):
        """Go to Main View"""
        self.parent.parentApp.switchForm("MAIN")

    def h_select(self, char):
        current_setting = self.values[self.cursor_line].split(maxsplit=1)
        self.parent.wCommand.value = ':set ' + current_setting[0] + '=' + current_setting[1]


class PreferencesView(npy.FormMuttActiveTraditional):
    """View for editing preferences/settings"""
    MAIN_WIDGET_CLASS = PrefMultiline
    ACTION_CONTROLLER = base.ClidActionController
    COMMAND_WIDGET_CLASS = base.ClidCommandLine
    # TODO: define self.prefdb and self.mp3db

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_value(database.PreferencesSettingsDataBase())
        settings = self.parentApp.settings
        when_changed = database.PreferencesWhenChanged(
            main_form=self.parentApp.getForm("MAIN"), settings=settings
            )
        self.value.set_attrs(parent=self, settings=settings, when_changed=when_changed)
        self.value.make_strings()
        self.load_pref()

        self.wStatus1.value = 'Preferences '

    def load_pref(self):
        """[Re]load preferences after being changed"""
        self.value.make_strings()
        self.wMain.values = self.value.disp_strings
