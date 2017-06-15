#!/usr/bin/env python3

"""Contains database objects for helping clid"""

import os
import glob

import stagger
import npyscreen


BASE_DIR = os.path.expanduser('~/Music/')


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
        self.meta_cache = dict()   # cache which holds the metadata of files as they are selected
        self._values = tuple(sorted(self.file_dict.keys()))   # sorted tuple of filenames


 # IDEA: set_values and set_search_list for updating values and search_list when refreshed

    def get_list(self):
        """Get a list of mp3 files in BASE_DIR recursively, make a dict
           out of it and assign it to file_dict
        """
        ret_list = []
        for dir_tree in os.walk(BASE_DIR, followlinks=True):   # get all mp3 files in the dir and sub-dirs
            ret_list.extend(glob.glob(dir_tree[0] + '/' + '*.mp3'))

        # make a dict with the basename as key and absolute path as value
        self.file_dict = dict([(os.path.basename(abspath), abspath) for abspath in ret_list])

    def filter_data(self):
        if self._filter and self._values:
            return [mp3 for mp3 in self.get_all_values() if self._filter in mp3.lower()]
        else:
            return self.get_all_values()

# try:
#                 metadata = stagger.read_tag(file)
#                 self.data[file] = (metadata.artist, metadata.album, metadata.track, metadata.title)
#             except stagger.errors.NoTagError:
#                 pass

    def parse_meta_for_status(self, filename):
        """Make a string like 'artist - album - track_number. title' from a filename
           (using file_dict and data[attributes])

           Args:
                filename: the filename(*not* the absolute path)
        """
        if not filename in self.meta_cache:
            try:
                metadata = stagger.read_tag(self.file_dict[filename])
                self.meta_cache[filename] = (metadata.artist, metadata.album, metadata.track, metadata.title)
            except stagger.errors.NoTagError:
                self.meta_cache[filename] = ('', '', '', '')

        ret = self.meta_cache[filename]
        return '{art} - {alb} - {tno}. {title} '.format(art=ret[0], alb=ret[1], tno=ret[2], title=ret[3])

    # def get_abs(self, filename):
        # return self.file_dict[filename]
