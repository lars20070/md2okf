# md2okf — developer task runner.
#
# Pi runs in one runtime: the Docker Sandbox (sbx) kit under pi/, which owns the
# only copy of the agent config (see AGENTS.md).
#
# Tool overrides (defaults suit local dev; CI overrides them — see ci.yml):
#   MARKDOWNLINT  markdownlint-cli2 launcher. Local: the brew-installed command.
#                 CI: `npx --yes markdownlint-cli2` (no global install needed).
#   RUFF          ruff launcher. Local: `uv run ruff` (uses the full project
#                 venv). CI: `uv run --only-group dev ruff` (installs only ruff
#                 and yamllint from the lockfile — no heavy project deps like
#                 marker-pdf).
#   PYTEST        pytest launcher. Local: `uv run --group test --group web2md`
#                 (uses the full project venv). CI: the same groups via
#                 `--only-group`, which drops the project deps — no marker-pdf.
#   YAMLLINT      yamllint launcher. Local and CI: `uv run --group dev yamllint`
#                 (dev group; CI uses `--only-group dev`).
#   CSPELL        cspell launcher. Local and CI: `npx --yes cspell`.
MARKDOWNLINT ?= markdownlint-cli2
RUFF ?= uv run ruff
PYTEST ?= uv run --group test --group web2md pytest
YAMLLINT ?= uv run --group dev yamllint
CSPELL ?= npx --yes cspell

.DEFAULT_GOAL := lint
.PHONY: lint lint-okf validate test test-web2md test-sandbox wiki scrape

# Lint tracked Markdown, JSON, YAML, and shell, spell-check owned Markdown, and
# lint Python. Driving every check off `git ls-files` means a newly added file
# is covered the moment it is tracked, rather than when someone remembers to
# extend a hand-maintained list here.
#
# Exclusions, all deliberate:
#   md/                generated Marker book output — large, and linted manually
#                      (see README), not here.
#   .claude/, .cursor/ agent-tool config rather than project documentation. The
#                      skill files are written to their tools' own conventions
#                      (front matter, no H1), which markdownlint reads as errors.
#   SPEC.md            upstream OKF spec, not project prose.
#   CLAUDE.md          one-line `@AGENTS.md` pointer, not a document.
# cspell runs on owned Markdown only (same exclusions as markdownlint).
lint:
	git ls-files -z -- '*.md' ':!md/' ':!.claude/' ':!.cursor/' ':!CLAUDE.md' ':!SPEC.md' \
		| xargs -0 $(MARKDOWNLINT)
	git ls-files -z -- '*.json' | xargs -0 -n1 jq empty
	git ls-files -z -- '*.yaml' '*.yml' | xargs -0 $(YAMLLINT)
	git ls-files -z -- '*.sh' | xargs -0 shellcheck
	git ls-files -z -- '*.md' ':!md/' ':!.claude/' ':!.cursor/' ':!CLAUDE.md' ':!SPEC.md' \
		| xargs -0 $(CSPELL) --no-progress
	$(RUFF) check .
	@echo "All lint checks passed."

# Lint the generated okf/ wiki with okf-lint
# (https://github.com/thisismydesign/okf-lint). Run via `pnpm dlx`, so nothing
# needs installing on the host. Rules live in okf/.okflintrc.json. Kept out of
# `make lint` because okf/ is generated output and gitignored — this is a
# host-side developer command, not part of the source-tree lint or CI.
lint-okf:
	pnpm dlx @thisismydesign/okf-lint ./okf

# Validate the sandbox kit spec against the current Sandbox Kit schema.
validate:
	./scripts/validate-spec.sh

# Both suites. Host-only: the sandbox half needs `sbx login`. CI runs
# `test-web2md` on its own and does not invoke this target.
test: test-web2md test-sandbox

# Unit-test the web2md scraper (web2md/tests/). Offline: HTTP is mocked with
# httpx.MockTransport, so no test opens a socket. Config is in pyproject.toml,
# which also puts web2md/src/ on the import path.
test-web2md:
	$(PYTEST)

# Check that the sandbox delivers the toolchain, agent config and proxy-managed
# key that pi/spec.yaml promises.
test-sandbox:
	./tests/test-sandbox.sh

# Compile the OKF wiki with the sandboxed Pi runtime (Docker Sandbox / sbx).
wiki:
	./scripts/compile-wiki.sh

# Fetch the website into md/ as one file.
scrape:
	uv run --group web2md python web2md/src/web2md.py
