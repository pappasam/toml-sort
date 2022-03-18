# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.20.0

### Changed

- Moved CLI from click to argparse.

## 0.19.0

### Added

- CLI option to ignore case while sorting

## 0.18.0

Note: in this release, we've discovered a strange bug (we believe in tomlkit) where, sometimes, AOT elements are ordered without our consent. One of the cli tests has been marked `xfail`. If you'd like to help figure out why, we're always looking for contributors!

### Added

- Support for multiple FILENAME arguments in the CLI. Used for precommit / linting multiple files. Thanks @atugushev!
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

- AOT workaround in AOT parser. Latest version of tomlkit no longer spits out duplicate elements for AOT.
