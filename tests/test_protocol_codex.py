"""Tests for md2okf.protocols.codex, against captured Codex output.

Every stream here is real: tests/fixtures/protocols/codex/ holds what the
stage 3.1 spike recorded (see its README). Hand-written events appear only
where a captured one is cut, reordered or combined, never invented from
documentation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from md2okf import agents, workbench
from md2okf import compile as compile_mod
from md2okf.protocols import DISPLAY_WIDTH, codex

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "protocols" / "codex"
STDIN_NOTICE = "Reading additional input from stdin..."


def _lines(name: str) -> list[str]:
    return (FIXTURES / name).read_text(encoding="utf-8").splitlines()


def _events(name: str):
    return list(codex.process(_lines(name)))


# --- the captured runs ---------------------------------------------------------


def test_a_file_change_is_one_tool_call_although_it_starts_and_completes():
    events = _events("success-write.jsonl")
    tool_calls = [event for event in events if event.is_tool_call]
    assert len(tool_calls) == 1
    assert tool_calls[0].display.startswith("file_change add /Users/user/")
    assert not any(event.failure for event in events)
    assert [event.display for event in events if event.display][-1] == "done"


def test_each_command_counts_once():
    events = _events("success-commands.jsonl")
    tool_calls = [event.display for event in events if event.is_tool_call]
    assert len(tool_calls) == 2
    assert all(display.startswith("command_execution /bin/bash -lc ") for display in tool_calls)
    assert any(event.display == "SPIKE-SKILL-MARKER-4c1e" for event in events)


def test_turn_failed_is_the_failure_and_its_json_detail_is_unwrapped():
    failures = [event.failure for event in _events("error-unknown-model.jsonl") if event.failure]
    assert failures == [
        "turn.failed: The 'md2okf-spike-no-such-model' model is not supported when using Codex with a ChatGPT account."
    ]


def test_warnings_before_the_failure_are_shown_but_are_not_the_verdict():
    """The run opens with an `error` item and a top-level `error` event; only `turn.failed` is terminal."""
    events = _events("error-unknown-model.jsonl")
    shown = [event.display for event in events if event.display]
    assert shown[0].startswith("[warning] Model metadata for")
    assert shown[1].startswith("[error] The 'md2okf-spike-no-such-model' model is not supported")
    assert [json.loads(event.raw)["type"] for event in events if event.failure] == ["turn.failed"]


# --- lines that are not protocol events ----------------------------------------


def test_codex_stdin_notice_is_hidden():
    (captured,) = (FIXTURES / "stderr.txt").read_text(encoding="utf-8").splitlines()
    assert captured == STDIN_NOTICE
    (event,) = codex.process([captured])
    assert (event.display, event.is_tool_call, event.failure) == (None, False, None)


def test_other_plain_text_is_shown_verbatim():
    (event,) = codex.process(["thread 'main' panicked at src/lib.rs:1"])
    assert event.display == "thread 'main' panicked at src/lib.rs:1"


def test_a_line_cut_short_is_shown_verbatim_and_never_a_tool_call():
    whole = next(line for line in _lines("success-write.jsonl") if codex.is_tool_call(line))
    cut = whole[: len(whole) // 2]
    (event,) = codex.process([cut])
    assert (event.display, event.is_tool_call, event.failure) == (cut, False, None)


# --- counting ------------------------------------------------------------------


def test_a_completion_without_its_start_still_counts():
    """A tool item seen only when it completes -- the stream joined late -- is still work done."""
    completed = [line for line in _lines("success-write.jsonl") if json.loads(line)["type"] == "item.completed"]
    events = list(codex.process(completed))
    assert sum(event.is_tool_call for event in events) == 1


def test_is_tool_call_marks_only_the_start():
    lines = [
        line for line in _lines("success-write.jsonl") if json.loads(line).get("item", {}).get("type") == "file_change"
    ]
    assert [codex.is_tool_call(line) for line in lines] == [True, False]


def test_a_long_tool_call_is_cut_to_the_shared_display_width():
    start = next(json.loads(line) for line in _lines("success-commands.jsonl") if codex.is_tool_call(line))
    start["item"]["command"] = "x" * 500
    assert len(codex.translate(json.dumps(start))) == DISPLAY_WIDTH


@pytest.mark.parametrize("event_type", ["thread.started", "turn.started", "turn.completed"])
def test_lifecycle_events_render_as_nothing(event_type):
    line = next(raw for raw in _lines("success-write.jsonl") if json.loads(raw)["type"] == event_type)
    assert (codex.translate(line), codex.failure(line)) == (None, None)


# --- through the driver ---------------------------------------------------------

STUB = agents.Agent(
    name="codex",
    min_sbx_version=(0, 45, 0),
    compile_args=lambda prompt: ["md2okf-agent", "codex", "exec", "--json", prompt],
    interactive_args=("md2okf-agent", "codex"),
    compile_prompt=lambda document: f"compile {document}",
    check_credentials=lambda _name: None,
    protocol=codex,
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


def test_the_driver_reports_the_unknown_model(fake_sbx, tmp_path):
    lines = [STDIN_NOTICE, *_lines("error-unknown-model.jsonl")]
    with pytest.raises(compile_mod.CompileError) as excinfo:
        _run(fake_sbx, tmp_path, lines, returncode=1)
    message = str(excinfo.value)
    assert message.startswith("codex exited 1: turn.failed: The 'md2okf-spike-no-such-model' model is not supported")
    assert STDIN_NOTICE not in message
    assert not (tmp_path / "out").exists()


def test_the_driver_accepts_the_successful_write(fake_sbx, tmp_path):
    row = _run(fake_sbx, tmp_path, [STDIN_NOTICE, *_lines("success-write.jsonl")], returncode=0)
    assert row.iterations == 1


def test_the_driver_refuses_a_turn_without_tool_items(fake_sbx, tmp_path):
    prose_only = [line for line in _lines("success-write.jsonl") if "file_change" not in line]
    with pytest.raises(compile_mod.CompileError, match="codex session made no tool calls"):
        _run(fake_sbx, tmp_path, prose_only, returncode=0)
