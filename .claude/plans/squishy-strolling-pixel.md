# Give `sizeokf` its behaviour: content sizes excluding frontmatter, with `-L`

## Context

`sizeokf` is currently a scaffold — it parses `--help` and `--version` and does
nothing. This change makes it do its job: report the **character count of
Markdown content, excluding YAML frontmatter**, per file and per folder
(folders recursive), with a `-L`/`--level` depth cap matching `inspectmd` and
`inspectokf`.

The reason to exclude frontmatter is not cosmetic. Measured on the current wiki:

| | chars |
| --- | --- |
| raw | 186,950 |
| frontmatter | 81,518 — **43.6%** |
| content | **105,432** |

So `du`, `wc -c` and every other byte-counting tool overstate the actual prose by
roughly a factor of two. No existing tool answers "how much writing is in this
category", which is the question that matters when deciding whether a page needs
splitting or a category is thin.

Four design decisions, confirmed with the user:

- **Fixed-width table** with a header row, in `inspectmd`'s house style.
- **Largest first**, so the answer to "what is big here" is the first row.
- **Chars + file count** columns — the count distinguishes "many short pages"
  from "few long ones" and is free while walking.
- **Copy the frontmatter logic** into `sizeokf` rather than share a module,
  honouring the repo's zero-overlap rule (`AGENTS.md`: "nothing shared").

## Behaviour

```
$ sizeokf -L 1
okf: 105,432 chars, 217 files

Chars    Files  Path
-------  -----  ---------------------
 21,324     43  british-history/
 19,030     38  ancient-world/
 11,612     29  popular-culture/
  7,849     15  american-history/
    ...
  1,773      1  index.md
    460      1  log.md
```

Rules, all to be stated in the README:

- **Only `*.md` files count.** Non-Markdown (`.okflintrc.json`, `.DS_Store`) is
  ignored entirely — neither listed nor counted.
- **Characters, not bytes** — `len(str)` after UTF-8 decode, including newlines.
  The wiki has 1,104 multi-byte characters, so this differs from `wc -c` by ~0.6%.
- **Directory rows are always recursive**, regardless of `-L`. This is the thing
  `tree --du -L 1` gets wrong (it reports 544 bytes for a 60K category).
- **`-L N` limits which entities get a row**, exactly like `inspectokf -L N`:
  `-L 1` lists the 13 categories plus `index.md`/`log.md` (15 rows); unlimited
  lists every file too. Default unlimited, `N` must be ≥ 1.
- **Sort is global across all listed rows**, largest first, ties broken
  alphabetically by path so output is deterministic. (At `-L 1` — the common
  case, and all this wiki supports since it is only one level deep — global and
  per-parent sorting are identical.)
- **Trailing `/` on directory rows** to distinguish them from files at a glance.
- A directory containing no `.md` files still gets a row, with `0`.

## Implementation

Mirror `inspectmd`'s two-module split (`parse.py` + `cli.py`):

**`sizeokf/src/sizeokf/sizes.py`** (new)

- `strip_frontmatter(text: str) -> str` — a copy of the semantics in
  `inspectmd/src/inspectmd/parse.py:60` (`split_frontmatter`), simplified to
  return just the body since `sizeokf` needs no line offsets. Preserve all its
  edge cases: strip a leading BOM; text not starting with `---` is unchanged; a
  first line that is not exactly `---` after stripping is unchanged; an
  **unterminated** block is treated as *no* frontmatter. The body starts at the
  line after the closing `---`, so a blank line following it is counted — same
  as `inspectmd`, and matches the 105,432 figure above.
- `Entry` frozen dataclass: `path` (relative to the root), `is_dir`, `chars`,
  `files`, `depth`.
- `collect(root: Path, *, max_level: int | None) -> tuple[list[Entry], Entry]` —
  one walk computing recursive totals for every directory, returning the listed
  entries plus a root total for the summary line.

**`sizeokf/src/sizeokf/cli.py`** (rewrite)

- `format_table(entries) -> str` — same column-width algorithm as
  `inspectmd/src/inspectmd/cli.py:14` `format_table`: compute widths from
  headers and rows, join with two spaces, emit a `---` rule row. Thousands
  separators on the numeric columns; right-align them.
- `_build_parser()` — add a `path` positional (`nargs="?"`, default `Path("okf")`)
  and `-L`/`--level` (`type=int`, `metavar="N"`), keeping `--version`.
- `main()` — validate `--level >= 1` **before** the path check, reusing the exact
  message shape from `inspectokf/src/inspectokf/cli.py`:
  `sizeokf: --level must be 1 or greater (got N)`, exit `2`. Then
  `sizeokf: not a directory: <path>`, exit `2`. Print summary line, blank line,
  table. Exit `0`.
- Per-file read errors (`OSError`, `UnicodeDecodeError`) warn on stderr, count
  the file as `0` chars, and do not abort the walk — one unreadable file must not
  lose the other 216 results.

**Tests** — mirror `inspectmd`'s split into two files:

- `sizeokf/tests/test_sizes.py` — `strip_frontmatter` edge cases (present,
  absent, BOM, unterminated, `---` inside body, empty file, frontmatter-only
  file); `collect` recursion, `.md`-only filtering, and depth limiting, built on
  `tmp_path` fixtures.
- `sizeokf/tests/test_cli.py` — keep the existing `--version`/`--help`/unknown-flag
  tests; replace the two "does nothing" and "no positional" tests, which now
  assert the opposite. Add: table renders with header and totals; `-L 1` and
  `--level 1` agree; `--level 0`/`-1` exit `2` naming `--level`; missing
  directory exits `2`; sort is descending with alphabetical tie-break; a
  directory with no Markdown reports `0`.

## Docs

The "scaffold, no behaviour yet" wording must go everywhere it appears:

- `sizeokf/README.md` — rewrite: drop the scaffold note, document the columns,
  the frontmatter rule, `-L`, and exit codes.
- `README.md` (root) — the `sizeokf/` table row.
- `AGENTS.md` (root) — the `sizeokf/` repository-map paragraph.
- `pi/spec.yaml` — the `Installed tools` bullet becomes
  `` - `sizeokf` — Markdown content size, excluding frontmatter ``.
- `pi/files/home/.pi/agent/AGENTS.md` — **new** section, alongside the existing
  `inspectmd` and `inspectokf` ones: how to survey wiki size, starting shallow
  with `sizeokf -L 1`, and that the number is content only, so it is comparable
  across pages regardless of frontmatter bulk.

No `.cspell.json` change expected (`frontmatter` and `sizeokf` are both already
listed) — the lint run confirms.

## Verification

```bash
make test-sizeokf      # new suites, offline
make lint              # ruff, markdownlint, cspell
make validate          # REQUIRED: pi/ changed
```

Then against the real wiki, checking the numbers derived during design:

```bash
uv cache clean sizeokf && uv tool install --force --reinstall ./sizeokf

sizeokf -L 1                 # 15 rows; british-history/ first at 21,324
sizeokf | head -3            # summary must read: okf: 105,432 chars, 217 files
sizeokf -L 1 | wc -l         # 15 rows + summary + blank + 2 header lines
sizeokf --level 1 okf        # identical to -L 1
sizeokf -L 0 okf; echo $?    # our own message, exit 2
sizeokf /no/such; echo $?    # "not a directory", exit 2
sizeokf okf/science-nature   # 3,294 chars, 7 files
```

Cross-check the total independently — it must equal 105,432, i.e. raw minus
frontmatter, **not** the 188,054 that `wc -c` reports:

```bash
find okf -name '*.md' -exec cat {} + | wc -c    # 186,950 raw chars (differs: includes frontmatter)
```

Note `uv tool install --force` reuses a cached wheel when the version is
unchanged — hence the `uv cache clean` above; this bit us on `inspectokf`.

Finally, on the host, since `pi/` changed:

```bash
sbx rm --force md2okf && make test-sandbox
```
