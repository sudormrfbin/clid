#!/usr/bin/env python3

import os

import configobj
import npyscreen as npy

SETTINGS = configobj.ConfigObj(os.path.dirname(__file__) + '/config.ini')

class PrefMultiline(npy.MultiLine):
    def set_up_handlers(self):
        super().set_up_handlers()
        self.handlers['1'] = self.switch_to_main

    def switch_to_main(self, char):
        self.parent.parentApp.switchForm("MAIN")


class PreferencesView(npy.FormMuttActiveTraditional):
    """View for editing preferences/settings"""
    MAIN_WIDGET_CLASS = PrefMultiline
