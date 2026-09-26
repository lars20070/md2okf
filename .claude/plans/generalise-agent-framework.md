# Multi-agent sandbox kits: pi, claude, codex

## Context

`md2okf` currently drives exactly one agent framework, Pi, through one sandbox
kit (`kits/md2okf/`). The Python driver assumes Pi everywhere: the kit
directory is a fixed lookup (`resources.kit_dir()`), the sandbox has one fixed
name (`workbench.SANDBOX_NAME = "md2okf"`), post-create validation checks Pi's
OpenRouter sentinel (`workbench.py:597`), the compile prompt names Pi's skill
path (`compile.py:21-25`), the maintainer entry point `python -m md2okf.sandbox`
hardcodes all of the above (`sandbox.py:248-287`), and — the deepest coupling —
`compile.py`'s Ralph loop invokes `["pi", "--mode", "json", prompt]` and
`events.py` parses Pi's own NDJSON protocol to render progress and detect
whether a turn did any work.

The user wants to add `claude` (Claude Code) and `codex` (OpenAI Codex CLI) as
equally-supported agent frameworks, selected by an environment variable, with
the **same automated compile pipeline** Pi gets today (not just an interactive shell). `lars20070/sbxagent` is the style guide
for the kits themselves: a thin kit that `extends:` a built-in parent (native
vendor login, not OpenRouter). Both CLIs support a non-interactive,
NDJSON-streaming mode comparable to Pi's.

Cursor (Cursor CLI) was the fourth candidate and has been dropped. Its
subscription login could not be carried into a headless compile: the host's
OAuth secret was not injected into the sandbox, and after an interactive login
persisted to the file store, `agent -p` still failed with "Authentication
required". Adding it again would start from a new spike.

**sbxagent is a guide for kit *contents*, not for process lifecycle.**
sbxagent starts agents through the kit entrypoint (`sbx run`). md2okf creates a
detached sandbox and then runs every compile turn and every `--agent` session
through `sbx exec <name> -- <argv>`, which never passes through the entrypoint.
Anything sbxagent does in its entrypoint must be re-homed for md2okf — see
"Per-process wrapper" in Part 2.

Design decisions locked in (planning-session answers, plus defaults the user
confirmed after the external reviews):

- Full compile-pipeline parity per agent.
- Native vendor login per agent (not routed through OpenRouter).
- `kits/md2okf/` renamed to `kits/pi/`, with `kits/claude/` and `kits/codex/`
  as symmetric siblings.
- One sandbox + one workbench per agent, namespaced, so all three can
  **coexist** — their sandboxes and state survive side by side; they do **not**
  compile concurrently. The global per-user lock (`workbench.LOCK_PATH_TEMPLATE`)
  stays as it is. Document this in the README.
- **The new kits carry only what compiling needs:** vendor authentication,
  instructions and procedure, the OKF toolchain, trace persistence, the sandbox
  network allowlist, and the headless command. No MCP servers (neither GitHub
  nor Context7 — the compile procedure uses neither) and no vendor network-block
  hooks (the sandbox allowlist is already the enforcement boundary). Both are
  listed under "Deferred". Pi keeps its existing Context7 extension unchanged.
- Instruction and procedure files are **checked in per agent**, not generated
  from a shared template — see Part 2.

## Part 0 — Pre-existing bugs to fix first (independent of new agents)

Both hit Pi today and both would silently break the new kits, so they land
first, on their own.

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
(`files/home/.pi/agent/AGENTS.md`, later the new kits' equivalents) changes the
fingerprint. Existing users get one rebuild.

### sdist excludes are unanchored

`pyproject.toml:73` has `exclude = [".claude", ".cursor"]`. Hatchling reads
these gitignore-style, so a slash-less pattern matches at any depth — it would
strip `kits/claude/files/home/.claude/**` from the sdist, and the wheel built
from it (`uv build` builds the wheel from the sdist) would lose them or fail resolving the force-include. Anchor them:
`exclude = ["/.claude", "/.cursor"]`. Pin the behavior with a
`tests/test_package.py` assertion that every packaged kit's hidden files are
present in the wheel, and make `make dist` part of every stage's offline gate.

## Part 1 — Driver: from one fixed kit to a selectable `Agent`

### `MD2OKF_AGENT` environment variable

Read once via `os.environ.get("MD2OKF_AGENT", "pi")`, following the precedence
pattern `workbench.state_home()` already uses for `XDG_STATE_HOME`
(`workbench.py:83-92`). Valid values are exactly the **registered** agents at
that stage — `pi` only through Milestone 1, growing as each agent registers
(stage N.4). An
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
    name: str                                    # "pi" | "claude" | "codex"
    min_sbx_version: tuple[int, int, int]        # pi (0, 43, 0); extends-kits per "sbx version"
    compile_args: Callable[[str], list[str]]     # prompt -> full argv for one Ralph-loop turn
    interactive_args: tuple[str, ...]            # argv for `--agent`
    compile_prompt: Callable[[str], str]         # document path -> first-turn prompt
    check_credentials: Callable[[str], str | None]  # sandbox name -> None if ready, else a remedy message
    protocol: Protocol                           # the protocols/<name>.py module (see below)

AGENTS: dict[str, Agent] = {"pi": ...}           # grows one entry per agent milestone
DEFAULT_AGENT = "pi"

class UnknownAgentError(Exception): ...
def resolve(value: str) -> Agent: ...            # AGENTS[value] or raise listing valid names
```

#### `compile_args` / `interactive_args`

Every argv goes through the kit's per-process wrapper `md2okf-agent` (Part 2),
except Pi's until stage 1.6, which introduces the wrapper and moves Pi onto it
before any new agent depends on it.

| Agent | `compile_args(prompt)` | `interactive_args` |
|---|---|---|
| pi | `["md2okf-agent", "pi", "--mode", "json", prompt]` (from stage 1.6; `pi` directly before) | `["md2okf-agent", "pi"]` |
| claude | `["md2okf-agent", "claude", "-p", "--output-format", "stream-json", "--verbose", "--permission-mode", "bypassPermissions", "--strict-mcp-config", prompt]` | `["md2okf-agent", "claude", "--permission-mode", "bypassPermissions"]` |
| codex | `["md2okf-agent", "codex", "exec", "--json", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox", "-c", "mcp_servers.mcp-gateway.enabled=false", prompt]` | `["md2okf-agent", "codex", "--dangerously-bypass-approvals-and-sandbox"]` |

Why each flag is load-bearing:

- **claude `--permission-mode bypassPermissions`** — headless `-p` in the
  default mode denies every tool call that would prompt, with no one to
  approve it. The spike found the `claude` parent already makes
  `bypassPermissions` the default (a run without the flag wrote its file, and
  its `system/init` event reports `bypassPermissions`). The flag stays anyway:
  it costs nothing and keeps the compile independent of a parent default that
  may change. The microVM is the isolation boundary, as for the other agents.
- **claude `--strict-mcp-config`** (compile only; added by the spike) — with no
  `--mcp-config`, the turn loads no MCP servers. Without it the spike's turns
  loaded the parent's `mcp-gateway` plus every claude.ai connector on the
  logged-in account (Gmail, Drive and others, some `needs-auth`), which a
  compile needs none of and which make runs depend on the account.
  `--agent` keeps them.
- **codex `--skip-git-repo-check`** — `codex exec` refuses to run outside a Git
  repository, and the workspace is the generated wiki, which has no `.git`.

Unit tests assert each registered agent's exact argv. Each row is confirmed
against the CLI's `--help` in the agent's spike (stage N.1) and
backed by one **live headless write test**: capturing protocol samples alone
does not catch a command that never gets far enough to emit useful events.

#### `compile_prompt`

The current `COMPILE_PROMPT` is not neutral — it tells the agent to read
`~/.pi/agent/skills/compile-okf/SKILL.md` — and the three runtimes have no shared
activation syntax. So prompt construction is agent-owned; only the document
path, the workspace-root sentence ("never create an okf/ child directory") and
`CONTINUATION_PROMPT` stay common:

| Agent | activation in the first-turn prompt |
|---|---|
| pi | read `~/.pi/agent/skills/compile-okf/SKILL.md` (today's text, unchanged) |
| claude | read `~/.claude/skills/compile-okf/SKILL.md` — Pi's wording with Claude's path (built in stage 2.4: slash activation in `-p` was never measured, and naming the file works however skills load) |
| codex | `$compile-okf` (skill at `~/.agents/skills/compile-okf/SKILL.md`) |

Tests assert each agent's prompt names the procedure its kit actually installs,
by checking the path/name exists in `kits/<agent>/`.

#### `check_credentials`

Replaces the Pi-only `sandbox.key_is_proxy_managed()` call in `ensure_sandbox()`.
`KeyNotProxyManagedError` generalises to `CredentialNotReadyError(name, remedy)`
carrying an agent-specific remedy message. Pi's implementation is today's
OpenRouter sentinel check.

Lifecycle rules:

- **Checked on both create and reuse.** Today `ensure_sandbox()` returns
  `"reuse"` before the key check (`workbench.py:590-592`), so a sandbox whose
  create succeeded but whose credential was not ready is never re-checked once
  the user follows the remedy — or, worse, is reused while still broken. The
  check moves to after both branches. Ownership-marker semantics are unchanged
  (the marker is still written before the check on create).
- **Non-interactive and unpaid.** It runs on every compile, `--shell`,
  `--agent` and `python -m md2okf.sandbox`, so it must be a local probe through
  `sandbox._run` (stdin `/dev/null`) — an env sentinel or a CLI's own
  auth-status command — never a model request. Each new agent's probe is chosen
  in its spike. Claude's (from its spike): `claude auth status` prints JSON
  with `"loggedIn": true` when the credential is in place.
- **A secret takes effect only when a sandbox is created.** sbx injects the
  credential at create time (the spike's sandbox got its
  `~/.claude/.credentials.json` then), so the remedy for a not-ready
  credential is "set the secret, then `sbx rm --force md2okf-<agent>`", not
  merely "run again". Each agent's remedy text says so.
- **`--shell` does not require it.** A failed check is fatal for compile,
  `--agent` and `python -m md2okf.sandbox`; for `--shell` it prints the remedy as
  a warning and opens the shell anyway, since a diagnostic shell is most needed
  exactly when credentials are broken.

Tests (fake sbx): create → not ready → `CredentialNotReadyError`, marker
written; remedy applied → next call reuses and succeeds; reuse while not ready
→ error, no rebuild; `--shell` with not-ready credentials → warning, shell
opens. (The fake models a credential that becomes ready in place. Live, sbx
injects credentials at create time, so the real remedy ends with `--fresh` —
see the Claude spike findings. Pi's remedy text does not yet say so; the
`sbx secret set-custom` output itself warns that existing sandboxes may keep
the old value. Fix Pi's remedy alongside Claude's in stage 2.4.)

#### sbx version

`sandbox.MIN_VERSION = (0, 43, 0)` becomes the default, and
`Agent.min_sbx_version` overrides it per agent. sbxagent — the source of the
extends-kit patterns — requires sbx 0.45.0. Unless a new kit is proven on 0.43
in its spike, its `min_sbx_version` is `(0, 45, 0)` — Claude's is, the spike
having run on 0.45.0 only — and the preflight
(`sandbox.py:75-98`) checks the resolved agent's minimum. Pi keeps 0.43. README
and `kits/<agent>/README.md` state each minimum.

### New package: `src/md2okf/protocols/`

`src/md2okf/events.py` moves to `src/md2okf/protocols/pi.py`, and
`tests/test_events.py` moves alongside it. Each protocol module exposes the
same interface, with a normalized record that carries a terminal outcome:

```python
class Event(NamedTuple):
    raw: str
    display: str | None       # what -v prints, or None
    is_tool_call: bool
    failure: str | None       # the protocol declared the turn failed (result is_error, turn.failed, error, ...)

def translate(line: str) -> str | None: ...
def is_tool_call(line: str) -> bool: ...
def process(lines: Iterable[str]) -> Iterator[Event]: ...
```

**A protocol-declared failure is authoritative, like a non-zero exit.** A CLI
can emit a terminal error event and still exit 0, or report it after earlier
tool calls. Relying on the exit code alone would then either raise the
misleading "made no tool calls" error or, worse, treat the turn as a success and
mirror its output to `-o`. So a turn fails when **either** the process exits
non-zero **or** any event carries a `failure`. Pi's parser reports `failure`
only if its captured output shows a terminal error event; otherwise it is
always `None`, keeping Milestone 1 behavior-neutral.

New modules, one per agent milestone (stage N.2):

- `protocols/claude.py` — `stream-json`: `assistant` messages with `content`
  blocks, `tool_use` blocks as calls, final `result` with `is_error` as a
  failure.
- `protocols/codex.py` — `exec --json`: `item.completed` with
  `item.type in {"command_execution", "file_change", ...}` as tool calls,
  only `turn.failed` as a failure (an `error` event before it is a warning;
  see the stage 3.1 findings).

**These field names come from docs, not captured output.** Each parser is
derived from real output captured in its agent's spike — the way `events.py`'s
docstring says it replaced the old jq filter. Fixtures per protocol, all
captured: a successful run, a terminal failure, malformed JSON, and plain
stderr.

Keep `display` consistent across modules (tool call → `"ToolName args"` cut to
`DISPLAY_WIDTH`; assistant text/thinking joined by blank lines) so `-v` reads
the same regardless of `MD2OKF_AGENT`.

### `compile.py`

`compile_document` gains `agent: agents.Agent`:

- `compile.py:221` → `sandbox.exec_stream(name, agent.compile_args(prompt))`.
- `compile.py:225` → `agent.protocol.process(stream)`, consuming `Event`s and
  remembering the last `failure`.
- `COMPILE_PROMPT.format(...)` → `agent.compile_prompt(document)`;
  `CONTINUATION_PROMPT` stays shared.
- After the stream closes, in this order: a `failure` or a non-zero exit raises
  `CompileError(f"{agent.name} turn failed: ...")` — the protocol failure text
  first, then `_diagnostic_tail()` for any plain-text context; only then the
  "made no tool calls" check; only then `mirror_out`. The hardcoded "pi exited"
  and "pi session" messages (`compile.py:244-246`) use `agent.name`.

Tests: exit 0 plus a protocol failure → `CompileError`, nothing mirrored; tool
calls followed by a protocol failure → `CompileError` (not success, not "no
tool calls"); non-zero exit with no structured failure → today's tail message;
`test_failure_tail_excludes_protocol_json` (`tests/test_compile.py:463`) still
holds.

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
  Claude) onto `$MD2OKF_STATE_DIR/sessions`. Passing sbxagent's `projects`
  SUBDIR instead would bind onto a sibling that is not host-mounted, so traces
  would vanish with the sandbox. Fix the `sessions` docstring, which says "Pi's".
- `ensure_sandbox()` takes the `Agent`, passes `resources.kit_dir(agent.name)`
  and `sandbox_name(agent.name)` to `sandbox.create(...)`, and runs
  `agent.check_credentials(name)` on both create and reuse (see above).
- The lock stays global.

**One-time migration note** (CHANGELOG.md): the existing `md2okf` sandbox and
`$XDG_STATE_HOME/md2okf/` workbench layout are superseded by `md2okf-pi` and
`.../md2okf/pi/`. Cleanup is `sbx rm --force md2okf`. The old workbench's
top-level `work/`, `sessions/` and fingerprint files sit beside the new `pi/`
subdirectory and can be deleted by hand — `sessions/` holds old Pi
transcripts, in case the user wants to move them into `pi/sessions/`.

### `cli.py`

- Resolve `MD2OKF_AGENT` right after `parser.parse_args` in `main()`
  (`cli.py:301-309`), before the `--shell`/`--agent` branch, and map
  `agents.UnknownAgentError` to exit 2 there.
- `_format_sbx_run`/`_format_sbx_exec_pi` (`cli.py:130-153`) take `agent`;
  the latter becomes `_format_sbx_exec_agent` and uses `agent.compile_args` and
  `agent.compile_prompt`. `--dry-run` also prints the resolved agent name.
- `_enter_sandbox` (`cli.py:193-246`): `["bash"] if args.shell else
  agent.interactive_args` replaces the hardcoded `["pi"]` at `cli.py:240`, and
  applies the `--shell` credential-warning rule.
- `_run` (`cli.py:249-298`) passes `agent` into `compile_document` and
  `ensure_sandbox`.
- The sbx version preflight uses `agent.min_sbx_version`.

### `python -m md2okf.sandbox` (maintainer entry point)

`_ensure_default_sandbox()` (`sandbox.py:248-287`) is documented in AGENTS.md
and is how `tests/test-sandbox.sh` asks the driver for a correctly mounted
sandbox. It independently hardcodes `preflight()`, `Workbench.default()`,
`ensure_sandbox(wb)`, `SANDBOX_NAME` and `KeyNotProxyManagedError`. It must:

- resolve `MD2OKF_AGENT` the same way as `cli.py` (unknown → exit 2);
- preflight against `agent.min_sbx_version`;
- use `Workbench.default(agent.name)`, `ensure_sandbox(wb, agent)` and
  `sandbox_name(agent.name)` in its output line;
- catch `CredentialNotReadyError` (exit 2, remedy printed).

Parameterize its existing tests over `pi` and, from stage 2.4, one non-Pi
agent, so the live sandbox test can never create or inspect the wrong sandbox
while the main CLI works.

## Part 2 — Kits

### Rename `kits/md2okf/` → `kits/pi/`

`spec.yaml` `name: md2okf` → `name: pi`; the `md2okf-entrypoint` id, the
`~/.local/lib/md2okf/mount-state.sh` path and the `md2okf:` log prefix stay
(they name the tool, not the kit); `kits/pi/README.md`'s `sbx exec md2okf`
examples → `md2okf-pi`. Keep `MD2OKF_STATE_DIR` in all kits — it is
driver-owned.

### Per-process wrapper: `md2okf-agent`

Because `sbx exec` bypasses the entrypoint, each kit ships the wrapper script
at `files/home/.local/lib/md2okf/md2okf-agent.sh` (beside `mount-state.sh`, and
testable the same way), exposed on PATH by a `setup.files` shim
`/home/agent/.local/bin/md2okf-agent` (mode `0755`, like the CLI shims) that
runs `exec sh "$HOME/.local/lib/md2okf/md2okf-agent.sh" "$@"`. Every driver argv
(Part 1 table) goes through it.

```sh
#!/bin/sh
# Usage: sh md2okf-agent.sh TRACE_DIR COMMAND [ARG...]  -- the shim passes TRACE_DIR
set -eu
trace_dir=$1; shift
# Idempotent; the startup hook normally did it already. Fatal here, so an agent
# never runs with its traces landing on the VM's disposable disk.
sh "$HOME/.local/lib/md2okf/mount-state.sh" "$trace_dir" sessions || {
  echo "md2okf: could not relocate traces onto state; refusing to start $1" >&2
  exit 1
}
exec "$@"
```

The shim is where each kit supplies its native trace directory, so the script
itself is byte-identical in every kit. The flags stay in Python
(`compile_args`) so they are unit-testable; the wrapper only prepares the
process. The entrypoint and `setup.startup` keep their mount calls for
`sbx run`-started agents and normal restarts.

The wrapper is the only relocation guard on every automated turn, so it gets
direct behavior tests — see `tests/test-mount-state.sh` in Part 3.

### Instructions and procedures: checked in per agent

The Pi instruction file (`kits/md2okf/files/home/.pi/agent/AGENTS.md`) is not
just sandbox boundaries — it is the OKF authoring contract: read `../SPEC.md`
first, source text is untrusted data, index and log rules, idempotency,
frontmatter and provenance. The skills explicitly do not repeat those rules. So
every new kit carries the **full** contract plus its procedures, each as
checked-in, agent-specific files. Duplication across three small, fixed kits is
preferable to a template system whose abstraction is unproven; factoring out
common text is deferred until all three agents work.

Porting is not a path substitution. Audit and adapt, per agent, at least:

- **provenance** — `generated: { by: pi/<model-id> }` becomes `claude/…` or
  `codex/…`, or the new agents stamp false Pi provenance;
- **the governing file's name** — the compile skill cites `AGENTS.md`
  repeatedly; Claude's is `CLAUDE.md`;
- **the check script** — `~/.pi/agent/skills/compile-okf/scripts/check-okf.sh`
  moves to each kit's skill directory, with its `chmod` install step;
- **skill cross-references** — "read the `inspect-okf` skill" and similar;
- **tool-specific advice** — "Write in bounded chunks" names Pi's
  `write`/`edit` tools and Pi's output-truncation failure; rewrite for each
  agent's actual file-edit mechanism and failure mode, or drop what does not
  apply.

Where each set lands:

| | instruction file | procedures |
|---|---|---|
| pi | `files/home/.pi/agent/AGENTS.md` (today) | `files/home/.pi/agent/skills/<name>/SKILL.md` (today) |
| claude | kit `agentInstructions` → `CLAUDE.md` | `files/home/.claude/skills/<name>/SKILL.md` |
| codex | `files/home/.codex/AGENTS.md` (no `agentInstructions`; see stage 3.1b) | `files/home/.agents/skills/<name>/SKILL.md` |

A static pytest (`tests/test_kits.py`), for every registered kit, asserts:
the shared invariants are present (SPEC first, untrusted input, frontmatter,
idempotency); `generated.by` names the kit's own agent; no other agent's paths
appear (e.g. no `.pi/` in the claude kit); every path the instructions and
procedures reference exists in the kit; the skill the agent's `compile_prompt`
names exists; and `mount-state.sh` and `md2okf-agent.sh` are byte-identical
across kits.

### spec.yaml skeleton (per new kit)

```yaml
extends: claude   # or codex — the sbx built-in parent kit
agentInstructions:
  filename: CLAUDE.md   # codex declares none: ~/.codex/AGENTS.md instead
  content: |
    <checked-in, agent-specific: sandbox boundary (work_okf rw;
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
      # kits/pi's OKF-toolchain hosts, minus openrouter.ai, pi.dev and
      # context7.com: npm, PyPI, Ubuntu archives, download.docker.com,
      # github.com + release CDNs, mqlang.org/book/. Vendor API hosts come
      # from the extends: parent's preset — confirm against the live sandbox
      # in the spike rather than assuming.
setup:
  install:
    # OKF CLI installs from kits/pi, verbatim: apt tools, markdownlint-cli2,
    # cspell, ruff, yamllint, mq, okfctl. Plus the check-okf.sh chmod.
  startup:
    # mount-state.sh <native trace dir> sessions   (idempotent)
  files:
    # md2okf-agent shim; inspectmd/inspectokf/sizeokf/merkleokf shims from kits/pi.
```

### Per-agent differences

| | claude | codex |
|---|---|---|
| `extends:` | `claude` | `codex` |
| instruction filename | `CLAUDE.md` | `AGENTS.md` (global, not `agentInstructions`) |
| native trace dir (bound to `sessions`) | `~/.claude/projects` (confirmed: `<escaped cwd>/<session>.jsonl`) | `~/.codex/sessions` |
| procedure delivery | skills | skills |
| where `agentInstructions` lands | `<workspace>/../CLAUDE.md`, parent's text plus the kit's, loaded by Claude (confirmed) | nowhere Codex reads (the wiki is not a git repo); the kit ships the contract as `~/.codex/AGENTS.md` instead (confirmed) |
| credential | host `anthropic` secret, OAuth or API key; injected at create (confirmed) | host `openai` secret, OAuth or API key; injected at create (confirmed) |
| credential probe | `claude auth status` → `"loggedIn": true` | `codex login status` → "Logged in" |
| sbx minimum | 0.45.0 | 0.45.0 |

## Part 3 — Tooling and tests

### `pyproject.toml`

- Force-include one line per **registered** kit, added in that kit's
  release stage: `"kits/pi" = "md2okf/kits/pi"` in stage 1.1, then claude,
  then codex.
- Anchored sdist excludes (Part 0).

### `scripts/validate-spec.sh`

Replace the hardcoded `kits/md2okf/spec.yaml` (`validate-spec.sh:22-23`) with
a discovered loop:
`for spec in kits/*/spec.yaml; do sbx kit validate "$(dirname "$spec")"; done`.

### `Makefile`

- `check-okf` (`Makefile:91`) repoints from `kits/md2okf/files/...` to
  `kits/pi/files/...`.
- `test-sandbox` (`Makefile:179-180`) passes the agent explicitly — today it
  passes nothing, so `make test-sandbox AGENT=claude` would silently test Pi:

  ```make
  AGENTS ?= pi        # registered agents; grows at stage N.4
  test-sandbox:
  	for agent in $(or $(AGENT),$(AGENTS)); do ./tests/test-sandbox.sh "$$agent" || exit 1; done
  ```

### `tests/test-sandbox.sh` + guest scripts

*(As built, stage 2.4: the agent-neutral checks — toolchain, shared helpers,
provenance, the `../okf` rule, the trace bind and host probe, the mount-escape
invariants — live in `tests/test-sandbox-guest-common.sh`. Each
`test-sandbox-guest-<agent>.sh` only defines `AGENT_*` variables and an
`agent_checks` function; `test-sandbox.sh` pipes the agent file and then the
common file into the VM as one script.)*

`kit_name="md2okf"` (`test-sandbox.sh:18`) becomes a **required** positional
argument — no default, so nothing falls back to Pi by accident — driving the
kit path, the sandbox name (`md2okf-$1`) and `MD2OKF_AGENT` for the
`python -m md2okf.sandbox` call. Split `test-sandbox-guest.sh` into
`test-sandbox-guest-<agent>.sh`, starting from today's script as `-pi`; only
`-pi` checks the `OPENROUTER_API_KEY` sentinel. Each guest script must:

- write a file through the agent's **native** trace path, and the host side
  must then find it under the workbench's `sessions/` — proving the bind lands
  on host-backed state, not on a VM-local sibling;
- confirm `md2okf-agent` is on PATH and runs a trivial command through it;
- confirm the instruction file names the right producer.

### `tests/test-mount-state.sh`

It asserts **exactly two** `mount-state.sh` call sites in the spec
(`test-mount-state.sh:198-201`), so it fails the moment the wrapper lands
(stage 1.6). Update it in that stage:

- replace the count with explicit checks for the three intended sites — the
  entrypoint, the startup hook, and `md2okf-agent.sh`;
- exercise `md2okf-agent.sh` directly under the existing fake `HOME`: success
  (bind in place, command runs), relocation failure (non-zero exit, command
  **not** run, message on stderr), and exact argument forwarding (arguments
  with spaces and an empty argument arrive unchanged);
- point `HELPER` (`test-mount-state.sh:6`) at `kits/pi/…` after the rename.

### `tests/conftest.py`

`FakePopen` (`conftest.py:190`) hardcodes `tail[0] == "pi"`. Generalize to
accept any registered agent's `compile_args` head (`pi`, `md2okf-agent`), and
let a test script the stream's lines and exit code independently, for the
failure-combination tests.

### New/updated tests (summary)

- `agents.py`: `resolve()` for every registered name; `UnknownAgentError`
  listing valid names; exact `compile_args`, `interactive_args` and
  `compile_prompt` per agent.
- `resources.kit_dir(<agent>)` in both installed and checkout paths.
- `workbench.sandbox_name` / `Workbench.default` per agent; the credential
  lifecycle sequence (Part 1).
- `python -m md2okf.sandbox` over `pi` and one non-Pi agent; unknown → exit 2.
- Fingerprint and package tests (Part 0).
- Protocols: captured fixtures per module; failure-combination tests in
  `test_compile.py` (Part 1).
- `tests/test_kits.py` static invariants (Part 2).
- `cli.py`: `MD2OKF_AGENT=bogus md2okf ...` exits 2; the preflight uses the
  agent's minimum.

## Staged roadmap

Five milestones, each split into small stages. A **stage** is one reviewable
commit (or a short series) that ends in a **checkpoint**; the next stage does
not start until the checkpoint passes. A **milestone** is the merge and release
unit: work happens on a branch, and only a finished milestone is merged to
`master` and tagged. That is what lets a stage leave something deliberately
incomplete (a kit authored but not yet packaged, an agent registered for
checkout use but not yet documented) without it ever reaching a user.

### Checkpoint vocabulary

Defined once, referenced by every stage.

- **Offline gate** — `make lint && make validate && make test-shell &&
  make test-md2okf && make dist`. No `sbx login`, no cost; runs at every stage.
  (`make test-clis` and `make test-web2md` are kit-agnostic; run them at
  milestone ends.)
- **Dry-run diff** — `uv run md2okf --dry-run tests/fixtures/smoke.md` (with
  `MD2OKF_AGENT=<agent>` where relevant), diffed against the baseline saved in
  stage 0.1. Every difference must be one the stage says it introduces. This is
  the cheap, deterministic proof that a refactor did not change what the driver
  would run.
- **Sandbox check (`<agent>`)** — `sbx rm --force <sandbox>; make test-sandbox
  AGENT=<agent>` (before stage 1.4: `sbx rm --force md2okf; make test-sandbox`).
  Needs `sbx login`; minutes, no model cost.
- **Live smoke (`<agent>`)** — `MD2OKF_AGENT=<agent> uv run md2okf
  tests/fixtures/smoke.md -o "$(mktemp -d)"`. Passes when: exit 0; converges
  within the iteration cap; the compile-okf `check-okf.sh` passes on the output
  directory; pages carry `generated.by: <agent>/…`; and the output holds no
  agent artefacts (`.claude/`, `.agents/`, `.pi/`, `.codex/`, `AGENTS.md`,
  `CLAUDE.md`). Needs `sbx login` and the agent's credential; costs cents.

### Milestone 0 — Groundwork and existing bugs (Pi only)

**Stage 0.1 — Baselines and a smoke fixture.** Add `tests/fixtures/smoke.md`:
a short (300–500 words), licence-clean document with two or three headings,
so every live check takes minutes and cents instead of compiling the
15 000-word style guide in `md/`. Save the dry-run output and one Pi live-smoke
result (iterations, pages written, `check-okf.sh` outcome) to the scratchpad as
the reference for later stages. No driver or kit changes.
*Checkpoint:* offline gate green on the untouched tree (so any later failure is
ours); sandbox check (pi) and live smoke (pi) pass.

**Stage 0.2 — Fingerprint fix** (Part 0).
*Checkpoint:* offline gate, including the new hidden-directory fingerprint
tests. Live: `uv run python -m md2okf.sandbox` reports `created` once (the
fingerprint definition changed), then `reuse`; edit a comment in the Pi kit's
`AGENTS.md` → `created`; revert → `created`; again → `reuse`.

**Stage 0.3 — Anchored sdist excludes** (Part 0).
*Checkpoint:* offline gate. `tar tzf dist/*.tar.gz` shows no repository-root
`.claude/` or `.cursor/`. Manual probe: an uncommitted
`kits/md2okf/files/home/.claude/probe` file survives into the wheel built by
`make dist` (the permanent test arrives with `kits/claude/` in stage 2.6).

*Milestone 0 exit:* merge; release as a patch if wanted. Users get one sandbox
rebuild.

### Milestone 1 — Pi on the generalised framework

Goal: every Part 1 abstraction exists, with Pi as its only implementation. At
the end, adding an agent means authoring a kit, a protocol module and one
registry entry, and Pi behaves as before apart from the listed renames. The live
smoke (pi) at each stage is the regression guard.

**Stage 1.1 — Rename `kits/md2okf/` → `kits/pi/`** (Part 2). Also the installed
layout (`kit/` → `kits/pi/`: `_installed_root()` probe and force-include), while
`kit_dir()` still takes no argument, and every path reference: `Makefile`
(`check-okf`), `scripts/validate-spec.sh`, `tests/test-mount-state.sh`
(`HELPER`), `tests/test-sandbox.sh`, `.github/workflows/`, AGENTS.md, README,
CONTRIBUTING and the kit README. The sandbox is still called `md2okf`.
*Checkpoint:* offline gate; `rg -n 'kits/md2okf' --glob '!CHANGELOG.md'` finds
nothing; dry-run diff shows only kit-path changes; sandbox check (pi) — which
also confirms nothing keys on the kit's `name:` (sbx secrets are keyed by
service or sandbox, not kit); live smoke (pi).

**Stage 1.2 — `agents.py` with Pi only.** The `Agent` with `name`,
`compile_args`, `interactive_args`, `compile_prompt` and `protocol` (still the
`events` module). `MD2OKF_AGENT` resolution in `cli.py`; `compile.py` and
`cli.py` take the `Agent`; error messages use `agent.name`; `--dry-run` prints
the agent.
*Checkpoint:* offline gate plus new tests: `resolve()`, exact Pi argv, Pi's
prompt byte-identical to today's `COMPILE_PROMPT`, `MD2OKF_AGENT=bogus` exits 2,
`MD2OKF_AGENT=pi` behaves exactly like unset. Dry-run diff: only the new agent
line. Live smoke (pi).

**Stage 1.3 — `protocols/` package and authoritative failures** (Part 1,
"New package" and `compile.py`). Move `events.py` → `protocols/pi.py`, add the
`Event` record and the failure ordering in `compile.py`, and generalise
`FakePopen` (any argv head; scripted lines and exit code). The failure-combination
tests use a stub `Agent` with a stub protocol, so they do not depend on Pi
having a terminal error event. Before deciding Pi's own `failure` detection,
look for a terminal error in real Pi output (existing transcripts under
`sessions/`, or one run with an invalid model id); if there is none, Pi's
`failure` stays `None`.
*Checkpoint:* offline gate; the moved `test_events.py` passes unchanged in
substance; failure-combination tests pass. Dry-run diff: none. Live smoke (pi),
and `-v` output reads the same as the baseline run.

**Stage 1.4 — Per-agent namespacing** (Part 1, `resources.py`, `workbench.py`,
`python -m md2okf.sandbox`; Part 3, `Makefile` and `tests/test-sandbox.sh`).
`sandbox_name(agent)`, `Workbench.default(agent)`, `kit_dir(agent)`,
`ensure_sandbox(wb, agent)` (still calling the OpenRouter check), the
maintainer entry point, the required `test-sandbox.sh` argument and the
Makefile `AGENTS` list. CHANGELOG migration note. It also covers users of a
custom gateway: the sandbox-scoped `sbx secret set-custom --sandbox md2okf …`
(README:336, `kits/pi/README.md:66`) must be re-run for `md2okf-pi`.
*Checkpoint:* offline gate with the parameterised tests. Dry-run diff: sandbox
`md2okf` → `md2okf-pi`, workbench `…/md2okf/` → `…/md2okf/pi/`. Live, with the
old `md2okf` sandbox still present: `make test-sandbox AGENT=pi` creates
`md2okf-pi` and leaves `md2okf` untouched; `make test-sandbox` without `AGENT`
tests pi; `./tests/test-sandbox.sh` without an argument fails with a usage
message; live smoke (pi); then follow the migration note (`sbx rm --force
md2okf`) exactly as a user would.

**Stage 1.5 — Credential lifecycle and per-agent sbx minimum** (Part 1,
`check_credentials` and sbx version).
*Checkpoint:* offline gate with the lifecycle tests on the fake sbx: not ready →
error and marker written → remedy → reuse succeeds; reuse while not ready →
error, no rebuild; `--shell` warns and opens. Live: sandbox check (pi) via the
reuse path, now also running the check (note the added latency; it should be
one `sbx exec`); `uv run md2okf --shell` opens; live smoke (pi). The not-ready
path is **not** tested live by removing the OpenRouter secret — that would
disturb shared credential state, and the fake sbx covers it.

**Stage 1.6 — Wrapper and static kit tests, for Pi** (Part 2, "Per-process
wrapper" and "Instructions and procedures"; Part 3, `tests/test-mount-state.sh`).
Add `md2okf-agent.sh` and its shim to `kits/pi/`, and move Pi's
`compile_args`/`interactive_args` onto it. Update `test-mount-state.sh` for the
three call sites and the wrapper's behavior. Add `tests/test_kits.py`, run over
every `kits/*/` directory, not only registered agents. Proving the wrapper on
the known agent first means Milestone 2 does not debug it and Claude together.
*Checkpoint:* offline gate, including the new `test-shell` cases (success,
relocation failure, argument forwarding) and `test_kits.py` for pi. Dry-run
diff: argv now starts with `md2okf-agent`. Sandbox check (pi), whose guest
script now runs a command through the wrapper and writes a trace through
`~/.pi/agent/sessions` that the host finds under `sessions/`. Live smoke (pi).
`uv run md2okf --agent` launches Pi.

*Milestone 1 exit:* `make test-clis` and `make test-web2md` too; compare the
live smoke (pi) with the stage 0.1 reference (converges in a similar number of
iterations, `check-okf.sh` passes). Merge; release as a minor version.
User-visible: the sandbox/workbench rename, and `MD2OKF_AGENT` (accepting `pi`).

### Milestone 2 — Claude

**Stage 2.1 — Spike, no production code.** In a scratch kit outside `kits/` (a
minimal `extends: claude` plus mounts shaped like the workbench's), created
exactly the way md2okf creates (`sbx run --detached`, captured output, stdin
`/dev/null` — `sandbox.py:53-55, 122-137`), answer and record:

- **Detached first-use authentication.** Create *before* provisioning the
  credential and observe (prompt? failure? success?); provision it on the host
  (`sbx secret set …`); create again. This order also exercises the
  not-ready → remedy → ready sequence live, without disturbing an existing
  credential. **If the detached create cannot complete without a prompt, stop
  and replan** rather than improvising an attached-create path — that is a
  second sandbox lifecycle (terminal requirements, subprocess handling, when
  ownership is recorded), not a small fallback.
- **Credential probe** — a local, unpaid, non-interactive readiness check.
- **Exact argv** — every flag in the Part 1 table, confirmed against `--help`
  and a real headless run that writes a file in a non-git workspace.
- **Where things land** — the path `agentInstructions` is written to, that the
  agent loads it with the wiki as its workspace, and the native trace directory.
- **sbx minimum** — 0.43 or 0.45.
- **Captured protocol** — a success, a terminal failure (and how it was
  provoked, for stage 2.5), a malformed line and plain stderr, committed under
  `tests/fixtures/protocols/claude/`.

*Checkpoint:* each question has a recorded answer, folded back into this plan's
Part 1 and Part 2 tables. The only code change is the fixtures, so the offline
gate stays green.

*Findings (run 2026-09-26, sbx 0.45.0, Claude Code 2.1.280; raw answers in the
untracked `spikes/claude/out/`, fixtures in `tests/fixtures/protocols/claude/`):*

- **Detached create works.** With the host's `anthropic` secret set by OAuth
  (a `/login` inside a Claude sandbox — `sbx secret set anthropic --oauth` is
  refused, see the open gates below; an API key via `sbx secret set anthropic`
  is the alternative), `sbx run --detached` finished in 5 s with no prompt and
  the sandbox came up logged in (`claude auth status`: `loggedIn: true`,
  `authMethod: claude.ai`; `~/.claude/.credentials.json` present; no
  `ANTHROPIC_*` variable set). No stop-and-replan. **Not observed:** a create
  with *no* secret, because one was already configured; the not-ready path
  stays covered by the fake-sbx lifecycle tests, and the remedy is "set the
  secret, then `--fresh`" because sbx injects credentials at create time.
- **Argv.** The planned command wrote its file in a non-git workspace from a
  plain `sbx exec` (exit 0; the file appeared on the host). Every flag exists
  in `claude --help` (2.1.280) except `--max-turns`, which is accepted but
  undocumented. `--strict-mcp-config` added — see Part 1.
- **Where things land.** sbx writes `CLAUDE.md` (≈17 KB: the parent's own
  sandbox text plus the kit's `agentInstructions`) into the workspace's parent,
  next to `md/` and `SPEC.md`, and Claude loads it from there: asked for the
  marker line, it quoted it and named `CLAUDE.md`. Outside the wiki, so never
  part of the output. Pi's kit does the same (`work/AGENTS.md`). The parent's
  part of that file was not captured; stage 2.3 reads it (`sbx exec … cat
  ../CLAUDE.md`) for anything that contradicts the OKF rules.
- **Traces** are written to `~/.claude/projects/<cwd with / as ->/<session>.jsonl`,
  so the kit binds `~/.claude/projects` as planned.
- **Parent image:** `docker/sandbox-templates:claude-code-docker`, Ubuntu 26.04,
  `claude` at `~/.local/bin`, which is on a plain `sbx exec` PATH. It has `jq`,
  `curl`, `python3`, `uv`, `node`, `npm`, `rg` and `git`, but not `tree`,
  `shellcheck` or `fdfind`, so the kit keeps kits/pi's apt step. `~/.claude/`
  already holds the parent's `settings.json` and a `skills/` directory with 18
  bundled skills; stage 2.4 checks that the kit's skills appear beside them
  (the `skills` list in a turn's `system/init` event).
- **Network:** `mqlang.org` and `context7.com` were blocked; npm, PyPI,
  GitHub, the Ubuntu mirrors and Docker's apt repo were reachable. That host
  may carry global `sbx policy` allow rules from other projects, so the kit
  still lists every host kits/pi does (minus `openrouter.ai`, `pi.dev` and
  `context7.com`) rather than relying on them.
- **Protocol** (for stage 2.2): one JSON object per line. `system/init` first;
  `assistant` events carry `message.content` blocks of type `text`, `thinking`
  (often an empty string) and `tool_use` (`name`, `input`) — one `tool_use`
  block is one tool call; `user` events carry `tool_result` blocks whose
  `is_error` is per call, not terminal; `system` subtypes `commands_changed`
  and `thinking_tokens`, and `rate_limit_event`, are noise. The last event is
  `result`, and **`is_error` is the failure signal**: an unknown model gives
  `subtype: success` with `is_error: true`, `terminal_reason: api_error` and
  the reason in `result`; `--max-turns` gives `subtype: error_max_turns`,
  `is_error: true`, `result` absent and the reason in `errors`. Both exited 1.
  stderr carries plain-text lines such as
  `[claude-code:unrecognized_model] {…}`.
- **Stage 2.4 sandbox check (2026-09-26):** `make test-sandbox` passed for
  both agents. In `md2okf-claude` the parent's part of `../CLAUDE.md` is the
  generic Docker Sandbox text (environment persistence, network-policy
  remedies, git authentication and pushing, workspace modes), with md2okf's
  text after it; nothing there conflicts with the OKF contract once md2okf's
  precedence line applies (the wiki is not a git repository). One compile-argv
  turn's `system/init` event reported `mcp_servers: []` (so
  `--strict-mcp-config` removes the parent's gateway and the account's
  connectors) and the six md2okf skills first in `skills`.
- **Stage 2.5's streamed failure** can be provoked with `--max-turns 1` on a
  task needing several tool calls: cheap, and it fails inside the stream after
  real tool calls, which is the case the driver's failure rule exists for.

**Stage 2.2 — `protocols/claude.py`**, offline and unregistered.
*Checkpoint:* offline gate; fixture tests: tool calls counted, `display` in the
same style as Pi's, the terminal failure fixture yields `failure`, and the
malformed line and stderr reach the diagnostic tail.

**Stage 2.3 — Author `kits/claude/`** (Part 2): `spec.yaml`, the `CLAUDE.md`
instructions (the full contract, adapted per the porting audit list), skills,
check script and wrapper shim. Not registered.
*Checkpoint:* offline gate — `make validate` picks the kit up through the glob,
`test_kits.py` passes for claude (producer, no `.pi/` paths, referenced paths
exist, helpers byte-identical), and a fingerprint test covers `.claude/`. A
human review of the instruction diff against Pi's: this is the stage to read
most closely, because it sets the pattern for Codex.

**Stage 2.4 — Register for checkout use; first sandbox.** Add `claude` to
`AGENTS` (argv, prompt, credential probe, sbx minimum, protocol), to the
Makefile `AGENTS` list, and add `test-sandbox-guest-claude.sh`. *As built:* the
force-include moved here from stage 2.6, because `tests/test_package.py` holds
every registered kit to being in the wheel and a registered agent that fails
from an installed wheel is a trap; only the full docs wait for 2.6. The kit is
named `md2okf-claude` (not `claude`, the parent it extends), and both agents'
credential remedies end with `sbx rm --force md2okf-<agent>`.
*Checkpoint:* offline gate plus argv and prompt tests. Dry-run diff for
`MD2OKF_AGENT=claude`: `md2okf-claude`, `kits/claude`, the exact argv. Sandbox
check (claude): the toolchain is present, `CLAUDE.md` names producer `claude`,
the wrapper runs, and a trace written through `~/.claude/projects` appears
under the host's `sessions/`. `MD2OKF_AGENT=claude uv run md2okf --agent`
opens Claude; `--shell` opens bash. Live smoke (pi) still passes.

**Stage 2.5 — First real compiles.**
*Checkpoint:* live smoke (claude). Then the failure case provoked in the spike
gives a `CompileError` carrying the structured failure, with nothing mirrored
to `-o` (never provoked by removing the vendor credential). Finally, one run on
`md/GoogleStyleGuide-abridged.md`, compared with a Pi run of the same document:
`check-okf.sh` passes, and the page count and structure are comparable. If the
instructions need tuning, edit and rerun; the automatic rebuild on each edit
also re-confirms stage 0.2.

**Stage 2.6 — Release Claude.** Force-include `kits/claude`; `test_package.py`
asserts its hidden files are in the wheel (the permanent test for stage 0.3);
README (Environment table, credential prerequisite from the spike, sbx
minimum), `cli.py` epilog, `kits/claude/README.md`, CHANGELOG.
*Checkpoint:* offline gate; `make test-clis` and `make test-web2md`; an
installed-wheel check — `MD2OKF_AGENT=claude uvx --from dist/md2okf-*.whl
md2okf --dry-run tests/fixtures/smoke.md` resolves the kit from the installed
layout; live smoke (claude) and live smoke (pi).

*Milestone 2 exit:* merge; release.

*Stages 2.6 and 3.6, as built (2026-09-26):* the force-includes and
`test_package.py` coverage landed with registration (2.4, 3.4). The docs landed
together for both agents: a README "Choosing an agent" section (per-agent
sandbox, sbx minimum and host credential, the create-time injection rule, and
the per-agent `generated.by`), Requirements, Quickstart, Session state, How it
works and Troubleshooting made agent-neutral; `kits/claude/README.md` and
`kits/codex/README.md`; CONTRIBUTING, AGENTS.md, the package description and
the CHANGELOG. The installed-wheel check resolves `kits/claude` and
`kits/codex` from site-packages. (A note for re-running it by hand: `uv tool
run --from <wheel>` caches by path, so re-running a rebuilt wheel of the same
version from the same path can test the old one even with `--refresh`;
`--no-cache` or a fresh path avoids it. `make dist` builds into a fresh
`mktemp` directory each time, so it is not affected.) `make test-sandbox
AGENT=codex` passed on the host (including the MCP-gateway override and
`codex login status`), so Milestones 2 and 3 are complete.

### Milestone 3 — Codex

The same six stages, with these Codex-specific checkpoint items:

- **3.1 spike:** the `openai` first-use approval is the known risk and the most
  likely "stop and replan"; confirm that `--skip-git-repo-check` is both
  needed and sufficient; confirm skills load from `~/.agents/skills` and that
  `$compile-okf` activates the skill.
- **3.4 sandbox check:** traces written through `~/.codex/sessions` land in the
  host's `sessions/`.

*Milestone 3 exit:* the stage 2.6 checkpoint for codex, plus live smoke for
claude and pi.

*Stage 3.1 findings (run 2026-09-26, sbx 0.45.0, `codex-cli` 0.149.1; raw
answers in the untracked `spikes/codex/out/`, fixtures in
`tests/fixtures/protocols/codex/`):*

- **Detached create works** — 5 s, no approval prompt, with the host's `openai`
  secret set by OAuth. The parent writes `~/.codex/config.toml` with
  `approval_policy = "never"`, `sandbox_mode = "danger-full-access"`, a
  `sandboxd` model provider (the credential goes through sbx; `OPENAI_API_KEY`
  is unset, `SBX_CRED_OPENAI_MODE=oauth`) and an `mcp-gateway` MCP server.
  `codex login status` says "Logged in using an API key" (the injected
  placeholder), so it is the credential probe candidate.
- **Argv:** the planned command wrote its file from a plain `sbx exec` in the
  non-git workspace. Neither `--skip-git-repo-check` nor
  `--dangerously-bypass-approvals-and-sandbox` turned out to be load-bearing
  (each control run wrote too) — the parent's config already allows it. Both
  stay, for the same reason as Claude's `--permission-mode`.
  `-c 'web_search="disabled"'` is accepted. Every run prints
  `Reading additional input from stdin...` on stderr.
- **Skills:** `$md2okf-spike-probe` activated a skill shipped in
  `~/.agents/skills` at once, so Codex's compile prompt uses `$compile-okf`, as
  the Part 1 table says. Naming the file path also worked, but only after the
  model guessed `~` as `/Users/lars` first.
- **BLOCKER — instructions are not read.** sbx writes `agentInstructions` to
  `<workspace>/../AGENTS.md`, but asked for the marker line, Codex answered
  `NONE`: it reads `AGENTS.md` from a project root (git) down to the working
  directory, and the wiki is not a repository. Stage 3.1b probes the
  alternatives side by side: `~/.codex/AGENTS.md` (Codex's global
  instructions) and `-c 'project_root_markers=["SPEC.md"]'` (making the
  workspace's parent the project root). It also checks whether the gateway
  can be switched off for a compile. Codex's kit waits for that answer.
- **Model:** asked, Codex answered only "GPT-5"; `config.toml` sets no model.
  Provenance can be `codex/gpt-5` unless a turn event carries a precise ID.
- **Traces:** `~/.codex/sessions/<yyyy>/<mm>/<dd>/rollout-*.jsonl`, as planned.
- **Protocol** (for stage 3.2): `thread.started`, `turn.started`; tool work as
  `item.started`/`item.completed` with `item.type` `file_change` or
  `command_execution`; prose as `agent_message` items; `turn.completed`
  (usage) at the end. A failure is `turn.failed` with `error.message`, preceded
  by a top-level `error` event; an `error` *item* at the start of the failing
  run was only a warning, so only `turn.failed` is terminal. Exit 1.
- **Image and network** as for Claude: no `tree`, `shellcheck`, `fdfind`;
  `mqlang.org` blocked.

*Stage 3.1b findings (same day, `spikes/codex/followup.sh`):*

- **Instructions: resolved.** A kit-shipped `files/home/.codex/AGENTS.md`
  survives the parent's setup (`CODEX_HOME=/home/agent/.codex`) and Codex reads
  it by default. With `-c 'project_root_markers=["SPEC.md"]'` Codex reads
  `../AGENTS.md` too, but the global file needs no flag, so the kit ships the
  whole OKF contract there and declares no `agentInstructions`.
- **MCP gateway:** `-c 'mcp_servers={}'` leaves it enabled;
  `-c 'mcp_servers.mcp-gateway.enabled=false'` disables it (`codex mcp list`),
  and a turn with the override runs. Compile turns pass it.

*As built (stages 3.2–3.4):* `protocols/codex.py` counts each tool item once
(start, or completion when the start was never seen), treats only
`turn.failed` as terminal and hides the stdin notice. `kits/codex` (named
`md2okf-codex`) carries `~/.codex/AGENTS.md`, the six skills under
`~/.agents/skills` and the shared helpers, and relocates `~/.codex/sessions`.
`MD2OKF_AGENT=codex` is registered and packaged, prompt `$compile-okf …`,
credential probe `codex login status`. Web search is left as the parent has
it, like Claude's web tools — see Deferred.

*Stage 3.5 (2026-09-26):* `--agent` opens Codex (`gpt-5.6-sol`, "YOLO mode").
The smoke compile converged in 2 iterations like Pi's and Claude's, passed the
gate (one `missing-xref` advice), split the document into five topic pages,
signed `codex/gpt-5.6`, and left no agent files. The forced failure
(`-m` unknown model) gave `codex exited 1: turn.failed: …` with nothing
mirrored; it also showed Codex's stdin notice leaking into the message, now
fixed (the diagnostic tail keeps only lines the protocol shows).
`make test-sandbox AGENT=codex` passed later the same day.

*Open live gates (from the code review, 2026-09-26).* The implementation of
Milestones 0–3 is complete; two live checks the stages ask for have no record
yet, and neither implies a code change unless it fails:

- **Detached create without the vendor secret** (stage 2.1, and 3.1 by
  inheritance). Both spikes created with the secret already set. The fake-sbx
  tests prove the remedy only once `sbx run --detached` finishes; create runs
  with stdin `/dev/null` and no timeout, so a parent that prompts should fail
  fast, but one that waits on anything else would hang. Service secrets are
  global, so the check means removing the secret, running
  `MD2OKF_AGENT=<agent> uv run python -m md2okf.sandbox` against a removed
  sandbox, and restoring the secret. Pass: exit 2 with the agent's remedy.
- **The full-document comparison** (stages 2.5 and 3.5): compile
  `md/GoogleStyleGuide-abridged.md` with pi, claude and codex; record
  iterations, page count, `generated.by` and the `check-okf.sh` outcome here.
  Only the smoke fixture has been compiled with Claude and Codex.

*Gate 1, claude (2026-09-26): passed.* With no `anthropic` secret, the
detached create finished and `python -m md2okf.sandbox` exited 2 with the
remedy. Restoring the secret showed the remedy itself was wrong:
`sbx secret set anthropic --oauth` is refused ("`--oauth`: openai/global
only"; "sign in from inside the Claude sandbox"), so the Claude remedy and docs
now say `sbx run claude`, then `/login`. Confirmed: a `/login` inside a Claude
sandbox brought `sbx secret ls` back to `anthropic (oauth configured)`.

*Gate 1, codex (2026-09-26): passed.* With no `openai` secret, the detached
create finished and `python -m md2okf.sandbox` exited 2 with the remedy, whose
`sbx secret set openai --oauth` then restored the secret from the host. Gate 1
is closed for both agents; the full-document comparison remains open.

### Milestone 4 — Deferred items (optional)

Each item under "Deferred" becomes its own stage, gated by the offline gate
plus the live smoke of every agent it touches.

## Deferred (after all three compile paths are stable)

- **Vendor network-block hooks** for Claude (`PostToolUse` managed settings)
  and Codex (`requirements.toml`), ported from sbxagent. The sandbox allowlist
  already enforces egress; the hooks are asymmetric (none for Pi)
  and add failure modes to the compile path.
- **MCP servers in the new kits** — Context7 and, if ever wanted, GitHub — as an
  interactive-agent (`--agent`) enhancement. Includes Codex's install-time
  `config.toml` append.
- **A shared instruction source** (template plus a sync script with a lint
  `--check`), once three working, checked-in instruction sets show which text is
  genuinely common and whether duplication is actually a maintenance problem.
- **Concurrent compilation across agents** — would need per-agent locks plus
  output locking for a shared `-o` directory.
- **Web tools during a compile.** Claude keeps its `WebSearch`/`WebFetch` tools
  and Codex its hosted `web_search` (which runs on OpenAI's side, outside the
  sandbox's network allowlist; `-c 'web_search="disabled"'` is accepted).
  Pi has none. Decide once, for every agent, whether a compile may search.
