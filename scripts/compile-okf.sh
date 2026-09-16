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
# Model and provider come from the kit's own config
# (kits/md2okf/files/home/.pi/agent/settings.json + models.json), delivered to
# ~/.pi/agent/ in the VM — no --provider/--model flags here.
# OPENROUTER_API_KEY is proxy-managed by sbx (configured once via `sbx secret`,
# see README), so it is NOT required in the host environment.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

# shellcheck source=scripts/lib/sandbox-mounts.sh
source "${repo_root}/scripts/lib/sandbox-mounts.sh"

markdown_folder="${1:-md}"
kit_name="md2okf" # keyed to `name:` in kits/md2okf/spec.yaml and to sbx secrets
# __DOCUMENT__ is replaced with the source path for each Pi run.
compile_prompt="Load the compile-okf skill: read ~/.pi/agent/skills/compile-okf/SKILL.md, then follow it to compile __DOCUMENT__ into the OKF wiki in your workspace."
# Appended to compile_prompt on Ralph loop iterations after the first, so Pi
# knows it may be resuming unfinished work rather than starting the document
# over from scratch.
continuation_prompt="This is a follow-up pass on this document: the wiki may already hold partial work from a previous pass. Compare the source against what is on disk and continue at the first gap — do not start over."

if ! command -v sbx >/dev/null 2>&1; then
	echo "Error: 'sbx' CLI not found in PATH." >&2
	echo "Please install it with: brew install docker/tap/sbx" >&2
	exit 1
fi

if [[ ! -d "${markdown_folder}" ]]; then
	echo "Markdown folder not found: ${markdown_folder}" >&2
	exit 1
fi
# Absolute, so the path handed to Pi below names the same file on the host and
# inside the VM.
document_folder="$(cd "${markdown_folder}" && pwd)"

# Recreate the sandbox so the latest kit changes and secrets are applied, then
# leave it running (detached) so we can exec one Pi run per document into it.
# The workspace arguments are the least-privilege mount — see
# scripts/lib/sandbox-mounts.sh.
read -r -a workspace_args <<<"$(sandbox_workspace_args)"
sbx rm --force "${kit_name}" || true
sbx run --detached --name "${kit_name}" ./kits/md2okf/ "${workspace_args[@]}"

# Compile each document into the wiki. `sbx exec` runs with the primary
# workspace — okf/ — as its cwd, and every mount appears inside the VM at its
# host absolute path, so an absolute host path names the same file in both
# places and Pi resolves it whatever its working directory is.
#
# `</dev/null` is REQUIRED, not tidiness.
# `sbx exec` hands the guest process a pipe for stdin, and Pi's non-interactive
# modes read piped stdin to merge it into the prompt. Run from a terminal, that
# pipe never reaches EOF, so Pi blocks before its first API call and the
# compile hangs forever with no output and no OpenRouter activity.
#
# `--mode json` streams session events as JSON lines; a jq filter prints each
# tool start and assistant message_end text/thinking so the host can watch
# progress. --session-dir points at the logs/sessions/ mount, which keeps
# transcripts across `sbx rm`.
#
# Ralph loop: re-run Pi on the same document until merkleokf --nolog -L 0
# reports an unchanged wiki root hash (log.md excluded). Cap with RALPH_MAX
# (default 10) so a runaway compile fails instead of looping forever.
#
# The wiki is named by its absolute path, not as `.`, even though it is the cwd
# `sbx exec` starts in: --nolog only skips the root log.md when the walk root
# is a directory named okf (scripts/merkleokf/src/merkleokf/merkle.py), and
# `.` has no name. Under `.` the log would be hashed, every run appends to it,
# and the loop would never converge.
wiki_root_hash() {
	sbx exec "${kit_name}" -- merkleokf --nolog -L 0 "${repo_root}/okf" |
		awk 'NR==3 {print $1}'
}

# Host-side view of pi --mode json: tool starts + assistant prose/thinking.
pi_event_filter='fromjson? // empty
| if .type == "tool_execution_start" then
    ("\(.toolName) \(.args|tostring)")[:120]
  elif .type == "message_end" and .message.role == "assistant" then
    (.message.content // []
     | map(
         select(.type == "text" or .type == "thinking")
         | if .type == "thinking" then "[thinking]\n\(.thinking)" else .text end
       )
     | join("\n\n")
     | select(length > 0))
  else empty end'

session_dir="${repo_root}/logs/sessions" # created by sandbox_workspace_args

max_iterations="${RALPH_MAX:-10}"
shopt -s nullglob
for document in "${document_folder}"/*.md; do
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
			--mode json \
			--session-dir "${session_dir}" \
			"${iteration_prompt}" \
			</dev/null |
			jq --unbuffered -R -r "${pi_event_filter}"
		curr_hash="$(wiki_root_hash)"
		echo "${prev_hash} -> ${curr_hash}"
		if [[ "${curr_hash}" == "${prev_hash}" ]]; then
			break
		fi
		prev_hash="${curr_hash}"
	done
done
