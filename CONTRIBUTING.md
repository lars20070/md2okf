# Contributing to md2okf

This guide covers working *on* the repository: the task runner, the test
suites, the sandbox kit, and how the agent's own configuration is laid out. If
you only want to compile a wiki, [the README](README.md) is enough.

`AGENTS.md` holds the same ground rules for coding agents working on this repo.

The default branch is `master`. Base pull requests on `master` and use it in
links to files in this repository.

## Commands

```bash
make lint                # markdownlint, jq, yamllint, shellcheck, cspell, ruff,
                         # lat check (the lat.md/ knowledge graph); also
                         # VERSION ↔ CHANGELOG.md and VERSION ↔ every
                         # subproject (scripts/sync-versions.sh --check)
make validate            # build every kit with docker buildx and check it with kit-tck
make test-web2md         # pytest, the web2md scraper suite
make test-clis           # pytest, the four host CLI suites
make test-md2okf         # pytest, the md2okf driver suite
make test                # all of the above plus test-sandbox
make install             # install md2okf onto PATH (uv tool)
make install-clis        # install the four host CLIs onto PATH
make dist                # build the wheel and sdist, and smoke-test the artifact
make test-sandbox        # check the sandbox has the tools, config and key it promises
make check-okf           # check the generated wiki
make scrape              # fetch the website into md/ as one file
```

Compiling is the tool's own job, not a make target:

```bash
uv run md2okf md/                       # from a clone, no install
md2okf -o wikis/handbook docs/handbook/ # once `make install` has run
```

markdownlint needs `brew install markdownlint-cli2`; yamllint and ruff run via
`uv tool run`, and cspell and lat (`lat.md@0.13.11`) via `npx`, so none of them
needs a separate install. The lat hooks for Claude Code and Codex and the `lat`
MCP server are different: they call a bare `lat`, so install it once with
`npm install -g lat.md@0.13.11` if you use them.
`make check-okf` needs `okfctl`: `brew install cwest/tap/okfctl`.

CI (`.github/workflows/ci.yml`) runs six jobs on every pull request: `lint`,
`test-web2md`, `test-clis`, `test-md2okf`, `build-package` and `validate-kit`.
Each one reuses the matching make target, so a green
`make lint && make test-web2md && make test-clis && make test-md2okf &&
make dist && make validate` locally means a green build (`validate-kit` builds
both architectures; see below).

## Keep the knowledge graph current

`lat.md/` records why md2okf is built the way it is, linked into the code and
the tests. `make lint` runs `lat check`, which proves every link resolves, but
not that the prose is still true, and it does not notice a deleted
`# @lat:` back-reference. When you change a behaviour, rename a section or move
one, follow the review steps in `lat.md/development.md`, "Keeping the graph
current": `lat refs` finds the sections and back-references the change
touches.

## Validate the kits before you finish

Touch anything under `kits/` or `scripts/*.sh` and run `make validate`
before you call the job done. The kits are Sandbox Kit schema v3 source kits,
which `sbx kit validate` cannot read, so `make validate` builds each one with
`docker buildx` and checks the artifact with `kit-tck`. The kit frontend, pinned
by digest in each descriptor's `# syntax=` line, rejects a malformed descriptor
before it builds anything; kit-tck then checks annotations, layers, image config
and overlay ownership, and the script checks that a mixin ships nothing owned by
anyone but root and the agent.

It needs Docker with Buildx and
[kit-tck 3.0.0-m.12](https://github.com/docker/sandbox-kit-spec/releases/tag/v3.0.0-m.12),
the spec version sbx 0.54.0 bundles; it needs no sbx daemon and no login. It
creates a `docker-container` Buildx builder called `md2okf-kits` if none is
named in `KIT_BUILDER`, because exporting an OCI layout needs one. A cold run
pulls the frontend and the base images, so it is not offline. It builds
`linux/amd64` and `linux/arm64`; without QEMU, build only your own platform
with `make validate KIT_PLATFORMS=linux/arm64` (or `linux/amd64`). When `sbx`
is installed, it is first checked against the minimum below.

This is separate from how users get the kits built: `sbx` builds a local source
kit itself, with host Buildx when there is one and its own builder sandbox
otherwise, so `md2okf` users need no Docker.

Each kit is checked alone. How a mixin composes onto its workload — a file, a
credential or a hook that clashes — shows only in a live sandbox, through
`make test-sandbox`.

### The sbx minimum

`SBX_VERSION` holds one plain `X.Y.Z`: the single sbx floor for every agent.
The driver refuses an older `sbx` (the wheel carries the file, so an installed
`md2okf` enforces the same floor as a checkout), and `make validate` does the
same wherever `sbx` is installed. CI's `validate-kit` job installs exactly that
release, verified by checksum. Local installations may be newer, and those
newer releases are not tested by CI.

To raise the minimum, change all of these together:

1. `SBX_VERSION`.
2. `expected_sha256` in the `validate-kit` job of `.github/workflows/ci.yml`,
   the SHA-256 of that release's `DockerSandboxes-linux.tar.gz`.
3. The sbx version in the "Install sbx" section of `README.md`.
4. A Changed entry in `CHANGELOG.md`.
5. If the release bundles a newer kit spec: the `# syntax=` frontend digest in
   every `kits/md2okf-*/md2okf-*.yaml`, `KIT_TCK_VERSION` in
   `scripts/validate-spec.sh`, and the kit-tck version and checksum in the
   `validate-kit` job.

The test suite reads the floor from `SBX_VERSION`, so it needs no edit. The
fingerprint includes the sbx version, so every sandbox rebuilds once after an
upgrade.

### The pinned workloads

The Claude Code and Codex kits are mixins over Docker's published `claude` and
`codex` workloads, pinned in `src/md2okf/agents.py` (`CLAUDE_WORKLOAD`,
`CODEX_WORKLOAD`) by multi-platform index digest, never by a floating tag or a
bare agent name. The digest is part of the sandbox fingerprint, so bumping it
rebuilds that agent's sandbox on its next run, and nothing else does. Before a
bump, read the candidate's descriptor — what it provides, its hooks, its
agent-context and skills paths — without a daemon:

```bash
ref=docker.io/sbx/claude@sha256:<index digest>
kit-tck inspect --descriptor "$ref" | grep -v '^  - deb/'
```

Then run `make test-sandbox AGENT=claude` (or `codex`) against it.

### Piloting a kit change

`MD2OKF_SANDBOX_NAME` (maintainer-only) replaces the sandbox name for every
agent. Pair it with a temporary `XDG_STATE_HOME`, so the pilot gets its own
workbench and ownership marker and leaves your working sandbox and its
transcripts alone:

```bash
export MD2OKF_SANDBOX_NAME=md2okf-pilot XDG_STATE_HOME="$(mktemp -d)"
make test-sandbox AGENT=claude
sbx rm --force md2okf-pilot
```

Changing only the state directory leaves the usual name occupied and without
its marker, so the driver refuses it as unowned; changing only the name would
reuse the real workbench.

On a failed create, the install hooks' logs are in
`/var/log/sbx-kits/<kit>/install-<n>.log` inside the sandbox. The driver runs
`sbx run --no-input`, so a question sbx would ask — a kit's permissions needing
confirmation, say — fails with the command that answers it, and `md2okf`
prints that diagnostic.

The test suite reads the floor from `SBX_VERSION`, so it needs no edit.

`make test-sandbox` asks the other question: does each agent's sandbox
actually have every tool its kit installs, the agent config and skills from
`kits/md2okf-<agent>/files/`, and a ready credential? It needs
an `sbx login` session, and each agent's credential (see the README's
"Choosing an agent").
It asks the driver for the sandbox, the same way a compile does. The driver
reuses the sandbox it owns while its fingerprint still matches: the kit tree,
the sbx version, the mounts and the pinned workload. Reuse is fast, and nothing
a compile left behind is lost. After an edit under `kits/md2okf-<agent>/` the
fingerprint no longer matches, so the driver rebuilds the sandbox before the
checks run (minutes); there is no need to remove it first. A reused sandbox
never runs `sbx run --kit` again, though, so to prove a kit still composes from
scratch without touching your working sandbox, run the check as a pilot (see
[Piloting a kit change](#piloting-a-kit-change)). It checks every registered
agent in turn; `make test-sandbox AGENT=pi` checks one.

## Working inside the sandbox

Two flags open the sandbox, building or refreshing it first when none exists or
the running one no longer matches its `kits/md2okf-<agent>/`:

```bash
md2okf --shell   # interactive shell at the wiki root
md2okf --agent   # interactive agent session in the same sandbox
```

Only `--fresh` combines with either; `-o`, `-n`, `-q`, `-v`,
`--dry-run` and input paths are refused rather than ignored — though a value
that equals the default (`-o okf`) is indistinguishable from not passing it,
and goes through. Both also need a terminal on stdin, and say so before
building anything. The flag is `--agent` rather than `--pi` so that swapping
the agent framework later would not change a published interface.

**For looking, not for authoring.** You land in the workbench's `work/okf`,
holding whatever the last compile left. No compile run is restaged: the helper
CLIs and the bundled `work/SPEC.md` are restaged, and prior staged documents
otherwise remain. Nothing written to `work/okf` survives
the next compile, but that compile cannot start underneath an active session:
the interactive command holds the workbench lock until it exits. The agent's transcripts
persist under `sessions/`. Entry is likewise refused while a compile holds the
lock.

The raw one-liners remain the fallback — for a machine without the driver on
PATH, or a flag these do not pass through:

```bash
sbx exec -it md2okf-pi -- bash
sbx exec md2okf-pi -- pi --list-models deepseek
```

Once a sandbox exists, this should print `proxy-managed` rather than your key:

```bash
sbx exec md2okf-pi -- sh -lc 'echo "$OPENROUTER_API_KEY"'
```

## Python layout

Python tooling is thin. The repository root *is* a project — it holds the
`md2okf` command itself, because the tool is named after the repository and a
root `pyproject.toml` is what makes `uv tool install git+https://…` work with no
registry, and what lets the package read `VERSION` as its version source.
Everything else stays independent: `extras/pdf2md/`, `extras/web2md/`, `scripts/inspectmd/`,
`scripts/inspectokf/`, `scripts/sizeokf/`, and `scripts/merkleokf/` are separate
uv projects, each with its own `pyproject.toml` and (where needed) `uv.lock`,
and nothing shared between them.
`extras/pdf2md/` exists only to give `marker` a pinned venv; `extras/web2md/` owns the
scraper's dependencies and its pytest/ruff config; the four `scripts/` projects
are installable stdlib-only CLIs with their own ruff and pytest. So the heavy
dependencies (marker-pdf, torch) cannot reach the lint or test jobs at all,
rather than being excluded by flag.

`ruff` and `yamllint` belong to no project; `make lint` runs them ephemerally at
a pinned version with `uv tool run`, and checks each tracked subproject in turn
— a new subproject carries its own `[tool.ruff]` and needs no Makefile change.
The root project's `[tool.ruff]` excludes the subprojects and the non-project
Python (`kits/`, `scripts/`, `md/`, `okf/`, agent-tool config), so each file is
linted once, under its own rules.

### Virtual environments are per-platform

A venv pins an absolute interpreter path and platform-specific wheels, so it
cannot be shared between a macOS host and a Linux sandbox bind-mounting the same
tree. On Linux, export `UV_PROJECT_ENVIRONMENT=.venv-linux` so the default
`.venv/` stays macOS-only. Keep the value **relative**: the repo holds seven
independent uv projects, and a relative path gives each its own, where an
absolute one would collapse them into a single shared environment. `make`
exports it for you on Linux, so the targets above are correct either way — a
bare `uv run` or `uv sync` is not. `uv.lock` is the portable artifact: share the
lock, never the venv. A venv left behind by the other platform needs no cleanup;
uv detects the dangling interpreter and rebuilds it.

### Helper CLIs

Four CLIs survey the wiki. The sandbox exposes the same commands to the agent,
and `make install-clis` puts them on your own PATH. All four take `-L`/`--level`
as a depth cap.

| Command | What it prints |
| --- | --- |
| `inspectmd <file>` | a Markdown heading map: line ranges, word counts, kebab-case slugs |
| `inspectokf [path]` | the wiki directory tree, via `tree` (default `okf/`) |
| `sizeokf [path]` | Markdown word counts per file and folder, excluding frontmatter |
| `merkleokf [path]` | a Merkle hash tree, one hash per file and per directory |

`sizeokf` and `merkleokf` also take `--nolog`, which ignores `okf/log.md`.
`merkleokf` hashes raw bytes, deliberately the opposite of `sizeokf`, which
strips frontmatter: `merkleokf` answers "did this change", `sizeokf` answers
"how much prose is here", and they share no code.

## How the agent knows what to do

The instructions come in two parts, shown here for Pi; the Claude Code and
Codex kits carry the same two parts, ported, in the places their agents read
them (see each kit's `README.md`). `kits/md2okf-pi/files/home/.pi/agent/AGENTS.md`
holds what every task must respect: the OKF conventions, the directories the
agent may write to, and the rule that `SPEC.md` outranks both. Each task's
procedure lives in a skill of its own. Task skill today: `compile-okf`. Tool
skills: `inspect-md`, `inspect-okf`, `size-okf`, `merkle-okf`, `curate-okf` — a
tool gets a skill, not an `AGENTS.md` section. The sandbox also installs the
`context7-docs` skill via `@upstash/context7-pi` for library docs lookups. A
new task gets a new directory rather than more rules in `AGENTS.md`.

A skill is a directory holding a `SKILL.md` — YAML frontmatter with a `name` and
`description`, then the instructions, plus any scripts it needs. Pi picks skills
up from `~/.pi/agent/skills/`, Claude Code from `~/.claude/skills/`, Codex from
`~/.agents/skills/`. A change to a skill or to the shared contract belongs in
every kit: `tests/test_kits.py` checks each kit for the shared rules, its own
`generated.by` producer, byte-identical gate scripts and the one shim hook
every kit shares.

Pi's kit is `kits/md2okf-pi/`, and the config it carries lives in
`kits/md2okf-pi/files/home/.pi/agent/`. The Claude Code and Codex kits keep their
skills in `kits/md2okf-<agent>/files/skills/` and their instructions in the
`agent-context@2` entry of their descriptor. All of it is built into the
sandbox, not mounted, so an edit reaches the agent on the next fresh sandbox —
which `md2okf` builds by itself once the kit's hash no longer matches what the
running one was built from, or immediately on `--fresh`.
[The kit guide](kits/md2okf-pi/README.md) covers the model and provider settings.

`tests/` holds the paired live-sandbox checks (`test-sandbox.sh`, which asks the
driver for a sandbox and then calls `sbx`, and the POSIX `sh` script it runs
inside the VM). The driver's own suite is pytest, under the same `tests/`
directory; `test_kits.py` in it checks every kit's instructions statically.

## Checking the wiki

[okfctl](https://github.com/cwest/okfctl) checks the wiki against the spec and
against its own curation health, and it owns the reserved `index.md` files: the
agent runs `okfctl index build` rather than writing link lists by hand.

The gate is `kits/md2okf-pi/files/home/.pi/agent/skills/compile-okf/scripts/check-okf.sh`,
one script with two call sites — the agent runs it before it finishes, and
`make check-okf` runs the same file on the host. It combines five checks:
`okfctl validate` for the spec floor, a `frontmatter-guard.py` for the
conventions the floor deliberately leaves open (title, description, tags,
`generated` provenance, the `okf_version` marker, the log's date headings),
`okfctl lint` for curation defects, `okfctl analyze` for links that resolve to
nothing, and `okfctl index check` for a stale or hand-edited index.

Lint findings split two ways. `broken-link`, `orphan`, `type-hygiene`,
`status-lifecycle` and `spec-version` block the run — each has one correct fix.
`missing-xref` and `coverage-gap` are printed as advice, because they are
judgment calls and the gate runs unattended inside the compile loop.

The guard reads the expected `okf_version` from md2okf's own `SPEC.md`, never
from a spec beside the bundle it checks. On the host the script sits in the kit
tree, `kits/md2okf-<agent>/files/`, and reads the `SPEC.md` beside that `kits/`
directory: the repository root, or the packaged copy in an installed md2okf.
In the sandbox, where no kit tree exists, it reads the read-only `../SPEC.md`
mount beside the workspace, which md2okf stages from that same file. Nothing
else is searched, and a missing spec exits `2`. There is no override, so a
bundle copied elsewhere to try something out is checked in place, against the
same spec.

The sandbox installs okfctl at a pinned version; on the host it comes from
Homebrew, so the two can drift — `okfctl version` says which. The check sits
outside `make lint` and outside CI because `okf/` is generated.

## Releasing

Pushing a `vX.Y.Z` tag triggers `.github/workflows/release.yml`, which creates
a GitHub Release whose notes are the matching section of `CHANGELOG.md`.

Pushing the tag also publishes: the workflow builds the wheel and sdist once
with `make dist`, uploads them to PyPI by trusted publishing (no token — the
`pypi` GitHub environment is what PyPI's publisher configuration is keyed to),
and only then creates the Release, with those same artifacts attached. The jobs
are a chain rather than a fan-out on purpose, so nothing can attach assets to a
Release that does not exist yet, and a re-run is safe because PyPI treats an
upload of a byte-identical file as idempotent.

### One-time setup

Trusted publishing is an agreement between two configurations, and neither of
them lives in this repository, so a fork — or a rebuilt PyPI project — has to
establish both before the first tag. Each one fails in a way that does not point
at itself, so both are worth naming.

- **The `pypi` GitHub environment must permit tag refs.** `publish-pypi` is the
  only job carrying an `environment:`, and this workflow is triggered by tags
  alone. An environment that restricts deployments to selected *branches*
  therefore matches nothing, because a branch rule never covers a tag: under
  Settings → Environments → `pypi` → Deployment branches and tags, add a rule
  of ref type **Tag** with the pattern `v*`. Until then the job fails *before
  its first step*, which means there are no logs to fetch and
  `gh run view --log-failed` answers `log not found`. The message is an
  annotation instead:
  `gh api repos/lars20070/md2okf/check-runs/<job-id>/annotations`.
- **The PyPI publisher must match the token's claims exactly**, and must be on
  `pypi.org` rather than `test.pypi.org` — separate databases, and a publisher
  registered on the wrong one is indistinguishable from no publisher at all. The
  fields are owner `lars20070`, repository `md2okf`, workflow `release.yml` (the
  filename, not the display name `Release`) and environment `pypi`. A mismatch
  fails with `invalid-publisher: valid token, but no corresponding publisher`;
  `uv publish` prints the claims it sent, so compare the configuration against
  those rather than against this list. Before the project exists this is a
  *pending* publisher, and the first successful upload converts it into the
  project's own.

### Cutting a release

1. Move `[Unreleased]` entries into a dated `## [X.Y.Z] - YYYY-MM-DD` section
   with a real body (not just a heading).
2. Set `VERSION` to `X.Y.Z`.
3. Run `./scripts/sync-versions.sh`, which writes `X.Y.Z` into every other
   project's `pyproject.toml` and refreshes each `uv.lock`. One version covers
   the whole repository, the helper CLIs included.
4. Land that commit on `master`. `make lint` fails if `VERSION` disagrees with
   the latest changelog release heading, or with any subproject's version.
5. Sanity-check the notes: `./scripts/release-notes.sh X.Y.Z`
6. Tag and push: `git tag vX.Y.Z && git push origin vX.Y.Z`

The workflow re-runs `make lint` and refuses a tag whose version disagrees with
`VERSION` (`scripts/check-release-tag.sh`). An empty changelog section fails
before the Release is created. Re-running a tag converges rather than failing:
the build produces the same bytes, PyPI accepts a re-upload of a file it already
has, and an existing Release keeps its notes — which may have been edited by
hand — while its assets are refreshed with `gh release upload --clobber`.
