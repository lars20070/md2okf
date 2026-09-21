#!/usr/bin/env bash
set -euo pipefail

# Hold every subproject's version at the repo's VERSION.
#
# VERSION is the single source of truth for the whole repository: the md2okf
# driver reads it directly ([tool.hatch.version] in the root pyproject.toml),
# and every other project carries a literal copy that this script writes.
#
#     ./scripts/sync-versions.sh            # rewrite the literals from VERSION
#     ./scripts/sync-versions.sh --check    # report drift, change nothing
#
# `make lint` runs the --check form, so a forgotten bump fails there and in CI
# rather than shipping a wheel that disagrees with its own tag.
#
# The literals are not replaced by a dynamic version reading ../../VERSION,
# although hatchling accepts one: the four helper CLIs are built from a staged
# copy that is only pyproject.toml + src/ (md2okf.workbench.stage_clis, and the
# wheel's force-include), so a build-time read above the project root fails
# exactly where the agent runs the CLI.

usage() {
	echo "usage: $(basename "$0") [--check]" >&2
	exit 2
}

check_only=false
case "${1:-}" in
	--check) check_only=true ;;
	"") ;;
	*) usage ;;
esac
[[ "$#" -le 1 ]] || usage

cd "$(dirname "$0")/.."

version="$(grep -m1 -oE '[0-9]+\.[0-9]+\.[0-9]+' VERSION || true)"
if [[ -z "${version}" ]]; then
	echo "sync-versions: could not find X.Y.Z in VERSION" >&2
	exit 1
fi

# The version a project's own uv.lock records for itself, or "" when the lock
# is absent or the project is dynamic (uv omits the field for those, which is
# why the root md2okf lock needs nothing here).
locked_version() {
	local lock="$1" name="$2"
	[[ -f "${lock}" ]] || return 0
	awk -v want="name = \"${name}\"" '
		/^\[\[package\]\]/ { in_pkg = 0 }
		$0 == want { in_pkg = 1; next }
		in_pkg && /^version = / { gsub(/[":]|version = /, ""); print; exit }
	' "${lock}"
}

status=0
while IFS= read -r pyproject; do
	current="$(sed -n -E 's/^version = "(.*)"$/\1/p' "${pyproject}" | head -1)"

	# The root project is dynamic: hatchling reads VERSION itself, so there is
	# no literal to write. Anything else without one is a packaging mistake.
	if [[ -z "${current}" ]]; then
		if grep -qE '^dynamic = \[.*"version".*\]' "${pyproject}"; then
			continue
		fi
		echo "sync-versions: ${pyproject} declares no version and is not dynamic" >&2
		status=1
		continue
	fi

	project="$(dirname "${pyproject}")"
	name="$(sed -n -E 's/^name = "(.*)"$/\1/p' "${pyproject}" | head -1)"
	locked="$(locked_version "${project}/uv.lock" "${name}")"

	# A project's own lock records its version, so a bump leaves the lock stale
	# until uv rewrites it -- and `uv run` would then rewrite a tracked file in
	# the middle of `make test-clis`. Refresh it here instead.
	if [[ "${current}" == "${version}" ]] && [[ -z "${locked}" || "${locked}" == "${version}" ]]; then
		continue
	fi

	if [[ "${check_only}" == true ]]; then
		if [[ "${current}" != "${version}" ]]; then
			echo "sync-versions: ${pyproject} is ${current}, but VERSION is ${version}" >&2
		else
			echo "sync-versions: ${project}/uv.lock still records ${locked}" >&2
		fi
		status=1
		continue
	fi

	if [[ "${current}" != "${version}" ]]; then
		# Write-and-rename rather than `sed -i`, whose in-place flag takes a
		# suffix on BSD (macOS) but not on GNU. Same atomic swap the driver
		# uses, and the temporary file is a sibling, so the rename never
		# crosses a filesystem.
		sed -E "s/^version = \".*\"$/version = \"${version}\"/" \
			"${pyproject}" >"${pyproject}.tmp"
		mv "${pyproject}.tmp" "${pyproject}"
		echo "sync-versions: ${pyproject} ${current} -> ${version}"
	fi

	if [[ -n "${locked}" ]]; then
		uv lock --project "${project}" >/dev/null
		echo "sync-versions: ${project}/uv.lock refreshed"
	fi
done < <(git ls-files -- 'pyproject.toml' '*/pyproject.toml')

if [[ "${status}" -ne 0 ]] && [[ "${check_only}" == true ]]; then
	echo "sync-versions: run ./scripts/sync-versions.sh to fix" >&2
fi
exit "${status}"
