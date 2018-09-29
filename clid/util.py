
"""
clid.util
~~~~~~~~~

Utilities for clid.
"""

from os import path

_HERE = path.dirname(__file__)
DATA_DIR = path.join(_HERE, 'data')
DEFAULT_CONFIG = path.join(DATA_DIR, 'config.yaml')
