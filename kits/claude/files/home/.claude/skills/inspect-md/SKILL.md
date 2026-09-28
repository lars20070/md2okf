---
name: inspect-md
description: Map headings in a long Markdown source under ../md/ before reading it in ranges. Use when a source is too large to pull into one call.
---

# Map a long Markdown source with `inspectmd`

Use the `inspectmd` CLI (on `PATH`) to plan ranged reads under `../md/`. The
skill is `inspect-md`; the binary is `inspectmd` — never shell the skill name.

## Invocation

```bash
inspectmd ../md/<document>.md
inspectmd -L 2 ../md/<document>.md
inspectmd --section N ../md/<document>.md
```

- Requires a Markdown **file** path (not a directory).
- `-L`/`--level N` shows the preamble and headings through level `N` (`N` ≥ 1).
  Omit it to show every heading.
- `--section N` prints only `start:end  N words`; the range is 1-based and
  inclusive.
- Exit codes: `0` ok, `2` usage or runtime error.

## Workflow

Map → select → read. Here `-L` means heading depth, not directory depth.

1. Run `inspectmd -L 2 ../md/<document>.md` (or without `-L` if you need deeper
   headings).
2. Pick an `Index`, then run `inspectmd --section N ../md/<document>.md`.
3. Read the reported span. Each span ends before the next heading at **any**
   level, so a parent does not include its child sections; read those indices
   separately. Never pull a whole book into one call.

## Reading the output

| Column | Meaning |
| --- | --- |
| `Index` | Stable section number in document order; filtering with `-L` does not renumber it. `0` is the preamble when present, otherwise the first heading. |
| `Level` | Heading depth: `0` preamble, `1` = `#`, …, `6` = `######`. |
| `Lines` | 1-based inclusive line range (`start-end`) for that section. |
| `Words` | Whitespace-split word count of that range. |
| `Slug` | Kebab-case slug derived from the heading title. |
| `Title` | Heading text as written (or `(preamble)` / `(empty)`). |

## Limits

- Maps **ATX headings only** (`#` … `######`), ignores headings inside fenced
  code, and omits leading YAML frontmatter from section ranges.
- The map is a plan for cuts and reads — **not** permission to paraphrase source
  prose. The fidelity rule in `compile-okf` still governs.
