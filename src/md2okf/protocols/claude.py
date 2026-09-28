"""Turn Claude Code's `-p --output-format stream-json` stream into the host-side view.

Derived from captured output (tests/fixtures/protocols/claude/, recorded by
the stage 2.1 spike against Claude Code 2.1.280), not from documentation:

- `assistant` events carry `message.content` blocks. A `tool_use` block
  (`name`, `input`) is one tool call; `text` and `thinking` blocks are prose.
  Claude Code streams one block per event in practice, but every block of an
  event is rendered, in order.
- `result` is the last event, and its `is_error` is what says the turn
  failed. `subtype` does not: an unknown model ends with `subtype: success`
  and `is_error: true`. The reason is in `result` (a string) or, when the run
  was cut off (`--max-turns`), in `errors` (a list).
- Everything else -- `system` (`init`, `commands_changed`,
  `thinking_tokens`), `user` (tool results, whose own `is_error` is per call
  and not terminal) and `rate_limit_event` -- renders as nothing.

`display` matches protocols.pi's: a tool call reads "ToolName args" cut to
DISPLAY_WIDTH, and prose blocks are joined by blank lines, so -v looks the
same whichever agent is running.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator

from md2okf.protocols import DISPLAY_WIDTH, Event

__all__ = ["DISPLAY_WIDTH", "failure", "is_tool_call", "process", "translate"]


def _load(line: str) -> dict | None:
    try:
        event = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None
    return event if isinstance(event, dict) else None


def _content(event: dict) -> list[dict]:
    if event.get("type") != "assistant":
        return []
    message = event.get("message") or {}
    return [block for block in message.get("content") or [] if isinstance(block, dict)]


def _translate_event(event: dict) -> str | None:
    parts = []
    for block in _content(event):
        kind = block.get("type")
        if kind == "tool_use":
            parts.append(f"{block.get('name', '')} {block.get('input', '')}"[:DISPLAY_WIDTH])
        elif kind == "text" and block.get("text"):
            parts.append(block["text"])
        elif kind == "thinking" and block.get("thinking"):
            # Often an empty string in this protocol; an empty one says nothing.
            parts.append(f"[thinking]\n{block['thinking']}")
    return "\n\n".join(parts) or None


def _is_tool_call_event(event: dict) -> bool:
    return any(block.get("type") == "tool_use" for block in _content(event))


def _failure_of(event: dict) -> str | None:
    """The terminal failure a `result` event states, or None.

    `is_error` first; an `error_*` subtype counts too, in case a future
    version reports a failure without the flag.
    """
    if event.get("type") != "result":
        return None
    subtype = str(event.get("subtype") or "")
    if event.get("is_error") is not True and not subtype.startswith("error"):
        return None
    reason = event.get("result")
    if not isinstance(reason, str) or not reason.strip():
        errors = [str(error) for error in event.get("errors") or [] if error]
        reason = "; ".join(errors)
    label = event.get("terminal_reason") or subtype or "error"
    return f"{label}: {reason}" if reason else str(label)


def translate(line: str) -> str | None:
    """One raw stream-json line -> the text worth showing, or None."""
    event = _load(line)
    return _translate_event(event) if event is not None else None


def is_tool_call(line: str) -> bool:
    """Whether a raw line is an `assistant` event carrying a `tool_use` block."""
    event = _load(line)
    return event is not None and _is_tool_call_event(event)


def failure(line: str) -> str | None:
    """The terminal failure a raw line states, or None -- see _failure_of."""
    event = _load(line)
    return _failure_of(event) if event is not None else None


def process(lines: Iterable[str]) -> Iterator[Event]:
    """Yield one Event per line, in order.

    A line that is not a JSON object -- plain stderr, or a line cut short --
    is shown verbatim, as protocols.pi does: it is a diagnostic, and often the
    only one.
    """
    for line in lines:
        event = _load(line)
        if event is None:
            yield Event(line, line, False, None)
            continue
        yield Event(line, _translate_event(event), _is_tool_call_event(event), _failure_of(event))
