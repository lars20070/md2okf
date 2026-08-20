# sizeokf

Report how much Markdown **content** an OKF wiki holds, per file and per folder,
as whitespace-split word counts with YAML frontmatter excluded. Folder totals
are recursive.

Frontmatter is a large share of a generated wiki, so `du`, `wc -c` and `ls` all
overstate the actual prose. This reports what a reader would actually read, in
words.

Stdlib only at runtime.

## Commands

```bash
# Install onto PATH (host)
make install-clis
sizeokf --version
sizeokf                        # every file and folder in okf/
sizeokf -L 0                   # walk root only
sizeokf -L 1                   # top level only: the categories
sizeokf --nolog                # omit okf/log.md from listing and totals
sizeokf --level 2 okf
sizeokf okf/science-nature     # any subfolder

# Without installing
uv tool run --from ./scripts/sizeokf sizeokf -L 1 okf
```

```text
 Words  Files  Path
------  -----  --------------------------
18,742    217  okf/
 3,821     43  okf/british-history/
 3,410     38  okf/ancient-world/
 2,088     29  okf/popular-culture/
   312      1  okf/index.md
    81      1  okf/log.md
```

| Column | Meaning |
| --- | --- |
| `Words` | Whitespace-split words of content, frontmatter excluded. Recursive for folders. |
| `Files` | Markdown files counted. Always `1` for a file. |
| `Path` | Rooted at the measured directory name. Folders end in `/`. Walk root always listed. |

Rows are sorted largest first, ties broken alphabetically, so repeated runs are
byte-identical and easy to diff.

## What counts

- **Only `*.md` files.** Anything else — `.okflintrc.json`, `.DS_Store` — is
  neither listed nor counted.
- **Words, not characters or bytes.** `len(text.split())` after a UTF-8 decode
  and frontmatter strip. Punctuation stays attached to tokens.
- **Frontmatter is the leading `---` … `---` block only.** It must open on line
  one. An unterminated block is treated as no frontmatter, matching how
  `inspectmd` maps headings. The body begins after the closing `---`, so a blank
  line following it is counted.
- **Folder totals are always recursive**, whatever `-L` is set to. `-L` decides
  which entries get a row, never how they are summed — unlike `tree --du -L 1`,
  which silently reports a directory's own inode size instead of its contents.
- **`--nolog`** omits only `okf/log.md` from the listing and from all totals.
  Nested `log.md` files and `log.md` under other root names are still counted.
- A folder with no Markdown in it still gets a row, showing `0`.
- Symlinks are not followed, so directory cycles and links outside the root
  cannot hang or escape the walk.
- An unreadable file or directory is reported on stderr, counted as `0`, and
  does not abort the walk.

Exit codes: `0` ok, `2` usage or runtime error (missing directory, `--level`
below `0`).

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
make test-clis

# The same, directly:
uv run --project scripts/sizeokf --group test pytest -c scripts/sizeokf/pyproject.toml
```
