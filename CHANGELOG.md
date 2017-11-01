CHANGELOG
=========

v0.7.0
------

- [x] Create docs
- [ ] Add unit tests
- [x] Batch tag files
- [ ] Customizable keybindings
- [x] Refactor the whole codebase
- [ ] Autocomplete in genre tag field
- [ ] Added genre to format specifiers
- [x] Change color of filename textbox
- [ ] ^L for refreshing screen
- [x] Filename field in tag editing view
- [x] Short description of preferences option in status line
- [x] Improved speed when batch tagging large number of files
- [ ] Show correct preview when changing dirs; 'No Files Found In Directory' if no mp3
- [ ] `Page Up` and `Page Down` keys when editing metadata to go to next and previous file
- [x] Save position of cursor(in which tbox) when editing files
- [x] Fix resize(min_l and min_c)
- [ ] Option for regex search
- [x] Invert selection
- [ ] Add search for pref view
- [x] Key binding for quitting app(^Q)

- - -

v0.6.3.1
--------

- [x] Fix: Issue #2 in Github - error when installing v0.6.3

v0.6.3
------

- [x] Vi keybindings
- [x] Added option for smooth scroll
- [x] Preferences are now saved when updating the app
- [x] Validators for smooth_scroll and preview_format
- [x] Display a "What's New" Popup when app is run after an update

- - -

v0.6.2
------

- [x] Fix: Issue #1 in Github
- [x] Added key-binding(`u`) for reloading `music_dir`
- [x] Fix: All option are now aligned properly in preferences view
- [x] Added validators for preferences(Error message is shown if an error occurs)

v0.6.1
------

- [x] Add track number to preview format option in preferences

v0.6.0
------

- [x] Add Home/End for command line
- [x] Use `set` command(to edit preferences) form main view
- [x] Add preferences option for custom preview in main view


v0.5.3
------

- [x] Add HOME and END keys to text boxes
- [x] Fix: Error thrown if date is not of the format YYYY-MM-DD


v0.5.2
------

- [x] Add date tag to editor
- [x] Add label to Preferences
- [x] Add comment tag to editor
- [x] Fix: Genre not being saved
- [x] Fix: Error thrown when Track No. is str(has to be int)
- [x] Fix: Error thrown when `OK` or `Cancel` is pressed


v0.5.1
------

- [x] Add keybindings to save(^S) and cancel(^Q) when editing tags
- [x] Update status line when page up/down is pressed in the main view
- [x] Fix: app crashes when up/down, page/up/down keys are pressed if there are no files in display
