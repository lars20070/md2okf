# Add `--level` / `-L` to `inspectokf`, and rename `inspectmd --max-depth` to match

## Context

`inspectokf` shells out to `tree` with no options, so it has exactly one output:
the entire wiki. On the current `okf/` that is **233 lines** listing 217 page
slugs. That is a large, low-density chunk of context for a Pi run whose real
question is usually "which category does this episode belong in?", and it grows
linearly with the wiki.

`tree` already solves this with `-L`. Measured on the current wiki, `tree -L 1 okf`
is **17 lines** and shows the 13 categories plus `index.md`/`log.md` — the shape of
the wiki without the payload. Exposing that flag lets the Pi agent orient cheaply
and then drill into one category, instead of paying for every filename up front.

The sibling CLI `inspectmd` already has this exact concept under a different name,
`--max-depth`. Rather than let the two tools spell one idea two ways, `inspectmd`
adopts `--level` / `-L` as well. That is the better name for `inspectmd` on its own
terms, not just for symmetry: its output table already has a **`Level`** column
(`0` preamble, `1` = `#`, …), so `--level 2` names the column it filters, where
`--max-depth` introduced a second word for the same thing.

**Default stays unlimited in both tools.** Omitting `-L` prints the full tree /
full heading map exactly as today, so depth is purely opt-in.

## Changes

### 1. `inspectokf/src/inspectokf/cli.py` — new flag

Add to `_build_parser()`, alongside the existing `path` / `--version`:

```python
parser.add_argument(
    "-L",
    "--level",
    type=int,
    metavar="N",
    help="descend at most N directory levels (default: unlimited)",
)
```

In `main()`, validate **before** the path and `tree` checks, so the error is
deterministic regardless of cwd and does not require `tree` to be installed.
`tree -L 0` fails with its own message (`tree: Invalid level, must be greater than
0.`, exit 1); catching it in Python keeps the `inspectokf: ` prefix consistent with
the existing `not a directory` error and keeps the failure testable offline:

```python
level: int | None = args.level
if level is not None and level < 1:
    print(f"inspectokf: --level must be 1 or greater (got {level})", file=sys.stderr)
    return 2
```

Build the command incrementally, leaving the no-flag call byte-identical to today:

```python
command = [tree_bin]
if level is not None:
    command += ["-L", str(level)]
command.append(str(path))
completed = subprocess.run(command, check=False)  # noqa: S603
```

Exit codes unchanged: `0` ok, `2` usage or runtime error.

### 2. `inspectokf/tests/test_cli.py`

The two existing exact-call assertions (`test_main_success`,
`test_main_default_path`) must keep passing untouched — that is the
backward-compat guarantee. Add, following the established `monkeypatch` +
`MagicMock` style:

- `-L 2` produces `["/usr/bin/tree", "-L", "2", str(wiki)]`
- `--level 1` produces the same call as `-L 1` (both spellings agree)
- invalid levels (`0` and `-1`, via `pytest.mark.parametrize` — `PT` rules are on)
  return `2`, mention `--level` on stderr, **and never call `subprocess.run`**;
  assert the mock was not called, since not shelling out is the point
- `-L` combined with the default path still resolves to `okf`

### 3. `inspectmd/src/inspectmd/cli.py` — rename

A clean rename, no back-compat alias: `inspectmd` is an internal, unpublished
`0.1.0` tool whose only scripted caller is the Pi agent config updated in step 5.

- Replace the `--max-depth` argument (line ~95) with the same `-L` / `--level`
  block as above, help text `show only headings at this level or above (1=H1, …)`.
  argparse then gives `args.level`; update the call site at line ~144.
- Rename `format_table`'s keyword-only parameter `max_depth` → `max_level`
  (signature line 14, docstring lines 17–18, filter expression line 23) so the
  internal vocabulary matches the `Level` column and the new flag.

Filtering semantics are unchanged: preamble (level 0) plus headings with
`level <= N`.

No short-flag collision — `inspectmd` currently defines only `--section`,
`--max-depth`, and `--version`.

### 4. `inspectmd/tests/test_cli.py`

- `test_format_table_max_depth` (line 24) → `test_format_table_max_level`, calling
  `format_table(sections, max_level=2)`.
- `test_main_max_depth` (line 83) → `test_main_level`, invoking
  `main([str(path), "--level", "1"])`; add a case asserting `-L 1` gives identical
  stdout, so both spellings are covered.

### 5. `pi/files/home/.pi/agent/AGENTS.md` — agent instructions

Two sections, both currently naming the old interface:

- *"Mapping long Markdown sources with `inspectmd`"* (line 158) — change
  `inspectmd --max-depth 2 md/<document>.md` to `inspectmd -L 2 md/<document>.md`.
  The `Level` column row in the table below it already explains the vocabulary; no
  other edit needed there.
- *"Surveying the wiki with `inspectokf`"* (lines 176–186) — rewrite so the shallow
  view is the recommended **first** move, not a footnote:

  ```bash
  inspectokf -L 1          # categories only — start here
  inspectokf okf/<topic>   # then drill into one category
  inspectokf               # full tree: every page in the wiki
  ```

  Prose to convey: start shallow and drill down; the bare command lists every page
  and runs to hundreds of lines on a wiki this size. Keep the existing sentences
  about defaulting to `okf/` and accepting any existing directory.

### 6. Docs

- `inspectokf/README.md` — add `inspectokf -L 1` / `inspectokf --level 2 okf` to the
  Commands block; state that the default is unlimited depth and that a level below
  `1` exits `2`.
- `inspectmd/README.md` (line 17) — `inspectmd --max-depth 2 …` → `inspectmd -L 2 …`.
- `AGENTS.md` (root, repository map, ~line 41) — extend the `inspectokf/` sentence
  to note the depth cap.
- **No change** to `pi/spec.yaml` (line 35 is a tool inventory, not a usage guide),
  to `README.md`'s project table (names projects, not flags), or to
  `tests/test-sandbox-guest.sh` (`check inspectokf` is a PATH-presence check).

### Deliberately out of scope

`inspectmd --level 0` currently degrades gracefully (preamble only, or
`(no sections at this depth)`) while `inspectokf --level 0` will error, because one
filters in-process and the other wraps a subprocess that rejects `0`. Leaving that
as-is: making `inspectmd` reject `0` would change existing behaviour for input that
works today, which is beyond a rename. Flagging it since the flags now look alike.

No version bumps — all three projects sit at `0.1.0` and the repo has no release
process.

## Verification

```bash
make test-inspectokf            # inspectokf suite, offline (tree is mocked)
make test-inspectmd             # inspectmd suite, offline
make lint                       # ruff + markdownlint + cspell over the doc edits
make validate                   # REQUIRED: pi/ changed (scripts/validate-spec.sh)
```

Confirm the old flag is gone repo-wide, so no doc or test still teaches it:

```bash
rg -n 'max.depth|max_depth' --glob '!**/__pycache__/**' --glob '!**/.*_cache/**' .
```

Then exercise both real binaries:

```bash
make install-inspectokf && make install-inspectmd
inspectokf -L 1 okf             # expect ~17 lines, "14 directories, 2 files"
inspectokf okf | wc -l          # expect 233 — unchanged full-tree behaviour
inspectokf -L 0 okf; echo $?    # expect our own message, exit 2
inspectmd -L 2 md/<document>.md # same table as the old --max-depth 2
inspectmd --max-depth 2 md/<document>.md   # expect argparse "unrecognized arguments"
```

`tree` must be on PATH for the `inspectokf` runs (`apt-get install tree` in this
sandbox; the Pi sandbox installs it via `pi/spec.yaml:96`).

Finally, on the host — and this one matters more than usual here. `pi/spec.yaml`
shims both CLIs as `uv tool run --from "${WORKDIR}/<tool>"`, so a *running* sandbox
picks up the renamed flag from the mounted workspace immediately, while its copy of
`AGENTS.md` was baked in at kit build time and would still teach `--max-depth`. The
two must be rebuilt together:

```bash
sbx rm --force md2okf && make test-sandbox
```
