# merkleokf

Print a Merkle hash tree for an OKF wiki folder: a content hash per file and a
hash per directory derived from its children, so a change to any page propagates
to exactly one chain of parent directories.

**Scaffold only.** The CLI parses `--help` and `--version` and does nothing else;
there is no hashing yet. The project exists so that adding it later touches this
directory alone.

Stdlib only at runtime.

## Commands

```bash
# Install onto PATH (host)
make install-merkleokf
merkleokf --version
merkleokf --help
merkleokf          # no output

# Without installing
uv tool run --from ./merkleokf merkleokf --help
```

Exit codes: `0` ok, `2` usage error.

## Layout

| Path | Contents |
| --- | --- |
| `src/merkleokf/` | installable package (`cli`) |
| `tests/` | offline pytest suite |
| `pyproject.toml` | hatchling build, ruff, pytest — own project, nothing shared |

## Tests

```bash
make test-merkleokf

# The same, directly:
uv run --project merkleokf --group test pytest -c merkleokf/pyproject.toml
```
