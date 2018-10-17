
"""
clid.gui.widgets
~~~~~~~~~~~~~~~~

Custom widgets made using `prompt_toolkit`.
"""


from prompt_toolkit.layout import (
    HSplit,
    VSplit,
    Window,
    ScrollOffsets,
    NumberedMargin,
    ScrollbarMargin,
    FormattedTextControl,
)
from prompt_toolkit.layout.screen import Point
from prompt_toolkit.widgets import Label, TextArea
from prompt_toolkit.key_binding import KeyBindings


class ItemList:
    """
    A widget for showing a list of items, complete with a scroll bar,
    line numbers and navigation keybindings.
    Attributes:
        items (list of str): List of items to show.
        cursor (prompt_toolkit.layout.screen.Point):
            Represents the cursor position in terms of lines and columns.
        _disp_items (list of tuples):
            `items` converted into a form `prompt_toolkit` can recognize and
            display properly.
        self.control: `prompt_toolkit` control that actually displays the data.
        self.window (prompt_toolkit.layout.Window):
            A `Window` displays a control, and is responsible for line wrapping,
            scrolling, etc.
    """

    def __init__(self, items):
        self.items = items
        self.cursor = Point(0, 0)
        self._disp_items = [("", i + "\n") for i in items]

        self.control = FormattedTextControl(
            text=self._disp_items,
            get_cursor_position=lambda: self.cursor,
            key_bindings=self._get_key_bindings(),
            focusable=True,
        )

        self.window = Window(
            content=self.control,
            # ignore_content_height=True,
            wrap_lines=False,
            cursorline=True,
            always_hide_cursor=True,
            right_margins=[ScrollbarMargin()],
            left_margins=[NumberedMargin()],
            scroll_offsets=ScrollOffsets(top=2, bottom=2),
        )

    def move_cursor_up(self, lines_to_move=1):
        # Move the cursor up by `lines_to_move` lines.
        y = self.cursor.y
        y = y - lines_to_move if y > 0 else 0
        self.cursor = Point(0, y)

    def move_cursor_down(self, lines_to_move=1):
        total_lines = len(self.items)
        y = self.cursor.y
        y = y + lines_to_move if y + lines_to_move < total_lines else y
        self.cursor = Point(0, y)

    def move_cursor_to_beginning(self):
        self.cursor = Point(0, 0)

    def move_cursor_to_end(self):
        y = len(self.items) - 1
        self.cursor = Point(0, y)

    def move_cursor_page_up(self):
        visible_lines = len(self.window.render_info.displayed_lines)
        # NOTE: we subtract 3 from visible_lines to compensate for scroll offsets
        #       so that the line from where page up was pressed is still visible
        #       at the bottom
        self.move_cursor_up(lines_to_move=visible_lines - 3)

    def move_cursor_page_down(self):
        visible_lines = len(self.window.render_info.displayed_lines)
        self.move_cursor_down(lines_to_move=visible_lines - 3)

    def _get_key_bindings(self):
        keybindings = KeyBindings()

        keybindings.add("up")(lambda event: self.move_cursor_up())
        keybindings.add("k")(lambda event: self.move_cursor_up())
        keybindings.add("down")(lambda event: self.move_cursor_down())
        keybindings.add("j")(lambda event: self.move_cursor_down())
        keybindings.add("home")(lambda event: self.move_cursor_to_beginning())
        keybindings.add("end")(lambda event: self.move_cursor_to_end())
        keybindings.add("pageup")(lambda event: self.move_cursor_page_up())
        keybindings.add("pagedown")(lambda event: self.move_cursor_page_down())

        return keybindings

    def __pt_container__(self):
        return self.window


class LabeledTextArea:
    """
    Widget for accepting input, with an attached label.
    Attributes:
        label (str): Text to be used as label.
        text (str): Initial value of the input field.
    """

    def __init__(self, label="", text=""):
        self.label = label + ': '

        self._text_control = TextArea(
            text=text, focusable=True, multiline=False, wrap_lines=False
        )

        self._label_control = Label(text=self.label, dont_extend_width=True)

        self.container = HSplit(
            [VSplit([self._label_control, self._text_control])], height=1
        )

    @property
    def text(self):
        return self._text_control.text

    @text.setter
    def text(self, value):
        self._text_control.text = value

    def __pt_container__(self):
        return self.container
