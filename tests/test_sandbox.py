"""Tests for md2okf.sandbox — the one seam onto `sbx`, against FakeSbx."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2okf import sandbox, workbench


def test_present_reflects_path(monkeypatch):
    monkeypatch.setattr(sandbox.shutil, "which", lambda _name: "/usr/bin/sbx")
    assert sandbox.present() is True
    monkeypatch.setattr(sandbox.shutil, "which", lambda _name: None)
    assert sandbox.present() is False


def test_fake_sbx_covers_presence_not_only_subprocess(fake_sbx):
    """Regression: the fixture faked subprocess but not shutil.which.

    present() then answered from the developer's own PATH, so every test
    reaching preflight() passed locally (sbx installed) and failed in CI
    (sbx absent) without touching a single faked subprocess call. The
    fixture has to cover the whole seam for the suite to be offline.
    """
    assert sandbox.present() is True
    sandbox.preflight()  # must not raise, whatever the host has installed


def test_version_parses_and_compares(fake_sbx):
    fake_sbx.version_string = "0.43.0"
    assert sandbox.version() == (0, 43, 0)
    assert sandbox.version_at_least() is True

    fake_sbx.version_string = "0.42.9"
    assert sandbox.version_at_least() is False


def test_version_unparsable_is_none(fake_sbx, monkeypatch):
    monkeypatch.setattr(
        sandbox.subprocess,
        "run",
        lambda *a, **k: __import__("subprocess").CompletedProcess(a[0], 0, "garbage\n", ""),
    )
    assert sandbox.version() is None
    assert sandbox.version_at_least() is False


def test_logged_in_reflects_ls(fake_sbx):
    fake_sbx.logged_in = True
    assert sandbox.logged_in() is True
    fake_sbx.logged_in = False
    assert sandbox.logged_in() is False


def test_exists_before_and_after_create(fake_sbx):
    assert sandbox.exists("md2okf") is False
    sandbox.create("md2okf", Path("/kit"), [], {})
    assert sandbox.exists("md2okf") is True


def test_create_returns_a_token_identity_reads_back(fake_sbx):
    token = sandbox.create("md2okf", Path("/kit"), [], {})
    assert token
    assert sandbox.identity("md2okf") == token


def test_create_mounts_and_env_reach_the_argv(fake_sbx):
    mounts = [sandbox.Mount(Path("/work/okf")), sandbox.Mount(Path("/work/md"), readonly=True)]
    sandbox.create("md2okf", Path("/kit"), mounts, {"SBXAGENT_STATE_DIR": "/state"})
    run_call = next(c for c in fake_sbx.calls if c[:3] == ["sbx", "run", "--detached"])
    assert run_call == [
        "sbx",
        "run",
        "--detached",
        "--name",
        "md2okf",
        "-e",
        "SBXAGENT_STATE_DIR=/state",
        "/kit",
        "/work/okf",
        "/work/md:ro",
    ]


def test_create_removes_any_prior_sandbox_first(fake_sbx):
    sandbox.create("md2okf", Path("/kit"), [], {})
    sandbox.create("md2okf", Path("/kit"), [], {})
    rm_calls = [c for c in fake_sbx.calls if c[:3] == ["sbx", "rm", "--force"]]
    assert len(rm_calls) == 2


def test_create_raises_on_sbx_run_failure(fake_sbx):
    fake_sbx.run_fail_names.add("md2okf")
    with pytest.raises(sandbox.SandboxError, match="md2okf"):
        sandbox.create("md2okf", Path("/kit"), [], {})


def test_create_removes_the_sandbox_when_the_token_write_fails(fake_sbx):
    """Regression (code review finding 3, related edge).

    `sbx run` succeeds, so the sandbox now exists; only the owner-token
    write fails. Left alone, the next invocation would see a real,
    token-less sandbox and demand a manual `sbx rm --force` for a sandbox
    we ourselves just created moments ago -- clean it up instead.
    """
    fake_sbx.token_write_fail_names.add("md2okf")
    with pytest.raises(sandbox.SandboxError, match="ownership token"):
        sandbox.create("md2okf", Path("/kit"), [], {})
    assert sandbox.exists("md2okf") is False


def test_identity_is_none_for_a_sandbox_that_is_not_ours(fake_sbx):
    fake_sbx.register("intruder")
    assert sandbox.identity("intruder") is None
    assert sandbox.identity("nonexistent") is None


def test_remove_deletes(fake_sbx):
    sandbox.create("md2okf", Path("/kit"), [], {})
    sandbox.remove("md2okf")
    assert sandbox.exists("md2okf") is False


def test_probe_reflects_configured_state(fake_sbx):
    sandbox.create("md2okf", Path("/kit"), [], {})
    fake_sbx.probe_ok = True
    assert sandbox.probe("md2okf", Path("/work/okf")) is True
    fake_sbx.probe_ok = False
    assert sandbox.probe("md2okf", Path("/work/okf")) is False


def test_key_is_proxy_managed(fake_sbx):
    sandbox.create("md2okf", Path("/kit"), [], {})
    fake_sbx.openrouter_key = "proxy-managed"
    assert sandbox.key_is_proxy_managed("md2okf") is True
    fake_sbx.openrouter_key = "sk-literal-value"
    assert sandbox.key_is_proxy_managed("md2okf") is False


def test_exec_capture_runs_through_the_seam(fake_sbx):
    sandbox.create("md2okf", Path("/kit"), [], {})
    fake_sbx.queue_hash("abc123456789")
    result = sandbox.exec_capture("md2okf", ["merkleokf", "--nolog", "-L", "0", "/work/okf"])
    assert result.returncode == 0
    assert "abc123456789" in result.stdout


def test_exec_stream_yields_lines_then_returncode(fake_sbx):
    sandbox.create("md2okf", Path("/kit"), [], {})
    fake_sbx.queue_pi(['{"type": "message_end"}', '{"type": "tool_execution_start"}'], returncode=0)
    stream = sandbox.exec_stream("md2okf", ["pi", "--mode", "json", "compile it"])
    lines = list(stream)
    assert lines == ['{"type": "message_end"}', '{"type": "tool_execution_start"}']
    assert stream.returncode == 0


def test_exec_stream_propagates_nonzero_returncode(fake_sbx):
    sandbox.create("md2okf", Path("/kit"), [], {})
    fake_sbx.queue_pi(["oops"], returncode=1)
    stream = sandbox.exec_stream("md2okf", ["pi", "--mode", "json", "compile it"])
    list(stream)
    assert stream.returncode == 1


# --- python -m md2okf.sandbox (maintainers) ---------------------------------


def test_ensure_default_sandbox_creates_and_reports(fake_sbx, isolated_state, capsys):
    assert sandbox._ensure_default_sandbox() == 0
    assert "created" in capsys.readouterr().out


def test_ensure_default_sandbox_reports_reuse_on_a_second_call(fake_sbx, isolated_state, capsys):
    sandbox._ensure_default_sandbox()
    capsys.readouterr()
    assert sandbox._ensure_default_sandbox() == 0
    assert "reuse" in capsys.readouterr().out


def test_ensure_default_sandbox_respects_the_run_lock(fake_sbx, isolated_state, capsys):
    """Regression.

    This maintainer helper touches the same sandbox as a real compile run
    but never took the lock, so it could race one.
    """
    with workbench.lock():
        assert sandbox._ensure_default_sandbox() == 2
    assert "another md2okf run" in capsys.readouterr().err


def test_ensure_default_sandbox_exits_2_on_an_unowned_sandbox(fake_sbx, isolated_state, capsys):
    fake_sbx.register("md2okf")
    assert sandbox._ensure_default_sandbox() == 2
    assert "sbx rm --force" in capsys.readouterr().err


def test_ensure_default_sandbox_exits_2_when_sbx_is_missing(isolated_state, capsys, monkeypatch):
    """Regression.

    This entry point skipped preflight() entirely, so a missing `sbx`
    crashed with a bare FileNotFoundError instead of exit 2.
    """
    monkeypatch.setattr(sandbox.shutil, "which", lambda _name: None)
    assert sandbox._ensure_default_sandbox() == 2
    assert "sbx" in capsys.readouterr().err


def test_preflight_raises_on_a_missing_sbx(monkeypatch):
    monkeypatch.setattr(sandbox.shutil, "which", lambda _name: None)
    with pytest.raises(sandbox.SandboxError, match="not found"):
        sandbox.preflight()


def test_preflight_raises_on_an_old_version(fake_sbx):
    fake_sbx.version_string = "0.10.0"
    with pytest.raises(sandbox.SandboxError, match="version"):
        sandbox.preflight()


def test_preflight_raises_when_not_logged_in(fake_sbx):
    fake_sbx.logged_in = False
    with pytest.raises(sandbox.SandboxError, match="logged in"):
        sandbox.preflight()


def test_preflight_passes_when_everything_is_fine(fake_sbx):
    sandbox.preflight()
