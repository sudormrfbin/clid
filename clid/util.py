#!/usr/bin/env python3

"""Common utilities for clid"""

import configobj

from . import const

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
            return const.GENRES[int(match[0])]
        except IndexError:
            return ''
    else:
        return num_gen

def run_if_window_not_empty(handler):
    """Decorator which accepts a handler as param and executes it
       only if the window is not empty(if there are files to display).
    """
    def wrapper(self, char):
        if self.values:
            handler(self, char)
    return wrapper

def status_update_wrapper(handler):
    """Decorator which runs key handler only if window is not empty. Also,
       the status line is updated.
    """
    def wrapper(self, char):
        if self.values:
            handler(self, char)
            self.set_current_status()
    return wrapper

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
