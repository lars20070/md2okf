# inspectokf

Print a directory tree for an OKF wiki folder by wrapping the `tree` CLI.
Default path is `okf/`; pass any existing directory (typically a wiki subfolder).

Stdlib only at runtime. Requires `tree` on PATH (installed in the sandbox).

## Commands

```bash
# Install onto PATH (host)
make install-inspectokf
inspectokf --version
inspectokf
inspectokf okf/
inspectokf okf/the-rest-is-history

# Without installing
uv tool run --from ./inspectokf inspectokf okf
```

Exit codes: `0` ok, `2` usage or runtime error (missing directory, `tree` missing,
or `tree` failed).

## Layout

| Path | Contents |
| --- | --- |
| `src/inspectokf/` | installable package (`cli`) |
| `tests/` | offline pytest suite (mocks `tree`) |
| `pyproject.toml` | hatchling build, ruff, pytest — own project, nothing shared |

## Tests

```bash
make test-inspectokf

# The same, directly:
uv run --project inspectokf --group test pytest -c inspectokf/pyproject.toml
```
