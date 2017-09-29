# clid

Clid is a command line app for editing tags of mp3 files. Clid is different from other
command line tools to edit tags, as you can edit tags in a curses based ui.

![clid main window](docs/docs/main.png "Main Window")

## Installation

See wiki for detailed installation instructions.<!--link-->

### Using pip

```shell
$ [sudo] pip install clid
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
<!--Real link-->

## Changelog

### v0.6.3

- [x] Vi keybindings
- [x] Added option for smooth scroll
- [x] Preferences are now saved when updating the app
- [x] Validators for `smooth_scroll` and `preview_format`
- [x] Display a "What's New" Popup when app is run after an update

### v0.6.2

- [x] Fix: Issue #1 in Github
- [x] Added key-binding(`u`) for reloading `music_dir`
- [x] Fix: All option are now aligned properly in preferences view
- [x] Added validators for preferences(Error message is shown if an error occurs)

## Thanks

I couldn't have made this app without these amazing libraries...

- [npyscreen](https://bitbucket.org/npcole/npyscreen), a Python wrapper around ncurses.
- [stagger](https://github.com/lorentey/stagger), an ID3v1/ID3v2 tag manipulation package written in pure Python 3
- [configobj](https://github.com/DiffSK/configobj), a Python 3+ compatible port of the configobj library

...And my dear laptop with 512 MB RAM ;)

Enjoy!
