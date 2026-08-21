# Sync frontmatter descriptions into `index.md` entries

## Context

Per `SPEC.md` §6, an `index.md` entry carries the description of the concept it
links to — the same sentence that lives in that concept's frontmatter
`description` (§4.1). The description is therefore stored twice, and the
frontmatter copy is the ground truth.

In the generated wiki the two copies have drifted completely: all 274 concept
files carry a proper one-line `description`, but every one of the 239 file
entries across the 40 `index.md` files instead holds a ~180-character excerpt of
the page body, cut mid-sentence. A new helper script makes the index copies
follow the frontmatter mechanically, so the wiki can be re-synced after any
compile run instead of relying on the agent to keep both copies aligned.

## What the wiki looks like today

- 40 `index.md` files, 278 bullet entries, all single-line, all links absolute
  (bundle-relative, e.g. `/part-1-seven-gateways/chapter-11-rebirth/overview.md`).
- Separator is ` — ` (U+2014 with spaces). Frontmatter descriptions themselves
  often contain ` — `, so an entry must be split structurally at the closing
  `)` of the link, never on the last separator.
- 239 entries point at `.md` files; **39 point at a subdirectory** (trailing
  `/`). Per the decision below those are left alone.
- Only `okf/index.md` has frontmatter (`okf_version`), per §11. Index bodies are
  `# Sections` / `# Subsections` headings plus bullets; the root index also has
  three lines of intro prose. No nested/indented bullets, no wrapped entries.
- Every chapter directory holds an `overview.md` that is deliberately *not*
  listed in its own `index.md` — the parent index links to the directory
  instead. Expect one "unlisted file" report per chapter directory.

## Decisions (confirmed)

1. **Directory entries are left untouched** and counted as skipped.
2. **Descriptions are copied verbatim**, at full length. `MD013` is already
   disabled in `.markdownlint-cli2.yaml`, so long lines are fine.
3. **Descriptions only.** No entries are added, removed or reordered; headings
   and prose are untouched. Anything else is reported, not fixed.
4. **Python with PyYAML**, matching `scripts/split-chapters.py`.

## Implementation

### New file: `scripts/sync-descriptions.py`

`#!/usr/bin/env python3`, module docstring, stdlib + `yaml`, in the style of
`scripts/split-chapters.py` (which already does `import yaml` and `pathlib`).

CLI (`argparse`):

| Flag | Behaviour |
|------|-----------|
| `PATH` (positional, default `okf`) | Bundle root. Absolute links resolve against it. |
| `--check` | Write nothing; exit `1` if any entry is out of sync. For CI / pre-commit. |
| `--diff` | Write nothing; print a unified diff (`difflib.unified_diff`) per changed file. |
| `--verbose` | Also list every unlisted concept file (otherwise only counted). |

Flow:

1. `sorted(root.rglob("index.md"))`.
2. Per index file, walk lines. Entry pattern:
   `^(?P<prefix>\s*[*-] \[(?P<title>[^\]]*)\]\((?P<target>[^)]*)\))(?P<rest>.*)$`
   — titles contain `(` `)` but only inside `[...]`, so this is safe.
3. Skip and count as *skipped*: targets ending in `/`, URLs
   (`http:`, `https:`, `mailto:`), and pure fragments (`#…`).
4. Resolve the target (strip `#fragment`): leading `/` → `root / target[1:]`,
   otherwise `index_file.parent / target`; then `Path(os.path.normpath(...))`.
5. Report and leave the line unchanged when: the resolved file does not exist;
   it is `index.md` or `log.md` (reserved, no frontmatter to read); it has no
   frontmatter; its `description` is missing, empty or not a scalar.
6. Read frontmatter with `yaml.safe_load` over the block between the leading
   `---` and the next `---` line. Normalise with `" ".join(str(desc).split())`
   so a folded/literal block scalar collapses to one line; otherwise verbatim.
7. Rebuild the line as `f"{prefix} — {description}"`, discarding `rest`. This
   preserves indentation, bullet character, title and target exactly.
8. Guard against wrapped entries: warn if a non-blank, non-bullet, non-heading
   line is indented directly under an entry line (none exist today, but a
   line-based rewrite would orphan it).
9. Write with `encoding="utf-8"`, `newline="\n"`, only when content changed;
   preserve the file's trailing-newline state.
10. Per directory, compare the sibling `*.md` files (excluding `index.md`,
    `log.md`) against the targets listed in that directory's `index.md`; count
    unlisted files, list them under `--verbose`.

Output: warnings to `stderr`, then a summary to `stdout`, e.g.
`sync-descriptions: 239 synced, 0 already current, 39 skipped (directory
entries), 33 concept files not listed in an index, 0 warnings`.
Exit `0` normally; `1` under `--check` when anything is out of sync; `2` on a
usage/IO error.

Explicit non-goals: no writes to `okf/log.md`, no touching frontmatter, no
truncation, no reordering.

### Optional, small: wire it into the Makefile and docs

Both are one-liners and easy to drop if unwanted.

- `Makefile`: add `sync-descriptions:` next to `lint-okf` (and to `.PHONY` on
  line 23), with the same comment rationale — host-only, operates on gitignored
  generated output, so deliberately outside `make lint` and CI.
- `AGENTS.md`: one line in the *Commands* block noting
  `python3 scripts/sync-descriptions.py --check` as the drift check for the
  generated wiki.

Note: `make lint` runs ruff only over tracked subprojects that own a
`pyproject.toml`, so `scripts/*.py` is not linted by it. The script will still
be kept ruff-clean (`uv tool run ruff@0.16.2 check scripts/sync-descriptions.py`)
and cspell-clean.

## Verification

`okf/` is read-only for this task, so all writing is exercised on a copy.
PyYAML is absent in this sandbox, so run through `uv run --with pyyaml python`
(the host `.venv` already has it).

1. **Read-only preview against the real wiki** — no writes:
   `python3 scripts/sync-descriptions.py --diff okf | head -40` and
   `python3 scripts/sync-descriptions.py --check okf; echo $?` → expect `1`
   plus a summary reporting ~239 entries out of sync and 39 skipped.
2. **Write test on a copy**: `cp -r okf "$SCRATCH/okf"`, run the script on it,
   then confirm for a sample (`chapter-11-rebirth/index.md`) that each entry's
   text after ` — ` is byte-identical to the target file's frontmatter
   `description`, via a small comparison loop over every entry in the copy.
3. **Idempotency**: run again on the copy → `0 synced`, exit `0`, and
   `--check` now exits `0`. `git`-less diff of the copy against itself between
   the two runs must be empty.
4. **Structure preserved**: `diff <(grep -c '' before) …` — confirm line counts,
   heading lines, bullet order, link targets and the root `okf_version`
   frontmatter are unchanged in the copy; only text after ` — ` differs.
5. **Edge cases on a scratch bundle**: entry pointing at a missing file, a file
   without frontmatter, a file with an empty `description`, a relative
   (`./x.md`) link, a `-` bullet instead of `*`, and a description containing
   ` — ` — each must be handled as specified without corrupting the line.
6. **Lint**: `uv tool run ruff@0.16.2 check scripts/sync-descriptions.py`, and
   `make lint` if `AGENTS.md`/`Makefile` were touched.
7. **Post-run wiki lint (host, user's call)**: after the user runs the script
   for real on `okf/`, `make lint-okf` should still pass — the okf-lint rules
   in `okf/.okflintrc.json` concern frontmatter and links, neither of which
   this script changes.
