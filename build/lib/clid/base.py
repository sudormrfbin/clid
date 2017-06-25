#!/usr/bin/env python3

"""Base classes to be used by clid"""

import npyscreen as npy

class ClidCommandLine(npy.ActionControllerSimple):
    """Base class for the command line at the bootom of the screen"""

    def create(self):
        self.add_action('^:q', self.exit_app, live=False)   # quit with ':q'

    def exit_app(self, command_line, widget_proxy, live):
        """Exit the app with ':q'"""
        exit()   # args are used internally by npyscreen

