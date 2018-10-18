
"""
clid.pref
~~~~~~~~~

Read and set preferences.
"""

import os
import shutil

import confuse

from . import util


class _ConfuseConfig(confuse.Configuration):
    """
    A custom Configuration object to be used by `Preferences`. This is *not*
    the object used for fetching preferences by the app.
    """

    def __init__(self, appname, config, default):
        self.config = config  # absolute path to user config
        self.default_config = default  # absolute path to default config file
        super().__init__(appname)

    def user_config_path(self):
        return self.config

    def _add_default_source(self):
        filename = self.default_config
        self.add(confuse.ConfigSource(confuse.load_yaml(filename), filename, True))


class Preferences:
    """
    Class for managing preferences.
    """

    def __init__(
        self, user_config=util.USER_CONFIG, default_config=util.DEFAULT_CONFIG
    ):
        """
        Args:
            user_config (str): Path to user config file.
            default_config (str): Path to default config file.
        """
        if not os.path.exists(user_config):
            self.create_config_file(path=user_config, default=default_config)
        self._config = _ConfuseConfig(
            appname="clid", config=user_config, default=default_config
        )

    @staticmethod
    def create_config_file(path=util.USER_CONFIG, default=util.DEFAULT_CONFIG):
        """
        Create a config file with default settings. Overwrites existing config file.
        Args:
            path (str): Path to file to be created.
            default (str):
                Path to the default config file to be used to create new config.
        """
        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        shutil.copy(default, path)

    def get(self, opt):
        """
        Return the value of the `opt` option.
        Args:
            opt (str): Name of option, like "general.mouse_support", etc.
        """
        val = self._config
        for key in opt.split("."):
            val = val[key]
        return val.get()
        # get method is used to resolve the value of an option from multiple config files
