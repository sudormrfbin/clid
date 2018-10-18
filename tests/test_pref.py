
"""
Test clid.pref
"""

from os import path

from clid.pref import Preferences

USER_CONFIG = path.join(path.dirname(__file__), "data", "user_config.yaml")
DEFAULT_CONFIG = path.join(path.dirname(__file__), "data", "default_config.yaml")


def test_create_config_file_new_is_created(tmpdir):
    user_conf = tmpdir.join("new_user_conf.yaml")
    Preferences(user_config=str(user_conf), default_config=DEFAULT_CONFIG)
    with open(DEFAULT_CONFIG) as d, open(user_conf) as u:
        assert d.read() == u.read()


def test_pref_get():
    config = Preferences(user_config=USER_CONFIG, default_config=DEFAULT_CONFIG)
    assert config.get('general.global.mouse') == False
    assert config.get('general.main_menu.title') == 'clid'
    assert config.get('keys.win_up') == 'k'
    assert config.get('keys.win_down') == 'down'
