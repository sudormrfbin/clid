#!/usr/bin/env python3

"""Contains database objects for helping clid"""

import os
import glob

import stagger
import npyscreen


BASE_DIR = '/mnt/0b6b53eb-f83a-4f34-9224-da2310643534/Music/'


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

        self.get_list()   # set file_dict attribute
        # self._set_data()   # set a dict of filenames mapping to their tags
        self._values = tuple(sorted(self.file_dict.keys()))   # sorted tuple of filenames


 # IDEA: set_values and set_search_list for updating values and search_list when refreshed

    def get_list(self):
        """Get a list of mp3 files in BASE_DIR recursively, make a dict
           out of it and assign it to file_dict
        """
        ret_list = []
        for dir_tree in os.walk(BASE_DIR):   # get all mp3 files in the dir and sub-dirs
            ret_list.extend(glob.glob(dir_tree[0] + '/' + '*.mp3'))

        # make a dict with the basename as key and absolute path as value
        self.file_dict = dict([(os.path.basename(abspath), abspath) for abspath in ret_list])

    def filter_data(self):
        if self._filter and self._values:
            return [mp3 for mp3 in self.get_all_values() if self._filter in mp3.lower()]
        else:
            return self.get_all_values()

    def _set_data(self):
        self.data = dict()
        for file in self.file_dict.values():
            try:
                metadata = stagger.read_tag(file)
                self.data[file] = (metadata.artist, metadata.album, metadata.track, metadata.title)
            except stagger.errors.NoTagError:
                pass

    def get_init_meta_status(self):
        """Get the value which will be the inital value of the second
           status bar(at startup)
        """
        # get the first filename shown, get the absolute path and then get the metadata:
        ret = self.data[self.file_dict[self.get_all_values()[0]]]
        return '{art} - {alb} - {tno}. {title}'.format(art=ret[0], alb=ret[1], tno=ret[2], title=ret[3])
