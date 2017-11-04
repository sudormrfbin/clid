#!/usr/bin/env python3

"""Window for editing preferences"""

import npyscreen as npy

from . import base


class PrefMultiline(base.ClidMultiLine):
    def h_select(self, char):
        option, value = self.values[self.cursor_line].split(maxsplit=1)
        self.parent.wCommand.value = ':set {opt}={val}'.format(opt=option, val=value)


class PreferencesView(npy.FormMuttActiveTraditional, base.ClidForm):
    """View for editing preferences/settings"""
    MAIN_WIDGET_CLASS = PrefMultiline
    ACTION_CONTROLLER = base.ClidActionController
    COMMAND_WIDGET_CLASS = base.ClidCommandLine

    def __init__(self, parentApp, *args, **kwargs):
        base.ClidForm.__init__(self, parentApp)
        self.maindb = self.prefdb
        super().__init__(*args, **kwargs)
        base.ClidForm.enable_resizing(self)

        self.handlers.update({
            '1': self.h_switch_to_main
        })

        self.load_pref()

        self.wStatus1.value = 'Preferences '
        self.wMain.set_current_status()

    def h_switch_to_main(self, char):
        """Go to Main View"""
        self.parentApp.switchForm("MAIN")

    def load_pref(self):
        """[Re]load preferences after being changed"""
        self.wMain.values = self.prefdb.get_values_to_display()
        self.display()
