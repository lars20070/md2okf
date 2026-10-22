# Upgrade md2okf's Pi from 0.86.1 to 1.4.0

## Context

md2okf pins Pi `0.86.1` (`kits/pi/spec.yaml`). The current release is `1.4.0`
(2026-10-21). In sbxagent 0.4.12 (PR #18), the same kind of upgrade (0.84.4 → 1.3.0)
set the pattern to follow:

- Pi comes prebuilt in Docker's `docker.io/sbx/pi-image`, pinned by digest, not from `npm install -g`.
- `$schema` is declared in `settings.json` and `models.json`.
- A GitHub MCP server is added with deferred tools, `+tool_search` and `autoEnableCodemode: false`.
- Context7 Pi moves to `0.1.3`.
- The trace skill is updated.
- Fullscreen TUI is documented, not overridden.

You decided:

- Add GitHub MCP like sbxagent.
- Port the trace skill and retarget its paths to md2okf.
- Release as **0.3.2**.
- Do the sbx 0.49.1 bump as a separate change.

### What Pi 0.87.0 → 1.4.0 changes for md2okf (I read the coding-agent CHANGELOG at v1.4.0)

- **`--mode json` wire format is unchanged** for what `protocols/pi.py` reads: `tool_execution_start{toolName,args}` and assistant `message_end.content`. 1.1.0 only adds `aborted` to `agent_settled`. The session format is still version 3. No parser change is expected; a real 1.4.0 fixture (§4) will confirm it.
- **Built-in MCP, codemode and tool_search exist from 0.99.0 on.** Codemode and tool_search are registered inactive. `defaultTools` still defaults to `read, bash, edit, write`.
- **The npm shrinkwrap is gone from 1.0.1**, so npm no longer pins Pi's dependencies. That is why sbxagent moved to the image.
- **Fullscreen TUI is the default from 1.0.0** (`tuiMode: "regular"` turns it off). This only affects `md2okf --agent`.
- **1.2.0 per-key OpenRouter model lists** (`/models/user`). These can change the figures `pi --list-models` reports, so the README's "1M context / 384K max output" claim must be checked again.
- **1.4.0:** compaction and branch summaries use the model's output limit. The `grep` tool runs `rg --no-config`. The `mcp.json` BOM fix also lands. Nothing here breaks this kit.
- **Breaking changes that don't apply here:**
  - Extension and SDK API changes (`finishTurn`, `TurnEndEvent`, `before_agent_start` union, `TranscriptContext`).
  - The Azure provider rename and the Kimi `/v1` base URL. The kit uses neither provider.
  - Theme schema validation. The kit ships no theme.
  - `-p` exiting 1 on truncation. The compile runs `--mode json`, not `-p`.
- The `openRouterRouting` compat and `modelOverrides` behave the same in 1.4.0 (`models-configuration.md`).

### GitHub authority policy

Binding the GitHub secret authorizes **every process in the `md2okf-pi` sandbox, compile turns included**. The sbx proxy injects the credential at the network level for `api.github.com` and `github.com`, and every compile turn has `bash`. So a source document that steers a compile turn could make authenticated GitHub requests with `curl` or `gh`. `--no-mcp` only keeps the `mcp__github__*` *tools* out of a compile. It is not a credential boundary, and neither is unsetting the token aliases in the wrapper.

The plan accepts this, consistent with "add GitHub MCP like sbxagent". It says so plainly in the docs, the agent instructions and the CHANGELOG Security entry, and it recommends a least-privilege token: a fine-grained token, read-only, scoped to the repositories you need. Leaving the secret unbound keeps GitHub unauthenticated, as it is today.

(The alternative is real isolation: a separate sandbox for interactive use. That would need a second sandbox per agent and is out of scope unless you want it.)

## Changes

### 1. `kits/pi/spec.yaml`

- **Image:** `docker/sandbox-templates:shell-docker` → `docker.io/sbx/pi-image@sha256:<index digest>`. Port sbxagent's comment block explaining why (not `extends:`, pinned by digest, freezes the template). The current `latest` index is `sha256:134b48cf…a1d2d5`, built 2026-10-22 05:11 UTC, after 1.4.0 was released. **Before pinning it**, confirm that both platforms report `@earendil-works/pi-coding-agent 1.4.0`, using sbxagent's `docker create` + `docker cp package.json` check (`docs/toolchain.md` there). The image sets `NPM_CONFIG_PREFIX=/usr/local/share/npm-global`, owned by `agent`, so the user-1000 `npm install --global` steps keep working.
- **Setup:**
  - Delete the Pi `npm_install_retry` install.
  - Keep the `npm config set proxy/https-proxy` lines as their own step ("Configure npm proxy").
  - Drop `fd-find` from apt, with sbxagent's comment: the image ships `fd` and `fdfind`.
  - Add the `github-mcp-server` v1.12.2 install step with the same SHA-256 digests as sbxagent (amd64 `95843162…290e`, arm64 `2b30f9fc…17a5`). Keep it in this kit's style (`uname -m`, `$HOME/.local/bin` or `/usr/local/bin`, matching mq/okfctl).
  - `CONTEXT7_PI_VERSION=0.1.3`.
- **Credentials:** add the `github` service (`GH_TOKEN`, proxyManaged; bearer on `api.github.com`, `x-access-token` basic auth on `github.com`), as in sbxagent. Binding it is **optional**. `GH_TOKEN` is always the `proxy-managed` placeholder in a local sandbox, and `SBX_CRED_GITHUB_MODE=none` is what marks the unbound case. The policy above applies.
- **Allowlist:**
  - Add `api.github.com:443`. `github.com` and the release CDN hosts are already listed.
  - Update the npm comment, since Pi no longer comes from npm.
  - Leave out the gist hosts: `/share` is not needed here.
- **Token export:** set `GITHUB_TOKEN`/`GITHUB_PERSONAL_ACCESS_TOKEN` from `GH_TOKEN` in **both** places:
  - the entrypoint `sh -c`, for `sbx run`;
  - the Pi-only `md2okf-agent` shim in `files:`. Every driver process goes through `sbx exec`, which skips the entrypoint (AGENTS.md: per-process setup goes in the wrapper). The export goes in the per-kit shim, not the shared `md2okf-agent.sh`, which `test_kits.py` requires to be byte-identical across kits.
- **agentInstructions:**
  - `fdfind` → `fd` (also `fdfind`).
  - Add a GitHub bullet: the deferred `mcp__github__*` tools are loaded through `tool_search` in interactive sessions; a compile runs with `--no-mcp`. Do **not** claim that GitHub access itself is interactive-only: `gh` and `git` over HTTPS carry the same credential whenever it is bound.

### 2. Pi config, `kits/pi/files/home/.pi/agent/`

- `settings.json`:
  - Add `"$schema": "https://pi.dev/schemas/settings.schema.json"`.
  - Add `"defaultTools": ["+tool_search"]`. This mirrors sbxagent on purpose, even though Pi 1.4.0 also turns tool_search on by itself for a deferred server.
  - Context7 package `@0.1.3`.
  - Keep `cacheWarming: "streaming"`.
  - Leave `tuiMode` unset, following sbxagent.
- `models.json`: add `"$schema": "https://pi.dev/schemas/models.schema.json"`.
- New `mcp.json`, identical to sbxagent's: `autoEnableCodemode: false`, plus a `github` stdio server with `GITHUB_PERSONAL_ACCESS_TOKEN: "${GITHUB_TOKEN}"` and `exposure: "deferred"`.

### 3. Driver: compiles carry no MCP tools, like Claude and Codex

`src/md2okf/agents.py`: `PI.compile_args` becomes `[WRAPPER, "pi", "--mode", "json", "--no-mcp", "--tools", "-tool_search", prompt]`.

- `--no-mcp` (Pi 1.0.4) is the counterpart of Claude's `--strict-mcp-config` and Codex's gateway override.
- `-tool_search` (1.1.0 `+/-` syntax) keeps the compile tool set exactly what it is on 0.86.1.
- The comment says what this does and does not do: it removes MCP tools, not GitHub credential access (see the policy above).
- `interactive_args` stays as is, so `md2okf --agent` gets GitHub MCP.
- Update `tests/test_agents.py` for the new argv.

`_pi_check_credentials` is unchanged: GitHub is optional, and a compile doesn't need it.

### 4. Tests

**Guest checks.** `tests/test-sandbox-guest-pi.sh` gets sbxagent PR #18's provenance and config checks, adapted:

- exact versions: `pi --version` is `1.4.0`, and `github-mcp-server --version` is `1.12.2`;
- the image owns Pi: `pi` resolves (`readlink -f`) into `$(npm root -g)/@earendil-works/pi-coding-agent`, and `/usr/local/bin/pi` points at the same file;
- there is no second Pi: `/opt/pi` is absent, and no nested `@earendil-works/pi-coding-agent` exists under `~/.pi/agent/npm` (Context7 lists Pi as a peer dependency);
- `fd` and `fdfind` are on PATH;
- `settings.json` (with `jq -e`) has the settings `$schema`, `npm:@upstash/context7-pi@0.1.3` in `packages`, `+tool_search` in `defaultTools`, `defaultProvider`/`defaultModel` unchanged, and `cacheWarming == "streaming"`;
- `models.json` has the models `$schema`, and all four `openrouter.modelOverrides` keys plus the `litellm` provider are still present;
- `mcp.json` equals the intended config exactly (`autoEnableCodemode == false`; `github` with `command`, `args: ["stdio"]`, `env`, `exposure: "deferred"`).

**Credential, wrapper and MCP path.** These run through the supported invocation path (`md2okf-agent`), not the bare guest shell, which `sbx exec` starts without the shim:

- Always: `md2okf-agent sh -c '…'` checks that `GH_TOKEN`, `GITHUB_TOKEN` and `GITHUB_PERSONAL_ACCESS_TOKEN` are all the `proxy-managed` sentinel, case-matched and never printed. This tests the shim's export.
- When `SBX_CRED_GITHUB_MODE` is not `none`:
  - `gh auth status` succeeds;
  - `md2okf-agent pi mcp list --json` shows `github` connected with tools;
  - one authenticated, read-only MCP `get_me` call, adapted from PR #18's Python stdio client, returns a login.
- When it is `none`, the routine run prints a clear "skipped: no GitHub secret bound" line. Running with `REQUIRE_GITHUB=1` turns that skip into a failure with the setup remedy (`gh auth token | sbx secret set github`, then `sbx rm --force md2okf-pi`). That is how a release certifies the authenticated integration.

**Protocol fixture.**

- Capture one real, sanitized `pi --mode json` run from Pi 1.4.0 into `tests/fixtures/protocols/pi/`. It needs at least a `tool_execution_start`, an assistant `message_end` and the terminal `agent_end`/`agent_settled`.
- Add a `README.md` stating the capture provenance, following the claude and codex fixture READMEs.
- Add tests in `tests/test_protocol_pi.py` that run the fixture through `process()`, `translate()` and `is_tool_call()`.

### 5. Trace skill: `.claude/skills/read-pi-session-traces/`

- Port sbxagent main's `SKILL.md`, `references/schema.md`, `scripts/pi_trace_commands.py`, `scripts/pi_trace_projection.py` and `tests/pi_trace_test.py`. The local copy is byte-identical to sbxagent's pre-PR base, so this is a clean overwrite.
- Then retarget:
  - `1.3.0` → `1.4.0`. The format is still v3, and 1.4.0 adds no carriers.
  - Rename `Pi130CarrierTests` to the version-independent `ModernCarrierTests`.
  - `sbxpi` → md2okf's `md2okf-pi`.
  - The paths → `${XDG_STATE_HOME:-~/.local/state}/md2okf/pi/sessions` and `kits/pi/spec.yaml`.
- Afterwards, `rg -n '130|1\.3\.0|sbxpi|sbxagent'` across the skill must find nothing left over.
- Run its pytest suite.

### 6. Docs

- `kits/pi/README.md`:
  - Pi now comes from the image, with sbxagent's digest-bump procedure for checking the version on both platforms.
  - A "GitHub MCP server" section:
    - optional setup via stdin, `gh auth token | sbx secret set github`, before creation (never `-t "$(…)"`, which puts the token in process arguments);
    - recommend a least-privilege fine-grained token;
    - state the authority policy: it covers compile turns too;
    - deferred tools; MCP tools in `md2okf --agent` only;
    - diagnose with `sbx exec md2okf-pi -- md2okf-agent pi mcp list`, or `/mcp` inside `md2okf --agent`, never a bare `pi mcp list`.
  - The fullscreen `tuiMode` note.
  - Recheck the deepseek catalogue figures (per-key OpenRouter lists).
- `docs/configuration.md` (Pi section): the optional GitHub secret (stdin form) and the authority note.
- `AGENTS.md` repo map: add `mcp.json` to the Pi config list.
- `.cspell.json`: add new words.

### 7. Release

- `VERSION` → `0.3.2`, then `./scripts/sync-versions.sh`. This also rewrites `extras/web2md` and the other subprojects and their lockfiles.
- Add a dated `CHANGELOG.md` `[0.3.2]` section modelled on sbxagent's entries:
  - **Changed:** Pi 1.4.0 via the image digest; Context7 0.1.3; trace skill.
  - **Added:** GitHub MCP, the `github` credential, `$schema`.
  - **Security:**
    - a bound GitHub secret is usable by every Pi process in the sandbox, compile turns included, with the token's full scope (recommend least privilege);
    - GitHub MCP results are not inspected;
    - trust and `.pi/mcp.json`.
- Stage the changes and draft the commit message, but don't commit (AGENTS.md).

## Verification

The task is not complete until all of these pass.

1. `make lint`, `make test-md2okf`, `make test-clis`, `make test-web2md`, `make test-shell`, the trace skill's pytest, and `make dist`.
2. Kit schema:
   - `make validate` on a signed-in host;
   - inside the sandbox, as the interim offline check, `sbx kit pack kits/<agent> --output <scratch>.zip` for **every** kit (`pi`, `claude`, `codex`).
   - Since I can't sign in to sbx here, you run `make validate`, and I don't call the task done until it passes.
3. `sbx rm --force md2okf-pi && make test-sandbox AGENT=pi`, so no sandbox built from the old kit is reused. Run it once more with the GitHub secret bound and `REQUIRE_GITHUB=1` to certify the authenticated MCP path.
4. Live smoke: `uv run md2okf -v -o "$(mktemp -d)" tests/fixtures/smoke.md`. Confirm:
   - tool calls and messages still render;
   - the compile's tool calls are only read/bash/edit/write and Context7;
   - no MCP startup noise appears.
   This run also supplies the §4 protocol fixture.
5. Run `sbx exec md2okf-pi -- md2okf-agent pi --list-models deepseek` and fix the kit README figures if they changed.
