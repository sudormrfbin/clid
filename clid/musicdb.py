#!/usr/bin/env python3

"""
clid.musicdb
~~~~~~~~~~~~

For managing music files.
"""

import os
import sys
import itertools
import collections

from fuzzyfinder.main import fuzzyfinder

from clid.exceptions import ClidUserError

# walk implemented using `scandir is faster than the one implemented with
# `listdir`. From python3.5 onwards os.walk uses `scandir`
if sys.version_info >= (3, 5):
    from os import walk
else:
    from scandir import walk


class MusicDataBase:
    """
    Manages music files.

    Attributes:
        music_dir(str or None): Path to base directory with audio files.
        _music_files(dict):
            Mapping with filetype as key and list of files as value, like
            {'mp3': ['a/b/c.mp3'], 'ogg': ['e/f/g.ogg']}
    """

    def __init__(self, music_dir=None):
        self.set_music_dir(music_dir=music_dir)

    def set_music_dir(self, music_dir):
        """
        Set `music_dir` attribute and scan the directory for audio files
        """
        try:
            music_dir = os.path.expanduser(music_dir)
            if not os.path.isdir(music_dir):
                raise ClidUserError(
                    "{} is not a valid directory path".format(music_dir)
                )
            self.music_dir = music_dir
        except (AttributeError, TypeError):  # music_dir -> None
            self.music_dir = None
            self._music_files = None
            return None

        def find_files(ext):
            """
            Find audio files with extension `ext` in music_dir. Returns a list
            sorted lexicographically.
            """
            ext = "." + ext
            files_found = []
            for dirpath, __, files in walk(self.music_dir, followlinks=True):
                files_found.extend(
                    [
                        os.path.join(dirpath, audio)
                        for audio in files
                        if audio.endswith(ext)
                    ]
                )
            return self.sort(files=files_found, sortby="name")

        # NOTE: Paths are not canonical
        self._music_files = {"mp3": find_files("mp3"), "ogg": find_files("ogg")}

    def get_files(self, ext="all"):
        """
        Get files from the database.

        Args:
            ext (str):
                The type of files to retrieve filtered by extension. If value
                is "all", return every file.

        Returns:
            list: List of absolute filenames.
        """
        if ext == "all":
            return list(itertools.chain(*self._music_files.values()))  # merge all lists
        return self._music_files[ext].copy()

    @staticmethod
    def splitext(path):
        """
        Similar to os.path.splitext, but instead returns a `namedtuple`.

        Args:
            path (str): Path to be splitted.

        Returns:
            collections.namedtuple:
                A `Path` namedtuple, with a `filename` and `ext` attribute.

        Note:
            the `ext` attribute is stripped of the dot which seperates the
            filename and extension.
        """
        namedtuple = collections.namedtuple("Path", ["filename", "ext"])

        name, ext = os.path.splitext(os.path.basename(path))
        ext = ext[1:]  # remove the dot from the extension
        return namedtuple(filename=name, ext=ext)

    def get_basename(self, path):
        """
        Get the filename only, without extension.
        """
        return self.splitext(path).filename

    def filename_search(self, text, ignore_case, fuzzy_search, ext="all"):
        """
        Search filenames for a match with the search text.

        Args:
            text (str): Text to search for.
            ignore_case (bool):
                Whether to consider case. This parameter is ignored if
                the fuzzy_search parameter is True.
            fuzzy_search (bool): Whether to use fuzzy searching.
            ext (str): Extensions to search for; 'mp3', 'ogg', etc.
        """
        files_to_search = self.get_files(ext=ext)

        if text == "":
            return files_to_search

        if fuzzy_search:
            return list(fuzzyfinder(text, files_to_search, accessor=self.get_basename))

        if ignore_case:
            text = text.lower()
            return [
                file
                for file in files_to_search
                if text in self.get_basename(file).lower()
            ]
        else:
            return [file for file in files_to_search if text in self.get_basename(file)]

    def sort(self, files, sortby=None, reverse=False):
        """
        Sort `files` by a condition.

        Args:
            files (list of str): Paths to be sorted.
            sortby (str):
                Condition to sort the paths. Possible value:
                "ext": By extension.
                "name": By the filename (by basename, not full path).
                "mod_time": By last modified time.
            reverse (bool): Whether to reverse the sorted list.

        Returns:
            list: The sorted list of paths.
        """
        if sortby is None:
            return files
        elif sortby == "ext":
            # lambda function returns a tuple - (extension, filename)
            return sorted(files, key=lambda x: self.splitext(x)[::-1], reverse=reverse)
        elif sortby == "name":
            return sorted(files, key=self.splitext, reverse=reverse)
        elif sortby == "mod_time":
            # sort by last modification time
            keyf = lambda x: os.stat(x).st_mtime
            # Time is returned as seconds since the Epoch, so the file that was
            # modified last would have the greatest value
            return sorted(files, key=keyf, reverse=(not reverse))
        else:
            raise ClidUserError(
                "{sortby} is not a valid sort parameter".format(sortby=sortby)
            )
