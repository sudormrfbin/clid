"""Test databases in clid"""

import os

import pytest

import clid.database


HERE = os.path.dirname(__file__)

@pytest.fixture
def mp3_files():
    with open(os.path.join(HERE, 'mp3_files.txt')) as f:
        return sorted(f.read().splitlines())


class TestMusicDB:

    @pytest.fixture(scope='session')
    def musicdb(self):
        return clid.database.MusicDataBase()

    @pytest.fixture
    def f_musicdb(self):
        db = clid.database.MusicDataBase()
        db._music_files = {
            'mp3': [
                'a/b/F.R.I.E.N.D.S.mp3',
                'a/b/d/FRIENDS.mp3',
                'a/b/c/friends.mp3',
            ],
            'ogg': [
                'a/b/fRiEnDs.ogg',
                'a/b/c/friends.ogg',
            ]
        }
        return db

    def test_set_music_dir(self, musicdb, mp3_files):
        musicdb.set_music_dir(os.path.join(HERE, 'samples'))
        assert mp3_files == sorted(musicdb._music_files['mp3'])

    # TODO: add ogg files
    def test_get_files(self, musicdb, mp3_files):
        assert mp3_files == sorted(musicdb.get_files(ext='all'))

    def test_file_path_are_absolute(self, musicdb):
        # assert [f for f in self.db.get_files('mp3') if os.path.isabs(f)]
        assert all([True if os.path.isabs(f) else False for f in musicdb.get_files('mp3')])

    def test_splitext(self, musicdb):
        results = musicdb.splitext("/a/b/How you doin' ?.mp3")
        assert isinstance(results, tuple)   # named tuple, actually
        assert results.filename == "How you doin' ?"
        assert results.ext == 'mp3'

    def test_get_basename(self, musicdb):
        assert musicdb.get_basename('/a/b/I know!.mp3') == 'I know!'

    def test_simple_filename_search_empty_str(self, f_musicdb):

    def test_file_path_are_absolute(self):
        assert [f for f in self.db.get_files('mp3') if os.path.isabs(f)]
