"""Test databases in clid"""

import os

import pytest

import clid.database
from clid.errors import ClidUserError


HERE = os.path.dirname(__file__)

@pytest.fixture
def mp3_files():
    mp3 = []
    for dirpath, __, files in os.walk(HERE):
        mp3.extend([os.path.join(dirpath, f) for f in files if f.endswith('.mp3')])
    return sorted(mp3)


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

    def test_raise_error_if_invalid_music_dir(self):
        with pytest.raises(ClidUserError):
            clid.database.MusicDataBase('/how/ya/doin ?!')

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
        expected = f_musicdb.get_files(ext='all')
        assert expected == f_musicdb.filename_search(text='', ignore_case=True, fuzzy_search=False)
        assert expected == f_musicdb.filename_search(text='', ignore_case=False, fuzzy_search=False)
        assert expected == f_musicdb.filename_search(text='', ignore_case=False, fuzzy_search=True)

    def test_simple_filename_search_ign_case(self, f_musicdb):
        results = f_musicdb.filename_search(text='fri', ignore_case=True, fuzzy_search=False)
        expected = [
            'a/b/d/FRIENDS.mp3',
            'a/b/fRiEnDs.ogg',
            'a/b/c/friends.mp3',
            'a/b/c/friends.ogg',
        ]
        assert sorted(results) == sorted(expected)

    def test_simple_filename_search_no_ign_case(self, f_musicdb):
        results = f_musicdb.filename_search(text='FRI', ignore_case=False, fuzzy_search=False)
        expected = ['a/b/d/FRIENDS.mp3',]
        assert results == expected

    def test_simple_filename_search_fuzzy(self, f_musicdb):
        results = f_musicdb.filename_search(text='fri', ignore_case=False, fuzzy_search=True)
        expected = [
            'a/b/d/FRIENDS.mp3',
            'a/b/fRiEnDs.ogg',
            'a/b/c/friends.mp3',
            'a/b/c/friends.ogg',
            'a/b/F.R.I.E.N.D.S.mp3',
        ]
        assert results == expected
