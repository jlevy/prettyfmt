.DEFAULT_GOAL := default

.PHONY: default lint test build clean

default: lint test

lint:
	poetry run python devtools/lint.py

test:
	poetry run pytest

build:
	poetry build

clean:
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .venv/
