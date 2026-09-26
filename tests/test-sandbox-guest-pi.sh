#!/bin/sh

# Pi's half of the in-sandbox checks: definitions only. tests/test-sandbox.sh
# pipes this file and then tests/test-sandbox-guest-common.sh into the
# md2okf-pi sandbox as one script; the common file documents the interface and
# runs everything, including agent_checks below.
#
# shellcheck disable=SC2034 # every AGENT_* variable is read by the common file

AGENT_NAME=pi
AGENT_BINARY=pi
AGENT_TRACE_DIR="${HOME}/.pi/agent/sessions"
AGENT_INSTRUCTIONS="${HOME}/.pi/agent/AGENTS.md"
AGENT_RUNTIME_PATHS="${HOME}/.pi/agent/AGENTS.md ${HOME}/.pi/agent/skills"

agent_checks() {
	# Config delivery: kits/pi/files/home/.pi/agent/ is copied at kit build
	# time, not mounted, so a layout change can leave Pi with no instructions
	# and no skill.
	check_file "${HOME}/.pi/agent/settings.json"
	check_file "${HOME}/.pi/agent/models.json"
	check_file "${HOME}/.pi/agent/skills/compile-okf/SKILL.md"
	check_exec "${HOME}/.pi/agent/skills/compile-okf/scripts/check-okf.sh"
	check_file "${HOME}/.pi/agent/skills/compile-okf/scripts/frontmatter-guard.py"
	check_file "${HOME}/.pi/agent/skills/inspect-md/SKILL.md"
	check_file "${HOME}/.pi/agent/skills/inspect-okf/SKILL.md"
	check_file "${HOME}/.pi/agent/skills/size-okf/SKILL.md"
	check_file "${HOME}/.pi/agent/skills/merkle-okf/SKILL.md"
	check_file "${HOME}/.pi/agent/skills/curate-okf/SKILL.md"

	# Context7 native Pi package (kits/pi/spec.yaml setup.install +
	# settings.json packages). Presence only — no live Context7 API call.
	if timeout 20 pi list 2>/dev/null | grep -q context7-pi; then
		ok "context7-pi (pi list)"
	else
		echo "MISSING context7-pi (pi list)"
		failures=$((failures + 1))
	fi

	if grep -q 'npm:@upstash/context7-pi@0.1.2' "${HOME}/.pi/agent/settings.json"; then
		ok "settings.json context7-pi package"
	else
		echo "MISSING settings.json context7-pi package"
		failures=$((failures + 1))
	fi

	c7_skill=$(
		find "${HOME}/.pi/agent/npm" \
			-path '*context7-pi*/skills/context7-docs/SKILL.md' \
			2>/dev/null | head -n 1
	)
	if [ -n "${c7_skill}" ] && [ -f "${c7_skill}" ]; then
		ok "${c7_skill}"
	else
		echo "MISSING context7-docs SKILL.md under ~/.pi/agent/npm"
		failures=$((failures + 1))
	fi

	# Credentials (kits/pi/spec.yaml). Automates the manual check in the
	# README. Never print the value — case-match and report only a verdict.
	case "${OPENROUTER_API_KEY-}" in
	"")
		echo "MISSING OPENROUTER_API_KEY"
		failures=$((failures + 1))
		;;
	proxy-managed) ok "OPENROUTER_API_KEY" ;;
	*) broken "OPENROUTER_API_KEY (literal value in the VM, expected the proxy-managed sentinel)" ;;
	esac
}
