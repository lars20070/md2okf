#!/bin/sh

# Runs INSIDE the md2okf sandbox, piped into `sbx exec ... sh -l -s` by
# tests/test-sandbox.sh (tests/ is not mounted, so this file cannot be named as
# a path inside the VM). Run on the host it would happily report on your
# laptop's toolchain instead, which proves nothing.
#
# POSIX sh, not bash: the guest shell is `sh`, so the `#!/bin/sh` shebang above
# is what makes shellcheck reject a bashism here rather than leaving it to fail
# inside the VM. Everything below relies on the login shell (`sh -l`) having put
# ~/.local/bin and the npm prefix on PATH.
#
# Deliberately no `set -e`: every check runs, and all failures are reported in
# one pass rather than stopping at the first.

failures=0

# `command -v` first, then a uniform smoke run: `--version`, falling back to
# `--help`. That fallback is what makes CLIs with unknown flag support (pi,
# okf-lint, markdownlint-cli2, cspell) checkable without fixture files or
# hard-coding which flag each one accepts. `timeout` guards a tool that waits
# rather than prints. Output is discarded, so no version is asserted.
check() {
	if ! command -v "$1" >/dev/null 2>&1; then
		echo "MISSING $1"
		failures=$((failures + 1))
		return
	fi
	if timeout 20 "$1" --version >/dev/null 2>&1 ||
		timeout 20 "$1" --help >/dev/null 2>&1; then
		echo "ok $1"
	else
		echo "BROKEN $1"
		failures=$((failures + 1))
	fi
}

check_file() {
	if [ -f "$1" ]; then
		echo "ok $1"
	else
		echo "MISSING $1"
		failures=$((failures + 1))
	fi
}

# The kit COPIES files in, so a lost exec bit is a real failure mode. Distinguish
# "absent" from "present but not executable" so the message points at the fix.
check_exec() {
	if [ ! -e "$1" ]; then
		echo "MISSING $1"
		failures=$((failures + 1))
	elif [ ! -x "$1" ]; then
		echo "NOT_EXECUTABLE $1"
		failures=$((failures + 1))
	else
		echo "ok $1"
	fi
}

# The tool list must match BOTH lists in kits/md2okf/spec.yaml: the
# setup.install / setup.files steps AND the agentInstructions "Installed tools"
# prose. That prose is the promise being tested here, so a tool installed but
# not promised — or promised but not installed — is itself the bug.

case "$(pwd -P)" in
*/okf) echo "ok sandbox workspace is the wiki root" ;;
*)
	echo "BROKEN sandbox workspace is not the wiki root: $(pwd -P)"
	failures=$((failures + 1))
	;;
esac

# apt (kits/md2okf/spec.yaml). Ubuntu's `fd-find` package provides `fdfind`;
# `rg` is the command provided by the `ripgrep` package.
check curl
check fdfind
check jq
check python3
check rg
check shellcheck
check tree

# npm through the retry wrapper (kits/md2okf/spec.yaml).
check pi
check okf-lint

# npm, Markdown and spelling linters (kits/md2okf/spec.yaml).
check markdownlint-cli2
check cspell

# uv (kits/md2okf/spec.yaml).
check ruff
check yamllint

# setup.files shims (kits/md2okf/spec.yaml): workspace-backed CLIs on PATH.
check inspectmd
check inspectokf
check sizeokf
check merkleokf

# pinned release binary (kits/md2okf/spec.yaml): checksummed download, no
# package manager.
check mq

# Config delivery: kits/md2okf/files/home/.pi/agent/ is copied at kit build
# time, not mounted, so a layout change can leave Pi with no instructions and
# no skill.
check_file "${HOME}/.pi/agent/AGENTS.md"
check_file "${HOME}/.pi/agent/settings.json"
check_file "${HOME}/.pi/agent/models.json"
check_file "${HOME}/.pi/agent/skills/compile-okf/SKILL.md"
check_exec "${HOME}/.pi/agent/skills/compile-okf/scripts/lint-okf.sh"
check_file "${HOME}/.pi/agent/skills/inspect-md/SKILL.md"
check_file "${HOME}/.pi/agent/skills/inspect-okf/SKILL.md"
check_file "${HOME}/.pi/agent/skills/size-okf/SKILL.md"
check_file "${HOME}/.pi/agent/skills/merkle-okf/SKILL.md"
check_file "${HOME}/.local/lib/md2okf/mount-state.sh"

if grep -R -F -q -- '../okf' "${HOME}/.pi/agent/AGENTS.md" \
	"${HOME}/.pi/agent/skills"; then
	echo "BROKEN Pi runtime instructions refer to the wiki as ../okf"
	failures=$((failures + 1))
else
	echo "ok Pi runtime instructions use the workspace root"
fi

# Persistent Pi sessions. The stock path must remain a real directory and be
# the same bind-mounted directory as the host-backed state target.
if [ -z "${SBXAGENT_STATE_DIR:-}" ]; then
	echo "MISSING SBXAGENT_STATE_DIR"
	failures=$((failures + 1))
else
	session_link="${HOME}/.pi/agent/sessions"
	session_target="${SBXAGENT_STATE_DIR}/sessions"
	if [ -L "${session_link}" ]; then
		echo "BROKEN ${session_link} is a symlink"
		failures=$((failures + 1))
	elif [ ! -d "${session_link}" ] || [ ! -d "${session_target}" ]; then
		echo "MISSING persistent Pi session directories"
		failures=$((failures + 1))
	elif [ "$(stat -c '%d:%i' "${session_link}")" != \
		"$(stat -c '%d:%i' "${session_target}")" ]; then
		echo "BROKEN ${session_link} is not bind-mounted onto state"
		failures=$((failures + 1))
	else
		probe=".md2okf-sandbox-test-$$"
		if printf 'persistent\n' >"${session_link}/${probe}" &&
			grep -qx persistent "${session_target}/${probe}"; then
			echo "ok persistent Pi session bind"
		else
			echo "BROKEN write through Pi session path did not reach state"
			failures=$((failures + 1))
		fi
		rm -f "${session_link:?}/${probe}"
	fi
fi

# Context7 native Pi package (kits/md2okf/spec.yaml setup.install +
# settings.json packages). Presence only — no live Context7 API call.
if timeout 20 pi list 2>/dev/null | grep -q context7-pi; then
	echo "ok context7-pi (pi list)"
else
	echo "MISSING context7-pi (pi list)"
	failures=$((failures + 1))
fi

if grep -q 'npm:@upstash/context7-pi@0.1.2' "${HOME}/.pi/agent/settings.json"; then
	echo "ok settings.json context7-pi package"
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
	echo "ok ${c7_skill}"
else
	echo "MISSING context7-docs SKILL.md under ~/.pi/agent/npm"
	failures=$((failures + 1))
fi

# Credentials (kits/md2okf/spec.yaml). Automates the manual check in the README.
# Never print the value — case-match and report only a verdict.
case "${OPENROUTER_API_KEY-}" in
"")
	echo "MISSING OPENROUTER_API_KEY"
	failures=$((failures + 1))
	;;
proxy-managed)
	echo "ok OPENROUTER_API_KEY"
	;;
*)
	echo "BROKEN OPENROUTER_API_KEY (literal value in the VM, expected the proxy-managed sentinel)"
	failures=$((failures + 1))
	;;
esac

if [ "${failures}" -ne 0 ]; then
	echo "FAILED: ${failures} check(s)"
	exit 1
fi
echo "All toolchain checks passed."
