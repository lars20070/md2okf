"""Tests for md2okf.protocols.pi, Pi's `--mode json` parser."""

from __future__ import annotations

import json
from pathlib import Path

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


# --- the captured Pi 1.4.0 run (tests/fixtures/protocols/pi/README.md) ---------

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "protocols" / "pi"


def _lines(name: str) -> list[str]:
    return (FIXTURES / name).read_text(encoding="utf-8").splitlines()


def test_captured_run_shows_thinking_the_tool_call_and_the_reply_in_order():
    """Only those three lines are shown.

    Everything else Pi 1.4.0 emits -- system and user messages, per-token
    updates, tool updates and results, turn and agent ends -- is dropped.
    """
    shown = [event.display for event in events.process(_lines("success-bash.jsonl")) if event.display]
    assert shown == ["[thinking]\nList the workspace first.", "bash {'command': 'ls'}", "Done."]


def test_captured_run_has_exactly_one_tool_call_and_no_failure():
    lines = _lines("success-bash.jsonl")
    processed = list(events.process(lines))
    assert [event.raw for event in processed] == lines
    assert sum(event.is_tool_call for event in processed) == 1
    assert sum(events.is_tool_call(line) for line in lines) == 1
    assert not any(event.failure for event in processed)


def test_captured_run_is_all_protocol_events_none_shown_verbatim():
    """Every captured line is JSON, so none takes the non-JSON diagnostic path."""
    for line in _lines("success-bash.jsonl"):
        assert isinstance(json.loads(line), dict)


def test_captured_system_message_and_tool_lifecycle_are_not_rendered():
    """Pi 1.4.0 adds a role "system" message pair; tool updates and ends are not calls."""
    by_type = {}
    for line in _lines("success-bash.jsonl"):
        event = json.loads(line)
        role = (event.get("message") or {}).get("role")
        by_type.setdefault((event["type"], role), []).append(line)

    for line in by_type[("message_end", "system")] + by_type[("message_end", "toolResult")]:
        assert events.translate(line) is None
    for kind in ("tool_execution_update", "tool_execution_end"):
        for line in by_type[(kind, None)]:
            assert events.translate(line) is None
            assert events.is_tool_call(line) is False


def test_captured_run_ends_with_agent_end_then_agent_settled():
    """The terminal events Pi 1.4.0 emits; `aborted` is new in 1.1.0."""
    tail = [json.loads(line) for line in _lines("success-bash.jsonl")[-2:]]
    assert [event["type"] for event in tail] == ["agent_end", "agent_settled"]
    assert tail[-1]["aborted"] is False


def test_process_never_reports_a_failure_until_one_is_captured():
    """Pi's failures are decided by its exit code; see the module docstring."""
    lines = [
        json.dumps({"type": "tool_execution_start", "toolName": "Read", "args": {}}),
        json.dumps({"type": "agent_end"}),
        "Error: something went wrong",
    ]
    assert [event.failure for event in events.process(lines)] == [None, None, None]
