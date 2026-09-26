"""Tests for md2okf.protocols.claude, against captured Claude Code output.

Every stream here is real: tests/fixtures/protocols/claude/ holds what the
stage 2.1 spike recorded (see its README). Hand-written events appear only
where a captured one is cut or combined, never invented from documentation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from md2okf import agents, workbench
from md2okf import compile as compile_mod
from md2okf.protocols import DISPLAY_WIDTH, claude
from md2okf.protocols import pi as pi_protocol

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "protocols" / "claude"


def _lines(name: str) -> list[str]:
    return (FIXTURES / name).read_text(encoding="utf-8").splitlines()


def _events(name: str):
    return list(claude.process(_lines(name)))


# --- the four captured runs ----------------------------------------------------


def test_a_successful_write_is_one_tool_call_and_no_failure():
    events = _events("success-write.jsonl")
    tool_calls = [event for event in events if event.is_tool_call]
    assert len(tool_calls) == 1
    assert tool_calls[0].display.startswith("Write {'file_path': ")
    assert [event.failure for event in events] == [None] * len(events)
    assert [event.display for event in events if event.display] == [tool_calls[0].display, "done"]


def test_a_text_only_turn_has_no_tool_calls_and_no_failure():
    """Exit 0 and no tool call: the driver's "did not follow the skill" case, not a failure."""
    events = _events("success-no-tool-calls.jsonl")
    assert not any(event.is_tool_call for event in events)
    assert not any(event.failure for event in events)
    assert any("SPIKE-MARKER-7f3a" in (event.display or "") for event in events)


def test_an_unknown_model_is_a_failure_although_its_subtype_says_success():
    """`is_error` is the signal: this run's result has `subtype: success`."""
    lines = _lines("error-unknown-model.jsonl")
    assert json.loads(lines[-1])["subtype"] == "success"

    failures = [event.failure for event in claude.process(lines) if event.failure]

    assert failures == [
        "api_error: There's an issue with the selected model (md2okf-spike-no-such-model). "
        "It may not exist or you may not have access to it. Run --model to pick a different model."
    ]


def test_a_max_turns_cutoff_is_a_failure_after_a_real_tool_call():
    """The reason is in `errors`, not `result`, and the turn had already done work."""
    events = _events("error-max-turns.jsonl")
    assert sum(event.is_tool_call for event in events) == 1
    assert [event.failure for event in events if event.failure] == [
        "max_turns: Reached maximum number of turns (1)"
    ]
    first_tool = next(i for i, event in enumerate(events) if event.is_tool_call)
    first_failure = next(i for i, event in enumerate(events) if event.failure)
    assert first_tool < first_failure


# --- lines that are not protocol events ----------------------------------------


def test_plain_stderr_is_shown_verbatim_and_is_neither_a_call_nor_a_failure():
    stderr = (FIXTURES / "error-unknown-model.stderr").read_text(encoding="utf-8").strip()
    assert stderr.startswith("[claude-code:unrecognized_model]")
    (event,) = claude.process([stderr])
    assert (event.display, event.is_tool_call, event.failure) == (stderr, False, None)


def test_a_line_cut_short_is_shown_verbatim_and_never_a_tool_call():
    """A captured tool_use event, truncated: it must not count, crash, or vanish."""
    whole = next(line for line in _lines("success-write.jsonl") if claude.is_tool_call(line))
    cut = whole[: len(whole) // 2]
    (event,) = claude.process([cut])
    assert (event.display, event.is_tool_call, event.failure) == (cut, False, None)


def test_a_json_value_that_is_not_an_object_is_treated_as_text():
    (event,) = claude.process(["[1, 2, 3]"])
    assert (event.display, event.is_tool_call, event.failure) == ("[1, 2, 3]", False, None)


# --- display parity with Pi ------------------------------------------------------


def test_a_tool_call_reads_exactly_as_it_does_for_pi():
    arguments = {"file_path": "/wiki/page.md", "content": "hello"}
    claude_line = json.dumps(
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Write", "input": arguments}]}}
    )
    pi_line = json.dumps({"type": "tool_execution_start", "toolName": "Write", "args": arguments})
    assert claude.translate(claude_line) == pi_protocol.translate(pi_line) == f"Write {arguments}"


def test_a_long_tool_call_is_cut_to_the_shared_display_width():
    whole = next(line for line in _lines("success-write.jsonl") if claude.is_tool_call(line))
    event = json.loads(whole)
    event["message"]["content"][0]["input"] = {"command": "x" * 500}
    assert len(claude.translate(json.dumps(event))) == DISPLAY_WIDTH


def test_prose_blocks_join_like_pi_and_empty_thinking_is_dropped():
    line = json.dumps(
        {
            "type": "assistant",
            "message": {
                "content": [
                    {"type": "thinking", "thinking": ""},
                    {"type": "thinking", "thinking": "considering"},
                    {"type": "text", "text": "done"},
                ]
            },
        }
    )
    assert claude.translate(line) == "[thinking]\nconsidering\n\ndone"


@pytest.mark.parametrize("event_type", ["system", "user", "rate_limit_event"])
def test_non_assistant_events_render_as_nothing(event_type):
    line = next(json.loads(raw) for raw in _lines("error-max-turns.jsonl") if json.loads(raw)["type"] == event_type)
    assert claude.translate(json.dumps(line)) is None
    assert claude.failure(json.dumps(line)) is None


def test_a_successful_result_renders_as_nothing():
    result = _lines("success-write.jsonl")[-1]
    assert json.loads(result)["type"] == "result"
    assert (claude.translate(result), claude.failure(result)) == (None, None)


# --- through the driver ---------------------------------------------------------
#
# The parser as the Ralph loop uses it: a stub agent with the real Claude
# protocol, fed the captured streams (stdout and stderr merged, as `sbx exec`
# delivers them) and the exit codes the spike recorded.

STUB = agents.Agent(
    name="claude",
    min_sbx_version=(0, 45, 0),
    compile_args=lambda prompt: ["md2okf-agent", "claude", "-p", prompt],
    interactive_args=("md2okf-agent", "claude"),
    compile_prompt=lambda document: f"compile {document}",
    check_credentials=lambda _name: None,
    protocol=claude,
)
NAME = workbench.sandbox_name(STUB.name)


def _run(fake_sbx, tmp_path, lines, returncode):
    fake_sbx.register(NAME)
    wb = workbench.Workbench(root=tmp_path / "state")
    wb.ensure_roots()
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    source = tmp_path / "doc.md"
    source.write_text("# doc", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(lines, returncode=returncode)
    fake_sbx.queue_hash("aaaa0000")
    doc = compile_mod.Document(display=str(source), basename="doc.md")
    return compile_mod.compile_document(STUB, NAME, doc, wb, tmp_path / "out")


def test_the_driver_reports_the_unknown_model_with_its_stderr(fake_sbx, tmp_path):
    stderr = (FIXTURES / "error-unknown-model.stderr").read_text(encoding="utf-8").splitlines()
    with pytest.raises(compile_mod.CompileError) as excinfo:
        _run(fake_sbx, tmp_path, [*_lines("error-unknown-model.jsonl"), *stderr], returncode=1)
    message = str(excinfo.value)
    assert message.startswith("claude exited 1: api_error: There's an issue with the selected model")
    assert "[claude-code:unrecognized_model]" in message
    assert '"type":' not in message  # envelopes stay out of the tail
    assert not (tmp_path / "out").exists()


def test_the_driver_fails_a_cut_off_turn_even_though_it_made_a_tool_call(fake_sbx, tmp_path):
    with pytest.raises(compile_mod.CompileError) as excinfo:
        _run(fake_sbx, tmp_path, _lines("error-max-turns.jsonl"), returncode=1)
    message = str(excinfo.value)
    assert "max_turns: Reached maximum number of turns (1)" in message
    assert "no tool calls" not in message


def test_the_driver_accepts_the_successful_write(fake_sbx, tmp_path):
    row = _run(fake_sbx, tmp_path, _lines("success-write.jsonl"), returncode=0)
    assert row.iterations == 1


def test_the_driver_refuses_a_text_only_turn(fake_sbx, tmp_path):
    with pytest.raises(compile_mod.CompileError, match="claude session made no tool calls"):
        _run(fake_sbx, tmp_path, _lines("success-no-tool-calls.jsonl"), returncode=0)


def test_the_registered_claude_agent_uses_this_parser():
    assert agents.AGENTS["claude"].protocol is claude
