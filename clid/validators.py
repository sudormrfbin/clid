#!/usr/bin/env python3

"""Contains validating functions used to check whether valid values
   are given when changing preferencs. ValidationError is raised
   if value to be tested doesn't pass the test.
"""

import os

from . import _const

class ValidationError(Exception):
    """Raised when validation fails"""
    pass


def true_or_false(test):
    """Checks whether test is either 'true' or 'false'
       Used by other functions.
    """
    if not(test == 'true' or test == 'false'):
        raise ValidationError('Acceptable values are "true" or "false"("' + test +  '" is not valid)')


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


def preview_format(test):
    """Checks whether is a valid which can be used as a preview format
       Args:
            test(str): str to be tested
       Raises:
       ValidationError
    """
    valid_specs_list = _const.FORMAT.keys()
    specs_list = _const.FORMAT_PAT.findall(test)

    for spec in specs_list:
        if spec not in valid_specs_list:
            raise ValidationError('"' + spec + '"' + ' is not a valid format specifier')


VALIDATORS = {
    'music_dir': music_dir,
    'vim_mode': true_or_false,
    'smooth_scroll': true_or_false,
    'preview_format': preview_format
}
