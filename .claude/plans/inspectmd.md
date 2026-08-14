# Add an `inspect-md` tool

## Context

`SKILL.md` devotes a whole section ("Write in bounded chunks") to a failure mode
that costs a run: Pi tries to `write` a long page in one call, the call is cut
off mid-argument, validation fails, and nothing reaches disk. The current advice
is qualitative — "read long sources in ranges", "a section or two, not a whole
chapter" — so the agent has to guess where a document's seams are by reading it,
which is the very thing that blows the output limit.

`inspect-md` replaces that guess with a measurement. It reads one Markdown
document and prints its heading tree with line ranges and sizes, so a reader —
Pi or a human — can plan reads and page boundaries before opening the file.

It has four audiences, and that shapes where it lives: Pi inside the sandbox,
you on the host, you inside the sandbox via `scripts/bash.sh`, and pytest on the
host and in CI.

## Decisions taken

1. **A workspace subproject, not a skill asset.** `inspect-md/src/inspect_md.py`,
   mirroring `web2md/` — run by path, no `[build-system]`, tests alongside.
2. **One entry point for everybody: `scripts/inspect-md.sh`.** `scripts/` is in
   the mounted workspace, so the identical command works on the host and inside
   the VM. This is why the tool gets a wrapper where `lint-okf.sh` needs none:
   the wrapper is what makes one command serve four audiences, and it earns the
   hyphenated name.
3. **Standard library only.** The sandbox has apt `python3` and no project venv
   (`pi/spec.yaml` never runs `uv sync`; `uv tool install` builds private venvs
   for ruff and yamllint alone). The host's gitignored `.venv/` is visible in the
   VM through the workspace mount but is a host-platform artefact — never import
   from it. The wrapper therefore calls plain `python3`, not `uv run`, and
   `re`/`pathlib`/`argparse`/`dataclasses` cover the whole job.
4. **`pi/` is not touched at all.** No file added to the payload, no
   `setup.install` step, no change to either tool list in `spec.yaml`.

### Why not inside the skill

`scripts/compile-wiki.sh:38-40` records it as verified: `sbx exec` runs with the
VM workspace — the repo root — as its cwd, so a repo-relative path resolves
identically on both sides. `pi/README.md:12-13` is equally explicit that
`files/` is **copied at kit build time, not mounted**. Together those mean:

- A skill-owned copy buys no reachability the workspace doesn't already give.
- It costs a rebuild per edit. `make wiki` rebuilds, but `scripts/bash.sh` and
  `make test-sandbox` deliberately *reuse* a running sandbox — so iterating on a
  payload file means `sbx rm --force md2okf` each time, or debugging a stale copy.
- It is invisible to any future skill, and `AGENTS.md` is explicit that a new
  task gets a new skill.

`lint-okf.sh` stays where it is on all three counts reversed: it wraps a
globally-installed npm binary, it is three lines, nothing tests it, and the host
already reaches `okf-lint` by another route (`make lint-okf` via `pnpm dlx`).

## Directory tree

`+` new, `~` changed, everything else is context.

```text
md2okf/
├── AGENTS.md                              ~ one line in the repository map
├── Makefile                               ~ test-inspect-md target, test deps
├── pyproject.toml                         ~ testpaths, pythonpath, per-file-ignores
├── .github/
│   └── workflows/
│       └── ci.yml                         ~ one step in the test-web2md job
├── inspect-md/                            + the tool, mirroring web2md/
│   ├── README.md                          +
│   ├── src/
│   │   └── inspect_md.py                  + stdlib only, run by path
│   └── tests/
│       └── test_inspect_md.py             +
├── scripts/                               host + VM entry points
│   ├── bash.sh
│   ├── compile-wiki.sh
│   ├── inspect-md.sh                      + the single entry point
│   └── validate-spec.sh
├── md/                                    read-only sources (the tool's input)
│   ├── GoogleStyleGuide.md
│   ├── TheRestIsHistory-abridged.md
│   └── TheRestIsHistory.md
├── okf/                                   generated wiki (gitignored, untouched)
├── pi/                                    the sandbox kit — UNCHANGED except prose
│   ├── README.md
│   ├── spec.yaml                          unchanged: nothing new is installed
│   └── files/                             ← COPIED to ~/ at kit build time
│       └── home/.pi/agent/
│           ├── AGENTS.md                  ~ advertise the workspace tool
│           ├── models.json
│           ├── settings.json
│           └── skills/compile-wiki/
│               ├── SKILL.md               ~ document inspect-md
│               └── scripts/
│                   └── lint-okf.sh        unchanged; stays skill-owned
├── tests/                                 sandbox shell tests
│   ├── test-sandbox-guest.sh              ~ smoke-run the wrapper in the VM
│   └── test-sandbox.sh
└── web2md/                                the other Python subproject (untouched)
    ├── src/web2md.py
    └── tests/
```

Everything reaches it the same way:

```bash
./scripts/inspect-md.sh md/GoogleStyleGuide.md     # host, VM, Pi, all identical
```

## Files

### New: `inspect-md/src/inspect_md.py`

Structured as pure functions plus a thin formatting layer, so the tests target
parsing rather than column alignment — the shape `web2md/src/web2md.py` uses:

```python
@dataclass(frozen=True)
class Section:
    index: int      # 0 is the preamble, if any
    level: int      # 1-6; 0 for the preamble
    title: str
    slug: str       # kebab-case, per the AGENTS.md slug convention
    start: int      # 1-based, inclusive, the heading line itself
    end: int        # 1-based, inclusive
    chars: int
```

- `split_frontmatter(text) -> tuple[int, str]` — leading `---` block, returning
  its last line number and the remainder. Every document in `md/` has one
  (`md/GoogleStyleGuide.md:1-8`), and it must not be mistaken for content.
- `parse_sections(text, offset) -> list[Section]` — ATX headings only.
- `slugify(title) -> str` — kebab-case, matching the convention in
  `pi/files/home/.pi/agent/AGENTS.md`, so the output can be reused verbatim as a
  filename.
- `format_table(sections) -> str`, `main(argv=None) -> int`.

**Parser rules, each one a test:**

- ATX only (`#` … `######`), up to three leading spaces, optional closing `#`s.
  Both producers emit ATX — `web2md/src/web2md.py:425` sets
  `heading_style = ATX`, and Marker's output in `md/` is ATX throughout — so
  setext underlines are deliberately *not* headings. Pin that in a test and say
  so in the module docstring.
- `#` inside a fenced block is not a heading: ``` and `~~~`, info strings, and
  closing fences at least as long as the opener.
- Text between the frontmatter and the first heading is section 0, the preamble.
- A section runs to the line before the next heading of any level, or EOF.
- No headings, or an empty file: print the file summary and say so; exit 0.

**CLI contract** (mirroring `lint-okf.sh`'s documented exit codes):

```text
inspect-md.sh [--section N] [--max-depth N] <file>
  0  parsed and printed
  2  usage or runtime error (missing file, unreadable, --section out of range)
```

`--section N` prints one section's `start:end` range and size, for feeding
straight to a ranged read. `--max-depth N` collapses the tree for a deeply
nested document. `--help` must work, because `tests/test-sandbox-guest.sh`
smoke-runs it. No `--json`: the consumer is an agent reading terminal output,
and a second format is surface with no reader.

### New: `scripts/inspect-md.sh`

The single entry point, following the shape every script in `scripts/` already
has: `#!/usr/bin/env bash`, `set -euo pipefail`, a `# Usage:` comment block,
repo-root resolution from `BASH_SOURCE` (so it works from any cwd, on either
side of the mount), a `command -v python3` guard exiting 2, then

```bash
exec python3 "${repo_root}/inspect-md/src/inspect_md.py" "$@"
```

`python3`, not `uv run` — see decision 3. Add a comment saying so, or someone
will "fix" it later and break the sandbox.

### New: `inspect-md/README.md`

Short, in the register of `web2md/README.md`: what it reports, the one command,
why stdlib-only, and that `make test-inspect-md` runs the suite offline.

### New: `inspect-md/tests/test_inspect_md.py`

pytest imports the module via `pythonpath`; no `__init__.py` and no `conftest.py`
needed. Cases: the parser rules above, `slugify` (punctuation, case, runs of
spaces, non-ASCII), and two `main(argv)` smoke tests through `capsys` — one clean
parse, one missing file asserting exit 2.

### Changed: `pyproject.toml`

```toml
testpaths = ["web2md/tests", "inspect-md/tests"]
pythonpath = ["web2md/src", "inspect-md/src"]

[tool.ruff.lint.per-file-ignores]
"inspect-md/tests/*" = ["D100", "D103"]   # alongside the existing web2md entry
```

`ruff check .` already covers the new module — no ruff change beyond the
per-file-ignore. It must satisfy `D` (google convention) and the 100-char limit.

### Changed: `Makefile`

`testpaths` now names two suites, so bare `pytest` would run both and make
`test-web2md` a misnomer. Give each target its path and reuse `$(PYTEST)`:

```make
test-web2md:
	$(PYTEST) web2md/tests

test-inspect-md:
	$(PYTEST) inspect-md/tests

test: test-web2md test-inspect-md test-sandbox
```

Add `test-inspect-md` to `.PHONY`. No new launcher variable: the existing
`PYTEST` carries the `web2md` group, harmless here, and CI's `--only-group`
override works unchanged. No `make inspect-md` target — the wrapper *is* the
entry point, and a make target only gets in the way of passing a filename.

### Changed: `.github/workflows/ci.yml`

Add one step to the existing `test-web2md` job, reusing its override:

```yaml
- run: make test-inspect-md PYTEST='uv run --only-group test pytest'
```

Keep the job id — renaming it to `test-python` would be tidier but breaks any
required status check configured on the current name.

### Changed: `pi/files/home/.pi/agent/AGENTS.md`

A short **Workspace tools** entry, so every present and future skill knows the
tool exists: what `./scripts/inspect-md.sh` reports, that it is read-only, and
that it is run from the workspace root. Keep it to the toolchain fact — the
procedure stays in the skill, per the repo's own rule.

### Changed: `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md`

- In **Write in bounded chunks**, before the existing advice: run
  `./scripts/inspect-md.sh md/<document>.md` first and cut on the reported
  ranges.
- In step 2 of the **Procedure**, point at it as the way to open a long source.
- Keep the register of the `okf-lint` section: what it reports, what the exit
  codes mean, and that its output is a plan, not permission to paraphrase — the
  fidelity rule still outranks convenience.

Both files are copied at kit build time, so these two edits — unlike the tool
itself — need a fresh sandbox before Pi sees them.

### Changed: `tests/test-sandbox-guest.sh`

The guest script already runs with the workspace as cwd (`test-sandbox.sh` calls
it as `./tests/test-sandbox-guest.sh`), so the existing `check` helper smoke-runs
the wrapper as-is:

```sh
# Workspace tooling: not installed by the kit, reached through the mount. This
# is the only check that proves python3 + the workspace entry point work
# together inside the VM, which is now the tool's sole delivery route.
check ./scripts/inspect-md.sh
```

`check` tries `--version`, falls back to `--help`; argparse supplies the latter.
Note in the comment that this sits outside the "must match both lists in
`pi/spec.yaml`" contract the file documents, and why.

### Changed: `AGENTS.md` (repo root)

Two sentences in the repository map: `inspect-md/` is the second first-party
Python subproject, same no-`[build-system]` shape as `web2md/`, reached through
`scripts/inspect-md.sh` from both the host and the sandbox; `make test-inspect-md`
runs its suite. Add `test-inspect-md` to the commands block.

### Not changed: `pi/spec.yaml`

Nothing new is installed and nothing is added to the payload, so the two lists
that `tests/test-sandbox-guest.sh` cross-checks stay in agreement. `make
validate` should pass untouched — run it anyway, per `AGENTS.md`, since files
under `pi/` changed.

## Verification

```bash
make lint                       # ruff, shellcheck on the new wrapper, markdownlint + cspell
make test-inspect-md            # the new suite
make test-web2md                # confirm the testpaths split didn't break it
make validate                   # required after any change under pi/
```

Watch for new words in `.cspell.json` — the SKILL.md and AGENTS.md prose is
spell-checked.

Then exercise it on the real corpus, which is the point of the tool — the three
documents in `md/` differ in shape (one Marker book, two scraped episode lists):

```bash
./scripts/inspect-md.sh md/GoogleStyleGuide.md
./scripts/inspect-md.sh md/TheRestIsHistory.md --max-depth 2
./scripts/inspect-md.sh md/GoogleStyleGuide.md --section 3
```

Sanity-check the ranges against the file: the last section's `end` should be the
final line, and section starts should agree with `rg -n '^#{1,6} ' md/<file>`.

Then prove the same command works through the mount, which is the whole premise:

```bash
sbx rm --force md2okf && make test-sandbox    # fresh sandbox: new AGENTS.md/SKILL.md too
./scripts/bash.sh                             # then, inside: ./scripts/inspect-md.sh md/…
```

`make lint-okf` and a full `make wiki` are optional here; `make wiki` is the only
way to watch Pi actually use the tool, and it costs a full compile.

## Out of scope

`--json` output, a coverage check against `okf/`, setext heading support, and any
third-party dependency. If a dependency ever becomes necessary the routes are a
PEP 723 script run with `uv run --script` (PyPI is already in the egress
allowlist) or an install step in `spec.yaml` — both slower, and both reopening
the placement question this plan settles.
