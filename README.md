# toml-sort

A command line utility to sort your toml files. Requires Python 3.6 or greater.

## Motivation

I wrote this library because I couldn't find any "good" sorting utilities for TOML files. This library strives to sort TOML files by providing the following features:

* Preserve comments
* Sort tables / arrays of Tables
* Option to sort table keys, or not
* Preserve whitespace / indentation (in progress)

## Installation

```bash
pip install toml-sort
```

## Usage

This project can be used as either a Python library or a command line utility. I will document the Python library interface in the future when it stabilizes. The command line interface should remain fairly stable.

### Command line interface

Read from stdin, write to stdout:

    cat input.toml | toml-sort

Read from file on disk, write to file on disk:

    toml-sort -o output.toml input.toml

Read from file on disk, write to stdout

    toml-sort input.toml

Read from stdin, write to file on disk

    cat input.toml | toml-sort -o output.toml

Only sort the top-level tables / arrays of tables

    cat input.toml | toml-sort -i
    cat input.toml | toml-sort --ignore-non-tables

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
