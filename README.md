# clid

Clid is a command line app for editing tags of mp3 files. Clid is different from other
command line tools to edit tags, as you can edit tags in a curses based ui.

![clid main window](docs/docs/main.png "Main Window")

## Installation

See wiki for detailed installation instructions.<!--link-->

### Using pip

```shell
$ [sudo] pip3 install clid
```

### From Source

```shell
$ git clone https://github.com/GokulSoumya/clid.git
$ cd clid
$ [sudo] python3 setup.py install
```

### Updating

To update the app, run

```shell
$ [sudo] pip install -U clid
```

You can launch the app by entering `clid` in the command line.

## Usage

### Quick Start

1. Move with arrow keys or `j` and `k`.
2. <kbd>Enter</kbd> to select a file.
3. Edit the tags.
4. `OK` to save the tags or `Cancel` to abort edit.
5. Type `:q` at main window to quit.

See the [wiki](docs/docs/index.md) for documentation and additional details.

## Changelog

### v0.7.0

- Fix resize issue
- Created documentation
- Customizable keybindings
- Refactor the whole codebase
- Autocomplete in genre tag field
- Key binding for quitting app(^Q)
- Tag multiple files at the same time
- Invert selection made for batch tagging
- Edit filename from inside the tag editor
- Show correct tag preview when changing directory
- Option for using regular expressions while searching
- Genre can now be displayed in the status line preview
- Short description of preferences option in status line
- Save position of cursor in the tag editorwhen editing files

### v0.6.3

- Vi keybindings
- Added option for smooth scroll
- Preferences are now saved when updating the app
- Validators for `smooth_scroll` and `preview_format`
- Display a "What's New" Popup when app is run after an update

## Thanks

I couldn't have made this app without these amazing libraries...

- [npyscreen](https://bitbucket.org/npcole/npyscreen), a Python wrapper around ncurses.
- [stagger](https://github.com/lorentey/stagger), an ID3v1/ID3v2 tag manipulation package written in pure Python 3
- [configobj](https://github.com/DiffSK/configobj), a Python 3+ compatible port of the configobj library

...And my dear laptop with 512 MB RAM ;)

Enjoy!
