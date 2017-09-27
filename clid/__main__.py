#!/usr/bin/env python3

"""Clid is an app to edit the id3v2 tags of mp3 files from the command line."""

import configobj
import npyscreen as npy

from . import main
from . import pref
from . import const
from . import editmeta


class ClidApp(npy.NPSAppManaged):
    """Class used by npyscreen to manage forms.

       Attributes:
            current_files(list):
                list of abs path of files selected for editing
            settings(configobj.ConfigObj):
                object used to read and write preferences
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_files = []   # changed when a file is selected in main screen
        self.settings = configobj.ConfigObj(const.CONFIG_DIR + 'clid.ini')

    def onStart(self):
        npy.setTheme(npy.Themes.ElegantTheme)
        self.addForm("MAIN", main.MainView)
        self.addForm("SETTINGS", pref.PreferencesView)
        # addFormClass to create a new instance every time
        self.addFormClass("MULTIEDIT", editmeta.MultiEditMetaView)
        self.addFormClass("SINGLEEDIT", editmeta.SingleEditMetaView)


def run():
    ClidApp().run()

if __name__ == '__main__':
    run()
