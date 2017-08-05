#!/usr/bin/env python3

"""Contains database objects for helping clid"""

import os
import glob

import stagger
import npyscreen

from . import _const

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
        """- Get a list of mp3 files in BASE_DIR recursively
           - Make a dict out of it
           - Assign it to `file_dict`
           - Set `_values` attribute
        """
        base = self.settings['music_dir']

        ret_list = []
        for dir_tree in os.walk(base, followlinks=True):   # get all mp3 files in the dir and sub-dirs
            ret_list.extend(glob.glob(dir_tree[0] + '/' + '*.mp3'))

        # make a dict with the basename as key and absolute path as value
        self.file_dict = dict([(os.path.basename(abspath), abspath) for abspath in ret_list])
        self._values = tuple(sorted(self.file_dict.keys()))   # sorted tuple of filenames


    def parse_meta_for_status(self, filename):
        """Make a string like 'artist - album - track_number. title' from a filename
           (using file_dict and data[attributes])

           Args:
                filename: the filename(*not* the absolute path)
        """
        if not filename in self.meta_cache:
            try:
                meta = stagger.read_tag(self.file_dict[filename])
                temp = self.pre_format   # make a copy of format and replace specifiers with tags

                for spec in self.specifiers:   # str to convert track number to str if given
                    temp = temp.replace(spec, str(getattr(meta, _const.FORMAT[spec])))
                self.meta_cache[filename] = temp
            except stagger.errors.NoTagError:
                self.meta_cache[filename] = _const.FORMAT_PAT.sub('', self.specifiers)

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
            when_changed(dict):
                dict of str:function; str is a setting; function to be executed when corresponding
                setting is changed
    """
    def __init__(self):
        self.parent = None   # set by parent; see docstring
        self.settings = None   # also set by parent
        self.disp_strings = []
        self.when_changed = {
            'music_dir': self.music_dir,
            'preview_format': self.preview_format
        }

    def make_strings(self):
        """Make a list of strings which will be used to display the settings
           in the editing window
        """
        self.disp_strings = [key + '  ' + value for key, value in self.settings.items()]

    def change_setting(self, key, new):
        """Change a setting in the clid.ini"""
        if key in self.settings:
            self.settings[key] = new
            self.settings.write()
            self.when_changed[key]()

    def music_dir(self):
        """To be executed when `music_dir` option is changed"""
        main_form = self.parent.parentApp.getForm("MAIN")
        main_form.value.load_files_and_set_values()
        main_form.load_files()

    def preview_format(self):
        """To be executed when `preview_format` option is changed"""
        main_form = self.parent.parentApp.getForm("MAIN")
        main_form.value.meta_cache = dict()
        main_form.value.load_preview_format()
        main_form.wMain.set_status(main_form.wMain.get_selected())   # change current file's preview into new format
