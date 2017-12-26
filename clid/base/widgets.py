#!/usr/bin/env python3

"""Base classes for Widgets"""

import curses
import weakref

import npyscreen as npy

from clid import util
from clid import const


class ClidTextfield(npy.wgtextbox.Textfield):
    """Normal textbox with home and end keys working"""
    def set_up_handlers(self):
        super().set_up_handlers()
        self.add_handlers({
            curses.KEY_END:  self.h_end,
            curses.KEY_HOME: self.h_home
        })

    def h_home(self, char):
        """Home Key"""
        self.cursor_position = 0

    def h_end(self, char):
        """End Key"""
        self.cursor_position = len(self.value)


class ClidVimTextfield(ClidTextfield):
    """Textfield class to be used as input boxes for tag fields when editing tags
       if vim mode is enabled.
       Attributes:
            vim_handlers(dict): dict of key mappings with key: handler.
    """
    def __init__(self, *args, **kwargs):
        self.vim_handlers = {
            # movement
            'k': self.h_exit_up,
            'j': self.h_exit_down,
            'h': self.h_cursor_left,
            'l': self.h_cursor_right,
            curses.ascii.SP:      self.h_cursor_right,   # Space
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

    def set_up_handlers(self):
        super().set_up_handlers()
        self.vim_add_handlers()
# TODO: replace esc with users key
        self.handlers[curses.ascii.ESC] = self.h_vim_normal_mode  # ESC is a bit slow

    def vim_add_handlers(self):
        """Add vim keybindings to list of keybindings. Used when entering
           Normal mode.
        """
        self.add_handlers(self.vim_handlers)

    def vim_remove_handlers(self):
        """Remove vim keybindings from list of keybindings. Used when
           entering Insert mode.
        """
        for handler in self.vim_handlers:
            del self.handlers[handler]
        # revert backspace to what it normally does
        self.handlers[curses.KEY_BACKSPACE] = self.h_delete_left

    def h_addch(self, inp):
        """Add characters only if in insert mode"""
        if self.parent.in_insert_mode:
            super().h_addch(inp)

    def h_vim_insert_mode(self, char):
        """Enter insert mode"""
        self.parent.in_insert_mode = True
        self.vim_remove_handlers()
        # else `k`, j`, etc will not be added to text(will still act as keybindings)

    def h_vim_normal_mode(self, char):
        """Exit insert mode by pressing Esc"""
        self.parent.in_insert_mode = False
        self.cursor_position -= 1   # just like in vim
        self.vim_add_handlers()   # removed earlier when going to insert mode

    def h_vim_append_char(self, char):
        """Append characters, like `a` in vim"""
        self.h_vim_insert_mode(char)
        self.cursor_position += 1

    def h_vim_append_char_at_end(self, char):
        """Add characters to the end of the line, like `A` in vim"""
        self.h_vim_insert_mode(char)
        self.h_end(char)   # go to the end


class ClidGenreTextfield(ClidTextfield, npy.Autocomplete):
    """Special textbox for genre tag with autocompleting"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.genres = [genre.lower() for genre in const.GENRES]
        self.handlers.update({
            curses.ascii.TAB: self.h_auto_complete
        })

    def h_auto_complete(self, char):
        """Attempt to auto-complete genre"""
        value = self.value.lower()
        complete_list = [genre.title() for genre in self.genres if value in genre]
        if len(complete_list) is 1:
            self.value = complete_list[0]
        else:
            self.value = complete_list[self.get_choice(complete_list)]
        self.cursor_position = len(self.value)


class ClidVimGenreTextfiled(ClidVimTextfield, ClidGenreTextfield):
    """Like ClidGenreTextfield, but with vim keybindings"""
    def __init__(self, *args, **kwargs):
        ClidVimTextfield.__init__(self, *args, **kwargs)
        ClidGenreTextfield.__init__(self, *args, **kwargs)


class ClidCommandLine(npy.fmFormMuttActive.TextCommandBoxTraditional, ClidTextfield):
    """Command line shown at bottom of screen"""

    # TODO: HistoryDB with _search_history(deque) and _command_history
    # TODO: pickle the data structs for history and reload on startup

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prev_msg = None

    def set_value(self, value):
        """Set text and place cursor at the end"""
        self.value = value
        self.cursor_position = len(self.value)
        self.display()

    def when_value_edited(self):
        if self.value != self.prev_msg:
            self.show_bold = False
            self.color = 'DEFAULT'
        super().when_value_edited()

    def show_notif(self, title, msg, color):
        """Show a notification(msg) with text color set to `color`"""
        self.color = color
        self.show_bold = True
        self.prev_msg = '({title}): {message}'.format(title=title, message=msg)
        self.set_value(self.prev_msg)

    def h_execute_command(self, *args, **keywords):
        if self.history and self.value.startswith(':'):
            self._history_store.append(self.value)
            self._current_history_index = False

            command = self.value
            self.value = ''
            self.parent.action_controller.process_command_complete(command, weakref.proxy(self))
        else:
            self.value = ''


class ClidMultiLine(npy.MultiLine):
    """MultiLine class used for showing files and prefs"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.slow_scroll = self.parent.prefdb.is_option_enabled('smooth_scroll')

    def set_current_status(self, *args, **kwargs):
        """Show additional information about the thing under the cursor"""
        data = self.parent.maindb.parse_info_for_status(
            str_needing_info=self.get_selected(), *args, **kwargs
            )
        self.parent.wStatus2.value = data
        self.parent.display()

    def get_selected(self):
        """Return the item under the cursor line"""
        return self.values[self.cursor_line]

    # Movement Handlers

    @util.run_if_window_not_empty(update_status_line=True)
    def h_cursor_page_up(self, char):
        super().h_cursor_page_up(char)

    @util.run_if_window_not_empty(update_status_line=True)
    def h_cursor_page_down(self, char):
        super().h_cursor_page_down(char)

    @util.run_if_window_not_empty(update_status_line=True)
    def h_cursor_line_up(self, char):
        super().h_cursor_line_up(char)

    @util.run_if_window_not_empty(update_status_line=True)
    def h_cursor_line_down(self, char):
        super().h_cursor_line_down(char)

    @util.run_if_window_not_empty(update_status_line=True)
    def h_cursor_beginning(self, char):
        super().h_cursor_beginning(char)

    @util.run_if_window_not_empty(update_status_line=True)
    def h_cursor_end(self, char):
        super().h_cursor_end(char)
