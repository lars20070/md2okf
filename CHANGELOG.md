# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-07

### Changed

- Bump the documented minimum `sbx` version from 0.38.0 to 0.42.0.
- `scripts/bash.sh`, `scripts/pi.sh`, `scripts/compile-okf.sh` and
  `tests/test-sandbox.sh` now invoke `sbx run` with the kit path as the
  positional operand (`sbx run --name "${kit_name}" ./pi/`) instead of the
  deprecated `--kit <ref> <name>` form, which `sbx` v0.42.0 warns about on
  every invocation.
