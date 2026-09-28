"""Tests for md2okf.protocols.pi, Pi's `--mode json` parser."""

from __future__ import annotations

import json

from md2okf.protocols import Event
from md2okf.protocols import pi as events


def test_translate_tool_execution_start():
    line = json.dumps({"type": "tool_execution_start", "toolName": "Read", "args": {"path": "a.md"}})
    assert events.translate(line) == "Read {'path': 'a.md'}"


def test_translate_cuts_long_tool_calls_to_display_width():
    line = json.dumps({"type": "tool_execution_start", "toolName": "Bash", "args": {"command": "x" * 500}})
    assert len(events.translate(line)) == events.DISPLAY_WIDTH


def test_translate_assistant_message_end_joins_text_and_thinking():
    line = json.dumps(
        {
            "type": "message_end",
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "thinking", "thinking": "considering"},
                    {"type": "text", "text": "done"},
                ],
            },
        }
    )
    assert events.translate(line) == "[thinking]\nconsidering\n\ndone"


def test_translate_ignores_non_assistant_message_end():
    line = json.dumps({"type": "message_end", "message": {"role": "user", "content": []}})
    assert events.translate(line) is None


def test_translate_ignores_empty_assistant_message():
    line = json.dumps({"type": "message_end", "message": {"role": "assistant", "content": []}})
    assert events.translate(line) is None


def test_translate_ignores_unknown_event_types():
    assert events.translate(json.dumps({"type": "session_start"})) is None


def test_translate_ignores_non_json_lines():
    assert events.translate("not json at all") is None
    assert events.translate("") is None
    assert events.translate("[1, 2, 3]") is None


def test_is_tool_call():
    assert events.is_tool_call(json.dumps({"type": "tool_execution_start"})) is True
    assert events.is_tool_call(json.dumps({"type": "message_end"})) is False
    assert events.is_tool_call("garbage") is False


def test_process_yields_events_in_order():
    message_end = {"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": "hi"}]}}
    tool_line = json.dumps({"type": "tool_execution_start", "toolName": "Read", "args": {}})
    message_line = json.dumps(message_end)
    lines = [tool_line, "not json", message_line]

    results = list(events.process(lines))

    assert results == [
        Event(tool_line, "Read {}", True, None),
        Event("not json", "not json", False, None),  # non-JSON is a diagnostic: shown verbatim
        Event(message_line, "hi", False, None),
    ]


def test_process_drops_protocol_events_but_keeps_non_json_diagnostics():
    """Regression, found watching a live -v run.

    Pi emits a `message_update` envelope per token. Treating every
    untranslated line as a diagnostic flooded -v with thousands of
    empty-delta JSON objects and buried the tool calls. A protocol event we
    do not render must be dropped; genuinely non-JSON output must not be.
    """
    delta = json.dumps(
        {"type": "message_update", "assistantMessageEvent": {"type": "toolcall_delta", "delta": ""}}
    )
    traceback_line = "RuntimeError: the actual reason this failed"

    displays = [event.display for event in events.process([delta, traceback_line])]

    assert displays == [None, traceback_line]


def test_process_never_reports_a_failure_until_one_is_captured():
    """Pi's failures are decided by its exit code; see the module docstring."""
    lines = [
        json.dumps({"type": "tool_execution_start", "toolName": "Read", "args": {}}),
        json.dumps({"type": "agent_end"}),
        "Error: something went wrong",
    ]
    assert [event.failure for event in events.process(lines)] == [None, None, None]
