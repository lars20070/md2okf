# Sync frontmatter descriptions into `index.md` entries

## Context

Per `SPEC.md` §6, an `index.md` entry SHOULD carry the description of the
concept it links to — the same sentence that lives in that concept's
frontmatter `description` (§4.1). The frontmatter copy is the ground truth.

In the generated wiki the two copies have drifted: concept files carry a proper
one-line `description`, but file entries in `index.md` mostly hold a ~180-character
excerpt of the page body, cut mid-sentence. A small helper script re-syncs the
index copies from frontmatter after any compile run.

## What the wiki looks like today

- 40 `index.md` files; 239 file entries and 39 directory entries (trailing `/`).
- Separator is ` — ` (U+2014 with spaces). Frontmatter descriptions often contain
  ` — `, so split at the closing `)` of the link, never on the separator.
- All links are absolute (bundle-relative). Only `okf/index.md` has frontmatter
  (`okf_version`). No nested/indented bullets, no wrapped entries.
- Verified safe for a line-based rewrite: every bullet is `* `, no title
  contains `]`, no target contains a space, `#`, or `(`, every target is either
  a `.md` file or a trailing-`/` directory, and every file ends with a newline.
- Chapter `overview.md` files are deliberately unlisted in their own
  `index.md` — not this script's concern.

## Decisions

1. **Directory entries are left untouched** and counted as skipped.
2. **Descriptions are copied verbatim**, at full length. `MD013` is already
   disabled, so long lines are fine.
3. **Descriptions only.** No entries added, removed, or reordered; headings and
   prose untouched. Problems are reported, not fixed.
4. **Python with PyYAML**, matching `scripts/split-chapters.py`.

## Implementation

### New file: `scripts/sync-descriptions.py`

`#!/usr/bin/env python3`, module docstring, stdlib + `yaml`, in the style of
`scripts/split-chapters.py`.

CLI (`argparse`):

| Flag | Behaviour |
|------|-----------|
| `PATH` (positional, default `okf`) | Bundle root. Absolute links resolve against it. |
| `--check` | Write nothing; exit `1` if any entry is out of sync. |

Flow:

1. `sorted(root.rglob("index.md"))`.
2. Per index file, match entry lines:
   `^(?P<prefix>\s*[*-] \[(?P<title>[^\]]*)\]\((?P<target>[^)]*)\))(?P<rest>.*)$`
3. Skip and count as *skipped*: targets ending in `/`, and defensively anything
   that is not a `.md` path (URL, bare anchor) or is reserved (`index.md`,
   `log.md` — no description by design). None exist today.
4. Resolve the target (strip `#fragment`): leading `/` → `root / target[1:]`,
   otherwise `index_file.parent / target`; then `Path(os.path.normpath(...))`.
5. Warn and leave the line unchanged when: the resolved file does not exist; it
   has no frontmatter; or `description` is missing, empty, or not a scalar.
6. Read frontmatter with `yaml.safe_load` over the block between the leading
   `---` and the next `---` line. Normalise with `" ".join(str(desc).split())`
   so a folded/literal block scalar collapses to one line.
7. Rebuild as `f"{prefix} — {description}"`, discarding `rest`. Preserves
   indentation, bullet character, title, and target.
8. Write with `encoding="utf-8"`, `newline="\n"`, only when content changed;
   preserve the file's trailing-newline state.

Output: warnings to `stderr`, summary to `stdout`, e.g.
`sync-descriptions: 239 synced, 0 already current, 39 skipped (directory
entries), 0 warnings`.
Exit `0` normally; `1` under `--check` when anything is out of sync; `2` on a
usage/IO error.

Non-goals: no Makefile or `AGENTS.md` wiring; no unlisted-file inventory; no
writes to `okf/log.md`; no touching frontmatter; no truncation or reordering.

Keep the script ruff-clean:
`uv tool run ruff@0.16.2 check scripts/sync-descriptions.py`.

## Verification

`okf/` is read-only for this task — write on a copy. Use
`uv run --with pyyaml python` if system Python lacks PyYAML.

1. **Check against the real wiki**:
   `python3 scripts/sync-descriptions.py --check okf; echo $?` → expect `1`
   and a summary with ~239 out of sync, 39 skipped.
2. **Write on a copy**: `cp -r okf "$SCRATCH/okf"`, run the script, spot-check
   one chapter `index.md` so text after ` — ` matches each target's frontmatter
   `description`.
3. **Structure preserved**: in the copy, line counts, headings, bullet order,
   and link targets are unchanged versus `okf/` — only text after ` — ` differs.
4. **Idempotency**: run again → `0 synced`, `--check` exits `0`.
5. **Lint**: `uv tool run ruff@0.16.2 check scripts/sync-descriptions.py`.
