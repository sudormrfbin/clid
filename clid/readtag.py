#!/usr/bin/env python3

"""Modified version of stagger to be used by clid"""

import stagger

from . import util


def getter_and_setter_for_tag(tag_field):
    """Used to construct appropriate getters and setters for attributes like
        artist, album, etc in `ReadTags` class.
        Args:
            tag_field(str): tag field for which getters and setters are
                made. It will later be an attribute of the class.
        Returns:
            tuple: tuple of (getter, setter)
    """
    def getter(self):
        return getattr(self.meta, tag_field)

    def setter(self, value):
        setattr(self.meta, tag_field, value)

    return (getter, setter)


class ReadTags():
    """Read tags from a file. This is a wrapper around stagger's
       default behaviour to make it easy to write code.
    """
    def __init__(self, filename):
        try:
            self.meta = stagger.read_tag(filename)
        except stagger.NoTagError:
            self.meta = stagger.Tag23()   # create an ID3v2.3 instance
        self.write = self.meta.write   # for saving to file

    date = property(*getter_and_setter_for_tag('date'))
    album = property(*getter_and_setter_for_tag('album'))
    title = property(*getter_and_setter_for_tag('title'))
    artist = property(*getter_and_setter_for_tag('artist'))
    comment = property(*getter_and_setter_for_tag('comment'))
    album_artist = property(*getter_and_setter_for_tag('album_artist'))

    @property
    def genre(self):
        """Genre tag; modified so that correct(readable) genre is returned
           instead of numerical gene
        """
        return util.resolve_genre(self.meta.genre)

    @genre.setter
    def genre(self, value):
        self.meta.genre = value

    @property
    def track(self):
        """Track number. Modified so that a string is returned. If
           track number is not set (self.meta.track will be 0), ''
           is returned
        """
        return '' if self.meta.track == 0 else str(self.meta.track)

    @track.setter
    def track(self, value):
        """We want the track number to be deleted, if value is ''. For this,
           self.meta.track has to be '0'.
        """
        value = '0' if value == '' else value
        self.meta.track = value
