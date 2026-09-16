#!/usr/bin/env bash
set -euo pipefail

# Check that the sandbox delivers what kits/md2okf/spec.yaml promises: the
# installed toolchain, the agent config copied in from kits/md2okf/files/, and
# a proxy-managed OPENROUTER_API_KEY. The checks themselves live in
# tests/test-sandbox-guest.sh.
#
# Usage: test-sandbox.sh
#
# Reuses the existing md2okf sandbox, creating one only if missing (minutes), so
# it may be testing a sandbox older than your last kits/md2okf/ edit. To force
# a fresh one: sbx rm --force md2okf && ./tests/test-sandbox.sh

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

# The workspace arguments are the least-privilege mount — see
# scripts/lib/sandbox-mounts.sh.
if ! sbx ls -q | grep -qx "${kit_name}"; then
	echo "No ${kit_name} sandbox found — creating one (this takes minutes)."
	read -r -a workspace_args <<<"$(sandbox_workspace_args)"
	sbx run --detached --name "${kit_name}" ./kits/md2okf/ "${workspace_args[@]}"
fi

# `sh -l` must be a LOGIN shell: the uv tools land in ~/.local/bin and the npm
# globals in the user prefix, neither of which is on a non-login PATH. `-s`
# reads the script from stdin, because tests/ is not one of the sandbox's
# mounts and so cannot be named as a path inside the VM. Feeding stdin from
# the file also closes it at EOF, which is what stops the guest blocking on a
# pipe that never ends (scripts/compile-okf.sh:61-65).
sbx exec "${kit_name}" -- sh -l -s <"${repo_root}/tests/test-sandbox-guest.sh"
