# Claude Code stream fixtures

Captured output of `claude -p --output-format stream-json --verbose`, the
format `md2okf.protocols.claude` parses. Real output, not hand-written: the
parser is derived from these, never from documentation.

Captured on 2026-09-26 by `spikes/claude/spike.sh` (stage 2.1 of the
generalise-agent-framework plan), with Claude Code 2.1.280 in a sandbox built
on the sbx 0.45.0 `claude` parent kit, logged in through the host's
`anthropic` OAuth secret. Each run was a plain `sbx exec` in a non-git
workspace shaped like md2okf's workbench.

| File | Run | Exit | What it shows |
| --- | --- | --- | --- |
| `success-write.jsonl` | asked to write one file, with `--permission-mode bypassPermissions` | 0 | a `tool_use` block (`Write`), its `tool_result`, and a `result` with `is_error: false` |
| `success-no-tool-calls.jsonl` | asked to answer without tools | 0 | a turn with text only: exit 0, but no tool call |
| `error-unknown-model.jsonl` | `--model` naming a model that does not exist | 1 | a `result` whose `subtype` is still `success` but whose `is_error` is `true` (`terminal_reason: api_error`) |
| `error-unknown-model.stderr` | the same run's stderr | | one plain-text line, not JSON |
| `error-max-turns.jsonl` | `--max-turns 1` on a task needing more | 1 | a `result` with `subtype: error_max_turns`, `is_error: true` and an `errors` list |

`is_error` is the field to trust: `subtype` says `success` for the unknown
model. A malformed line is made in the tests by cutting a captured line short.
The driver merges stdout and stderr into one stream, so tests that need both
combine the `.jsonl` and `.stderr` files.

## Redactions

Only values that describe the account rather than the protocol were changed;
every event and field is otherwise as captured.

- The home path `/Users/lars/` is `/Users/user/`, in paths and in the escaped
  project directory name.
- In `system`/`init`, the claude.ai account connectors are removed from
  `mcp_servers` and their tools from `tools`.
- In `rate_limit_event`, `rate_limit_info` is reduced to
  `{"status": "allowed"}`.
