# Add an `inspect-md` tool to the `compile-wiki` skill

## Context

`SKILL.md` devotes a whole section ("Write in bounded chunks") to a failure mode
that costs a run: Pi tries to `write` a long page in one call, the call is cut
off mid-argument, validation fails, and nothing reaches disk. The current advice
is qualitative — "read long sources in ranges", "a section or two, not a whole
chapter" — so the agent has to guess where a document's seams are by reading it,
which is the very thing that blows the output limit.

`inspect-md` replaces that guess with a measurement. It reads one source
document under `md/` and prints its heading tree with line ranges and sizes, so
the agent can plan its reads and its page boundaries before it opens the file.
It is a read-only, stdlib-only companion to `lint-okf.sh`: the same skill, the
same invocation convention, the same exit-code contract.

## Decisions taken

1. **Self-contained in the skill.** One copy, at
   `pi/files/home/.pi/agent/skills/compile-wiki/scripts/inspect_md.py`, shipped
   into the VM by the kit's `files/` convention alongside `lint-okf.sh`.
2. **No shell wrapper.** Shebang plus exec bit, invoked by absolute path exactly
   as `SKILL.md` invokes `lint-okf.sh`. A wrapper would only add a
   `command -v python3` guard, and `python3` is already an asserted kit tool.
3. **Standard library only.** The sandbox has apt `python3` and no project venv
   (`pi/spec.yaml` never runs `uv sync`; `uv tool install` builds private venvs
   for ruff and yamllint alone). The host's gitignored `.venv/` is visible in the
   VM through the workspace mount but is a host-platform artefact — never import
   from it. `re`, `pathlib`, `argparse`, `dataclasses` cover the whole job.

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
├── md/                                    read-only sources (the tool's input)
│   ├── GoogleStyleGuide.md
│   ├── TheRestIsHistory-abridged.md
│   └── TheRestIsHistory.md
├── okf/                                   generated wiki (gitignored, untouched)
├── pi/                                    the sandbox kit
│   ├── README.md
│   ├── spec.yaml                          unchanged — nothing new is installed
│   ├── files/                             ← everything below here is COPIED to ~/
│   │   └── home/
│   │       └── .pi/
│   │           └── agent/
│   │               ├── AGENTS.md
│   │               ├── models.json
│   │               ├── settings.json
│   │               └── skills/
│   │                   └── compile-wiki/
│   │                       ├── SKILL.md   ~ document inspect-md
│   │                       └── scripts/
│   │                           ├── lint-okf.sh
│   │                           └── inspect_md.py    + the tool (exec bit, stdlib)
│   └── tests/                             + NOT copied — host-side pytest
│       └── test_inspect_md.py             +
├── scripts/                               host-side wrappers (untouched)
│   ├── bash.sh
│   ├── compile-wiki.sh
│   └── validate-spec.sh
├── tests/                                 sandbox shell tests
│   ├── test-sandbox-guest.sh              ~ check_exec for inspect_md.py
│   └── test-sandbox.sh
└── web2md/                                the other Python subproject (untouched)
    ├── src/web2md.py
    └── tests/
```

The load-bearing line is `pi/files/`: the kit copies that subtree into the VM at
`~/`, so `pi/tests/` sits one level up on purpose — a sibling of `files/`, not
inside it — and never ships to the sandbox. That is also why `pi/spec.yaml`
needs no edit: the tool arrives as a file, not as an install step.

## Files

### New: `pi/files/home/.pi/agent/skills/compile-wiki/scripts/inspect_md.py`

Executable (`chmod +x` — the kit copies files, and `tests/test-sandbox-guest.sh`
asserts the exec bit because a lost one is a real failure mode).

Structured as pure functions plus a thin formatting layer, so the tests target
parsing rather than column alignment — the shape `web2md/src/web2md.py` already
uses:

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
  `pi/files/home/.pi/agent/AGENTS.md` so the agent can reuse the output verbatim
  as a filename.
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
inspect_md.py [--section N] [--max-depth N] <file>
  0  parsed and printed
  2  usage or runtime error (missing file, unreadable, --section out of range)
```

`--section N` prints one section's `start:end` range and size, for feeding
straight to a ranged read. `--max-depth N` collapses the tree for a document
with deep nesting. No `--json`: the consumer is an agent reading terminal
output, and a second format is surface with no reader.

### New: `pi/tests/test_inspect_md.py`

Outside `files/`, so it is never copied into the VM. pytest imports the module
via `pythonpath`; the filename is unique across both suites, so no `__init__.py`
and no `conftest.py` are needed. Cases: the parser rules above, `slugify`
(punctuation, case, runs of spaces, non-ASCII), and two `main(argv)` smoke tests
through `capsys` — one clean parse, one missing file asserting exit 2.

### Changed: `pyproject.toml`

```toml
testpaths = ["web2md/tests", "pi/tests"]
pythonpath = ["web2md/src", "pi/files/home/.pi/agent/skills/compile-wiki/scripts"]

[tool.ruff.lint.per-file-ignores]
"pi/tests/*" = ["D100", "D103"]   # alongside the existing web2md/tests entry
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
	$(PYTEST) pi/tests

test: test-web2md test-inspect-md test-sandbox
```

Add `test-inspect-md` to `.PHONY`. No new launcher variable: the existing
`PYTEST` carries the `web2md` group, which is harmless here, and CI's
`--only-group` override works unchanged.

### Changed: `.github/workflows/ci.yml`

Add one step to the existing `test-web2md` job, reusing its override:

```yaml
- run: make test-inspect-md PYTEST='uv run --only-group test pytest'
```

Keep the job id as it is — renaming it to `test-python` would be tidier but
breaks any required-status-check configured on the current name.

### Changed: `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md`

- In **Write in bounded chunks**, before the existing advice: run `inspect-md`
  first and cut on the reported ranges, with the invocation spelled in full —
  `~/.pi/agent/skills/compile-wiki/scripts/inspect_md.py md/<document>.md` —
  and the same "your working directory is the workspace, not this skill's
  directory" note that `lint-okf.sh` carries.
- In step 2 of the **Procedure**, point at it as the way to open a long source.
- Keep the tone of the `okf-lint` section: what it reports, what the exit codes
  mean, and that its output is a plan, not permission to paraphrase — the
  fidelity rule still outranks convenience.

### Changed: `tests/test-sandbox-guest.sh`

Add next to the existing `check_exec` for `lint-okf.sh`:

```sh
check_exec "${HOME}/.pi/agent/skills/compile-wiki/scripts/inspect_md.py"
```

### Changed: `AGENTS.md` (repo root)

One sentence in the repository map: the skill now ships a stdlib-only Python
tool whose tests live in `pi/tests/`, and `make test-inspect-md` runs them.

### Not changed: `pi/spec.yaml`

Nothing new is installed. `python3` is already in `setup.install` and already
promised in the `agentInstructions` tool list, so the two lists that
`tests/test-sandbox-guest.sh` cross-checks stay in agreement. `make validate` is
therefore expected to pass untouched — but run it anyway, per `AGENTS.md`, since
`pi/` changed.

## Verification

```bash
make lint                       # ruff, shellcheck, markdownlint + cspell on SKILL.md
make test-inspect-md            # the new suite
make test-web2md                # confirm the testpaths split didn't break it
make validate                   # required after any change under pi/
```

Then exercise it on the real corpus, which is the point of the tool — the three
documents in `md/` differ in shape (one Marker book, two scraped episode lists):

```bash
python3 pi/files/home/.pi/agent/skills/compile-wiki/scripts/inspect_md.py md/GoogleStyleGuide.md
python3 pi/files/home/.pi/agent/skills/compile-wiki/scripts/inspect_md.py md/TheRestIsHistory.md --max-depth 2
python3 pi/files/home/.pi/agent/skills/compile-wiki/scripts/inspect_md.py md/GoogleStyleGuide.md --section 3
```

Sanity-check the ranges against the file: the last section's `end` should be the
final line, and section starts should agree with `rg -n '^#{1,6} ' md/<file>`.

Finally, prove it reaches the VM — the kit copies config at build time, so a
stale sandbox would test the old payload:

```bash
sbx rm --force md2okf && make test-sandbox
```

`make lint-okf` and a full `make wiki` are optional here; `make wiki` is the only
way to see Pi actually use the tool, and it costs a full compile.

## Out of scope

`--json` output, a coverage check against `okf/`, setext heading support, and
any third-party dependency. If a dependency ever becomes necessary, the two
routes are a PEP 723 script run with `uv run --script` (PyPI is already in the
egress allowlist) or a fifth `setup.install` step — both slower and both
requiring the `agentInstructions` tool list to change.
