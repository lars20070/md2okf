# Multi-agent sandbox kits: pi, claude, codex, cursor

## Context

`md2okf` currently drives exactly one agent framework, Pi, through one sandbox
kit (`kits/md2okf/`). The Python driver assumes Pi everywhere: the kit
directory is a fixed lookup (`resources.kit_dir()`), the sandbox has one fixed
name (`workbench.SANDBOX_NAME = "md2okf"`), and — the deepest coupling —
`compile.py`'s Ralph loop invokes `["pi", "--mode", "json", prompt]` and
`events.py` parses Pi's own NDJSON protocol to render progress and detect
whether a turn did any work.

The user wants to add `claude` (Claude Code), `codex` (OpenAI Codex CLI) and
`cursor` (Cursor CLI) as equally-supported agent frameworks, selected by an
environment variable, with the **same automated compile pipeline** Pi gets
today (not just an interactive shell) — confirmed in review. `lars20070/sbxagent`
is the explicit style guide: its `kits/sbxclaude`, `kits/sbxcodex`,
`kits/sbxcursor` show the pattern for a thin kit that `extends:` a built-in
parent (native vendor login, not OpenRouter), a GH_TOKEN→GITHUB_TOKEN
entrypoint wrapper, per-agent MCP config, and — for claude/codex — a
network-block enforcement hook (cursor has none, by design, since Cursor
exposes no verified hook equivalent). Research this session confirmed all
three CLIs also support a non-interactive, NDJSON-streaming mode comparable to
Pi's (`claude -p --output-format stream-json`, `codex exec --json`,
`agent -p --output-format stream-json`), and that Claude Code and Codex both
support the same `SKILL.md` file convention Pi's `compile-okf` skill already
uses — only Cursor lacks a skill mechanism and needs its procedures folded
into `.cursor/rules/`/`AGENTS.md` instead, which it reads natively.

Design decisions locked in during review (see the four `AskUserQuestion`
answers this session): full compile-pipeline parity per agent; native vendor
login per agent (not routed through OpenRouter); `kits/md2okf/` renamed to
`kits/pi/` with `kits/claude/`, `kits/codex/`, `kits/cursor/` as symmetric
siblings; one sandbox + one workbench per agent, namespaced, so all four can
coexist.

This is a large change. It touches the driver's core abstractions (kit
lookup, sandbox naming, event parsing), three new sandbox kits authored from
scratch, and every piece of tooling that assumed exactly one kit. The plan
below describes the target architecture once and gives representative file
paths; the actual new-kit authoring (spec.yaml, skills, network allow lists)
repeats the same pattern three times and is described once with pi/claude as
the worked example.

## Part 1 — Driver: from one fixed kit to a selectable `Agent`

### `MD2OKF_AGENT` environment variable

New, read once via `os.environ.get("MD2OKF_AGENT", "pi")`, following the exact
precedence pattern `workbench.state_home()` already uses for `XDG_STATE_HOME`
(`src/md2okf/workbench.py:83-92`). Valid values: `pi`, `claude`, `codex`,
`cursor`. An unrecognized value is a decided-before-any-work-starts failure
(exit 2), same tier as an unresolvable `--spec` file today.

Document it in `cli.py`'s epilog (`src/md2okf/cli.py:42-51`) alongside
`OPENROUTER_API_KEY`/`XDG_STATE_HOME`/`SPEC_MD`, and in README.md's
Environment table (`README.md:347-359`).

### New module: `src/md2okf/agents.py`

Replaces the driver's hardcoded Pi assumptions with a small registry:

```python
@dataclass(frozen=True)
class Agent:
    name: str                                   # "pi" | "claude" | "codex" | "cursor"
    binary: str                                  # "pi" | "claude" | "codex" | "agent"
    interactive_args: list[str]                  # argv for `--agent` (e.g. ["pi"])
    compile_args: Callable[[str], list[str]]      # prompt -> full argv for one Ralph-loop turn
    translate: Callable[[str], str | None]
    is_tool_call: Callable[[str], bool]
    process: Callable[[Iterable[str]], Iterator[tuple[str, str | None, bool]]]

AGENTS: dict[str, Agent] = {"pi": ..., "claude": ..., "codex": ..., "cursor": ...}
DEFAULT_AGENT = "pi"

class UnknownAgentError(Exception): ...

def resolve(value: str) -> Agent: ...  # AGENTS[value] or raise UnknownAgentError listing valid names
```

`compile_args` per agent (confirmed against each CLI's own non-interactive
flags via Context7 this session; verify exact flag spelling against
`--help` output during implementation, same spirit as `events.py`'s docstring
noting it replaces a jq filter derived from real output):

| Agent | `compile_args(prompt)` | `interactive_args` |
|---|---|---|
| pi | `["pi", "--mode", "json", prompt]` (unchanged) | `["pi"]` |
| claude | `["claude", "-p", "--output-format", "stream-json", "--verbose", prompt]` | `["claude"]` |
| codex | `["codex", "exec", "--json", "--dangerously-bypass-approvals-and-sandbox", prompt]` | `["codex"]` |
| cursor | `["agent", "-p", "--output-format", "stream-json", "--force", prompt]` | `["agent"]` |

### New package: `src/md2okf/protocols/`

`src/md2okf/events.py` (Pi's NDJSON parser) moves to `src/md2okf/protocols/pi.py`
unchanged in behavior; `tests/test_events.py` moves alongside it. Three new
sibling modules, each exposing the same three functions with the same
signatures (`translate(line) -> str | None`, `is_tool_call(line) -> bool`,
`process(lines) -> Iterator[tuple[str, str | None, bool]]`), so `compile.py`
never needs to know which agent it's talking to beyond `agent.process`:

- `protocols/claude.py` — Claude Code's `stream-json` events (`assistant`
  messages with `content` blocks, a `tool_use` block type for calls, a final
  `result` event for success/failure).
- `protocols/codex.py` — Codex's `--json` `ThreadEvent` stream (`item.completed`
  with `item.type in {"command_execution", "file_change"}` as the tool-call
  signal; `turn.failed`/`thread.error` as failure).
- `protocols/cursor.py` — Cursor's `stream-json` events (`type: "tool_call"`
  with `subtype: "started"/"completed"` for calls, `type: "assistant"` for
  text, `type: "result"` with `is_error` for the final outcome).

**Risk flagged for implementation, not resolved by this plan**: the exact
field names above come from CLI docs/source snippets, not a captured live
sample. Before writing each parser, run the agent once in its real sandbox
(`sbx exec <name> -- claude -p --output-format stream-json --verbose "..."`,
etc.), capture actual output, and derive the parser from it — exactly how
`events.py`'s own docstring says it replaced the old jq filter. Budget this as
a distinct sub-task per new agent, not a paper design.

Keep `translate()`'s output shape consistent across all four modules (tool
call → `"ToolName args"` cut to `DISPLAY_WIDTH`; assistant text/thinking joined
by blank lines) so `-v` output reads the same regardless of `MD2OKF_AGENT`.

### `compile.py`

`compile_document` gains an `agent: agents.Agent` parameter. Replace the two
hardcoded spots:
- `src/md2okf/compile.py:221` — `sandbox.exec_stream(name, ["pi", "--mode", "json", prompt])`
  → `sandbox.exec_stream(name, agent.compile_args(prompt))`.
- `src/md2okf/compile.py:225` — `events.process(stream)` → `agent.process(stream)`.

`COMPILE_PROMPT`/`CONTINUATION_PROMPT` (`compile.py:21-32`) stay agent-neutral
text ("follow the compile-okf skill") rather than hardcoding
`~/.pi/agent/skills/...` — each kit's own instruction file tells that agent
how skills/rules are discovered in its environment, so the prompt itself
doesn't need to know the path.

### `resources.py`

`kit_dir()` (`src/md2okf/resources.py:59-62`) takes an `agent: str` param.
Installed layout changes from singular `kit/` to plural `kits/<agent>/`, so
`_installed_root()`'s existence probe (`resources.py:32`,
`(candidate / "kit").is_dir()`) becomes `(candidate / "kits").is_dir()`, and
the checkout fallback becomes `_checkout_path(f"kits/{agent}", "the sandbox kit")`.

### `workbench.py`

- `SANDBOX_NAME = "md2okf"` (`workbench.py:23`) becomes a function
  `sandbox_name(agent: str) -> str` returning `f"md2okf-{agent}"` — every one
  of the four gets its own sandbox, matching sbxagent's one-sandbox-per-wrapper
  model. Every call site (`cli.py`, `compile.py` call sites, tests) threads
  the resolved agent name through instead of importing the constant.
- `Workbench.default()` (`workbench.py:149-152`) takes `agent: str`, root
  becomes `state_home() / "md2okf" / agent` — nested, so `XDG_STATE_HOME`
  gains one `md2okf/` folder with four agent subfolders rather than four
  top-level `md2okf-*` folders.
- `ensure_sandbox()` passes `resources.kit_dir(agent)` and `sandbox_name(agent)`
  through to `sandbox.create(...)`.

**One-time migration note** (goes in CHANGELOG.md): existing users' current
`md2okf` sandbox and `~/.local/state/md2okf/` workbench are orphaned by this
change (the new default is `md2okf-pi` / `.../md2okf/pi/`). Document
`sbx rm --force md2okf` as the cleanup step; the old workbench directory can
be deleted manually. This is a one-time cost, not an ongoing compatibility
concern — `kits/md2okf/` is being renamed anyway, which already forces a kit
rebuild via the existing content-hash fingerprint regardless of sandbox naming.

### `cli.py`

- Resolve and validate `MD2OKF_AGENT` immediately after `parser.parse_args`
  in `main()` (`cli.py:301-309`), before the `--shell`/`--agent` branch, so
  both the interactive and compile paths get one validated `Agent` up front.
  `agents.UnknownAgentError` joins the exception tuple already caught in
  `_resolve_inputs` (`cli.py:106`).
- `_format_sbx_run`/`_format_sbx_exec_pi` (`cli.py:130-153`) take `agent` and
  use `workbench.sandbox_name(agent.name)`/`resources.kit_dir(agent.name)`/
  `agent.compile_args(prompt)` instead of the hardcoded Pi invocation; rename
  the latter to `_format_sbx_exec_agent`.
- `_enter_sandbox` (`cli.py:193-246`): `sandbox.exec_interactive(sandbox_name, ["bash"] if args.shell else agent.interactive_args)`
  replaces the hardcoded `["pi"]` at `cli.py:240`.
- `_run` (`cli.py:249-298`) passes `agent` into `compile_mod.compile_document(...)`.

## Part 2 — Three new sandbox kits, ported from `sbxagent`

Rename `kits/md2okf/` → `kits/pi/` (spec.yaml `name: md2okf` → `name: pi`,
`md2okf-entrypoint` id, `~/.local/lib/md2okf/mount-state.sh` path and
`md2okf:` log prefix in `kits/pi/spec.yaml`, and `kits/pi/README.md`'s
`sbx exec md2okf` examples → `sbx exec md2okf-pi`). Keep `MD2OKF_STATE_DIR`
as the env var name across all four kits — it's driver-owned, not
sbxagent-derived, no reason to rename it.

Then author `kits/claude/`, `kits/codex/`, `kits/cursor/`, each following the
same template (worked example below uses claude; codex and cursor repeat the
pattern with the differences called out in the tables further down):

### spec.yaml skeleton (per new kit)

```yaml
extends: claude   # or codex / cursor — the sbx built-in parent kit
agentInstructions:
  filename: CLAUDE.md   # AGENTS.md for codex/cursor, per sbxagent's own table
  content: |
    ## Sandbox environment
    <port kits/pi's existing workspace-boundary text: fixed mounts
    (work_okf rw, work_md/work_scripts/work_spec ro, sessions state dir),
    "never create an okf/ child directory", policy-block reporting rule>
    ## Preinstalled tools
    <same OKF toolchain list as kits/pi: okfctl, mq, inspectmd, inspectokf,
    sizeokf, merkleokf, markdownlint-cli2, cspell, ruff, yamllint>
entrypoint:
  - sh
  - -c
  - |
    set -eu
    if [ -n "${GH_TOKEN:-}" ]; then export GITHUB_TOKEN="$GH_TOKEN"; fi
    sh "$HOME/.local/lib/md2okf/mount-state.sh" "$HOME/.claude/projects" projects || ...
    exec claude "$@"
  - md2okf-entrypoint
permissions:
  network:
    allow:
      # kits/pi's existing OKF-toolchain hosts (registry.npmjs.org, pypi.org,
      # files.pythonhosted.org, archive/security/ports.ubuntu.com,
      # download.docker.com, github.com + release-assets.githubusercontent.com,
      # mqlang.org/book/, context7.com) -- every new kit needs the same OKF
      # tooling installed, so needs the same hosts.
      # No claude.ai/anthropic hosts here: extends: claude's own base preset
      # already allows them (sbxagent's spec.yaml comments confirm this
      # per-agent, and note the pattern "verified with `sbx<agent> policy check`").
setup:
  install:
    # Same OKF CLI installs kits/pi already has: okfctl, mq, markdownlint-cli2,
    # cspell, ruff, yamllint (ported verbatim -- these are agent-agnostic).
    # github-mcp-server, ported from sbxagent's claude/codex/cursor kits.
    # Network-block escalation hook (claude, codex only -- see below).
  startup:
    # Bind-mount step (same pattern as kits/pi's, different LINK/SUBDIR).
```

### Per-agent differences (from `sbxagent`, confirmed this session)

| | claude | codex | cursor |
|---|---|---|---|
| `extends:` | `claude` | `codex` | `cursor` |
| instruction filename | `CLAUDE.md` | `AGENTS.md` | `AGENTS.md` |
| entrypoint token export | `GITHUB_TOKEN` | `GITHUB_TOKEN` **and** `GITHUB_PERSONAL_ACCESS_TOKEN` (codex's `config.toml` has no `${VAR}` expansion) | `GITHUB_TOKEN` |
| trace bind-mount target | `~/.claude/projects` | `~/.codex/sessions` | `~/.cursor/projects` |
| GitHub MCP token syntax | `"${GITHUB_TOKEN}"` in `~/.claude.json` | static `env_vars = ["GITHUB_PERSONAL_ACCESS_TOKEN"]` in `config.toml`, appended via startup step (parent kit truncates the file at install time) | `"${env:GITHUB_TOKEN}"` in `~/.cursor/mcp.json`, shipped as a static `files/home/.cursor/mcp.json` |
| network-block guard | managed-settings `PostToolUse`/`PostToolUseFailure` hook, hard stop (`continue: false`) | same hook mechanism written to `/etc/codex/requirements.toml`, soft (cannot force a stop) | **none** — no verified Cursor hook equivalent; `agentInstructions` just asks the agent to report a block, unenforced (matches sbxagent's own documented gap) |
| OKF procedure delivery | `.claude/skills/<name>/SKILL.md`, same frontmatter Pi already uses — port the six skills near-verbatim, updating only `~/.pi/agent/skills/...` path references to `~/.claude/skills/...` | `SKILL.md` under Codex's own skill root (confirmed native support, same `name`/`description` frontmatter, scanned to depth 6) — port the same way | **no skill mechanism** — fold the six skills' procedural content into `.cursor/rules/*.md` (or `AGENTS.md`, which Cursor CLI also reads per its own docs) since Cursor has nothing equivalent to progressive-disclosure skill loading. Confirm the exact rules-file convention (always-applied vs. scoped) against Cursor CLI docs during implementation. |

Reuse `kits/pi/files/home/.local/lib/md2okf/mount-state.sh` verbatim in all
three new kits (already proven byte-compatible with sbxagent's own script);
only the entrypoint/startup call sites' `LINK`/`SUBDIR` arguments differ, per
the table above.

Port the network-block `jq` filter and its Claude Code `managed-settings.json`
hook / Codex `requirements.toml` hook setup steps directly from
`sbxagent`'s `kits/sbxclaude/spec.yaml` and `kits/sbxcodex/spec.yaml` (already
read in full this session) — adjust only the matcher tool name (`Bash|WebFetch`
for claude, `^Bash$` for codex, per sbxagent's own table) and drop the
self-reference exemption's file-list (`AGENTS.md|CLAUDE.md|spec.yaml|...`) to
match md2okf's own filenames instead of sbxagent's.

## Part 3 — Tooling and tests

### `pyproject.toml`

`force-include` (`pyproject.toml:61-71`) expands from one line to four:
```toml
"kits/pi" = "md2okf/kits/pi"
"kits/claude" = "md2okf/kits/claude"
"kits/codex" = "md2okf/kits/codex"
"kits/cursor" = "md2okf/kits/cursor"
```

### `scripts/validate-spec.sh`

Currently hardcodes `kits/md2okf/spec.yaml` (`validate-spec.sh:22-23`). Switch
to the glob idiom `sbxagent` itself uses for uniform per-kit checks (its
`release.yml` comment: *"discovered, not hardcoded, so a fifth kit needs no
edit here"*): `for kit in kits/*/; do sbx kit validate "${kit%/}"; done`.

### `Makefile`

- `check-okf` target (`Makefile:91`) repoints from `kits/md2okf/files/...` to
  `kits/pi/files/...` — no other change; the check itself validates the
  *generated wiki*, which stays agent-agnostic.
- No other Makefile target needs the glob treatment yet (`install`,
  `install-clis`, `dist` are already kit-agnostic).

### `tests/test-sandbox.sh` + `tests/test-sandbox-guest.sh`

`kit_name="md2okf"` (`test-sandbox.sh:18`) becomes parameterized (an
`AGENT=${1:-pi}` argument), driving both the kit path and the expected
sandbox name (`md2okf-${AGENT}`). Because the guest-side invariants differ
meaningfully per agent (different config paths, and — critically — only `pi`
checks `OPENROUTER_API_KEY`'s proxy-managed sentinel; claude/codex/cursor have
no equivalent, they use native vendor login), split
`test-sandbox-guest.sh` into one script per kit
(`test-sandbox-guest-pi.sh`, `-claude.sh`, `-codex.sh`, `-cursor.sh`),
copying the current script as the `pi` variant and adjusting per the table in
Part 2. `make test-sandbox` runs all four (or accepts an `AGENT=` override for
a single one during development).

### `tests/conftest.py`

`FakePopen`'s dispatch (`conftest.py:190`) hardcodes `tail[0] == "pi"` and
raises `AssertionError` for anything else — the one place in the existing fake
that assumes Pi. Generalize to accept any of the four binaries
(`{"pi", "claude", "codex", "agent"}`), or drop the strict check in favor of
just recording whatever argv arrived, matching how `FakePopen`'s execvp
fake already handles this generically (`conftest.py:200-203`).

### New/updated tests

- `agents.py`: `resolve()` returns the right `Agent` for each of the four
  names and raises `UnknownAgentError` (with the valid-names list in the
  message) for anything else.
- `resources.kit_dir("claude")` etc. resolve correctly in both the installed
  (`_installed_root()`) and checkout (`_checkout_path`) code paths — extend
  the existing `tests/test_resources.py` coverage per agent rather than only
  for `"pi"`.
- `workbench.sandbox_name("claude")` / `Workbench.default("claude")` produce
  the namespaced name/root — extend `tests/test_workbench.py`'s existing
  `SANDBOX_NAME`/`Workbench.default` coverage (including the fingerprint test
  at `test_workbench.py:548`) per agent.
- `protocols/claude.py`, `protocols/codex.py`, `protocols/cursor.py`: unit
  tests against **captured real sample output** (see the risk note in Part 1)
  — do not hand-write fixture JSON from guessed schemas.
- `cli.py`: `MD2OKF_AGENT=bogus md2okf ...` exits 2 with a clear message.

## Verification

1. `make lint` — the shared-file check (`Makefile:46-63`) will need its
   reference kit (`ref=kits/sbxclaude/...` equivalent, currently implicitly
   `kits/md2okf/...`) repointed at one of the four new kit directories for
   `mount-state.sh`/`.editorconfig`/`.gitconfig` parity, if md2okf adopts
   that same cross-kit invariant check (recommended, not required by this
   plan — flag as an optional follow-up).
2. `make validate` (now looping `kits/*/`) passes for all four kits.
3. `make test-md2okf` (pytest, offline, fake `sbx`) covers the new
   `agents`/`protocols` modules and the parameterized `resources`/`workbench`
   behavior — no live sandbox needed for this tier.
4. `make test-clis` unaffected (kit-agnostic helper CLIs).
5. Per new kit, live verification against a real sandbox (needs `sbx login`):
   - `sbx rm --force md2okf-claude 2>/dev/null; MD2OKF_AGENT=claude uv run md2okf --dry-run md/<one-doc>.md` —
     confirms the resolved kit dir, sandbox name, and compile-args line look right.
   - `MD2OKF_AGENT=claude uv run md2okf md/<one-small-doc>.md -o /tmp/okf-claude-test` —
     a full compile run, confirming the protocol parser correctly detects tool
     calls and convergence, and that `-o` receives a real wiki.
   - `MD2OKF_AGENT=claude uv run md2okf --agent` — confirms the interactive
     path launches `claude` (not `pi`) in the right sandbox.
   - Repeat for `codex` and `cursor`.
6. `./scripts/validate-spec.sh` (or `make validate`) directly after any
   kit-directory edit, per AGENTS.md's own standing rule.

## Suggested delivery order

Given the size, land this as four increments rather than one changeset:

1. **Foundation**: `MD2OKF_AGENT`/`agents.py`/`protocols/` package, the
   `kits/md2okf/` → `kits/pi/` rename, and every driver/tooling change in
   Parts 1 and 3 — with only `"pi"` registered. This alone is fully testable
   and ships zero behavior change for existing users beyond the one-time
   sandbox/workbench rename.
2. `kits/claude/` + `protocols/claude.py`, registered.
3. `kits/codex/` + `protocols/codex.py`, registered.
4. `kits/cursor/` + `protocols/cursor.py` (and its rules-file procedure
   adaptation), registered.

Each of 2-4 is independently shippable and follows the exact same template,
so the first one (claude) is the one worth reviewing most closely — codex and
cursor are largely repetition once it's right.
