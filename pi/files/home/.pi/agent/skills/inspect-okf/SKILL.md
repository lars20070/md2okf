---
name: inspect-okf
description: Survey what the OKF wiki already contains before writing. Use when choosing where to place or update pages under okf/.
---

# Survey the wiki with `inspectokf`

Use the `inspectokf` CLI (on `PATH`) to see what exists under `okf/`. The skill
name is `inspect-okf`; the binary is `inspectokf` — never shell the skill id.

## Invocation

```bash
inspectokf -L 1          # top level only: the categories — start here
inspectokf okf/<topic>   # then descend into the one category you need
inspectokf               # every page: hundreds of lines — avoid opening with this
```

- Default path: `okf/`. Pass any existing directory (typically a wiki subfolder).
- `-L`/`--level N` descends at most `N` directory levels (`N` ≥ 1). Default:
  unlimited.
- Output is the `tree` listing of that path. An empty or dotfile-only directory
  exits `0` with `0 directories, 0 files` and does not require `tree`.
- Exit codes: `0` ok, `2` usage or runtime error.

## Workflow

Shallow first, then descend into the one path that matters. Do not open with the
full unlimited tree.

## Reading the output

Each line is a path that exists on disk. Folders and files appear as `tree`
renders them. Use this to find pages already covering a topic before writing.

## Limits

- Hides **dotfiles**, so `.okflintrc.json` is invisible here.
- Slugs are lossy (`1981.md`, `exams.md` say nothing about content) — open the
  page when you need substance.
- A page listed here may still be **unreachable in the wiki** if no `index.md`
  links it; `okf-lint` does not catch that either.
