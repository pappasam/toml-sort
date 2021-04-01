# toml-sort

[![pypi-version](https://img.shields.io/pypi/v/toml-sort.svg)](https://python.org/pypi/toml-sort)
[![license](https://img.shields.io/pypi/l/toml-sort.svg)](https://python.org/pypi/toml-sort)
[![python-versions](https://img.shields.io/pypi/pyversions/toml-sort.svg)](https://python.org/pypi/toml-sort)
[![image-pypi-downloads](https://pepy.tech/badge/toml-sort)](https://pepy.tech/project/toml-sort)
[![readthedocs-status](https://readthedocs.org/projects/toml-sort/badge/?version=latest)](https://toml-sort.readthedocs.io/en/latest/?badge=latest)

A command line utility to sort and format your toml files. Requires Python 3.6+.

Read the latest documentation here: <https://toml-sort.readthedocs.io/en/latest/>

## Installation

```bash
# With pip
pip install toml-sort

# With poetry
poetry add --dev toml-sort
```

## Motivation

This library sorts TOML files, providing the following features:

- Sort tables and Arrays of Tables (AoT)
- Option to sort non-tables / non-AoT's, or not
- Preserve inline comments
- Option to preserve top-level document comments, or not
- Standardize whitespace and indentation

I wrote this library/application because I couldn't find any "good" sorting utilities for TOML files. Now, I use this as part of my daily workflow. Hopefully it helps you too!

## Command line usage

This project can be used as either a command line utility or a Python library. Read the docs for an overview of its library capabilities. For command line usage, see below:

```console
$ toml-sort --help
Usage: toml-sort [OPTIONS] [FILENAMES]...

  Sort toml file FILENAME(s), writing to file(s) or stdout (default)

  FILENAME a filepath or standard input (-)

  Examples (non-exhaustive list):
    Stdin -> Stdout : cat input.toml | toml-sort
    Disk -> Disk    : toml-sort -o output.toml input.toml
    Linting         : toml-sort --check input.toml input2.toml input3.toml
    Inplace Disk    : toml-sort --in-place input.toml input2.toml

Options:
  -o, --output PATH  The output filepath. Choose stdout with '-' (the
                     default).

  -a, --all          Sort all keys. Default is to only sort non-inline 'tables
                     and arrays of tables'.

  -i, --in-place     Makes changes to the original input file. Note: you
                     cannot redirect from a file to itself in Bash. POSIX
                     shells process redirections first, then execute the
                     command.

  --no-header        Do not keep a document's leading comments.
  --check            Check if an original file is changed by the formatter.
                     Return code 0 means it would not change. Return code 1
                     means it would change.

  -I, --ignore-case  When sorting, ignore case.
  --version          Show the version and exit.
  --help             Show this message and exit.
```

## Example

The following example shows the input, and output, from the CLI with default options.

### Unformatted, unsorted input

```toml
# My great TOML example

  title = "The example"

[[a-section.hello]]
ports = [ 8001, 8001, 8002 ]
dob = 1979-05-27T07:32:00Z # First class dates? Why not?



  [b-section]
  date = "2018"
  name = "Richard Stallman"

[[a-section.hello]]
ports = [ 80 ]
dob = 1920-05-27T07:32:00Z # Another date!

                          [a-section]
                          date = "2019"
                          name = "Samuel Roeca"
```

### Formatted, sorted output

```toml
# My great TOML example

title = "The example"

[a-section]
date = "2019"
name = "Samuel Roeca"

[[a-section.hello]]
ports = [ 8001, 8001, 8002 ]
dob = 1979-05-27T07:32:00Z # First class dates? Why not?

[[a-section.hello]]
ports = [ 80 ]
dob = 1920-05-27T07:32:00Z # Another date!

[b-section]
date = "2018"
name = "Richard Stallman"
```

## Local Development

Local development for this project is quite simple.

**Dependencies**

Install the following tools manually.

- [Poetry>=1.0](https://github.com/sdispater/poetry#installation)
- [GNU Make](https://www.gnu.org/software/make/)

_Recommended_

- [asdf](https://github.com/asdf-vm/asdf)

**Set up development environment**

```bash
make setup
```

**Run Tests**

```bash
make test
```

## Written by

Samuel Roeca, *samuel.roeca@gmail.com*
