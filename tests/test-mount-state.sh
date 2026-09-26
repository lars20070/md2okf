#!/usr/bin/env bash
# Exercise the kit's mount-state helper directly on the host.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HELPER="${ROOT}/kits/pi/files/home/.local/lib/md2okf/mount-state.sh"
WRAPPER="${ROOT}/kits/pi/files/home/.local/lib/md2okf/md2okf-agent.sh"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/md2okf-state-test.XXXXXX")"
TESTS=0

unmount_all() {
	local pass_number mount_point
	[[ -r /proc/self/mountinfo ]] || return 0
	for pass_number in 1 2 3; do
		: "${pass_number}"
		while read -r mount_point; do
			sudo -n umount "${mount_point}" 2>/dev/null || true
		done < <(awk '{ print $5 }' /proc/self/mountinfo |
			grep -F "${TEST_ROOT}/" | awk '{ print length, $0 }' |
			sort -rn | cut -d' ' -f2-)
	done
}

cleanup() {
	unmount_all
	chmod -R u+rwx "${TEST_ROOT}" 2>/dev/null || true
	rm -rf "${TEST_ROOT}"
}
trap cleanup EXIT

fail() {
	echo "not ok - $*" >&2
	exit 1
}

pass() {
	TESTS=$((TESTS + 1))
	echo "ok ${TESTS} - $*"
}

skip() {
	[[ -z "${MD2OKF_REQUIRE_BIND:-}" ]] ||
		fail "$* — MD2OKF_REQUIRE_BIND is set"
	echo "skip - $*"
}

assert_eq() {
	local expected="$1"
	local actual="$2"
	local context="$3"
	[[ "${actual}" == "${expected}" ]] ||
		fail "${context}: expected '${expected}', got '${actual}'"
}

mount_count() {
	[[ -r /proc/self/mountinfo ]] || { echo 0; return 0; }
	awk -v path="$1" '$5 == path { total++ } END { print total + 0 }' \
		/proc/self/mountinfo
}

STDERR=""
STATUS=0
run_helper() {
	local stderr_file="${TEST_ROOT}/stderr"
	set +e
	sh "${HELPER}" "$@" 2>"${stderr_file}"
	STATUS=$?
	set -e
	STDERR="$(<"${stderr_file}")"
}

fresh() {
	local name="$1"
	CASE="${TEST_ROOT}/${name}"
	STATE="${CASE}/state"
	LINK="${CASE}/home/agent/sessions"
	mkdir -p "${CASE}/home/agent"
	export MD2OKF_STATE_DIR="${STATE}"
}

stub_command() {
	local command="$1"
	local status="$2"
	FAKE_BIN="${CASE}/bin"
	mkdir -p "${FAKE_BIN}"
	printf '#!/bin/sh\nexit %s\n' "${status}" >"${FAKE_BIN}/${command}"
	chmod +x "${FAKE_BIN}/${command}"
}

BIND_AVAILABLE=no
mkdir -p "${TEST_ROOT}/bind-probe/src" "${TEST_ROOT}/bind-probe/dst"
if sudo -n mount --bind "${TEST_ROOT}/bind-probe/src" \
	"${TEST_ROOT}/bind-probe/dst" 2>/dev/null; then
	sudo -n umount "${TEST_ROOT}/bind-probe/dst" 2>/dev/null || true
	BIND_AVAILABLE=yes
fi

fresh no-env
unset MD2OKF_STATE_DIR
mkdir -p "${LINK}"
run_helper "${LINK}" sessions
assert_eq 0 "${STATUS}" "no-env status"
[[ -d "${LINK}" && ! -e "${STATE}" ]] || fail "no-env invocation changed state"
pass "an unset MD2OKF_STATE_DIR is a no-op"

if [[ "${BIND_AVAILABLE}" == yes ]]; then
	fresh first
	LINK="${CASE}/home/agent/.pi/agent/sessions"
	run_helper "${LINK}" sessions
	assert_eq 0 "${STATUS}" "first bind status"
	assert_eq "$(stat -c '%d:%i' "${STATE}/sessions")" \
		"$(stat -c '%d:%i' "${LINK}")" "first bind identity"
	echo one >"${LINK}/trace"
	assert_eq one "$(<"${STATE}/sessions/trace")" "write-through"
	assert_eq 1 "$(mount_count "${LINK}")" "initial mount count"
	run_helper "${LINK}" sessions
	assert_eq 0 "${STATUS}" "repeat status"
	assert_eq 1 "$(mount_count "${LINK}")" "repeat mount count"
	pass "initial bind works and a repeated invocation is idempotent"
	unmount_all
else
	skip "initial-bind and idempotency cases need sudo mount --bind"
fi

fresh merge
mkdir -p "${STATE}/sessions/shared" "${LINK}/shared" "${LINK}/nested"
echo host >"${STATE}/sessions/shared/trace"
echo keep >"${STATE}/sessions/only-in-state"
echo stale >"${LINK}/shared/trace"
echo seeded >"${LINK}/fresh"
echo hidden >"${LINK}/.dotfile"
echo deep >"${LINK}/nested/trace"
stub_command sudo 0
PATH="${FAKE_BIN}:${PATH}" run_helper "${LINK}" sessions
assert_eq 0 "${STATUS}" "merge status"
assert_eq host "$(<"${STATE}/sessions/shared/trace")" "host value"
assert_eq keep "$(<"${STATE}/sessions/only-in-state")" "state-only value"
assert_eq seeded "$(<"${STATE}/sessions/fresh")" "merged value"
assert_eq hidden "$(<"${STATE}/sessions/.dotfile")" "merged dotfile"
assert_eq deep "$(<"${STATE}/sessions/nested/trace")" "merged directory"
pass "host state is authoritative while absent stock entries are merged"

fresh bind-fails
mkdir -p "${LINK}"
echo one >"${LINK}/trace"
stub_command sudo 1
PATH="${FAKE_BIN}:${PATH}" run_helper "${LINK}" sessions
assert_eq 1 "${STATUS}" "bind failure status"
[[ "${STDERR}" == *"could not bind-mount"* ]] || fail "bind failure was not reported"
pass "a bind failure is fatal"

fresh copy-fails
mkdir -p "${LINK}"
echo one >"${LINK}/trace"
stub_command cp 1
stub_command sudo 0
PATH="${FAKE_BIN}:${PATH}" run_helper "${LINK}" sessions
assert_eq 1 "${STATUS}" "copy failure status"
[[ "${STDERR}" == *"could not copy"* ]] || fail "copy failure was not reported"
pass "a copy failure is fatal"

# --- md2okf-agent.sh: the per-process wrapper ---------------------------------
#
# The driver starts every agent process through it (`sbx exec` bypasses the
# entrypoint), so it is the only relocation guard on an automated turn. Driven
# like the entrypoint above: a stub mount-state.sh under a fake HOME whose
# status the case chooses, and a stub agent that records exactly what it got.
fresh wrapper
FAKE_HOME="${CASE}/home/agent"
FAKE_BIN="${CASE}/bin"
AGENT_LOG="${CASE}/agent.log"
MOUNT_LOG="${CASE}/mount.log"
mkdir -p "${FAKE_HOME}/.local/lib/md2okf" "${FAKE_BIN}"
# shellcheck disable=SC2016 # variables belong to the generated scripts
printf '#!/bin/sh\nprintf "%%s|" "$@" >"${WRAPPER_MOUNT_LOG}"\nexit "${MOUNT_STATE_TEST_STATUS}"\n' \
	>"${FAKE_HOME}/.local/lib/md2okf/mount-state.sh"
# shellcheck disable=SC2016 # variables belong to the generated scripts
printf '#!/bin/sh\nfor arg in "$@"; do printf "[%%s]\\n" "$arg"; done >"${WRAPPER_AGENT_LOG}"\nexit "${FAKE_AGENT_STATUS:-0}"\n' \
	>"${FAKE_BIN}/fake-agent"
chmod +x "${FAKE_BIN}/fake-agent"

run_wrapper() {
	local stderr_file="${CASE}/wrapper-stderr"
	: >"${AGENT_LOG}"
	: >"${MOUNT_LOG}"
	set +e
	WRAPPER_AGENT_LOG="${AGENT_LOG}" WRAPPER_MOUNT_LOG="${MOUNT_LOG}" \
		HOME="${FAKE_HOME}" PATH="${FAKE_BIN}:${PATH}" sh "${WRAPPER}" "$@" \
		2>"${stderr_file}"
	STATUS=$?
	set -e
	STDERR="$(<"${stderr_file}")"
}

MOUNT_STATE_TEST_STATUS=0 run_wrapper /trace/dir fake-agent "two words" "" last
assert_eq 0 "${STATUS}" "wrapper success status"
assert_eq "/trace/dir|sessions|" "$(<"${MOUNT_LOG}")" "wrapper relocation arguments"
assert_eq $'[two words]\n[]\n[last]' "$(<"${AGENT_LOG}")" "wrapper argument forwarding"
pass "the wrapper relocates the trace directory, then runs the agent with its arguments intact"

MOUNT_STATE_TEST_STATUS=0 FAKE_AGENT_STATUS=7 run_wrapper /trace/dir fake-agent
assert_eq 7 "${STATUS}" "wrapper exit status passthrough"
pass "the agent's own exit status comes back unchanged"

MOUNT_STATE_TEST_STATUS=1 run_wrapper /trace/dir fake-agent --should-not-run
assert_eq 1 "${STATUS}" "wrapper relocation failure status"
[[ ! -s "${AGENT_LOG}" ]] || fail "the wrapper started the agent after relocation failed"
[[ "${STDERR}" == *"refusing to start fake-agent"* ]] ||
	fail "the wrapper did not explain its refusal: ${STDERR}"
pass "the wrapper refuses to start the agent when relocation fails"

MOUNT_STATE_TEST_STATUS=0 run_wrapper /trace/dir
assert_eq 2 "${STATUS}" "wrapper usage status"
[[ ! -s "${MOUNT_LOG}" ]] || fail "the wrapper relocated with no command to run"
[[ "${STDERR}" == *"usage:"* ]] || fail "the wrapper did not print its usage"
pass "the wrapper refuses to run without a command"

# --- every kit's relocation sites ----------------------------------------------
#
# The bind is required from all three lifecycle sites: the entrypoint (starts
# where the startup hook is not replayed), the startup hook (normal starts),
# and the wrapper shim (every process the driver starts with `sbx exec`). Each
# is named rather than counted, so a missing site and a stray duplicate are
# both caught with a message saying which -- and all three must name the same
# native trace directory, or an agent's traces would be bound in one lifecycle
# and land on the VM's disposable disk in another.
#
# check_kit KIT AGENT_BINARY TRACE_DIR -- TRACE_DIR relative to $HOME.
check_kit() {
	local kit="$1" binary="$2" trace="$3"
	local spec="${ROOT}/kits/${kit}/spec.yaml"
	local entrypoint startup shim calls fake_home fake_bin agent_log
	[[ -f "${spec}" ]] || fail "kits/${kit}/spec.yaml is missing"

	# Extract and execute the real entrypoint block: the agent must not launch
	# after a relocation failure.
	entrypoint="$(awk '
		$0 == "    - |" { block = 1; next }
		block && /^    - / { exit }
		block { sub(/^      /, ""); print }
	' "${spec}")"
	[[ -n "${entrypoint}" ]] || fail "kits/${kit}: no entrypoint block found"
	fresh "entrypoint-${kit}"
	fake_home="${CASE}/home/agent"
	fake_bin="${CASE}/bin"
	agent_log="${CASE}/agent.log"
	mkdir -p "${fake_home}/.local/lib/md2okf" "${fake_bin}"
	# shellcheck disable=SC2016 # variables belong to the generated scripts
	printf '#!/bin/sh\nexit "${MOUNT_STATE_TEST_STATUS}"\n' \
		>"${fake_home}/.local/lib/md2okf/mount-state.sh"
	# shellcheck disable=SC2016 # variables belong to the generated scripts
	printf '#!/bin/sh\nprintf "started\\n" >>"${ENTRYPOINT_AGENT_LOG}"\n' \
		>"${fake_bin}/${binary}"
	chmod +x "${fake_home}/.local/lib/md2okf/mount-state.sh" "${fake_bin}/${binary}"
	: >"${agent_log}"
	MOUNT_STATE_TEST_STATUS=0 ENTRYPOINT_AGENT_LOG="${agent_log}" HOME="${fake_home}" \
		PATH="${fake_bin}:${PATH}" sh -c "${entrypoint}" md2okf-entrypoint
	[[ -s "${agent_log}" ]] || fail "kits/${kit}: entrypoint did not launch ${binary} after a successful bind"
	: >"${agent_log}"
	set +e
	MOUNT_STATE_TEST_STATUS=1 ENTRYPOINT_AGENT_LOG="${agent_log}" HOME="${fake_home}" \
		PATH="${fake_bin}:${PATH}" sh -c "${entrypoint}" md2okf-entrypoint \
		2>"${CASE}/entrypoint-stderr"
	STATUS=$?
	set -e
	assert_eq 1 "${STATUS}" "kits/${kit} entrypoint failure status"
	[[ ! -s "${agent_log}" ]] || fail "kits/${kit}: entrypoint launched ${binary} after relocation failed"
	grep -q "refusing to start ${binary}" "${CASE}/entrypoint-stderr" ||
		fail "kits/${kit}: entrypoint did not explain its refusal"
	pass "kits/${kit}: the entrypoint refuses to launch ${binary} when relocation fails"

	calls="$(grep -c 'lib/md2okf/mount-state\.sh' "${spec}" || true)"
	assert_eq 2 "${calls}" "kits/${kit}: mount-state calls in the spec (entrypoint and startup)"
	# shellcheck disable=SC2016 # match the spec's literal in-sandbox HOME
	[[ "${entrypoint}" == *'"$HOME/'"${trace}"'" sessions'* ]] ||
		fail "kits/${kit}: entrypoint does not relocate ~/${trace}"
	startup="$(awk '
		$0 == "  startup:" { block = 1; next }
		block && /^  [^ ]/ { exit }
		block { print }
	' "${spec}")"
	# shellcheck disable=SC2016 # match the spec's literal in-sandbox HOME
	[[ "${startup}" == *'"$HOME/'"${trace}"'" sessions'* ]] ||
		fail "kits/${kit}: startup hook does not relocate ~/${trace}"
	[[ "${startup}" == *'user: "agent"'* ]] ||
		fail "kits/${kit}: startup hook does not run as the agent user"
	shim="$(awk '
		$0 == "    - path: /home/agent/.local/bin/md2okf-agent" { block = 1; next }
		block && /^    - path: / { exit }
		block { print }
	' "${spec}")"
	[[ -n "${shim}" ]] || fail "kits/${kit}: no md2okf-agent shim"
	[[ "${shim}" == *'/.local/lib/md2okf/md2okf-agent.sh"'* ]] ||
		fail "kits/${kit}: the md2okf-agent shim does not run md2okf-agent.sh"
	# shellcheck disable=SC2016 # match the spec's literal in-sandbox paths
	[[ "${shim}" == *'"${home}/'"${trace}"'" "$@"'* ]] ||
		fail "kits/${kit}: the md2okf-agent shim does not pass ~/${trace}"
	cmp -s "${WRAPPER}" "${ROOT}/kits/${kit}/files/home/.local/lib/md2okf/md2okf-agent.sh" ||
		fail "kits/${kit}: md2okf-agent.sh differs from kits/pi's"
	pass "kits/${kit}: entrypoint, startup hook and wrapper all relocate ~/${trace}"
}

grep -q 'lib/md2okf/mount-state\.sh' "${WRAPPER}" ||
	fail "md2okf-agent.sh does not invoke mount-state.sh"

check_kit pi pi .pi/agent/sessions
check_kit claude claude .claude/projects
check_kit codex codex .codex/sessions

echo "All ${TESTS} mount-state tests passed."
