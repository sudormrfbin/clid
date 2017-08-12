#!/usr/bin/env python3

"""Base classes to be used by clid"""

import curses

import npyscreen as npy

class ClidActionController(npy.ActionControllerSimple):
    """Base class for the command line at the bottom of the screen"""

    def create(self):
        self.add_action('^:q$', self.exit_app, live=False)   # quit with ':q'
        self.add_action('^:set .+', self.change_setting, live=False)


    def exit_app(self, command_line, widget_proxy, live):
        """Exit the app with ':q'"""
        exit()   # args are used internally by npyscreen

    def change_setting(self, command_line, widget_proxy, live):
        """Change a setting in the ini file"""
        pass   # different for main and pref view; defined in respective files

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


class ClidCommandLine(npy.fmFormMuttActive.TextCommandBoxTraditional, ClidTextfield):
    # def print_message(self, msg, color):
    #     """Print a message into the command line.

    #        Args:
    #             msg(str): message to be displayed.
    #             color(str):
    #                 Color with which the message should be displayed. See npyscreen.npysThemes
    #     """
    #     self.color = color
    #     self.show_bold = True
    #     self.value = msg
    #     # self.color = 'DEFAULT'
    #     # self.show_bold = False
    pass
