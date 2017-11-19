#!/usr/bin/env python3

"""Base classes to be used by clid"""

import os
import re
import curses

import npyscreen as npy

from . import util
from . import const
from . import readtag


class ClidActionController(npy.ActionControllerSimple):
    """Base class for the command line at the bottom of the screen"""

    def create(self):
        self.add_action('^:q$', lambda *args, **kwargs: exit(), live=False)   # exit
        self.add_action('^:bind .+', function=self.change_key, live=False)
        self.add_action('^:set .+', function=self.change_setting, live=False)

    def change_setting(self, command_line, widget_proxy, live):
        """Change a setting in the ini file.
           command_line will be of the form `:set option=value`
        """
        option, value = command_line[5:].split(sep='=')
        self.parent.prefdb.set_pref(option, value)
        # reload and display settings
        self.parent.parentApp.getForm("SETTINGS").load_pref()

    def change_key(self, command_line, widget_proxy, live):
        """Change a keybinding.
           command_line will be of the form `:bind action=key`
        """
        option, value = command_line[6:].split(sep='=')
        self.parent.prefdb.set_key(option, value)
        # reload and display settings
        self.parent.parentApp.getForm("SETTINGS").load_pref()


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
    def __init__(self, *args, **kwargs):
        ClidVimTextfield.__init__(self, *args, **kwargs)
        ClidGenreTextfield.__init__(self, *args, **kwargs)


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
    def when_value_edited(self):
        self.cursor_position = len(self.value)
        super().when_value_edited()


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


class ClidDataBase():
    """General structure of databases used by clid"""

    def __init__(self, app):
        self.app = app

    def get_values_to_display(self):
        """Return a list of strings that will be displayed on the screen"""
        pass

    def get_filtered_values(self, search):
        """Search the list of items returned by `get_values_to_display` for the
           substring `search`
        """
        if search == '':
            return self.get_values_to_display()
        search = search.lower()
        try:
            # check for invalid regex
            re.compile(search)
        except re.error:
            return self.get_values_to_display()
        if self.app.prefdb.is_option_enabled('use_regex_in_search'):
            return [item for item in self.get_values_to_display() if re.search(search, item)]
        return [item for item in self.get_values_to_display() if search in item.lower()]

    def parse_info_for_status(self, str_needing_info, *args, **kwargs):
        """Return a string that will be displayed on the status line, providing
           additional info on the item under the cursor
        """
        pass


class ClidForm():
    def __init__(self, parentApp):
        self.parentApp = parentApp
        self.mp3db = self.parentApp.mp3db
        self.prefdb = self.parentApp.prefdb

    def enable_resizing(self):
        """Fix resizing by modifying the minimum number of columns and lines
           the form needs. Cannot be put in __init__, as the __init__ method
           of [another] parent class of the child class overrides these attributes.
           So this method is called afterwards
        """
        self.min_c = 72   # min number of columns(width)
        self.min_l = 24   # min number of lines(height)


class ClidEditMetaView(npy.ActionFormV2, ClidForm):
    """Edit the metadata of a track.
       Attributes:
            files(list): List of files whose tags are being edited.
            in_insert_mode(bool):
                Indicates whether the form is in insert/normal
                mode(if vim_mode are enabled). This is actually
                set as an attribute of the parent form so that all
                text boxes in the form are in the same mode.
    """
    OK_BUTTON_TEXT = 'Save'
    PRESERVE_SELECTED_WIDGET_DEFAULT = True   # to remember last position

    def __init__(self, parentApp, *args, **kwags):
        ClidForm.__init__(self, parentApp)
        super().__init__(*args, **kwags)
        ClidForm.enable_resizing(self)

        self.editw = self.parentApp.current_field   # go to last used tag field
        self.in_insert_mode = False
        self.files = self.parentApp.current_files
        self.load_keys()

    def load_keys(self):
        get_key = self.prefdb.get_key
        self.handlers.update({
            get_key('save_tags')           : self.h_ok,
            get_key('cancel_saving_tags')  : self.h_cancel
        })

    def _get_textbox_cls(self):
        """Return tuple of classes(normal and genre) to be used as textbox input
           field, depending on the value of the setting `vim_mode`
        """
        if self.prefdb.is_option_enabled('vim_mode'):
            tbox, gbox = ClidVimTextfield, ClidVimGenreTextfiled
        else:
            tbox, gbox = ClidTextfield, ClidGenreTextfield

        # make textboxes with labels
        class TitleTbox(npy.TitleText):
            _entry_type = tbox

        class TitleGbox(npy.TitleText):
            _entry_type = gbox

        return (TitleTbox, TitleGbox)

    def create(self):
        tbox, gbox = self._get_textbox_cls()
        self.tit = self.add(widgetClass=tbox, name='Title')
        self.nextrely += 1
        self.alb = self.add(widgetClass=tbox, name='Album')
        self.nextrely += 1
        self.art = self.add(widgetClass=tbox, name='Artist')
        self.nextrely += 1
        self.ala = self.add(widgetClass=tbox, name='Album Artist')
        self.nextrely += 2
        self.gen = self.add(widgetClass=gbox, name='Genre')
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
            return
        # track number check
        if not util.is_track_number_valid(self.tno.value):
            npy.notify_confirm(message='Track number can only take integer values',
                               title='Invalid Track Number', editw=1)
            return
        # FIXME: values of tags are reset to initial when ok is pressed(no prob with ^S)

        tag_fields = self.get_fields_to_save().items()
        for mp3 in self.files:
            meta = readtag.ReadTags(mp3)
            for tag, value in tag_fields:
                setattr(meta, tag, value)
            meta.write(mp3)
            # update meta cache
            self.mp3db.parse_info_for_status(
                str_needing_info=os.path.basename(mp3), force=True
                )

        # show the new tags of file under cursor in the status line
        self.parentApp.getForm("MAIN").wMain.set_current_status()
        self.do_after_saving_tags()

        self.parentApp.current_field = self._get_tbox_to_remember()
        self.switch_to_main()

    def on_cancel(self):
        """Switch to main view at once without saving"""
        self.parentApp.current_field = self._get_tbox_to_remember()
        self.switch_to_main()

    def _get_tbox_to_remember(self):
        """Return the int representing the textbox(tag field) to be remembered"""
        if self.editw > len(self._widgets__) - 3:   # cursor is in ok/cancel button
            return len(self._widgets__) - 3   # return last textbox field
        return self.editw
