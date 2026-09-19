# Contributing to md2okf

This guide covers working *on* the repository: the task runner, the test
suites, the sandbox kit, and how the agent's own configuration is laid out. If
you only want to compile a wiki, [the README](README.md) is enough.

`AGENTS.md` holds the same ground rules for coding agents working on this repo.

## Commands

```bash
make lint                # markdownlint, jq, yamllint, shellcheck, cspell, ruff;
                         # also VERSION ↔ CHANGELOG.md agreement
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

Once a sandbox exists — `md2okf` builds one on first use, or
`uv run python -m md2okf.sandbox` makes one without compiling anything — these
are the two ways in. They are `sbx` one-liners rather than scripts, because the
command owns sandbox creation and nothing else needs to:

```bash
sbx exec -it md2okf -- bash   # interactive shell at the wiki root
sbx exec -it md2okf -- pi     # interactive Pi in the same sandbox
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

The wheel and sdist that `make dist` builds are not published yet: publishing to
PyPI, and the workflow ordering it needs, is the last stage of
`.claude/plans/interface-plan.md`. Until then the install paths are
`uv tool install .` from a clone and `uv tool install git+https://…`.

1. Move `[Unreleased]` entries into a dated `## [X.Y.Z] - YYYY-MM-DD` section
   with a real body (not just a heading).
2. Set `VERSION` to `X.Y.Z`.
3. Land that commit on `master`. `make lint` fails if `VERSION` and the latest
   changelog release heading disagree.
4. Sanity-check the notes: `./scripts/release-notes.sh X.Y.Z`
5. Tag and push: `git tag vX.Y.Z && git push origin vX.Y.Z`

The workflow re-runs `make lint` and refuses a tag whose version disagrees with
`VERSION` (`scripts/check-release-tag.sh`). An empty changelog section fails
before the Release is created. Re-running is safe: if the Release already
exists, the job skips it rather than modifying it.
