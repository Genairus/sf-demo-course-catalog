PYTHON ?= python3
setup:
	$(PYTHON) --version

build:
	$(PYTHON) -m compileall -q catalog

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

lint:
	$(PYTHON) -W error -m compileall -q -f catalog tests
