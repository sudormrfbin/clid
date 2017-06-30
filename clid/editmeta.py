#!/usr/bin/env python3

"""Form class for editing the metadata of a track"""

import os

import stagger
import npyscreen as npy

from . import _genres


class EditMeta(npy.ActionFormV2):
    """Edit the metadata of a track"""
    def create(self):
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

        self.tit = self.add(npy.TitleText, name='Title', value=self.meta.title)
        self.nextrely += 1
        self.alb = self.add(npy.TitleText, name='Album', value=self.meta.album)
        self.nextrely += 1
        self.art = self.add(npy.TitleText, name='Artist', value=self.meta.artist)
        self.nextrely += 1
        self.ala = self.add(npy.TitleText, name='Album Artist', value=self.meta.album_artist)
        self.nextrely += 2

        self.gen = self.add(npy.TitleText, name='Genre', value=self.resolve_genre(self.meta.genre))
        self.nextrely += 1
        self.dat = self.add(npy.TitleText, name='Date/Year', value=self.meta.date)
        self.nextrely += 1
        self.tno = self.add(npy.TitleText, name='Track Number',
                            value=str(self.meta.track if self.meta.track != 0 else ''))
        self.nextrely += 2
        self.com = self.add(npy.TitleText, name='Comment', value=self.meta.comment)

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
        match = _genres.GENRE_PAT.findall(num_gen)

        if match:
            try:
                return _genres.GENRES[int(match[0])]
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
        self.meta.date = self.dat.value
        # FIXME: error thrown when date is not in the format YYYY-MM-DD

        self.meta.title = self.tit.value
        self.meta.album = self.alb.value
        self.meta.genre = self.gen.value
        self.meta.artist = self.art.value
        self.meta.comment = self.com.value
        self.meta.album_artist = self.ala.value

        track = self.tno.value if self.tno.value != '' else '0'   # automatically converted to int by stagger
        try:
            int(track)
        except ValueError:
            npy.notify_confirm(message='Track Number can only take integer values',
                               title='Track Number not an integer', editw=0)
            return None
        else:
            self.meta.track = track
        # FIXME: values of tags are reset to initial when ok is pressed(no prob with ^S)

        self.meta.write()

        status_meta = '{art} - {alb} - {tno}. {title} '.format(
            art=self.meta.artist,
            alb=self.meta.album,
            tno=self.meta.track if self.meta.track != 0 else ' ',
            title=self.meta.title
            )
        main_form = self.parentApp.getForm("MAIN")
        main_form.wStatus2.value = status_meta

        # update the metadata cache(database.Mp3DataBase.meta_cache) with new tags
        main_form.value.meta_cache[os.path.basename(self.file)] = status_meta

        self.editing = False
        self.parentApp.switchForm("MAIN")
