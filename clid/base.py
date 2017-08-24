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
    """Normal textbox with home and end keys working"""
    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers[curses.KEY_END] = self.h_end
        self.handlers[curses.KEY_HOME] = self.h_home

    def h_home(self, input):
        self.cursor_position = 0

    def h_end(self, input):
        self.cursor_position = len(self.value)


class ClidVimTextfield(ClidTextfield):
    """Textfield class to be used as input boxes for tag fields when editing tags
       if vim mode is enabled.
    """
    def __init__(self, *args, **kwargs):
        self.vim_handlers = {
            # movement
            'k': self.h_exit_up,
            'j': self.h_exit_down,
            'h': self.h_cursor_left,
            'l': self.h_cursor_right,
            curses.ascii.SP: self.h_cursor_right,   # Space
            curses.KEY_BACKSPACE: self.h_cursor_left,
            # deletion
            'X': self.h_delete_left,
            'x': self.h_delete_right,
            # insert chars
            'i': self.h_vim_insert_mode,
            'a': self.h_vim_append_char,
            'A': self.h_vim_append_char_at_end,
        }
        super().__init__(*args, **kwargs)   # set_up_handlers is called in __init__

    def vim_add_handlers(self):
        """Add vim keybindings to list of keybindings"""
        self.add_handlers(self.vim_handlers)

    def vim_remove_handlers(self):
        """Remove vim keybindings from list of keybindings"""
        for handler in self.vim_handlers:
            del self.handlers[handler]
        self.handlers[curses.KEY_BACKSPACE] = self.h_delete_left   # else nothing will happen

    def set_up_handlers(self):
        super().set_up_handlers()
        self.vim_add_handlers()
        self.handlers[curses.ascii.ESC] = self.h_vim_normal_mode   # is a bit slow

    def h_addch(self, input):
        if self.parent.in_insert_mode:   # add characters only if in insert mode
            super().h_addch(input)

    def h_vim_insert_mode(self, input):
        """Enter insert mode"""
        self.parent.in_insert_mode = True
        self.vim_remove_handlers()   # else `k`, j`, etc will not be added to text(will still act as keybindings)

    def h_vim_normal_mode(self, input):
        """Exit insert mode by pressing Esc"""
        self.parent.in_insert_mode = False
        self.cursor_position -= 1   # just like in vim
        self.vim_add_handlers()   # removed earlier when going to insert mode

    def h_vim_append_char(self, input):
        """Append characters, like `a` in vim"""
        self.h_vim_insert_mode(input)
        self.cursor_position += 1

    def h_vim_append_char_at_end(self, input):
        """Add characters to the end of the line, like `A` in vim"""
        self.h_vim_insert_mode(input)
        self.h_end(input)   # go to the end

class ClidVimTitleText(npy.TitleText):
    _entry_type = ClidVimTextfield

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
