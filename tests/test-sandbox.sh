#!/usr/bin/env bash
set -euo pipefail

# Check that one agent's sandbox delivers what kits/<agent>/spec.yaml promises:
# the installed toolchain, the agent config copied in from kits/<agent>/files/,
# a ready credential, and the driver's mount invariants. The checks themselves
# live in tests/test-sandbox-guest-common.sh, which every agent shares, and
# tests/test-sandbox-guest-<agent>.sh, which defines what differs.
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
common_script="${repo_root}/tests/test-sandbox-guest-common.sh"
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
# mounts and so cannot be named as a path inside the VM: the agent's file
# (definitions only) and then the common file, as one script. `cat` closes
# stdin at EOF, which is what stops the guest blocking on a pipe that never
# ends -- the same reason md2okf.sandbox runs every non-interactive agent
# turn with stdin=DEVNULL.
guest_log="$(mktemp "${TMPDIR:-/tmp}/md2okf-guest.XXXXXX")"
trap 'rm -f "${guest_log}"' EXIT
cat "${guest_script}" "${common_script}" |
	sbx exec "${sandbox_name}" -- sh -l -s | tee "${guest_log}"

# --- host-side checks ----------------------------------------------------------
#
# What only the host can see, or only a plain `sbx exec` reproduces.
host_failures=0

# The wrapper, run exactly as the driver runs every agent process: a plain,
# non-login `sbx exec`, so it must be on that PATH -- not only on the login
# shell's the guest script above ran in -- and must hand its arguments to the
# command untouched.
wrapped="$(sbx exec "${sandbox_name}" -- md2okf-agent printf '%s|' 'two words' last </dev/null)" || true
if [[ "${wrapped}" == "two words|last|" ]]; then
	echo "ok md2okf-agent runs a command under a plain sbx exec, arguments intact"
else
	echo "BROKEN md2okf-agent under a plain sbx exec printed '${wrapped}'"
	host_failures=$((host_failures + 1))
fi

# The guest wrote a token through the agent's native trace path; it must be
# in this agent's workbench sessions/ on the host, which is the whole point of
# the bind. The path comes from the driver itself, not a copy of its rules.
token="$(sed -n 's/^trace-probe //p' "${guest_log}" | tail -n 1)"
sessions_dir="$(
	MD2OKF_AGENT="${agent}" uv run python -c \
		'from md2okf import agents, workbench; print(workbench.Workbench.default(agents.from_env().name).sessions)'
)"
host_probe="${sessions_dir}/.md2okf-host-probe"
if [[ -n "${token}" && -f "${host_probe}" && "$(<"${host_probe}")" == "${token}" ]]; then
	echo "ok a trace written in the sandbox reached ${sessions_dir} on the host"
else
	echo "BROKEN the guest's trace probe did not reach ${host_probe}"
	host_failures=$((host_failures + 1))
fi
rm -f "${host_probe}"

if [[ "${host_failures}" -ne 0 ]]; then
	echo "FAILED: ${host_failures} host-side check(s)"
	exit 1
fi
echo "All host-side checks passed."
