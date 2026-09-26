# Codex stream fixtures

Captured output of `codex exec --json`, the format `md2okf.protocols.codex`
will parse. Real output, not hand-written: the parser is derived from these,
never from documentation.

Captured on 2026-09-26 by `spikes/codex/spike.sh` (stage 3.1 of the
generalise-agent-framework plan), with `codex-cli 0.149.1` in a sandbox built
on the sbx 0.45.0 `codex` parent kit, logged in through the host's `openai`
OAuth secret. Each run was a plain `sbx exec` in a non-git workspace shaped
like md2okf's workbench, with stdin closed.

| File | Run | Exit | What it shows |
| --- | --- | --- | --- |
| `success-write.jsonl` | asked to write one file | 0 | a `file_change` item (`item.started`, then `item.completed`), agent messages, and `turn.completed` |
| `success-commands.jsonl` | asked to read a skill file by path | 0 | two `command_execution` items, each started and completed |
| `error-unknown-model.jsonl` | `-m` naming a model that does not exist | 1 | a non-terminal `error` *item* (a model-metadata warning), then a top-level `error` event and `turn.failed` carrying the reason |
| `stderr.txt` | every run's stderr | | one plain-text line, `Reading additional input from stdin...`, printed whenever stdin is not a terminal |

Two things to note for the parser: the `error` item that opens the failing run
is only a warning (the turn goes on to start), so only `turn.failed` is
terminal; and the stderr line appears on every turn, so it is noise, not a
diagnostic.

## Redactions

Only the home path `/Users/lars/` was changed, to `/Users/user/`. Every event
and field is otherwise as captured.
