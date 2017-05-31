#!/usr/bin/env python3

"""Form class for editing the metadata of a track"""

import npyscreen as npy
import stagger


class EditMeta(npy.ActionFormV2):
    """Edit the metadata of a track"""
    def create(self):
        try:
            self.meta = stagger.read_tag(self.parentApp.current_file)
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
        self.nextrely += 1

        self.tno = self.add(npy.TitleText, name='Track Number', value=str(self.meta.track))
        # convert to str as a TypeError will be raised by npyscreen as you can't len() int
        # (nedded by npyscreen to calculate cursor position)
        self.nextrely += 1

        # TODO: add genre(need to fix the number id of genres)
        # gen = self.add(npy.TitleText, name='Genre', value=self.meta.genre)

    def on_cancel(self):
        """Switch to standard view at once without saving"""
        self.editing = False
        self.parentApp.switchForm("MAIN")

    def on_ok(self):
        """Save and switch to standard view"""
        self.meta.title = self.tit.value
        self.meta.album = self.alb.value
        self.meta.artist = self.art.value
        self.meta.album_artist = self.ala.value

        # TODO: make tno accept only numbers(or make a popup if other characters are given)
        self.meta.track = self.tno.value   # automatically converted to int by stagger
        self.meta.write()
        self.editing = False
        self.parentApp.switchForm("MAIN")
