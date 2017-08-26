#!/usr/bin/env python3

"""Form class for editing the metadata of a track"""

import os
import curses

import stagger
import npyscreen as npy

from . import base
from . import _const


class EditMeta(npy.ActionFormV2):
    """Edit the metadata of a track.

       Attributes:
            in_insert_mode(bool):
                Used to decide whether the form is in insert/normal
                mode(if vi_keybindings are enabled). This is actually
                set as an attribute of the parent form so that all
                text boxes in the form are in the same mode.
    """

    def __init__(self, *args, **kwags):
        super().__init__(*args, **kwags)
        self.in_insert_mode = False

    def create(self):
        # error if placed in __init__
        self.TEXTBOX = base.ClidVimTitleText \
                if self.parentApp.settings['vim_mode'] == 'true'\
                else base.ClidTitleText   # vim keybindings if enabled

        self.file = self.parentApp.current_file
        try:
            self.meta = stagger.read_tag(self.file)
        except stagger.errors.NoTagError:
            temp = stagger.Tag23()   # create a id3v2.3 tag instance
            temp.album = ' '   # so that there is something to write to the file
            temp.write(self.parentApp.current_file)

            self.meta = stagger.read_tag(self.parentApp.current_file)
            self.meta.album = ''   # revert what was just done
            self.meta.write()

        self.filenamebox = self.add(self.TEXTBOX, name='Filename',
            value=os.path.basename(self.file).replace('.mp3', ''))
        self.nextrely += 2

        self.tit = self.add(self.TEXTBOX, name='Title', value=self.meta.title)
        self.nextrely += 1
        self.alb = self.add(self.TEXTBOX, name='Album', value=self.meta.album)
        self.nextrely += 1
        self.art = self.add(self.TEXTBOX, name='Artist', value=self.meta.artist)
        self.nextrely += 1
        self.ala = self.add(self.TEXTBOX, name='Album Artist', value=self.meta.album_artist)
        self.nextrely += 2

        self.gen = self.add(self.TEXTBOX, name='Genre', value=self.resolve_genre(self.meta.genre))
        self.nextrely += 1
        self.dat = self.add(self.TEXTBOX, name='Date/Year', value=self.meta.date)
        self.nextrely += 1
        self.tno = self.add(self.TEXTBOX, name='Track Number',
                            value=str(self.meta.track if self.meta.track != 0 else ''))
        self.nextrely += 2
        self.com = self.add(self.TEXTBOX, name='Comment', value=self.meta.comment)

    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers['^S'] = self.h_ok
        self.handlers['^Q'] = self.h_cancel

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
        self.editing = False
        self.parentApp.switchForm("MAIN")

    def on_ok(self):   # char is for handlers
        """Save and switch to standard view"""
        try:
            self.meta.date = self.dat.value
        except ValueError:
            npy.notify_confirm(message='Date should be of the form YYYY-MM-DD',
                               title='Invalid Date Format', editw=1)
            return None

        track = self.tno.value if self.tno.value != '' else '0'   # automatically converted to int by stagger
        try:
            int(track)
        except ValueError:
            npy.notify_confirm(message='Track number can only take integer values',
                               title='Invalid Track Number', editw=1)
            return None
        else:
            self.meta.track = track
        # FIXME: values of tags are reset to initial when ok is pressed(no prob with ^S)

        self.meta.title = self.tit.value
        self.meta.album = self.alb.value
        self.meta.genre = self.gen.value
        self.meta.artist = self.art.value
        self.meta.comment = self.com.value
        self.meta.album_artist = self.ala.value

        self.meta.write()

        new_filename = os.path.dirname(self.file) + '/' + self.filenamebox.value + '.mp3'
        if self.file != new_filename:   # filename was changed
            os.rename(self.file, new_filename)

        main_form = self.parentApp.getForm("MAIN")
        main_form.value.load_files_and_set_values()

        main_form.wMain.set_status(filename=os.path.basename(new_filename))   # show the new tags in the status line
        main_form.load_files()

        self.editing = False
        self.parentApp.switchForm("MAIN")
