PYTHON ?= python3
export PYTHONPATH := src

setup:
	$(PYTHON) --version

build:
	$(PYTHON) -m compileall -q src

test:
	$(PYTHON) -m unittest discover -s tests -t . -v

lint:
	$(PYTHON) -W error -m compileall -q -f src tests
