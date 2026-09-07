#!/usr/bin/env bash
set -euo pipefail

# Assert that a release tag is well formed and names the version this working
# tree actually declares.
#
# Called from the tag-triggered path in .github/workflows/release.yml.
#
# This deliberately does NOT re-check CHANGELOG.md. `make lint` already fails
# when VERSION and CHANGELOG.md's latest release heading disagree, and the
# release workflow runs `make lint` in the same job. Duplicating that here
# would be a second copy to keep in sync.

SELF="$(basename "$0")"

die() {
	echo "${SELF}: $*" >&2
	exit 1
}

# fd 3 carries machine-readable key=value output for $GITHUB_OUTPUT. CI opens
# it (3>>"$GITHUB_OUTPUT"); when it is closed, fall back to the real stdout so a
# local run still prints the values. Everything else is redirected to stderr, so
# no human-facing line can land in $GITHUB_OUTPUT and fail the step with
# "Invalid format".
if ! { : >&3; } 2>/dev/null; then
	exec 3>&1
fi
exec 1>&2

[[ "$#" -eq 1 ]] || die "usage: ${SELF} TAG    (for example: ${SELF} v1.2.3)"

tag="$1"

repo="$(cd "$(dirname "$0")/.." && pwd -P)"

[[ "${tag}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]] ||
	die "tag '${tag}' is not of the form vX.Y.Z"

[[ -f "${repo}/VERSION" ]] || die "no VERSION file at ${repo}/VERSION"

# Same extraction the Makefile's version-agreement check uses, so the two can
# never disagree about what VERSION says.
declared="$(grep -m1 -oE '[0-9]+\.[0-9]+\.[0-9]+' "${repo}/VERSION" || true)"
[[ -n "${declared}" ]] || die "could not find X.Y.Z in ${repo}/VERSION"

version="${tag#v}"
[[ "${version}" == "${declared}" ]] ||
	die "tag '${tag}' says ${version} but VERSION says ${declared}"

echo "${SELF}: ${tag} agrees with VERSION (${declared})"
printf 'version=%s\n' "${version}" >&3
