# Agent Instructions

> **Scope:** these are instructions for **development agents** working *on* this
> repository (e.g. Claude Code) — how to build, lint, and validate it. They are
> not Pi's task instructions. Pi runs inside the sandbox with `okf/` as its
> workspace and cannot read this repository-level file; if you are Pi, your
> role and rules live in your own agent config (`~/.pi/agent/AGENTS.md`, authored
> from `kits/pi/files/home/.pi/agent/AGENTS.md`) — nothing here changes that.
> Host MCP (Context7 / GitHub in `.mcp.json`) is for Cursor/Claude on the host
> only. Sandbox Pi gets Context7 through the native `@upstash/context7-pi`
> package installed by the kit, not via MCP.

## Git

Never run `git commit` or `git push` (including pushing tags) in this repo.
Stage changes, draft the commit message, and hand it to the user — they run
the commit and push themselves.

## Python environments

A virtual environment is not portable across platforms: it pins an absolute
interpreter path, a platform-specific `home` in `pyvenv.cfg`, and wheels
compiled for one OS and architecture. The host is macOS while development
sandboxes are Linux, and a direct-mode sandbox bind-mounts the same tree, so one
`.venv/` cannot serve both — whichever side synced last wins and the other
breaks. `uv.lock` is the portable artifact: share the lock, never the venv.

On Linux, set `UV_PROJECT_ENVIRONMENT` before any `uv` command, so the default
`.venv/` stays macOS-only. In a Docker Sandbox that means the persistent
environment file:

```bash
echo 'export UV_PROJECT_ENVIRONMENT=.venv-linux' >> /etc/sandbox-persistent.sh
```

Keep the value **relative**. The repo holds seven independent uv projects, and a
relative path gives each its own `.venv-linux/`, where an absolute one would
collapse all seven into a single shared environment and break the zero-overlap
rule. `make` exports this itself on Linux, so those targets are correct either
way — bare `uv run` and `uv sync` are not. A venv left behind by the other
platform needs no cleanup: uv detects the dangling interpreter and rebuilds it.

## Repository map

md2okf compiles Markdown into an OKF wiki with the Pi coding agent: one Pi run
per source document, folded into the wiki. The `md2okf` command is the host
driver, at the repository root (`pyproject.toml`, `src/md2okf/`); it takes any
files or folders and writes to any `-o` directory, staging both through a fixed
workbench under `$XDG_STATE_HOME/md2okf` so one sandbox serves every run. In
this repository the defaults are `md/` in and `okf/` out: `md/` is tracked;
`okf/` is gitignored in full — the wiki is generated output.

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

The agent framework is selected by `MD2OKF_AGENT` (`src/md2okf/agents.py`);
`pi` (the default), `claude` and `codex` are registered. Where each agent
reads its instructions differs, and was measured, not assumed: Pi from
`~/.pi/agent/AGENTS.md`, Claude Code from the kit's `agentInstructions` (sbx
writes `../CLAUDE.md`), Codex from `~/.codex/AGENTS.md` (it ignores files
outside a git project). Each kit's `README.md` says why. Each agent has its own kit
(`kits/<agent>/`), sandbox (`md2okf-<agent>`) and workbench
(`$XDG_STATE_HOME/md2okf/<agent>/`); everything agent-specific — command lines,
first-turn prompt, credential check, sbx minimum, event-stream parser
(`src/md2okf/protocols/<agent>.py`) — lives on its `Agent`, never in the
generic modules. An agent is registered only once its kit ships.

Pi runs in one runtime: the Docker Sandbox (sbx) kit rooted at `kits/pi/`.
Its spec is `kits/pi/spec.yaml` and its Pi config (`AGENTS.md`,
`settings.json`, `models.json`, `skills/`) lives in
`kits/pi/files/home/.pi/agent/`. The agent has `bash`, so it lints
its own output and dates its log entries, and the OpenRouter key stays outside
the VM (proxy-managed by sbx). Config is copied in at kit build time, so edits
only land in a fresh sandbox — which `md2okf` builds when the kit's hash stops
matching the running sandbox's, or at once on `--fresh`. The `files/`
level is fixed by the Sandbox Kit schema and cannot be renamed or removed. The
kit uses the finalized kit-spec v2 grammar and requires sbx 0.43.0 or newer.

Within the config, the split is: `AGENTS.md` holds what every task must respect
(OKF conventions, the writable directories, `SPEC.md` outranking both), while
each task's procedure lives in its own skill directory under `skills/`. Task
skill today: `compile-okf`. Tool skills: `inspect-md`, `inspect-okf`, `size-okf`,
`merkle-okf`, `curate-okf` — **a tool gets a skill, not an `AGENTS.md`
section.** Helper skill:
`context7-docs`, installed by the kit via `@upstash/context7-pi`. A new task gets
a new skill, not more rules in `AGENTS.md`.

`tests/` holds the driver's pytest suite (offline: `conftest.py` fakes the one
`sbx` seam; `test_kits.py` holds every `kits/*/` to the shared authoring
contract, its own provenance and byte-identical helpers) and two shell suites
that pytest cannot replace — the paired live-sandbox check (`test-sandbox.sh`,
which asks the driver for a sandbox, runs `test-sandbox-guest-<agent>.sh` inside
the VM, then checks from the host what only the host can see) and
`test-mount-state.sh` for the guest-side bind helper and the `md2okf-agent`
wrapper.

Every agent process the driver starts — each compile turn and `md2okf --agent`
— runs through the kit's `md2okf-agent` wrapper
(`files/home/.local/lib/md2okf/md2okf-agent.sh`, identical in every kit, put on
PATH by a per-kit `setup.files` shim naming the agent's native trace
directory). `sbx exec` bypasses the kit entrypoint, so per-process setup goes in
the wrapper, never the entrypoint. The agent's flags stay in `agents.py`.

## Commands

```bash
make lint                # markdownlint, jq, yamllint, shellcheck, cspell, ruff;
                         # also VERSION ↔ CHANGELOG.md and VERSION ↔ every
                         # subproject (scripts/sync-versions.sh --check)
make validate            # validate every sandbox kit spec (runs scripts/validate-spec.sh)
make test-shell          # host test for the session bind helper and md2okf-agent
make test-web2md         # pytest, the web2md scraper suite (offline)
make test-clis           # pytest, the four host CLI suites (offline)
make test-md2okf         # pytest, the md2okf driver suite (offline, fake sbx)
make test                # all of the above plus test-sandbox
make install             # uv tool install md2okf onto PATH
make install-clis        # uv tool install the four host CLIs onto PATH
make dist                # build wheel + sdist and smoke-test the artifact
make test-sandbox        # check each agent's sandbox delivers what its kit promises
                         # (AGENT=pi for one; tests/test-sandbox.sh needs the agent)
make scrape              # fetch the website into md/ as one file (web2md)
make check-okf           # check the generated okf/ wiki (okfctl + frontmatter guard)
```

Compiling is the tool, not a make target:

```bash
uv run md2okf md/                            # compile from a clone, no install
uv run md2okf -o wikis/other docs/other/     # any input folder, any output folder
uv run md2okf --dry-run md/                  # resolve and print; no sandbox, nothing paid
uv run md2okf -n 20 md/                      # raise the per-document iteration cap
uv run md2okf -o "$(mktemp -d)" tests/fixtures/smoke.md  # cheap live smoke run
MD2OKF_AGENT=pi uv run md2okf md/            # pick the agent framework (pi is the default)
uv run python -m md2okf.sandbox              # ensure the sandbox exists, compile nothing
uv run md2okf --shell                        # ensure the sandbox, then shell into it
uv run md2okf --agent                        # ensure the sandbox, then open the agent
sbx exec -it md2okf-pi -- bash               # the same, minus the ensure step
sbx rm --force md2okf-pi                     # discard it; the next run rebuilds
./scripts/sync-versions.sh                   # write VERSION into every subproject
./scripts/release-notes.sh X.Y.Z             # print CHANGELOG.md notes for a release
./scripts/check-release-tag.sh vX.Y.Z        # assert a tag matches VERSION
```

`VERSION` is the one version for the whole repository. The root project reads it
directly (`[tool.hatch.version]`), and every other project — the four host CLIs,
`web2md`, `pdf2md` — carries a literal that `./scripts/sync-versions.sh` writes
and refreshes each `uv.lock` for. A literal rather than a dynamic read of
`../../VERSION`, because the CLIs are also built from a staged copy that holds
only `pyproject.toml` and `src/` (`stage_clis`), where a path above the project
root does not exist. Bump `VERSION`, then run the script; `make lint` fails on
any project left behind.

`--shell` and `--agent` are for inspecting the sandbox, not for authoring. They
do not restage a compile run: helper CLIs are refreshed, an empty `work/SPEC.md`
gets the bundled spec, and prior workbench content otherwise remains in place.
The next compile replaces `work/okf`; Pi transcripts persist under `sessions/`.
The command holds the workbench lock until the session exits, so a concurrent
compile or `--fresh` invocation is refused. Only `--fresh` combines with them —
every other compile option is refused rather than ignored, unless its value
happens to equal the default. Both need a terminal on stdin, and refuse before
touching the sandbox without one.

The agent's credential check (`Agent.check_credentials`) runs after every
create *and* every reuse. A compile, `--agent` and `python -m md2okf.sandbox`
refuse with exit 2 and the agent's remedy when it fails; `--shell` prints the
remedy as a warning and opens anyway, because a diagnostic shell is most useful
exactly then.

`make check-okf` is host-only and needs a generated `okf/` plus `okfctl` on
PATH (`brew install cwest/tap/okfctl`); it sits outside `make lint` and outside
CI because `okf/` is gitignored output, and the driver does not call it.
`make test-sandbox` is host-only for the other reason — it needs an sbx runtime
— and asks the driver for a sandbox, reusing the existing one when it is still
ours and still matches. `md2okf` takes `OPENROUTER_API_KEY` from `sbx secret`,
not from your shell (see the README for the two-step setup). Anything that
touches a sandbox — `md2okf`, `make test-sandbox`, `sbx exec` — needs an active
`sbx login` session; `make validate`, `make dist` and the pytest suites are
static and do not.

Pushing a `vX.Y.Z` tag triggers `.github/workflows/release.yml`: it verifies the
tag against `VERSION`, builds the wheel and sdist once, publishes them to PyPI
by trusted publishing, and then creates a GitHub Release whose notes are the
matching `CHANGELOG.md` section and whose assets are those same artifacts. See
[CONTRIBUTING.md](CONTRIBUTING.md#releasing).

## Always validate the sandbox kit spec before finishing

Whenever you change anything under `kits/` or `scripts/*.sh`, you MUST validate the
Sandbox Kit specs before considering the task complete:

```bash
./scripts/validate-spec.sh   # or: make validate
```

This checks every `kits/*/spec.yaml` against the current Sandbox Kit schema (a
static schema check — no Docker, login, or network required). The same check runs
in CI (see `.github/workflows/ci.yml`, job `validate-kit`), so validating locally
first avoids CI failures. Do not finish a task until it passes. If the `sbx` CLI
is not installed, install it with `brew install docker/tap/sbx`. If validation
reports unknown fields, upgrade an older installation with `brew upgrade sbx`.

`make validate` only checks the spec statically. If you changed what the sandbox
installs or what it carries in `kits/pi/files/`, also run `sbx rm --force md2okf-pi &&
make test-sandbox AGENT=pi` — on its own `make test-sandbox` reuses whatever sandbox
is running, which may predate your edit.

## Skills

- `context7-docs` — fetch current library/framework docs before writing code
  against one.
- `debug-third-party` — check for a known upstream bug before working around
  an error that looks like it's from a dependency.
