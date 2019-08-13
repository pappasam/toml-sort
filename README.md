# toml-sort

A command line utility to sort and format your toml files. Requires Python 3.6 or greater.

## Installation

```bash
pip install toml-sort
```

## Motivation

 This library strives to sort TOML files by providing the following features:

* Preserve inline comments and top-level comments, when possible
* Sort tables / arrays of Tables
* Option to sort table keys, or not
* Standardize whitespace and indentation

I wrote this library because I couldn't find any "good" sorting utilities for TOML files.

## Usage

This project can be used as either a command line utility or a Python library.

### Command line interface

Read from stdin, write to stdout:

    cat input.toml | toml-sort

Read from file on disk, write to file on disk:

    toml-sort -o output.toml input.toml

Read from file on disk, write to stdout

    toml-sort input.toml

Read from stdin, write to file on disk

    cat input.toml | toml-sort -o output.toml

Sort all keys, not just top-level / table keys

    cat input.toml | toml-sort -a

## Local Development

Local development for this project is quite simple.

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
