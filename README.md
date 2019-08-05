# toml-sort

A command line utility to sort your toml files. Requires Python 3.6 or greater.

## Installation

```bash
pip install toml-sort
```

## Usage

Currently, this project only reads from a toml file on disk and writes to stdout. I plan to flesh out the interface in the coming days.

```bash
# Prints sorted results to stdout
toml-sort FILENAME
```

## Local Development

### Dependencies

* [Poetry](https://github.com/sdispater/poetry#installation)
* [GNU Make](https://www.gnu.org/software/make/)

### Run Tests

```bash
make test
```

## Written by

Samuel Roeca *samuel.roeca@gmail.com*
