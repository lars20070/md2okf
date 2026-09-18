# md2okf — developer task runner.
#
# Pi runs in one runtime: the Docker Sandbox (sbx) kit under kits/md2okf/, which
# owns the only copy of the agent config (see AGENTS.md).
#
# Tool overrides (defaults suit local dev; CI overrides only MARKDOWNLINT):
#   MARKDOWNLINT  markdownlint-cli2 launcher. Local: the brew-installed command.
#                 CI: `npx --yes markdownlint-cli2` (no global install needed).
#   RUFF          ruff launcher. Ephemeral and pinned, so it belongs to no
#                 project; the pin matches the sandbox (kits/md2okf/spec.yaml).
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
.PHONY: lint check-okf validate test test-shell test-web2md test-clis test-md2okf \
	install-clis install test-sandbox wiki scrape

# Lint tracked Markdown, JSON, YAML, and shell, spell-check owned Markdown, lint
# Python, and check that VERSION and CHANGELOG.md's latest release agree.
# Driving every check off `git ls-files` means a newly added file is covered the
# moment it is tracked, rather than when someone remembers to extend a
# hand-maintained list here.
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
# The bare 'pyproject.toml' pattern adds the root md2okf project alongside the
# '*/pyproject.toml' subprojects; its own [tool.ruff] scopes that walk away
# from md/, okf/, and everything else that isn't its source.
lint:
	git ls-files -z -- '*.md' ':!md/' ':!.claude/' ':!.cursor/' ':!CLAUDE.md' ':!SPEC.md' \
		| xargs -0 $(MARKDOWNLINT)
	git ls-files -z -- '*.json' | xargs -0 -n1 jq empty
	git ls-files -z -- '*.yaml' '*.yml' | xargs -0 $(YAMLLINT)
	git ls-files -z -- '*.sh' | xargs -0 shellcheck
	git ls-files -z -- '*.md' ':!md/' ':!.claude/' ':!.cursor/' ':!CLAUDE.md' ':!SPEC.md' \
		| xargs -0 $(CSPELL) --no-progress
	git ls-files -- 'pyproject.toml' '*/pyproject.toml' | xargs -n1 dirname | xargs $(RUFF) check
	if [ ! -f VERSION ]; then \
		echo "lint: VERSION is missing" >&2; exit 1; \
	fi; \
	repo_version="$$(grep -m1 -oE '[0-9]+\.[0-9]+\.[0-9]+' VERSION)"; \
	if [ -z "$$repo_version" ]; then \
		echo "lint: could not find X.Y.Z in VERSION" >&2; exit 1; \
	fi; \
	changelog_version="$$(grep -m1 -oE '^## \[[0-9]+\.[0-9]+\.[0-9]+\]' CHANGELOG.md | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')"; \
	if [ -z "$$changelog_version" ]; then \
		echo "lint: could not find a ## [X.Y.Z] release heading in CHANGELOG.md" >&2; exit 1; \
	elif [ "$$repo_version" != "$$changelog_version" ]; then \
		echo "lint: VERSION is $$repo_version but CHANGELOG.md's latest release is $$changelog_version" >&2; \
		exit 1; \
	fi
	@echo "All lint checks passed."

# Check the generated okf/ wiki with okfctl (https://github.com/cwest/okfctl)
# and the frontmatter guard, using the same script the agent runs inside the
# sandbox — one implementation, two call sites. Needs okfctl on PATH:
# `brew install cwest/tap/okfctl`. Kept out of `make lint` because okf/ is
# generated output and gitignored — this is a host-side developer command,
# not part of the source-tree lint or CI.
check-okf:
	kits/md2okf/files/home/.pi/agent/skills/compile-okf/scripts/check-okf.sh ./okf

# Validate the sandbox kit spec against the current Sandbox Kit schema.
validate:
	./scripts/validate-spec.sh

# Host pytest suites plus the sandbox check. Host-only for the sandbox half
# (needs `sbx login`). CI runs each pytest job on its own and does not invoke
# this target.
test: test-shell test-web2md test-clis test-md2okf test-sandbox

# Host-side shell tests for state-path selection and the session bind helper.
# The real bind cases skip on hosts without password-free mount capability.
test-shell:
	./tests/test-sandbox-mounts.sh
	./tests/test-mount-state.sh

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
	uv run --project scripts/inspectmd --group test pytest -c scripts/inspectmd/pyproject.toml \
		scripts/inspectmd/tests
	uv run --project scripts/inspectokf --group test pytest -c scripts/inspectokf/pyproject.toml \
		scripts/inspectokf/tests
	uv run --project scripts/sizeokf --group test pytest -c scripts/sizeokf/pyproject.toml \
		scripts/sizeokf/tests
	uv run --project scripts/merkleokf --group test pytest -c scripts/merkleokf/pyproject.toml \
		scripts/merkleokf/tests

# Unit-test the md2okf driver itself. pytest's default discovery already
# collects only tests/test_*.py, leaving the tests/*.sh shell suites (run by
# test-shell and test-sandbox) untouched. Offline: every sbx call goes
# through the one seam in md2okf.sandbox, which these tests replace with a
# fake.
test-md2okf:
	uv run --group test pytest tests

# Install the four host CLIs onto PATH via uv tool.
install-clis:
	uv tool install --force ./scripts/inspectmd
	uv tool install --force ./scripts/inspectokf
	uv tool install --force ./scripts/sizeokf
	uv tool install --force ./scripts/merkleokf

# Install md2okf itself onto PATH via uv tool. Packaging the kit/SPEC/CLIs
# into the wheel (force-include) lands in a later stage; until then the
# installed tool has no bundled kit and fails clearly (ResourcesError) on
# anything but --help/--version — this target is for verifying the entry
# point wires up, not yet for real compiling from an install.
install:
	uv tool install --force .

# Check that the sandbox delivers the toolchain, agent config and proxy-managed
# key that kits/md2okf/spec.yaml promises.
test-sandbox:
	./tests/test-sandbox.sh

# Compile the OKF wiki with the sandboxed Pi runtime (Docker Sandbox / sbx).
# The md2okf driver is the documented path now; ./scripts/compile-okf.sh is
# still here as the rollback if it misbehaves, and goes in a later stage.
wiki:
	uv run md2okf md/

# Fetch the website into md/ as one file.
scrape:
	uv run --project web2md python web2md/src/web2md.py
