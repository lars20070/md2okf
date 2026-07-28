#!/usr/bin/env bash
set -euo pipefail

# Compile the OKF wiki with the CONTAINERISED Pi runtime (Docker Compose).
#
# Usage: compile-wiki-container.sh [md-folder]
#   md-folder  source folder of *.md documents
#              (default: md/)
#
# Self-contained: this driver shares no code with the sandbox driver. Model and
# provider come from pi/container/agent/settings.json — no --provider/--model
# flags here. All container config (security, resource limits, mounts, env)
# lives declaratively in pi/container/compose.yaml.
#
# The compilation workflow itself lives in the `compile-wiki` skill
# (pi/container/agent/skills/compile-wiki/SKILL.md), bind-mounted to
# ~/.pi/agent/skills/ in the container; pi/container/agent/AGENTS.md carries only
# the conventions that skill has to respect.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

markdown_folder="${1:-md}"
compose_file="pi/container/compose.yaml"

if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
	echo "Missing OPENROUTER_API_KEY environment variable." >&2
	exit 1
fi

if ! command -v docker >/dev/null 2>&1; then
	echo "Docker CLI not found. Install Docker Desktop or Docker Engine and try again." >&2
	exit 1
fi

if ! docker info >/dev/null 2>&1; then
	echo "Docker does not appear to be running. Start Docker Desktop (or Docker Engine) and try again." >&2
	exit 1
fi

if [[ ! -d "${markdown_folder}" ]]; then
	echo "Markdown folder not found: ${markdown_folder}" >&2
	exit 1
fi

# Build the Pi agent image.
docker compose -f "${compose_file}" build

# Compile each document into okf/ (mounted read-write from the repo root).
# md/ is mounted read-only at /workspace/md, so a host path md/<...>.md is
# visible inside the container at /workspace/md/<...>.md.
shopt -s nullglob
for document in "${markdown_folder}"/*.md; do
	document_inside="/workspace/${document}"
	echo "Compiling document ${document_inside}"
	docker compose -f "${compose_file}" run --rm -T pi \
		-xt bash \
		-p "Load the compile-wiki skill: read /home/node/.pi/agent/skills/compile-wiki/SKILL.md, then follow it to compile ${document_inside} into the OKF wiki under okf/." \
		</dev/null
done
