# inspectokf

Print a directory tree for an OKF wiki folder by wrapping the `tree` CLI.
Default path is `okf/`; pass any existing directory (typically a wiki subfolder).
Depth is unlimited unless `-L`/`--level` caps it — `-L 1` lists the categories
without their pages, which is the cheap way to orient on a large wiki.

Stdlib only at runtime. Requires `tree` on PATH (installed in the sandbox).

## Commands

```bash
# Install onto PATH (host)
make install-clis
inspectokf --version
inspectokf
inspectokf okf/
inspectokf okf/the-rest-is-history
inspectokf -L 1
inspectokf --level 2 okf

# Without installing
uv tool run --from ./scripts/inspectokf inspectokf okf
```

Exit codes: `0` ok, `2` usage or runtime error (missing directory, a `--level`
below `1`, `tree` missing, or `tree` failed).

## Layout

| Path | Contents |
| --- | --- |
| `src/inspectokf/` | installable package (`cli`) |
| `tests/` | offline pytest suite (mocks `tree`) |
| `pyproject.toml` | hatchling build, ruff, pytest — own project, nothing shared |

## Tests

```bash
make test-clis

# The same, directly:
uv run --project scripts/inspectokf --group test pytest -c scripts/inspectokf/pyproject.toml
```
