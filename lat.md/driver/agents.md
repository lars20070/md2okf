# Agents

Everything that differs between Pi, Claude Code and Codex lives on one `Agent` record and its event-stream parser, in [[src/md2okf/agents.py]] and [[src/md2okf/protocols]].

## Agent contract

[[src/md2okf/agents.py#Agent]] has eight fields: name, compile command line, interactive command line, first-turn prompt, credential check, event protocol, trace target and the workload its kit composes onto.

The generic modules, [[cli]], [[compile-loop]], [[workbench]] and [[sandbox]], never branch on an agent's name. The name also names the agent's kit (`kits/<name>`), its sandbox (`md2okf-<name>`) and its workbench. A new agent is therefore one new record, one protocol module and one kit.

## Registry

[[src/md2okf/agents.py#AGENTS]] holds the registered agents, [[src/md2okf/agents.py#resolve]] looks one up and [[src/md2okf/agents.py#from_env]] reads `MD2OKF_AGENT`, where unset or empty means Pi.

An unknown name is refused with exit 2, listing the valid ones. An agent is registered only once its kit ships, and the wheel gains one `force-include` line per registered kit at the same time (see [[development#Packaging]]).

## Trace target and workload

Every in-sandbox command line, compile turn or interactive session, starts with the agent itself, run by a plain `sbx exec`, which bypasses the kit's entrypoint.

Nothing per-process has to run first, because `trace_target` names the agent's native trace directory and the driver mounts the workbench's `sessions/` there (see [[lat.md/kits#Runtime]]). `workload_ref` is None for Pi, whose kit is the workload, and the pinned published workload for Claude Code and Codex, whose kits are mixins (see [[sandbox#Launch]]). The agent's own flags stay here in Python, where they are unit-tested.

## Compile turns run without MCP

A compile turn starts the agent with no MCP servers, because a compile uses none of them. Each agent spells this differently.

Pi gets `--no-mcp` and drops its `tool_search` loader. Claude Code gets `--strict-mcp-config` with no config, which excludes both the workload's gateway and any claude.ai connectors. Codex gets a `-c` override disabling the workload's gateway; an empty `mcp_servers` table was measured not to remove it. Interactive sessions keep MCP. Removing MCP tools does not remove GitHub access: a bound `github` secret still reaches `gh` and `git` through the shell.

## Workspace root rule

Every first-turn prompt ends with [[src/md2okf/agents.py#WORKSPACE_ROOT_RULE]], telling the agent it is already in the wiki and must never create an `okf/` child directory.

Agents told nothing created `okf/okf/`. The kits state the same rule in their instructions, and [[tests/test_kits.py]] checks it is there.

Each prompt names the agent's compile skill the way that agent activates it reliably: Pi and Claude Code are told to read the skill file, Codex uses `$compile-okf`.

## Credential checks

Each agent's credential check runs on every create and every reuse, so it must be local, unpaid and non-interactive: an environment sentinel or an auth-status command, never a model request.

Pi requires `OPENROUTER_API_KEY` to be the proxy-managed sentinel. Claude Code requires `claude auth status` to report it is logged in, and Codex requires `codex login status` to succeed. Every remedy ends with `_rebuild_hint`, because sbx injects credentials only when a sandbox is created: a secret set afterwards never reaches the existing sandbox, so it must be removed and rebuilt.

## Event record

Each protocol module turns one agent's NDJSON stream into [[src/md2okf/protocols/__init__.py#Event]] records, so the Ralph loop never parses agent output itself.

An event carries the raw line, what `-v` should display (or nothing), whether the line starts a tool call, and the protocol's own failure verdict. The `EventProtocol` contract is one `process` function. `failure` is authoritative like a nonzero exit, because an agent can report a terminal error and still exit 0 (see [[compile-loop#Turn verdict]]). Tool calls display as the tool name and arguments, cut to the same width for every agent.

## Per-agent verdicts

Each parser was derived from captured output, kept as fixtures in [[tests/fixtures/protocols]], not from documentation.

- Pi never reports a failure from the stream: no captured output has shown an event that means "this turn failed", so Pi's failures rest on its exit code.
- Claude Code: the final `result` event's `is_error` is the verdict, and `subtype` is ignored, because an unknown model ends with `subtype: success` and `is_error: true`.
- Codex: `turn.failed` is the one terminal failure, while earlier `error` events and items are only shown as warnings. A tool item is counted once per item id, whether its start or only its completion was seen. The `Reading additional input from stdin...` notice Codex prints on every non-terminal stdin is hidden as noise.
