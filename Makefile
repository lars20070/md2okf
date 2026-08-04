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
#                 from the lockfile — no heavy project deps like marker-pdf).
#   PYTEST        pytest launcher. Local: `uv run --group test --group web2md`
#                 (uses the full project venv). CI: the same groups via
#                 `--only-group`, which drops the project deps — no marker-pdf.
MARKDOWNLINT ?= markdownlint-cli2
RUFF ?= uv run ruff
PYTEST ?= uv run --group test --group web2md pytest

.DEFAULT_GOAL := lint
.PHONY: lint lint-okf validate test wiki scrape

# Lint tracked Markdown, shell, JSON, and Python. The large generated Marker
# book files under md/ are linted manually (see README), not here.
lint:
	$(MARKDOWNLINT) \
		"README.md" \
		"pdf2md/README.md" \
		"web2md/README.md" \
		"AGENTS.md" \
		"pi/README.md" \
		"pi/files/home/.pi/agent/**/*.md"
	shellcheck \
		scripts/*.sh \
		pi/files/home/.pi/agent/skills/*/scripts/*.sh
	git ls-files -z -- '*.json' | xargs -0 -n1 jq empty
	$(RUFF) check .

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

# Unit-test the web2md scraper (web2md/tests/). Offline: HTTP is mocked with
# httpx.MockTransport, so no test opens a socket. Config is in pyproject.toml,
# which also puts web2md/src/ on the import path.
test:
	$(PYTEST)

# Compile the OKF wiki with the sandboxed Pi runtime (Docker Sandbox / sbx).
wiki:
	./scripts/compile-wiki.sh

# Fetch the website into md/ as one file.
scrape:
	uv run --group web2md python web2md/src/web2md.py
