#!/usr/bin/env python3

import os
from setuptools import setup
from setuptools.command.install import install

import configobj

from clid import main

home = os.path.expanduser('~')
here = os.path.dirname(os.path.abspath(__file__))

class PostInstall(install):
    def run(self):
        with open(home + '/.clid.ini', 'w') as new:   # make an ini file: ~/.clid.ini
            old = open(here + '/clid/config.ini', 'r').read()
            new.write(old)

        config = configobj.ConfigObj(home + '/.clid.ini')   # set the default music dir as ~/Music
        config['music_dir'] = home + '/Music/'
        config.write()

        install.run(self)


setup(
    name='clid',
    version=main.__version__,

    packages=['clid'],

    description='Command line app to edit ID3 tags of mp3 files',
    keywords='mp3 id3 command-line ncurses',

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
