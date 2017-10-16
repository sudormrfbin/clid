#!/usr/bin/env python3

"""Main View/Window of clid"""

import curses

import npyscreen as npy

from . import base
from . import util
from . import const


__version__ = '0.7.0'


class MainActionController(base.ClidActionController):
    """Object that recieves recieves inpout in command line
       at the bottom.
       Note:
            self.parent refers to MainView -> class
    """
    def create(self):
        super().create()
        self.add_action('^/.+', self.search_for_files, live=True)   # search with '/'

    def search_for_files(self, command_line, widget_proxy, live):
        """Search for files while given a string"""
        # if len(command_line[1:]) > 2:
        #     self.parent.value.set_filter(command_line[1:])
        # else:   # search only if at least 3 charecters are given
        #     self.parent.value.set_filter(None)

        # self.parent.after_search_now_filter_view = True
        # self.parent.wMain.values = self.parent.value.get()
        # self.parent.display()
        # if self.parent.wMain.values:
        #     self.parent.wMain.set_current_status()
        # else:   # search didn't match
        #     self.parent.wStatus2.value = ' '
        #     self.parent.display()

        search = command_line[1:]   # first char will be '/' in command_line
        self.parent.wMain.values = self.parent.mp3db.get_filtered_values(search)
        if self.parent.wMain.values:
            self.parent.wMain.set_current_status()  # tag preview if a match is found
        else:
            self.parent.wStatus2.value = ' '   # show nothing if no files matched
        self.parent.after_search_now_filter_view = True
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
                Stores list of files which was selected for batch tagging
            _relative_index_of_space_selected_values(list):
                (property) List of indexes of space selected files *compared to
                self.parent.wMain.values*
       Note:
            self.parent refers to MainView -> class
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_filtering = False   # does NOT refer to search invoked with '/'
        self.space_selected_values = []

        self.slow_scroll = self.parent.prefdb.is_option_enabled('smooth_scroll')

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

    @util.run_if_window_not_empty
    def h_cursor_beginning(self, char):
        super().h_cursor_beginning(char)

    @util.run_if_window_not_empty
    def h_cursor_end(self, char):
        super().h_cursor_end(char)

    @property
    def _relative_index_of_space_selected_values(self):
        return [self.values.index(file) for file in self.space_selected_values
                if file in self.values]

    def set_current_status(self, *args, **kwargs):
        """Show metadata(preview) of file under cursor in the status line"""
        data = self.parent.mp3db.parse_info_for_status(
            filename=self.get_selected(), *args, **kwargs
            )
        self.parent.wStatus2.value = data
        self.parent.display()

    def get_selected(self):
        """Return the name of file under the cursor line"""
        with open('sdf', 'w') as f: f.write('{0}\n{1}'.format(len(self.values)-1, self.cursor_line))
        return self.values[self.cursor_line]

    def h_reload_files(self, char):
        """Reload files in `music_dir`"""
        self.parent.mp3db.load_mp3_files_from_music_dir()
        self.parent.load_files_to_show()

    # TODO: make it faster
    def h_revert_escape(self, char):
        """Handler which switches from the filtered view of search results
           to the normal view with the complete list of files, if search results
           are being displayed. If all files are being shown, empty
           `space_selected_values` to clear multi file selection
        """
        if self.parent.after_search_now_filter_view:
            self.values = self.parent.mp3db.get_values_to_display()   # revert
            self.parent.after_search_now_filter_view = False
            self.set_current_status()
        elif self.space_selected_values:   # if files have been selected with space
            self.space_selected_values = []
        self.display()

    def h_switch_to_settings(self, char):
        """Switch to Preferences View"""
        self.parent.parentApp.switchForm("SETTINGS")

    @util.run_if_window_not_empty
    def h_select(self, char):
        # TODO: Rewrite this whole function
        app = self.parent.parentApp
        file_dict = self.parent.mp3db.file_dict
        file_under_cursor = self.get_selected()
        # batch tagging window if multiple files are selected
        if self.space_selected_values:
            if file_under_cursor not in self.space_selected_values:
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
        """Add or remove current line from list of lines to be highlighted
           (for batch tagging) when <Space> is pressed.
        """
        current = self.get_selected()
        if current in self.space_selected_values:
            self.space_selected_values.remove(current)
        else:
            self.space_selected_values.append(current)

    # HACK: Following two funcions are actually used by npyscreen to display filtered
    #       values based on a search string, by highlighting the results. This is a
    #       hack that makes npyscreen highlight files that have been selected with
    #       <Space>, instead of highlighting search results

    def filter_value(self, index):
        return self._filter in self.display_value(self.values[index]).lower

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
       Attributes:
            after_search_now_filter_view(bool):
                Used to revert screen(ESC) to standard view after a search
                (see class MainMultiLine)
            mp3db: Reference to mp3db(see __main__.ClidApp)
            prefdb: Reference to prefdb(see __main__.ClidApp)
       Note:
            self.value refers to an instance of DATA_CONTROLER
    """
    MAIN_WIDGET_CLASS = MainMultiLine
    ACTION_CONTROLLER = MainActionController
    COMMAND_WIDGET_CLASS = base.ClidCommandLine

    def __init__(self, parentApp, *args, **kwargs):
        self.parentApp = parentApp
        self.mp3db = self.parentApp.mp3db
        self.prefdb = self.parentApp.prefdb
        super().__init__(*args, **kwargs)
        self.after_search_now_filter_view = False

        self.load_files_to_show()

        # widgets are created by self.create() in super()
        self.wStatus1.value = 'clid v' + __version__ + ' '

        # display tag preview of first file
        try:
            self.wStatus2.value = self.mp3db.parse_info_for_status(self.wMain.values[0])
        except IndexError:   # thrown if directory doest not have mp3 files
            self.wStatus2.value = 'No Files Found In Directory '

        with open(const.CONFIG_DIR + 'first', 'r') as file:
            first = file.read()

        if first == 'true':
            # if app is run after an update, display a what's new message
            with open(const.CONFIG_DIR + 'NEW') as new:
                disp = new.read()
            npy.notify_confirm(message=disp, title="What's New", editw=1, wide=True)
            with open(const.CONFIG_DIR + 'first', 'w') as file:
                file.write('false')

    def load_files_to_show(self):
        """Set the mp3 files that will be displayed"""
        self.wMain.values = self.mp3db.get_values_to_display()
