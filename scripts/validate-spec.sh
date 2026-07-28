#!/usr/bin/env bash

# Validate the Pi Docker Sandbox Kit spec (pi/sandbox/spec.yaml) against the
# current Sandbox Kit schema. Runs identically locally and in CI.
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

echo "Validating ${repo_root}/pi/sandbox against the current Sandbox Kit schema..."
exec sbx kit validate "${repo_root}/pi/sandbox/"
