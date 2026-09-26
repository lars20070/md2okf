"""Tests for md2okf.sandbox — the one seam onto `sbx`, against FakeSbx."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from md2okf import agents, sandbox, workbench

PI_SANDBOX = workbench.sandbox_name("pi")


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
    sandbox.create("md2okf", Path("/kit"), mounts, {"MD2OKF_STATE_DIR": "/state"})
    run_call = next(c for c in fake_sbx.calls if c[:3] == ["sbx", "run", "--detached"])
    assert run_call == [
        "sbx",
        "run",
        "--detached",
        "--name",
        "md2okf",
        "-e",
        "MD2OKF_STATE_DIR=/state",
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
    fake_sbx.queue_turn(['{"type": "message_end"}', '{"type": "tool_execution_start"}'], returncode=0)
    stream = sandbox.exec_stream("md2okf", ["pi", "--mode", "json", "compile it"])
    lines = list(stream)
    assert lines == ['{"type": "message_end"}', '{"type": "tool_execution_start"}']
    assert stream.returncode == 0


def test_exec_stream_propagates_nonzero_returncode(fake_sbx):
    sandbox.create("md2okf", Path("/kit"), [], {})
    fake_sbx.queue_turn(["oops"], returncode=1)
    stream = sandbox.exec_stream("md2okf", ["pi", "--mode", "json", "compile it"])
    list(stream)
    assert stream.returncode == 1


# --- python -m md2okf.sandbox (maintainers) ---------------------------------


@pytest.mark.parametrize("env_value", [None, "pi"])
def test_ensure_default_sandbox_creates_and_reports(fake_sbx, isolated_state, capsys, monkeypatch, env_value):
    if env_value is not None:
        monkeypatch.setenv("MD2OKF_AGENT", env_value)
    assert sandbox._ensure_default_sandbox() == 0
    assert capsys.readouterr().out == f"md2okf.sandbox: sandbox {PI_SANDBOX!r} created\n"
    assert sandbox.exists(PI_SANDBOX)
    assert workbench.Workbench.default("pi").fingerprint_path.is_file()


def test_ensure_default_sandbox_follows_md2okf_agent_to_claude(fake_sbx, isolated_state, capsys, monkeypatch):
    """The maintainer entry point must never create or inspect a different sandbox from the CLI's."""
    monkeypatch.setenv("MD2OKF_AGENT", "claude")
    fake_sbx.version_string = "0.45.0"
    assert sandbox._ensure_default_sandbox() == 0
    assert capsys.readouterr().out == "md2okf.sandbox: sandbox 'md2okf-claude' created\n"
    assert sandbox.exists("md2okf-claude")
    assert not sandbox.exists(PI_SANDBOX)
    assert workbench.Workbench.default("claude").fingerprint_path.is_file()


def test_ensure_default_sandbox_refuses_an_unknown_agent_before_touching_sbx(
    fake_sbx, isolated_state, capsys, monkeypatch
):
    monkeypatch.setenv("MD2OKF_AGENT", "bogus")
    assert sandbox._ensure_default_sandbox() == 2
    assert "valid: claude, codex, pi" in capsys.readouterr().err
    assert fake_sbx.calls == []


def test_ensure_default_sandbox_uses_the_agents_own_sbx_minimum(fake_sbx, isolated_state, capsys, monkeypatch):
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
    fake_sbx.version_string = "0.43.0"

    assert sandbox._ensure_default_sandbox() == 2
    assert "at least version 0.45.0" in capsys.readouterr().err


def test_ensure_default_sandbox_exits_2_with_the_remedy_when_credentials_are_not_ready(
    fake_sbx, isolated_state, capsys
):
    fake_sbx.openrouter_key = "sk-literal-value"
    assert sandbox._ensure_default_sandbox() == 2
    assert "sbx secret set openrouter" in capsys.readouterr().err
    # Created and recorded as ours all the same, so fixing the secret is enough.
    assert workbench.read_ownership_marker(workbench.Workbench.default("pi")) is not None


def test_ensure_default_sandbox_stages_the_helper_clis(fake_sbx, isolated_state):
    """Regression, found by the live stage 3 run.

    This entry point created the mount roots and the sandbox but never
    staged work/scripts, so the sandbox came up with an empty scripts
    mount and all four kit shims — each `uv tool run --from
    $(dirname $WORKDIR)/scripts/<cli>` — failed inside the VM. The unit
    suite could not see it: the mounts were right and sbx was faked, so
    only a real sandbox running a real shim showed it.
    """
    assert sandbox._ensure_default_sandbox() == 0
    work_scripts = workbench.Workbench.default("pi").work_scripts
    for cli_name in ("inspectmd", "inspectokf", "sizeokf", "merkleokf"):
        assert (work_scripts / cli_name / "pyproject.toml").is_file()
        assert (work_scripts / cli_name / "src").is_dir()


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


def test_ensure_default_sandbox_exits_2_on_an_unusable_lock_file(
    fake_sbx, isolated_state, capsys, tmp_path, monkeypatch
):
    """Regression.

    This entry point takes the same lock as a compile run, but caught only
    LockHeld -- so a squatted lock path crashed here with a traceback while
    the CLI returned exit 2 with a message.
    """
    monkeypatch.setattr(workbench, "LOCK_PATH_TEMPLATE", str(tmp_path / "lock-{uid}.lock"))
    os.mkfifo(tmp_path / f"lock-{os.getuid()}.lock")

    assert sandbox._ensure_default_sandbox() == 2
    assert "not a regular file" in capsys.readouterr().err


def test_ensure_default_sandbox_exits_2_on_an_unowned_sandbox(fake_sbx, isolated_state, capsys):
    fake_sbx.register(PI_SANDBOX)
    assert sandbox._ensure_default_sandbox() == 2
    assert "sbx rm --force" in capsys.readouterr().err


def test_python_dash_m_reports_a_failed_sbx_run_as_exit_2(tmp_path):
    """Regression: `python -m md2okf.sandbox` crashed with a traceback when `sbx run` failed.

    Run with -m, the module is __main__ -- a second copy of md2okf.sandbox
    whose SandboxError is not the class workbench raises -- so nothing caught
    it. Only a real `python -m` shows this: every in-process test imports the
    one canonical module. A stand-in `sbx` on PATH keeps it offline.
    """
    fakebin = tmp_path / "bin"
    fakebin.mkdir()
    fake = fakebin / "sbx"
    fake.write_text(
        "#!/bin/sh\n"
        'case "$1" in\n'
        '  version) echo "sbx version 0.45.0" ;;\n'
        "  ls) exit 0 ;;\n"
        '  run) echo "boom: run refused" >&2; exit 1 ;;\n'
        "  *) exit 1 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    fake.chmod(0o755)
    env = {
        **os.environ,
        "PATH": f"{fakebin}{os.pathsep}{os.environ.get('PATH', '')}",
        "PYTHONPATH": str(Path(__file__).resolve().parents[1] / "src"),
        "XDG_STATE_HOME": str(tmp_path / "xdg"),
    }
    env.pop("MD2OKF_AGENT", None)

    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "md2okf.sandbox"],
        env=env,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 2, result.stderr
    assert "Traceback" not in result.stderr
    assert "sbx run failed for 'md2okf-pi': boom: run refused" in result.stderr


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


def test_preflight_checks_the_minimum_it_is_given(fake_sbx):
    fake_sbx.version_string = "0.44.0"
    sandbox.preflight()  # the default floor, 0.43.0
    with pytest.raises(sandbox.SandboxError, match=r"at least version 0\.45\.0"):
        sandbox.preflight((0, 45, 0))


def test_preflight_raises_when_not_logged_in(fake_sbx):
    fake_sbx.logged_in = False
    with pytest.raises(sandbox.SandboxError, match="logged in"):
        sandbox.preflight()


def test_preflight_passes_when_everything_is_fine(fake_sbx):
    sandbox.preflight()
