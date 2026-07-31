#!/usr/bin/env bash
set -euo pipefail

# Check that the compiled OKF wiki is USABLE, not merely well-formed.
#
# Usage: test-house-style.sh [cases.json]
#
# One Pi run per case, each given a badly written paragraph and nothing but the
# wiki: the `pi-consume` service mounts okf/ read-only and does not mount md/ at
# all, so the agent cannot consult the source documents. Each reply must end in
# a json block naming the changes and the page each came from; grade.py then
# checks the edit landed, the citation resolves, and the cited page really says
# what was claimed.
#
# Provider and model are passed explicitly rather than read from settings.json,
# so a test run states which model it exercised and leaves repo config alone.
# Override with PI_PROVIDER / PI_MODEL.
#
# Exit: 0 all cases passed, 1 one or more failed, 2 could not run.

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${repo_root}"

cases_file="${1:-tests/house-style/cases.json}"
compose_file="pi/container/compose.yaml"
outdir="tests/house-style/out"
provider="${PI_PROVIDER:-litellm}"
model="${PI_MODEL:-gemini-3.1-pro-preview}"

fail_infra() {
	echo "error: $1" >&2
	exit 2
}

command -v docker >/dev/null 2>&1 || fail_infra "Docker CLI not found."
docker info >/dev/null 2>&1 || fail_infra "Docker does not appear to be running."
[[ -f "${cases_file}" ]] || fail_infra "Cases file not found: ${cases_file}"

# The wiki is the artefact under test; without it the run is meaningless rather
# than failing.
compiled_pages="$(find okf -name '*.md' ! -name '.okflintrc.json' 2>/dev/null | wc -l | tr -d ' ')"
[[ "${compiled_pages}" -gt 0 ]] || fail_infra "No compiled wiki under okf/ — run a compile first."

# Only the selected provider's key is needed. Checking here turns a missing
# credential into a clear message rather than an unauthenticated request that
# looks like a content failure.
case "${provider}" in
litellm) [[ -n "${LITELLM_API_KEY:-}" ]] || fail_infra "LITELLM_API_KEY is not set (provider=litellm)." ;;
openrouter) [[ -n "${OPENROUTER_API_KEY:-}" ]] || fail_infra "OPENROUTER_API_KEY is not set (provider=openrouter)." ;;
esac

mkdir -p "${outdir}"
rm -f "${outdir}"/*.txt

# Compose interpolates every service in the file, not just the one being run, so
# the sibling `pi` service's OPENROUTER_API_KEY fail-fast would abort a
# consumption run that never touches OpenRouter. Supply a placeholder purely to
# satisfy interpolation; pi-consume itself takes the variable as optional, and
# nothing here sends it anywhere.
export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-unused-by-consumption-test}"

docker compose -f "${compose_file}" build pi-consume >/dev/null

ids="$(python3 -c "
import json,sys
for c in json.load(open('${cases_file}'))['cases']:
    print(c['id'])
")"

echo "Consumption test: ${compiled_pages} wiki pages, provider=${provider}, model=${model}"
echo

for id in ${ids}; do
	paragraph="$(python3 -c "
import json
for c in json.load(open('${cases_file}'))['cases']:
    if c['id'] == '${id}':
        print(c['input'])
        break
")"
	echo "  running ${id}"
	# </dev/null is required, not tidiness: Pi's print mode reads piped stdin
	# and would block forever on a pipe that never reaches EOF.
	docker compose -f "${compose_file}" run --rm -T pi-consume \
		-xt bash \
		--provider "${provider}" \
		--model "${model}" \
		-p "Load the apply-house-style skill: read /home/node/.pi/agent/skills/apply-house-style/SKILL.md, then follow it to apply house style to this paragraph: ${paragraph}" \
		</dev/null >"${outdir}/${id}.txt" 2>&1 || true
done

echo
python3 tests/house-style/grade.py okf "${cases_file}" "${outdir}"
