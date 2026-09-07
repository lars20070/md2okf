# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-09-07

### Added

- `VERSION` and `CHANGELOG.md`, with `make lint` failing when they disagree.
- Notes-only GitHub Releases: pushing a `vX.Y.Z` tag runs
  `.github/workflows/release.yml`, which creates a Release whose body is the
  matching `CHANGELOG.md` section (`scripts/check-release-tag.sh`,
  `scripts/release-notes.sh`). Documented in `CONTRIBUTING.md`.
- `/skill-creator` and `/readme` skills for Claude Code and Cursor.

### Changed

- Bump the documented minimum `sbx` version from 0.38.0 to 0.42.0.
- `scripts/bash.sh`, `scripts/pi.sh`, `scripts/compile-okf.sh` and
  `tests/test-sandbox.sh` now invoke `sbx run` with the kit path as the
  positional operand (`sbx run --name "${kit_name}" ./pi/`) instead of the
  deprecated `--kit <ref> <name>` form, which `sbx` v0.42.0 warns about on
  every invocation.
- Simplify the README Mermaid overview diagram (layout and helper-tool
  colours).

### Fixed

- README quickstart warning now names this project (`md2okf`) when saying a
  later `sbx` may break it.
- Cursor `/skill-creator` now points at `.cursor/skills/` (paths and validate
  command), not `.claude/skills/`.
- `/skill-creator` `quick_validate.py`: require a full-line closing `---` for
  frontmatter (not a `---` prefix), and validate `compatibility` when the key
  is present rather than only when it is truthy.
