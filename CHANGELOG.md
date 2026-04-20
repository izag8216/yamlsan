# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-04-20

### Added

- `validate` command: scan markdown files against YAML/JSON schema
- `fix` command: auto-apply default values for missing fields
- `--ci` flag for CI-friendly minimal output with exit codes
- `--dry-run` flag for fix preview
- Schema supports: required, type, allowed, pattern, default, min/max length, min/max value
- Rich table output with color-coded errors and warnings
- Recursive directory scanning for `.md` files
- YAML and JSON schema file support
