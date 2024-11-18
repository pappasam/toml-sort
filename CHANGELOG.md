# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.24.1

### Fixed

- Re-add .pre-commit-hooks. Resolves <https://github.com/pappasam/toml-sort/issues/75>

## 0.24.0

### Fixed

- Only write to disk if file contents changed

### Removed

- Dropped support for Python 3.7 and 3.8.
- Dropped support for tomlkit < 0.13.2
- Removed sphinx documentation.

## 0.23.1

### Fixed

- Error where the `first` override introduced tomlkit wrappers into the configuration and caused serialization problems for the dataclass: <https://github.com/pappasam/toml-sort/pull/58>

## 0.23.0

### Added

- Ability to override sort configuration per key in configuration: <https://github.com/pappasam/toml-sort/pull/52>
- Option to sort particular keys first in output: <https://github.com/pappasam/toml-sort/pull/53>, updated by <https://github.com/pappasam/toml-sort/pull/54>

### Fixed

- Issue where files that contain only comments are doubled: <https://github.com/pappasam/toml-sort/pull/51>

## 0.22.4

### Fixed

- Trailing whitespace is no longer added to blank comments
- An issue where dotted keys raised a `TypeError`

## 0.22.3

### Fixed

- Turns out that, at this time, `toml-sort` is only compatible with `tomlkit` `0.11.2`+. We now make this clear in our dependencies. See: <https://github.com/pappasam/toml-sort/issues/41> and <https://github.com/sdispater/tomlkit/compare/0.11.1...0.11.2>.

## 0.22.2

### Added

- New pre-commit hook (`toml-sort-fix`) that enables users to change, instead of check, their toml files.

## 0.22.1

### Fixed

- Issue where an IndexError exception was raised on an empty array. See: <https://github.com/pappasam/toml-sort/pull/36>

## 0.22.0

Release entirely related to this PR: <https://github.com/pappasam/toml-sort/pull/33>

### Added

- Optionally add the ability to sort inline tables and arrays. New switches added for this functionality: `--sort-inline-tables` and `--sort-inline-arrays`, which are implied by the existing `--all` option
- New options groups to the CLI, to group the related formatting, comment, and sorting arguments
- Switch to add trailing comma to multi-line inline arrays `--trailing-comma-inline-array`
- Some additional formatting checks

### Changed

- Make sure inline arrays and tables are consistently formatted
- Normalize the formatting for `key = value` pairs, always one space on either side of equals sign

## 0.21.0

This is a pretty big comment-related release. Resolves the long-standing issue: <https://github.com/pappasam/toml-sort/issues/11>.

### Changed

- Header, Footer, and Block comments are retained by default and can be disabled with new CLI options.

### Added

- New CLI comment-removal options: `--no-comments`, `--no-header-comments`, `--no-footer-comments`, `--no-inline-comments`, `--no-block-comments`
- The ability to configure spaces before inline comments with `--spaces-before-inline-comment`

### Deprecated

- The CLI option: `--no-header`. This will be removed in a future release and is replaced by `--no-header-comments`

## 0.20.2

### Fixed

- An issue where the sorter fails with boolean values in file. See <https://github.com/pappasam/toml-sort/issues/29> and <https://github.com/pappasam/toml-sort/pull/31>

## 0.20.1

### Fixed

- Preserve inline comments for boolean values. See: <https://github.com/pappasam/toml-sort/pull/27>

## 0.20.0

### Added

- Support configuring CLI with `pyproject.toml` configuration file.

### Changed

- Moved CLI from click to `argparse`.
- Update minimum version of `tomlkit` to 0.8.0. This drops support for Python 3.6.

## 0.19.0

### Added

- CLI option to ignore case while sorting

## 0.18.0

Note: in this release, we've discovered a strange bug (we believe in `tomlkit`) where, sometimes, AOT elements are ordered without our consent. One of the CLI tests has been marked `xfail`. If you'd like to help figure out why, we're always looking for contributors!

### Added

- Support for multiple FILENAME arguments in the CLI. Used for `precommit` / linting multiple files. Thanks @atugushev!
- Pre-commit hook

### Changed

- Provide more-comprehensive error messages for interactive CLI usage.

## 0.17.0

### Added

- This `CHANGELOG.md`

### Changed

- `tomlkit>=0.5.8`. Upstream library made some important fixes.
- Add `isort`, make part of pre-commit pipeline.

### Fixed

- `mypy`, `pylint`, `black`, and `isort` all pass.

### Removed

- AOT workaround in AOT parser. Latest version of `tomlkit` no longer spits out duplicate elements for AOT.
