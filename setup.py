#!/usr/bin/env python3

import os
import sys
from setuptools import setup
from setuptools.command.install import install

from clid import version

if sys.version_info[0] != 3:
    sys.exit('clid requires Python3')

HOME = os.path.expanduser('~')
HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(HOME, '.config/clid')
USER_CONFIG_FILE = os.path.join(CONFIG_DIR, 'clid.ini')

LONG_DES = """
Clid is a command line app written in Python3 to manage your mp3 files' ID3 tags.
Unlike other tools, clid provides a graphical interface in the terminal to edit
tags, much like the way `cmus <https://github.com/cmus/cmus>`_ does for playing
mp3 files in the terminal.

See the `HOMEpage <https://github.com/GokulSoumya/clid>`_ for more details.
"""


def set_up_pref_file():
    """Update or create a config file"""
    import configobj
    try:
        os.makedirs(CONFIG_DIR)
    except FileExistsError:
        pass

    # get the ini file with default settings
    default_config = configobj.ConfigObj(os.path.join(HERE, 'clid/config.ini'))
    try:
        # get user's config file if app is already installed
        user_config = configobj.ConfigObj(USER_CONFIG_FILE, file_error=True)
    except OSError:
        # expand `~/Music` if app is being installed for the first time
        user_config = configobj.ConfigObj(USER_CONFIG_FILE)
        default_config['General']['music_dir'] = os.path.join(HOME, 'Music', '')

    default_config.merge(user_config)
    default_config.write(outfile=open(USER_CONFIG_FILE, 'wb'))


def make_whats_new():
    with open(os.path.join(HERE, 'clid/NEW.txt'), 'r') as file:
        to_write = file.read()
    with open(os.path.join(CONFIG_DIR, 'NEW'), 'w') as file:
        file.write(to_write)


class PostInstall(install):
    def run(self):
        set_up_pref_file()
        make_whats_new()
        with open(os.path.join(CONFIG_DIR, 'first'), 'w') as file:
            # used to display What's New popup(if true)
            file.write('true')

        install.run(self)


setup(
    name='clid',
    version=version.VERSION,
    license='MIT',

    packages=['clid', 'clid.base', 'clid.database', 'clid.forms'],

    description='Command line app based on ncurses to edit ID3 tags of mp3 files',
    long_description=LONG_DES,

    keywords='mp3 id3 command-line ncurses',
    classifiers=[
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Editors',
        'Topic :: Multimedia :: Sound/Audio :: Players :: MP3',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Environment :: Console :: Curses',
        'Intended Audience :: End Users/Desktop',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3 :: Only',
    ],

    author='Gokul',
    author_email='gokulps15@gmail.com',

    url='https://github.com/GokulSoumya/clid',

    # See https://PyPI.python.org/PyPI?%3Aaction=list_classifiers
    # See http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # See cheat in github

    install_requires=['npyscreen', 'stagger', 'configobj'],

    cmdclass={
        'install': PostInstall
    },
    entry_points={
        'console_scripts': [
            'clid = clid.__main__:run'
        ]
    }
)
