#!/usr/bin/env python3

"""Common utilities for clid"""

import npyscreen as npy

from . import const
from . import validators


def resolve_genre(num_gen):
    """Convert numerical genre values to readable values. Genre may be
        saved as a str of the format '(int)' by applications like EasyTag.
        Args:
            num_gen (str): str representing the genre.
        Returns:
            str: Name of the genre (Electronic, Blues, etc). Returns
            num_gen itself if it doesn't match the format.
    """
    match = const.GENRE_PAT.findall(num_gen)
    if match:
        try:
            return const.GENRES[int(match[0])]   # retrun the string form of genre
        except IndexError:
            # num_gen is in the form of a num gen, but the number is invalid
            return ''
    else:
        # it's probably a normal string
        return num_gen


def is_date_in_valid_format(date):
    """See if date string is in a format acceptable by stagger.
       Returns:
            bool: True if date is in valid format, False otherwise
    """
    match = const.DATE_PATTERN.match(date)
    if match is None or match.end() != len(date):
        return False
    return True


def is_track_number_valid(track):
    """Check if track number is a valid one. `track` must be '' or
       a number string.
    """
    return track.isnumeric() or track == ''


def get_lines_to_be_highlighted(sections):
    """Return a list of string that have to be highlighted in the
       pref window(section names)
    """
    return (sections + [len(sec) * '-' for sec in sections] + [' '])


def run_if_window_not_empty(update_status_line):
    """Decorator which accepts a handler as param and executes it
       only if the window is not empty(if there are files to display).
       Args:
            update_status_line(bool): Whether to update the status line
    """
    def wrap(handler):
        def handler_wrapper(self, char):
            if self.values:
                handler(self, char)
                if update_status_line:
                    self.set_current_status()
        return handler_wrapper
    return wrap


def change_pref(section):
    """Decorator for changing preferences.
       Args:
            section(str): Section to which a preference will belong to(Eg; General)
    """
    def wrap(func):
        def wrapper_func(self, option, value):
            if option in self._pref[section]:
                try:
                    func(self, option, value)
                    self._pref.write()   # save to file
                except validators.ValidationError as err:
                    # invalid value for specified option
                    npy.notify_confirm(message=str(err), title='Error', editw=True)
            else:
                # invalid option(not in preferences)
                npy.notify_confirm(
                    '"{}" is an invalid option'.format(option), title='Error', editw=True
                    )
        return wrapper_func
    return wrap

