#!/usr/bin/env python3

"""Contains MusicDataBase, the class which manages music files"""


import os
import fnmatch
import itertools
import collections

class MusicDataBase:
    """Manages music files
       Attributes:
            music_dir: Path to base directory with audio files
            _music_files(dict):
                Mapping with filetype as key and list of files as value
                _music_files -> {'mp3': ['a/b/c.mp3'], 'ogg': ['e/f/g.ogg']}
    """
    def __init__(self, music_dir=None):
        self.set_music_dir(music_dir=music_dir)

    def set_music_dir(self, music_dir):
        """Set `music_dir` attr and scan the dir for audio files"""
        try:
            self.music_dir = os.path.expanduser(music_dir)
        except AttributeError:   # music_dir -> None
            self.music_dir = None
            self._music_files = None
            return None

        def find_files(ext):
            """Find audio files with extension `ext` in music_dir. Returns a list
               sorted lexicographically
            """
            pattern = '*.{ext}'.format(ext=ext)   # make glob pattern to use with fnmatch
            files_found = []
            for dirpath, __, files in os.walk(self.music_dir, followlinks=True):
                files_here = fnmatch.filter(names=files, pat=pattern)
                files_found.extend([os.path.join(dirpath, file) for file in files_here])
            return sorted(files_found, key=self.get_basename)

        # NOTE: Paths are not canonical
        self._music_files = {
            'mp3': find_files('mp3'),
            'ogg': find_files('ogg'),
        }

    def get_files(self, ext='all'):
        """Return filenames with extension `ext`. If ext is 'all', return
           every file
        """
        if ext == 'all':
            return list(itertools.chain(*self._music_files.values()))   # merge all lists
        return self._music_files[ext].copy()

    def get_basename(self, path):
        """Return only the filename, without extension"""
        return self.splitext(path).filename

    @staticmethod
    def splitext(path):
        """Return the namedtuple (filename, ext). This function is like
           os.path.splitext, except that it will return the basename and
           extension in a named tuple.
        """
        namedtuple = collections.namedtuple('Path', ['filename', 'ext'])

        name, ext = os.path.splitext(os.path.basename(path))
        ext = ext[1:]   # remove the dot from the extension
        return namedtuple(filename=name, ext=ext)

    def filename_search(self, text, ignore_case, fuzzy_search, ext='all'):
        """Search filenames which match the search text
           ignore_case -> bool: ignored if fuzzy_search is True
           fuzzy_search -> bool: whether to use fuzzy searching
           ext -> str: extensions to search for; 'mp3', 'ogg', etc
        """
        files_to_search = self.get_files(ext=ext)

        if text == '':
            return files_to_search

        if fuzzy_search:
            return list(fuzzyfinder(text, files_to_search, accessor=self.get_basename))

        if ignore_case:
            text = text.lower()
            return [file for file in files_to_search if text in self.get_basename(file).lower()]
        else:
            return [file for file in files_to_search if text in self.get_basename(file)]

