#!/usr/bin/env python3

"""Modified version of stagger to be used by clid"""

import stagger

            # return '' if ret == 0 else str(ret) -> getter
            # value = '0' if value == '' else value -> setter

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


class ReadTags(object):
    """Read tags from a file. This is a wrapper around stagger's
       default behaviour to make it easy to write code.
    """
    def __init__(self, filename):
        self.meta = stagger.read_tag(filename)

    artist = property(*getter_and_setter_for_tag('artist'))
    album = property(*getter_and_setter_for_tag('album'))
    comment = property(*getter_and_setter_for_tag('comment'))
    album_artist = property(*getter_and_setter_for_tag('album_artist'))
    title = property(*getter_and_setter_for_tag('title'))

    @property
    def genre(self):
        pass
