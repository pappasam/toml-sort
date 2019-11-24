# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.17.0

### Added

* This `CHANGELOG.md`

### Changed

* `tomlkit>=0.5.8`. Upstream library made some important fixes.
* Add `isort`, make part of pre-commit pipeline

### Fixed

* `mypy`, `pylint`, `black`, and `isort` all pass.

### Removed

* AOT workaround in AOT parser. Latest version of tomlkit no longer spits out duplicate elements for AOT.
