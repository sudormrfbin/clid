"""Test databases in clid"""

import os

import clid.database.musicdb


HERE = os.path.dirname(__file__)

class TestMusicDB:
    db = clid.database.musicdb.MusicDataBase()

    def get_mp3_files_list_from_txt_file(self):
        """Return names of mp3 files stored in mp3_files.txt in a list"""
        with open(os.path.join(HERE, 'mp3_files.txt')) as f:
            return sorted([name.replace('\n', '') for name in f.readlines()])

    def test_set_music_dir(self):
        self.db.set_music_dir(os.path.join(HERE, 'samples'))
        mp3_files = self.get_mp3_files_list_from_txt_file()
        assert mp3_files == sorted(self.db._music_files['mp3'])

    # TODO: add ogg files
    def test_get_files(self):
        assert sorted(self.db.get_files(ext='all')) == \
                self.get_mp3_files_list_from_txt_file()

    def test_file_path_are_absolute(self):
        assert [f for f in self.db.get_files('mp3') if os.path.isabs(f)]
