# Observability for `make wiki` (Ralph loop + Pi runs)

## Context

Running Pi interactively via `scripts/pi.sh` (`sbx exec -it ... pi`) gives a
live TTY: you watch the agent think, call tools, and write pages. `make wiki`
→ `scripts/compile-okf.sh` gives none of that, and the cause is a single flag.

`scripts/compile-okf.sh:80` invokes `pi -p "${iteration_prompt}"`. Pi's **print
mode** (`-p`) is documented as a black box: it runs the whole agent loop
silently and prints only the final assistant text on completion. Everything
you normally watch — tool calls, file writes, lint runs, thinking — is
discarded. Layered on top, the Ralph loop added in this branch re-invokes Pi up
to `RALPH_MAX` times per document, so a long compile is now many silent
black-box runs in a row with only a hash comparison between them.

Upstream is aware of this gap: [earendil-works/pi#808](https://github.com/earendil-works/pi/issues/808)
("Make `pi -p` show what it's doing") proposed a `--stream` flag for print
mode. It is **closed with no comments and no implementation**, so there is no
`-p`-based streaming to wait for. The supported answer is a different mode.

**The fix**: Pi's [JSON mode](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/json.md)
(`--mode json`) streams *every* session event as JSON lines to stdout in
realtime — `tool_execution_start` with `toolName` and `args`, `message_update`
deltas, `turn_start`/`turn_end`, `agent_end`, plus cumulative `usage`. Piping
that through a small `jq` renderer restores a `pi.sh`-like live view, and
because it is a stream rather than a TTY it can also be captured to disk.

A second, independent loss: Pi writes a full JSONL session transcript per run,
but `compile-okf.sh:44` does `sbx rm --force` at the start of every compile, so
the previous run's transcripts are destroyed with the VM before you can read
them. Redirecting `--session-dir` into the mounted workspace fixes that.

**Intended outcome**: `make wiki` streams readable per-tool progress live,
keeps every transcript on the host, and stays scriptable via `QUIET=1`.

## Design decisions (confirmed with the user)

| Decision | Choice |
| --- | --- |
| Live view | `--mode json` piped through a `jq` renderer → readable lines |
| Transcripts | `--session-dir` into a gitignored host `logs/sessions/` |
| Ralph loop reporting | Just the hashes — keep loop output minimal |
| Verbosity | Verbose by default; `QUIET=1 make wiki` for one line per document |

## Implementation

### 1. Capture a real event stream first (do this before writing the filter)

The exact nested shapes of `args`, `result`, and `usage` are **not** fully
specified in the upstream docs, and the `jq` filter depends on them. Do not
write the filter from guesswork. Capture one real run and inspect it:

```bash
sbx exec md2okf -- pi --mode json \
  "Load the compile-okf skill: read ~/.pi/agent/skills/compile-okf/SKILL.md, then follow it to compile md/<small>.md into the OKF wiki under okf/." \
  </dev/null > /tmp/pi-events.jsonl
jq -r '.type' /tmp/pi-events.jsonl | sort | uniq -c
jq -c 'select(.type=="tool_execution_start")' /tmp/pi-events.jsonl | head
```

Keep the capture — it is the fixture for iterating on the renderer offline.

### 2. New file: `scripts/render-pi-events.sh`

A filter reading Pi's JSON event stream on stdin and writing the readable view
on stdout. Kept as its own script (not inline in the driver) so it is
shellchecked by `make lint` (`git ls-files -- '*.sh'`) and can be developed
offline against the step-1 capture: `scripts/render-pi-events.sh < /tmp/pi-events.jsonl`.

- Accept a `--quiet` flag: emit only the final assistant message plus the
  tool/token summary, giving the "one line per document" `QUIET=1` behaviour.
- Render, at minimum: `tool_execution_start` → `▸ <toolName>  <short arg>`;
  `message_end` → the assistant text; `tool_execution_end` with the error flag
  → `✖`; `agent_end` → `✔ N tools · N tokens` from cumulative `usage`.
- **Parse defensively.** Use `jq -R -r 'fromjson? // empty | …'` so any
  non-JSON line (a startup banner, a stray warning) is skipped rather than
  aborting the pipeline on a parse error. Consider also setting
  `"quietStartup": true` in `pi/files/home/.pi/agent/settings.json` to keep the
  stream clean.
- Truncate long tool `args` to one line — a `write` call carries a whole page
  and must not flood the terminal.

### 3. `scripts/compile-okf.sh`

- **Switch the invocation** at line 80 from `pi -p "${iteration_prompt}"` to
  `pi --mode json "${iteration_prompt}"` (the prompt is positional in JSON
  mode), piped into `scripts/render-pi-events.sh`.
- **Keep `</dev/null`.** The existing comment at lines 51-55 explains why it is
  required, and that reasoning (sbx hands the guest a pipe that never reaches
  EOF) is unchanged by the mode switch.
- **Mind `pipefail`.** The script runs `set -euo pipefail`, so a failing `pi`
  still aborts the run through the new pipe — preserving today's behaviour.
  Make sure the renderer itself always exits 0 on a well-formed stream.
- **Persist transcripts**: add `--session-dir logs/sessions` to the `pi` call.
  `sbx exec` runs with the VM workspace (the repo root) as its cwd — the
  invariant already documented at lines 47-49 and relied on for `md/<...>.md`
  paths — so a relative path lands in the mounted host tree. `mkdir -p
  logs/sessions` on the host before the loop.
- **Add a `QUIET` env var**, defaulting to unset (verbose). When set, pass
  `--quiet` through to the renderer. Document it in the header comment
  alongside the existing `RALPH_MAX` block (lines 10-11).
- **Loop reporting stays minimal** per the decision above: print the iteration
  banner as today, plus the old → new root hash each iteration, and nothing
  more. Do not add merkle diffs or `sizeokf` deltas.

### 4. Supporting changes

- `.gitignore` — add `logs/`. Follows the existing `okf/` output-dir precedent.
- `README.md` — the "Run it" section (lines 65-69) describes the Ralph loop;
  add that the compile now streams live progress and where transcripts land,
  and document `QUIET=1`.
- `AGENTS.md` — the commands block near line 107 mentions the Ralph loop; note
  `QUIET` next to `RALPH_MAX`.

## Explicitly out of scope

The three other findings from the earlier Ralph loop review are unrelated to
observability and are **not** addressed here: convergence having no positive
success signal, no per-invocation timeout, and the unrestored `shopt -s
nullglob`. The transcripts this change preserves do, however, make the first of
those far easier to diagnose after the fact.

## Verification

1. `make lint` — covers the new `scripts/render-pi-events.sh` via shellcheck
   and the docs edits via markdownlint/cspell.
2. `./scripts/render-pi-events.sh < /tmp/pi-events.jsonl` — renderer output is
   correct against the step-1 capture, with no jq parse errors. Repeat with
   `--quiet`.
3. `make validate` — required by `AGENTS.md` for any change under `scripts/*.sh`.
4. End-to-end: `make wiki` on a small `md/` folder. Confirm live tool-by-tool
   output appears, that it resembles the `scripts/pi.sh` experience, and that a
   multi-iteration document shows each iteration's hash transition.
5. Confirm `logs/sessions/*.jsonl` exists on the **host** after the run and
   survives a second `make wiki` (which tears the sandbox down first). Spot-check
   one transcript renders: `pi --export logs/sessions/<file>.jsonl /tmp/out.html`.
6. `QUIET=1 make wiki` — output collapses to one line per document.
7. `git status` — `logs/` is ignored and nothing new is untracked.
