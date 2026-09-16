<!-- cspell:words argparse workbench uvx pipx hatchling sdist okflintrc GHCR Sigstore SLSA Linuxbrew getopts importlib flock progfile subcommands DEVNULL -->

# Proposal: package and ship `md2okf` as a primitive

## Context

`.claude/plans/interface-redesign.md` settled the command surface — one
`md2okf` command in place of `make wiki` and three launcher scripts — and put
one thing out of scope: a standalone tool that runs against any folder, with
the kit, `SPEC.md` and the helper CLIs bundled. That is now the requirement.
`md2okf` should be a primitive in the `grep`/`awk` sense: one command, files
in, a directory out, flags for the few knobs, exit codes that mean something,
no subcommands, no project root, nothing to `cd` into. Then it sits in
pipelines (`web2md … | md2okf -o okf/`), loops (`for f in …; do md2okf -o
"wikis/$n" "$f"; done`), other people's Makefiles, and CI.

This document decides two things: the shape of the primitive, which every
option shares, and how to package and ship it — three options, one
recommended. The proposal's behaviour list ("Behaviour to carry over
verbatim") still applies and is not repeated.

## The primitive

`grep PATTERN [FILE…]` and `awk [-f PROGFILE] [FILE…]`: the program is fixed
or comes from `-f`, inputs are files or stdin, output goes to stdout,
diagnostics to stderr, and the exit status is the verdict. Mapped onto
md2okf:

```text
md2okf [-o DIR] [--spec FILE] [-n N] [--fresh] [--dry-run] [-q | -v] [FILE|DIR ...]
md2okf --version | --help
```

| | `grep` / `awk` | `md2okf` |
| --- | --- | --- |
| program | the pattern; `awk -f progfile` | fixed (the `compile-okf` skill). `--spec FILE` swaps the OKF spec, awk's `-f`; default is the bundled `SPEC.md` |
| inputs | files; `-` or none means stdin | Markdown files, in the order given; a DIR means its `*.md`, sorted; `-` or no argument means stdin (refused on a TTY with usage, exit 2 — a paid, minutes-long run should not start on an idle terminal) |
| output | stdout | the wiki in `-o DIR` (default `./okf`, created if missing). stdout carries one TSV line per document: `path  iterations  hash-before  hash-after`, so a pipeline can tell what happened |
| diagnostics | stderr | stderr: the `Compiling … (iteration n)` and `hash -> hash` lines. `-v` adds Pi's tool calls and prose (today's `jq` view); `-q` prints nothing |
| exit status | 0 / 1 / 2 | 0 every document converged; 1 a document hit the iteration cap — its partial work is on disk and named on stderr; 2 usage or environment (`sbx` missing or < 0.43, not logged in, key not proxy-managed, another run holds the sandbox) |
| state | none | one long-lived sandbox named `md2okf` (the name the `sbx secret` workaround is keyed to). Built on first use, reused after, rebuilt automatically when the bundled kit changes, and on `--fresh` |

Not in the surface: `shell`, `pi`, `sandbox up/down`, `doctor`, `lint`. Those
were repository chores, not the tool's job. `sbx exec -it md2okf -- bash` and
`-- pi` are one-liners once a sandbox exists; the environment checks run on
every invocation and fail with the fix in the message, which is what `doctor`
was for; `okf-lint` has its own CLI. `RALPH_MAX` becomes `-n`; `.env` goes —
a tool that is not tied to a checkout has no repository to read a `.env` from,
so `XDG_STATE_HOME` is the one knob, with `~/.local/state` as the default.

### Why it needs a workbench

sbx fixes a sandbox's mounts when the sandbox is created, `sbx run --name`
re-attaches with the old mounts, and a build takes minutes. A primitive that
takes arbitrary paths cannot mount them directly: the second `-o` would either
rebuild the sandbox every time or silently write into the first wiki. So the
tool owns a fixed staging layout under its state directory and syncs through
it:

```text
~/.local/state/md2okf/       $XDG_STATE_HOME/md2okf, as today
  sessions/                  Pi sessions, bind-mounted as today (mount-state.sh)
  work/
    okf/                     primary mount, rw   <- mirrored from -o DIR before the run,
                                                    back to it after every iteration
    md/                      mount, ro           <- the inputs, copied by basename
                                                    (stdin -> stdin.md; a basename clash is exit 2)
    scripts/                 mount, ro           <- the four CLI projects, copied from the package
    SPEC.md                  mount, ro           <- --spec, or the bundled copy
  sandbox-fingerprint        kit tree hash + tool version the sandbox was built from
  lock                       flock: one run at a time; a second invocation exits 2
```

This reproduces exactly the sibling layout the kit expects — `../md`,
`../scripts`, `../SPEC.md`, and a working directory *named* `okf`, which
`merkleokf --nolog` needs — so **the kit does not change**. The wiki copy is
Markdown-sized. Mirroring back after every iteration means an interrupted run
leaves the last completed pass in `-o DIR`. `.okflintrc.json` is seeded from
the bundled default when `-o DIR` has none, and the user's copy wins after
that.

## Three ways to package and ship it

Every option bundles the same four assets — the kit, `SPEC.md`, the default
`.okflintrc.json`, and the four CLI projects (`pyproject.toml` + `src/`) —
because the tool must work outside a checkout. They differ in what the
artifact is, what the host needs, and what the release publishes.

### Option A — a Python wheel on PyPI: `uv tool install md2okf`

A stdlib-only project at the repository root, laid out like the four helper
CLIs, with the assets carried as package data. `uv build` produces a pure
wheel and an sdist; the release workflow publishes them to PyPI by trusted
publishing (OIDC, no stored token) and attaches them to the GitHub Release.

```bash
uv tool install md2okf                                 # from PyPI
uvx md2okf -o okf/ doc.md                              # no install at all
uv tool install git+https://github.com/lars20070/md2okf  # straight from source, any ref
uv tool install md2okf==0.2.0                          # pinned
```

The driver is Python: argparse, native JSON for Pi's event stream (no `jq`),
`subprocess` for `sbx`, `os.execvp` for nothing — there are no interactive
subcommands left. `importlib.resources` locates the assets in the installed
wheel; in a checkout it falls back to `kits/md2okf/`, `SPEC.md`,
`okf/.okflintrc.json` and `scripts/`, so `uv run md2okf` works during
development without a build.

### Option B — a Homebrew tap: `brew install lars20070/tap/md2okf`

A tarball per release — `bin/md2okf` (Bash, the four scripts folded into one
with a `while … case` option loop) plus `share/md2okf/{kit,SPEC.md,okflintrc.json,clis}`
— attached to the GitHub Release, and a formula in a second repository,
`lars20070/homebrew-tap`, that unpacks it and declares
`depends_on "docker/tap/sbx"` and `depends_on "jq"`. The release workflow
uploads the tarball and opens a pull request against the tap with the new
`url` and `sha256`. Linux gets the same tarball with an `install.sh` into
`~/.local` (or Linuxbrew).

```bash
brew tap lars20070/tap && brew install md2okf          # macOS; pulls in sbx and jq
curl -fsSL https://github.com/lars20070/md2okf/releases/latest/download/install.sh | sh   # Linux
```

### Option C — the sandbox kit as the artifact: `sbx kit push` to GHCR

The Ralph loop moves *into* the kit as `files/home/.local/bin/md2okf-compile`
(POSIX `sh`: the loop, `pi --mode json </dev/null | jq`, the `merkleokf` hash
— every piece of it already runs inside the VM), `SPEC.md` and the CLI
projects are copied into `files/`, the iteration cap becomes a kit `arg`, and
the loop script becomes the kit's `entrypoint`. The release workflow runs
`sbx kit push ./kits/md2okf ghcr.io/lars20070/md2okf:X.Y.Z --sign`, which
signs the manifest with Sigstore and attaches SLSA provenance for free. There
is no host driver; the host command is `sbx run`, wrapped in a shell function
the README hands out.

```bash
sbx run --name md2okf -e SBXAGENT_STATE_DIR="$HOME/.local/state/md2okf" \
  ghcr.io/lars20070/md2okf:0.2.0 ./okf ./md:ro "$HOME/.local/state/md2okf" -- ../md/doc.md
sbx run "git+https://github.com/lars20070/md2okf.git#ref=v0.2.0&dir=kits/md2okf" …   # no registry
```

## Features

| | A: PyPI wheel | B: Homebrew tap | C: OCI kit on GHCR |
| --- | --- | --- | --- |
| Install | `uv tool install md2okf`; `uvx md2okf` with no install | `brew install lars20070/tap/md2okf` | none — `sbx run ghcr.io/…` behind a shell function |
| Host requirements | `sbx`, `uv` (or `pipx` / Python ≥ 3.12) | `sbx`, `jq` — brew installs both as dependencies | `sbx` only |
| Artifact | pure-Python wheel + sdist, ~300 KB | tarball + formula (two things to keep in step) | OCI artifact: tar+gzip layer, spec in the manifest |
| Channel | PyPI, GitHub Release assets, `git+https` URL | GitHub Release + a second repository (the tap) | GHCR; or `git+https://…#ref=&dir=` with no registry |
| macOS / Linux | identical | macOS native; Linux via Linuxbrew or `install.sh` | identical |
| Pinning | `md2okf==0.2.0` | versioned formula or tarball URL | `:0.2.0` tag, immutable digest |
| Signing / provenance | PyPI attestations via trusted publishing | `sha256` in the formula | Sigstore signature + SLSA provenance, built into `sbx kit push` |
| Driver | Python, argparse, `pytest` | Bash, hand-rolled options and help | POSIX `sh` inside the VM |
| Interface | `md2okf [-o DIR] FILE…` | same surface, hand-written | `sbx run`'s: positional mounts, `--`, `--kit-arg` |
| Any paths, one sandbox | yes — workbench | yes — workbench, in Bash | **no** — mounts fixed at creation; nothing on the host to notice a mismatch |
| stdin, `--dry-run`, TSV summary | yes | yes, more code | no host process to do it |
| Loop testable offline | `pytest` with a fake `sbx` | no | no |
| Tool ↔ kit drift | impossible: the kit is inside the wheel | impossible: inside the tarball | n/a: the kit *is* the tool |
| Release automation | `uv build` + `uv publish` in `release.yml` | tarball upload + formula-bump PR | `sbx kit push --sign` in `release.yml` |
| Repository impact | root `pyproject.toml`; four scripts retire | scripts stay; `packaging/` + tap repo appear | kit gains the loop; host scripts retire |
| Effort | 2–3 days | ~2 days, plus tap upkeep per release | ~1 day |

## Pros and cons

### A: PyPI wheel

**Pros.** Same layout, install mechanism, ruff rules and pytest harness as the
four helper CLIs, so `make lint` and CI extend by a line each. A real CLI:
`--help`, validated arguments, stdin, `--dry-run`, consistent exit codes. The
loop, the prompts, the hash comparison, the workbench mirroring and the
`stdin=DEVNULL` guard all become unit tests against a fake `sbx` — today they
are protected by comments. `jq` and `make` leave the user's requirements. The
wheel is pure Python, so one artifact serves macOS and Linux, and
`uv tool install git+https://…` works with no registry at all. A Homebrew
formula can wrap this same wheel later (`brew` has first-class support for
Python-package formulae), so A does not close the door on B.

**Cons.** `uv` (or `pipx`) joins `sbx` as a host requirement — it already is
one for `make install-clis` and `make scrape`, so the practical cost is a line
in the README. PyPI needs a one-time project registration and trusted
publisher setup by the owner. Force-including non-Python assets into a wheel
is a packaging detail that must be verified by listing the wheel, and the
in-checkout fallback is a second code path (one function, tested).

### B: Homebrew tap

**Pros.** `brew install` is exactly how macOS users already get `sbx`, so one
package manager covers both, and the formula's `depends_on` makes it
impossible to install `md2okf` without `sbx`. No Python or `uv` on the host.
Of the three, installing it feels most like installing `grep`.

**Cons.** The driver is Bash: every complaint the interface proposal made
about hand-rolled option parsing and an untested loop carries over, or the
formula depends on `python@3.12` and B becomes A with a worse channel. A
second repository to maintain and a sha256 to bump on every release. Linux —
where `sbx` is installed with `apt`, not `brew` — is second-class. `jq` stays.
Two artifacts (tarball, formula) to keep in step instead of one.

### C: OCI kit

**Pros.** Zero host install beyond the one thing every option needs, `sbx`.
Signing and provenance are free. The kit is the natural unit of an sbx
project, and Docker's own `sbx-kits-contrib` ships this way. The loop runs
where `pi` and `merkleokf` already are, so no host process parses JSON. The
`git+https` form works before any registry exists. Cheapest to build.

**Cons.** The interface is `sbx run`'s, not md2okf's — positional mount soup,
`--` separation, kit args — which is the opposite of the brief, and the moment
a wrapper is written to fix that, the wrapper needs shipping and we are back
in A or B. The decisive one: with no host process, nothing can notice that
the sandbox named `md2okf` was created with different mounts, so pointing it
at a second wiki silently writes into the first. That is a correctness trap,
not an ergonomic one, and it defeats "a building block in a wide variety of
use cases". Session state needs `-e SBXAGENT_STATE_DIR` and a fifth positional
on every call. No `--dry-run`, no stdin, no TSV.

## Recommendation: A

Ship `md2okf` as a pure-Python wheel installed with `uv tool`, the kit and the
other assets inside it, published to PyPI and attached to the GitHub Release.
It is the only option that gives the primitive its own interface, puts the
loop under test, removes `jq` and `make` from the user's path, works
identically on both platforms sbx supports, and reuses a convention this
repository already enforces four times over. B is a good *second channel*
once the wheel exists — a formula that wraps it — and should be added then,
not now. C mistakes the artifact for the product: the kit is what runs, but a
primitive needs a host-side command to own paths, stdin and exit codes.

## Implementation plan

### Layout

```text
pyproject.toml              name = "md2okf"; version from VERSION (hatch regex source);
                            [project.scripts] md2okf = "md2okf.cli:main"; hatchling;
                            requires-python >= 3.12; no dependencies; ruff + pytest as the CLIs
src/md2okf/
  __init__.py               __version__ from importlib.metadata
  cli.py                    argparse: the one command; main() returns the exit code
  resources.py              kit_dir(), spec_md(), okflintrc(), clis_dir(): the installed
                            package's copies, else the checkout's (kits/md2okf, SPEC.md,
                            okf/.okflintrc.json, scripts/<cli>)
  workbench.py              state dir (XDG precedence, minus .env), work/ layout, mirror
                            in/out, lock, .okflintrc seeding, kit fingerprint
  sandbox.py                the one sbx seam: present/version/login checks, exists(),
                            create(), remove(), exec(argv, stdin=DEVNULL, stream=…),
                            key check; `python -m md2okf.sandbox` ensures one (maintainers)
  compile.py                documents(), the two prompts, the Ralph loop, hash, TSV rows
  events.py                 one `pi --mode json` line -> text (replaces the jq filter)
tests/
  test_cli.py test_workbench.py test_sandbox.py test_compile.py test_events.py
  test_resources.py test_package.py            (pytest; the shell tests keep their test-*.sh names)
```

Root project, not `md2okf/`: the repository name is the tool name, and a root
`pyproject.toml` is what makes `uv tool install git+https://github.com/lars20070/md2okf`
and `uvx --from git+… md2okf` work with no registry. `CONTRIBUTING.md`'s
"no project at the root" rule was there to keep `uv run` and the lint
boundaries per directory; `uv run --project web2md` and the per-directory
`[tool.ruff]` tables keep doing that, and the wheel build lists
`src/md2okf` explicitly so `web2md/`, `pdf2md/` and `md/` cannot leak in.

Wheel contents, via `[tool.hatch.build.targets.wheel.force-include]`:
`kits/md2okf` → `md2okf/kit`, `SPEC.md` → `md2okf/SPEC.md`,
`okf/.okflintrc.json` → `md2okf/okflintrc.json`, and for each CLI
`scripts/<cli>/pyproject.toml` and `scripts/<cli>/src` → `md2okf/clis/<cli>/…`
(tests, `uv.lock`, README excluded). Verified by `tests/test_package.py`,
which builds the wheel and asserts those paths exist and no `.DS_Store`,
`tests/` or `uv.lock` does. Load the `context7-docs` skill for hatchling's
force-include and version-source syntax before writing the file.

### What to carry over, and from where

- `scripts/compile-okf.sh:28-32` — the two prompt strings and the "append
  the continuation from iteration 2" rule → `compile.py`.
- `scripts/compile-okf.sh:83-86` — `merkleokf --nolog -L 0 <abs okf>`, third
  line, first field → `compile.py`; the absolute path is the workbench's
  `work/okf`.
- `scripts/compile-okf.sh:89-100` — the jq filter → `events.py`, same three
  cases, 120-character cut.
- `scripts/compile-okf.sh:102-130` — the loop and cap → `compile.py`;
  `RALPH_MAX` becomes `-n`, default 10.
- `scripts/compile-okf.sh:63-67` — `stdin=subprocess.DEVNULL` on every
  non-interactive `sbx exec … pi`, with the reason in a comment and a test.
- `scripts/lib/sandbox-mounts.sh:39-48` — absolute-or-unset `XDG_STATE_HOME`,
  `mkdir -p`, mode `0700` → `workbench.py`. Drop the `.env` layer.
- `scripts/lib/sandbox-mounts.sh:56-62` — mount order (`okf` primary, then
  `md:ro`, `scripts:ro`, `SPEC.md:ro`, state rw) → `sandbox.create()`, with
  the workbench paths.
- `scripts/bash.sh:31-36` — `sbx ls -q | grep -qx` existence check, `sbx run
  --detached --name md2okf -e SBXAGENT_STATE_DIR=… <kit> <mounts>` →
  `sandbox.py`. Add the fingerprint comparison: rebuild when the recorded
  kit hash or tool version differs, or on `--fresh`.
- `scripts/compile-okf.sh:34-38` — the `brew install docker/tap/sbx` hint,
  plus new checks: `sbx version` ≥ 0.43.0, `sbx ls` succeeds (logged in),
  and after creation `sbx exec md2okf -- sh -lc 'echo "$OPENROUTER_API_KEY"'`
  prints `proxy-managed`, else exit 2 with the README's two `sbx secret`
  commands in the message.
- `kits/md2okf/` — untouched. The workbench reproduces the sibling layout
  its shims and skills assume (`spec.yaml:237-272`).
- `kits/md2okf/files/home/.local/lib/md2okf/mount-state.sh` and
  `tests/test-mount-state.sh` — untouched; guest-side.

### Repository changes

- Add `pyproject.toml`, `src/md2okf/`, the pytest suite; `uv lock`.
- Retire `scripts/compile-okf.sh`, `scripts/lib/sandbox-mounts.sh`,
  `.env.example`, the `.env` lines in `.gitignore` and README, and
  `tests/test-sandbox-mounts.sh` (its precedence cases become
  `tests/test_workbench.py`).
- `scripts/bash.sh`, `scripts/pi.sh`: two lines each —
  `uv run python -m md2okf.sandbox && sbx exec -it md2okf -- bash` (or `pi "$@"`).
  `tests/test-sandbox.sh`: same ensure call, then its existing `sbx exec … sh -l -s`.
- `Makefile`: `wiki` → `uv run md2okf md/` for one release, then goes; new
  `install` (`uv tool install --force .`) beside `install-clis`; new
  `test-md2okf` (`uv run --group test pytest tests`) added to `test`;
  the ruff line's glob gains the root `pyproject.toml`
  (`'pyproject.toml' '*/pyproject.toml'`).
- `.github/workflows/ci.yml`: `test-md2okf` job (pytest) and `build-package`
  job (`uv build`, then `uvx --from dist/*.whl md2okf --help`).
- `.github/workflows/release.yml`: a `publish` job after `verify` —
  `uv build`, `uv publish` with trusted publishing (`id-token: write`, the
  `pypi` environment), and `gh release upload` of `dist/*` onto the Release
  the existing job creates. Owner does once: create the PyPI project
  `md2okf` and register the repository as its trusted publisher.
- `README.md`: Requirements become `sbx` and `uv`; Quickstart becomes
  `uv tool install md2okf` then `md2okf my-document.md` (or
  `uvx md2okf …`); "How it works" gains the workbench and loses "always
  rebuilds"; Troubleshooting drops `RALPH_MAX` for `-n`; the diagram's
  driver box becomes `md2okf`.
- `CONTRIBUTING.md`: the Python-layout section (a root project now exists,
  and why), the Releasing section (there *is* a package to publish), the
  command table. `AGENTS.md`: repository map and command table.
  `kits/md2okf/README.md`: "which `make wiki` always builds" →
  "which `md2okf` rebuilds when the kit changes, or on `--fresh`".
- `CHANGELOG.md` under `[Unreleased]`: Added the `md2okf` command and the
  PyPI package; Removed the launchers, `sandbox-mounts.sh`, `.env`; Changed
  the host requirements and the sandbox reuse rule.
- `.cspell.json`: `argparse`, `uvx`, `hatchling`, `workbench`, and whatever
  the sources add.

### Staging

1. Land the package with the full command, the workbench and the tests;
   `make wiki` delegates to it. The kit and the guest-side helper do not move.
2. Retire the scripts and `.env`, port `test-sandbox-mounts.sh`, point
   `test-sandbox.sh` and the two dev scripts at `python -m md2okf.sandbox`,
   update the docs.
3. Publishing: the `build-package` CI job, the release `publish` job, PyPI
   trusted publisher registration, README install lines.

### Decisions taken here

- Root `pyproject.toml` (so `uv tool install git+…` works), not `md2okf/`.
- A staged workbench under the state directory, not direct mounts — the only
  way one sandbox serves arbitrary paths.
- No subcommands. Maintainer entry points are `python -m md2okf.sandbox` and
  plain `sbx exec`.
- stdout is a TSV summary; everything human goes to stderr.
- PyPI plus GitHub Release assets; the Homebrew formula waits until the wheel
  has shipped once.

## Verification

- `make lint` and `make validate` pass (the kit is unchanged; ruff now covers
  the root project).
- `uv run --group test pytest tests` — offline: fake `sbx` recorded per test;
  XDG precedence; mirror in/out including deletion and `.okflintrc.json`
  seeding; basename clash → 2; stdin on a TTY → 2; the cap → 1 with the
  document named; the continuation prompt from iteration 2; `stdin=DEVNULL`;
  the fingerprint rebuild rule; `events.py` against recorded Pi lines.
- `uv build`, then `unzip -l dist/md2okf-*.whl` shows `md2okf/kit/spec.yaml`,
  `md2okf/kit/files/home/.pi/agent/AGENTS.md`, `md2okf/SPEC.md`,
  `md2okf/okflintrc.json`, `md2okf/clis/merkleokf/pyproject.toml`, and no
  `.DS_Store`, `tests/` or `uv.lock`; `uvx --from dist/*.whl md2okf --help`.
- `uv tool install --force .` then, from a directory that is *not* the
  checkout, `md2okf --dry-run -o /tmp/w ~/some.md` prints the mounts,
  documents and command line without touching sbx.
- Live (paid, needs `sbx login` and the key): `sbx rm --force md2okf`, then
  `md2okf -v md/GoogleStyleGuide-abridged.md` from the checkout — the wiki
  lands in `./okf`, stdout has one TSV line, exit 0; run it again with a
  second `-o` to prove the sandbox is reused across paths; then
  `make test-sandbox` against the sandbox it built.
