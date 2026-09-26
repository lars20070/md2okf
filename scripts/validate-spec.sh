#!/usr/bin/env bash

# Validate every Docker Sandbox Kit spec (kits/*/spec.yaml) against the current
# Sandbox Kit schema. Runs identically locally and in CI. Kits are discovered,
# not listed, so a kit being authored is checked from its first commit -- long
# before md2okf.agents registers it -- and a new one needs no edit here.
#
# `sbx kit validate` is a static schema check: no Docker, no `sbx login`, no
# network. Whatever schema the installed `sbx` bundles is the schema we check
# against, so keeping `sbx` current keeps the check current.

set -euo pipefail

# Resolve the repo root from this script's location so it works from any CWD.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

if ! command -v sbx >/dev/null 2>&1; then
	echo "Error: 'sbx' CLI not found in PATH." >&2
	echo "Please install it with: brew install docker/tap/sbx" >&2
	exit 1
fi

status=0
found=0
for spec in "${repo_root}"/kits/*/spec.yaml; do
	[[ -f "${spec}" ]] || continue
	kit="$(dirname "${spec}")"
	found=$((found + 1))
	echo "Validating ${kit} against the current Sandbox Kit schema..."
	# Keep going after a failure, so one run reports every invalid kit.
	sbx kit validate "${kit}/" || status=1
done

if [[ "${found}" -eq 0 ]]; then
	echo "Error: no kits/*/spec.yaml found under ${repo_root}." >&2
	exit 1
fi
exit "${status}"
