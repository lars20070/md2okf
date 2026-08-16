# sizeokf

Report how much Markdown **content** an OKF wiki holds, per file and per folder,
with YAML frontmatter excluded. Folder totals are recursive.

Frontmatter is a large share of a generated wiki — 43.6% of the current `okf/` —
so `du`, `wc -c` and `ls` all overstate the actual prose by roughly a factor of
two. This reports what a reader would actually read.

Stdlib only at runtime.

## Commands

```bash
# Install onto PATH (host)
make install-sizeokf
sizeokf --version
sizeokf                        # every file and folder in okf/
sizeokf -L 1                   # top level only: the categories
sizeokf --level 2 okf
sizeokf okf/science-nature     # any subfolder

# Without installing
uv tool run --from ./sizeokf sizeokf -L 1 okf
```

```text
okf: 105,432 chars, 217 files

 Chars  Files  Path
------  -----  ----------------------
21,324     43  british-history/
19,030     38  ancient-world/
11,612     29  popular-culture/
 1,773      1  index.md
   460      1  log.md
```

| Column | Meaning |
| --- | --- |
| `Chars` | Characters of content, frontmatter excluded. Recursive for folders. |
| `Files` | Markdown files counted. Always `1` for a file. |
| `Path` | Relative to the measured directory. Folders end in `/`. |

Rows are sorted largest first, ties broken alphabetically, so repeated runs are
byte-identical and easy to diff.

## What counts

- **Only `*.md` files.** Anything else — `.okflintrc.json`, `.DS_Store` — is
  neither listed nor counted.
- **Characters, not bytes.** `len(str)` after a UTF-8 decode, newlines included.
  The current wiki has 1,104 multi-byte characters, so this differs from
  `wc -c` by about 0.6%.
- **Frontmatter is the leading `---` … `---` block only.** It must open on line
  one. An unterminated block is treated as no frontmatter, matching how
  `inspectmd` maps headings. The body begins after the closing `---`, so a blank
  line following it is counted.
- **Folder totals are always recursive**, whatever `-L` is set to. `-L` decides
  which entries get a row, never how they are summed — unlike `tree --du -L 1`,
  which silently reports a directory's own inode size instead of its contents.
- A folder with no Markdown in it still gets a row, showing `0`.
- An unreadable file is reported on stderr, counted as `0`, and does not abort
  the walk.

Exit codes: `0` ok, `2` usage or runtime error (missing directory, `--level`
below `1`).

## Layout

| Path | Contents |
| --- | --- |
| `src/sizeokf/` | installable package (`sizes`, `cli`) |
| `tests/` | offline pytest suite |
| `pyproject.toml` | hatchling build, ruff, pytest — own project, nothing shared |

`sizes.py` carries its own `strip_frontmatter`, deliberately duplicated from
`inspectmd` rather than shared: each project stays independently installable, so
the sandbox shims need no cross-project resolution. The two copies are pinned by
tests on both sides.

## Tests

```bash
make test-sizeokf

# The same, directly:
uv run --project sizeokf --group test pytest -c sizeokf/pyproject.toml
```
