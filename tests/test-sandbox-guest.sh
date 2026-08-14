#!/bin/sh

# Runs INSIDE the md2okf sandbox, launched by tests/test-sandbox.sh through
# `sbx exec ... sh -lc`. Run on the host it would happily report on your laptop's
# toolchain instead, which proves nothing.
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

# The kit COPIES files in, so a lost exec bit is a real failure mode.
check_exec() {
	if [ -x "$1" ]; then
		echo "ok $1"
	else
		echo "MISSING $1"
		failures=$((failures + 1))
	fi
}

# The tool list must match BOTH lists in pi/spec.yaml: the setup.install steps
# AND the agentInstructions prose at 27-33. That prose is the promise being
# tested here, so a tool installed but not promised — or promised but not
# installed — is itself the bug.

# apt (pi/spec.yaml:77-87). `rg` is the command; `ripgrep` is the package.
check curl
check jq
check python3
check rg
check shellcheck
check tree

# npm through the retry wrapper (pi/spec.yaml:91-118).
check pi
check okf-lint

# npm, Markdown and spelling linters (pi/spec.yaml:120).
check markdownlint-cli2
check cspell

# uv (pi/spec.yaml:124-129).
check ruff
check yamllint

# Config delivery: pi/files/home/.pi/agent/ is copied at kit build time, not
# mounted, so a layout change can leave Pi with no instructions and no skill.
check_file "$HOME/.pi/agent/AGENTS.md"
check_file "$HOME/.pi/agent/settings.json"
check_file "$HOME/.pi/agent/models.json"
check_file "$HOME/.pi/agent/skills/compile-wiki/SKILL.md"
check_exec "$HOME/.pi/agent/skills/compile-wiki/scripts/lint-okf.sh"

# Credentials (pi/spec.yaml:62-70). Automates the manual check in the README.
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

if [ "$failures" -ne 0 ]; then
	echo "FAILED: $failures check(s)"
	exit 1
fi
echo "All toolchain checks passed."
