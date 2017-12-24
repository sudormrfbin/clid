#!/usr/bin/env python3

"""Database for managing preferences"""

import configobj

from clid import util
from clid import base
from clid import const
from clid import validators


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

        # build status line help msg cache
        self.pref_help = {}
        for section in self._pref.values():
            for option, help_msg in section.comments.items():
                self.pref_help[option] = help_msg[0][2:] + ' '  # slice to remove `# `

    def get_pref(self, option):
        """Return the current setting for `option` from General section"""
        return self._pref['General'][option]

    def get_key(self, action, return_str=False):
        """Return the key corresponding to `action`
           Args:
                return_str(bool): Always return a human-readable string, instead of
                    int(returned if key is something like `insert`, `esc`, `end`, etc)
        """
        key = self._pref['Keybindings'][action]
        if const.VALID_KEY_CHARS.fullmatch(key) or return_str:
            return key
        else:
            # key is something like space, tab, insert
            return const.VALID_KEYS_EXTRA[key]

    def get_section_names(self):
        """Return(list) names of sections in pref"""
        return self._pref.sections.copy()

    def get_values_to_display(self):
        """Return a list of strings which will be used to display the settings
           in the editing window
        """
        disp_list = []
        for section, prefs in self._pref.items():
            disp_list.append(' ')
            disp_list.extend([section, len(section) * '-'])   # * '-' for underlining
            # number of characters after which value of an option is displayed
            max_length = len(max(prefs.keys(), key=len)) + 3  # +3 is just to beautify

            for option, value in prefs.items():
                # number of spaces to add so that all options are aligned correctly
                spaces = (max_length - len(option)) * ' '
                disp_list.append(option + spaces + value)
        return disp_list

    def parse_info_for_status(self, str_needing_info):
        """Return a short description of `str_needing_info`
           Note:
                `str_needing_info` will be a preference like `vim_mode   true`, as
                displayed in the preference window
        """
        pref = str_needing_info.split(maxsplit=1)[0]   # get only the pref, not value
        return self.pref_help[pref]

    def is_option_enabled(self, option):
        """Check whether `option` is set to 'true' or 'false',
           in preferences.
           Args:
                option(str): option to be checked, like vim_mode
           Returns:
                bool: True if enabled, False otherwise
        """
        return True if self.get_pref(option) == 'true' else False

    @util.change_pref(section='General')
    def set_pref(self, option, new_value):
        """Change a setting.
           Args:
                option(str): Setting that is to be changed
                new_value(str): New value of the setting
        """
        validators.validate(option, new_value)
        self._pref['General'][option] = new_value
        self.when_changed.run_hook(option)   # changes take effect

    @util.change_pref(section='Keybindings')
    def set_key(self, action, key):
        """Change a keybinding.
           Args:
                action(str): Action that is to be changed.
                key(str): New keybinding
        """
        if not self.get_key(action, return_str=True) == key:
            validators.validate_key(
                key=key, already_used_keys=self._pref['Keybindings'].values()
                )
            self._pref['Keybindings'][action] = key
            self.when_changed.run_hook('keybinding')


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

    def keybinding(self):
        """Run when keybindings are changed"""
        self.app.getForm("MAIN").load_keys()
        self.app.getForm("SETTINGS").load_keys()
