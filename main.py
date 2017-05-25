"""Clid is an app to edit the id3v2 tags of mp3 files from the
   command line.
"""

__version__ = '0.1'

import curses

import database
import npyscreen as npy


class CommandLine(npy.ActionControllerSimple):
    """Command line at the bottom."""

    def create(self):
        self.add_action('^:q', self.exit_app, live=False)   # quit with ':q'
        self.add_action('^/.+', self.search_for_files, live=True)

    def exit_app(self, command_line, widget_proxy, live):
        """Exit from the app."""
        # args are used internally by npy
        exit()

    def search_for_files(self, command_line, widget_proxy, live):
        """Search for files while given a string"""
        if len(command_line[1:]) > 2:
            self.parent.value.set_filter(command_line[1:])
        else:
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
    """
    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers[curses.ascii.ESC] = self.h_revert_escape

    def h_revert_escape(self, char):
        """Handler which switches from the filtered view of search results
           to the normal view with the complete list of files.
        """
        if self.parent.after_search_now_filter_view:   # if screen is showing search results
            self.parent.wMain.values = self.parent.value.get_all_values()   # display all the values
            self.parent.after_search_now_filter_view = False
# TODO: make it faster
# IDEA: use search_for_files to reset(/a to command_line ?)

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

        # used to revert screen(ESC) to standard view after a search has been done
        # see class ClidMultiline
        self.after_search_now_filter_view = False

        self.wStatus1.value = 'clid v0.1 '
        self.wStatus2.value = 'clid status line '
        self.wMain.values = self.value.get()


class ClidApp(npy.NPSAppManaged):
    def onStart(self):
        self.addForm("MAIN", ClidInterface)


if __name__ == '__main__':
    ClidApp().run()
