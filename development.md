## Development

Developer setup:

```shell
# To run a shell within the Python environment:
poetry shell
# Thereafter you can run tests.

# To run tests:
pytest   # all tests
pytest -s src/module/some_file.py  # one test, showing outputs

# Build wheel:
make build

# Linting and testing:
make lint
make test

# Poetry dependency management commands:
# Upgrade all dependencies:
poetry up
# Update poetry itself: 
poetry self update
```