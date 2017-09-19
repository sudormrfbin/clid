#!/usr/bin/env python3

"""Form class for editing the metadata of a track"""

import os
import curses

import stagger
import npyscreen as npy

from . import base
from . import _const


class SingleEditMeta(base.ClidEditMeta):
    """Edit the metadata of a *single* track."""
    def create(self):
        self.set_textbox()
        file = self.parentApp.current_files[0]
        try:
            meta = stagger.read_tag(file)
        except stagger.NoTagError:
            meta = stagger.Tag23()   # create a id3v2.3 tag instance

        self.filenamebox = self.add(self._title_textbox, name='Filename',
                                    value=os.path.basename(file).replace('.mp3', ''))
        self.nextrely += 2
        super().create()

        for tbox, field in _const.TAG_FIELDS.items():  # show file's tag
            getattr(self, tbox).value = str(getattr(meta, field))   # str for track_number

    def get_fields_to_save(self):
        return _const.TAG_FIELDS

    def on_ok(self):
        c = super().on_ok()
        if c is None:
            return None   # some error like invalid date or track number has occured
        mp3 = self.files[0]
        new_filename = os.path.dirname(mp3) + '/' + self.filenamebox.value + '.mp3'
        if mp3 != new_filename:   # filename was changed
            os.rename(mp3, new_filename)
            main_form = self.parentApp.getForm("MAIN")
            main_form.value.replace_file(old=mp3, new=new_filename)
            main_form.load_files()

        self.switch_to_main()


class MultiEditMeta(base.ClidEditMeta):
    def create(self):
        self.set_textbox()
        self.add(npy.Textfield, color='STANDOUT', editable=False,
                 value='Batch tagging {} files'.format(len(self.parentApp.current_files)))
        self.nextrely += 2
        super().create()

    def get_fields_to_save(self):
        # save only those fields which are not empty, to files
        return {tbox: field for tbox, field in _const.TAG_FIELDS.items()\
                if getattr(self, tbox).value}

    def on_ok(self):
        c = super().on_ok()
        if c is None:
            return None   # some error like invalid date or track number has occured
        self.switch_to_main()
