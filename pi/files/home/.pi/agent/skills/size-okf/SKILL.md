---
name: size-okf
description: Measure how much Markdown prose a page or category holds, excluding YAML frontmatter. Use when judging whether a page is thin or a category is unbalanced.
---

# Measure wiki content with `sizeokf`

Use the `sizeokf` CLI (on `PATH`) to count content characters under `okf/`. The
skill name is `size-okf`; the binary is `sizeokf` — never shell the skill id.

## Invocation

```bash
sizeokf -L 1             # chars per category — start here
sizeokf okf/<topic>      # then per page within one category
sizeokf                  # every file and folder (large)
```

- Default path: `okf/`. Pass any existing directory.
- `-L`/`--level N` lists entries at most `N` directory levels deep (`N` ≥ 1).
  Default: unlimited. Folder **totals** are always recursive.
- Exit codes: `0` ok, `2` usage or runtime error.

## Workflow

Shallow first (`sizeokf -L 1`), then descend into the one category you care
about. Same `-L` pattern as `inspectokf`, different question: how much is
written, not what exists.

## Reading the output

Summary line, then a table:

| Column | Meaning |
| --- | --- |
| `Chars` | Characters of Markdown **content**, frontmatter excluded. Recursive for folders. |
| `Files` | Markdown files counted. Always `1` for a file. |
| `Path` | Relative to the measured directory. Folders end in `/`. |

Rows are sorted largest first.

## Limits

- Counts **content only** — says nothing about frontmatter bulk.
- Never use it to reason about frontmatter itself; use `merkleokf` when asking
  whether bytes changed.
