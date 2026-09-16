#!/usr/bin/env bash
# Exercise the kit's mount-state helper directly on the host.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HELPER="${ROOT}/kits/md2okf/files/home/.local/lib/md2okf/mount-state.sh"
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
	[[ -z "${SBXAGENT_REQUIRE_BIND:-}" ]] ||
		fail "$* — SBXAGENT_REQUIRE_BIND is set"
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
	export SBXAGENT_STATE_DIR="${STATE}"
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
unset SBXAGENT_STATE_DIR
mkdir -p "${LINK}"
run_helper "${LINK}" sessions
assert_eq 0 "${STATUS}" "no-env status"
[[ -d "${LINK}" && ! -e "${STATE}" ]] || fail "no-env invocation changed state"
pass "an unset SBXAGENT_STATE_DIR is a no-op"

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

# Extract and execute the real entrypoint block. Pi must not launch after a
# relocation failure.
SPEC="${ROOT}/kits/md2okf/spec.yaml"
ENTRYPOINT="$(awk '
	$0 == "    - |" { block = 1; next }
	block && /^    - / { exit }
	block { sub(/^      /, ""); print }
' "${SPEC}")"
fresh entrypoint
FAKE_HOME="${CASE}/home/agent"
FAKE_BIN="${CASE}/bin"
AGENT_LOG="${CASE}/agent.log"
mkdir -p "${FAKE_HOME}/.local/lib/md2okf" "${FAKE_BIN}"
# shellcheck disable=SC2016 # variables belong to the generated scripts
printf '#!/bin/sh\nexit "${MOUNT_STATE_TEST_STATUS}"\n' \
	>"${FAKE_HOME}/.local/lib/md2okf/mount-state.sh"
# shellcheck disable=SC2016 # variables belong to the generated scripts
printf '#!/bin/sh\nprintf "started\\n" >>"${ENTRYPOINT_AGENT_LOG}"\n' \
	>"${FAKE_BIN}/pi"
chmod +x "${FAKE_HOME}/.local/lib/md2okf/mount-state.sh" "${FAKE_BIN}/pi"
: >"${AGENT_LOG}"
MOUNT_STATE_TEST_STATUS=0 ENTRYPOINT_AGENT_LOG="${AGENT_LOG}" HOME="${FAKE_HOME}" \
	PATH="${FAKE_BIN}:${PATH}" sh -c "${ENTRYPOINT}" md2okf-entrypoint
[[ -s "${AGENT_LOG}" ]] || fail "entrypoint did not launch Pi after a successful bind"
: >"${AGENT_LOG}"
set +e
MOUNT_STATE_TEST_STATUS=1 ENTRYPOINT_AGENT_LOG="${AGENT_LOG}" HOME="${FAKE_HOME}" \
	PATH="${FAKE_BIN}:${PATH}" sh -c "${ENTRYPOINT}" md2okf-entrypoint \
	2>"${CASE}/entrypoint-stderr"
STATUS=$?
set -e
assert_eq 1 "${STATUS}" "entrypoint failure status"
[[ ! -s "${AGENT_LOG}" ]] || fail "entrypoint launched Pi after relocation failed"
grep -q 'refusing to start pi' "${CASE}/entrypoint-stderr" ||
	fail "entrypoint did not explain its refusal"
pass "the Pi entrypoint refuses to launch when relocation fails"

# The bind is required from both lifecycle sites. Exactly two helper calls
# prevent either a missing site or an accidental duplicate.
calls="$(grep -c 'lib/md2okf/mount-state\.sh' "${SPEC}" || true)"
assert_eq 2 "${calls}" "mount-state call count"
STARTUP="$(awk '
	$0 == "  startup:" { block = 1; next }
	block && /^  [^ ]/ { exit }
	block { print }
' "${SPEC}")"
[[ "${STARTUP}" == *'lib/md2okf/mount-state.sh'* ]] ||
	fail "startup hook does not invoke mount-state.sh"
# shellcheck disable=SC2016 # match the spec's literal in-sandbox HOME
[[ "${STARTUP}" == *'"$HOME/.pi/agent/sessions" sessions'* ]] ||
	fail "startup hook passes the wrong session path"
[[ "${STARTUP}" == *'user: "agent"'* ]] ||
	fail "startup hook does not run as the agent user"
pass "the kit invokes mount-state.sh from entrypoint and startup"

echo "All ${TESTS} mount-state tests passed."
