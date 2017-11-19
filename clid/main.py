#!/usr/bin/env python3

"""Main View/Window of clid"""

import curses

import npyscreen as npy

from . import base
from . import util
from . import const
from . import version


class MainActionController(base.ClidActionController):
    """Object that recieves recieves inpout in command line
       at the bottom.
       Note:
            self.parent refers to MainView -> class
    """
    def create(self):
        super().create()
        self.add_action('^/', self.search_for_files, live=True)   # search with '/'

    def search_for_files(self, command_line, widget_proxy, live):
        search = command_line[1:]   # first char will be '/' in command_line
        self.parent.wMain.values = self.parent.mp3db.get_filtered_values(search)
        if self.parent.wMain.values:
            self.parent.wMain.cursor_line = 0
            self.parent.wMain.set_current_status()  # tag preview if a match is found
        else:
            self.parent.wStatus2.value = ' '   # show nothing if no files matched
        self.parent.after_search_now_filter_view = True
        self.parent.display()


class MainMultiLine(base.ClidMultiLine):
    """MultiLine class to be used by clid. `Esc` has been modified to revert
       the screen back to the normal view after a searh has been performed
       (the search results will be shown; blank if no matches are found)
       or if files have been selected. If files are selected *and* search
       has been performed, selected files will be kept intact and search will
       be reverted
       Attributes:
            space_selected_values(set):
                Stores set of files which was selected for batch tagging. A set is
                used as we don't want the same file to be added more than once
       Note:
            self.parent refers to MainView -> class
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.allow_filtering = False   # does NOT refer to search invoked with '/'
        self.space_selected_values = set()

        self.slow_scroll = self.parent.prefdb.is_option_enabled('smooth_scroll')

    def load_keys(self):
        get_key = self.parent.prefdb.get_key
        self.handlers.update({
            get_key('esc_key'):            self.h_revert_escape,
            get_key('select_item'):        self.h_multi_select,
            get_key('reload_music_dir'):   self.h_reload_files,
            get_key('invert_selection'):   self.h_invert_selection,
        })

    def get_relative_index_of_space_selected_values(self):
        """Return list of indexes of space selected files,
           *compared to self.parent.wMain.values*
        """
        return [self.values.index(file) for file in self.space_selected_values
                if file in self.values]

    # Handlers
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
            self.space_selected_values = set()
        self.display()

    @util.run_if_window_not_empty(update_status_line=False)
    def h_select(self, char):
        """Select a file using <Enter>(default)"""
        if self.space_selected_values:
            # add the file under cursor if it is not already in it
            self.space_selected_values.add(self.get_selected())
            self.parent.parentApp.set_current_files(self.space_selected_values)
            self.space_selected_values = set()
            self.parent.parentApp.switchForm("MULTIEDIT")
        else:
            self.parent.parentApp.set_current_files([self.get_selected()])
            self.parent.parentApp.switchForm("SINGLEEDIT")

    @util.run_if_window_not_empty(update_status_line=False)
    def h_multi_select(self, char):
        """Add or remove current line from list of lines to be highlighted
           (for batch tagging) when <Space> is pressed.
        """
        current = self.get_selected()
        try:
            self.space_selected_values.remove(current)   # unhighlight file
        except KeyError:
            self.space_selected_values.add(current)   # highlight file

    @util.run_if_window_not_empty(update_status_line=False)
    def h_invert_selection(self, char):
        """Invert selection made using <Space>"""
        self.space_selected_values = set(self.values) - self.space_selected_values


    # HACK: Following two funcions are actually used by npyscreen to display filtered
    #       values based on a search string, by highlighting the results. This is a
    #       hack that makes npyscreen highlight files that have been selected with
    #       <Space>, instead of highlighting search results

    def filter_value(self, index):
        return self._filter in self.display_value(self.values[index]).lower

    def _set_line_highlighting(self, line, value_indexer):
        """Highlight files which were selected with <Space>"""
        if value_indexer in self.get_relative_index_of_space_selected_values():
            self.set_is_line_important(line, True)   # mark as important(bold)
        else:
            self.set_is_line_important(line, False)
        # without this line every file will get highlighted as we go down
        self.set_is_line_cursor(line, False)


class MainView(npy.FormMuttActiveTraditional, base.ClidForm):
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
        base.ClidForm.__init__(self, parentApp)
        self.maindb = self.mp3db
        super().__init__(*args, **kwargs)
        base.ClidForm.enable_resizing(self)
        self.load_keys()

        self.after_search_now_filter_view = False
        self.load_files_to_show()
        self.wStatus1.value = 'clid v' + version.VERSION + ' '

        with open(const.CONFIG_DIR + 'first', 'r') as file:
            first = file.read()

        if first == 'true':
            # if app is run after an update, display a what's new message
            with open(const.CONFIG_DIR + 'NEW') as new:
                disp = new.read()
            npy.notify_confirm(message=disp, title="What's New", editw=0, wide=True)
            with open(const.CONFIG_DIR + 'first', 'w') as file:
                file.write('false')

    def load_keys(self):
        get_key = self.prefdb.get_key
        self.handlers.update({
            get_key('quit'):         lambda *a, **k: exit(),
            get_key('preferences'):  self.h_switch_to_settings,
        })
        self.wMain.load_keys()

    def h_switch_to_settings(self, char):
        """Switch to Preferences View"""
        self.parentApp.switchForm("SETTINGS")

    def load_files_to_show(self):
        """Set the mp3 files that will be displayed"""
        self.wMain.values = self.mp3db.get_values_to_display()
        # display tag preview of first file
        try:
            self.wMain.cursor_line = 0
            self.wMain.set_current_status()
        except IndexError:   # thrown if directory doest not have mp3 files
            self.wStatus2.value = 'No Files Found In Directory '
