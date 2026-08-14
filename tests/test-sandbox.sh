#!/usr/bin/env bash
set -euo pipefail

# Check that the sandbox delivers what pi/spec.yaml promises: the installed
# toolchain, the agent config copied in from pi/files/, and a proxy-managed
# OPENROUTER_API_KEY. The checks themselves live in tests/test-sandbox-guest.sh.
#
# Usage: test-sandbox.sh
#
# Reuses the existing md2okf sandbox, creating one only if missing (minutes), so
# it may be testing a sandbox older than your last pi/ edit. To force a fresh
# one: sbx rm --force md2okf && ./tests/test-sandbox.sh

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

kit_name="md2okf" # keyed to `name:` in pi/spec.yaml and to sbx secrets

if ! command -v sbx >/dev/null 2>&1; then
	echo "Error: 'sbx' CLI not found in PATH." >&2
	echo "Please install it with: brew install docker/tap/sbx" >&2
	exit 1
fi

if ! sbx ls -q | grep -qx "${kit_name}"; then
	echo "No ${kit_name} sandbox found — creating one (this takes minutes)."
	sbx run --detached --name "${kit_name}" --kit ./pi/ "${kit_name}"
fi

# `sh -lc` must be a LOGIN shell: the uv tools land in ~/.local/bin and the npm
# globals in the user prefix, neither of which is on a non-login PATH. The
# relative path resolves because `sbx exec` runs with the repo root as its cwd.
# `</dev/null` stops the guest blocking on an stdin pipe that never reaches EOF
# (scripts/compile-wiki.sh:42-46).
sbx exec "${kit_name}" -- sh -lc './tests/test-sandbox-guest.sh' </dev/null
