#!/usr/bin/env python3

"""Main View/Window of clid"""

__version__ = '0.7.0'

import curses

import npyscreen as npy

from . import base
from . import util
from . import const
from . import database


class MainActionController(base.ClidActionController):
    """Object that recieves recieves inpout in command line
       at the bottom.

       Note:
            self.parent refers to MainView -> class
            self.parent.value refers to database.Mp3DataBase -> class
    """
    def create(self):
        super().create()
        self.add_action('^/.+', self.search_for_files, live=True)   # search with '/'

    def search_for_files(self, command_line, widget_proxy, live):
        """Search for files while given a string"""
        if len(command_line[1:]) > 2:   # first char will be '/'
            self.parent.value.set_filter(command_line[1:])
        else:   # search only if at least 3 charecters are given
            self.parent.value.set_filter(None)

        self.parent.after_search_now_filter_view = True
        self.parent.wMain.values = self.parent.value.get()
        self.parent.display()
        if self.parent.wMain.values:
            self.parent.wMain.set_current_status()
        else:   # search didn't match
            self.parent.wStatus2.value = ' '
            self.parent.display()


class MainMultiLine(npy.MultiLine):
    """MultiLine class to be used by clid. `Esc` has been modified to revert
       the screen back to the normal view after a searh has been performed
       (the search results will be shown; blank if no matches are found)
       or if files have been selected. If files are selected *and* search
       has been performed, selected files will be kept intact and search will
       be reverted

       Attributes:
            space_selected_values(list):
                Stores list of files which was selected for batch tagging using <Space>
            _relative_index_of_space_selected_values(list):
                (property) List of indexes of space selected files *in context with
                self.parent.wMain.values*

       Note:
            self.parent refers to MainView -> class
            self.parent.value refers to database.Mp3DataBase -> class
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_filtering = False   # does NOT refer to search invoked with '/'
        self.space_selected_values = []

        self.slow_scroll = util.is_option_enabled('smooth_scroll')

        self.handlers.update({
            'u':              self.h_reload_files,
            '2':              self.h_switch_to_settings,
            curses.ascii.SP:  self.h_multi_select,
            curses.ascii.ESC: self.h_revert_escape,
        })


    # Movement Handlers
    @util.run_if_window_not_empty
    def h_cursor_page_up(self, char):
        super().h_cursor_page_up(char)

    @util.run_if_window_not_empty
    def h_cursor_page_down(self, char):
        super().h_cursor_page_down(char)

    @util.run_if_window_not_empty
    def h_cursor_line_up(self, char):
        super().h_cursor_line_up(char)

    @util.run_if_window_not_empty
    def h_cursor_line_down(self, char):
        super().h_cursor_line_down(char)

    @property
    def _relative_index_of_space_selected_values(self):
        return [self.values.index(file) for file in self.space_selected_values\
                if file in self.values]

    def set_current_status(self, *args, **kwargs):
        """Show metadata(preview) of file under cursor in the status line"""
        data = self.parent.value.parse_meta_for_status(
            filename=self.get_selected(), *args, **kwargs)
        self.parent.wStatus2.value = data
        self.parent.display()

    def get_selected(self):
        """Return the name of file under the cursor line"""
        return self.values[self.cursor_line]

    def h_reload_files(self, char):
        """Reload files in `music_dir`"""
        self.parent.value.load_files_and_set_values()
        self.parent.load_files()

    def h_revert_escape(self, char):
        """Handler which switches from the filtered view of search results
           to the normal view with the complete list of files.
        """
        if self.parent.after_search_now_filter_view:   # if screen is showing search results
            self.values = self.parent.value.get_all_values()   # revert
            self.parent.after_search_now_filter_view = False
        elif len(self.space_selected_values):
            self.space_selected_values = []

            self.display()

# TODO: make it faster

    def filter_value(self, index):
        return self._filter in self.display_value(self.values[index]).lower   # ignore case

    def h_switch_to_settings(self, char):
        self.parent.parentApp.switchForm("SETTINGS")


    @util.run_if_window_not_empty
    def h_select(self, char):
        app = self.parent.parentApp
        file_dict = self.parent.value.file_dict
        file_under_cursor = self.get_selected()
        # batch tagging window if multiple files are selected
        if self.space_selected_values:
            if not file_under_cursor in self.space_selected_values:
                self.space_selected_values.append(file_under_cursor)
            # abs path of files
            app.current_files = [file_dict[file] for file in self.space_selected_values]
            self.space_selected_values = []
            app.switchForm("MULTIEDIT")
        else:
            self.parent.parentApp.current_files = [file_dict[file_under_cursor]]
            self.parent.parentApp.switchForm("SINGLEEDIT")

    @util.run_if_window_not_empty
    def h_multi_select(self, char):
        """Add or remove current line from list of lines
           to be highlighted, when <Space> is pressed.
        """
        current = self.get_selected()
        if current in self.space_selected_values:
            self.space_selected_values.remove(current)
        else:
            self.space_selected_values.append(current)

    def _set_line_highlighting(self, line, value_indexer):
        """Highlight files which were selected with <Space>"""
        if value_indexer in self._relative_index_of_space_selected_values:
            self.set_is_line_important(line, True)   # mark as important
        else:
            self.set_is_line_important(line, False)

        # without this line every file will get highlighted as we go down
        self.set_is_line_cursor(line, False)


class MainView(npy.FormMuttActiveTraditional):
    """The main app with the ui.

       Note:
            self.value refers to an instance of DATA_CONTROLER
    """
    DATA_CONTROLER = database.MainMp3DataBase
    MAIN_WIDGET_CLASS = MainMultiLine
    ACTION_CONTROLLER = MainActionController
    COMMAND_WIDGET_CLASS = base.ClidCommandLine

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_value(self.DATA_CONTROLER())
        self.value.settings = self.parentApp.settings
        self.value.load_files_and_set_values()
        self.value.load_preview_format()

        self.load_files()

        # widgets are created by self.create() in super()
        self.wStatus1.value = 'clid v' + __version__ + ' '

        try:
            self.wStatus2.value = self.value.parse_meta_for_status(self.wMain.values[0])
        except IndexError:   # thrown if directory doest not have mp3 files
            self.wStatus2.value = 'No Files Found In Directory '
            self.wMain.values = []

        self.after_search_now_filter_view = False
        # used to revert screen(ESC) to standard view after a search(see class MainMultiLine)

        with open(const.CONFIG_DIR + 'first', 'r') as file:
            first = file.read()

        if first == 'true':
            # if app is run for first time or after an update, display a what's new message
            with open(const.CONFIG_DIR + 'NEW') as new:
                display = new.read()
            npy.notify_confirm(message=display, title='What\'s New', editw=1, wide=True)
            with open(const.CONFIG_DIR + 'first', 'w') as file:
                file.write('false')


    def load_files(self):
        """Set the mp3 files that will be displayed"""
        self.wMain.values = self.value.get_all_values()
