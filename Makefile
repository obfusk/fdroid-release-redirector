SHELL   := /bin/bash
PYTHON  ?= python3

export PYTHONWARNINGS := default

.PHONY: all test lint lint-extra clean cleanup

all:

test: lint lint-extra

lint:
	flake8 app.py
	pylint app.py

lint-extra:
	mypy --strict --disallow-any-unimported app.py

clean: cleanup

cleanup:
	find -name '*~' -delete -print
	rm -fr __pycache__/ .mypy_cache/
