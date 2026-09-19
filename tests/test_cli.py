"""Tests for md2okf.cli -- the end-to-end command, against FakeSbx."""

from __future__ import annotations

import io
import os
from pathlib import Path

import pytest

from md2okf import __version__, cli, sandbox, workbench


def _md(tmp_path: Path, name: str = "doc.md") -> Path:
    path = tmp_path / name
    path.write_text(f"# {name}\n", encoding="utf-8")
    return path


def test_version(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--version"])
    assert excinfo.value.code == 0
    assert capsys.readouterr().out.strip() == f"md2okf {__version__}"


# --- usage errors, decided before any work starts --------------------------


def test_missing_spec_file_is_exit_2(tmp_path, capsys, isolated_state):
    doc = _md(tmp_path)
    rc = cli.main(["--spec", str(tmp_path / "nope.md"), "-o", str(tmp_path / "out"), str(doc)])
    assert rc == 2
    assert "spec" in capsys.readouterr().err


def test_non_adoptable_output_is_exit_2(tmp_path, capsys, isolated_state):
    doc = _md(tmp_path)
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    (output_dir / "index.md").write_text("# just notes\n", encoding="utf-8")
    rc = cli.main(["-o", str(output_dir), str(doc)])
    assert rc == 2
    assert "refusing to adopt" in capsys.readouterr().err


def test_overlapping_output_inside_input_is_exit_2(tmp_path, capsys, isolated_state):
    folder = tmp_path / "md"
    folder.mkdir()
    _md(folder)
    rc = cli.main(["-o", str(folder / "out"), str(folder)])
    assert rc == 2
    assert "overlap" in capsys.readouterr().err


def test_no_documents_is_exit_2(tmp_path, capsys, isolated_state):
    empty = tmp_path / "empty"
    empty.mkdir()
    rc = cli.main(["-o", str(tmp_path / "out"), str(empty)])
    assert rc == 2
    assert "no documents" in capsys.readouterr().err


def test_n_less_than_one_is_exit_2(tmp_path, capsys, isolated_state):
    doc = _md(tmp_path)
    rc = cli.main(["-n", "0", "-o", str(tmp_path / "out"), str(doc)])
    assert rc == 2
    assert "-n" in capsys.readouterr().err


def test_dry_run_does_nothing_paid_and_creates_nothing(tmp_path, capsys, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    output_dir = tmp_path / "out"
    rc = cli.main(["--dry-run", "-o", str(output_dir), str(doc)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "dry-run" in out
    assert str(doc) in out
    assert fake_sbx.calls == []
    assert not output_dir.exists()
    assert not (isolated_state / "xdg-state" / "md2okf").exists()


def test_dry_run_prints_the_command_lines_that_would_run(tmp_path, capsys, isolated_state, fake_sbx):
    """Regression.

    The plan's stage 2 checkpoint requires --dry-run to print "the mounts,
    the documents and the command lines" -- only mounts and documents were
    printed.
    """
    doc = _md(tmp_path)
    rc = cli.main(["--dry-run", "-o", str(tmp_path / "out"), str(doc)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "commands:" in out
    assert "sbx run --detached --name md2okf" in out
    assert "sbx exec md2okf -- pi --mode json" in out
    assert doc.name in out  # the staged basename is embedded in the pi prompt
    assert fake_sbx.calls == []


def test_sbx_not_present_is_exit_2(tmp_path, capsys, isolated_state, monkeypatch):
    monkeypatch.setattr(sandbox.shutil, "which", lambda _name: None)
    doc = _md(tmp_path)
    rc = cli.main(["-o", str(tmp_path / "out"), str(doc)])
    assert rc == 2
    assert "sbx" in capsys.readouterr().err


def test_sbx_too_old_is_exit_2(tmp_path, capsys, isolated_state, fake_sbx):
    fake_sbx.version_string = "0.10.0"
    doc = _md(tmp_path)
    rc = cli.main(["-o", str(tmp_path / "out"), str(doc)])
    assert rc == 2
    assert "version" in capsys.readouterr().err


def test_not_logged_in_is_exit_2(tmp_path, capsys, isolated_state, fake_sbx):
    fake_sbx.logged_in = False
    doc = _md(tmp_path)
    rc = cli.main(["-o", str(tmp_path / "out"), str(doc)])
    assert rc == 2
    assert "logged in" in capsys.readouterr().err


# --- the happy path: create, compile, mirror out ----------------------------


def _write_a_page() -> None:
    """Stand in for what a real Pi run leaves on disk.

    A page, and the bundle-root index.md a compliant OKF wiki carries -- so
    a second run against the same -o DIR is recognised as adoptable.
    """
    work_okf = workbench.Workbench.default().work_okf
    (work_okf / "page.md").write_text("compiled", encoding="utf-8")
    index = work_okf / "index.md"
    if not index.exists():
        index.write_text('---\nokf_version: "0.2"\n---\n# Index\n', encoding="utf-8")


def test_first_run_creates_the_sandbox_and_prints_one_tsv_row(tmp_path, capsys, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    output_dir = tmp_path / "out"

    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_pi(['{"type": "tool_execution_start"}'], side_effect=_write_a_page)
    fake_sbx.queue_hash("aaaa0000")

    rc = cli.main(["-o", str(output_dir), str(doc)])
    assert rc == 0

    out, err = capsys.readouterr()
    lines = out.strip().splitlines()
    assert len(lines) == 1
    path, iterations, hash_before, hash_after = lines[0].split("\t")
    assert path == str(doc)
    assert iterations == "1"
    assert hash_before == hash_after == "aaaa0000"
    assert "Compiling document" in err

    assert any(c[:3] == ["sbx", "run", "--detached"] for c in fake_sbx.calls)
    assert (output_dir / "page.md").exists()


def test_second_run_with_unchanged_config_reuses_the_sandbox(tmp_path, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    output_dir = tmp_path / "out"

    for _ in range(2):
        fake_sbx.queue_hash("aaaa0000")
        fake_sbx.queue_pi(['{"type": "tool_execution_start"}'], side_effect=_write_a_page)
        fake_sbx.queue_hash("aaaa0000")

    assert cli.main(["-o", str(output_dir), str(doc)]) == 0
    run_calls_after_first = [c for c in fake_sbx.calls if c[:3] == ["sbx", "run", "--detached"]]
    assert len(run_calls_after_first) == 1

    assert cli.main(["-o", str(output_dir), str(doc)]) == 0
    run_calls_after_second = [c for c in fake_sbx.calls if c[:3] == ["sbx", "run", "--detached"]]
    assert len(run_calls_after_second) == 1  # not recreated


def test_fresh_forces_a_recreate(tmp_path, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    output_dir = tmp_path / "out"

    for _ in range(2):
        fake_sbx.queue_hash("aaaa0000")
        fake_sbx.queue_pi(['{"type": "tool_execution_start"}'], side_effect=_write_a_page)
        fake_sbx.queue_hash("aaaa0000")

    assert cli.main(["-o", str(output_dir), str(doc)]) == 0
    assert cli.main(["--fresh", "-o", str(output_dir), str(doc)]) == 0
    run_calls = [c for c in fake_sbx.calls if c[:3] == ["sbx", "run", "--detached"]]
    assert len(run_calls) == 2


def test_unowned_existing_sandbox_is_exit_2_and_not_deleted(tmp_path, capsys, isolated_state, fake_sbx):
    fake_sbx.register(workbench.SANDBOX_NAME)  # exists, but we never created it -- no marker on disk
    doc = _md(tmp_path)

    rc = cli.main(["-o", str(tmp_path / "out"), str(doc)])
    assert rc == 2
    assert "sbx rm --force" in capsys.readouterr().err
    assert sandbox.exists(workbench.SANDBOX_NAME) is True


def test_compile_failure_is_exit_1_and_still_prints_to_stderr(tmp_path, capsys, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_pi(['{"type": "tool_execution_start"}'], returncode=1)

    rc = cli.main(["-o", str(tmp_path / "out"), str(doc)])
    assert rc == 1
    out, err = capsys.readouterr()
    assert out == ""
    assert "exited 1" in err
    assert str(doc) in err  # the failing document must be named, not just "a" failure


# --- streams: stdout carries only the TSV -----------------------------------


def test_quiet_suppresses_rows_and_progress_but_not_fatal_errors(tmp_path, capsys, isolated_state):
    doc = _md(tmp_path)
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    (output_dir / "index.md").write_text("not a bundle\n", encoding="utf-8")

    rc = cli.main(["-q", "-o", str(output_dir), str(doc)])
    assert rc == 2
    out, err = capsys.readouterr()
    assert out == ""
    assert err != ""


def test_verbose_shows_tool_calls_and_prose(tmp_path, capsys, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_pi(
        ['{"type": "tool_execution_start", "toolName": "Read", "args": {}}'], side_effect=_write_a_page
    )
    fake_sbx.queue_hash("aaaa0000")

    rc = cli.main(["-v", "-o", str(tmp_path / "out"), str(doc)])
    assert rc == 0
    assert "Read {}" in capsys.readouterr().err


def test_stdin_is_labelled_dash(tmp_path, capsys, isolated_state, fake_sbx, monkeypatch):
    monkeypatch.setattr(cli.sys, "stdin", io.TextIOWrapper(io.BytesIO(b"# piped\n")))
    monkeypatch.setattr(cli.sys.stdin, "isatty", lambda: False)

    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_pi(['{"type": "tool_execution_start"}'], side_effect=_write_a_page)
    fake_sbx.queue_hash("aaaa0000")

    rc = cli.main(["-o", str(tmp_path / "out")])
    assert rc == 0
    out = capsys.readouterr().out
    assert out.startswith("-\t")


def test_a_path_with_a_tab_is_rejected(tmp_path, capsys, isolated_state):
    rc = cli.main(["-o", str(tmp_path / "out"), "a\tb.md"])
    assert rc == 2
    assert "tab" in capsys.readouterr().err


def test_more_than_one_dash_is_rejected(tmp_path, capsys, isolated_state):
    rc = cli.main(["-o", str(tmp_path / "out"), "-", "-"])
    assert rc == 2


# --- the lock ----------------------------------------------------------------


def test_a_second_run_fails_the_lock(tmp_path, capsys, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    with workbench.lock():
        rc = cli.main(["-o", str(tmp_path / "out"), str(doc)])
    assert rc == 2
    assert "another md2okf run" in capsys.readouterr().err


def test_an_unusable_lock_file_exits_2_with_a_message(tmp_path, capsys, isolated_state, fake_sbx, monkeypatch):
    """A squatted lock path is an environment problem, not a traceback.

    lock() is entered after the setup handlers, so this needs its own clause
    at the call site or the error escapes as a crash.
    """
    doc = _md(tmp_path)
    monkeypatch.setattr(workbench, "LOCK_PATH_TEMPLATE", str(tmp_path / "lock-{uid}.lock"))
    os.mkfifo(tmp_path / f"lock-{os.getuid()}.lock")

    rc = cli.main(["-o", str(tmp_path / "out"), str(doc)])

    assert rc == 2
    assert "not a regular file" in capsys.readouterr().err


def test_ctrl_c_exits_1_with_a_message_not_a_traceback(tmp_path, capsys, isolated_state, fake_sbx):
    """Regression, found by interrupting a live run.

    Ctrl-C used to propagate as a bare KeyboardInterrupt traceback. The
    plan's contract is a non-zero exit that says what survived, so the user
    knows -o DIR holds the last completed pass.
    """
    doc = _md(tmp_path)
    output_dir = tmp_path / "out"
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_pi(['{"type": "tool_execution_start"}', KeyboardInterrupt()])

    rc = cli.main(["-o", str(output_dir), str(doc)])

    assert rc == 1
    out, err = capsys.readouterr()
    assert out == ""  # no TSV row for a document that never finished
    assert "interrupted" in err
    assert str(output_dir) in err  # where the last completed pass is
    assert "Traceback" not in err


def test_ctrl_c_releases_the_lock(tmp_path, isolated_state, fake_sbx):
    """The lock must not survive an interrupted run, or the next one is stuck."""
    doc = _md(tmp_path)
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_pi(['{"type": "tool_execution_start"}', KeyboardInterrupt()])

    assert cli.main(["-o", str(tmp_path / "out"), str(doc)]) == 1

    with workbench.lock():  # would raise LockHeld if it had leaked
        pass
