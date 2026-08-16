# inspectmd

Print a Markdown heading map: 1-based line ranges, character sizes, and
kebab-case slugs. Use it to plan ranged reads and page boundaries before opening
a long source under `md/`.

Stdlib only at runtime — no Markdown library. ATX headings only; fenced blocks
and YAML frontmatter are skipped; text before the first heading is section 0.

## Commands

```bash
# Install onto PATH (host)
make install-inspectmd
inspectmd --version
inspectmd md/GoogleStyleGuide.md
inspectmd -L 2 md/TheRestIsHistory.md
inspectmd --section 3 md/GoogleStyleGuide.md

# Without installing
uv tool run --from ./inspectmd inspectmd md/GoogleStyleGuide.md
```

Exit codes: `0` ok, `2` usage or runtime error (missing file, bad `--section`, or
a `--level` below `1`).

## Layout

| Path | Contents |
| --- | --- |
| `src/inspectmd/` | installable package (`parse`, `cli`) |
| `tests/` | offline pytest suite |
| `pyproject.toml` | hatchling build, ruff, pytest — own project, nothing shared |

## Tests

```bash
make test-inspectmd

# The same, directly:
uv run --project inspectmd --group test pytest -c inspectmd/pyproject.toml
```
