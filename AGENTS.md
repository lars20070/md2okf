# Agent Instructions

> **Scope:** these are instructions for **development agents** working *on* this
> repository (e.g. Claude Code) — how to build, lint, and validate it. They are
> not Pi's task instructions. Pi runs inside the sandbox with the repo root as
> its workspace and may read this file as a project document; if you are Pi, your
> role and rules live in your own agent config (`~/.pi/agent/AGENTS.md`, authored
> from `pi/files/home/.pi/agent/AGENTS.md`) — nothing here changes that.
> Host MCP (Context7 / GitHub in `.mcp.json`) is for Cursor/Claude on the host
> only. Sandbox Pi gets Context7 through the native `@upstash/context7-pi`
> package installed by the kit, not via MCP.

## Repository map

md2okf compiles Markdown into an OKF wiki with the Pi coding agent: one source
document per file in `md/`, one Pi run per file, folded into the wiki under
`okf/`. `md/` is tracked; `okf/` is gitignored except for `okf/.okflintrc.json`,
which is tracked.

`SPEC.md` at the repo root is the OKF revision the wiki is built against — the
agent reads it at the start of every run, and it outranks any instruction file,
including the runtime agent configs. `pdf2md/` is the optional upstream step
that turns a PDF into Markdown with `marker`; it is manual and not wired into
the `make` pipeline.

`web2md/` is one upstream step: a deterministic scraper that fetches a
website into a single file under `md/`, driven by `make scrape`. Which site and
which output filename live in two constants at the top of `web2md/src/web2md.py`
(`SOURCE_URL`, `OUTPUT_FILE`). Module in `web2md/src/`, pytest suite in
`web2md/tests/`, gitignored HTML cache in `web2md/cache/`. There is no
`[build-system]`: the module is run by path and pytest imports it via
`pythonpath` in `web2md/pyproject.toml`. Run `make test-web2md` after touching
either directory; the suite is offline and needs no network.

`scripts/inspectmd/` is a third independent uv project: an installable CLI that prints a
Markdown heading map (line ranges, word counts, kebab-case slugs). The sandbox
exposes the same `inspectmd` command via a `setup.files` shim. Own
`pyproject.toml`, `uv.lock`, ruff and pytest — nothing shared with `web2md/` or
`pdf2md/`.

`scripts/inspectokf/` is a fourth independent uv project: an installable CLI that prints
a wiki directory tree by wrapping `tree` (default path `okf/`, unlimited depth
unless `-L`/`--level` caps it). The sandbox exposes `inspectokf` the same way.
Own `pyproject.toml`, `uv.lock`, ruff and pytest. Both inspect CLIs spell the
depth cap `-L`/`--level`.

`scripts/sizeokf/` is a fifth independent uv project: an installable CLI that reports
Markdown content **word counts** per file and per folder (recursive), **excluding
YAML frontmatter**. Same `-L`/`--level` depth cap as the inspect CLIs. It carries
its own `strip_frontmatter` rather than importing `inspectmd`'s, under the
zero-overlap rule; the two are pinned by tests on both sides. The sandbox
exposes `sizeokf` through the same `setup.files` shim. Own `pyproject.toml`,
`uv.lock`, ruff and pytest.

`scripts/merkleokf/` is a sixth independent uv project: an installable CLI that prints a
Merkle hash tree — a hash per `*.md` file and per directory — so a change to any
page moves its parents' hashes and nothing else. Same `-L`/`--level` cap as the
other CLIs; also accepts a single file. It hashes **raw bytes**, deliberately the
opposite of `scripts/sizeokf/`, which strips frontmatter: `merkleokf` answers "did this
change", `sizeokf` answers "how much prose is here", and they share no code.
Digests display as 12 hex characters; full digests are computed internally. The
sandbox exposes `merkleokf` through the same `setup.files` shim. Own
`pyproject.toml`, `uv.lock`, ruff and pytest.

Host install for these four CLIs is `make install-clis`; run `make test-clis`
after touching any of them.

Pi runs in one runtime: the Docker Sandbox (sbx) kit rooted at `pi/`. Its spec is
`pi/spec.yaml` and its Pi config (`AGENTS.md`, `settings.json`, `models.json`,
`skills/`) lives in `pi/files/home/.pi/agent/`. The agent has `bash`, so it lints
its own output and dates its log entries, and the OpenRouter key stays outside
the VM (proxy-managed by sbx). Config is copied in at kit build time, so edits
only land in a fresh sandbox — which `make wiki` always builds. The `files/`
level is fixed by the Sandbox Kit schema and cannot be renamed or removed. The
kit uses the finalized kit-spec v2 grammar and requires sbx 0.38.0 or newer.

Within the config, the split is: `AGENTS.md` holds what every task must respect
(OKF conventions, the writable directories, `SPEC.md` outranking both), while
each task's procedure lives in its own skill directory under `skills/`. Task
skill today: `compile-okf`. Tool skills: `inspect-md`, `inspect-okf`, `size-okf`,
`merkle-okf` — **a tool gets a skill, not an `AGENTS.md` section.** Helper skill:
`context7-docs`, installed by the kit via `@upstash/context7-pi`. A new task gets
a new skill, not more rules in `AGENTS.md`.

`tests/` holds shell tests for that sandbox, in pairs: a host-side script
(`test-sandbox.sh`, which owns the sandbox and calls `sbx`) and the POSIX `sh`
script it runs inside the VM (`test-sandbox-guest.sh`).

## Commands

```bash
make lint                # markdownlint, jq, yamllint, shellcheck, cspell, ruff
make validate            # validate the sandbox kit spec (runs scripts/validate-spec.sh)
make test-web2md         # pytest, the web2md scraper suite (offline)
make test-clis           # pytest, the four host CLI suites (offline)
make install-clis        # uv tool install the four host CLIs onto PATH
make test-sandbox        # check the sandbox delivers what pi/spec.yaml promises
make scrape              # fetch the website into md/ as one file (web2md)
make wiki                # compile the OKF wiki via the sandbox runtime
make lint-okf            # lint the generated okf/ wiki (okf-lint via pnpm dlx)
```

```bash
./scripts/bash.sh                            # shell into the existing sandbox
./scripts/pi.sh                              # interactive Pi in the existing sandbox
./scripts/compile-okf.sh md/other-books      # compile a different source folder
# Per document: Ralph loop until `merkleokf --nolog -L 0` is unchanged (RALPH_MAX=10)
sbx rm --force md2okf                        # discard the sandbox, so the next run rebuilds
```

`make lint-okf` is host-only and needs a generated `okf/`; it sits outside
`make lint` and outside CI because `okf/` is gitignored output, and the driver
does not call it. `make test-sandbox` is host-only for the other reason — it
needs an sbx runtime — and reuses the existing sandbox rather than rebuilding
it. `make wiki` takes `OPENROUTER_API_KEY` from `sbx secret`, not
from your shell (see the README for the two-step setup). Runtime commands such
as `make wiki`, `make test-sandbox`, `scripts/bash.sh` and `scripts/pi.sh`
require an active `sbx login` session; `make validate` is static and does not.

## Always validate the sandbox kit spec before finishing

Whenever you change anything under `pi/` or `scripts/*.sh`, you MUST validate the Pi
Sandbox Kit spec before considering the task complete:

```bash
./scripts/validate-spec.sh   # or: make validate
```

This checks `pi/spec.yaml` against the current Sandbox Kit schema (a
static schema check — no Docker, login, or network required). The same check runs
in CI (see `.github/workflows/ci.yml`, job `validate-kit`), so validating locally
first avoids CI failures. Do not finish a task until it passes. If the `sbx` CLI
is not installed, install it with `brew install docker/tap/sbx`. If validation
reports unknown fields, upgrade an older installation with `brew upgrade sbx`.

`make validate` only checks the spec statically. If you changed what the sandbox
installs or what it carries in `pi/files/`, also run `sbx rm --force md2okf &&
make test-sandbox` — on its own `make test-sandbox` reuses whatever sandbox
is running, which may predate your edit.

## Skills

- `context7-docs` — fetch current library/framework docs before writing code
  against one.
- `debug-third-party` — check for a known upstream bug before working around
  an error that looks like it's from a dependency.
