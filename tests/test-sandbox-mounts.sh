#!/usr/bin/env bash
# Host-side tests for .env loading and sandbox workspace arguments.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/md2okf-mounts-test.XXXXXX")"
TESTS=0
trap 'rm -rf "${TEST_ROOT}"' EXIT

fail() {
	echo "not ok - $*" >&2
	exit 1
}

pass() {
	TESTS=$((TESTS + 1))
	echo "ok ${TESTS} - $*"
}

assert_eq() {
	local expected="$1"
	local actual="$2"
	local context="$3"
	[[ "${actual}" == "${expected}" ]] ||
		fail "${context}: expected '${expected}', got '${actual}'"
}

fixture() {
	local name="$1"
	CASE="${TEST_ROOT}/${name}"
	REPO="${CASE}/repo"
	HOME_DIR="${CASE}/home"
	mkdir -p "${REPO}/scripts/lib" "${REPO}/okf" "${REPO}/md" \
		"${REPO}/scripts" "${HOME_DIR}"
	cp "${ROOT}/scripts/lib/sandbox-mounts.sh" "${REPO}/scripts/lib/"
	: >"${REPO}/SPEC.md"
}

# A value exported by the caller has higher precedence than .env.
fixture exported
printf 'XDG_STATE_HOME="%s"\n' "${CASE}/from env file" >"${REPO}/.env"
actual="$({
	cd "${REPO}"
	HOME="${HOME_DIR}" XDG_STATE_HOME="${CASE}/exported state" bash -c '
		source scripts/lib/sandbox-mounts.sh
		sandbox_workspace_args
		printf "%s\n" "${SBXAGENT_STATE_DIR}"
	'
})"
assert_eq "${CASE}/exported state/md2okf" "${actual}" "exported precedence"
pass "an exported XDG_STATE_HOME takes precedence over .env"

# With no exported value, .env supplies the state home and may use HOME.
fixture env-file
# shellcheck disable=SC2016 # HOME must expand when the fixture is sourced
printf '%s\n' 'XDG_STATE_HOME="${HOME}/state from env"' >"${REPO}/.env"
actual="$({
	cd "${REPO}"
	# shellcheck disable=SC2016 # variables belong to the child shell
	env -u XDG_STATE_HOME HOME="${HOME_DIR}" bash -c '
		source scripts/lib/sandbox-mounts.sh
		sandbox_workspace_args
		printf "%s\n" "${SBXAGENT_STATE_DIR}"
	'
})"
assert_eq "${HOME_DIR}/state from env/md2okf" "${actual}" ".env precedence"
pass ".env supplies XDG_STATE_HOME when no exported value exists"

# A relative value is invalid under XDG and falls back to ~/.local/state even
# when it came from the higher-precedence exported environment.
fixture relative
printf 'XDG_STATE_HOME="%s"\n' "${CASE}/absolute from env" >"${REPO}/.env"
actual="$({
	cd "${REPO}"
	HOME="${HOME_DIR}" XDG_STATE_HOME="relative/state" bash -c '
		source scripts/lib/sandbox-mounts.sh
		sandbox_workspace_args
		printf "%s\n" "${SBXAGENT_STATE_DIR}"
	'
})"
assert_eq "${HOME_DIR}/.local/state/md2okf" "${actual}" "relative fallback"
pass "a relative XDG_STATE_HOME falls back to ~/.local/state"

# The function writes a real Bash array, preserving a state path containing
# spaces as one mount operand. It also creates the state directory mode 0700
# and never adds the removed repository-local logs mount.
fixture array
state_home="${CASE}/state with spaces"
output="$({
	cd "${REPO}"
	HOME="${HOME_DIR}" XDG_STATE_HOME="${state_home}" bash -c '
		source scripts/lib/sandbox-mounts.sh
		sandbox_workspace_args
		printf "count=%s\n" "${#workspace_args[@]}"
		printf "primary=%s\n" "${workspace_args[0]}"
		for arg in "${workspace_args[@]}"; do printf "arg=%s\n" "${arg}"; done
		if stat -c %a "${SBXAGENT_STATE_DIR}" >/dev/null 2>&1; then
			stat -c "mode=%a" "${SBXAGENT_STATE_DIR}"
		else
			stat -f "mode=%Lp" "${SBXAGENT_STATE_DIR}"
		fi
	'
})"
[[ "${output}" == *$'count=5'* ]] || fail "workspace array does not have five entries"
[[ "${output}" == *$'primary=./okf'* ]] || fail "okf is not the primary workspace"
[[ "${output}" == *"arg=${state_home}/md2okf"* ]] ||
	fail "state path containing spaces was not preserved as one array entry"
[[ "${output}" == *$'mode=700'* ]] || fail "state directory mode is not 0700"
[[ "${output}" != *"logs"* ]] || fail "workspace arguments still contain a logs mount"
pass "workspace arguments preserve spaces, secure state, and omit logs"

# Every creator must inject the same state path that it mounts. tests/
# test-sandbox.sh is deliberately absent: sandbox creation there moved to the
# md2okf driver, which builds its own narrowed mount set rather than this one.
for creator in scripts/compile-okf.sh scripts/pi.sh scripts/bash.sh; do
	grep -q 'sandbox_workspace_args' "${ROOT}/${creator}" ||
		fail "${creator} does not populate workspace_args"
	# shellcheck disable=SC2016 # match the creator's literal expansion
	grep -q -- '-e "SBXAGENT_STATE_DIR=${SBXAGENT_STATE_DIR}"' "${ROOT}/${creator}" ||
		fail "${creator} does not inject SBXAGENT_STATE_DIR"
done
pass "every sandbox creator mounts and injects the shared state directory"

# Pi starts in the wiki root. Runtime instructions must not point back to it as
# ../okf: although that resolves to the same inode, it makes the wiki look like
# a child directory and has caused agents to create okf/okf/.
pi_agent_dir="${ROOT}/kits/md2okf/files/home/.pi/agent"
if grep -R -F -q -- '../okf' "${pi_agent_dir}"; then
	fail "Pi runtime instructions still refer to the wiki as ../okf"
fi
for skill in compile-okf inspect-okf size-okf merkle-okf; do
	# shellcheck disable=SC2016 # Assert the literal runtime expansion in the skill.
	grep -F -q -- '"$PWD"' "${pi_agent_dir}/skills/${skill}/SKILL.md" ||
		fail "${skill} does not name the wiki root as \"\$PWD\""
done
pass "Pi runtime instructions use the workspace root, not ../okf"

echo "All ${TESTS} sandbox-mount tests passed."
