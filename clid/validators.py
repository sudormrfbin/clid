#!/usr/bin/env python3

"""Contains validating functions used to check whether valid values
   are given when changing preferencs. ValidationError is raised
   if value to be tested doesn't pass the test.
"""

import os

class ValidationError(Exception):
    """Raised when validation fails"""
    pass

def music_dir(test):
    """Checks whether `test` exists and is a directory.

       Args:
            test(str): path to be tested.

       Raises:
            ValidationError: if `test` doesn't exist or is not directory
    """
    if not os.path.isdir(test):
        raise ValidationError('"' + test + '"' + ' is not a directory')
    if not os.path.exists(test):
        raise ValidationError('"' + test + '"' + ' doesn\'t exist')


VALIDATORS = {
    'music_dir': music_dir
}
