#!/usr/bin/env bash
set -euo pipefail

# Lint an OKF wiki bundle with okf-lint (https://github.com/thisismydesign/okf-lint).
#
# Usage: lint-okf.sh [bundle]
#   bundle  wiki root to lint (default: ./okf, relative to the workspace)
#
# Rule severities come from <bundle>/.okflintrc.json — never edit that file.
# okf-lint's output and exit code are passed through unchanged:
#   0  clean
#   1  errors, or the warning threshold exceeded
#   2  usage or runtime error (bad path, or okf-lint not installed)

bundle="${1:-./okf}"

if ! command -v okf-lint >/dev/null 2>&1; then
	echo "Error: 'okf-lint' not found in PATH." >&2
	exit 2
fi

if [[ ! -d "${bundle}" ]]; then
	echo "Error: wiki bundle not found: ${bundle}" >&2
	exit 2
fi

exec okf-lint "${bundle}"
