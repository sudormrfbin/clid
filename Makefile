TESTDIR = tests

.PHONY: test reqs

test:
	find $(TESTDIR)/samples -name "*.mp3" | xargs realpath > $(TESTDIR)/mp3_files.txt

reqs:
	pipreqs --force --savepath requirements.txt clid/
