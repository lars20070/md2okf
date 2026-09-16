#!/usr/bin/env bash
set -euo pipefail

# Open an interactive bash shell in the SANDBOXED Pi runtime (Docker Sandbox /
# sbx) — for inspecting config, installed tooling, or state left by a compile run.
#
# Usage: bash.sh
#
# Reuses the existing md2okf sandbox (creating it only if missing; `sbx exec`
# auto-starts it if stopped), so a prior compile run's state is preserved.
# OPENROUTER_API_KEY is proxy-managed by sbx, so it is NOT required in the host
# environment.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

# shellcheck source=scripts/lib/sandbox-mounts.sh
source "${repo_root}/scripts/lib/sandbox-mounts.sh"

kit_name="md2okf" # keyed to `name:` in kits/md2okf/spec.yaml and to sbx secrets

if ! command -v sbx >/dev/null 2>&1; then
	echo "Error: 'sbx' CLI not found in PATH." >&2
	echo "Please install it with: brew install docker/tap/sbx" >&2
	exit 1
fi

# Create the sandbox only if it does not already exist, so we reuse any running
# instance (and its state) instead of tearing it down. The workspace arguments
# are the least-privilege mount — see scripts/lib/sandbox-mounts.sh.
if ! sbx ls -q | grep -qx "${kit_name}"; then
	sandbox_workspace_args
	sbx run --detached --name "${kit_name}" \
		-e "SBXAGENT_STATE_DIR=${SBXAGENT_STATE_DIR}" \
		./kits/md2okf/ "${workspace_args[@]}"
fi

# Drop into an interactive shell at the workspace (okf/, the wiki root).
# `sbx exec` starts the sandbox first if it is stopped.
sbx exec -it "${kit_name}" -- bash
