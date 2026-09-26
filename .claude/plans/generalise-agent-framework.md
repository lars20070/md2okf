# Multi-agent sandbox kits: pi, claude, codex, cursor

## Context

`md2okf` currently drives exactly one agent framework, Pi, through one sandbox
kit (`kits/md2okf/`). The Python driver assumes Pi everywhere: the kit
directory is a fixed lookup (`resources.kit_dir()`), the sandbox has one fixed
name (`workbench.SANDBOX_NAME = "md2okf"`), post-create validation checks Pi's
OpenRouter sentinel (`workbench.py:597`), the compile prompt names Pi's skill
path (`compile.py:21-25`), and — the deepest coupling — `compile.py`'s Ralph
loop invokes `["pi", "--mode", "json", prompt]` and `events.py` parses Pi's own
NDJSON protocol to render progress and detect whether a turn did any work.

The user wants to add `claude` (Claude Code), `codex` (OpenAI Codex CLI) and
`cursor` (Cursor CLI) as equally-supported agent frameworks, selected by an
environment variable, with the **same automated compile pipeline** Pi gets
today (not just an interactive shell) — confirmed in review. `lars20070/sbxagent`
is the style guide for the kits themselves: a thin kit that `extends:` a
built-in parent (native vendor login, not OpenRouter), per-agent MCP config,
and — for claude/codex — a network-block enforcement hook. All three CLIs
support a non-interactive, NDJSON-streaming mode comparable to Pi's.

**sbxagent is a guide for kit *contents*, not for process lifecycle.**
sbxagent starts agents through the kit entrypoint (`sbx run`). md2okf creates a
detached sandbox and then runs every compile turn and every `--agent` session
through `sbx exec <name> -- <argv>`, which never passes through the entrypoint.
Anything sbxagent does in its entrypoint (env exports, the fatal trace-mount
check, permission flags) must be re-homed for md2okf — see "Per-process
wrapper" in Part 2.

Design decisions locked in (the four `AskUserQuestion` answers from the
planning session, plus the defaults taken after the external review):

- Full compile-pipeline parity per agent.
- Native vendor login per agent (not routed through OpenRouter).
- `kits/md2okf/` renamed to `kits/pi/`, with `kits/claude/`, `kits/codex/`,
  `kits/cursor/` as symmetric siblings.
- One sandbox + one workbench per agent, namespaced, so all four can
  **coexist** — meaning their sandboxes and state survive side by side, **not**
  that they compile concurrently. The global per-user lock
  (`workbench.LOCK_PATH_TEMPLATE`) stays exactly as it is; two agents writing
  the same `-o` directory at once would need output locking that this plan
  does not add. Document this in the README.
- No GitHub MCP in the md2okf kits (departure from sbxagent). The Pi kit has
  none, the compile task never touches GitHub, and dropping it removes a
  credential, a network host, and the whole GH_TOKEN→GITHUB_TOKEN export
  problem. Each kit gets Context7 only, matching Pi's native
  `@upstash/context7-pi`. Revisit if `--agent` users ask for it.
- Cursor gets its procedures through kit-provided instructions only, never
  through a `.cursor/` directory in the workspace (which *is* the generated
  wiki).

This is a large change. It touches the driver's core abstractions (kit lookup,
sandbox naming, credential validation, prompt construction, event parsing),
three new sandbox kits authored from scratch, and every piece of tooling that
assumed exactly one kit.

## Part 0 — Pre-existing bugs to fix first (independent of new agents)

Found while reviewing this plan. Both hit Pi today and both would silently
break the new kits, so they land first, on their own.

### Kit fingerprint ignores almost the whole kit

`workbench._hash_tree()` (`workbench.py:438-453`) skips every path with any
component starting with `.`. For `kits/md2okf/` that excludes
`files/home/.pi/**` and `files/home/.local/**`: **only 2 of the kit's 15 files
(`README.md`, `spec.yaml`) are hashed today.** Edits to Pi's `AGENTS.md`,
skills, `settings.json`, or `mount-state.sh` do not move the fingerprint, so a
stale sandbox is reused — contradicting AGENTS.md's promise that config edits
land when "the kit's hash stops matching".

Fix: narrow the exclusion to actual noise — a basename of `.DS_Store`, a
basename starting with `._` (AppleDouble), and any `__pycache__` component.
Keep `test_fingerprint_ignores_dotfiles_and_pycache` for those cases (rename to
match), and add a test that mutating a file under a hidden directory
(`files/home/.pi/agent/AGENTS.md`, and later `.claude`/`.agents`/`.codex`/
`.cursor` equivalents) changes the fingerprint. Existing users get one rebuild.

### sdist excludes are unanchored

`pyproject.toml:73` has `exclude = [".claude", ".cursor"]`. Hatchling reads
these gitignore-style, so a slash-less pattern matches at any depth — it would
strip `kits/claude/files/home/.claude/**` and `kits/cursor/files/home/.cursor/**`
from the sdist, and the wheel built from it (`uv build` builds the wheel from
the sdist) would lose them or fail resolving the force-include. Anchor them:
`exclude = ["/.claude", "/.cursor"]`. Pin the behavior with a
`tests/test_package.py` assertion that every packaged kit's hidden config files
are present in the wheel, and make `make dist` part of every increment's gate.

## Part 1 — Driver: from one fixed kit to a selectable `Agent`

### `MD2OKF_AGENT` environment variable

Read once via `os.environ.get("MD2OKF_AGENT", "pi")`, following the precedence
pattern `workbench.state_home()` already uses for `XDG_STATE_HOME`
(`workbench.py:83-92`). Valid values are exactly the **registered** agents at
that increment — `pi` only in increment 1, growing as each kit lands. An
unrecognized value is a decided-before-any-work-starts failure (exit 2), same
tier as an unresolvable `--spec` file today.

Document it in `cli.py`'s epilog (`cli.py:42-51`) and README.md's Environment
table (`README.md:347-359`), listing only the registered values.

### New module: `src/md2okf/agents.py`

The `Agent` owns **everything** that differs between runtimes, so no generic
module keeps a Pi branch:

```python
@dataclass(frozen=True)
class Agent:
    name: str                                    # "pi" | "claude" | "codex" | "cursor"
    min_sbx_version: tuple[int, int, int]        # pi (0, 43, 0); extends-kits per Part 1 "sbx version"
    compile_args: Callable[[str], list[str]]     # prompt -> full argv for one Ralph-loop turn
    interactive_args: list[str]                  # argv for `--agent`
    compile_prompt: Callable[[str], str]         # document path -> first-turn prompt
    check_credentials: Callable[[str], str | None]  # sandbox name -> None if ready, else a remedy message
    protocol: Protocol                           # the protocols/<name>.py module (see below)

AGENTS: dict[str, Agent] = {"pi": ...}           # grows one entry per increment
DEFAULT_AGENT = "pi"

class UnknownAgentError(Exception): ...
def resolve(value: str) -> Agent: ...            # AGENTS[value] or raise listing valid names
```

#### `compile_args` / `interactive_args`

Every argv goes through the kit's per-process wrapper `md2okf-agent` (Part 2),
except Pi's compile argv in increment 1 (no behavior change) — Pi moves onto
the wrapper with the rest once it exists.

| Agent | `compile_args(prompt)` | `interactive_args` |
|---|---|---|
| pi | `["pi", "--mode", "json", prompt]` (unchanged) | `["pi"]` |
| claude | `["md2okf-agent", "claude", "-p", "--output-format", "stream-json", "--verbose", "--permission-mode", "bypassPermissions", prompt]` | `["md2okf-agent", "claude", "--permission-mode", "bypassPermissions"]` |
| codex | `["md2okf-agent", "codex", "exec", "--json", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox", prompt]` | `["md2okf-agent", "codex", "--dangerously-bypass-approvals-and-sandbox"]` |
| cursor | `["md2okf-agent", "agent", "-p", "--output-format", "stream-json", "--force", "--trust", "--approve-mcps", prompt]` | `["md2okf-agent", "agent", "--approve-mcps"]` |

Why each flag is load-bearing:

- **claude `--permission-mode bypassPermissions`** — headless `-p` starts in
  the default mode and, with no one to approve, denies every tool call that
  would prompt; without it the turn cannot write the wiki. The microVM is the
  isolation boundary, as for the other agents. (`--dangerously-skip-permissions`
  is equivalent; pick one.)
- **codex `--skip-git-repo-check`** — `codex exec` refuses to run outside a Git
  repository, and the workspace is the generated wiki, which has no `.git`.
  Without it the first Codex turn exits before any tool call.
- **cursor `--force`** — without it print mode only proposes edits.
  **`--trust`** — skips the workspace-trust prompt that would otherwise block
  headless mode. **`--approve-mcps`** — auto-approves the Context7 MCP server
  instead of needing sbxagent's separate startup approval step.

Unit tests assert each registered agent's exact argv. Verify spelling against
each CLI's `--help` in the live sandbox during implementation, and back every
row with one **live headless write test** (Verification §5): capturing protocol
samples alone does not catch a command that never gets far enough to emit
useful events.

#### `compile_prompt`

The current `COMPILE_PROMPT` is not neutral — it tells the agent to read
`~/.pi/agent/skills/compile-okf/SKILL.md` — and the four runtimes have no shared
activation syntax. So prompt construction is agent-owned; only the document
path, the workspace-root sentence ("never create an okf/ child directory") and
`CONTINUATION_PROMPT` stay common:

| Agent | activation in the first-turn prompt |
|---|---|
| pi | read `~/.pi/agent/skills/compile-okf/SKILL.md` (today's text, unchanged) |
| claude | `/compile-okf` (skill at `~/.claude/skills/compile-okf/SKILL.md`) |
| codex | `$compile-okf` (skill at `~/.agents/skills/compile-okf/SKILL.md`) |
| cursor | "follow the compile procedure in your instructions" (no skill mechanism) |

Tests assert each agent's prompt names the procedure its kit actually installs,
by checking the path/name exists in `kits/<agent>/`.

#### `check_credentials`

Replaces the unconditional `sandbox.key_is_proxy_managed()` call in
`ensure_sandbox()` (`workbench.py:597`), which would reject every non-Pi
sandbox. Pi's implementation is today's OpenRouter sentinel check.
`KeyNotProxyManagedError` generalises to `CredentialNotReadyError(name, remedy)`
carrying an agent-specific remedy message; ownership-marker semantics are
unchanged (the marker is still written before the check). The new agents'
checks are decided in their own increments — a cheap probe of the
proxy-managed vendor credential, confirmed during the live spike, not guessed.

#### sbx version

`sandbox.MIN_VERSION = (0, 43, 0)` becomes the default, and
`Agent.min_sbx_version` overrides it per agent. sbxagent — the source of the
extends-kit patterns — requires sbx 0.45.0 and depends on its parent-kit merge,
startup, credential and managed-hook behavior. Unless a new kit is proven on
0.43, its `min_sbx_version` is `(0, 45, 0)`, and the preflight
(`sandbox.py:75-98`) checks the resolved agent's minimum. Pi keeps 0.43. README
and `kits/<agent>/README.md` state each minimum.

### New package: `src/md2okf/protocols/`

`src/md2okf/events.py` moves to `src/md2okf/protocols/pi.py`, and
`tests/test_events.py` moves alongside it. Each protocol module exposes the
same interface, but the normalized record gains the failure information the
current tuple cannot carry:

```python
class Event(NamedTuple):
    raw: str
    display: str | None       # what -v prints, or None
    is_tool_call: bool
    diagnostic: str | None    # a structured error worth keeping (result error, turn.failed, ...)

def translate(line: str) -> str | None: ...
def is_tool_call(line: str) -> bool: ...
def process(lines: Iterable[str]) -> Iterator[Event]: ...
```

Today `_diagnostic_tail()` (`compile.py:43-51`) drops every line starting with
`{`, so an error that the agent reports *as JSON* (Claude `result` with
`is_error`, Codex `turn.failed`/`error`, Cursor `result.is_error`) would
surface as a bare "agent exited 1". `compile.py` therefore collects the
`diagnostic` values alongside the non-JSON lines and folds both into the same
bounded tail. The process exit code stays authoritative for success/failure;
`diagnostic` only enriches the message. `test_failure_tail_excludes_protocol_json`
(`tests/test_compile.py:463`) stays true for non-diagnostic envelopes and gains
a sibling asserting a structured error does appear.

New modules, one per agent increment:

- `protocols/claude.py` — `stream-json` events: `assistant` messages with
  `content` blocks, `tool_use` blocks as calls, final `result` (with
  `is_error`) as the outcome.
- `protocols/codex.py` — `exec --json` stream: `item.completed` with
  `item.type in {"command_execution", "file_change", ...}` as tool calls,
  `turn.failed`/`error` as diagnostics.
- `protocols/cursor.py` — `stream-json`: `tool_call` with `subtype`
  `started`/`completed` as calls, `assistant` for text, `result` with
  `is_error` as the outcome.

**Risk, resolved per increment, not on paper:** these field names come from
docs, not captured output. Before writing each parser, run the agent headless
in its real sandbox, capture the output, and derive the parser from it — the
way `events.py`'s docstring says it replaced the old jq filter. Fixtures per
protocol: a successful run, a structured failure, malformed JSON, and plain
stderr — all from captured output, not hand-written from guessed schemas.

Keep `display` consistent across modules (tool call → `"ToolName args"` cut to
`DISPLAY_WIDTH`; assistant text/thinking joined by blank lines) so `-v` reads
the same regardless of `MD2OKF_AGENT`.

### `compile.py`

`compile_document` gains `agent: agents.Agent`:

- `compile.py:221` → `sandbox.exec_stream(name, agent.compile_args(prompt))`.
- `compile.py:225` → `agent.protocol.process(stream)`, consuming `Event`s.
- `COMPILE_PROMPT.format(...)` → `agent.compile_prompt(document)`;
  `CONTINUATION_PROMPT` stays shared.
- The failure path folds `Event.diagnostic` values into the diagnostic tail.

### `resources.py`

`kit_dir()` (`resources.py:59-62`) takes `agent: str`. The installed layout
changes from singular `kit/` to plural `kits/<agent>/`, so `_installed_root()`'s
probe (`resources.py:32`) becomes `(candidate / "kits").is_dir()`, and the
checkout fallback becomes `_checkout_path(f"kits/{agent}", "the sandbox kit")`.

### `workbench.py`

- `SANDBOX_NAME = "md2okf"` becomes `sandbox_name(agent: str) -> str` returning
  `f"md2okf-{agent}"`. Every call site threads the resolved agent name through.
- `Workbench.default()` takes `agent: str`; root becomes
  `state_home() / "md2okf" / agent`.
- **Trace mount stays one host mount named `sessions` for every agent.**
  `Workbench.mounts()` (`workbench.py:194-202`) is unchanged; each kit binds its
  agent's native trace directory (whatever it is called — `projects` for
  Claude/Cursor) onto `$MD2OKF_STATE_DIR/sessions`. Passing sbxagent's `projects`
  SUBDIR instead would bind onto a sibling that is not host-mounted, so traces
  would vanish with the sandbox. Fix the `sessions` docstring, which says "Pi's".
- `ensure_sandbox()` takes the `Agent`, passes `resources.kit_dir(agent.name)`
  and `sandbox_name(agent.name)` to `sandbox.create(...)`, and replaces the
  OpenRouter check with `agent.check_credentials(name)`.
- The lock stays global (see Context).

**One-time migration note** (CHANGELOG.md): the existing `md2okf` sandbox and
`$XDG_STATE_HOME/md2okf/` workbench layout are superseded by `md2okf-pi` and
`.../md2okf/pi/`. Cleanup is `sbx rm --force md2okf`. The old workbench's
top-level `work/`, `sessions/` and fingerprint files sit beside the new `pi/`
subdirectory and can be deleted by hand — note that `sessions/` holds old Pi
transcripts, in case the user wants to move them into `pi/sessions/`.

### `cli.py`

- Resolve `MD2OKF_AGENT` right after `parser.parse_args` in `main()`
  (`cli.py:301-309`), before the `--shell`/`--agent` branch.
  `agents.UnknownAgentError` joins the exception tuple in `_resolve_inputs`
  (`cli.py:106`) — or is caught in `main()` directly if that branch runs first.
- `_format_sbx_run`/`_format_sbx_exec_pi` (`cli.py:130-153`) take `agent`;
  the latter becomes `_format_sbx_exec_agent` and uses `agent.compile_args` and
  `agent.compile_prompt`. `--dry-run` also prints the resolved agent name.
- `_enter_sandbox` (`cli.py:193-246`): `["bash"] if args.shell else
  agent.interactive_args` replaces the hardcoded `["pi"]` at `cli.py:240`.
- `_run` (`cli.py:249-298`) passes `agent` into `compile_document` and
  `ensure_sandbox`.
- The sbx version preflight uses `agent.min_sbx_version`.

## Part 2 — Kits

### Rename `kits/md2okf/` → `kits/pi/`

`spec.yaml` `name: md2okf` → `name: pi`; the `md2okf-entrypoint` id, the
`~/.local/lib/md2okf/mount-state.sh` path and the `md2okf:` log prefix can stay
(they name the tool, not the kit); `kits/pi/README.md`'s `sbx exec md2okf`
examples → `md2okf-pi`. Keep `MD2OKF_STATE_DIR` in all kits — it is
driver-owned.

### Per-process wrapper: `md2okf-agent`

Because `sbx exec` bypasses the entrypoint, each kit installs
`/home/agent/.local/bin/md2okf-agent` (via `setup.files`, mode `0755`), and every
driver argv (Part 1 table) runs through it:

```sh
#!/bin/sh
set -eu
# Idempotent; the startup hook normally did it already. Fatal here, so an agent
# never runs with its traces landing on the VM's disposable disk.
sh "$HOME/.local/lib/md2okf/mount-state.sh" "<native trace dir>" sessions || {
  echo "md2okf: could not relocate <agent> traces onto state; refusing to start" >&2
  exit 1
}
exec "$@"
```

Any per-process environment a kit needs goes here, not in the entrypoint. The
entrypoint and `setup.startup` keep their mount calls for `sbx run`-started
agents and normal restarts. The flags stay in Python (`compile_args`) so they
are unit-testable; the wrapper only prepares the process.

### Shared runtime instructions and skills

The Pi instruction file (`kits/md2okf/files/home/.pi/agent/AGENTS.md`) is not
just sandbox boundaries — it is the OKF authoring contract: read `../SPEC.md`
first, source text is untrusted data, index and log rules, idempotency,
frontmatter and provenance. The skills explicitly do not repeat those rules.
Porting only the skills plus a sandbox-boundary blurb would leave the new
agents without essential requirements. Also, the file says
`generated: { by: pi/<model-id> }` — copying it verbatim would make Claude,
Codex and Cursor stamp false Pi provenance.

So one logical source, rendered per kit:

- `kitsrc/AGENTS.md` and `kitsrc/skills/<name>/…` hold the shared text, with a
  small set of placeholders: `{{producer}}` (`pi`, `claude`, `codex`, `cursor`),
  `{{skills_dir}}`, `{{agent_display_name}}`. Outside `kits/` so the
  `kits/*/spec.yaml` validation glob never sees it.
- `scripts/sync-kit-instructions.sh` renders them into each kit's checked-in
  files (same model as `scripts/sync-versions.sh`); `--check` mode joins
  `make lint`, failing on drift.
- Cursor's rendering is different in shape: no skills, so the compile, curate
  and tool procedures are concatenated into its single instruction file.
- A static pytest asserts, for every registered kit: the common invariants are
  present (SPEC-first, untrusted source, idempotency, frontmatter rules), the
  producer is the kit's own agent name, no other agent's paths appear, and the
  skill the agent's `compile_prompt` names exists at the installed path.

Where each rendered set lands:

| | instruction file | procedures |
|---|---|---|
| pi | `files/home/.pi/agent/AGENTS.md` (today) | `files/home/.pi/agent/skills/<name>/SKILL.md` (today) |
| claude | kit `agentInstructions` → `CLAUDE.md` | `files/home/.claude/skills/<name>/SKILL.md` |
| codex | kit `agentInstructions` → `AGENTS.md` | `files/home/.agents/skills/<name>/SKILL.md` (user scope; `/etc/codex/skills` is the admin alternative) |
| cursor | kit `agentInstructions` → `AGENTS.md`, carrying the full procedure | none — no skill mechanism, and **no** `.cursor/rules` in the workspace, which is the generated wiki |

**Cursor verification gate:** Cursor CLI documents reading `AGENTS.md`,
`CLAUDE.md` and `.cursor/rules` from the *project*. Before building the cursor
kit, confirm where sbx's `cursor` parent writes `agentInstructions` and that
`agent -p` actually loads it when the workspace is the wiki. If it only works by
placing a file in the workspace root, stop and decide — a file there would
become part of the output (and `okfctl` would see it).

### spec.yaml skeleton (per new kit)

```yaml
extends: claude   # or codex / cursor — the sbx built-in parent kit
agentInstructions:
  filename: CLAUDE.md   # AGENTS.md for codex/cursor
  content: |
    <rendered from kitsrc/AGENTS.md: sandbox boundary (work_okf rw;
    work_md/work_scripts/work_spec ro; $MD2OKF_STATE_DIR/sessions), the tool list,
    and the full OKF authoring contract with producer = this agent>
entrypoint:
  - sh
  - -c
  - |
    set -eu
    sh "$HOME/.local/lib/md2okf/mount-state.sh" "<native trace dir>" sessions || { ...; exit 1; }
    exec claude "$@"
  - md2okf-entrypoint
permissions:
  network:
    allow:
      # kits/pi's OKF-toolchain hosts, minus openrouter.ai and pi.dev: npm,
      # PyPI, Ubuntu archives, download.docker.com, github.com + release CDNs,
      # mqlang.org/book/, context7.com. Vendor API hosts come from the
      # extends: parent's preset — confirm with `sbx policy` against the
      # live sandbox rather than assuming.
setup:
  install:
    # OKF CLI installs from kits/pi, verbatim: apt tools, markdownlint-cli2,
    # cspell, ruff, yamllint, mq, okfctl.
    # Context7 MCP registration (per-agent syntax, table below).
    # Network-block escalation hook (claude, codex only).
  startup:
    # mount-state.sh <native trace dir> sessions   (idempotent)
  files:
    # md2okf-agent wrapper; inspectmd/inspectokf/sizeokf/merkleokf shims from kits/pi.
```

### Per-agent differences

| | claude | codex | cursor |
|---|---|---|---|
| `extends:` | `claude` | `codex` | `cursor` |
| instruction filename | `CLAUDE.md` | `AGENTS.md` | `AGENTS.md` |
| native trace dir (bound to `sessions`) | `~/.claude/projects` | `~/.codex/sessions` | `~/.cursor/projects` |
| Context7 MCP | `~/.claude.json` / managed MCP config | appended to `~/.codex/config.toml` **once, in `setup.install`**, after the parent truncates it — never in `startup`, which would append duplicate TOML tables on every start and eventually break the config | static `files/home/.cursor/mcp.json`; approval via `--approve-mcps` in the argv |
| network-block guard | managed-settings `PostToolUse`/`PostToolUseFailure` hook, hard stop (`continue: false`), matcher `Bash\|WebFetch` | same hook via `/etc/codex/requirements.toml`, soft (cannot force a stop), matcher `^Bash$` | none — no verified hook; instructions ask the agent to report a block (Pi's status quo too) |
| first-use credential | decide in spike | **blocked on the auth spike below** | decide in spike |

Reuse `mount-state.sh` verbatim in all kits. Port the network-block `jq` filter
and hook setup from sbxagent's `kits/sbxclaude/spec.yaml` and
`kits/sbxcodex/spec.yaml`, adjusting the matcher and the self-reference
exemption's file list to md2okf's own filenames.

### Codex first-use authentication (spike, gates increment 4)

sbxagent documents that the built-in `codex` parent asks the user to approve
the `openai` credential on first creation. md2okf creates with
`sbx run --detached`, captured output and `stdin=DEVNULL` (`sandbox.py:53-55,
122-137`), so that prompt cannot be answered — the run would fail minutes into
creation with a generic `sbx run failed`. `--agent` cannot help, because it
creates the sandbox before entering it.

Spike: provision the credential on the host first (`sbx secret set openai …`
or the parent's documented equivalent), then run the exact detached create
md2okf uses. Then:

- **If creation proceeds without prompting** → make host provisioning a
  documented prerequisite, and make `codex.check_credentials` give that exact
  remedy command when it is missing.
- **If it still prompts** → add an explicit bootstrap: for an agent flagged
  `interactive_create`, `sandbox.create` runs `sbx run` attached to the
  terminal (and refuses without one, like `--shell`/`--agent` do today), so
  the first creation happens in a session where the user can approve it.

Run the same check for claude and cursor in their increments; do not assume
they are prompt-free.

## Part 3 — Tooling and tests

### `pyproject.toml`

- Force-include one line per **registered** kit, added in that kit's
  increment: `"kits/pi" = "md2okf/kits/pi"` in increment 1, then claude,
  codex, cursor. Never advertise a kit that does not exist yet.
- Anchored sdist excludes (Part 0).

### `scripts/validate-spec.sh`

Replace the hardcoded `kits/md2okf/spec.yaml` (`validate-spec.sh:22-23`) with
a discovered loop, like sbxagent's release workflow:
`for spec in kits/*/spec.yaml; do sbx kit validate "$(dirname "$spec")"; done`.

### `Makefile`

- `check-okf` (`Makefile:91`) repoints from `kits/md2okf/files/...` to
  `kits/pi/files/...`.
- `lint` gains `scripts/sync-kit-instructions.sh --check`.
- Optional follow-up: a cross-kit parity check that `mount-state.sh` and the
  `md2okf-agent` template are byte-identical across kits.

### `tests/test-sandbox.sh` + guest scripts

`kit_name="md2okf"` (`test-sandbox.sh:18`) becomes `AGENT=${1:-pi}`, driving
the kit path and the sandbox name (`md2okf-${AGENT}`). Split
`test-sandbox-guest.sh` into `test-sandbox-guest-<agent>.sh`, starting from
today's script as `-pi`; only `-pi` checks the `OPENROUTER_API_KEY` sentinel.
Each guest script must, among its checks:

- write a file through the agent's **native** trace path, and the host side
  must then find it under the workbench's `sessions/` — proving the bind lands
  on host-backed state, not on a VM-local sibling;
- confirm `md2okf-agent` is on PATH and executable;
- confirm the rendered instruction file names the right producer.

`make test-sandbox` runs every registered agent, or one with `AGENT=`.

### `tests/conftest.py`

`FakePopen` (`conftest.py:190`) hardcodes `tail[0] == "pi"`. Generalize to
accept any registered agent's `compile_args` head (`pi`, `md2okf-agent`).

### New/updated tests

- `agents.py`: `resolve()` for every registered name; `UnknownAgentError`
  listing valid names otherwise; exact `compile_args`, `interactive_args` and
  `compile_prompt` per agent.
- `resources.kit_dir(<agent>)` in both installed and checkout paths
  (`tests/test_resources.py`).
- `workbench.sandbox_name(<agent>)` / `Workbench.default(<agent>)`;
  `ensure_sandbox` calls `agent.check_credentials` and no longer calls the
  OpenRouter check for a non-Pi agent (`tests/test_workbench.py`).
- Fingerprint: hidden-directory changes move it; `.DS_Store`/`._*`/`__pycache__`
  do not (Part 0).
- Package: every packaged kit's hidden files are in the wheel (Part 0).
- Protocols: per module, captured fixtures for success, structured failure,
  malformed JSON and plain stderr; a structured failure appears in the
  `CompileError` message.
- Instructions: the static render test from Part 2.
- `cli.py`: `MD2OKF_AGENT=bogus md2okf ...` exits 2 with a clear message; the
  sbx preflight uses the agent's minimum version.

## Verification (every increment)

1. `make lint` — including `sync-versions.sh --check` and
   `sync-kit-instructions.sh --check`.
2. `make validate` — every `kits/*/spec.yaml`.
3. `make test-md2okf`, `make test-clis`, `make test-web2md`, `make test-shell`.
4. `make dist` — the wheel built *from the sdist*, which is where the hidden-dir
   exclusion bug would show.
5. Per registered agent, live (needs `sbx login`, plus the agent's vendor
   credential):
   - `sbx rm --force md2okf-<agent>; MD2OKF_AGENT=<agent> uv run md2okf --dry-run md/<doc>.md`
     — resolved agent, kit dir, sandbox name and exact argv.
   - `sbx rm --force md2okf-<agent> && make test-sandbox AGENT=<agent>` —
     fresh sandbox, native trace write verified from the host.
   - `MD2OKF_AGENT=<agent> uv run md2okf md/<small-doc>.md -o /tmp/okf-<agent>`
     — a real headless write: tool calls detected, convergence reached, pages
     written with `generated.by: <agent>/…`.
   - Force a failure (e.g. unset the vendor credential) and confirm the
     `CompileError` carries the structured error, not just "exited 1".
   - `MD2OKF_AGENT=<agent> uv run md2okf --agent` — launches the right CLI in
     the right sandbox.

## Delivery order

Each increment updates the registry, the packaged-kit list, docs and tests
together, so every intermediate state is internally consistent.

0. **Fingerprint and sdist fixes** (Part 0). Standalone, benefits Pi now.
1. **Foundation, Pi only.** `agents.py` with agent-owned argv, prompt,
   credential check, sbx minimum and protocol; `protocols/` package with the
   `Event` record and diagnostic folding; `kits/md2okf/` → `kits/pi/`;
   namespaced sandbox/workbench; `kitsrc/` + sync script producing Pi's current
   files byte-for-byte; tooling from Part 3. Only `pi` is registered, packaged
   or documented. Behavior change for users: the one-time sandbox/workbench
   rename.
2. **Claude**, end to end: kit, `md2okf-agent` wrapper (Pi moves onto it here
   too), rendered instructions and skills, `protocols/claude.py` from captured
   output, credential check, live headless write and persisted-trace test.
   Proves the parent-kit, permission, instruction and protocol patterns — the
   increment to review most closely.
3. **Codex**, after the auth spike: `--skip-git-repo-check`, install-time MCP
   append, `~/.agents/skills`, and the chosen first-use flow.
4. **Cursor**, after the instruction-location gate: single rendered instruction
   file, `--force --trust --approve-mcps`.
