# shellcheck shell=bash

# The sandbox's workspace mounts, defined once for every launcher that creates
# it (scripts/compile-okf.sh, scripts/bash.sh, scripts/pi.sh,
# tests/test-sandbox.sh). Sourced, not executed.
#
# Without these arguments `sbx run` mounts the current directory — the whole
# repository, read-write. The agent would then be able to read .git, CI config
# and every other file, and to write anywhere in the tree; its restriction to
# okf/ would rest on instructions alone. Naming the mounts makes that
# restriction a property of the filesystem instead.

# Print the ordered workspace PATH arguments for `sbx run`/`sbx create`, and
# create the mount sources that are not tracked in git.
#
# `sbx` takes them positionally: the first is the primary workspace — mounted
# read-write and the sandbox's default working directory — and the rest are
# additional workspaces, read-only when suffixed with `:ro`. Each one appears
# inside the VM at its host absolute path, so the read-only mounts stay
# siblings of the wiki and the agent reaches them as ../md, ../scripts and
# ../SPEC.md.
#
# Callers must be at the repository root, as every launcher already is.
sandbox_workspace_args() {
	# Not tracked in git (.gitignore: logs/), so `sbx run` would fail on a
	# missing mount source in a fresh clone.
	mkdir -p logs/sessions

	# okf/           the wiki: the agent's only writable content output
	# md/            source documents, read as data and never modified
	# scripts/       the four helper CLI projects the kit's shims run
	# SPEC.md        the OKF spec, which outranks every instruction file
	# logs/sessions/ Pi transcripts, written by `pi --session-dir`
	echo "./okf ./md:ro ./scripts:ro ./SPEC.md:ro ./logs/sessions"
}
