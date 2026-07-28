# Making `make wiki-sandbox` observable

Recommendation for seeing what the Pi agent actually does during a headless
`sbx exec … pi -p …` run.

## Why you currently see nothing

Pi's print-mode source ([`print-mode.ts`](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/modes/print-mode.ts))
shows that with `-p`, Pi subscribes to the session event stream and **discards
every event**, then prints only the text blocks of the final assistant message:

```ts
unsubscribe = session.subscribe((event) => {
    if (mode === "json") { writeRawStdout(`${JSON.stringify(event)}\n`); }   // ← nothing happens in text mode
});
```

So the blindness isn't `sbx`'s fault — it's the mode. `--verbose` won't help
either; the docs define it as "force verbose *startup*" (banner/config echo),
not a tool trace.

## Options considered

| Option | Verdict |
| --- | --- |
| `--mode json` — every event as JSON lines on stdout | **Best.** Live, structured, no VM changes |
| `--mode rpc` — bidirectional protocol over stdin/stdout | Built for embedding Pi in a custom UI; overkill here |
| Post-hoc session inspection (`pi -r`, `/export`, `pi --export s.jsonl out.html`) | Excellent *complement*, but not live |
| A custom Pi extension that subscribes to events | Most flexible, most work — `--mode json` already gives the same event objects |
| `sbx exec -it … pi` interactively | The manual route; doesn't fix `make wiki-sandbox` |

## Recommendation: `--mode json`, formatted on the host, tee'd to a log

`--mode json` is dispatched in [`main.ts:113`](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/main.ts#L113)
*before* the print check, so it is already one-shot non-interactive — `-p` is not
needed alongside it. Each event is written with its own `write()` (a promise
chain, no batching), so it streams in real time through the `sbx exec` pipe.

You get `tool_execution_start` / `_end` (every bash command, every file write,
and whether it errored), `message_end`, `turn_end` with token usage, plus
`compaction_start` and `auto_retry_start` — exactly the events that silently eat
a long run.

Three edits:

### 1. `scripts/pi-trace.jq` (new)

Turns the event stream into a readable trace:

```jq
def clock: (now | localtime | strftime("%H:%M:%S"));
def clip($n): tostring | gsub("\\s+"; " ") | if (length > $n) then .[0:$n] + "…" else . end;
def tool_args: . as $a
  | ($a.command // $a.path // $a.file_path // $a.pattern // $a.query // ($a | tojson)) | clip(100);
def assistant_text: [.content[]? | select(.type == "text") | .text] | join("");

if   .type == "session"              then "\(clock) ── session \(.id[0:8]) cwd=\(.cwd)"
elif .type == "tool_execution_start" then "\(clock) → \(.toolName)  \(.args | tool_args)"
elif .type == "tool_execution_end"   then "\(clock)   \(if .isError then "✗" else "✓" end) \(.toolName)  \((.result.output // .result.content // .result) | clip(160))"
elif .type == "message_end" and .message.role == "assistant" then
  (.message | assistant_text) as $t | if ($t|length) > 0 then "\(clock) 💬 \($t | clip(600))" else empty end
elif .type == "turn_end"             then (.message.usage // {}) as $u
  | "\(clock) ── turn end  in=\($u.input // "?") out=\($u.output // "?") cost=\($u.cost // "?")"
elif .type == "compaction_start"     then "\(clock) ⚠ compacting context (\(.reason))"
elif .type == "auto_retry_start"     then "\(clock) ⚠ retry \(.attempt)/\(.maxAttempts): \(.errorMessage | clip(120))"
elif .type == "agent_end"            then "\(clock) ── agent end"
else empty end
```

### 2. `scripts/compile-wiki-sandbox.sh` (lines 42–46)

Replace the loop body:

```bash
log_dir="logs"
mkdir -p "${log_dir}"

for document in "${markdown_folder}"/*.md; do
	slug="$(basename "${document}" .md)"
	echo "Compiling document ${document}  (raw events: ${log_dir}/${slug}.jsonl)"
	sbx exec "${kit_name}" -- pi \
		--mode json \
		--name "okf: ${slug}" \
		"Read ${document} carefully. Then create or update the OKF wiki under okf/ following your instructions." \
		| tee "${log_dir}/${slug}.jsonl" \
		| jq -r --unbuffered -f scripts/pi-trace.jq
done
```

`--unbuffered` matters — without it jq block-buffers into the terminal and you
are back to staring at nothing. `pipefail` is already set, so a Pi failure still
aborts the loop. `--name` labels the session so the picker below is navigable.

### 3. `.gitignore`

Add `logs/`.

### Sample output

Rendered against a synthetic stream built from the documented schema:

```text
17:28:19 ── session 3f2a9b10 cwd=/workspace
17:28:19 → bash  cat SPEC.md
17:28:19   ✓ bash  # OKF Specification Version: 1.4 lots and lots of text that goes on…
17:28:19 → write  okf/index.md
17:28:19   ✓ write  wrote 3 lines
17:28:19   ✗ read  ENOENT: no such file
17:28:19 💬 I read SPEC.md (v1.4) and updated okf/index.md accordingly.
17:28:19 ── turn end  in=12045 out=842 cost=0.0123
```

The formatter was tested against that synthetic file, **not** a live run — the
exact key names inside `result` and `usage` may differ slightly, which is why
every field has a `//` fallback and the raw `.jsonl` is kept as ground truth.

## Free complement: post-mortem in the TUI

The script leaves the sandbox running detached, and sessions persist in
`~/.pi/agent/sessions/` inside the VM. So after a bad run:

```bash
sbx exec -it pi-kit -- pi -r      # session picker → open the run in the full TUI
                                  # then /tree to walk it, /export report.html
```

That gives the rich rendering (diffs, collapsible tool output) without re-running
anything.

## Two notes

- `scripts/compile-wiki-container.sh` (lines 53–57) has the identical blind
  spot. Per `AGENTS.md` the runtimes are deliberately independent, so it needs
  the same edit applied by hand — the only difference is that `-xt bash` stays
  and there is no `sbx exec` prefix.
- Writing session files straight onto the host tree via
  `--session-dir logs/sessions` was considered (the workspace is mounted rw, so
  they would land in the working copy for `tail -f` and host-side `pi --export`).
  Left out because how Pi resolves a *relative* `--session-dir` against the VM
  cwd is unverified. Worth a one-off test if the HTML transcripts should land on
  the host automatically.

## Sources

- [json.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/json.md)
- [usage.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/usage.md)
- [sessions.md](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/sessions.md)
- [print-mode.ts](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/src/modes/print-mode.ts)
