#!/bin/sh

# Codex's half of the in-sandbox checks: definitions only.
# tests/test-sandbox.sh pipes this file and then
# tests/test-sandbox-guest-common.sh into the md2okf-codex sandbox as one
# script; the common file documents the interface and runs everything,
# including agent_checks below.
#
# shellcheck disable=SC2034 # every AGENT_* variable is read by the common file

AGENT_NAME=codex
AGENT_BINARY=codex
AGENT_TRACE_DIR="${HOME}/.codex/sessions"
# Codex's global instructions: the one place it reads them from when the
# workspace is not a git repository (measured by the Codex spike).
AGENT_INSTRUCTIONS="${HOME}/.codex/AGENTS.md"
skills="${HOME}/.agents/skills"
AGENT_RUNTIME_PATHS="${AGENT_INSTRUCTIONS} ${skills}/compile-okf ${skills}/curate-okf ${skills}/inspect-md ${skills}/inspect-okf ${skills}/merkle-okf ${skills}/size-okf"

agent_checks() {
	# Config delivery: kits/codex/files/home/ is copied at kit build time,
	# and the codex parent rewrites parts of ~/.codex/ at every create -- so a
	# layout change, or a clash with the parent, can leave Codex with no
	# instructions or no skill.
	check_file "${skills}/compile-okf/SKILL.md"
	check_exec "${skills}/compile-okf/scripts/check-okf.sh"
	check_file "${skills}/compile-okf/scripts/frontmatter-guard.py"
	check_file "${skills}/inspect-md/SKILL.md"
	check_file "${skills}/inspect-okf/SKILL.md"
	check_file "${skills}/size-okf/SKILL.md"
	check_file "${skills}/merkle-okf/SKILL.md"
	check_file "${skills}/curate-okf/SKILL.md"

	if grep -q "^# OKF Wiki Maintainer" "${AGENT_INSTRUCTIONS}" 2>/dev/null; then
		ok "Codex's global AGENTS.md carries the md2okf instructions"
	else
		broken "Codex's global AGENTS.md does not carry the md2okf instructions: ${AGENT_INSTRUCTIONS}"
	fi

	# The override every compile turn passes must still switch the parent's
	# MCP gateway off (measured by the Codex spike on codex-cli 0.149.1).
	# Positive evidence only: a `codex` that failed to run must not pass.
	servers="$(timeout 30 codex -c 'mcp_servers.mcp-gateway.enabled=false' mcp list 2>/dev/null)"
	if printf '%s\n' "${servers}" | grep -q 'mcp-gateway.*disabled'; then
		ok "the compile override disables the parent's MCP gateway"
	elif printf '%s\n' "${servers}" | grep -q '^Name'; then
		if printf '%s\n' "${servers}" | grep -q 'mcp-gateway'; then
			broken "the compile override no longer disables the parent's MCP gateway"
		else
			ok "the parent registers no MCP gateway to switch off"
		fi
	else
		broken "could not list Codex's MCP servers"
	fi

	# Credentials: the same local, unpaid probe md2okf runs before every
	# compile. Reports a verdict only, never account details.
	if timeout 30 codex login status 2>&1 | grep -q "Logged in"; then
		ok "codex login status: logged in"
	else
		broken "codex login status: not logged in (sbx secret set openai, then rebuild)"
	fi
}
