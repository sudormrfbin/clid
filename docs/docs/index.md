# clid

Clid is an app for those whose home is the terminal and can't live without a well organized music collection :)
With clid, you can edit the metadata(tags) of mp3 files, right from the terminal. Awesome ? Let's get started !

## Installation

You're gonna need two things before you install the app:
- Python**3**
- Pip(python's package manager)[optional]

Pip will be installed by default if Python version is > 3.4 (`python --version`).
Else you will have to install it manually.
<!--instructions on how to do this-->

You can use your package manager to install them.

### Using Pip

```shell
$ [sudo] pip install clid
```

### From Source(Without Pip)

```shell
$ git clone https://github.com/GokulSoumya/clid.git
$ cd clid
$ [sudo] python3 setup.py install
```

## Launching The App

Enter `clid` in the command line to start the app:

![clid main window](main.png "Main Window")

What do ya think, eh ?

## Quick Start

The basics are simple:
1. Move with arrow keys or `j` and `k`.
2. <kbd>Enter</kbd> to select a file.
3. Edit the tags.
4. `OK` to save the tags or `Cancel` to abort edit.

## Main Window

Main window has 3 parts:

![clid main annnotated](main_annotated.png)

<!--link-->
1. File viewer, showing files in `~/Music` by default,
2. Status line , showing live preview of tags of file under cursor,
3. Command line, which accepts commands.


### File Viewer

You can see the mp3 files in the selected directory<!--link--> in the main window. You can use <kbd>UpArrow</kbd>,
<kbd>DownArrow</kbd>, <kbd>j</kbd>, <kbd>k</kbd>, <kbd>Home</kbd>, <kbd>PageUp</kbd>, etc to move around.
Hit <kbd>Enter</kbd> when you've found the file you want to edit, or batch tag files<!--link-->. You can also search
for files<!--link-->.

### Status Line

The status line shows a live preview of metadata of file under cursor in the specified format<!--link-->.
The default format is `artist - album - track_number title`.

### Command Line

You can execute commands and perform searches from here. Press `:` to enter commands<!--link--> and
`/` to search<!--link--> for files

## Editing Tags

### Tagging Individual Files

1. Select the file you want to edit with <kbd>Enter</kbd>
2. Edit the tags as required.

> You can also change the name of the file here. The extension(`.mp3`) isn't shown.

3. You can then press `OK` to save the changes or `Cancel` to discard changes. Default keybindings for
saving tags is <kbd>Ctrl</kbd> + <kbd>S</kbd> and canceling is <kbd>Ctrl</kbd> + <kbd>Q</kbd>.

### Tagging Multiple Files At Once

You can batch tag files in clid:

1. Select and deselect files with <kbd>Space</kbd> and press <kbd>Enter</kbd> to edit the files. *Note that 
pressing <kbd>Enter</kbd> will also add the file currently under the cursor to list of files that will be edited*.

2. You will see a window with blank tag fields. Only the tag fields which you modify here will be saved to the
files, that is, if this is what you have,

![clid batch tagging](batch_tag_edit.png)

then 

3. You can save or cancel as mentioned above.



