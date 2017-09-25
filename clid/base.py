#!/usr/bin/env python3

"""Base classes to be used by clid"""

import os
import curses

import stagger
import npyscreen as npy

from . import _const

class ClidActionController(npy.ActionControllerSimple):
    """Base class for the command line at the bottom of the screen"""

    def create(self):
        self.add_action('^:q$', lambda *args, **kwargs: exit(), live=False)   # quit with ':q'
        self.add_action('^:set .+', self.change_setting, live=False)

    def change_setting(self, command_line, widget_proxy, live):
        """Change a setting in the ini file"""
        pass   # different for main and pref view; defined in respective files


class ClidTextfield(npy.wgtextbox.Textfield):
    """Normal textbox with home and end keys working"""
    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers[curses.KEY_END] = self.h_end
        self.handlers[curses.KEY_HOME] = self.h_home

    def h_home(self, char):
        self.cursor_position = 0

    def h_end(self, char):
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

    def h_addch(self, char):
        if self.parent.in_insert_mode:   # add characters only if in insert mode
            super().h_addch(char)

    def h_vim_insert_mode(self, char):
        """Enter insert mode"""
        self.parent.in_insert_mode = True
        self.vim_remove_handlers()   # else `k`, j`, etc will not be added to text(will still act as keybindings)

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


class ClidEditMeta(npy.ActionFormV2):
    """Edit the metadata of a track.

       Attributes:
            files(list): List of files whose tags are being edited.
            _label_textbox(ClidTextfield):
                Text box which acts like a label(cannot be edited).
            _title_textbox(ClidTextfield):
                Text box with a title, to be used as input field for tags.
            in_insert_mode(bool):
                Used to decide whether the form is in insert/normal
                mode(if vi_keybindings are enabled). This is actually
                set as an attribute of the parent form so that all
                text boxes in the form are in the same mode.
    """
    def __init__(self, *args, **kwags):
        super().__init__(*args, **kwags)
        self.handlers.update({
            '^S': self.h_ok,
            '^Q': self.h_cancel
        })
        self.in_insert_mode = False
        self.files = self.parentApp.current_files

    def set_textbox(self):
        """Set the text boxes to be used(with or without vim-bindings).
           Called by child classes.
        """
        if self.parentApp.settings['vim_mode'] == 'true':
            self._title_textbox = ClidVimTitleText   # vim keybindings if enabled
            self._label_textbox = ClidVimTextfield
        else:
            self._title_textbox = ClidTitleText
            self._label_textbox = ClidTextfield

    def create(self):
        self.tit = self.add(self._title_textbox, name='Title')
        self.nextrely += 1
        self.alb = self.add(self._title_textbox, name='Album')
        self.nextrely += 1
        self.art = self.add(self._title_textbox, name='Artist')
        self.nextrely += 1
        self.ala = self.add(self._title_textbox, name='Album Artist')
        self.nextrely += 2
        self.gen = self.add(self._title_textbox, name='Genre')
        self.nextrely += 1
        self.dat = self.add(self._title_textbox, name='Date/Year')
        self.nextrely += 1
        self.tno = self.add(self._title_textbox, name='Track Number')
        self.nextrely += 2
        self.com = self.add(self._title_textbox, name='Comment')

    def resolve_genre(self, num_gen):
        """Convert numerical genre values to readable values. Genre may be
           saved as a str of the format '(int)' by applications like EasyTag.

           Args:
                num_gen (str): str representing the genre.

           Returns:
                str: Name of the genre (Electronic, Blues, etc). Returns
                num_gen itself if it doesn't match the format.
        """
        match = _const.GENRE_PAT.findall(num_gen)

        if match:
            try:
                return _const.GENRES[int(match[0])]
            except IndexError:
                return ''
        else:
            return num_gen

    def h_ok(self, char):
        """Handler to save the tags"""
        self.on_ok()

    def h_cancel(self, char):
        """Handler to cancel the operation"""
        self.on_cancel()

    def on_cancel(self):   # char is for handlers
        """Switch to standard view at once without saving"""
        self.switch_to_main()

    def switch_to_main(self):
        self.editing = False
        self.parentApp.switchForm("MAIN")

    def get_fields_to_save(self):
        """Return a modified version of _const.TAG_FIELDS. Only tag fields in
           returned dict will be saved to file; used by children
        """
        pass

    def on_ok(self):   # char is for handlers
        """Save and switch to standard view"""
        # date format check
        match = _const.DATE_PATTERN.match(self.dat.value)
        if match is None or match.end() != len(self.dat.value):
            npy.notify_confirm(message='Date should be of the form YYYY-MM-DD HH:MM:SS',
                               title='Invalid Date Format', editw=1)
            return None
        # track number check
        track = str(self.tno.value) or '0'   # automatically converted to int by stagger
        if not track.isnumeric():
            npy.notify_confirm(message='Track number can only take integer values',
                               title='Invalid Track Number', editw=1)
            return None
        # FIXME: values of tags are reset to initial when ok is pressed(no prob with ^S)

        main_form = self.parentApp.getForm("MAIN")
        tag_fields = self.get_fields_to_save().items()
        for mp3 in self.files:
            try:
                meta = stagger.read_tag(mp3)
            except stagger.NoTagError:
                meta = stagger.Tag23()   # create an ID3v2.3 instance
            for tbox, field in tag_fields:   # equivalent to `meta.title = self.tit.value`...
                tag = track if field == 'track' else getattr(self, tbox).value   # get value to be written to file
                setattr(meta, field, tag)
            meta.write(mp3)
            # update meta cache
            main_form.value.parse_meta_for_status(filename=os.path.basename(mp3), force=True)

        # show the new tags in the status line
        main_form.wMain.set_current_status()
        return True
