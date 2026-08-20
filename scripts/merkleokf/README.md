# merkleokf

Print a Merkle hash tree for an OKF wiki: a hash per Markdown file, and a hash
per directory derived from its children. A change to any page propagates to its
parent directories and to the root — and to nothing else.

That is what makes change detection cheap. Compare one root hash; if it moved,
read the 15-row `-L 1` listing, find the single category whose hash also moved,
and descend. Directories whose hash is unchanged are *provably* untouched, not
merely probably.

Stdlib only at runtime.

## Commands

```bash
# Install onto PATH (host)
make install-clis
merkleokf --version
merkleokf                      # every file and folder in okf/
merkleokf -L 1                 # top level only: the categories
merkleokf --level 2 okf
merkleokf okf/science-nature   # any subfolder
merkleokf okf/index.md         # a single file

# Without installing
uv tool run --from ./scripts/merkleokf merkleokf -L 1 okf
```

```text
Hash          Files  Path
------------  -----  --------------------------
86c7544437e0    217  okf/
51766f25dfdd     15  okf/american-history/
15d3bec65739     38  okf/ancient-world/
5423a3e28d49     43  okf/british-history/
55dc280ffc06      1  okf/index.md
59d43a1b974d      1  okf/log.md
```

| Column | Meaning |
| --- | --- |
| `Hash` | First 12 hex characters of the SHA-256 digest. Merkle digest for folders. |
| `Files` | Markdown files covered. Always `1` for a file. |
| `Path` | Rooted at the hashed directory name. Folders end in `/`. Walk root always listed. |

Rows are sorted alphabetically so two runs diff line by line — the entire point.
A subfolder hashed on its own gives the same digest as its row in the parent's
table.

## What is hashed

- **Raw file bytes**, frontmatter included. `merkleokf` is the integrity tool: a
  timestamp bump or a tag fix is a change and will move the hash. `sizeokf` is
  the one that ignores frontmatter and measures prose — the two answer different
  questions on purpose, and share no code.
- **Only `*.md` files.** `.DS_Store` and `.okflintrc.json` are ignored, so a
  hash never flaps because Finder looked at a folder.
- **Directory digests** cover their children sorted by name, each contributing a
  type tag, its name, and its digest (`d`/`f` + name + digest). Names are
  included so a pure rename is visible; type tags so a file and a directory of
  the same name cannot collide; sorting so the digest is reproducible across
  filesystems.
- **Folder digests are always full-depth recursive**, whatever `-L` is set to.
  `-L` decides which entries get a row, never what they cover.
- Symlinks are not followed, so cycles cannot hang the walk.
- A folder with no Markdown still gets a row, showing `0` files.
- An unreadable file is reported on stderr and contributes a zero digest rather
  than aborting the walk.

### Why 12 characters

48 bits: collision odds are about 8e-11 across today's 217 files and 2e-7 at
10,000. Full digests are always computed and compared internally; only the
display truncates. Printing all 64 hex characters would add roughly 190% to the
output of a full listing, which is a poor trade for a tool meant to be read.

## Layout

| Path | Contents |
| --- | --- |
| `src/merkleokf/` | installable package (`merkle`, `cli`) |
| `tests/` | offline pytest suite |
| `pyproject.toml` | hatchling build, ruff, pytest — own project, nothing shared |

Exit codes: `0` ok, `2` usage or runtime error (path is neither file nor
directory, `--level` below `1`).

## Tests

```bash
make test-clis

# The same, directly:
uv run --project scripts/merkleokf --group test pytest -c scripts/merkleokf/pyproject.toml
```
