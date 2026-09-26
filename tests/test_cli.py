"""Tests for md2okf.cli -- the end-to-end command, against FakeSbx."""

from __future__ import annotations

import io
import os
from pathlib import Path

import pytest
from conftest import ExecvpCalled

from md2okf import __version__, agents, cli, resources, sandbox, workbench

PI_SANDBOX = workbench.sandbox_name("pi")


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
    assert "  agent:  pi\n" in out
    assert f"sbx run --detached --name {PI_SANDBOX} " in out
    assert f"{resources.kit_dir('pi')} " in out
    assert f"sbx exec {PI_SANDBOX} -- pi --mode json 'Load the compile-okf skill" in out
    assert doc.name in out  # the staged basename is embedded in the pi prompt
    assert fake_sbx.calls == []


def test_dry_run_shows_the_agents_workbench(tmp_path, capsys, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    assert cli.main(["--dry-run", "-o", str(tmp_path / "out"), str(doc)]) == 0
    out = capsys.readouterr().out
    assert f"MD2OKF_STATE_DIR={isolated_state / 'xdg-state' / 'md2okf' / 'pi'} " in out


@pytest.mark.parametrize("flags", [["--dry-run"], [], ["--shell"], ["--agent"]])
def test_unknown_agent_is_exit_2_before_any_work(flags, tmp_path, capsys, isolated_state, fake_sbx, a_tty, monkeypatch):
    monkeypatch.setenv("MD2OKF_AGENT", "bogus")
    args = flags if flags in (["--shell"], ["--agent"]) else [*flags, "-o", str(tmp_path / "out"), str(_md(tmp_path))]
    assert cli.main(args) == 2
    err = capsys.readouterr().err
    assert "MD2OKF_AGENT='bogus'" in err
    assert "valid: pi" in err
    assert fake_sbx.calls == []
    assert not (isolated_state / "xdg-state").exists()


def test_explicit_pi_behaves_exactly_like_unset(tmp_path, capsys, isolated_state, fake_sbx, monkeypatch):
    doc = _md(tmp_path)
    args = ["--dry-run", "-o", str(tmp_path / "out"), str(doc)]
    assert cli.main(args) == 0
    unset = capsys.readouterr().out
    monkeypatch.setenv("MD2OKF_AGENT", "pi")
    assert cli.main(args) == 0
    assert capsys.readouterr().out == unset


def test_the_epilog_documents_md2okf_agent(capsys):
    with pytest.raises(SystemExit):
        cli.main(["--help"])
    assert "MD2OKF_AGENT" in capsys.readouterr().out


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
    work_okf = workbench.Workbench.default("pi").work_okf
    (work_okf / "page.md").write_text("compiled", encoding="utf-8")
    index = work_okf / "index.md"
    if not index.exists():
        index.write_text('---\nokf_version: "0.2"\n---\n# Index\n', encoding="utf-8")


def test_first_run_creates_the_sandbox_and_prints_one_tsv_row(tmp_path, capsys, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    output_dir = tmp_path / "out"

    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'], side_effect=_write_a_page)
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
        fake_sbx.queue_turn(['{"type": "tool_execution_start"}'], side_effect=_write_a_page)
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
        fake_sbx.queue_turn(['{"type": "tool_execution_start"}'], side_effect=_write_a_page)
        fake_sbx.queue_hash("aaaa0000")

    assert cli.main(["-o", str(output_dir), str(doc)]) == 0
    assert cli.main(["--fresh", "-o", str(output_dir), str(doc)]) == 0
    run_calls = [c for c in fake_sbx.calls if c[:3] == ["sbx", "run", "--detached"]]
    assert len(run_calls) == 2


def test_unowned_existing_sandbox_is_exit_2_and_not_deleted(tmp_path, capsys, isolated_state, fake_sbx):
    fake_sbx.register(PI_SANDBOX)  # exists, but we never created it -- no marker on disk
    doc = _md(tmp_path)

    rc = cli.main(["-o", str(tmp_path / "out"), str(doc)])
    assert rc == 2
    assert "sbx rm --force" in capsys.readouterr().err
    assert sandbox.exists(PI_SANDBOX) is True


def test_compile_failure_is_exit_1_and_still_prints_to_stderr(tmp_path, capsys, isolated_state, fake_sbx):
    doc = _md(tmp_path)
    fake_sbx.queue_hash("aaaa0000")
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'], returncode=1)

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
    fake_sbx.queue_turn(
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
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}'], side_effect=_write_a_page)
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
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}', KeyboardInterrupt()])

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
    fake_sbx.queue_turn(['{"type": "tool_execution_start"}', KeyboardInterrupt()])

    assert cli.main(["-o", str(tmp_path / "out"), str(doc)]) == 1

    with workbench.lock():  # would raise LockHeld if it had leaked
        pass


# --- interactive entry: --shell and --agent ---------------------------------
#
# A successful hand-over has no exit code to assert on -- exec_interactive
# replaces the process -- so these assert on the argv carried by ExecvpCalled,
# which FakeSbx raises in execvp's place.


def _exec_calls(fake_sbx):
    return [c for c in fake_sbx.calls if c[:3] == ["sbx", "exec", "-it"]]


def test_shell_execs_an_interactive_bash_in_the_sandbox(isolated_state, fake_sbx, a_tty):
    with pytest.raises(ExecvpCalled) as excinfo:
        cli.main(["--shell"])
    assert excinfo.value.argv == ["sbx", "exec", "-it", PI_SANDBOX, "--", "bash"]


def test_agent_execs_a_bare_interactive_agent_in_the_sandbox(isolated_state, fake_sbx, a_tty):
    with pytest.raises(ExecvpCalled) as excinfo:
        cli.main(["--agent"])
    assert excinfo.value.argv == ["sbx", "exec", "-it", PI_SANDBOX, "--", "pi"]


def test_shell_opens_with_a_warning_when_credentials_are_not_ready(isolated_state, fake_sbx, a_tty, capsys):
    """A diagnostic shell is most needed exactly when the credential is broken."""
    fake_sbx.openrouter_key = "sk-literal-value"
    with pytest.raises(ExecvpCalled) as excinfo:
        cli.main(["--shell"])
    assert excinfo.value.argv == ["sbx", "exec", "-it", PI_SANDBOX, "--", "bash"]
    err = capsys.readouterr().err
    assert "md2okf: warning: OPENROUTER_API_KEY" in err
    assert "sbx secret set openrouter" in err


def test_agent_refuses_to_open_when_credentials_are_not_ready(isolated_state, fake_sbx, a_tty, capsys):
    fake_sbx.openrouter_key = "sk-literal-value"
    assert cli.main(["--agent"]) == 2
    assert "sbx secret set openrouter" in capsys.readouterr().err
    assert _exec_calls(fake_sbx) == []


def test_compile_refuses_to_start_when_credentials_are_not_ready(tmp_path, isolated_state, fake_sbx, capsys):
    fake_sbx.openrouter_key = "sk-literal-value"
    assert cli.main(["-o", str(tmp_path / "out"), str(_md(tmp_path))]) == 2
    assert "sbx secret set openrouter" in capsys.readouterr().err
    assert fake_sbx.turn_argvs == []


def test_compile_uses_the_agents_own_sbx_minimum(tmp_path, isolated_state, fake_sbx, capsys, monkeypatch):
    newer = agents.Agent(
        name="pi",
        min_sbx_version=(0, 45, 0),
        compile_args=agents.PI.compile_args,
        interactive_args=agents.PI.interactive_args,
        compile_prompt=agents.PI.compile_prompt,
        check_credentials=agents.PI.check_credentials,
        protocol=agents.PI.protocol,
    )
    monkeypatch.setitem(agents.AGENTS, "pi", newer)
    fake_sbx.version_string = "0.44.0"
    assert cli.main(["-o", str(tmp_path / "out"), str(_md(tmp_path))]) == 2
    assert "at least version 0.45.0" in capsys.readouterr().err


def test_shell_creates_the_sandbox_before_entering_it(isolated_state, fake_sbx, a_tty):
    with pytest.raises(ExecvpCalled):
        cli.main(["--shell"])

    shapes = [c[:3] for c in fake_sbx.calls]
    assert ["sbx", "run", "--detached"] in shapes
    assert shapes.index(["sbx", "run", "--detached"]) < shapes.index(["sbx", "exec", "-it"])


def test_interactive_holds_the_lock_through_process_replacement(
    monkeypatch, isolated_state, fake_sbx, a_tty
):
    """Both halves of the guarantee, because either alone leaves it broken.

    The lock must still be held when execvp is called, or a compile could
    start between setup and hand-over; and the call must ask for
    survive_exec, or the flock dies with this process image and the session
    that replaces it runs unprotected. Only the first is observable in
    process, so the second is asserted on the call.

    real_lock is used inside the fake exec so that probe does not land in the
    recorded kwargs.
    """
    real_lock = workbench.lock
    lock_kwargs = []

    def spy(**kwargs):
        lock_kwargs.append(kwargs)
        return real_lock(**kwargs)

    monkeypatch.setattr(workbench, "lock", spy)
    observed = False

    def execvp_while_locked(_file, argv):
        nonlocal observed
        with pytest.raises(workbench.LockHeld), real_lock():
            pass
        observed = True
        raise ExecvpCalled(list(argv))

    monkeypatch.setattr(sandbox.os, "execvp", execvp_while_locked)
    with pytest.raises(ExecvpCalled):
        cli.main(["--shell"])

    assert observed
    assert lock_kwargs == [{"survive_exec": True}]
    with real_lock():  # The fake exec raised, so the context released it.
        pass


@pytest.mark.parametrize("flag", ["--shell", "--agent"])
def test_interactive_never_mounts_an_empty_spec(flag, isolated_state, fake_sbx, a_tty):
    """Regression: a never-compiled workbench handed the agent a 0-byte SPEC.md."""
    with pytest.raises(ExecvpCalled):
        cli.main([flag])

    work_spec = isolated_state / "xdg-state" / "md2okf" / "pi" / "work" / "SPEC.md"
    assert work_spec.stat().st_size > 0
    assert b"**Version" in work_spec.read_bytes()


@pytest.mark.parametrize("flag", ["--shell", "--agent"])
def test_interactive_reports_an_unreadable_spec_rather_than_raising(
    flag, capsys, monkeypatch, isolated_state, fake_sbx, a_tty
):
    """A packaged spec that cannot be read is a diagnostic and exit 2, not a traceback."""
    monkeypatch.setattr(resources, "spec_md", lambda: isolated_state / "missing" / "SPEC.md")

    assert cli.main([flag]) == 2
    assert "md2okf: staging the sandbox tooling failed" in capsys.readouterr().err


def test_shell_with_fresh_recreates_the_sandbox_before_entering_it(isolated_state, fake_sbx, a_tty):
    for argv in (["--shell"], ["--shell", "--fresh"]):
        with pytest.raises(ExecvpCalled):
            cli.main(argv)

    run_calls = [c for c in fake_sbx.calls if c[:3] == ["sbx", "run", "--detached"]]
    assert len(run_calls) == 2  # the second entry reused nothing


def test_shell_reports_when_another_run_holds_the_lock(capsys, isolated_state, fake_sbx, a_tty):
    """Regression: the interactive path needs its own LockHeld handler.

    main()'s sits inside the compile-path try, which the early return never
    enters, so a held lock would otherwise escape as a traceback.
    """
    with workbench.lock():
        rc = cli.main(["--shell"])

    assert rc == 2
    assert "another md2okf run" in capsys.readouterr().err
    assert _exec_calls(fake_sbx) == []


def test_shell_does_not_read_stdin_when_no_paths_are_given(monkeypatch, isolated_state, fake_sbx, a_tty):
    """--shell must short-circuit before _resolve_inputs, which reads stdin."""

    def explode(_paths):
        raise AssertionError("--shell must not resolve documents")

    monkeypatch.setattr(cli.compile_mod, "resolve_documents", explode)
    with pytest.raises(ExecvpCalled):
        cli.main(["--shell"])


def test_shell_rejects_positional_paths(tmp_path, capsys, isolated_state, fake_sbx):
    rc = cli.main(["--shell", str(_md(tmp_path))])
    assert rc == 2
    assert "takes no FILE|DIR" in capsys.readouterr().err
    assert fake_sbx.calls == []


def test_shell_rejects_compile_only_options(capsys, isolated_state, fake_sbx):
    for option in (["-o", "wikis/x"], ["--spec", "S.md"], ["-n", "3"], ["-q"], ["-v"], ["--dry-run"]):
        rc = cli.main(["--shell", *option])
        assert rc == 2, option
        assert "has no meaning with --shell" in capsys.readouterr().err, option
    assert fake_sbx.calls == []


def test_shell_and_agent_together_are_rejected(capsys):
    with pytest.raises(SystemExit) as excinfo:
        cli.main(["--shell", "--agent"])
    assert excinfo.value.code == 2
    assert "not allowed with" in capsys.readouterr().err


def test_interactive_entry_without_a_tty_touches_no_sandbox(capsys, isolated_state, fake_sbx):
    """`sbx exec -it` cannot work without a terminal, so refuse before the lifecycle.

    Checked here rather than left to sbx because ensure_sandbox() runs first:
    failing later would mean a sandbox built for nothing, or with --fresh a
    working one destroyed and rebuilt.
    """
    for flag in ("--shell", "--agent"):
        rc = cli.main([flag])  # no a_tty fixture: pytest's stdin is not a terminal
        assert rc == 2, flag
        assert "needs a terminal" in capsys.readouterr().err, flag
    assert fake_sbx.calls == []
