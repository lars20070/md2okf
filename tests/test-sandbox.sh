#!/usr/bin/env bash
set -euo pipefail

# Check that the sandbox delivers what kits/md2okf/spec.yaml promises: the
# installed toolchain, the agent config copied in from kits/md2okf/files/, a
# proxy-managed OPENROUTER_API_KEY, and the driver's mount invariants. The
# checks themselves live in tests/test-sandbox-guest.sh.
#
# Usage: test-sandbox.sh
#
# Reuses the existing md2okf sandbox, creating one only if missing (minutes), so
# it may be testing a sandbox older than your last kits/md2okf/ edit. To force
# a fresh one: sbx rm --force md2okf && ./tests/test-sandbox.sh

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

kit_name="md2okf" # keyed to `name:` in kits/md2okf/spec.yaml and to sbx secrets

if ! command -v sbx >/dev/null 2>&1; then
	echo "Error: 'sbx' CLI not found in PATH." >&2
	echo "Please install it with: brew install docker/tap/sbx" >&2
	exit 1
fi

# The driver owns sandbox creation: it is the only thing that builds the
# narrowed mount set — work/okf rw, work/{md,scripts,SPEC.md} ro, sessions/ rw,
# and the state root deliberately unmounted — that the guest-side invariant
# checks below assert. Creating one here from the legacy shell mounts instead
# would hand those checks a sandbox that cannot satisfy them. Reuses an
# existing sandbox when it is ours and its configuration still matches.
uv run python -m md2okf.sandbox

# `sh -l` must be a LOGIN shell: the uv tools land in ~/.local/bin and the npm
# globals in the user prefix, neither of which is on a non-login PATH. `-s`
# reads the script from stdin, because tests/ is not one of the sandbox's
# mounts and so cannot be named as a path inside the VM. Feeding stdin from
# the file also closes it at EOF, which is what stops the guest blocking on a
# pipe that never ends -- the same reason md2okf.sandbox runs every
# non-interactive `pi` with stdin=DEVNULL.
sbx exec "${kit_name}" -- sh -l -s <"${repo_root}/tests/test-sandbox-guest.sh"
