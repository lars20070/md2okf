#!/usr/bin/env bash
set -euo pipefail

# Check that one agent's sandbox delivers what kits/<agent>/ promises: the
# installed toolchain, the agent config from kits/<agent>/files/, a ready
# credential, and the driver's mount invariants. The checks themselves live in
# tests/test-sandbox-guest-common.sh, which every agent shares, and
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
#
# To pilot a kit change beside a working sandbox, set both MD2OKF_SANDBOX_NAME
# and a temporary XDG_STATE_HOME (see CONTRIBUTING.md); every path and name
# below comes from the driver, so both are honoured.

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

# Every name and path from the driver itself, not a copy of its rules.
driver_value() {
	MD2OKF_AGENT="${agent}" uv run python -c "from md2okf import agents, workbench
agent = agents.from_env()
wb = workbench.Workbench.default(agent.name)
print($1)"
}
sandbox_name="$(driver_value 'workbench.sandbox_name(agent.name)')"
sessions_dir="$(driver_value 'wb.sessions')"
wiki_dir="$(driver_value 'wb.work_okf')"

# `sh -l` is a LOGIN shell, as an interactive session would be; the host-side
# checks below repeat what matters under a plain `sbx exec`, which is how the
# driver runs everything. `-s`
# reads the script from stdin, because tests/ is not one of the sandbox's
# mounts and so cannot be named as a path inside the VM: the agent's file
# (definitions only) and then the common file, as one script. `cat` closes
# stdin at EOF, which is what stops the guest blocking on a pipe that never
# ends -- the same reason md2okf.sandbox runs every non-interactive agent
# turn with stdin=DEVNULL.
#
# REQUIRE_GITHUB=1 (Pi only) makes "no GitHub secret bound" a failure rather
# than a skip. It goes in as the script's first line because a plain `sbx
# exec` does not carry the host's environment; only a literal 1 is passed.
require_github=0
[[ "${REQUIRE_GITHUB:-0}" == 1 ]] && require_github=1
guest_log="$(mktemp "${TMPDIR:-/tmp}/md2okf-guest.XXXXXX")"
trap 'rm -f "${guest_log}"' EXIT
{
	printf 'REQUIRE_GITHUB=%s\n' "${require_github}"
	cat "${guest_script}" "${common_script}"
} |
	sbx exec "${sandbox_name}" -- sh -l -s | tee "${guest_log}"

# --- host-side checks ----------------------------------------------------------
#
# What only the host can see, or only a plain `sbx exec` reproduces.
host_failures=0

# A plain, non-login `sbx exec`, exactly as the driver starts every agent
# turn: it must start in the wiki root, and a shim must run on that PATH
# against the wiki at the host path the driver names (compile.wiki_root_hash).
plain_pwd="$(sbx exec "${sandbox_name}" -- pwd -P </dev/null)" || true
if [[ "${plain_pwd}" == "${wiki_dir}" ]]; then
	echo "ok a plain sbx exec starts in the wiki root, at its host path"
else
	echo "BROKEN a plain sbx exec starts in '${plain_pwd}', not ${wiki_dir}"
	host_failures=$((host_failures + 1))
fi
if sbx exec "${sandbox_name}" -- merkleokf --nolog -L 0 "${wiki_dir}" </dev/null >/dev/null 2>&1; then
	echo "ok merkleokf runs under a plain sbx exec on the wiki's host path"
else
	echo "BROKEN merkleokf failed under a plain sbx exec on ${wiki_dir}"
	host_failures=$((host_failures + 1))
fi

# Pi only: the GitHub credential under the same plain exec. Never print the
# value; the inner shell reports a verdict.
if [[ "${agent}" == pi ]]; then
	# shellcheck disable=SC2016 # expanded by the inner shell
	verdict="$(sbx exec "${sandbox_name}" -- sh -c '
		if [ "${SBX_CRED_GITHUB_MODE:-none}" = none ]; then echo unbound
		elif [ "${GITHUB_TOKEN-}" = proxy-managed ]; then echo ok
		else echo bad; fi' </dev/null)" || true
	case "${verdict}" in
	ok) echo "ok GITHUB_TOKEN is the sentinel under a plain sbx exec" ;;
	unbound) echo "ok skipped: no GitHub secret bound" ;;
	*)
		echo "BROKEN GITHUB_TOKEN is not the sentinel under a plain sbx exec"
		host_failures=$((host_failures + 1))
		;;
	esac
fi

# The guest wrote a token through the agent's native trace path; it must be
# in this agent's workbench sessions/ on the host, which is the whole point of
# the mount.
token="$(sed -n 's/^trace-probe //p' "${guest_log}" | tail -n 1)"
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
