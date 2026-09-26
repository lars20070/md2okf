"""Tests for md2okf.compile."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from md2okf import agents, workbench
from md2okf import compile as compile_mod
from md2okf.protocols import Event

PI = agents.PI
NAME = workbench.sandbox_name(PI.name)


def _wb(tmp_path: Path) -> workbench.Workbench:
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    return wb


# --- resolve_documents() -----------------------------------------------------


def test_resolve_documents_defaults_to_stdin_when_piped():
    docs = compile_mod.resolve_documents([], stdin_is_tty=lambda: False)
    assert docs == [compile_mod.Document(display="-", basename="stdin.md", stdin=True)]


def test_resolve_documents_refuses_stdin_on_a_tty():
    with pytest.raises(compile_mod.UsageError):
        compile_mod.resolve_documents([], stdin_is_tty=lambda: True)
    with pytest.raises(compile_mod.UsageError):
        compile_mod.resolve_documents(["-"], stdin_is_tty=lambda: True)


def test_resolve_documents_refuses_more_than_one_dash():
    with pytest.raises(compile_mod.UsageError):
        compile_mod.resolve_documents(["-", "-"], stdin_is_tty=lambda: False)


def test_resolve_documents_expands_a_directory_sorted_non_recursive(tmp_path):
    folder = tmp_path / "md"
    folder.mkdir()
    (folder / "b.md").write_text("b", encoding="utf-8")
    (folder / "a.md").write_text("a", encoding="utf-8")
    (folder / "not-markdown.txt").write_text("x", encoding="utf-8")
    (folder / "sub").mkdir()
    (folder / "sub" / "nested.md").write_text("nested", encoding="utf-8")

    docs = compile_mod.resolve_documents([str(folder)])
    assert [d.basename for d in docs] == ["a.md", "b.md"]


def test_resolve_documents_keeps_duplicate_arguments_in_order(tmp_path):
    doc = tmp_path / "x.md"
    doc.write_text("x", encoding="utf-8")
    docs = compile_mod.resolve_documents([str(doc), str(doc)])
    assert len(docs) == 2
    assert docs[0].basename == docs[1].basename == "x.md"


def test_resolve_documents_rejects_a_basename_clash(tmp_path):
    a = tmp_path / "a" / "x.md"
    b = tmp_path / "b" / "x.md"
    a.parent.mkdir(parents=True)
    b.parent.mkdir(parents=True)
    a.write_text("a", encoding="utf-8")
    b.write_text("b", encoding="utf-8")
    with pytest.raises(compile_mod.UsageError):
        compile_mod.resolve_documents([str(a), str(b)])


def test_resolve_documents_rejects_tab_or_newline_in_a_path():
    with pytest.raises(compile_mod.UsageError):
        compile_mod.resolve_documents(["a\tb.md"])
    with pytest.raises(compile_mod.UsageError):
        compile_mod.resolve_documents(["a\nb.md"])


def test_resolve_documents_rejects_a_tab_in_a_filename_discovered_via_a_directory(tmp_path):
    """Regression.

    Only the raw CLI argument was checked for a tab/newline, not filenames a
    directory glob discovers -- POSIX allows a tab in a filename, and it
    would otherwise corrupt that document's TSV row.
    """
    folder = tmp_path / "md"
    folder.mkdir()
    (folder / "a\tb.md").write_text("x", encoding="utf-8")
    with pytest.raises(compile_mod.UsageError):
        compile_mod.resolve_documents([str(folder)])


def test_resolve_documents_rejects_an_empty_folder(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    with pytest.raises(compile_mod.UsageError):
        compile_mod.resolve_documents([str(empty)])


def test_resolve_documents_rejects_a_symlinked_input(tmp_path):
    real = tmp_path / "real.md"
    real.write_text("x", encoding="utf-8")
    link = tmp_path / "link.md"
    link.symlink_to(real)
    with pytest.raises(workbench.WorkbenchError):
        compile_mod.resolve_documents([str(link)])


def test_resolve_documents_rejects_a_nonexistent_path(tmp_path):
    with pytest.raises(compile_mod.UsageError):
        compile_mod.resolve_documents([str(tmp_path / "nope.md")])


def test_resolve_documents_rejects_a_symlinked_file_inside_a_directory(tmp_path):
    """Regression.

    Only the directory argument itself was safety-checked, not the *.md
    files discovered inside it -- so a symlinked file would slip past
    resolution (exit 2) and only fail later at staging (exit 1).
    """
    folder = tmp_path / "md"
    folder.mkdir()
    real = tmp_path / "real.md"
    real.write_text("x", encoding="utf-8")
    (folder / "link.md").symlink_to(real)
    with pytest.raises(workbench.WorkbenchError):
        compile_mod.resolve_documents([str(folder)])


def test_stage_items_reads_stdin_lazily(monkeypatch):
    import io

    monkeypatch.setattr(compile_mod.sys, "stdin", type("S", (), {"buffer": io.BytesIO(b"piped content")})())
    items = compile_mod.stage_items([compile_mod.Document(display="-", basename="stdin.md", stdin=True)])
    assert items == [("stdin.md", b"piped content")]


# --- the Ralph loop ----------------------------------------------------------


def _doc(tmp_path: Path, name: str = "a.md") -> compile_mod.Document:
    source = tmp_path / name
    source.write_text(f"# {name}", encoding="utf-8")
    return compile_mod.Document(display=str(source), basename=name)


def test_hash_stable_first_pass_is_convergence_not_failure(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("already compiled", encoding="utf-8")
    fake_sbx.queue_hash("aaaa1111")  # before
    fake_sbx.queue_turn(['{"type": "tool_execution_start", "toolName": "Read", "args": {}}'])
    fake_sbx.queue_hash("aaaa1111")  # after iteration 1: unchanged

    row = compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")

    assert row.iterations == 1
    assert row.hash_before == row.hash_after == "aaaa1111"


def test_loop_runs_until_hash_stabilises(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])
    fake_sbx.queue_hash("bbbb1111")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])
    fake_sbx.queue_hash("bbbb1111")

    row = compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")
    assert row.iterations == 2
    assert row.hash_before == "aaaa0000"
    assert row.hash_after == "bbbb1111"


def test_nonzero_pi_exit_is_a_failure_not_convergence(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'], returncode=1)

    with pytest.raises(compile_mod.CompileError, match="exited 1"):
        compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")


def test_zero_tool_calls_is_a_failure(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "message_end", "message": {"role": "assistant", "content": []}}'])

    with pytest.raises(compile_mod.CompileError, match="no tool calls"):
        compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")


def test_wiki_empty_before_and_after_is_a_failure(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)  # work_okf stays empty
    fake_sbx.queue_hash("eeee0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])
    fake_sbx.queue_hash("eeee0000")

    with pytest.raises(compile_mod.CompileError, match="still empty"):
        compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")


def test_iteration_cap_is_a_failure_naming_the_document(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    for i in range(3):
        fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])
        fake_sbx.queue_hash(f"cccc{i + 1:04d}")  # never repeats -> never converges

    doc = _doc(tmp_path)
    with pytest.raises(compile_mod.CompileError) as excinfo:
        compile_mod.compile_document(PI, NAME, doc, wb, tmp_path / "out", max_iterations=2)
    assert excinfo.value.document == doc.display
    # Regression: .document was recorded but never folded into str(exc), so
    # the message a caller actually prints silently dropped the document.
    assert doc.display in str(excinfo.value)


def test_malformed_hash_is_never_convergence(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("not-hex!!")

    with pytest.raises(compile_mod.CompileError, match="malformed hash"):
        compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")


def test_continuation_prompt_appended_from_iteration_two(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])
    fake_sbx.queue_hash("bbbb1111")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])
    fake_sbx.queue_hash("bbbb1111")

    compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")

    first, second = fake_sbx.turn_argvs
    assert first == ["pi", "--mode", "json", PI.compile_prompt(wb.work_md / "a.md")]
    assert compile_mod.CONTINUATION_PROMPT not in first[-1]
    assert second[-1] == f"{first[-1]} {compile_mod.CONTINUATION_PROMPT}"


def test_mirrors_out_after_every_iteration(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    output_dir = tmp_path / "out"
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])
    fake_sbx.queue_hash("aaaa0000")

    compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, output_dir)
    assert (output_dir / "page.md").read_text(encoding="utf-8") == "seed"


def test_mirror_out_failure_is_a_compileerror_not_a_crash(fake_sbx, tmp_path, monkeypatch):
    """Regression.

    mirror_out raised WorkbenchError/MirrorError, which the caller's
    per-document loop never catches (only CompileError) -- an unhandled
    exception instead of the documented exit 1.
    """
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])

    def boom(work_okf, output_dir):
        # Same message shape mirror_out itself raises, so this test also
        # covers the regression: the workbench path used to be recorded
        # only as an attribute, never actually in the message text that
        # cli.py's print(f"md2okf: {exc}") relies on.
        raise workbench.MirrorError(f"disk full; the completed work is still at {work_okf}", work_okf)

    monkeypatch.setattr(compile_mod.workbench, "mirror_out", boom)

    doc = _doc(tmp_path)
    with pytest.raises(compile_mod.CompileError) as excinfo:
        compile_mod.compile_document(PI, NAME, doc, wb, tmp_path / "out")
    assert excinfo.value.document == doc.display
    assert str(wb.work_okf) in str(excinfo.value)


def test_a_real_mirror_out_failure_names_the_recovery_path_end_to_end(fake_sbx, tmp_path):
    """Regression, exercised through the real mirror_out (no monkeypatching).

    A caller only ever sees str(exc); the Stage 2 contract requires that
    text to name the workbench path holding the completed work, not just
    set it as an exception attribute nobody reads.
    """
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])

    blocker = tmp_path / "blocker"
    blocker.write_text("a file, not a directory", encoding="utf-8")
    output_dir = blocker / "out"  # mkdir(parents=True) under a file must fail

    doc = _doc(tmp_path)
    with pytest.raises(compile_mod.CompileError) as excinfo:
        compile_mod.compile_document(PI, NAME, doc, wb, output_dir)
    assert str(wb.work_okf) in str(excinfo.value)


def test_on_progress_and_on_event_callbacks(fake_sbx, tmp_path):
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(
        [
            '{"type": "tool_execution_start", "toolName": "Read", "args": {}}',
            '{"type": "message_end", "message": {"role": "assistant", "content": [{"type": "text", "text": "hi"}]}}',
        ]
    )
    fake_sbx.queue_hash("aaaa0000")

    progress: list[str] = []
    verbose_events: list[str] = []
    compile_mod.compile_document(
        PI, NAME, _doc(tmp_path), wb, tmp_path / "out", on_progress=progress.append, on_event=verbose_events.append
    )
    assert any("iteration 1" in line for line in progress)
    assert any("aaaa0000 -> aaaa0000" in line for line in progress)
    assert verbose_events == ["Read {}", "hi"]


def test_on_event_shows_unrecognized_lines_raw_when_verbose(fake_sbx, tmp_path):
    """Regression (code review finding 2).

    A line protocols/pi.py cannot translate -- malformed JSON, plain stderr text,
    a traceback merged in from stderr -- must still reach -v, not vanish
    just because it wasn't a recognised tool call or assistant message.
    """
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(
        [
            "Traceback (most recent call last):",
            "RuntimeError: something broke",
            '{"type": "tool_execution_start", "toolName": "Read", "args": {}}',
        ]
    )
    fake_sbx.queue_hash("aaaa0000")

    verbose_events: list[str] = []
    compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out", on_event=verbose_events.append)
    assert verbose_events == [
        "Traceback (most recent call last):",
        "RuntimeError: something broke",
        "Read {}",
    ]


def test_nonzero_pi_exit_includes_diagnostic_output_in_the_error(fake_sbx, tmp_path):
    """Regression (code review finding 2).

    Previously the message was just "pi exited N", with the actual reason
    -- Pi's own stderr, a traceback, sbx's own diagnostic text -- discarded
    entirely, even without -v.
    """
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(
        [
            '{"type": "tool_execution_start"}',
            "Traceback (most recent call last):",
            "RuntimeError: the actual reason this failed",
        ],
        returncode=1,
    )

    with pytest.raises(compile_mod.CompileError, match="the actual reason this failed"):
        compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")


def test_ctrl_c_mid_stream_does_not_mirror_a_partial_iteration(fake_sbx, tmp_path):
    """Regression, found by an interrupted live run.

    The plan's contract: on interruption, do not mirror out the
    half-finished iteration. mirror_out() sits after the stream loop, so
    -o DIR must be untouched -- and the local `sbx exec` conduit must be
    cleaned up rather than left behind.
    """
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    output_dir = tmp_path / "out"
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}', KeyboardInterrupt()])

    with pytest.raises(KeyboardInterrupt):
        compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, output_dir)

    assert not output_dir.exists()  # nothing half-written reached -o DIR
    assert fake_sbx.last_popen.terminated is True
    assert fake_sbx.last_popen.stdout.closed is True


def test_stream_is_closed_on_the_normal_path_too(fake_sbx, tmp_path):
    """close() is in a finally, so it must be harmless after a clean run."""
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'])
    fake_sbx.queue_hash("aaaa0000")

    compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")

    # Exited normally, so it was waited on rather than terminated.
    assert fake_sbx.last_popen.terminated is False
    assert fake_sbx.last_popen.stdout.closed is True


def test_verbose_does_not_echo_pi_protocol_events(fake_sbx, tmp_path):
    """Regression, found watching a live -v run.

    Pi emits a `message_update` envelope per token. These must not reach
    -v, or the tool calls it exists to show are buried in thousands of
    empty-delta JSON objects.
    """
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(
        [
            '{"type": "message_update", "assistantMessageEvent": {"type": "toolcall_delta", "delta": ""}}',
            '{"type": "message_update", "assistantMessageEvent": {"type": "thinking_delta", "delta": "x"}}',
            '{"type": "tool_execution_start", "toolName": "Read", "args": {}}',
            "plain stderr text worth seeing",
        ]
    )
    fake_sbx.queue_hash("aaaa0000")

    seen: list[str] = []
    compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out", on_event=seen.append)

    assert seen == ["Read {}", "plain stderr text worth seeing"]


def test_failure_tail_excludes_protocol_json(fake_sbx, tmp_path):
    """The cause belongs in the message, not a wall of JSON envelopes."""
    fake_sbx.register(NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(
        [
            '{"type": "tool_execution_start"}',
            '{"type": "message_update", "assistantMessageEvent": {"type": "toolcall_delta", "delta": ""}}',
            "RuntimeError: the actual reason",
        ],
        returncode=1,
    )

    with pytest.raises(compile_mod.CompileError) as excinfo:
        compile_mod.compile_document(PI, NAME, _doc(tmp_path), wb, tmp_path / "out")

    message = str(excinfo.value)
    assert "RuntimeError: the actual reason" in message
    assert "message_update" not in message


# --- protocol-declared failures ----------------------------------------------
#
# Driven by a stub agent rather than Pi, whose parser never reports a failure
# (see protocols/pi.py): the rule under test is the driver's, and it must hold
# for every agent whose protocol can state one.


TOOL = json.dumps({"tool": "Read"})


def _fail(why: str) -> str:
    return json.dumps({"fail": why})


class _StubProtocol:
    """A made-up NDJSON protocol: {"tool": ...} is a tool call, {"fail": why} a terminal failure."""

    @staticmethod
    def process(lines):
        for line in lines:
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                yield Event(line, line, False, None)  # plain text: a diagnostic
                continue
            if "tool" in event:
                yield Event(line, event["tool"], True, None)
            else:
                yield Event(line, None, False, event.get("fail"))


STUB = agents.Agent(
    name="stub",
    min_sbx_version=(0, 43, 0),
    compile_args=lambda prompt: ["stub-agent", "--headless", prompt],
    interactive_args=("stub-agent",),
    compile_prompt=lambda document: f"compile {document}",
    check_credentials=lambda _name: None,
    protocol=_StubProtocol(),
)
STUB_NAME = workbench.sandbox_name(STUB.name)


def _seeded(fake_sbx, tmp_path: Path) -> tuple[workbench.Workbench, Path]:
    fake_sbx.register(STUB_NAME)
    wb = _wb(tmp_path)
    (wb.work_okf / "page.md").write_text("seed", encoding="utf-8")
    fake_sbx.queue_hash("aaaa0000")
    return wb, tmp_path / "out"


def test_the_turn_runs_the_agents_own_argv_and_prompt(fake_sbx, tmp_path):
    wb, out = _seeded(fake_sbx, tmp_path)
    fake_sbx.queue_turn([TOOL])
    fake_sbx.queue_hash("aaaa0000")

    compile_mod.compile_document(STUB, STUB_NAME, _doc(tmp_path), wb, out)

    assert fake_sbx.turn_argvs == [["stub-agent", "--headless", f"compile {wb.work_md / 'a.md'}"]]


def test_exit_zero_with_a_protocol_failure_fails_and_mirrors_nothing(fake_sbx, tmp_path):
    wb, out = _seeded(fake_sbx, tmp_path)
    fake_sbx.queue_turn([TOOL, _fail("the model refused the request")], returncode=0)

    with pytest.raises(compile_mod.CompileError, match="stub reported a failed turn: the model refused") as excinfo:
        compile_mod.compile_document(STUB, STUB_NAME, _doc(tmp_path), wb, out)

    assert str(tmp_path / "a.md") in str(excinfo.value)
    assert not out.exists()


def test_a_failure_after_tool_calls_is_not_reported_as_no_tool_calls(fake_sbx, tmp_path):
    """Work done before a terminal failure must not turn it into success -- or into the wrong error."""
    wb, out = _seeded(fake_sbx, tmp_path)
    fake_sbx.queue_turn([TOOL, TOOL, _fail("context window exceeded")])

    with pytest.raises(compile_mod.CompileError) as excinfo:
        compile_mod.compile_document(STUB, STUB_NAME, _doc(tmp_path), wb, out)

    message = str(excinfo.value)
    assert "context window exceeded" in message
    assert "no tool calls" not in message


def test_a_protocol_failure_with_no_tool_calls_reports_the_failure(fake_sbx, tmp_path):
    wb, out = _seeded(fake_sbx, tmp_path)
    fake_sbx.queue_turn([_fail("invalid model id")])

    with pytest.raises(compile_mod.CompileError, match="invalid model id") as excinfo:
        compile_mod.compile_document(STUB, STUB_NAME, _doc(tmp_path), wb, out)

    assert "no tool calls" not in str(excinfo.value)


def test_nonzero_exit_and_a_protocol_failure_report_both(fake_sbx, tmp_path):
    wb, out = _seeded(fake_sbx, tmp_path)
    fake_sbx.queue_turn([TOOL, _fail("rate limited"), "sbx: connection reset"], returncode=3)

    with pytest.raises(compile_mod.CompileError) as excinfo:
        compile_mod.compile_document(STUB, STUB_NAME, _doc(tmp_path), wb, out)

    message = str(excinfo.value)
    assert message.startswith("stub exited 3: rate limited\nsbx: connection reset")


def test_nonzero_exit_without_a_protocol_failure_keeps_the_plain_tail(fake_sbx, tmp_path):
    wb, out = _seeded(fake_sbx, tmp_path)
    fake_sbx.queue_turn([TOOL, "Traceback: the real cause"], returncode=1)

    with pytest.raises(compile_mod.CompileError, match=r"^stub exited 1: Traceback: the real cause"):
        compile_mod.compile_document(STUB, STUB_NAME, _doc(tmp_path), wb, out)


def test_no_tool_calls_names_the_agent(fake_sbx, tmp_path):
    wb, out = _seeded(fake_sbx, tmp_path)
    fake_sbx.queue_turn(["just talking"])

    with pytest.raises(compile_mod.CompileError, match="stub session made no tool calls"):
        compile_mod.compile_document(STUB, STUB_NAME, _doc(tmp_path), wb, out)
