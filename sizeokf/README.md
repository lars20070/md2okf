# sizeokf

Report sizes for an OKF wiki folder.

**Scaffold only.** The CLI parses `--help` and `--version` and does nothing else;
there is no size reporting yet. The project exists so that adding it later
touches this directory alone.

Stdlib only at runtime.

## Commands

```bash
# Install onto PATH (host)
make install-sizeokf
sizeokf --version
sizeokf --help
sizeokf            # no output

# Without installing
uv tool run --from ./sizeokf sizeokf --help
```

Exit codes: `0` ok, `2` usage error.

## Layout

| Path | Contents |
| --- | --- |
| `src/sizeokf/` | installable package (`cli`) |
| `tests/` | offline pytest suite |
| `pyproject.toml` | hatchling build, ruff, pytest — own project, nothing shared |

## Tests

```bash
make test-sizeokf

# The same, directly:
uv run --project sizeokf --group test pytest -c sizeokf/pyproject.toml
```
