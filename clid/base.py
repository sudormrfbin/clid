#!/usr/bin/env python3

"""Base classes to be used by clid"""

import curses

import npyscreen as npy

class ClidCommandLine(npy.ActionControllerSimple):
    """Base class for the command line at the bootom of the screen"""

    def create(self):
        self.add_action('^:q$', self.exit_app, live=False)   # quit with ':q'

    def exit_app(self, command_line, widget_proxy, live):
        """Exit the app with ':q'"""
        exit()   # args are used internally by npyscreen


class ClidTextfield(npy.wgtextbox.Textfield):
    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers[curses.KEY_END] = self.h_end
        self.handlers[curses.KEY_HOME] = self.h_home

    def h_home(self, char):
        self.cursor_position = 0

    def h_end(self, char):
        self.cursor_position = len(self.value)

class ClidTitleText(npy.TitleText):
    _entry_type = ClidTextfield
