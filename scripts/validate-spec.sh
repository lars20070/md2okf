#!/usr/bin/env bash

# Validate every Docker Sandbox Kit spec (kits/*/spec.yaml) against the current
# Sandbox Kit schema. Runs identically locally and in CI. Kits are discovered,
# not listed, so a kit being authored is checked from its first commit -- long
# before md2okf.agents registers it -- and a new one needs no edit here.
#
# `sbx kit validate` is a static schema check: no Docker, no `sbx login`, no
# network. It uses the installed CLI's schema, after checking that CLI against
# the repository-wide minimum in SBX_VERSION.

set -euo pipefail

# Resolve the repo root from this script's location so it works from any CWD.
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd "${script_dir}/.." && pwd)"

if ! command -v sbx >/dev/null 2>&1; then
	echo "Error: 'sbx' CLI not found in PATH." >&2
	echo "Please install it with: brew install docker/tap/sbx" >&2
	exit 1
fi

required="$(<"${repo_root}/SBX_VERSION")"
if [[ ! "${required}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
	echo "Error: SBX_VERSION must contain exactly one X.Y.Z version." >&2
	exit 1
fi

installed="$(sbx version | grep -m1 -oE '[0-9]+\.[0-9]+\.[0-9]+')" || {
	echo "Error: could not read a version from 'sbx version'." >&2
	exit 1
}
if [[ "$(printf '%s\n' "${required}" "${installed}" | sort -V | head -n1)" != "${required}" ]]; then
	echo "Error: sbx ${required} or newer is required; found ${installed}." >&2
	echo "Please upgrade sbx with Homebrew or APT." >&2
	exit 1
fi

status=0
found=0
for spec in "${repo_root}"/kits/*/spec.yaml; do
	[[ -f "${spec}" ]] || continue
	kit="$(dirname "${spec}")"
	found=$((found + 1))
	echo "Validating ${kit} with sbx ${installed} (minimum ${required})..."
	# Keep going after a failure, so one run reports every invalid kit.
	sbx kit validate "${kit}/" || status=1
done

if [[ "${found}" -eq 0 ]]; then
	echo "Error: no kits/*/spec.yaml found under ${repo_root}." >&2
	exit 1
fi
exit "${status}"
