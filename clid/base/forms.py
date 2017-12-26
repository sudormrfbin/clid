#!/usr/bin/env python3

"""Base classes for Forms"""

import os

import npyscreen as npy

from clid import base
from clid import util
from clid import readtag


class ClidForm():
    """Base class for Forms"""

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

    def show_notif(self, title, msg):
        """Notify the user about `msg`"""
        # child classes will have wCommand attribute
        self.wCommand.show_notif(title, msg)


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
            get_key('save_tags'): self.h_ok,
            get_key('cancel_saving_tags'): self.h_cancel
        })

    def show_notif(self, title, msg):
        npy.notify_confirm(message=msg, form_color=util.get_color(title),
                           title=title, editw=1)

    def _get_textbox_cls(self):
        """Return tuple of classes(normal and genre) to be used as textbox input
           field, depending on the value of the setting `vim_mode`
        """
        if self.prefdb.is_option_enabled('vim_mode'):
            tbox, gbox = base.ClidVimTextfield, base.ClidVimGenreTextfiled
        else:
            tbox, gbox = base.ClidTextfield, base.ClidGenreTextfield

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
            self.show_notif(msg='Date should be of the form YYYY-MM-DD HH:MM:SS',
                            title='Error')
            return
        # track number check
        if not util.is_track_number_valid(self.tno.value):
            self.show_notif(msg='Track number can only take integer values',
                            title='Error')
            return
        # FIXME: values of tags are reset to initial when ok is pressed(no prob
        # with ^S)

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
