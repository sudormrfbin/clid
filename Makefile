TESTDIR = tests

.PHONY: test

test:
	find $(TESTDIR)/samples -name "*.mp3" | xargs realpath > $(TESTDIR)/mp3_files.txt
