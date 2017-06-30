# clid

Clid is a command line app written in Python3 for command-line lovers to edit mp3 files' ID3 tags. This app is different from other
command line tools to edit tags, as you can edit tags in a graphical interface.(It's like [cmus](https://github.com/cmus/cmus),
without the player and with a tag editor)

Made with a lot of help from

- [npyscreen](https://bitbucket.org/npcole/npyscreen), a Python wrapper around ncurses.
- [stagger](https://github.com/lorentey/stagger), an ID3v1/ID3v2 tag manipulation package written in pure Python 3
- [configobj](https://github.com/DiffSK/configobj), a Python 3+ compatible port of the configobj library
- and a laptop with 512 MB RAM(Yeah. I know.)

## Installation

> Note: You should have Python 3 installed, not Python 2, to install and use clid.

> Note: You will have to install pip manually if the Python version is < 3.4


### Using pip

```shell
$ [sudo] pip install clid
```

### From Source

```shell
$ git clone https://github.com
$ /GokulSoumya/clid.git
$ cd clid
$ [sudo] python3 setup.py install
```

You can then launch the app by entering `clid` in the command line.


## Usage

### Viewing Files

The main window will show the mp3 files you have in `~/Music`. The interface is similar to that of cmus:

![clid main window](./img/main.png  "The Main Window")

You will have a command line at the bottom of the window, to recieve commands. You will also see a live preview of the
common tags of the file under the cursor.

> Note: The status line shows the tags in `artist - album - track_number title` format

### Editing Tags

To edit the tags of a file, simply hit <kbd>Enter</kbd>(or <kbd>Return</kbd>). You will see a new window:

![clid tag edit](./img/edit.png  "Tag Editing Window")

Use the arrow keys to move through the tags; edit them if needed and hit `OK`(or <kbd>Ctrl</kbd> + <kbd>S</kbd>) when you're done. `Cancel`(<kbd>Ctrl</kbd> + <kbd>Q</kbd>) will discard changes.


### Editing Preferences

To edit preferences, press `2`. Then hit <kbd>Enter</kbd> on the highlighted setting to edit it (it will be then shown
at the bottom of the screen; edit it and hit <kbd>Enter</kbd> again).
