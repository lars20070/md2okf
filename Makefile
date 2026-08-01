# md2okf — developer task runner.
#
# The two Pi runtimes are independent: pi/container/ and pi/sandbox/ each own a
# copy of the agent config. Targets below are tagged to one runtime where it
# matters, so deleting a runtime later is a line-level edit here (see AGENTS.md).
#
# Tool overrides (defaults suit local dev; CI overrides them — see ci.yml):
#   MARKDOWNLINT  markdownlint-cli2 launcher. Local: the brew-installed command.
#                 CI: `npx --yes markdownlint-cli2` (no global install needed).
#   RUFF          ruff launcher. Local: `uv run ruff` (uses the full project
#                 venv). CI: `uv run --only-group dev ruff` (installs only ruff
#                 from the lockfile — no heavy project deps like marker-pdf).
#   HADOLINT      hadolint launcher. Local: the brew-installed command. CI: a
#                 pinned binary downloaded to PATH (see ci.yml), so the default
#                 works there too. Config lives in .hadolint.yaml.
MARKDOWNLINT ?= markdownlint-cli2
RUFF ?= uv run ruff
HADOLINT ?= hadolint

.DEFAULT_GOAL := lint
.PHONY: lint lint-okf validate wiki-container wiki-sandbox style-guide

# Lint tracked Markdown, shell, Python, and the container Dockerfile. One
# Markdown glob per runtime so deleting a runtime is a one-line removal. The
# large generated Marker book files under md/ are linted manually (see README),
# not here.
lint:
	$(MARKDOWNLINT) \
		"README.md" \
		"pdf2md/README.md" \
		"web2md/README.md" \
		"AGENTS.md" \
		"pi/container/agent/**/*.md" \
		"pi/sandbox/files/home/.pi/agent/**/*.md"
	shellcheck \
		scripts/*.sh \
		pi/sandbox/files/home/.pi/agent/skills/*/scripts/*.sh
	$(RUFF) check .
	$(HADOLINT) pi/container/Dockerfile

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

# Compile the OKF wiki with the containerised Pi runtime (Docker Compose).
wiki-container:
	./scripts/compile-wiki-container.sh

# Compile the OKF wiki with the sandboxed Pi runtime (Docker Sandbox / sbx).
wiki-sandbox:
	./scripts/compile-wiki-sandbox.sh

# Fetch the website into md/ as one file.
scrape:
	uv run --group web2md python web2md/web2md.py
