---
name: inspectokf tree CLI
overview: Add a fourth independent uv project, inspectokf — installable CLI that prints `tree` for okf/ (or a given wiki subfolder) — with the same host/sandbox/CI wiring as inspectmd. V1 is a thin tree wrapper only.
todos:
  - id: package
    content: Create inspectokf/ package (cli tree wrapper, pyproject, lock, README, tests)
    status: pending
  - id: host-ci
    content: Wire Makefile, CI test-inspectokf, root docs
    status: pending
  - id: sandbox-docs
    content: Add pi/spec.yaml shim + agentInstructions; guest check; Pi AGENTS note; validate
    status: pending
isProject: true
---

# Add `inspectokf` CLI (tree wrapper)

## Scope (v1)

```bash
inspectokf              # defaults to okf
inspectokf okf/
inspectokf okf/the-rest-is-history
```

- Stdlib-only Python package; runs host/sandbox `tree` via `subprocess` and prints its stdout/stderr.
- Exit `0` on success, `2` on usage/runtime (missing path, not a directory, `tree` not on PATH, non-zero `tree`).
- `--version` via `importlib.metadata` (same pattern as inspectmd).
- No Markdown parsing, no `--json`, no okf-lint. Path may be any existing directory; docs say it is for the wiki under `okf/`.

## Package layout

Mirror [`inspectmd/`](../inspectmd/) as a **fourth** independent uv project (own `pyproject.toml`, `uv.lock`, ruff, pytest — zero overlap):

```text
inspectokf/
  pyproject.toml          # hatchling; scripts; test group; [tool.ruff] copy of inspectmd’s
  uv.lock
  README.md
  src/inspectokf/
    __init__.py           # __version__ from importlib.metadata
    __main__.py
    cli.py                # argparse + tree subprocess + main/entrypoint
  tests/
    test_cli.py           # success (mocked tree), missing dir → 2, no tree → 2, --version
```

[`inspectokf/pyproject.toml`](../inspectokf/pyproject.toml): `requires-python = ">=3.12"`, no runtime deps, `[project.scripts] inspectokf = "inspectokf.cli:entrypoint"`, same pytest/ruff block as inspectmd.

CLI essentials in `cli.py`:

- Positional `path` defaulting to `okf` (`nargs="?"`, `default=Path("okf")`).
- Validate `path.is_dir()`; else stderr + exit 2.
- `shutil.which("tree")`; if missing, stderr + exit 2.
- `subprocess.run(["tree", str(path)], capture_output=False)` (inherit stdio) or capture-and-forward; return 0 if tree exit 0 else 2.

## Delivery (same as inspectmd)

### Host

- [`Makefile`](../Makefile): `test-inspectokf`, `install-inspectokf`; fold into `test:` and `.PHONY`.
- [`.github/workflows/ci.yml`](../.github/workflows/ci.yml): `test-inspectokf` job mirroring `test-inspectmd`.
- Ruff auto-picks up via tracked `*/pyproject.toml` — no lint Makefile change.

### Sandbox — [`pi/spec.yaml`](../pi/spec.yaml)

- agentInstructions “Installed tools”: `` `inspectokf` — wiki directory tree (via `tree`) ``
- `setup.files` shim (beside inspectmd):

```yaml
- path: /home/agent/.local/bin/inspectokf
  mode: "0755"
  description: Workspace-backed inspectokf CLI
  content: |
    #!/bin/sh
    set -eu
    exec uv tool run --from "${WORKDIR}/inspectokf" inspectokf "$@"
```

`tree` is already installed and checked in the guest script.

### Guest test — [`tests/test-sandbox-guest.sh`](../tests/test-sandbox-guest.sh)

`check inspectokf` next to `check inspectmd`.

### Docs

- Root [`AGENTS.md`](../AGENTS.md) / [`README.md`](../README.md): fourth Python project; `make test-inspectokf` / `make install-inspectokf`.
- Pi [`AGENTS.md`](../pi/files/home/.pi/agent/AGENTS.md): short “Survey the wiki with `inspectokf`” note (default `okf`, optional subfolder) — no separate Pi skill in v1 (matches current inspectmd: docs in AGENTS, no skill dir).
- [`inspectokf/README.md`](../inspectokf/README.md): one-page usage.
- cspell: add `inspectokf` if needed.

No dedicated Pi skill directory for v1.

## Verify

```bash
uv lock --project inspectokf
make test-inspectokf
make lint
make validate
make install-inspectokf && inspectokf okf
# when logged in: sbx rm --force md2okf && make test-sandbox
```

## Out of scope

OKF frontmatter/index analysis, `okf-lint` wrapping, Markdown heading maps, requiring the path to live under `okf/`, and a Pi skill package.
