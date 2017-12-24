#!/usr/bin/env python3

"""Database for managing music files"""

import os
import glob

from clid import base
from clid import const
from clid import readtag


class Mp3DataBase(base.ClidDataBase):
    """Class to manage mp3 files.
       Attributes:
            app(npyscreen.NPSAppManaged): Reference to parent application
            preview_format(str):
                String with format specifiers used to display preview of
                files' tags; Eg: '%a - %l - %t'
            format_specs(list):
                List of format specifiers in preview_format; Eg:['%l', '%a']
            meta_cache(dict):
                Cache which holds the metadata of files as they are selected.
                Basename of file as key and metadata as value.
            mp3_basenames(list):
                Holds basename of mp3 files in alphabetical order.
            file_dict(dict):
                Basename as key and abs path as value, of mp3 files.
    """

    def __init__(self, app):
        super().__init__(app)
        self.load_mp3_files_from_music_dir()
        self.load_preview_format()

    def load_preview_format(self):
        """[Re]load the preview format and. Used when `preview_format` option
           is changed by user.
           Attributes Changed:
                meta_cache, preview_format, format_specs
        """
        self.meta_cache = dict()   # empty the meta_cache as preview format has changed
        self.preview_format = self.app.prefdb.get_pref('preview_format')
        self.format_specs = const.FORMAT_PAT.findall(self.preview_format)

    def load_mp3_files_from_music_dir(self):
        """Re[load] the list of mp3 files in case `music_dir` is changed
           Attributes Changed:
                file_dict, mp3_basenames
        """
        mp3_files = []
        mp3_dir = self.app.prefdb.get_pref('music_dir')
        # get all mp3 files in the dir and sub-dirs
        for dir_tree in os.walk(mp3_dir, followlinks=True):
            mp3_found = glob.glob(os.path.join(dir_tree[0], '*.mp3'))
            mp3_files.extend(mp3_found)

        # make a dict with the basename as key and absolute path as value
        self.file_dict = {os.path.basename(mp3): mp3 for mp3 in mp3_files}
        # alphabetically ordered  tuple of filenames
        self.mp3_basenames = tuple(sorted(self.file_dict.keys()))

    def get_values_to_display(self):
        """Return values that is to be displayed in the corresponding form"""
        return self.mp3_basenames

    def get_abs_path(self, path):
        """Return the absolute path of path from self.file_dict"""
        return self.file_dict[path]

    def parse_info_for_status(self, str_needing_info, force=False):
        """Make a string that will be displayed in the status line of corresponding
           form, based on the user's `preview_format` option,
           (Eg: `artist - album - track_name`) and then add it to meta_cache.
           Args:
                filename: the filename(basename of file)
                force: reconstruct the string even if it is already in meta_cache and
                       add it to meta_cache
           Returns:
                str: String constructed
           Note:
                `str_needing_info` will be a basename of a file
        """
        filename = str_needing_info
        # make a copy of format and replace specifiers with tags
        p_format = self.preview_format
        if (filename not in self.meta_cache) or force:
            meta = readtag.ReadTags(self.get_abs_path(filename))
            for spec in self.format_specs:
                tag = const.FORMAT_SPECS[spec]   # get corresponding tag name
                p_format = p_format.replace(spec, getattr(meta, tag))
            self.meta_cache[filename] = p_format

        return self.meta_cache[filename]

    def rename_file(self, old, new):
        """Rename a file. This method replaces all references of `old` with new
           Used externally when a file is renamed.
           Args:
                old(str): abs path to old name of file
                new(str): abs path to new name of file
        """
        del self.file_dict[os.path.basename(old)]
        self.file_dict[os.path.basename(new)] = new
        # reconstruct to include new file
        self.mp3_basenames = tuple(sorted(self.file_dict.keys()))

        del self.meta_cache[os.path.basename(old)]
        self.parse_info_for_status(os.path.basename(new))   # replace in meta_cache
