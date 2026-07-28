# Observable `make wiki-sandbox`: raw event log + a Python trace viewer

## Context

A `make wiki-sandbox` run is a black box. Pi's print mode subscribes to the
session event stream and **discards every event**, printing only the text blocks
of the *final* assistant message ([print-mode.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/modes/print-mode.ts)) —
so narration like "Now let me write chapters 7-10 and the glossary" is produced
during the run but never reaches the terminal. That blindness is what made the
stdin stall look identical to a working run, and it is why progress on a 15-minute
compile can only be inferred from files appearing in `okf/`.

`--verbose` does not help (the docs define it as forced verbose *startup*, i.e.
the banner), and Pi deliberately ships no CLI-level tracing hook — its
[observability design](https://github.com/earendil-works/pi/blob/main/packages/agent/docs/observability.md)
exposes `subscribePiObservability()` to library embedders only, with OTel left to
third-party wrappers. The supported route for a CLI run is `--mode json`, which
streams every session event as JSON lines to stdout.

Outcome: the driver writes the raw event stream to a log file, and a separate
viewer renders it — live in a second terminal during a run, or after the fact
against any saved log.

This supersedes [.claude/plans/observe-pi-agent-sandbox.md](.claude/plans/observe-pi-agent-sandbox.md),
an earlier unimplemented sketch of the same idea. Its jq filter is not used, but
its findings are, and several of its "unverified" notes are now settled (below).

## Decisions

- The driver writes **raw JSONL only**; the compile terminal stays quiet apart
  from a per-document heading naming the log file.
- The viewer shows **narration + tool calls + per-turn usage**, plus compaction
  and auto-retry warnings.
- The viewer is **Python** (covered by `ruff check .` in `make lint`).
- **Sandbox only** — `scripts/compile-wiki-container.sh` keeps its current
  behaviour.

## What is already verified

- `--mode json` is dispatched at [main.ts:113](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/main.ts#L113)
  *before* the print check, so it is one-shot non-interactive on its own. Line
  116 also shows Pi selects print mode automatically when stdout is not a TTY.
- Each event is written with its own `write()`, so a redirect to a file grows in
  real time — `--follow` works.
- Real `usage` shape, read from a live session in the VM:
  `{input, output, cacheRead, cacheWrite, reasoning, totalTokens, cost:{input, output, cacheRead, cacheWrite, total}}`.
  Note `cost` is an **object** — the earlier plan's `\(.cost)` would have printed
  `{...}`; use `cost.total`.
- Assistant and toolResult messages carry a `timestamp` (epoch ms); bare events
  such as `tool_execution_start` do not.
- `jq` 1.7.1 is present at `/usr/bin/jq`, but is not used given the Python choice.

Still unverified, and the reason the raw log is kept as ground truth: the exact
shape of `tool_execution_end.result`. The session file only exposes toolResult
*messages* (`{role, toolCallId, toolName, content:[{type, text}], isError, timestamp}`),
which is probably but not certainly the same object. The viewer must use
fallbacks, and the smoke test below settles it.

## Changes

### 1. `scripts/compile-wiki-sandbox.sh`

Loop body becomes roughly:

```bash
log_dir="logs"
mkdir -p "${log_dir}"
stamp="$(date +%Y%m%d-%H%M%S)"

for document in "${markdown_folder}"/*.md; do
	slug="$(basename "${document}" .md)"
	log="${log_dir}/${slug}-${stamp}.jsonl"
	echo "Compiling document ${document}"
	echo "  events → ${log}   (watch with: make wiki-watch)"
	sbx exec "${kit_name}" -- pi \
		--mode json \
		--name "okf: ${slug}" \
		-p "Load the compile-wiki skill: read ~/.pi/agent/skills/compile-wiki/SKILL.md, then follow it to compile ${document} into the OKF wiki under okf/." \
		</dev/null >"${log}" \
		|| { echo "Pi failed on ${document}; last events:" >&2; \
		     python3 -u scripts/pi-trace.py --tail 20 "${log}" >&2; exit 1; }
done
```

Points that matter:

- `</dev/null` **stays** — it is what fixed the stdin stall.
- `-p` is redundant under `--mode json` but harmless; keeping it means the script
  still behaves if the mode flag is ever removed.
- `--name "okf: <slug>"` labels the session so `sbx exec -it pi-kit -- pi -r`
  finds it later in the picker.
- Redirect, not `tee`: with "raw only" there is nothing to render inline, and a
  plain `>` avoids `pipefail` interactions.

### 2. `scripts/pi-trace.py` (new)

`python3 -u scripts/pi-trace.py [FILE] [--follow] [--tail N]`

- `FILE` defaults to the newest `logs/*.jsonl`; `-` reads stdin. `--follow` tails
  a growing file, waiting up to ~60s for it to appear so it can be started before
  the driver.
- Standard library only. One `handle_<event_type>` mapping, unknown events
  ignored so a Pi upgrade cannot crash the viewer.

| Event | Rendered as |
| --- | --- |
| `session` | `── session <id8>  cwd=…` header |
| `message_end` (assistant) | `💬 ` + text blocks, wrapped and indented |
| `tool_execution_start` | `→ <tool>  <key arg>` — `command` / `path` / `file_path` / `pattern` / `query`, else compact JSON, clipped to ~100 chars |
| `tool_execution_end` | `  ✓/✗ <tool>  <result summary>` from `.result.output // .result.content[].text // .result`, clipped to ~160 |
| `turn_end` | `── turn  in=… out=… cost=$…` from `message.usage`, using `cost.total` |
| `compaction_start` / `auto_retry_start` | `⚠ …` with reason / attempt |
| `agent_end` | final summary: turns, tool calls, total tokens, total cost, elapsed |

Timestamps: use `message.timestamp` when the event carries a message; otherwise
wall clock in `--follow` mode, and carry forward the last known message timestamp
when replaying a saved log. Narration is *not* aggressively clipped — it is the
point of the exercise.

### 3. `Makefile`

Add a `wiki-watch` target (`python3 -u scripts/pi-trace.py --follow`), extend
`.PHONY`, and mention it in the header comment block next to `wiki-sandbox`.

### 4. `.gitignore`

Add `logs/`.

### 5. `README.md`

Short subsection under the sandbox runtime: run `make wiki-sandbox` in one
terminal and `make wiki-watch` in another; logs are per-document and disposable;
`pi -r` inside the sandbox reopens a session in the full TUI for a rich
post-mortem.

## Verification

1. **Smoke-test the event schema first** — this settles `tool_execution_end`
   before the viewer is finished:

   ```bash
   sbx exec pi-kit -- pi --mode json --no-session \
     "Run 'ls okf' with the bash tool, then reply DONE." </dev/null > /tmp/smoke.jsonl
   echo "exit=$?"
   jq -r '.type' /tmp/smoke.jsonl | sort | uniq -c
   jq 'select(.type=="tool_execution_end") | .result' /tmp/smoke.jsonl | head -20
   ```

   Confirm the result keys, and whether a failed run exits non-zero in json mode
   (the `||` branch in the driver depends on it; if json mode always exits 0,
   detect failure by scanning the log for an error `stopReason` instead).

2. `make lint` — ruff lints the new `scripts/pi-trace.py`, shellcheck the driver.
   `make validate` — required by AGENTS.md for any change under `scripts/`.
3. **Replay** an existing log end-to-end:
   `python3 -u scripts/pi-trace.py logs/<file>.jsonl | head -40`.
4. **Live**: `make wiki-sandbox` in one terminal, `make wiki-watch` in another.
   Confirm narration appears within a second or two of the model emitting it (not
   in a burst at the end), that the log grows, and that `✗` shows up for the
   failed-`edit` case that occurs naturally on long chapters.
5. **Interrupt path**: Ctrl-C a run and confirm the partial log still renders and
   the viewer exits cleanly rather than tracebacking on a truncated last line.
