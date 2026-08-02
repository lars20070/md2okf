#!/usr/bin/env bash
set -euo pipefail

# Open an interactive bash shell in the SANDBOXED Pi runtime (Docker Sandbox /
# sbx) — for inspecting config, installed tooling, or state left by a compile run.
#
# Usage: bash.sh
#
# Reuses the existing pi-kit sandbox (creating it only if missing; `sbx exec`
# auto-starts it if stopped), so a prior compile run's state is preserved.
# OPENROUTER_API_KEY is proxy-managed by sbx, so it is NOT required in the host
# environment.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

kit_name="pi-kit" # keyed to `name:` in pi/spec.yaml and to sbx secrets

if ! command -v sbx >/dev/null 2>&1; then
	echo "Error: 'sbx' CLI not found in PATH." >&2
	echo "Please install it with: brew install docker/tap/sbx" >&2
	exit 1
fi

# Create the sandbox only if it does not already exist, so we reuse any running
# instance (and its state) instead of tearing it down.
if ! sbx ls -q | grep -qx "${kit_name}"; then
	sbx run --detached --name "${kit_name}" --kit ./pi/ "${kit_name}"
fi

# Drop into an interactive shell at the workspace (the repo root). `sbx exec`
# starts the sandbox first if it is stopped.
sbx exec -it "${kit_name}" -- bash
