#!/bin/sh

# Pi's half of the in-sandbox checks: definitions only. tests/test-sandbox.sh
# pipes this file and then tests/test-sandbox-guest-common.sh into the
# md2okf-pi sandbox as one script; the common file documents the interface and
# runs everything, including agent_checks below.
#
# shellcheck disable=SC2034 # every AGENT_* variable is read by the common file

AGENT_NAME=pi
AGENT_BINARY=pi
AGENT_TRACE_DIR="${HOME}/.pi/agent/sessions"
AGENT_INSTRUCTIONS="${HOME}/.pi/agent/AGENTS.md"
AGENT_RUNTIME_PATHS="${HOME}/.pi/agent/AGENTS.md ${HOME}/.pi/agent/skills"

# Exact pins in kits/pi/spec.yaml (Pi through the image digest).
EXPECTED_PI_VERSION=1.4.0
EXPECTED_GITHUB_MCP_VERSION=1.12.2
EXPECTED_CONTEXT7_PI_VERSION=0.1.3

# Set by test-sandbox.sh from the host's REQUIRE_GITHUB. 1 turns "no GitHub
# secret bound" from a skip into a failure, which is how a release certifies
# the authenticated GitHub MCP path.
REQUIRE_GITHUB="${REQUIRE_GITHUB:-0}"

# `jq -e FILTER FILE`, reported as one check.
check_jq() {
	label=$1
	filter=$2
	file=$3
	if jq -e "${filter}" "${file}" >/dev/null 2>&1; then
		ok "${label}"
	else
		broken "${label} (${file})"
	fi
}

# The version output must name the pin as a whole word.
check_version() {
	tool=$1
	expected=$2
	shift 2
	if output=$("$@" 2>&1 </dev/null) &&
		printf '%s\n' "${output}" | grep -Fqw "${expected}"; then
		ok "${tool} is ${expected}"
	else
		broken "${tool} is not ${expected}: ${output}"
	fi
}

agent_checks() {
	# Config delivery: kits/pi/files/home/.pi/agent/ is copied at kit build
	# time, not mounted, so a layout change can leave Pi with no instructions
	# and no skill.
	check_file "${HOME}/.pi/agent/settings.json"
	check_file "${HOME}/.pi/agent/models.json"
	check_file "${HOME}/.pi/agent/skills/compile-okf/SKILL.md"
	check_exec "${HOME}/.pi/agent/skills/compile-okf/scripts/check-okf.sh"
	check_file "${HOME}/.pi/agent/skills/compile-okf/scripts/frontmatter-guard.py"
	check_file "${HOME}/.pi/agent/skills/inspect-md/SKILL.md"
	check_file "${HOME}/.pi/agent/skills/inspect-okf/SKILL.md"
	check_file "${HOME}/.pi/agent/skills/size-okf/SKILL.md"
	check_file "${HOME}/.pi/agent/skills/merkle-okf/SKILL.md"
	check_file "${HOME}/.pi/agent/skills/curate-okf/SKILL.md"

	# Context7 native Pi package (kits/pi/spec.yaml setup.install +
	# settings.json packages). Presence only — no live Context7 API call.
	if timeout 20 pi list 2>/dev/null | grep -q context7-pi; then
		ok "context7-pi (pi list)"
	else
		echo "MISSING context7-pi (pi list)"
		failures=$((failures + 1))
	fi

	c7_skill=$(
		find "${HOME}/.pi/agent/npm" \
			-path '*context7-pi*/skills/context7-docs/SKILL.md' \
			2>/dev/null | head -n 1
	)
	if [ -n "${c7_skill}" ] && [ -f "${c7_skill}" ]; then
		ok "${c7_skill}"
	else
		echo "MISSING context7-docs SKILL.md under ~/.pi/agent/npm"
		failures=$((failures + 1))
	fi

	# Credentials (kits/pi/spec.yaml). Automates the manual check in the
	# README. Never print the value — case-match and report only a verdict.
	case "${OPENROUTER_API_KEY-}" in
	"")
		echo "MISSING OPENROUTER_API_KEY"
		failures=$((failures + 1))
		;;
	proxy-managed) ok "OPENROUTER_API_KEY" ;;
	*) broken "OPENROUTER_API_KEY (literal value in the VM, expected the proxy-managed sentinel)" ;;
	esac

	pi_provenance_checks
	pi_config_checks
	pi_github_checks
}

# Pi comes prebuilt in the kit's digest-pinned image, not from a kit step: one
# Pi, the image's, at the pinned version.
pi_provenance_checks() {
	check_version pi "${EXPECTED_PI_VERSION}" pi --version
	check_version github-mcp-server "${EXPECTED_GITHUB_MCP_VERSION}" github-mcp-server --version

	pi_package_dir=$(readlink -f "$(npm root -g)/@earendil-works/pi-coding-agent")
	pi_real=$(readlink -f "$(command -v pi)")
	case "${pi_real}" in
	"${pi_package_dir}"/*) ok "pi on PATH is the image's npm install" ;;
	*) broken "pi on PATH (${pi_real}) is not the image's install in ${pi_package_dir}" ;;
	esac
	if [ "$(readlink -f /usr/local/bin/pi)" = "${pi_real}" ]; then
		ok "/usr/local/bin/pi resolves to the same install"
	else
		broken "/usr/local/bin/pi does not resolve to ${pi_real}"
	fi

	if [ -e /opt/pi ]; then
		broken "/opt/pi exists: a second Pi besides the image's"
	else
		ok "no second Pi under /opt/pi"
	fi
	# Context7 lists Pi as a peer dependency; a nested copy would be a second,
	# unpinned Pi.
	nested_pi=$(
		find "${HOME}/.pi/agent/npm" -path '*/@earendil-works/pi-coding-agent' \
			-print 2>/dev/null | head -n 1
	)
	if [ -n "${nested_pi}" ]; then
		broken "a Pi package pulled in a second Pi: ${nested_pi}"
	else
		ok "Pi packages pulled in no second Pi"
	fi

	# Pi downloads an unpinned fd at first launch unless `fd` or `fdfind` is
	# on PATH; the image ships both (the common checks cover fdfind).
	check fd
	check gh
}

# shellcheck disable=SC2016 # $schema and ${GITHUB_TOKEN} are jq/JSON literals
pi_config_checks() {
	settings="${HOME}/.pi/agent/settings.json"
	models="${HOME}/.pi/agent/models.json"
	mcp="${HOME}/.pi/agent/mcp.json"
	check_file "${mcp}"

	check_jq "settings.json declares Pi's \$schema" \
		'."$schema" == "https://pi.dev/schemas/settings.schema.json"' "${settings}"
	# `pi install` merges this into the shipped settings.json at build time, so
	# its presence proves that step ran and its result survived.
	check_jq "settings.json pins context7-pi ${EXPECTED_CONTEXT7_PI_VERSION}" \
		".packages | index(\"npm:@upstash/context7-pi@${EXPECTED_CONTEXT7_PI_VERSION}\") != null" \
		"${settings}"
	check_jq "settings.json enables tool_search for the deferred GitHub tools" \
		'.defaultTools | index("+tool_search") != null' "${settings}"
	check_jq "settings.json defaults to openrouter / deepseek/deepseek-v4-pro" \
		'.defaultProvider == "openrouter" and .defaultModel == "deepseek/deepseek-v4-pro"' \
		"${settings}"
	check_jq "settings.json keeps cacheWarming streaming" \
		'.cacheWarming == "streaming"' "${settings}"

	check_jq "models.json declares Pi's \$schema" \
		'."$schema" == "https://pi.dev/schemas/models.schema.json"' "${models}"
	check_jq "models.json keeps the four DeepInfra routing pins" \
		'.providers.openrouter.modelOverrides | keys
			== ["deepseek/deepseek-v4-pro", "moonshotai/kimi-k3",
				"qwen/qwen3.6-35b-a3b", "qwen/qwen3.8-2.4t-a95b"]' "${models}"
	check_jq "models.json keeps the litellm provider" \
		'.providers.litellm.models | length > 0' "${models}"

	# Exact equality, so a promoted exposure, a different token source or
	# codemode switched back on fails here.
	check_jq "mcp.json is the kit's deferred stdio github entry, codemode off" \
		'. == {
			"autoEnableCodemode": false,
			"mcpServers": {"github": {
				"command": "github-mcp-server",
				"args": ["stdio"],
				"env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"},
				"exposure": "deferred"
			}}
		}' "${mcp}"
}

# The token exports and the MCP path, through md2okf-agent: the driver starts
# every Pi process that way, under an `sbx exec` that skips the entrypoint, so
# the shim -- not this login shell -- is what must export them.
pi_github_checks() {
	# Never print a value: the inner shell case-matches and names only the
	# first variable that is not the sentinel.
	# shellcheck disable=SC2016 # expanded by the inner shell, not this one
	verdict=$(
		md2okf-agent sh -c '
			for name in GH_TOKEN GITHUB_TOKEN GITHUB_PERSONAL_ACCESS_TOKEN; do
				eval "value=\${${name}-}"
				case "${value}" in
				proxy-managed) ;;
				*) echo "${name}"; exit 0 ;;
				esac
			done
			echo ok' </dev/null 2>&1
	)
	if [ "${verdict}" = ok ]; then
		ok "md2okf-agent exports GH_TOKEN, GITHUB_TOKEN and GITHUB_PERSONAL_ACCESS_TOKEN as the sentinel"
	else
		broken "md2okf-agent: ${verdict} is not the proxy-managed sentinel"
	fi

	# GH_TOKEN is always the sentinel in a local sandbox; this is what says
	# whether a host secret stands behind it. Binding one later does not reach
	# an existing sandbox.
	if [ "${SBX_CRED_GITHUB_MODE:-none}" = none ]; then
		if [ "${REQUIRE_GITHUB}" = 1 ]; then
			broken "no GitHub secret was bound when this sandbox was created (REQUIRE_GITHUB=1). On the host: gh auth token | sbx secret set github (or a least-privilege token, see kits/pi/README.md), then sbx rm --force md2okf-pi"
		else
			echo "ok skipped: no GitHub secret bound (REQUIRE_GITHUB=1 makes this a failure)"
		fi
		return
	fi

	if gh auth status >/dev/null 2>&1 </dev/null; then
		ok "gh is authenticated through the proxy"
	else
		broken "gh auth status failed with a GitHub secret bound"
	fi

	# Exits 1 when an entry is invalid or an enabled server is not connected.
	mcp_list=$(md2okf-agent pi mcp list --json </dev/null 2>/dev/null)
	if printf '%s\n' "${mcp_list}" | jq -e \
		'any(.servers[]; .name == "github" and .state == "connected" and (.tools | length) > 0)' \
		>/dev/null 2>&1; then
		ok "pi mcp list shows github connected, with tools"
	else
		broken "pi mcp list does not show github connected with tools"
	fi

	# Listing tools needs no credential. One read-only call proves the proxy
	# authenticates the server's requests, through the shim's exports. The
	# heredoc is the client's stdin, so it cannot swallow the rest of this
	# script, which `sh -s` is reading from stdin too.
	if login=$(md2okf-agent python3 - <<'PY'
import json
import queue
import subprocess
import sys
import threading
import time

deadline = time.monotonic() + 60
server = subprocess.Popen(
    ["github-mcp-server", "stdio"],
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
)
lines = queue.Queue()
stderr = []


def pump(stream, sink):
    for line in stream:
        sink(line)
    if stream is server.stdout:
        lines.put(None)


threading.Thread(target=pump, args=(server.stdout, lines.put), daemon=True).start()
threading.Thread(target=pump, args=(server.stderr, stderr.append), daemon=True).start()


def fail(message):
    server.kill()
    time.sleep(0.2)
    print(message, file=sys.stderr)
    tail = "".join(stderr)[-4000:]
    if tail:
        print("github-mcp-server stderr:\n" + tail, file=sys.stderr)
    sys.exit(1)


def send(message):
    server.stdin.write(json.dumps(message) + "\n")
    server.stdin.flush()


def response(request_id):
    while True:
        left = deadline - time.monotonic()
        if left <= 0:
            fail(f"no response to request {request_id} within 60 s")
        try:
            line = lines.get(timeout=left)
        except queue.Empty:
            continue
        if line is None:
            fail(f"github-mcp-server exited before answering request {request_id}")
        try:
            message = json.loads(line)
        except ValueError:
            continue
        if isinstance(message, dict) and message.get("id") == request_id:
            if "error" in message:
                fail(f"request {request_id} failed: {message['error']}")
            return message.get("result") or {}


send(
    {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "md2okf-test-sandbox", "version": "1"},
        },
    }
)
response(1)
send({"jsonrpc": "2.0", "method": "notifications/initialized"})
send({"jsonrpc": "2.0", "id": 2, "method": "tools/call", "params": {"name": "get_me", "arguments": {}}})
result = response(2)
if result.get("isError"):
    fail(f"get_me returned an error: {json.dumps(result)[:2000]}")
try:
    me = json.loads(result["content"][0]["text"])
except (KeyError, IndexError, TypeError, ValueError):
    fail(f"get_me returned no JSON text: {json.dumps(result)[:2000]}")
login = me.get("login") if isinstance(me, dict) else None
if not isinstance(login, str) or not login:
    fail(f"get_me returned no login: {json.dumps(me)[:2000]}")
server.stdin.close()
server.terminate()
print(login)
PY
	); then
		ok "github-mcp-server reaches GitHub authenticated, as ${login}"
	else
		broken "github-mcp-server could not make an authenticated GitHub request (see above)"
	fi
}
