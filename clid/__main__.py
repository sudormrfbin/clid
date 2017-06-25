#!/usr/bin/env python3

"""Clid is an app to edit the id3v2 tags of mp3 files from the command line."""

from . import main

def run():
    main.ClidApp().run()

if __name__ == '__main__':
    run()
