#!/usr/bin/env python3

"""Window for editing preferences"""

import npyscreen as npy

from . import base


class PrefMultiline(base.ClidMultiLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handlers.update({
            '1': self.h_switch_to_main
        })

    def h_switch_to_main(self, char):
        """Go to Main View"""
        self.parent.parentApp.switchForm("MAIN")

    def h_select(self, char):
        option, value = self.values[self.cursor_line].split(maxsplit=1)
        self.parent.wCommand.value = ':set {opt}={val}'.format(opt=option, val=value)


class PreferencesView(npy.FormMuttActiveTraditional, base.ClidForm):
    """View for editing preferences/settings"""
    MAIN_WIDGET_CLASS = PrefMultiline
    ACTION_CONTROLLER = base.ClidActionController
    COMMAND_WIDGET_CLASS = base.ClidCommandLine

    def __init__(self, parentApp, *args, **kwargs):
        super(npy.eveventhandler.EventHandler, self).__init__(parentApp)  # base.ClidForm
        self.maindb = self.prefdb
        super().__init__(*args, **kwargs)
        super(npy.eveventhandler.EventHandler, self).enable_resizing()

        self.load_pref()

        self.wStatus1.value = 'Preferences '
        self.wMain.set_current_status()

    def load_pref(self):
        """[Re]load preferences after being changed"""
        self.wMain.values = self.prefdb.get_values_to_display()
        self.display()
