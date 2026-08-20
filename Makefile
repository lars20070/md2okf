# md2okf — developer task runner.
#
# Pi runs in one runtime: the Docker Sandbox (sbx) kit under pi/, which owns the
# only copy of the agent config (see AGENTS.md).
#
# Tool overrides (defaults suit local dev; CI overrides only MARKDOWNLINT):
#   MARKDOWNLINT  markdownlint-cli2 launcher. Local: the brew-installed command.
#                 CI: `npx --yes markdownlint-cli2` (no global install needed).
#   RUFF          ruff launcher. Ephemeral and pinned, so it belongs to no
#                 project; the pin matches the sandbox (pi/spec.yaml).
#   PYTEST        pytest launcher. Default: web2md. Prefer the per-project
#                 targets (`test-web2md`, `test-clis`) which pass `-c`.
#   YAMLLINT      yamllint launcher. Repo-wide (YAML lives outside the Python
#                 projects), so ephemeral and pinned like ruff.
#   CSPELL        cspell launcher. Local and CI: `npx --yes cspell`.
MARKDOWNLINT ?= markdownlint-cli2
RUFF ?= uv tool run ruff@0.16.2
PYTEST ?= uv run --project web2md --group test pytest -c web2md/pyproject.toml
YAMLLINT ?= uv tool run yamllint@1.38.0
CSPELL ?= npx --yes cspell

.DEFAULT_GOAL := lint
.PHONY: lint lint-okf validate test test-web2md test-clis install-clis \
	test-sandbox wiki scrape

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
#
# ruff runs once per tracked subproject rather than once over the tree, because
# each project carries its own [tool.ruff]. Deriving the list from tracked
# pyproject.toml files means a new subproject is linted the moment it is added.
lint:
	git ls-files -z -- '*.md' ':!md/' ':!.claude/' ':!.cursor/' ':!CLAUDE.md' ':!SPEC.md' \
		| xargs -0 $(MARKDOWNLINT)
	git ls-files -z -- '*.json' | xargs -0 -n1 jq empty
	git ls-files -z -- '*.yaml' '*.yml' | xargs -0 $(YAMLLINT)
	git ls-files -z -- '*.sh' | xargs -0 shellcheck
	git ls-files -z -- '*.md' ':!md/' ':!.claude/' ':!.cursor/' ':!CLAUDE.md' ':!SPEC.md' \
		| xargs -0 $(CSPELL) --no-progress
	git ls-files -- '*/pyproject.toml' | xargs -n1 dirname | xargs $(RUFF) check
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

# Host pytest suites plus the sandbox check. Host-only for the sandbox half
# (needs `sbx login`). CI runs each pytest job on its own and does not invoke
# this target.
test: test-web2md test-clis test-sandbox

# Unit-test the web2md scraper (web2md/tests/). Offline: HTTP is mocked with
# httpx.MockTransport, so no test opens a socket. Config is in
# web2md/pyproject.toml, which also puts web2md/src/ on the import path.
test-web2md:
	$(PYTEST) web2md/tests

# Unit-test the four host CLIs (inspectmd, inspectokf, sizeokf, merkleokf).
# Each has its own project and lockfile — nothing shared. Offline; stdlib-only
# subjects under test (inspectokf mocks tree). Explicit suite paths keep
# collection inside each project when pytest is launched from the repo root.
test-clis:
	uv run --project inspectmd --group test pytest -c inspectmd/pyproject.toml \
		inspectmd/tests
	uv run --project inspectokf --group test pytest -c inspectokf/pyproject.toml \
		inspectokf/tests
	uv run --project sizeokf --group test pytest -c sizeokf/pyproject.toml \
		sizeokf/tests
	uv run --project merkleokf --group test pytest -c merkleokf/pyproject.toml \
		merkleokf/tests

# Install the four host CLIs onto PATH via uv tool.
install-clis:
	uv tool install --force ./inspectmd
	uv tool install --force ./inspectokf
	uv tool install --force ./sizeokf
	uv tool install --force ./merkleokf

# Check that the sandbox delivers the toolchain, agent config and proxy-managed
# key that pi/spec.yaml promises.
test-sandbox:
	./tests/test-sandbox.sh

# Compile the OKF wiki with the sandboxed Pi runtime (Docker Sandbox / sbx).
wiki:
	./scripts/compile-okf.sh

# Fetch the website into md/ as one file.
scrape:
	uv run --project web2md python web2md/src/web2md.py
