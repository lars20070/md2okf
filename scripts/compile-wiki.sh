#!/usr/bin/env bash
set -euo pipefail

# Compile the OKF wiki with the SANDBOXED Pi runtime (Docker Sandbox / sbx).
#
# Usage: compile-wiki.sh [md-folder]
#   md-folder  source folder of *.md documents
#              (default: md/)
#
# Model and provider come from the kit's own config (pi/files/home/.pi/agent/
# settings.json + models.json), delivered to ~/.pi/agent/ in the VM — no
# --provider/--model flags here. OPENROUTER_API_KEY is proxy-managed by sbx
# (configured once via `sbx secret`, see README), so it is NOT required in the
# host environment.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

markdown_folder="${1:-md}"
kit_name="pi-kit" # keyed to `name:` in pi/spec.yaml and to sbx secrets

if ! command -v sbx >/dev/null 2>&1; then
	echo "Error: 'sbx' CLI not found in PATH." >&2
	echo "Please install it with: brew install docker/tap/sbx" >&2
	exit 1
fi

if [[ ! -d "${markdown_folder}" ]]; then
	echo "Markdown folder not found: ${markdown_folder}" >&2
	exit 1
fi

# Recreate the sandbox so the latest kit changes and secrets are applied, then
# leave it running (detached) so we can exec one Pi run per document into it.
sbx rm --force "${kit_name}" || true
sbx run --detached --name "${kit_name}" --kit ./pi/ "${kit_name}"

# Compile each document into okf/. Verified: `sbx exec` runs with the VM
# workspace (the repo root) as its cwd, so a host path md/<...>.md is the same
# relative path inside the VM and Pi resolves it directly.
#
# `</dev/null` is REQUIRED, not tidiness.
# `sbx exec` hands the guest process a pipe for stdin, and Pi's print mode reads
# piped stdin to merge it into the prompt. Run from a terminal, that pipe never
# reaches EOF, so Pi blocks before its first API call and the compile hangs
# forever with no output and no OpenRouter activity.
shopt -s nullglob
for document in "${markdown_folder}"/*.md; do
	echo "Compiling document ${document}"
	sbx exec "${kit_name}" -- pi \
		-p "Load the compile-wiki skill: read ~/.pi/agent/skills/compile-wiki/SKILL.md, then follow it to compile ${document} into the OKF wiki under okf/." \
		</dev/null
done
