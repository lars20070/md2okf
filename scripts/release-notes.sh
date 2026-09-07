#!/usr/bin/env bash
set -euo pipefail

# Print one release's section of CHANGELOG.md, for use as GitHub Release notes.
#
#   usage: scripts/release-notes.sh VERSION      (for example: 0.1.0)
#
# A pure function — version in, notes out — so the release workflow can pipe it
# straight into `gh release create --notes-file -`, and so it is testable by
# hand without a tag or CI.
#
# It is called twice per release, deliberately. The `verify` job runs it with
# stdout discarded, purely so an empty section fails the run *before* the
# GitHub Release is created; the `github-release` job then runs it for the
# notes themselves. `make lint` cannot cover that: it checks only that the
# latest `## [X.Y.Z]` heading exists and agrees with VERSION, and a heading
# with an empty body passes that happily.

SELF="$(basename "$0")"

die() {
	echo "${SELF}: $*" >&2
	exit 1
}

[[ "$#" -eq 1 ]] || die "usage: ${SELF} VERSION    (for example: ${SELF} 0.1.0)"

version="$1"

repo="$(cd "$(dirname "$0")/.." && pwd -P)"
changelog="${repo}/CHANGELOG.md"

[[ "${version}" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]] ||
	die "'${version}' is not of the form X.Y.Z"
[[ -f "${changelog}" ]] || die "no CHANGELOG.md at ${changelog}"

# Escape the dots so 0.1.0 cannot also match 0x1x0. Built from the argument
# rather than interpolated raw, because awk takes an extended regexp here and an
# unescaped dot matches any character.
pattern="$(printf '%s' "${version}" | sed 's/\./\\./g')"

# The heading line is skipped by `next`, so the notes start at the first
# `### ` — which is what we want: GitHub already shows the tag as the title
# and dates the release, so repeating "## [0.1.0] - 2026-09-07" inside the
# body is noise.
notes="$(awk -v pat="^## \\\\[${pattern}\\\\]" \
	'$0 ~ pat {f=1; next} /^## \[/ {f=0} f' "${changelog}")"

# An empty body means a version was cut with nothing to say about it, which is
# worth failing a release over — and, called from `verify`, it fails before
# the Release is created rather than after.
#
# grep rather than `tr -d '[:space:]'`: BSD tr is multibyte-aware while GNU tr
# is byte-oriented, and changelog entries may carry non-ASCII punctuation. A
# bracket expression behaves the same on both.
printf '%s' "${notes}" | grep -q '[^[:space:]]' ||
	die "CHANGELOG.md has no content under '## [${version}]'"

printf '%s\n' "${notes}"
