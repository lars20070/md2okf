"""Turn Codex's `codex exec --json` stream into the host-side view.

Derived from captured output (tests/fixtures/protocols/codex/, recorded by
the stage 3.1 spike against codex-cli 0.149.1), not from documentation:

- Work arrives as items. `item.started` and then `item.completed` carry the
  same item `id`; an item whose `type` is not prose (`agent_message`,
  `reasoning`) or a warning (`error`) is one tool call -- `command_execution`
  and `file_change` in the captured runs. It is counted and shown once, when
  it starts, or when it completes if its start was never seen.
- `agent_message` items carry the prose, in `text`, when they complete.
- `turn.failed` is the one terminal failure; its `error.message` is often a
  JSON string with a `detail`. A top-level `error` event precedes it, and an
  `error` *item* may appear before the turn even starts -- both only warnings
  on their own, so they are shown, never taken as the verdict.
- Codex prints `Reading additional input from stdin...` to stderr on every
  turn whose stdin is not a terminal; that one line is noise.

`display` matches the other protocols: a tool call reads "kind details" cut
to DISPLAY_WIDTH -- Codex's items have no tool names, so the item type stands
in for one -- and prose blocks are joined by blank lines.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator

from md2okf.protocols import DISPLAY_WIDTH, Event

__all__ = ["DISPLAY_WIDTH", "failure", "is_tool_call", "process", "translate"]

_NOT_TOOLS = frozenset({"agent_message", "reasoning", "error"})
_STDIN_NOTICE = "Reading additional input from stdin..."


def _load(line: str) -> dict | None:
    try:
        event = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None
    return event if isinstance(event, dict) else None


def _item(event: dict) -> dict:
    item = event.get("item")
    return item if isinstance(item, dict) else {}


def _is_tool_item(event: dict) -> bool:
    item = _item(event)
    return event.get("type") in {"item.started", "item.completed"} and bool(item.get("type")) and (
        item.get("type") not in _NOT_TOOLS
    )


def _tool_details(item: dict) -> str:
    kind = item.get("type")
    if kind == "command_execution":
        return str(item.get("command", ""))
    if kind == "file_change":
        changes = [c for c in item.get("changes") or [] if isinstance(c, dict)]
        return ", ".join(f"{c.get('kind', '')} {c.get('path', '')}".strip() for c in changes)
    rest = {key: value for key, value in item.items() if key not in {"id", "type", "status"}}
    return str(rest) if rest else ""


def _message(raw: object) -> str:
    """An error message, with a JSON-encoded `{"detail": ...}` unwrapped."""
    text = str(raw or "")
    try:
        decoded = json.loads(text)
    except ValueError:
        return text
    if isinstance(decoded, dict) and decoded.get("detail"):
        return str(decoded["detail"])
    return text


def _translate_event(event: dict) -> str | None:
    kind = event.get("type")
    if _is_tool_item(event):
        item = _item(event)
        return f"{item.get('type')} {_tool_details(item)}".strip()[:DISPLAY_WIDTH]
    if kind == "item.completed":
        item = _item(event)
        if item.get("type") == "agent_message" and item.get("text"):
            return str(item["text"])
        if item.get("type") == "reasoning" and item.get("text"):
            return f"[thinking]\n{item['text']}"
        if item.get("type") == "error" and item.get("message"):
            return f"[warning] {item['message']}"
        return None
    if kind == "error":
        return f"[error] {_message(event.get('message'))}"
    return None


def _failure_of(event: dict) -> str | None:
    if event.get("type") != "turn.failed":
        return None
    error = event.get("error")
    message = _message(error.get("message")) if isinstance(error, dict) else ""
    return f"turn.failed: {message}" if message else "turn.failed"


def translate(line: str) -> str | None:
    """One raw `codex exec --json` line -> the text worth showing, or None."""
    event = _load(line)
    return _translate_event(event) if event is not None else None


def is_tool_call(line: str) -> bool:
    """Whether a raw line starts a tool item (a completion alone counts only in process())."""
    event = _load(line)
    return event is not None and event.get("type") == "item.started" and _is_tool_item(event)


def failure(line: str) -> str | None:
    """The terminal failure a raw line states (`turn.failed`), or None."""
    event = _load(line)
    return _failure_of(event) if event is not None else None


def process(lines: Iterable[str]) -> Iterator[Event]:
    """Yield one Event per line, in order, counting each tool item once.

    A line that is not a JSON object is shown verbatim, as the other
    protocols do -- except Codex's own stdin notice, which is noise.
    """
    started: set[str] = set()
    for line in lines:
        event = _load(line)
        if event is None:
            display = None if line.strip() == _STDIN_NOTICE else line
            yield Event(line, display, False, None)
            continue
        if _is_tool_item(event):
            item_id = str(_item(event).get("id", ""))
            first_sight = event.get("type") == "item.started" or item_id not in started
            if event.get("type") == "item.started":
                started.add(item_id)
            else:
                started.discard(item_id)
            yield Event(line, _translate_event(event) if first_sight else None, first_sight, None)
            continue
        yield Event(line, _translate_event(event), False, _failure_of(event))
