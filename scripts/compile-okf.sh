#!/usr/bin/env bash
set -euo pipefail

# Compile the OKF wiki with the SANDBOXED Pi runtime (Docker Sandbox / sbx).
#
# Usage: compile-okf.sh [md-folder]
#   md-folder  source folder of *.md documents
#              (default: md/)
#
# Env: RALPH_MAX  max Pi iterations per document when the wiki hash keeps
#                 changing (default: 10)
#
# Model and provider come from the kit's own config (pi/files/home/.pi/agent/
# settings.json + models.json), delivered to ~/.pi/agent/ in the VM — no
# --provider/--model flags here. OPENROUTER_API_KEY is proxy-managed by sbx
# (configured once via `sbx secret`, see README), so it is NOT required in the
# host environment.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

markdown_folder="${1:-md}"
kit_name="md2okf" # keyed to `name:` in pi/spec.yaml and to sbx secrets
# __DOCUMENT__ is replaced with the source path for each Pi run.
compile_prompt="Load the compile-okf skill: read ~/.pi/agent/skills/compile-okf/SKILL.md, then follow it to compile __DOCUMENT__ into the OKF wiki under okf/."
# Appended to compile_prompt on Ralph loop iterations after the first, so Pi
# knows it may be resuming unfinished work rather than starting the document
# over from scratch.
continuation_prompt="This is a follow-up pass on this document: okf/ may already hold partial work from a previous pass. Compare the source against what is on disk and continue at the first gap — do not start over."

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
#
# Ralph loop: re-run Pi on the same document until merkleokf --nolog -L 0
# reports an unchanged wiki root hash (log.md excluded). Cap with RALPH_MAX
# (default 10) so a runaway compile fails instead of looping forever.
wiki_root_hash() {
	sbx exec "${kit_name}" -- merkleokf --nolog -L 0 okf/ | awk 'NR==3 {print $1}'
}

max_iterations="${RALPH_MAX:-10}"
shopt -s nullglob
for document in "${markdown_folder}"/*.md; do
	prev_hash="$(wiki_root_hash)"
	iteration=0
	while true; do
		iteration=$((iteration + 1))
		if ((iteration > max_iterations)); then
			echo "Error: Ralph loop hit ${max_iterations} iterations for ${document}" >&2
			exit 1
		fi
		iteration_prompt="${compile_prompt//__DOCUMENT__/${document}}"
		if ((iteration > 1)); then
			iteration_prompt="${iteration_prompt} ${continuation_prompt}"
		fi
		echo "Compiling document ${document} (iteration ${iteration})"
		sbx exec "${kit_name}" -- pi \
			-p "${iteration_prompt}" \
			</dev/null
		curr_hash="$(wiki_root_hash)"
		if [[ "${curr_hash}" == "${prev_hash}" ]]; then
			break
		fi
		prev_hash="${curr_hash}"
	done
done
