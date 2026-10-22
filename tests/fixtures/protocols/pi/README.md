# Pi stream fixtures

Captured output of `pi --mode json`, the format `md2okf.protocols.pi` parses.
Real output from the real Pi binary, not hand-written.

Captured on 2026-10-22 with Pi `1.4.0`, the binary in the image `kits/pi/spec.yaml`
pins (`docker.io/sbx/pi-image@sha256:134b48cf…a1d2d5`, linux/arm64), run
directly with `docker run` rather than in an `md2okf-pi` sandbox. The flags
were the compile's own, from `md2okf.agents.PI`, with stdin closed:

```bash
pi --mode json --no-mcp --tools -tool_search \
  "Run ls in the current directory, then reply with one word." </dev/null
```

The config was the kit's `settings.json` and `mcp.json`, with two changes:
`packages` was removed, so Context7 was not fetched, and the default model
pointed at a local provider. That provider was a scripted OpenAI-compatible
endpoint (`api: "openai-completions"`, as OpenRouter is) on `127.0.0.1` inside
the container. Its first reply streamed `reasoning_content` and one `bash`
tool call (`ls`); its second streamed the text `Done.`. So the **model's
replies are scripted**, but every line of the stream is what Pi 1.4.0 itself
emitted around them: the session header, the system and user messages,
per-token `message_update`s, the tool execution, `turn_end`, `agent_end` and
`agent_settled`. The `bash` call really ran, in a workspace holding one
`index.md`.

| File | Run | Exit | What it shows |
| --- | --- | --- | --- |
| `success-bash.jsonl` | one tool call, then a one-word reply | 0 | a `role: "system"` message pair before the user prompt; an assistant `message_end` with a `thinking` block and a `toolCall` block; `tool_execution_start`, two `tool_execution_update`s and `tool_execution_end`; a second turn's text-only `message_end`; then `agent_end` and `agent_settled` (`aborted: false`) |

Stderr was empty. Both requests offered the model exactly `read`, `bash`,
`edit` and `write`: `--tools -tool_search` removed the loader that
`settings.json` adds, and `--no-mcp` kept the kit's `github` server from
starting (its binary was not even installed in the container).

To do: replace or extend this with a capture from a live `md2okf-pi`
sandbox against OpenRouter, through `md2okf-agent`, and with a failing run.
No captured stream yet shows an event that means "this turn failed".

## Redactions

None. The only paths are the container's (`/work/okf`, `/home/agent`,
`/usr/local/share/npm-global`).
