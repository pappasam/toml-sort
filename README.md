# toml-sort

A command line utility to sort your toml files. Requires Python 3.6 or greater.

## Installation

```bash
pip install toml-sort
```

## Usage

Read from stdin, write to stdout:

    cat input.toml | toml-sort

Read from file on disk, write to file on disk:

    toml-sort -o output.toml input.toml

Read from file on disk, write to stdout

    toml-sort input.toml

Read from stdin, write to file on disk

    cat input.toml | toml-sort -o output.toml

## Local Development

This project is super simple.

**Dependencies**

Install the following tools manually.

* [Poetry](https://github.com/sdispater/poetry#installation)
* [GNU Make](https://www.gnu.org/software/make/)

*Recommended*

* [pyenv](https://github.com/pyenv/pyenv)

**Set up development environment**

```bash
make setup
```

**Run Tests**

```bash
make test
```

## Written by

Samuel Roeca *samuel.roeca@gmail.com*
