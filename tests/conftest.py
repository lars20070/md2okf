"""Shared pytest fixtures: a fake `sbx` standing in at the one real seam.

`md2okf.sandbox` is the only module that reaches the outside world, so faking
what it calls is enough to exercise every layer above it — workbench, compile,
cli — without ever shelling out to a real `sbx`.

That seam is four functions, not one: subprocess.run and subprocess.Popen,
*and* shutil.which, which `present()` uses to decide whether `sbx` exists at
all, *and* os.execvp, which the interactive `--shell`/`--agent` path uses.
Leaving which unfaked made the suite quietly depend on the developer's own
machine having sbx installed — green locally, seven failures in CI, where
nothing reaches a faked subprocess because preflight() bails first.
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from typing import NoReturn

import pytest

from md2okf import cli as cli_module
from md2okf import sandbox as sandbox_module
from md2okf import workbench as workbench_module


class ExecvpCalled(Exception):
    """Raised in place of os.execvp, which replaces the process and never returns.

    A fake that returned instead would exercise a path production does not
    have: after a real execvp this process is gone, so there is no "after".
    """

    def __init__(self, argv: list[str]) -> None:
        """Carry the full argv the caller would have exec'd."""
        super().__init__(" ".join(argv))
        self.argv = argv


@dataclass
class _Box:
    token: str | None = None


class _FakeStdout:
    """The line iterator, with a close() the driver's cleanup path can call."""

    def __init__(self, lines: list) -> None:
        self._lines = list(lines)
        self.closed = False

    def __iter__(self):
        for line in self._lines:
            # An exception in the queued lines is raised *during* iteration,
            # which is how a mid-stream KeyboardInterrupt (Ctrl-C while pi is
            # still talking) is reproduced.
            if isinstance(line, BaseException):
                raise line
            yield f"{line}\n"

    def close(self) -> None:
        self.closed = True


class FakePopen:
    """Stands in for subprocess.Popen for one streamed `sbx exec ... pi` call."""

    def __init__(self, lines: list, returncode: int) -> None:
        """Pre-load the lines a real Popen.stdout would yield, and the exit code."""
        self.stdout = _FakeStdout(lines)
        self._returncode = returncode
        self.finished = False
        self.terminated = False

    def wait(self) -> int:
        """Stand in for subprocess.Popen.wait()."""
        self.finished = True
        return self._returncode

    def poll(self) -> int | None:
        """None while still running, mirroring subprocess.Popen.poll()."""
        return self._returncode if self.finished else None

    def terminate(self) -> None:
        """Record that the driver stopped the conduit."""
        self.terminated = True
        self.finished = True


@dataclass
class FakeSbx:
    """A scriptable double for the `sbx` CLI, keyed off argv shape."""

    calls: list[list[str]] = field(default_factory=list)
    sandboxes: dict[str, _Box] = field(default_factory=dict)
    version_string: str = "0.43.0"
    logged_in: bool = True
    run_fail_names: set[str] = field(default_factory=set)
    token_write_fail_names: set[str] = field(default_factory=set)
    openrouter_key: str = "proxy-managed"
    probe_ok: bool = True
    last_popen: FakePopen | None = None
    _pi_queue: list[tuple[list, int, object]] = field(default_factory=list)
    _merkle_queue: list[tuple[str, int]] = field(default_factory=list)

    def register(self, name: str) -> None:
        """Register a sandbox that exists but was never created through us."""
        self.sandboxes[name] = _Box()

    def queue_pi(self, lines: list, returncode: int = 0, side_effect=None) -> None:
        """Queue one `pi --mode json` session's worth of raw stdout lines.

        `side_effect`, if given, runs with no arguments as this session
        "starts" -- e.g. writing a page into work/okf, standing in for what a
        real Pi run would leave on disk.
        """
        self._pi_queue.append((lines, returncode, side_effect))

    def queue_hash(self, digest: str, returncode: int = 0) -> None:
        """Queue one `merkleokf --nolog -L 0` response's root digest."""
        self._merkle_queue.append((digest, returncode))

    def run(  # noqa: PLR0911
        self,
        argv: list[str],
        *,
        stdin: object = None,
        capture_output: bool = True,
        text: bool = True,
        check: bool = False,
    ) -> subprocess.CompletedProcess[str]:
        """Stand in for subprocess.run."""
        self.calls.append(list(argv))

        def done(rc: int, out: str = "", err: str = "") -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(argv, rc, out, err)

        if argv[:2] == ["sbx", "version"]:
            return done(0, f"sbx version {self.version_string}\n")
        if argv[:2] == ["sbx", "ls"] and len(argv) == 2:
            return done(0 if self.logged_in else 1)
        if argv[:3] == ["sbx", "ls", "-q"]:
            return done(0, "".join(f"{name}\n" for name in self.sandboxes))
        if argv[:3] == ["sbx", "rm", "--force"]:
            existed = self.sandboxes.pop(argv[3], None) is not None
            return done(0 if existed else 1)
        if argv[:3] == ["sbx", "run", "--detached"]:
            name = argv[argv.index("--name") + 1]
            if name in self.run_fail_names:
                return done(1, "", "boom")
            self.sandboxes[name] = _Box()
            return done(0)
        if argv[:2] == ["sbx", "exec"]:
            return self._dispatch_exec_capture(argv)
        raise AssertionError(f"FakeSbx.run: unhandled argv {argv!r}")

    def _dispatch_exec_capture(self, argv: list[str]) -> subprocess.CompletedProcess[str]:  # noqa: PLR0911
        def done(rc: int, out: str = "", err: str = "") -> subprocess.CompletedProcess[str]:
            return subprocess.CompletedProcess(argv, rc, out, err)

        name = argv[2]
        tail = argv[argv.index("--") + 1 :]
        box = self.sandboxes.get(name)
        if box is None:
            return done(1, "", f"no such sandbox: {name}")
        if tail[:2] == ["sh", "-c"] and tail[2].startswith("echo "):
            if name in self.token_write_fail_names:
                return done(1, "", "disk full")
            box.token = tail[2].split()[1]
            return done(0)
        if tail == ["cat", sandbox_module.OWNER_TOKEN_PATH]:
            return done(0, f"{box.token}\n") if box.token else done(1)
        if tail[:2] == ["test", "-d"]:
            return done(0) if self.probe_ok else done(1)
        if tail[:2] == ["sh", "-lc"]:
            return done(0, f"{self.openrouter_key}\n")
        if tail[0] == "merkleokf":
            if not self._merkle_queue:
                raise AssertionError("no queued merkleokf response")
            digest, rc = self._merkle_queue.pop(0)
            table = f"Hash          Files  Path\n------------  -----  ----\n{digest}      1  okf/\n"
            return done(rc, table)
        raise AssertionError(f"FakeSbx.run(exec): unhandled tail {tail!r}")

    def popen(self, argv: list[str], **_kwargs: object) -> FakePopen:
        """Stand in for subprocess.Popen (streamed `sbx exec ... pi` only)."""
        self.calls.append(list(argv))
        tail = argv[argv.index("--") + 1 :]
        if tail[0] == "pi":
            if not self._pi_queue:
                raise AssertionError("no queued pi response")
            lines, rc, side_effect = self._pi_queue.pop(0)
            if side_effect is not None:
                side_effect()
            self.last_popen = FakePopen(lines, rc)
            return self.last_popen
        raise AssertionError(f"FakeSbx.popen: unhandled tail {tail!r}")

    def execvp(self, file: str, argv: list[str]) -> NoReturn:
        """Stand in for os.execvp (interactive `sbx exec -it`), which never returns."""
        self.calls.append(list(argv))
        raise ExecvpCalled(list(argv))


@pytest.fixture
def fake_sbx(monkeypatch: pytest.MonkeyPatch) -> FakeSbx:
    """Patch the seam md2okf.sandbox reaches the outside world through.

    A test that wants the opposite -- `sbx` absent -- re-patches `which`
    itself; a monkeypatch in the test body is applied after this fixture
    and so wins.

    execvp is patched unconditionally, not only for the tests that expect it:
    a bug that reached it during an unrelated test would otherwise replace the
    pytest process with an interactive shell.
    """
    fake = FakeSbx()
    monkeypatch.setattr(sandbox_module.subprocess, "run", fake.run)
    monkeypatch.setattr(sandbox_module.subprocess, "Popen", fake.popen)
    monkeypatch.setattr(sandbox_module.os, "execvp", fake.execvp)
    # Faked alongside the subprocess calls, so the suite is the same whether
    # or not the machine running it happens to have sbx installed.
    monkeypatch.setattr(sandbox_module.shutil, "which", lambda name: f"/usr/bin/{name}")
    return fake


@pytest.fixture
def a_tty(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make stdin look like a terminal, which --shell/--agent require.

    pytest replaces sys.stdin with a stand-in whose isatty() is False, so
    without this every interactive-entry test would be refused before it
    reached the behaviour it is there to check.
    """
    monkeypatch.setattr(cli_module.sys.stdin, "isatty", lambda: True)


@pytest.fixture
def isolated_state(tmp_path, monkeypatch: pytest.MonkeyPatch):
    """A private XDG_STATE_HOME and lock path, so tests never touch the real ones."""
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "xdg-state"))
    monkeypatch.setattr(workbench_module, "LOCK_PATH_TEMPLATE", str(tmp_path / "md2okf-{uid}.lock"))
    return tmp_path
