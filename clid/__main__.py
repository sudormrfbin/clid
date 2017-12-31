#!/usr/bin/env python3

"""Clid is an app to edit the id3v2 tags of mp3 files from the command line."""

import curses

import configobj
import npyscreen

from . import const
from . import forms
from . import database


class ClidApp(npyscreen.NPSAppManaged):
    """Class used by npyscreen to manage forms.

       Attributes:
            current_files(list):
                List of abs path of files selected for editing
            settings(configobj.ConfigObj):
                Object used to read and write preferences
            mp3db(database.Mp3DataBase):
                Used to manage mp3 files. Handles discovering files, storing a
                metadata cache, etc
            prefdb(database.PreferencesDataBase):
                Used to manage preferences. Handles validating new settings, etc
            current_field(int):
                Used to automatically jump to last selected tag field when
                editing tags
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_files = []   # changed when a file is selected in main screen
        self.current_field = 0   # remember last edited tag field
        self.settings = configobj.ConfigObj(const.CONFIG_DIR + 'clid.ini')
        # databases for managing mp3 files and preferences
        self.prefdb = database.PreferencesDataBase(app=self)
        self.mp3db = database.Mp3DataBase(app=self)

    def set_current_files(self, files):
        """Set `current_files` attribute"""
        self.current_files = [self.mp3db.get_abs_path(file) for file in files]

    def show_notif(self, title, msg):
        """Notify the user of something, either using the command line or a popup"""
        self._THISFORM.show_notif(title, msg)

    def onStart(self):
        self.configure_mouse_support()

        npyscreen.setTheme(npyscreen.Themes.ElegantTheme)
        self.addForm("MAIN", forms.MainView)
        self.addForm("SETTINGS", forms.PreferencesView)
        # addFormClass to create a new instance every time
        self.addFormClass("MULTIEDIT", forms.MultiEditMetaView)
        self.addFormClass("SINGLEEDIT", forms.SingleEditMetaView)

    def configure_mouse_support(self):
        """Configure mouse to be enabled or disabled"""
        if self.prefdb.is_option_enabled('mouse_support') is True:
            curses.mousemask(curses.ALL_MOUSE_EVENTS)
        else:
            curses.mousemask(0)   # do not listen for mouse events


def run():
    """Launch the app. This function is also used as an entry point."""
    ClidApp().run()


if __name__ == '__main__':
    run()
