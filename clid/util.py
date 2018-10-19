"""
clid.util
~~~~~~~~~

Utilities for clid.
"""

from os import path

import confuse

_HERE = path.dirname(__file__)
CLID_DATA_DIR = path.join(_HERE, "data")
DEFAULT_CONFIG = path.join(CLID_DATA_DIR, "config.yaml")

USER_DATA_DIR = path.join(confuse.config_dirs()[0], "clid")
USER_CONFIG = path.join(USER_DATA_DIR, "config.yaml")
