# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `okfctl` (pinned 0.4.0, checksummed release archive) to the sandbox toolchain,
  and a `curate-okf` skill covering it. It replaces `okf-lint` as the wiki's
  gate and takes ownership of the reserved `index.md` files: the agent runs
  `okfctl index build` instead of writing link lists by hand, and the gate's
  `okfctl index check` fails closed on a stale or hand-edited index.
- `compile-okf/scripts/check-okf.sh`, one gate with two call sites — the agent
  runs it before finishing, `make check-okf` runs the same file on the host. It
  combines `okfctl validate`, a new dependency-free `frontmatter-guard.py`,
  `okfctl lint`, `okfctl analyze` for links that resolve to nothing, and
  `okfctl index check`. Lint defects (`broken-link`, `orphan`, `type-hygiene`,
  `status-lifecycle`, `spec-version`) block; `missing-xref` and `coverage-gap`
  are printed as advice, since they are judgment calls and the gate runs
  unattended inside the compile loop.

### Changed

- Migrate the wiki to **OKF v0.2**, following `SPEC.md`: every page's legacy
  `timestamp` becomes `generated: { by, at }` (§5.2) with the actor recorded as
  `pi/<model-id>` (§7), and the bundle-root `index.md` marker moves to `"0.2"`.
  Index links are now relative, which is what `okfctl index build` writes;
  cross-links in page prose stay bundle-absolute.

- Persist Pi's native `~/.pi/agent/sessions` tree in
  `$XDG_STATE_HOME/md2okf/sessions`, bind-mounted from host state instead of a
  repository-local `logs/sessions/`. An exported `XDG_STATE_HOME` takes
  precedence over the gitignored `.env`, with `~/.local/state` as the fallback;
  changing it requires rebuilding the sandbox. Existing legacy transcripts are
  not migrated.
- Mount only what the agent needs into the sandbox, instead of the whole
  repository read-write: `okf/` and the external session-state directory
  read-write, and `md/`, `scripts/` and `SPEC.md` read-only. Nothing else in the
  repository is visible inside the microVM, so the agent's restriction to
  `okf/` is now enforced by the filesystem rather than by instructions alone.
  The mount list lives in `scripts/lib/sandbox-mounts.sh`, shared by every
  script that creates the sandbox.
- `okf/` is the primary mount and therefore the working directory inside the
  VM, so the agent's config and the `compile-okf` lint wrapper now address the
  read-only mounts as `../md/`, `../scripts/` and `../SPEC.md`.
- Move the Docker Sandbox kit from `pi/` to `kits/md2okf/`. Scripts, tests, and
  docs now point at `./kits/md2okf/`.
- Bump the documented minimum `sbx` version from 0.42.0 to 0.43.0.

### Fixed

- Ensure the `compile-okf` check script is executable after kit setup (`chmod`
  in `kits/md2okf/spec.yaml`), so `make test-sandbox` passes when the static
  `files/home/` copy drops the exec bit.

### Removed

- `okf-lint` (`@thisismydesign/okf-lint`) and its `okf/.okflintrc.json` rule
  file, superseded by `okfctl` and the frontmatter guard. The guard re-implements
  the rules okfctl's spec floor deliberately leaves open — title, description,
  tags, provenance, the `okf_version` marker and the log's date headings — and
  adds a format check on provenance timestamps. `prefer-absolute-links` retires
  with it, for index files only.

## [0.1.0] - 2026-09-07

### Added

- `VERSION` and `CHANGELOG.md`, with `make lint` failing when they disagree.
- Notes-only GitHub Releases: pushing a `vX.Y.Z` tag runs
  `.github/workflows/release.yml`, which creates a Release whose body is the
  matching `CHANGELOG.md` section (`scripts/check-release-tag.sh`,
  `scripts/release-notes.sh`). Documented in `CONTRIBUTING.md`.
- `/skill-creator` and `/readme` skills for Claude Code and Cursor.

### Changed

- Bump the pinned Pi coding agent from 0.84.2 to 0.85.1.
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
