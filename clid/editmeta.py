#!/usr/bin/env python3

"""Form class for editing the metadata of a track"""

import npyscreen as npy


class EditMeta(npy.Form):
    """Edit the metadata of a track"""
    def create(self):
        self.add(npy.TitleText, name='Title')
        self.add(npy.TitleText, name='Album')
        self.add(npy.TitleText, name='Artist')
        self.add(npy.TitleText, name='Album Artist')

        self.nextrely += 1
        self.add(npy.TitleText, name='Genre')
        self.add(npy.TitleText, name='Track Number')
        