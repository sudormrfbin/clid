#!/usr/bin/env python3

__version__ = '0.3.1'

import curses
import npyscreen as npy

from . import database
from . import editmeta
# import database
# import editmeta

class CommandLine(npy.ActionControllerSimple):
    """Command line at the bottom.

       Note:
            self.parent refers to ClidInterface -> class
            self.parent.value refers to database.Mp3DataBase -> class
    """
    def create(self):
        self.add_action('^:q', self.exit_app, live=False)   # quit with ':q'
        self.add_action('^/.+', self.search_for_files, live=True)   # search with '/'


    def exit_app(self, command_line, widget_proxy, live):
        exit()   # args are used internally by npyscreen


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
    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers[curses.ascii.ESC] = self.h_revert_escape


    def h_revert_escape(self, char):
        """Handler which switches from the filtered view of search results
           to the normal view with the complete list of files.
        """
        if self.parent.after_search_now_filter_view:   # if screen is showing search results
            self.values = self.parent.value.get_all_values()   # revert
            self.parent.after_search_now_filter_view = False

            self.display()

# TODO: make it faster

    def h_cursor_line_down(self, char):
        """Modified handler(move down) which also changes the second status
           line's value according to the file which is highlighted
        """
        if (self.cursor_line + 1) < len(self.values):   # need to +1 as cursor_line is the index
            filename = self.values[self.cursor_line + 1]
            self.parent.wStatus2.value = self.parent.value.parse_meta_for_status(filename=filename)
            self.parent.display()

        super().h_cursor_line_down(char)   # code has some returns in between

    def h_cursor_line_up(self, char):
        """Modified handler(move up) which also changes the second status
           line's value according to the file which is highlighted
        """
        super().h_cursor_line_up(char)

        filename = self.values[self.cursor_line]
        self.parent.wStatus2.value = self.parent.value.parse_meta_for_status(filename=filename)
        self.parent.display()

# TODO: add handlers for page up and page down
# TODO: make the cursor go to top/bottom if key is pressed at top/bottom

    def h_select(self, char):
        self.parent.parentApp.current_file = self.parent.value.file_dict[self.values[self.cursor_line]]
        self.parent.parentApp.switchForm("EDIT")

class ClidInterface(npy.FormMuttActiveTraditional):
    """The main app with the ui.

       Note:
            self.value refers to an instance of DATA_CONTROLER
    """
    ACTION_CONTROLLER = CommandLine
    MAIN_WIDGET_CLASS = ClidMultiline
    DATA_CONTROLER = database.Mp3DataBase

    def create(self):
        super().create()   # so that status widgets are created
        self.set_value(self.DATA_CONTROLER())   # isn't automatically done(open issue ?)

        # used to revert screen(ESC) to standard view after a search(see class ClidMultiline)
        self.after_search_now_filter_view = False

        self.wMain.values = self.value.get_all_values()
        self.wStatus1.value = 'clid v' + __version__ + ' '
        self.wStatus2.value = self.value.parse_meta_for_status(self.wMain.values[0])


class ClidApp(npy.NPSAppManaged):
    def onStart(self):
        npy.setTheme(npy.Themes.ElegantTheme)
        self.current_file = None   # changed when a file is selected in main screen
        self.addForm("MAIN", ClidInterface)
        self.addFormClass("EDIT", editmeta.EditMeta)   # addFormClass to create a new instance every time
