---
name: inspect-md
description: Map headings in a long Markdown source under md/ before reading it in ranges. Use when a source is too large to pull into one call.
---

# Map a long Markdown source with `inspectmd`

Use the `inspectmd` CLI (on `PATH`) to plan ranged reads of a file under `md/`.
The skill name is `inspect-md`; the binary is `inspectmd` — never shell the
skill id.

## Invocation

```bash
inspectmd md/<document>.md
inspectmd -L 2 md/<document>.md
inspectmd --section N md/<document>.md
```

- Requires a Markdown **file** path (not a directory).
- `-L`/`--level N` caps the map at heading level `N` (`N` ≥ 1). Omit for every
  heading.
- `--section N` prints only `start:end  N words` for a ranged read.
- Exit codes: `0` ok, `2` usage or runtime error.

## Workflow

Map → cut → read. Do **not** treat `-L` as a directory depth (that is the wiki
tools).

1. Run `inspectmd -L 2 md/<document>.md` (or without `-L` if you need deeper
   headings).
2. Pick a section `Index`, then `inspectmd --section N md/<document>.md`.
3. Ranged-read that line span — never pull a whole book into one call.

## Reading the output

| Column | Meaning |
| --- | --- |
| `Index` | Section number in document order (`0` = preamble when present). Pass this to `--section`. |
| `Level` | Heading depth: `0` preamble, `1` = `#`, …, `6` = `######`. |
| `Lines` | 1-based inclusive line range (`start-end`) for that section. |
| `Words` | Whitespace-split word count of that range. |
| `Slug` | Kebab-case slug from the heading title (same style as OKF file names). |
| `Title` | Heading text as written (or `(preamble)` / `(empty)`). |

## Limits

- Maps **ATX headings only** (`#` … `######`).
- The map is a plan for cuts and reads — **not** permission to paraphrase source
  prose. The fidelity rule in `compile-okf` still governs.
