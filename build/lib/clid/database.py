#!/usr/bin/env python3

"""Contains database objects for helping clid"""

import os
import glob

import stagger
import npyscreen
import configobj

CONFIG = os.path.expanduser('~/.clid.ini')


class Mp3DataBase(npyscreen.NPSFilteredDataBase):
    """Class to manage the structure of mp3 files in BASE_DIR.

       Attributes:
            file_dict(dict):
                dict with the filename as key and absolute path to
                file as value. Used for displaying files and changing
                metadata
    """
    def __init__(self):
        super().__init__()

        self.load_files_and_set_values()   # set `file_dict` and `_values` attribute
        self.meta_cache = dict()   # cache which holds the metadata of files as they are selected

 # IDEA: set_values and set_search_list for updating values and search_list when refreshed


    def load_files_and_set_values(self):
        """- Get a list of mp3 files in BASE_DIR recursively
           - Make a dict out of it
           - Assign it to `file_dict`
           - Set `_values` attribute
        """
        base = configobj.ConfigObj(CONFIG)['music_dir']

        ret_list = []
        for dir_tree in os.walk(base, followlinks=True):   # get all mp3 files in the dir and sub-dirs
            ret_list.extend(glob.glob(dir_tree[0] + '/' + '*.mp3'))

        # make a dict with the basename as key and absolute path as value
        self.file_dict = dict([(os.path.basename(abspath), abspath) for abspath in ret_list])
        self._values = tuple(sorted(self.file_dict.keys()))   # sorted tuple of filenames

    def filter_data(self):
        if self._filter and self._values:
            return [mp3 for mp3 in self.get_all_values() if self._filter in mp3.lower()]
        else:
            return self.get_all_values()

    def parse_meta_for_status(self, filename):
        """Make a string like 'artist - album - track_number. title' from a filename
           (using file_dict and data[attributes])

           Args:
                filename: the filename(*not* the absolute path)
        """
        if not filename in self.meta_cache:
            try:
                metadata = stagger.read_tag(self.file_dict[filename])
                self.meta_cache[filename] = '{art} - {alb} - {tno}. {title} '.format(
                    art=metadata.artist,
                    alb=metadata.album,
                    # stagger saves track number as 0 if it is not given(won't be shown in players)
                    tno=metadata.track if metadata.track != 0 else ' ',
                    title=metadata.title
                    )
            except stagger.errors.NoTagError:
                self.meta_cache[filename] = ' - - . '

        return self.meta_cache[filename]

    # def get_abs(self, filename):
        # return self.file_dict[filename]


class SettingsDataBase(object):
    """Class to manage the settings/config file.

       Attributes:
            _settings(configobj.ConfigObj): `ConfigObj` object for the clid.ini file
            disp_strings(list):
                list of formatted strings which will be used to display settings in the window
    """
    def __init__(self):
        self._settings = configobj.ConfigObj(CONFIG)
        self.make_strings()

    def make_strings(self):
        """Make a list of strings which will be used to display the settings
           in the editing window
        """
        self.disp_strings = [key + '  ' + value for key, value in self._settings.items()]

    def change_setting(self, key, new):
        """Change a setting in the clid.ini"""
        if key in self._settings:
            self._settings[key] = new
            self._settings.write()
