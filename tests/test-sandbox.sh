#!/usr/bin/env bash
set -euo pipefail

# Check that one agent's sandbox delivers what kits/<agent>/spec.yaml promises:
# the installed toolchain, the agent config copied in from kits/<agent>/files/,
# a ready credential, and the driver's mount invariants. The checks themselves
# live in tests/test-sandbox-guest-<agent>.sh.
#
# Usage: test-sandbox.sh AGENT      (e.g. pi; `make test-sandbox` runs them all)
#
# The agent is required, with no default, so a mistyped or forgotten one fails
# here instead of silently testing Pi.
#
# Reuses the agent's existing sandbox, creating one only if missing (minutes),
# so it may be testing a sandbox older than your last kits/<agent>/ edit. To
# force a fresh one: sbx rm --force md2okf-pi && ./tests/test-sandbox.sh pi

if [[ "$#" -ne 1 || -z "$1" ]]; then
	echo "Usage: $0 AGENT   (e.g. pi)" >&2
	exit 2
fi
agent="$1"

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

guest_script="${repo_root}/tests/test-sandbox-guest-${agent}.sh"
if [[ ! -f "${guest_script}" ]]; then
	echo "Error: no guest checks for agent '${agent}' (${guest_script} is missing)." >&2
	exit 2
fi

sandbox_name="md2okf-${agent}" # workbench.sandbox_name()

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
MD2OKF_AGENT="${agent}" uv run python -m md2okf.sandbox

# `sh -l` must be a LOGIN shell: the uv tools land in ~/.local/bin and the npm
# globals in the user prefix, neither of which is on a non-login PATH. `-s`
# reads the script from stdin, because tests/ is not one of the sandbox's
# mounts and so cannot be named as a path inside the VM. Feeding stdin from
# the file also closes it at EOF, which is what stops the guest blocking on a
# pipe that never ends -- the same reason md2okf.sandbox runs every
# non-interactive agent turn with stdin=DEVNULL.
sbx exec "${sandbox_name}" -- sh -l -s <"${guest_script}"
