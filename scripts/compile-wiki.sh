#!/usr/bin/env bash
set -euo pipefail

# Compile the OKF wiki with the SANDBOXED Pi runtime (Docker Sandbox / sbx).
#
# Usage: compile-wiki.sh [md-folder]
#   md-folder  source folder of *.md documents
#              (default: md/)
#
# Env:
#   MAX_PASSES   most Pi runs to spend on one document (default: 20). Each pass
#                resumes from what the previous one left in okf/, so a document
#                larger than a single run still completes.
#   MAX_RETRIES  consecutive failed passes tolerated before abandoning a document
#                (default: 3). Provider errors (OpenRouter 502 and friends) are
#                transient and frequent on long compiles; a failed pass is retried
#                with backoff rather than killing the whole compile.
#
# Model and provider come from the kit's own config (pi/files/home/.pi/agent/
# settings.json + models.json), delivered to ~/.pi/agent/ in the VM — no
# --provider/--model flags here. OPENROUTER_API_KEY is proxy-managed by sbx
# (configured once via `sbx secret`, see README), so it is NOT required in the
# host environment.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

markdown_folder="${1:-md}"
kit_name="md2okf"               # keyed to `name:` in pi/spec.yaml and to sbx secrets
max_passes="${MAX_PASSES:-20}"  # upper bound on Pi runs per document
max_retries="${MAX_RETRIES:-3}" # consecutive failed passes tolerated before giving up
failed_documents=0

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
# A document larger than one Pi run is compiled over SEVERAL runs. Fidelity means
# the wiki is about as large as the source, so a book-length document cannot be
# written inside a single context; the skill makes each run resumable (the wiki on
# disk records what is done) and this loop supplies the runs. Passes repeat until
# one adds no bytes to okf/, i.e. there was nothing left to do — or until
# MAX_PASSES, which bounds the cost of a run that cannot converge.
#
# `</dev/null` is REQUIRED, not tidiness.
# `sbx exec` hands the guest process a pipe for stdin, and Pi's print mode reads
# piped stdin to merge it into the prompt. Run from a terminal, that pipe never
# reaches EOF, so Pi blocks before its first API call and the compile hangs
# forever with no output and no OpenRouter activity.

# Total bytes of wiki content, the loop's progress metric. Bytes rather than page
# count, so a pass that only splits a page or fills in an index still registers.
# Guarded because `set -o pipefail` would otherwise abort the run if okf/ is
# missing on the first pass.
wiki_size() {
	if [[ ! -d okf ]]; then
		echo 0
		return
	fi
	find okf -name '*.md' -exec cat {} + | wc -c
}

shopt -s nullglob
for document in "${markdown_folder}"/*.md; do
	echo "Compiling document ${document}"
	previous=-1
	pass=1
	failures=0
	while [[ "${pass}" -le "${max_passes}" ]]; do
		echo "  pass ${pass}/${max_passes}"

		# A failed pass must not kill the compile. `set -e` would abort the whole
		# run on any non-zero exit, throwing away every remaining pass over one
		# transient provider hiccup — while the completed work sits safely in okf/.
		# Guarding the call keeps the loop alive; the skill's resumability means a
		# retry simply picks up where the failed pass left off.
		if ! sbx exec "${kit_name}" -- pi \
			-p "Load the compile-wiki skill: read ~/.pi/agent/skills/compile-wiki/SKILL.md, then follow it to compile ${document} into the OKF wiki under okf/. This may be a continuation: okf/ already holds the work of earlier passes. Compare the source against what is on disk and continue at the first gap — do not start over." \
			</dev/null; then
			failures=$((failures + 1))
			if [[ "${failures}" -ge "${max_retries}" ]]; then
				echo "  ${failures} consecutive failed passes; abandoning ${document}." >&2
				echo "  Everything compiled so far is preserved in okf/ — re-run to continue." >&2
				failed_documents=$((failed_documents + 1))
				break
			fi
			backoff=$((failures * 15))
			echo "  pass failed (provider error?); retrying in ${backoff}s" >&2
			sleep "${backoff}"
			continue
		fi
		failures=0

		current="$(wiki_size)"
		if [[ "${current}" -eq "${previous}" ]]; then
			echo "  pass ${pass} added nothing; ${document} is done"
			break
		fi
		if [[ "${pass}" -eq "${max_passes}" ]]; then
			echo "  reached MAX_PASSES (${max_passes}) and the wiki was still growing." >&2
			echo "  ${document} is probably INCOMPLETE — re-run, or raise MAX_PASSES." >&2
		fi
		previous="${current}"
		pass=$((pass + 1))
	done
done

# Report failure only after compiling everything that could be compiled, so one
# bad document does not cost the rest of the folder.
if [[ "${failed_documents}" -gt 0 ]]; then
	echo "${failed_documents} document(s) abandoned after repeated provider errors." >&2
	exit 1
fi
