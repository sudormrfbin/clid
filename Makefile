
PROJECTDIR = $(dir $(realpath $(firstword $(MAKEFILE_LIST))))
TESTDIR = $(PROJECTDIR)tests

test:
	find $(TESTDIR)/samples -name "*.mp3" > $(TESTDIR)/mp3_files.txt
