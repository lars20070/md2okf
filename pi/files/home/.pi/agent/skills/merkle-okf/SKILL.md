---
name: merkle-okf
description: Confirm which wiki pages a run actually changed via Merkle hashes. Use before and after writing under okf/.
---

# Confirm what changed with `merkleokf`

Use the `merkleokf` CLI (on `PATH`) to localise edits under `okf/`. The skill
name is `merkle-okf`; the binary is `merkleokf` — never shell the skill id.

## Invocation

```bash
merkleokf -L 1                     # categories — capture before and after
merkleokf okf/<topic>              # descend where a hash moved
merkleokf okf/<topic>/<page>.md    # a single file
```

- Default path: `okf/`. Pass a directory or a single Markdown file.
- `-L`/`--level N` lists entries at most `N` directory levels deep (`N` ≥ 0;
  `0` = walk root only; ignored for a file). Default: unlimited. Digests always
  cover the full subtree.
- Exit codes: `0` ok, `2` usage or runtime error.

## Workflow

Needs a **before** and an **after** listing — one post-write run alone cannot
localise anything.

1. Before writing: `merkleokf -L 1` and keep the listing.
2. After writing: run it again and diff against the baseline.
3. Descend only into folders whose hash moved; folders whose hash is unchanged
   are provably untouched.

## Reading the output

A table (no summary line). The walk root is always the first path listed when
sorted alphabetically:

| Column | Meaning |
| --- | --- |
| `Hash` | First 12 hex characters of the SHA-256 digest (Merkle digest for folders). |
| `Files` | Markdown files covered. Always `1` for a file. |
| `Path` | Rooted at the hashed directory's name (e.g. `okf/…`). Folders end in `/`. |

Rows are sorted alphabetically so two runs diff line by line.

## Limits

- Hashes **raw bytes — frontmatter included**. A timestamp or tag edit counts as
  a change (unlike `sizeokf`).
- A moved hash proves *that* something changed, never that the change is
  correct. Lint still gates conformance.
