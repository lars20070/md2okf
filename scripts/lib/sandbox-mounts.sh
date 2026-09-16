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

# Config layer weaker than a real exported variable, stronger than the default
# below. Source .env if present, then restore everything that was already
# exported so the caller's environment always wins.
sandbox_mounts_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
sandbox_mounts_env="${sandbox_mounts_root}/.env"
if [[ -r "${sandbox_mounts_env}" ]]; then
	sandbox_mounts_before="$(export -p)"
	set -a
	# shellcheck disable=SC1090
	. "${sandbox_mounts_env}"
	set +a
	eval "${sandbox_mounts_before}" 2>/dev/null || true
fi

# Populate the global workspace_args array with the ordered workspace PATH
# arguments for `sbx run`, and create the writable mount sources.
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
	# XDG_STATE_HOME must be absolute. Treat a relative value as unset instead
	# of resolving it against whichever directory happened to invoke us.
	case "${XDG_STATE_HOME:-}" in
	/*) sandbox_state_home="${XDG_STATE_HOME}" ;;
	*) sandbox_state_home="${HOME}/.local/state" ;;
	esac
	SBXAGENT_STATE_DIR="${sandbox_state_home}/md2okf"
	export SBXAGENT_STATE_DIR
	mkdir -p "${SBXAGENT_STATE_DIR}"
	chmod 700 "${SBXAGENT_STATE_DIR}"

	# okf/           the wiki: the agent's only writable content output
	# md/            source documents, read as data and never modified
	# scripts/       the four helper CLI projects the kit's shims run
	# SPEC.md        the OKF spec, which outranks every instruction file
	# state dir      persistent Pi sessions, mounted read-write
	# shellcheck disable=SC2034 # consumed by every script that sources us
	workspace_args=(
		"./okf"
		"./md:ro"
		"./scripts:ro"
		"./SPEC.md:ro"
		"${SBXAGENT_STATE_DIR}"
	)
}
