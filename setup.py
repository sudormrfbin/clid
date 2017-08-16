#!/usr/bin/env python3

import os
import sys
from setuptools import setup
from setuptools.command.install import install

from clid import main

if sys.version_info[0] != 3:
    sys.exit('clid requires Python3')

home = os.path.expanduser('~')
here = os.path.dirname(os.path.abspath(__file__))

long_des = """Clid is a command line app written in Python3 to manage your mp3 files' ID3 tags.
Unlike other tools, clid provides a graphical interface in the terminal to edit
tags, much like the way `cmus <https://github.com/cmus/cmus>`_ does for playing
mp3 files in the terminal.

See the `homepage <https://github.com/GokulSoumya/clid>`_ for more details.
"""

class PostInstall(install):
    def run(self):
        import configobj

        default = configobj.ConfigObj(here + '/clid/config.ini')   # get the ini file with default settings
        try:
            # get user's config file if app is already installed
            user = configobj.ConfigObj(home + '/.clid.ini', file_error=True)
        except OSError:
            # expand `~/Music` if app is being installed for the first time
            user = configobj.ConfigObj(home + '/.clid.ini')
            user['music_dir'] = home + '/Music/'

        default.update(user)   # save user's settings and add new settings options
        default.write(outfile=open(home + '/.clid.ini', 'wb'))   # will raise error if outfile is filename

        install.run(self)


setup(
    name='clid',
    version=main.__version__,
    license='MIT',

    packages=['clid'],

    description='Command line app based on ncurses to edit ID3 tags of mp3 files',
    long_description = long_des,

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
