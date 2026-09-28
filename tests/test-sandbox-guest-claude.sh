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
# sbx writes the kit's agentInstructions here, beside ../md and ../SPEC.md,
# after the claude parent's own notes (measured by the Claude spike).
AGENT_INSTRUCTIONS="$(dirname "$(pwd -P)")/CLAUDE.md"
skills="${HOME}/.claude/skills"
# Only md2okf's own skills: ~/.claude/skills also holds the parent's bundled
# ones, which are not this kit's to police.
AGENT_RUNTIME_PATHS="${AGENT_INSTRUCTIONS} ${skills}/compile-okf ${skills}/curate-okf ${skills}/inspect-md ${skills}/inspect-okf ${skills}/merkle-okf ${skills}/size-okf"

agent_checks() {
	# Config delivery: kits/claude/files/home/.claude/skills/ is copied at
	# kit build time into a directory the parent kit already populates, so a
	# layout change -- or a clash with the parent -- can leave Claude with no
	# skill.
	check_file "${skills}/compile-okf/SKILL.md"
	check_exec "${skills}/compile-okf/scripts/check-okf.sh"
	check_file "${skills}/compile-okf/scripts/frontmatter-guard.py"
	check_file "${skills}/inspect-md/SKILL.md"
	check_file "${skills}/inspect-okf/SKILL.md"
	check_file "${skills}/size-okf/SKILL.md"
	check_file "${skills}/merkle-okf/SKILL.md"
	check_file "${skills}/curate-okf/SKILL.md"

	# The whole OKF contract, not just the parent's generic notes, reached
	# the instructions file.
	if grep -q "^# OKF Wiki Maintainer" "${AGENT_INSTRUCTIONS}" 2>/dev/null; then
		ok "CLAUDE.md carries the md2okf instructions"
	else
		broken "CLAUDE.md does not carry the md2okf instructions: ${AGENT_INSTRUCTIONS}"
	fi

	# Credentials: the same local, unpaid probe md2okf runs before every
	# compile. Reports a verdict only, never account details.
	if timeout 30 claude auth status 2>/dev/null | jq -e '.loggedIn == true' >/dev/null 2>&1; then
		ok "claude auth status: logged in"
	else
		broken "claude auth status: not logged in (sbx secret set anthropic, then rebuild)"
	fi
}
