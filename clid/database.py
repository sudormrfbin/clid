#!/usr/bin/env python3

"""Contains database objects for helping clid"""

import os
import glob

import stagger
import npyscreen

from . import _const
from . import validators

CONFIG = os.path.expanduser('~/.clid.ini')


class Mp3DataBase(npyscreen.NPSFilteredDataBase):
    """Class to manage the structure of mp3 files in BASE_DIR.

       Attributes:
            file_dict(dict):
                dict with the filename as key and absolute path to
                file as value. Used for displaying files and changing
                metadata.
            settings(configobj.ConfigObj):
                used for accessing the ini file.
            pre_format(str):
                string with format specifiers used to display preview of
                files' tags.
            specifiers(list):
                list of format specifiers in pre_format
            meta_cache(dict):
                cache which holds the metadata of files as they are selected.

    """
    def __init__(self):
        super().__init__()

        self.settings = None   # set by main.ClidInterface
        self.file_dict = dict()
        self.meta_cache = dict()
        self.pre_format = ''
        self.specifiers = []

 # IDEA: set_values and set_search_list for updating values and search_list when refreshed

    def filter_data(self):
        if self._filter and self._values:
            return [mp3 for mp3 in self.get_all_values() if self._filter in mp3.lower()]
        else:
            return self.get_all_values()

    def load_preview_format(self):
        """Make approriate varibles to hold preview formats"""
        self.pre_format = self.settings['preview_format']
        self.specifiers = _const.FORMAT_PAT.findall(self.pre_format)

    def load_files_and_set_values(self):
        """- Get a list of mp3 files in `music_dir` recursively
           - Make a dict out of it
           - Assign it to `file_dict`
           - Set `_values` attribute
           - Empty the meta_cache
        """
        base = self.settings['music_dir']

        ret_list = []
        for dir_tree in os.walk(base, followlinks=True):   # get all mp3 files in the dir and sub-dirs
            ret_list.extend(glob.glob(dir_tree[0] + '/' + '*.mp3'))

        # make a dict with the basename as key and absolute path as value
        self.file_dict = dict([(os.path.basename(abspath), abspath) for abspath in ret_list])
        self._values = tuple(sorted(self.file_dict.keys()))   # sorted tuple of filenames
        self.meta_cache = dict()


    def parse_meta_for_status(self, filename):
        """Make a string like 'artist - album - track_number. title' from a filename
           (using file_dict and data[attributes])

           Args:
                filename: the filename(*not* the absolute path)
        """
        temp = self.pre_format   # make a copy of format and replace specifiers with tags
        if not filename in self.meta_cache:
            try:
                meta = stagger.read_tag(self.file_dict[filename])
                for spec in self.specifiers:   # str to convert track number to str if given
                    temp = temp.replace(spec, str(getattr(meta, _const.FORMAT[spec])))
                self.meta_cache[filename] = temp
            except stagger.errors.NoTagError:
                self.meta_cache[filename] = _const.FORMAT_PAT.sub('', temp)

        return self.meta_cache[filename]

    # def get_abs(self, filename):
        # return self.file_dict[filename]


class SettingsDataBase(object):
    """Class to manage the settings/config file.

       Attributes:
            settings(configobj.ConfigObj):
                `ConfigObj` object for the clid.ini file
            parent(npyscreen.FormMuttActiveTraditional):
                used to refer to parent form(pref.PreferencesView)
            disp_strings(list):
                list of formatted strings which will be used to display settings in the window
    """
    def __init__(self):
        self.parent = None   # set by parent; see docstring
        self.settings = None   # also set by parent
        self.disp_strings = []
        self.when_changed = None

    def set_attrs(self, parent, settings, when_changed):
        """Set attributes that can only be set after a particular external operation"""
        self.parent = parent
        self.settings = settings
        self.when_changed = when_changed

    def make_strings(self):
        """Make a list of strings which will be used to display the settings
           in the editing window
        """
        # number of characters after which value of an option is displayed
        max_length = len(max(self.settings.keys(), key=len)) + 3   # +3 is just to beautify
        self.disp_strings = []

        for key, value in self.settings.items():
            # number of spaces to add so that all options are aligned correctly
            spaces = (max_length - len(key)) * ' '
            self.disp_strings.append(key + spaces + value)


    def change_setting(self, key, new):
        """Change a setting in the clid.ini"""
        if key in self.settings:
            try:
                validators.VALIDATORS[key](new)
                self.settings[key] = new
                self.settings.write()
                self.when_changed.when_changed[key]()
            except validators.ValidationError as error:
                # self.parent.wCommand.print_message(str(error), 'WARNING')
                npyscreen.notify_confirm(message=str(error), title='Error', editw=1)
        else:
            npyscreen.notify_confirm(
                message='You\'ve got a typo, I think; ' + '"' + key + '"' + ' is not a valid option which can be set.',
                title='Error', editw=1
            )


class WhenChanged(object):
    """Class with functions to be executed when an option is changed.
       This is class is used by SettingsDataBase

       Attributes:
            settings(configobj.ConfigObj):
                For accessing settings
            main_form(npy.FormMuttActiveTraditionl):
                Actually the main form with the files view
            when_changed(dict):
                dict of str:function; str is a setting; function to be executed when corresponding
                setting is changed
    """
    def __init__(self, main_form, settings):
        self.settings = settings
        self.main_form = main_form
        self.when_changed = {
            'vim_mode': self.vim_mode,
            'music_dir': self.music_dir,
            'smooth_scroll': self.smooth_scroll,
            'preview_format': self.preview_format
        }

    def vim_mode(self):
        pass   # doesn't need anything

    def music_dir(self):
        self.main_form.value.load_files_and_set_values()
        self.main_form.load_files()

    def preview_format(self):
        self.main_form.value.meta_cache = dict()
        self.main_form.value.load_preview_format()
        self.main_form.wMain.set_status(self.main_form.wMain.get_selected())   # change current file's preview into new format

    def smooth_scroll(self):
        smooth = self.settings['smooth_scroll']
        self.main_form.wMain.slow_scroll = True if smooth == 'true' else False
