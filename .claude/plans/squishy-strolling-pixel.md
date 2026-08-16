# Give `merkleokf` its behaviour: a Merkle hash tree, with `-L`

## Context

`merkleokf` is currently a scaffold — it parses `--help` and `--version` and does
nothing. This change makes it compute a **Merkle hash tree** over an OKF wiki: a
content hash per Markdown file, and a hash per directory derived from its
children, so a change to any leaf propagates to exactly one chain of parents.
A `-L`/`--level` depth cap matches `inspectmd`, `inspectokf` and `sizeokf`.

The point is cheap change localisation. Verified on the real wiki during design:
editing **one** leaf file changed the root hash and exactly **one** of 15
top-level rows; the other 13 categories stayed byte-identical. So an agent reads
15 lines, sees which category moved, and descends — instead of diffing 217 files.

Today the alternative is hand-rolled git plumbing (`GIT_INDEX_FILE` +
`git add -Af` + `git write-tree` + `git ls-tree`), which works but leaks objects
unless redirected, silently includes `.DS_Store`, and gives `-` for every
directory size.

Four design decisions, confirmed with the user:

- **Raw file bytes** are hashed — *not* frontmatter-stripped content. This makes
  `merkleokf` the integrity tool and `sizeokf` the prose tool: any byte change,
  including a timestamp bump, moves the hash. Consequence: a regeneration that
  rewrites the 164 shared `2026-08-11` timestamps will light up the whole tree,
  and that is the intended, honest answer.
- **Only `*.md` files** feed the tree, matching `sizeokf`. `.DS_Store` (live in
  `okf/` today, and rewritten whenever Finder looks at the folder) and
  `.okflintrc.json` are both ignored, so hashes never flap from OS noise.
- **12 hex characters** displayed, from SHA-256. 48 bits: collision odds ~8e-11
  at 217 files, ~2e-7 at 10,000. Full digests are computed internally; only the
  display is truncated.
- **Alphabetical by path**, so two runs diff line-by-line — the entire point.

**This combination means `merkleokf` shares no logic with `sizeokf`.** Hashing
raw bytes removes any need to duplicate `strip_frontmatter`, so there is no
second copy to keep in sync.

## Behaviour

```
$ merkleokf -L 1
okf: 86c7544437e0, 217 files

Hash          Files  Path
------------  -----  ----------------------
51766f25dfdd     15  american-history/
15d3bec65739     38  ancient-world/
5423a3e28d49     43  british-history/
...
55dc280ffc06      1  index.md
59d43a1b974d      1  log.md
```

Those are the **real** hashes for the current wiki, computed twice during design
(a standalone prototype and a second independent script agreed). They are the
verification anchors below.

Rules, all to be stated in the README:

- **Directory digest construction**: children sorted by name, each contributing
  a type tag, its name, and its digest — `b"d" + name + digest` for directories,
  `b"f" + name + digest` for files. Names must be included or a rename is
  invisible; type tags must be included or a file and a directory of the same
  name collide; sorting must be explicit or the hash is not reproducible across
  filesystems.
- **Directory hashes are always full-depth recursive**, whatever `-L` says. `-L`
  decides which entries get a row, never what they cover.
- **`-L N`** lists entries at most `N` levels deep, exactly like `inspectokf -L N`.
  Default unlimited; `N` must be ≥ 1.
- **A file argument is allowed** — `merkleokf okf/index.md` prints that one
  file's hash. `-L` is accepted but has no effect on a file.
- **No decoding.** Files are read as bytes, so there is no encoding to get wrong
  and no `UnicodeDecodeError` path. An unreadable file is reported on stderr and
  contributes a zero digest rather than aborting the walk.
- **Symlinks are not followed** into directories, avoiding cycles.
- A directory with no Markdown still gets a row: the digest of an empty child
  list, and `0` files.

## Implementation

Mirror the `sizeokf` module split (`sizes.py` + `cli.py`), which mirrors
`inspectmd`'s:

**`merkleokf/src/merkleokf/merkle.py`** (new)

- `DISPLAY_WIDTH = 12` — one named constant, so the truncation is not scattered.
- `hash_file(path: Path) -> bytes` — SHA-256 over raw bytes.
- `Entry` frozen dataclass: `path` (relative, directories end in `/`), `is_dir`,
  `digest` (full bytes), `files`, `depth`.
- `collect(root, *, max_level) -> tuple[list[Entry], Entry]` — one walk returning
  the listed entries plus a root `Entry` for the summary line. Entries sorted by
  path. Reuse the shape of `sizeokf/src/sizeokf/sizes.py` `collect`, which
  already does recursive totals with a `max_level` listing cap.

**`merkleokf/src/merkleokf/cli.py`** (rewrite)

- `format_table(entries)` — same column-width algorithm as
  `sizeokf/src/sizeokf/cli.py:15` `format_table`: widths from headers and rows,
  two-space join, `---` rule row. Columns `Hash`, `Files`, `Path`; `Files`
  right-aligned, `Hash` and `Path` left.
- `_build_parser()` — `path` positional (`nargs="?"`, default `Path("okf")`),
  `-L`/`--level`, `--version`.
- `main()` — validate `--level >= 1` first, reusing the exact message shape from
  `sizeokf`/`inspectokf`: `merkleokf: --level must be 1 or greater (got N)`,
  exit `2`. Then dispatch on the path: a file prints `<hash>  <name>`; a
  directory prints the summary line, a blank line, then the table; anything else
  is `merkleokf: not a file or directory: <path>`, exit `2`.

**Tests** — two files, mirroring `sizeokf`:

- `merkleokf/tests/test_merkle.py` — digest determinism (same tree, same hash);
  **change propagation** (edit one leaf → its parent and the root move, siblings
  do not) — the central property, tested on a `tmp_path` fixture; renaming a file
  changes the parent hash; a file and a directory of the same name produce
  different digests; non-`.md` files and dotfiles are ignored; `max_level` limits
  listing but not coverage; empty directory.
- `merkleokf/tests/test_cli.py` — keep `--version`/`--help`/unknown-flag; replace
  the two scaffold tests; add table rendering, `-L 1` vs `--level 1` agreement,
  `--level 0`/`-1` exit `2`, missing path exit `2`, and the single-file form.

## Docs

Remove "scaffold, no behaviour yet" everywhere it appears:

- `merkleokf/README.md` — rewrite: columns, the raw-bytes/`*.md`-only rules, the
  12-hex truncation and why, `-L`, the file form, exit codes.
- `README.md` (root) — the `merkleokf/` table row.
- `AGENTS.md` (root) — the `merkleokf/` repository-map paragraph, noting the
  deliberate split from `sizeokf` (integrity vs prose) and that no code is shared.
- `pi/spec.yaml` — bullet becomes
  `` - `merkleokf` — wiki Merkle hash tree, for change detection ``.
- `pi/files/home/.pi/agent/AGENTS.md` — **new** section after the `sizeokf` one:
  run `merkleokf -L 1` before and after editing; a category whose hash moved is
  where the edits landed, one whose hash did not is provably untouched. State
  plainly that it hashes raw bytes, so frontmatter changes count.

No `.cspell.json` change expected — `merkleokf` and `Merkle` both already pass.

## Verification

```bash
make test-merkleokf    # new suites, offline
make lint              # ruff, markdownlint, cspell
make validate          # REQUIRED: pi/ changed
```

Then against the real wiki, checking the hashes derived during design — these
are exact, not approximate:

```bash
uv cache clean merkleokf && uv tool install --force --reinstall ./merkleokf

merkleokf -L 1               # root 86c7544437e0, 217 files, 15 rows
                             # american-history/ 51766f25dfdd, ancient-world/ 15d3bec65739
merkleokf --level 1 okf      # identical to -L 1
merkleokf -L 0 okf; echo $?  # our own message, exit 2
merkleokf /no/such; echo $?  # exit 2
merkleokf okf/index.md       # single-file form, one hash
```

Then prove the property the tool exists for, on a copy so `okf/` is untouched:

```bash
cp -r okf /tmp/mk && merkleokf -L 1 /tmp/mk > /tmp/before.txt
printf '\nx\n' >> /tmp/mk/science-nature/dinosaurs.md
merkleokf -L 1 /tmp/mk > /tmp/after.txt
diff /tmp/before.txt /tmp/after.txt   # expect exactly 2 rows changed: root + science-nature/
```

Cross-check the root against git's own Merkle implementation, which should agree
on *which* subtree moved even though the digests differ (git uses SHA-1 blob/tree
objects):

```bash
GIT_INDEX_FILE=/tmp/mk.idx GIT_OBJECT_DIRECTORY=/tmp/mk.obj \
  git add -Af okf && git ls-tree "$(git write-tree)" okf/
```

Note `uv tool install --force` reuses a cached wheel when the version is
unchanged — hence `uv cache clean`; this bit us on `inspectokf`.

Finally, on the host, since `pi/` changed:

```bash
sbx rm --force md2okf && make test-sandbox
```
