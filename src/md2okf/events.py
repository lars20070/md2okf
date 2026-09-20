"""Turn Pi's `--mode json` event stream into the host-side progress view.

Replaces the jq filter in the old shell driver
(the retired `scripts/compile-okf.sh`): the same three cases, the same 120-character
cut on tool calls.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Iterator

DISPLAY_WIDTH = 120


def _load(line: str) -> dict | None:
    try:
        event = json.loads(line)
    except (json.JSONDecodeError, ValueError):
        return None
    return event if isinstance(event, dict) else None


def _translate_event(event: dict) -> str | None:
    event_type = event.get("type")
    if event_type == "tool_execution_start":
        tool_name = event.get("toolName", "")
        args = event.get("args", "")
        return f"{tool_name} {args}"[:DISPLAY_WIDTH]

    if event_type == "message_end":
        message = event.get("message") or {}
        if message.get("role") != "assistant":
            return None
        parts = []
        for block in message.get("content") or []:
            if block.get("type") == "thinking":
                parts.append(f"[thinking]\n{block.get('thinking', '')}")
            elif block.get("type") == "text":
                parts.append(block.get("text", ""))
        return "\n\n".join(parts) or None

    return None


def translate(line: str) -> str | None:
    """One raw `pi --mode json` line -> the text worth showing, or None.

    A tool call becomes "toolName args" (cut to DISPLAY_WIDTH); an assistant
    `message_end` becomes its joined text/thinking parts; anything else,
    including a line that is not JSON, produces nothing.
    """
    event = _load(line)
    return _translate_event(event) if event is not None else None


def is_tool_call(line: str) -> bool:
    """Whether a raw line is a `tool_execution_start` event.

    A session with zero of these did not follow the compile-okf skill (its
    first two steps are tool calls) -- see compile.py's "did nothing" check.
    """
    event = _load(line)
    return event is not None and event.get("type") == "tool_execution_start"


def process(lines: Iterable[str]) -> Iterator[tuple[str, str | None, bool]]:
    """Yield (raw line, display-or-None, is_tool_call) for each line, in order.

    `display` is what a human should actually see, and the distinction it
    draws matters in both directions:

    - A line that is **not JSON at all** -- plain stderr text, a traceback
      merged in from stderr -- is shown verbatim. Dropping these is what
      left a failing run reporting only "pi exited 1" with no cause.
    - A line that **is** a Pi protocol event we do not render is dropped.
      Pi emits a `message_update` envelope per *token*, so showing these
      floods the terminal with thousands of empty-delta JSON objects and
      buries the tool calls -v exists to reveal.
    """
    for line in lines:
        event = _load(line)
        if event is None:
            yield line, line, False  # not JSON: a diagnostic, worth showing
            continue
        yield line, _translate_event(event), event.get("type") == "tool_execution_start"
