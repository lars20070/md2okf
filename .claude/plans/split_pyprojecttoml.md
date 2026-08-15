# Split the root pyproject.toml into pdf2md/ and web2md/

## Context

Today one root `pyproject.toml` + one root `uv.lock` serve two unrelated
things: `marker-pdf`/`psutil` for the manual `pdf2md` step, and the `web2md`
scraper's own runtime/test deps plus repo-wide `ruff`/`yamllint`. They're kept
apart today only by `dependency-groups` + `--only-group` gymnastics in the
Makefile/CI, specifically so linting and testing never pull in `marker-pdf`'s
heavy torch chain.

The user wants `pdf2md` and `web2md` to become two **entirely independent**
uv projects — own `pyproject.toml`, own `uv.lock`, no shared root file, no
overlap. This plan does that, and updates every place that currently assumes
a single root project: `Makefile`, CI, `AGENTS.md`, `README.md`, both
sub-READMEs, and `.coderabbit.yaml`.

`pdf2md/pyproject.toml` has no first-party Python of its own to lint or test —
its whole purpose is letting someone spin up an isolated venv that has
`marker` installed. `uv run --project pdf2md marker ...` (or `uv sync
--project pdf2md` up front) creates and populates `pdf2md/.venv` on first use,
which is the entire point of the file: a pinned, disposable environment for
running the third-party `marker` CLI, not a package to build or test.

## Design decisions (already validated empirically in this sandbox)

- **`ruff`/`yamllint` become ephemeral**, run via `uv tool run ruff` / `uv tool
  run yamllint` (the `uvx` equivalent — confirmed working here even though the
  standalone `uvx` shim isn't installed in this sandbox). They are declared in
  **no** `pyproject.toml`. This is what makes "no overlap" possible: repo-wide
  lint tooling isn't owned by either project. Verified `ruff check <dir>`
  correctly picks up that subproject's own `[tool.ruff]` config via ruff's
  normal upward config discovery.
- **`[tool.ruff]` config moves into `web2md/pyproject.toml`** — the only
  project with lintable first-party Python today. `pdf2md/pyproject.toml`
  carries no lint config since it has no `.py` files of its own.
- **`make lint` runs ruff once per subproject, not once over the whole repo.**
  Instead of `$(RUFF) check .`, it derives the subproject list from tracked
  `*/pyproject.toml` files (`git ls-files -- '*/pyproject.toml' | xargs -n1
  dirname | xargs $(RUFF) check`) — the same "driven by `git ls-files`, not a
  hand-maintained list" philosophy the rest of `lint`'s exclusions already
  follow (see the target's own comment). Today that's just `web2md`; the
  moment a future subproject (e.g. a Python `pdf2md` or a new `inspectmd`)
  gets its own tracked `pyproject.toml`, `make lint` picks it up automatically
  with no Makefile edit required.
- **Invocation uses `uv run --project <dir> ...`**, not `cd`/`--directory`.
  For `marker` (pdf2md) this is sufficient alone: CWD stays at the repo root,
  so the existing `pdf/`/`md/` relative paths in `pdf2md/README.md` keep
  working unchanged. For `pytest` (web2md), `--project` alone does **not**
  relocate pytest's own config discovery (verified: `uv run --project web2md
  pytest` alone fails with `ModuleNotFoundError`), so it's paired with
  `pytest -c web2md/pyproject.toml`, which correctly resolves `testpaths`/
  `pythonpath` relative to that file's directory (verified: passes).
- **web2md's runtime deps (`httpx`, `beautifulsoup4`, `lxml`, `markdownify`)
  move from a `web2md` dependency-group into plain `[project].dependencies`.**
  Today they're a separate group so `--only-group test` (CI) can skip them
  along with the heavy root deps; verified `--only-group` excludes
  `[project].dependencies` entirely. Once `web2md` is its own project,
  `marker-pdf` can never be in its dependency graph, so there's nothing left
  to exclude — CI can use the exact same `--group test` invocation as local
  dev. **This drops the CI-specific `--only-group` override for pytest
  entirely**, and drops the CI-specific overrides for ruff/yamllint too
  (verified via the ephemeral-tool decision above).
- **`psutil` moves to `pdf2md/pyproject.toml`** alongside `marker-pdf` — it
  has been paired with `marker-pdf` since the first commit (`3c994d7`), and a
  repo-wide grep found no other usage.
- Both new projects get their **own committed `uv.lock`**, matching the
  current convention of tracking the root lockfile. The root `pyproject.toml`
  and `uv.lock` are deleted.
- `.gitignore` needs **no changes** — `.venv/`, `.pytest_cache/`,
  `.ruff_cache/` are unanchored patterns (no leading `/`), so they already
  match at any depth, including `pdf2md/.venv/` and `web2md/.venv/`.
- `.python-version` at the repo root is left as-is; uv resolves a Python
  version per-project via `requires-python` regardless, so no per-project
  copy is needed.

## Files to create

**`pdf2md/pyproject.toml`**
```toml
[project]
name = "pdf2md"
version = "0.1.0"
description = "Convert a PDF into Markdown with marker"
requires-python = ">=3.12"
dependencies = ["marker-pdf>=1.10.2", "psutil>=7.2.2"]

# No [build-system]: pdf2md has no first-party Python of its own. This file
# only pins marker's own dependency versions; commands run with
# `uv run --project pdf2md marker ...` (see README.md).
```

**`web2md/pyproject.toml`** — carries the scraper's runtime deps as regular
`[project].dependencies`, the `test` group, `[tool.pytest.ini_options]` (paths
now relative to this file: `testpaths = ["tests"]`, `pythonpath = ["src"]`),
and the full `[tool.ruff]` block moved verbatim from today's root file (with
`per-file-ignores` key changed from `"web2md/tests/*"` to `"tests/*"`).

**`pdf2md/uv.lock`**, **`web2md/uv.lock`** — generated via `uv lock --project
pdf2md` and `uv lock --project web2md`, committed.

## Files to delete

- `/pyproject.toml`
- `/uv.lock`

## Files to modify

**`Makefile`**
- `RUFF ?= uv tool run ruff`, `YAMLLINT ?= uv tool run yamllint` (was `uv run
  ruff` / `uv run --group dev yamllint`).
- `PYTEST ?= uv run --project web2md --group test pytest -c web2md/pyproject.toml`
  (was `uv run --group test --group web2md pytest`).
- `lint` target: replace `$(RUFF) check .` with
  `git ls-files -- '*/pyproject.toml' | xargs -n1 dirname | xargs $(RUFF) check`
  — runs ruff once per subproject directory instead of once over the whole
  tree, auto-discovered from tracked `pyproject.toml` files (see design note
  above).
- `scrape` target: `uv run --project web2md python web2md/src/web2md.py` (drop
  `--group web2md`, no longer needed now deps are plain project dependencies).
- Rewrite the top-of-file tool-override comment block (lines 6–18) to explain
  the new split, the per-subproject ruff invocation, and why `RUFF`/`YAMLLINT`
  need no CI override anymore.

**`.github/workflows/ci.yml`**
- `lint` job: drop the `YAMLLINT=`/`RUFF=` overrides — keep only
  `MARKDOWNLINT='npx --yes markdownlint-cli2'`. Update the job's leading
  comment (currently says "yamllint and ruff run from the dev group only") to
  reflect ephemeral `uv tool run` invocation.
- `test-web2md` job: drop the `PYTEST=` override — plain `make test-web2md`.
  Update its leading comment (currently explains `--only-group` twice) to say
  web2md is its own project with nothing heavy to exclude.
- Both jobs keep `astral-sh/setup-uv@v9.0.0` (still needed for `uv tool run`
  and `uv run --project`).
- `validate-kit` job: unchanged.

**`AGENTS.md`** — in the Repository map section, update the sentence "pytest
imports it via `pythonpath` in `pyproject.toml`" → "in `web2md/pyproject.toml`",
and add a short clause noting `pdf2md/` and `web2md/` are now independent uv
projects (own `pyproject.toml`/`uv.lock`), with repo-wide `ruff`/`yamllint`
run via `uv tool run` rather than owned by either.

**`README.md`** — rewrite the Development section's closing paragraph (lines
172–176, "Python tooling is thin, split across three dependency groups...")
to describe the two independent projects instead, and fix the yamllint/ruff
install sentence (line 142–143, currently "yamllint runs via the uv `dev`
group") to say both run ephemerally via `uv tool run`.

**`pdf2md/README.md`** — update all `uv run marker ...` / `uv run
marker_single ...` commands to `uv run --project pdf2md marker ...` /
`uv run --project pdf2md marker_single ...`, and add a leading `uv sync
--project pdf2md` step (mirroring `web2md/README.md`'s "Install scraper deps"
line) so the venv-creation purpose of `pdf2md/pyproject.toml` is explicit
rather than implied by `uv run`'s automatic sync.

**`web2md/README.md`**
- Layout section (line 41–43): fix the `[build-system]`/`pythonpath` sentence
  to reference `web2md/pyproject.toml` and the new relative path.
- Fetch/convert commands: `uv sync --group web2md` → `uv sync --project
  web2md`; `uv run --group web2md python web2md/src/web2md.py` → `uv run
  --project web2md python web2md/src/web2md.py` (both variants incl.
  `--refresh`).
- Tests section: `uv run --group test --group web2md pytest web2md/tests` →
  `uv run --project web2md --group test pytest -c web2md/pyproject.toml`.

**`.coderabbit.yaml`** — `ruff.config_file: "pyproject.toml"` →
`"web2md/pyproject.toml"` (line 145), the only remaining ruff config in the
repo.

## Verification

1. `uv lock --project pdf2md` and `uv lock --project web2md` — both resolve
   cleanly, producing `pdf2md/uv.lock` and `web2md/uv.lock`.
2. `make lint` — yamllint via `uv tool run` against the whole repo; ruff via
   `uv tool run` once per discovered subproject (today just `web2md`),
   confirm it applies `web2md/pyproject.toml`'s ruff config and passes (or
   shows only pre-existing findings). Confirm `pdf2md` — no `.py` files —
   doesn't break the invocation.
3. `make test-web2md` — full web2md suite passes using the new
   `--project web2md ... -c web2md/pyproject.toml` invocation, confirming
   `pythonpath`/`testpaths` resolve correctly from the moved config.
4. `make scrape` — spot-check it still writes into `md/` at the repo root
   (unaffected, since `web2md.py` derives paths from `Path(__file__)`, not
   CWD).
5. `uv run --project pdf2md marker --help` — sanity-check the pdf2md project
   resolves and marker's CLI is reachable (skip a full `marker` conversion
   run; installing `marker-pdf`'s torch chain is slow/heavy and not needed to
   prove the split works).
6. `git status` / diff review — confirm no leftover root `pyproject.toml` /
   `uv.lock`, and that `.gitignore` genuinely needs no edits (per the design
   note above).
7. `pi/` and `scripts/` are untouched, so `make validate` /
   `./scripts/validate-spec.sh` is not required by AGENTS.md's own rule for
   this change — skip it.
