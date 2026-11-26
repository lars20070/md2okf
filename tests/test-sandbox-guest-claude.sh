#!/bin/sh

# Claude Code's half of the in-sandbox checks: definitions only.
# tests/test-sandbox.sh pipes this file and then
# tests/test-sandbox-guest-common.sh into the md2okf-claude sandbox as one
# script; the common file documents the interface and runs everything,
# including agent_checks below.
#
# shellcheck disable=SC2034 # every AGENT_* variable is read by the common file

AGENT_NAME=claude
AGENT_BINARY=claude
AGENT_TRACE_DIR="${HOME}/.claude/projects"
AGENT_CONFIG_DIR="${HOME}/.claude"
# The workload's agent-context@2 profile: its own generic notes, then the
# kit's OKF contract.
AGENT_INSTRUCTIONS="${HOME}/.claude/CLAUDE.md"
skills="${HOME}/.claude/skills"
# Only md2okf's own skills: ~/.claude/skills may also hold the host's shared
# store, which is not this kit's to police.
AGENT_RUNTIME_PATHS="${AGENT_INSTRUCTIONS} ${skills}/compile-okf/ ${skills}/curate-okf/ ${skills}/inspect-md/ ${skills}/inspect-okf/ ${skills}/merkle-okf/ ${skills}/size-okf/"

agent_checks() {
	# Skill delivery: the kit ships its skills under /usr/share and the
	# runtime exposes them here (agent-skill@1), beside whatever the host's
	# shared store holds -- so a layout change, or a clash with the store,
	# can leave Claude with no skill.
	check_file "${skills}/compile-okf/SKILL.md"
	check_exec "${skills}/compile-okf/scripts/check-okf.sh"
	check_file "${skills}/compile-okf/scripts/frontmatter-guard.py"
	check_file "${skills}/inspect-md/SKILL.md"
	check_file "${skills}/inspect-okf/SKILL.md"
	check_file "${skills}/size-okf/SKILL.md"
	check_file "${skills}/merkle-okf/SKILL.md"
	check_file "${skills}/curate-okf/SKILL.md"

	# Both bodies reached the profile: the kit's whole OKF contract, and the
	# workload's own guidance, which v3 composes into the same file.
	if grep -q "^# OKF Wiki Maintainer" "${AGENT_INSTRUCTIONS}" 2>/dev/null; then
		ok "CLAUDE.md carries the md2okf instructions"
	else
		broken "CLAUDE.md does not carry the md2okf instructions: ${AGENT_INSTRUCTIONS}"
	fi
	if grep -q "Claude Code is installed at" "${AGENT_INSTRUCTIONS}" 2>/dev/null; then
		ok "CLAUDE.md keeps the workload's own guidance"
	else
		broken "CLAUDE.md lost the workload's own guidance: ${AGENT_INSTRUCTIONS}"
	fi

	# Credentials: the same local, unpaid probe md2okf runs before every
	# compile. Reports a verdict only, never account details.
	if timeout 30 claude auth status 2>/dev/null | jq -e '.loggedIn == true' >/dev/null 2>&1; then
		ok "claude auth status: logged in"
	else
		broken "claude auth status: not logged in (sbx secret set anthropic, then rebuild)"
	fi
}
