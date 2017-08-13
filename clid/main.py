#!/usr/bin/env python3

__version__ = '0.6.2'

import os
import curses

import configobj
import npyscreen as npy

from . import base
from . import pref
from . import database
from . import editmeta


class MainActionController(base.ClidActionController):
    """Object that recieves recieves inpout in command line
       at the bottom.

       Note:
            self.parent refers to ClidInterface -> class
            self.parent.value refers to database.Mp3DataBase -> class
    """
    def create(self):
        super().create()
        self.add_action('^/.+', self.search_for_files, live=True)   # search with '/'

    def change_setting(self, command_line, widget_proxy, live):
        setting = command_line[5:].split(sep='=')
        pref_form = self.parent.parentApp.getForm("SETTINGS")
        pref_form.value.change_setting(setting[0], setting[1])   # writes to the ini file
        pref_form.value.when_changed[setting[0]]()

        pref_form.load_pref()
        pref_form.wMain.display()
        self.parent.display()


    def search_for_files(self, command_line, widget_proxy, live):
        """Search for files while given a string"""
        if len(command_line[1:]) > 2:   # first char will be '/'
            self.parent.value.set_filter(command_line[1:])

        else:   # search only if at least 3 charecters are given
            self.parent.value.set_filter(None)

        self.parent.after_search_now_filter_view = True
        self.parent.wMain.values = self.parent.value.get()
        self.parent.wMain.display()


class ClidMultiline(npy.MultiLine):
    """MultiLine class to be used by clid. `Esc` has been modified to revert
       the screen back to the normal view after a searh has been performed
       (the search results will be shown; blank if no matches are found)

       Note:
            self.parent refers to ClidInterface -> class
            self.parent.value refers to database.Mp3DataBase -> class
    """

    def set_status(self, filename):
        """Set the the value of self.parent.wStatus2 with metadata of file under cursor."""
        self.parent.wStatus2.value = self.parent.value.parse_meta_for_status(filename=filename)

    def get_selected(self):
        return self.values[self.cursor_line]

    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers['u'] = self.h_reload_files
        self.handlers['2'] = self.h_switch_to_settings
        self.handlers[curses.ascii.ESC] = self.h_revert_escape


    def h_reload_files(self, char):
        """Reload files in `music_dir`"""
        self.parent.value.load_files_and_set_values()
        self.parent.load_files()

    def h_revert_escape(self, char):
        """Handler which switches from the filtered view of search results
           to the normal view with the complete list of files.
        """
        if self.parent.after_search_now_filter_view:   # if screen is showing search results
            self.values = self.parent.value.get_all_values()   # revert
            self.parent.after_search_now_filter_view = False

            self.display()

# TODO: make it faster

    def h_switch_to_settings(self, char):
        self.parent.parentApp.switchForm("SETTINGS")

    
    # NOTE: The if blocks with self.cursor_line is mainly to prevent the app from
    #       crashing Eg: when there is nothing to display(empty folder)

    def h_cursor_line_down(self, char):
        """Modified handler(move down) which also changes the second status
           line's value according to the file which is highlighted
        """
        if (self.cursor_line + 1) < len(self.values):   # need to +1 as cursor_line is the index
            filename = self.values[self.cursor_line + 1]
            self.set_status(filename)
            self.parent.display()

        super().h_cursor_line_down(char)   # code has some returns in between

    def h_cursor_line_up(self, char):
        """Modified handler(move up) which also changes the second status
           line's value according to the file which is highlighted
        """
        super().h_cursor_line_up(char)

        if self.cursor_line -1 > 0:
            self.set_status(self.get_selected())
            self.parent.display()

    def h_cursor_page_down(self, char):
        super().h_cursor_page_down(char)
        if self.cursor_line != -1:    # -1 if there is nothing to display
            self.set_status(self.get_selected())
            self.parent.display()

    def h_cursor_page_up(self, char):
        super().h_cursor_page_up(char)
        if self.cursor_line -1 > 0:
            self.set_status(self.get_selected())
            self.parent.display()

    def h_select(self, char):
        self.parent.parentApp.current_file = self.parent.value.file_dict[self.values[self.cursor_line]]
        self.parent.parentApp.switchForm("EDIT")

# TODO: smooth scroll


class ClidInterface(npy.FormMuttActiveTraditional):
    """The main app with the ui.

       Note:
            self.value refers to an instance of DATA_CONTROLER
    """
    DATA_CONTROLER = database.Mp3DataBase
    MAIN_WIDGET_CLASS = ClidMultiline
    ACTION_CONTROLLER = MainActionController
    COMMAND_WIDGET_CLASS = base.ClidCommandLine

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_value(self.DATA_CONTROLER())
        self.value.settings = self.parentApp.settings
        self.value.load_files_and_set_values()
        self.value.load_preview_format()

        self.load_files()

        # widgets are created by self.create() in super()
        self.wStatus1.value = 'clid v' + __version__ + ' '

        try:
            self.wStatus2.value = self.value.parse_meta_for_status(self.wMain.values[0])
        except IndexError:   # thrown if directory doest not have mp3 files
            self.wStatus2.value = 'No Files Found In Directory'
            self.wMain.values = []

        self.after_search_now_filter_view = False
        # used to revert screen(ESC) to standard view after a search(see class ClidMultiline)

    # change to `load_pref`
    def load_files(self):
        """Set the mp3 files that will be displayed"""
        self.wMain.values = self.value.get_all_values()


class ClidApp(npy.NPSAppManaged):
    """Class used by npyscreen to manage forms.

       Attributes:
            current_file(str):
                file selected when in main_view(path)
            settings(configobj.ConfigObj):
                object used to read and write preferences
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.current_file = None   # changed when a file is selected in main screen
        self.settings = configobj.ConfigObj(os.path.expanduser('~/.clid.ini'))

    def onStart(self):
        npy.setTheme(npy.Themes.ElegantTheme)
        self.addForm("MAIN", ClidInterface)
        self.addForm("SETTINGS", pref.PreferencesView)
        self.addFormClass("EDIT", editmeta.EditMeta)   # addFormClass to create a new instance every time
