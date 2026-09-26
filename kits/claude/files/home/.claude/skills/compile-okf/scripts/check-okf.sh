#!/usr/bin/env bash
set -uo pipefail

# Check an OKF wiki bundle with okfctl (https://github.com/cwest/okfctl) and the
# frontmatter guard that ships beside this script.
#
# Usage: check-okf.sh [bundle]
#   bundle  wiki root to check (default: ., the workspace, which IS the wiki root)
#
# Every check runs even after one fails, so a single pass reports everything
# there is to fix. Exit codes:
#   0  clean
#   1  findings
#   2  usage or runtime error (bad path, or a required tool is missing)
#
# The guard reads the expected okf_version from SPEC.md, which it looks up as the
# SIBLING of the bundle: `./SPEC.md` for a bundle at `./okf` on the host, and the
# `../SPEC.md` mount when the workspace IS the bundle in the sandbox. A bundle
# copied somewhere else — `cp -r okf /tmp/okf-check`, say, to try a negative case
# — has no sibling spec and exits 2. That is the lookup working, not a broken
# gate: point SPEC_MD at the real file.
#
# What blocks and what only advises:
#   BLOCK   okfctl validate            OKF spec floor (a non-empty `type`)
#   BLOCK   frontmatter-guard.py       the wiki's own frontmatter and log conventions
#   BLOCK   okfctl lint                defect checks only — see BLOCKING_CHECKS below
#   BLOCK   okfctl analyze             internal links that resolve to nothing
#   BLOCK   okfctl index check         a stale, hand-edited or wrong index.md
#   advise  okfctl lint                missing-xref and coverage-gap, printed not enforced
#
# The lint split is deliberate. A defect has one correct fix; a judgment finding
# may not, and this gate runs unattended inside the compile loop.

# Lint checks that fail the gate. Everything else okfctl lint reports is printed
# as advice. Keep in sync with the curate-okf skill.
BLOCKING_CHECKS='["broken-link","orphan","type-hygiene","status-lifecycle","spec-version"]'

script_dir="$(CDPATH='' cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
guard="${script_dir}/frontmatter-guard.py"

bundle="${1:-.}"

for tool in okfctl jq python3; do
	if ! command -v "${tool}" >/dev/null 2>&1; then
		echo "Error: '${tool}' not found in PATH." >&2
		exit 2
	fi
done

if [[ ! -d "${bundle}" ]]; then
	echo "Error: wiki bundle not found: ${bundle}" >&2
	exit 2
fi

if [[ ! -f "${guard}" ]]; then
	echo "Error: frontmatter guard not found: ${guard}" >&2
	exit 2
fi

status=0

# 1. OKF spec floor. Deliberately without --strict: a floor violation fails
# regardless, while git drift stays advisory — okf/ is gitignored, so on the
# host every node looks drifted and --strict would be pure noise.
echo "== okfctl validate =="
if ! okfctl validate "${bundle}"; then
	status=1
fi

# 2. The conventions okfctl's floor deliberately does not encode.
echo
echo "== frontmatter guard =="
python3 "${guard}" "${bundle}"
guard_status=$?
if [[ "${guard_status}" -eq 2 ]]; then
	exit 2
elif [[ "${guard_status}" -ne 0 ]]; then
	status=1
fi

# 3. Curation health. One lint run feeds both the defect gate and the advice,
# so the two can never disagree about what was found.
echo
echo "== okfctl lint =="
lint_json="$(okfctl lint --json "${bundle}")"
lint_status=$?
if [[ "${lint_status}" -ne 0 ]] || [[ -z "${lint_json}" ]]; then
	echo "Error: could not read 'okfctl lint --json ${bundle}'." >&2
	exit 2
fi

if [[ "$(jq 'length' <<<"${lint_json}")" -eq 0 ]]; then
	echo "OK: no lint findings"
else
	jq -r --argjson blocking "${BLOCKING_CHECKS}" \
		'.[] | (if (.check | IN($blocking[])) then "BLOCK " else "advise " end) + .message' \
		<<<"${lint_json}"
	if ! jq -e --argjson blocking "${BLOCKING_CHECKS}" \
		'[.[] | select(.check | IN($blocking[]))] | length == 0' \
		<<<"${lint_json}" >/dev/null; then
		echo "okfctl lint: blocking finding(s) above" >&2
		status=1
	fi
fi

# 4. Links that resolve to nothing. Not the same question as lint's broken-link,
# which only fires when a node of the same basename exists somewhere else to
# suggest: that one asks "is this path wrong", this one asks "does this link go
# anywhere". A link to a page nobody has written is silent in lint.
#
# This walks concept nodes only — index.md and log.md are reserved files, not
# nodes, so a bad link in an index is invisible here. Step 5 is what covers
# those: an index that points at a missing page cannot be one `index build`
# would have written.
echo
echo "== dangling links =="
analyze_json="$(okfctl analyze --json "${bundle}")"
analyze_status=$?
if [[ "${analyze_status}" -ne 0 ]] || [[ -z "${analyze_json}" ]]; then
	echo "Error: could not read 'okfctl analyze --json ${bundle}'." >&2
	exit 2
fi

dangling="$(jq -r '.coverage_gaps.dangling_links[]? | "dangling-link: \(.from) -> \(.target)"' \
	<<<"${analyze_json}")"
jq_status=$?
if [[ "${jq_status}" -ne 0 ]]; then
	echo "Error: could not parse 'okfctl analyze --json ${bundle}'." >&2
	exit 2
fi

if [[ -n "${dangling}" ]]; then
	echo "${dangling}"
	status=1
else
	echo "OK: no dangling internal links"
fi

# 5. The reserved index.md files are generated, never hand-written. This fails
# closed on a stale index (a page added without a rebuild), on a hand-edited
# one, and on an index entry pointing at a page that does not exist. Regenerate
# with `okfctl index build`.
echo
echo "== index check =="
if ! okfctl index check "${bundle}"; then
	status=1
fi

echo
if [[ "${status}" -eq 0 ]]; then
	echo "OK: ${bundle} passes every check."
else
	echo "FAIL: ${bundle} has findings above." >&2
fi
exit "${status}"
