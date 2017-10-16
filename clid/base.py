#!/usr/bin/env python3

"""Base classes to be used by clid"""

import os
import curses

import npyscreen as npy

from . import util
from . import readtag


class ClidActionController(npy.ActionControllerSimple):
    """Base class for the command line at the bottom of the screen"""

    def create(self):
        self.add_action('^:q$', lambda *args, **kwargs: exit(), live=False)   # quit with ':q'
        self.add_action('^:set .+', self.change_setting, live=False)

    def change_setting(self, command_line, widget_proxy, live):
        """Change a setting in the ini file.
           command_line will be of the form `:set option=value`
        """
        option, value = command_line[5:].split(sep='=')
        self.parent.prefdb.set_pref(option, value)
        # reload and display settings
        self.parent.parentApp.getForm("SETTINGS").load_pref()


class ClidTextfield(npy.wgtextbox.Textfield):
    """Normal textbox with home and end keys working"""
    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers[curses.KEY_END] = self.h_end
        self.handlers[curses.KEY_HOME] = self.h_home

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
        self.handlers[curses.KEY_BACKSPACE] = self.h_delete_left   # else backspace will not work

    def set_up_handlers(self):
        super().set_up_handlers()
        self.vim_add_handlers()
        self.handlers[curses.ascii.ESC] = self.h_vim_normal_mode   # is a bit slow

    def h_addch(self, char):
        """Add characters only if in insert mode"""
        if self.parent.in_insert_mode:
            super().h_addch(char)

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


class ClidVimTitleText(npy.TitleText):
    """Textbox with label and vim keybindings"""
    _entry_type = ClidVimTextfield


class ClidTitleText(npy.TitleText):
    """Textbox with label and without vim keybindings"""
    _entry_type = ClidTextfield


class ClidCommandLine(npy.fmFormMuttActive.TextCommandBoxTraditional, ClidTextfield):
    """Command line shown at bottom of screen"""
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


class ClidEditMetaView(npy.ActionFormV2):
    """Edit the metadata of a track.
       Attributes:
            files(list): List of files whose tags are being edited.
            in_insert_mode(bool):
                Indicates whether the form is in insert/normal
                mode(if vim_mode are enabled). This is actually
                set as an attribute of the parent form so that all
                text boxes in the form are in the same mode.
    """
    def __init__(self, *args, **kwags):
        super().__init__(*args, **kwags)
        self.handlers.update({
            '^S': self.h_ok,
            '^Q': self.h_cancel
        })
        self.mp3db = self.parentApp.mp3db
        self.prefdb = self.parentApp.prefdb
        self.in_insert_mode = False
        self.files = self.parentApp.current_files

    def _get_textbox_cls(self):
        """Return a class to be used as textbox input field, depending on the
           value of the setting `vim_mode`
        """
        if self.prefdb.is_option_enabled('vim_mode'):
            return ClidVimTitleText
        return ClidTitleText

    def create(self):
        tbox = self._get_textbox_cls()
        self.tit = self.add(widgetClass=tbox, name='Title')
        self.nextrely += 1
        self.alb = self.add(widgetClass=tbox, name='Album')
        self.nextrely += 1
        self.art = self.add(widgetClass=tbox, name='Artist')
        self.nextrely += 1
        self.ala = self.add(widgetClass=tbox, name='Album Artist')
        self.nextrely += 2
        self.gen = self.add(widgetClass=tbox, name='Genre')
        self.nextrely += 1
        self.dat = self.add(widgetClass=tbox, name='Date/Year')
        self.nextrely += 1
        self.tno = self.add(widgetClass=tbox, name='Track Number')
        self.nextrely += 2
        self.com = self.add(widgetClass=tbox, name='Comment')

    def h_ok(self, char):
        """Handler to save the tags"""
        self.on_ok()

    def h_cancel(self, char):
        """Handler to cancel the operation"""
        self.on_cancel()

    def on_cancel(self):
        """Switch to main view at once without saving"""
        self.switch_to_main()

    def switch_to_main(self):
        """Switch to main view. Used by `on_cancel` (at once) and
           `on_ok` (after saving tags).
        """
        self.editing = False
        self.parentApp.switchForm("MAIN")

    def get_fields_to_save(self):
        """Return a dict with name of tag as key and value of textbox
           with tag name as value; Eg: {'artist': value of artist textbox}
        """
        pass

    def do_after_saving_tags(self):
        """Stuff to do after saving tags, like renaming the mp3 file.
           Overridden by child classes
        """
        pass

    def on_ok(self):
        """Save and switch to standard view"""
        # date format check
        if not util.is_date_in_valid_format(self.dat.value):
            npy.notify_confirm(message='Date should be of the form YYYY-MM-DD HH:MM:SS',
                               title='Invalid Date Format', editw=1)
            return None
        # track number check
        if not util.is_track_number_valid(self.tno.value):
            npy.notify_confirm(message='Track number can only take integer values',
                               title='Invalid Track Number', editw=1)
            return None
        # FIXME: values of tags are reset to initial when ok is pressed(no prob with ^S)

        tag_fields = self.get_fields_to_save().items()
        for mp3 in self.files:
            meta = readtag.ReadTags(mp3)
            for tag, value in tag_fields:
                setattr(meta, tag, value)
            meta.write(mp3)
            # update meta cache
            self.mp3db.parse_info_for_status(filename=os.path.basename(mp3), force=True)

        # show the new tags of file under cursor in the status line
        self.parentApp.getForm("MAIN").set_current_status()
        self.do_after_saving_tags()

        self.switch_to_main()
