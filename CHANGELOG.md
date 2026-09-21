# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2026-09-21

### Added

- **`md2okf --shell` and `md2okf --agent`, which open the sandbox.** Both build
  or refresh it first when none exists or the running one no longer matches
  `kits/md2okf/`, so the prerequisite behind the bare
  `sbx exec -it md2okf -- bash` — knowing to run `python -m md2okf.sandbox`
  first, and that a stale sandbox is entered silently — is gone. The terminal
  is handed over with `execvp` rather than a child process, so the TTY, job
  control, Ctrl-C and the exit code are the guest's own. These are for
  inspecting the sandbox, not authoring in it: they do not restage a compile
  run. Helper CLIs are refreshed, an empty spec mount gets the bundled spec, and
  prior workbench content otherwise remains. The next compile replaces
  `work/okf`; Pi transcripts persist. Only `--fresh` combines with them; every
  other compile option is refused rather than ignored. The flag is `--agent`
  rather than `--pi` so that changing the agent framework later would not
  change a published interface.

### Changed

- **The default model is now `deepseek/deepseek-v4-pro`**, in place of
  `qwen/qwen3.6-35b-a3b`. Every compile runs on it unless `settings.json` says
  otherwise, so the cost and the quality of a run both move with this. The
  routing pin it needs was already in `models.json` — DeepInfra only, no
  fallbacks — and, being a model Pi's catalogue knows, it keeps the catalogue's
  1M context and 384K output rather than the 16,384-token default that truncates
  a long `write` mid-argument.
- **One version for the whole repository.** `VERSION` now governs every project
  in the tree, not just the driver: the four host CLIs (`inspectmd`,
  `inspectokf`, `sizeokf`, `merkleokf`), `web2md` and `pdf2md` all move from
  their standalone `0.1.0` to the repo version. `./scripts/sync-versions.sh`
  writes the literal into each `pyproject.toml` and refreshes each `uv.lock`,
  and `make lint` runs its `--check` form, so a release cannot ship a CLI whose
  `--version` disagrees with the tag. The version stays a literal rather than a
  dynamic read of `../../VERSION` because the CLIs are also built from a staged
  copy holding only `pyproject.toml` and `src/`, where no path above the project
  root exists.
- Bump the pinned Pi coding agent from 0.85.1 to 0.86.1, and pin `cacheWarming`
  to `"streaming"` alongside it. 0.86 adds cost-aware prompt-cache warming and
  defaults it on, so the kit states its position rather than inheriting one
  that can move again on the next bump. Nothing else in the release reaches
  this project: the `--mode json` wire format is unchanged, and all three of
  0.86.0's breaking changes are extension- or SDK-level.
- The `inspect-md` skill now states what its section ranges actually cover: a
  span ends at the next heading of **any** level, so a parent section does not
  contain its children and each has to be read by its own index. It also records
  that `-L` filters the map without renumbering `Index`, and that frontmatter
  and headings inside fenced code are left out.
- `tree` is documented as a host requirement for `inspectokf`, and
  `make install-clis` now warns when it is missing rather than leaving the
  binary to report it at first use. Only the host is affected: the sandbox
  installs its own copy, so a compile never needed one.
- Linux gets its own uv environments. A venv is not portable across platforms
  and a direct-mode sandbox shares the tree with the macOS host, so `make`
  exports `UV_PROJECT_ENVIRONMENT=.venv-linux` on Linux and the default `.venv/`
  stays macOS-only. The value is relative on purpose: each of the seven uv
  projects then gets its own, where an absolute path would collapse them into
  one shared environment.
- The README overview diagram names the agent's skills by their skill ids
  (`inspect-md`, `inspect-okf`, `size-okf`, `merkle-okf`, `curate-okf`) rather
  than by the binaries behind four of them, which is the distinction every one
  of those skills makes in its own first paragraph. `curate-okf` joins the
  diagram, and the session-state node names the `sessions` directory the driver
  actually mounts.

### Fixed

- **`--shell` and `--agent` no longer mount an empty `SPEC.md`.** `ensure_roots`
  can only create the spec mount empty — sbx cannot mount a path that does not
  exist — and only a compile's `restage` filled it, so an interactive session on
  a workbench that had never compiled handed the agent a 0-byte `../SPEC.md`.
  That is the one file outranking every instruction it has, and an agent reading
  it empty wrote a wiki declaring `okf_version: ""`, which `okfctl index build`
  then dropped, leaving the frontmatter guard and the index check looking as
  though they contradicted each other. `stage_tooling` now floors the mount with
  the bundled spec, filling it only when empty, so a compile's `--spec` still
  governs the session that follows it.
- Stale documentation left over from 0.2.0. `AGENTS.md` described the release
  workflow as creating a notes-only GitHub Release, from before it built,
  published to PyPI and attached the artifacts; `CONTRIBUTING.md` described
  `make lint` as checking `VERSION` against `CHANGELOG.md` alone, from before it
  also checked every subproject; and the `pdf2md` and `web2md` guides still sent
  their output to `make wiki`, a target `md2okf` replaced. `CONTRIBUTING.md`
  also documents the per-platform venv rule that until now only `AGENTS.md`
  carried, so a contributor on Linux is told before `uv` writes the wrong one.

### Removed

- **`scripts/sync-descriptions.py`.** It rewrote each `index.md` entry's
  description from the linked page's frontmatter, from before `okfctl` owned
  the indexes. `okfctl index build` now regenerates them inside the sandbox, so
  the script was a second implementation of a job already done — and an unwired
  one: nothing in `make`, the kit or any skill invoked it.

## [0.2.0] - 2026-09-20

### Added

- **`md2okf`, one command in place of `make wiki` and three launcher scripts.**
  Files or folders in, a directory out: `md2okf [-o DIR] [--spec FILE] [-n N]
  [--fresh] [--dry-run] [-q|-v] [FILE|DIR ...]`. stdout carries one TSV row per
  document (`path  iterations  hash-before  hash-after`) and nothing else,
  diagnostics go to stderr, and the exit status is the verdict: 0 every
  document converged (a hash-stable first pass included — that is the
  idempotent re-run), 1 the run failed, 2 usage or environment, decided before
  any work starts. The driver is stdlib-only Python with a pytest suite that
  fakes the one `sbx` seam, so the Ralph loop, the prompts and the event
  rendering are testable without a paid sandbox run.
- **A workbench, so one sandbox serves any input and output.** sbx fixes a
  sandbox's mounts at creation, so runs are staged through
  `$XDG_STATE_HOME/md2okf/work` instead: inputs copied in, the target wiki
  mirrored in before the run and back out after every iteration, the five mount
  paths never changing. The sandbox is rebuilt only when the kit it was built
  from changes, when the recorded configuration no longer matches, or on
  `--fresh` — and one that cannot be proven to belong to the driver is reported,
  never deleted.
- **Publication to PyPI.** `md2okf` is now installable with
  `uv tool install md2okf` (or runnable with `uvx md2okf`), with the sandbox
  kit, `SPEC.md` and the four helper CLI projects carried inside the wheel, so
  it compiles without a checkout. A `vX.Y.Z` tag builds the wheel and sdist
  once, publishes them by trusted publishing — OIDC, no stored token — and then
  creates the GitHub Release with those same artifacts attached.
- `NOTICE-OKF-SPEC.md` and `LICENSE-OKF-SPEC.txt`, recording that the bundled
  `SPEC.md` is the Open Knowledge Format v0.2 specification, taken verbatim from
  `GoogleCloudPlatform/open-knowledge-format` and licensed Apache-2.0. Both ship
  in the wheel and the sdist beside md2okf's own MIT licence. Package metadata
  gains the README as its long description, an SPDX licence expression, project
  URLs and classifiers, and the sdist no longer carries the agent-tool
  directories and their vendored third-party skills.
- `make install` (the command onto PATH), `make test-md2okf` (the driver suite,
  also in `make test`) and `make dist` (wheel and sdist, plus a smoke test of
  the built artifact from outside the checkout). CI gains `test-md2okf` and
  `build-package` jobs.
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

- Host requirements are now `sbx` and `uv`; `make` and `jq` are developer tools
  rather than user ones. The Quickstart is `uv tool install .` then
  `md2okf my-document.md`.
- The writable state mount narrows from the state root to
  `$XDG_STATE_HOME/md2okf/sessions`, so the host-side ownership marker and the
  staged read-only inputs are outside the sandbox's namespace. The environment
  variable the guest helper reads is renamed `MD2OKF_STATE_DIR`, and the
  per-user lock moves to `/tmp/md2okf-<uid>.lock`, outside the configurable
  state directory.
- `merkleokf --nolog` now skips the root `log.md` whatever the wiki directory is
  called, instead of only when it is named `okf` — the hash call is what decides
  convergence, and `-o` can name any directory.
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

- The shell compile path: `scripts/compile-okf.sh`, `scripts/bash.sh`,
  `scripts/pi.sh`, `scripts/lib/sandbox-mounts.sh` and the `make wiki` target.
  `md2okf` replaces the first, `sbx exec -it md2okf -- bash` (or `-- pi`) the
  next two, and `src/md2okf/workbench.py` the mount list. `jq` and `make` leave
  the user-facing requirements with them.
- `.env` and `.env.example`. A tool that is not tied to a checkout has no
  repository to read a `.env` from, so an exported absolute `XDG_STATE_HOME` is
  the one knob, with `~/.local/state` as the default.
- `tests/test-sandbox-mounts.sh`, whose subject moved into the driver: the
  state-path and mount-list cases are `tests/test_workbench.py`, and its check
  that the agent's runtime instructions never call the wiki `../okf` is
  `tests/test_kit.py`.
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
