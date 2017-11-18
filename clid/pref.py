#!/usr/bin/env python3

"""Window for editing preferences"""

import npyscreen as npy

from . import base
from . import util


class PrefMultiline(base.ClidMultiLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.high_lines = util.get_lines_to_be_highlighted(
            self.parent.prefdb.get_section_names()
            )   # list of strings to be highlighted when displaying prefs - section names

    def h_select(self, char):
        if self.get_selected() in self.high_lines:
            return None
        # find section to which current pref belongs
        l = self.values[:self.cursor_line]
        l.reverse()
        section = l[l.index(' ') - 1]
        opt, val = self.get_selected().split(maxsplit=1)

        if section == 'General':
            self.parent.wCommand.value = ':set {opt}={val}'.format(opt=opt, val=val)
        elif section == 'Keybindings':
            self.parent.wCommand.value = ':bind {opt}={val}'.format(opt=opt, val=val)

    def set_current_status(self, *args, **kwargs):
        if self.get_selected() in self.high_lines:
            self.parent.wStatus2.value = ''  # cursor under section name or blank line
            self.parent.display()
        else:
            super().set_current_status()

    def _set_line_highlighting(self, line, value_indexer):
        """Highlight sections"""
        try:
            if self.values[value_indexer] in self.high_lines:
                self.set_is_line_important(line, True)
        except IndexError:
            # value of value_indexer may be upto the current height of the window
            # so if all prefs fit in the screen, value_indexer may be > len(self.values)
            pass
        self.set_is_line_cursor(line, False)


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

        self.load_keys()
        self.load_pref()

        self.wStatus1.value = 'Preferences '
        self.wMain.set_current_status()

    def load_keys(self):
        self.handlers.update({
            self.prefdb.get_key('files_view'): self.h_switch_to_files_view
        })

    def h_switch_to_files_view(self, char):
        """Go to Main View"""
        self.parentApp.switchForm("MAIN")

    def load_pref(self):
        """[Re]load preferences after being changed"""
        self.wMain.values = self.prefdb.get_values_to_display()
        self.display()
