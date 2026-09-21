# Contributing to md2okf

This guide covers working *on* the repository: the task runner, the test
suites, the sandbox kit, and how the agent's own configuration is laid out. If
you only want to compile a wiki, [the README](README.md) is enough.

`AGENTS.md` holds the same ground rules for coding agents working on this repo.

## Commands

```bash
make lint                # markdownlint, jq, yamllint, shellcheck, cspell, ruff;
                         # also VERSION ↔ CHANGELOG.md and VERSION ↔ every
                         # subproject (scripts/sync-versions.sh --check)
make validate            # check kits/md2okf/spec.yaml against the Sandbox Kit schema
make test-shell          # host test for the guest's session bind helper
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
`uv tool run` and cspell via `npx`, so none of them needs a separate install.
`make check-okf` needs `okfctl`: `brew install cwest/tap/okfctl`.

CI (`.github/workflows/ci.yml`) runs seven jobs on every pull request: `lint`,
`test-shell`, `test-web2md`, `test-clis`, `test-md2okf`, `build-package`, and
`validate-kit`. Each one reuses the matching make target, so a green
`make lint && make validate && make test-shell && make test-web2md &&
make test-clis && make test-md2okf && make dist` locally means a green build.

## Validate the kit spec before you finish

Touch anything under `kits/md2okf/` or `scripts/*.sh` and run `make validate`
before you call the job done. It checks the kit spec against the schema bundled
in your `sbx` binary, and needs no Docker, no login and no network. CI runs the
same check in its `validate-kit` job, so catching a break locally saves a red
build. The current kit requires sbx 0.43.0 or newer; `brew upgrade sbx` fixes
unknown field errors from an older install.

`make test-sandbox` asks the other question: does the sandbox actually have
every tool `kits/md2okf/spec.yaml` installs, the agent config copied in from
`kits/md2okf/files/`, and a proxy-managed key? It needs an `sbx login` session.
Like the scripts below it reuses the sandbox — fast, and nothing a compile left
behind is lost — and only builds one if none exists. That also means it tests
the sandbox you have, which may be older than your last `kits/md2okf/` edit. To
check the current kit from scratch, throw the sandbox away first with
`sbx rm --force md2okf`; building the next one takes minutes.

## Working inside the sandbox

Two flags open the sandbox, building or refreshing it first when none exists or
the running one no longer matches `kits/md2okf/`:

```bash
md2okf --shell   # interactive shell at the wiki root
md2okf --agent   # interactive agent session in the same sandbox
```

Only `--fresh` combines with either; `-o`, `--spec`, `-n`, `-q`, `-v`,
`--dry-run` and input paths are refused rather than ignored — though a value
that equals the default (`-o okf`) is indistinguishable from not passing it,
and goes through. Both also need a terminal on stdin, and say so before
building anything. The flag is `--agent` rather than `--pi` so that swapping
the agent framework later would not change a published interface.

**For looking, not for authoring.** You land in the workbench's `work/okf`,
holding whatever the last compile left. No compile run is restaged: helper CLIs
are refreshed, an empty `work/SPEC.md` gets the bundled spec, and prior staged
documents and spec otherwise remain. Nothing written to `work/okf` survives
the next compile, but that compile cannot start underneath an active session:
the interactive command holds the workbench lock until it exits. Pi transcripts
persist under `sessions/`. Entry is likewise refused while a compile holds the
lock.

The raw one-liners remain the fallback — for a machine without the driver on
PATH, or a flag these do not pass through:

```bash
sbx exec -it md2okf -- bash
sbx exec md2okf -- pi --list-models deepseek
```

Once a sandbox exists, this should print `proxy-managed` rather than your key:

```bash
sbx exec md2okf -- sh -lc 'echo "$OPENROUTER_API_KEY"'
```

## Python layout

Python tooling is thin. The repository root *is* a project — it holds the
`md2okf` command itself, because the tool is named after the repository and a
root `pyproject.toml` is what makes `uv tool install git+https://…` work with no
registry, and what lets the package read `VERSION` as its version source.
Everything else stays independent: `pdf2md/`, `web2md/`, `scripts/inspectmd/`,
`scripts/inspectokf/`, `scripts/sizeokf/`, and `scripts/merkleokf/` are separate
uv projects, each with its own `pyproject.toml` and (where needed) `uv.lock`,
and nothing shared between them.
`pdf2md/` exists only to give `marker` a pinned venv; `web2md/` owns the
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

The instructions come in two parts. `kits/md2okf/files/home/.pi/agent/AGENTS.md`
holds what every task must respect: the OKF conventions, the directories the
agent may write to, and the rule that `SPEC.md` outranks both. Each task's
procedure lives in a skill of its own. Task skill today: `compile-okf`. Tool
skills: `inspect-md`, `inspect-okf`, `size-okf`, `merkle-okf`, `curate-okf` — a
tool gets a skill, not an `AGENTS.md` section. The sandbox also installs the
`context7-docs` skill via `@upstash/context7-pi` for library docs lookups. A
new task gets a new directory rather than more rules in `AGENTS.md`.

A skill is a directory holding a `SKILL.md` — YAML frontmatter with a `name` and
`description`, then the instructions, plus any scripts it needs. Pi picks skills
up from `~/.pi/agent/skills/`.

The kit is `kits/md2okf/`, and the config it carries lives in
`kits/md2okf/files/home/.pi/agent/`. That config is copied into the sandbox when
the kit is built, not mounted, so an edit reaches Pi on the next fresh sandbox —
which `md2okf` builds by itself once the kit's hash no longer matches what the
running one was built from, or immediately on `--fresh`.
[The kit guide](kits/md2okf/README.md) covers the model and provider settings.

`tests/` holds the paired live-sandbox checks (`test-sandbox.sh`, which asks the
driver for a sandbox and then calls `sbx`, and the POSIX `sh` script it runs
inside the VM), plus `test-mount-state.sh` for the guest-side bind helper. The
driver's own suite is pytest, under the same `tests/` directory.

## Checking the wiki

[okfctl](https://github.com/cwest/okfctl) checks the wiki against the spec and
against its own curation health, and it owns the reserved `index.md` files: the
agent runs `okfctl index build` rather than writing link lists by hand.

The gate is `kits/md2okf/files/home/.pi/agent/skills/compile-okf/scripts/check-okf.sh`,
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

The guard reads the expected `okf_version` from `SPEC.md`, looked up as the
sibling of the bundle — `./SPEC.md` beside `./okf` on the host, the
`../SPEC.md` mount in the sandbox. A bundle copied elsewhere to try something
out has no sibling spec and the guard exits `2`; set `SPEC_MD` to point at the
real file rather than reading it as a broken gate.

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
