---
name: size-okf
description: Measure how much Markdown prose a page or category holds, excluding YAML frontmatter. Use when judging whether a page is thin or a category is unbalanced.
---

# Measure wiki content with `sizeokf`

Use the `sizeokf` CLI (on `PATH`) to count content words in the wiki. The
skill name is `size-okf`; the binary is `sizeokf` — never shell the skill id.

## Invocation

```bash
sizeokf -L 1 "$PWD"          # words per category — start here
sizeokf "$PWD/<topic>"       # then per page within one category
sizeokf "$PWD"               # every file and folder (large)
```

- **Always name the wiki as `"$PWD"`**. You are already in the wiki root; the
  CLI's own default (`okf/`) is for host-side use and would select an invalid
  nested `okf/` directory here. The absolute path also preserves the root name
  that `--nolog` relies on. Any existing directory works.
- `-L`/`--level N` lists entries at most `N` directory levels deep (`N` ≥ 0;
  `0` = walk root only). Default: unlimited. Folder **totals** are always
  recursive.
- `--nolog` omits the wiki's root `log.md` from the listing and totals (nested
  `log.md` still counted).
- Exit codes: `0` ok, `2` usage or runtime error.

## Workflow

Shallow first (`sizeokf -L 1`), then descend into the one category you care
about. Same `-L` pattern as `inspectokf`, different question: how much is
written, not what exists.

## Reading the output

A table (no summary line). The walk root is always listed:

| Column | Meaning |
| --- | --- |
| `Words` | Whitespace-split words of Markdown **content**, frontmatter excluded. Recursive for folders. |
| `Files` | Markdown files counted. Always `1` for a file. |
| `Path` | Rooted at the measured directory's name (e.g. `okf/…`). Folders end in `/`. |

Rows are sorted largest first.

## Limits

- Counts **content only** — says nothing about frontmatter bulk.
- Never use it to reason about frontmatter itself; use `merkleokf` when asking
  whether bytes changed.
