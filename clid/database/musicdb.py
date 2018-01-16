#!/usr/bin/env python3

"""Contains MusicDataBase, the class which manages music files"""


import os
import fnmatch

class MusicDataBase:
    """Manages music files
       Attributes:
            music_dir: Path to base directory with audio files
            music_files(dict):
                Mapping with filetype as key and list of files as value
                music_files -> {'mp3': ['a/b/c.mp3'], 'ogg': ['e/f/g.ogg']}
    """
    def __init__(self, music_dir=None):
        self.set_music_dir(music_dir=music_dir)

    def set_music_dir(self, music_dir):
        """Set `music_dir` attr and scan the dir for audio files"""
        try:
            self.music_dir = os.path.expanduser(music_dir)
        except AttributeError:   # music_dir -> None
            self.music_dir = None
            return None

        def find_files(ext):
            """Find audio files with extension `ext` in music_dir. Returns a list."""
            pattern = '*.{ext}'.format(ext=ext)   # make glob pattern to use with fnmatch
            files_found = []
            for dirpath, __, files in os.walk(self.music_dir, followlinks=True):
                files_here = fnmatch.filter(names=files, pat=pattern)
                files_found.extend([os.path.join(dirpath, file) for file in files_here])
            return files_found

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
            return sum(self._music_files.values(), [])   # merge all lists
        return self._music_files[ext].copy()
