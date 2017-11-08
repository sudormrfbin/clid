#!/usr/bin/env python3

"""Form class for editing the metadata of a track"""

import os

import npyscreen as npy

from . import base
from . import const
from . import readtag


class SingleEditMetaView(base.ClidEditMetaView):
    """Edit the metadata of a *single* track."""
    def create(self):
        file = self.parentApp.current_files[0]
        meta = readtag.ReadTags(file)
        # show name of file(can be edited)
        self.filenamebox = self.add(
            widgetClass=self._get_textbox_cls()[0], name='Filename',
            labelColor='STANDOUT', color='CONTROL',
            value=os.path.basename(file).replace('.mp3', '')
            )
        self.nextrely += 2
        super().create()

        for tbox, field in const.TAG_FIELDS.items():  # show file's tag
            getattr(self, tbox).value = getattr(meta, field)

    def get_fields_to_save(self):
        return {tag: getattr(self, tbox).value for tbox, tag in const.TAG_FIELDS.items()}

    def do_after_saving_tags(self):
        """Rename the file if necessary."""
        mp3 = self.files[0]
        new_filename = os.path.join(os.path.dirname(mp3), self.filenamebox.value) + '.mp3'
        if mp3 != new_filename:   # filename was changed
            os.rename(mp3, new_filename)
            self.mp3db.rename_file(old=mp3, new=new_filename)
            self.parentApp.getForm("MAIN").load_files_to_show()


class MultiEditMetaView(base.ClidEditMetaView):
    """Edit metadata of multiple tracks"""
    def create(self):
        # show number of files selected
        self.add(npy.Textfield, color='STANDOUT', editable=False,
                 value='Editing {} files'.format(len(self.parentApp.current_files)))
        self.nextrely += 2
        super().create()

    def get_fields_to_save(self):
        # save only those fields which are not empty, to files
        temp = {}
        for tbox, tag in const.TAG_FIELDS.items():
            if getattr(self, tbox).value != '':
                temp[tag] = getattr(self, tbox).value
        return temp
