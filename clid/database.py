#!/usr/bin/env python3

"""Contains database objects for helping clid"""

import os
import glob

import configobj
import npyscreen as npy

from . import base
from . import const
from . import readtag
from . import validators


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

    def get_abs_path(self, base):
        """Return the absolute path of base from self.file_dict"""
        return self.file_dict[base]

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
        temp = self.preview_format   # make a copy of format and replace specifiers with tags
        if (filename not in self.meta_cache) or force:
            meta = readtag.ReadTags(self.get_abs_path(filename))
            for spec in self.format_specs:
                tag = const.FORMAT_SPECS[spec]   # get corresponding tag name
                temp = temp.replace(spec, getattr(meta, tag))
            self.meta_cache[filename] = temp

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


class PreferencesDataBase(base.ClidDataBase):
    """Class to manage the settings/config file
       Attributes:
            _pref(configobj.ConfigObj): Stores clid's settings
            app(npyscreen.NPSAppManaged): Reference to parent application
            when_changed(WhenOptionChanged)
    """
    def __init__(self, app):
        super().__init__(app)
        self.when_changed = WhenOptionChanged(app=self.app)
        self._pref = configobj.ConfigObj(const.CONFIG_DIR + 'clid.ini')

    def get_pref(self, option):
        """Return the current setting for `option`"""
        return self._pref[option]

    def get_values_to_display(self):
        """Return a list of strings which will be used to display the settings
           in the editing window
        """
        # number of characters after which value of an option is displayed
        max_length = len(max(self._pref.keys(), key=len)) + 3   # +3 is just to beautify
        ret = []

        for key, value in self._pref.items():
            # number of spaces to add so that all options are aligned correctly
            spaces = (max_length - len(key)) * ' '
            ret.append(key + spaces + value)
        return ret

    def parse_info_for_status(self, str_needing_info):
        """Return a short description of `str_needing_info`
           Note:
                `str_needing_info` will be a preference like `vim_mode   true`
        """
        pref = str_needing_info.split(maxsplit=1)[0]   # get only the pref, not value
        return const.PREF_DESC[pref]

    def is_option_enabled(self, option):
        """Check whether `option` is set to 'true' or 'false',
           in preferences.
           Args:
                option(str): option to be checked, like vim_mode
           Returns:
                bool: True if enabled, False otherwise
        """
        return True if self.get_pref(option) == 'true' else False

    def set_pref(self, option, new_value):
        """Change a setting.
           Args:
                option(str): Setting that is to be changed
                new_value(str): New value of the setting
        """
        if option in self._pref:
            try:
                validators.validate(option, new_value)
            except validators.ValidationError as err:
                # invalid value for specified option
                npy.notify_confirm(message=str(err), title='Error', editw=True)
            else:
                self._pref[option] = new_value
                self._pref.write()   # save to file
                self.when_changed.run_hook(option)   # changes take effect
        else:
            # invalid option(not in preferences)
            npy.notify_confirm(
                '"{}" is an invalid option'.format(option), title='Error', editw=True
            )


class WhenOptionChanged():
    """Class containing function to be run when an option is changed so
       the app doesn't have to be relaunched to see the effects.
       Used *only* by PreferencesDataBase.
    """
    def __init__(self, app):
        self.app = app

    def run_hook(self, option):
        """Run the function which correspond to option(str)"""
        getattr(self, option)()

    def vim_mode(self):
        pass   # doesn't need anything

    def music_dir(self):
        self.app.mp3db.load_mp3_files_from_music_dir()
        self.app.getForm("MAIN").load_files_to_show()

    def preview_format(self):
        self.app.mp3db.load_preview_format()
        self.app.getForm("MAIN").wMain.set_current_status()
        # change current file's preview into new format

    def smooth_scroll(self):
        scroll_option = self.app.prefdb.is_option_enabled('smooth_scroll')
        self.app.getForm("MAIN").wMain.slow_scroll = scroll_option

    def use_regex_in_search(self):
        pass
