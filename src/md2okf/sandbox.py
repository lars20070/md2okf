"""The one seam onto the `sbx` CLI.

Every process this package spawns to talk to a sandbox goes through
:func:`_run` or :class:`Exec` in this module, and nowhere else — so a test
only ever needs to fake ``subprocess.run``/``subprocess.Popen`` once, at this
one boundary, to exercise everything above it.
"""

from __future__ import annotations

import re
import secrets
import shutil
import subprocess
import sys
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from pathlib import Path

MIN_VERSION = (0, 43, 0)

# This is the plan's own documented fallback (interface-plan.md, "Risks and
# open items"), not an invented deviation: which `sbx inspect` field (if any)
# is a stable sandbox identity is explicitly left unverified there, to be
# confirmed against a *live* sbx session in stage 3. Stage 2 is offline and
# has no sandbox to inspect, so it implements the fallback the plan already
# specifies instead of guessing at stage 3's job: a random token written into
# the guest at creation and read back on reuse.
#
# Threat model: the token is guest-writable, so it is not proof against a
# guest that deliberately tries to impersonate ownership. It only needs to
# answer "did *we* create this sandbox" against accidental reuse (a stale
# sandbox from a prior run, an unrelated sandbox that happens to hold this
# name) — and resolve_sandbox_state() always compares the *live* token against
# the one recorded at creation, so a missing or altered token can only cause a
# false *rejection* (fails safe: exit 2, "sbx rm --force"), never a false
# acceptance of a sandbox we did not create.
#
# Inside the guest VM only — never a host path, so this is not a shared-tmp
# race on the host. Random per creation (see create()), so a stale file left
# by an unrelated image could never be mistaken for our own.
OWNER_TOKEN_PATH = "/tmp/md2okf-owner"  # noqa: S108


class SandboxError(Exception):
    """A checked failure talking to `sbx`."""


def _run(argv: list[str], *, stdin: int | None = subprocess.DEVNULL) -> subprocess.CompletedProcess[str]:
    """Run `argv` and capture it. The only place this module calls subprocess.run."""
    return subprocess.run(argv, stdin=stdin, capture_output=True, text=True, check=False)  # noqa: S603


def present() -> bool:
    """Whether the `sbx` executable exists on PATH."""
    return shutil.which("sbx") is not None


def version() -> tuple[int, int, int] | None:
    """Parsed (major, minor, patch) from `sbx version`, or None if unparsable."""
    result = _run(["sbx", "version"])
    if result.returncode != 0:
        return None
    match = re.search(r"(\d+)\.(\d+)\.(\d+)", result.stdout)
    if not match:
        return None
    major, minor, patch = (int(part) for part in match.groups())
    return (major, minor, patch)


def version_at_least(minimum: tuple[int, int, int] = MIN_VERSION) -> bool:
    """Whether `sbx version` is at least `minimum`."""
    found = version()
    return found is not None and found >= minimum


def logged_in() -> bool:
    """`sbx ls` succeeding is what a logged-in session looks like."""
    return _run(["sbx", "ls"]).returncode == 0


def preflight() -> None:
    """Check the sbx environment before anything that would shell out to it.

    Every other function in this module assumes `sbx` is on PATH: `_run`
    calls `subprocess.run(["sbx", ...])` directly, which raises a bare
    FileNotFoundError (not SandboxError) if it is missing. Callers -- cli.py
    and `python -m md2okf.sandbox` alike -- must call this first and turn
    SandboxError into a clean exit, or a missing `sbx` crashes instead.
    """
    if not present():
        raise SandboxError("'sbx' CLI not found in PATH. Install it with: brew install docker/tap/sbx")
    if not version_at_least():
        minimum = ".".join(str(part) for part in MIN_VERSION)
        raise SandboxError(f"sbx must be at least version {minimum}")
    if not logged_in():
        raise SandboxError("not logged in to sbx; run `sbx login`")


def exists(name: str) -> bool:
    """Whether a sandbox called `name` currently exists."""
    result = _run(["sbx", "ls", "-q"])
    return name in result.stdout.splitlines()


@dataclass(frozen=True)
class Mount:
    """One `sbx run` workspace argument."""

    path: Path
    readonly: bool = False

    def as_arg(self) -> str:
        """The positional argument `sbx run` expects for this mount."""
        return f"{self.path}:ro" if self.readonly else str(self.path)


def create(name: str, kit_dir: Path, mounts: Iterable[Mount], env: dict[str, str]) -> str:
    """Recreate `name` over `mounts`, and return its fresh owner token.

    Tolerates a prior sandbox by this name not existing, mirroring today's
    `sbx rm --force ... || true`. Raises SandboxError on any failure from here
    on — a failed create must leave no ownership marker (see workbench.py).
    """
    _run(["sbx", "rm", "--force", name])

    argv = ["sbx", "run", "--detached", "--name", name]
    for key, value in env.items():
        argv += ["-e", f"{key}={value}"]
    argv.append(str(kit_dir))
    argv += [mount.as_arg() for mount in mounts]
    result = _run(argv)
    if result.returncode != 0:
        raise SandboxError(f"sbx run failed for {name!r}: {result.stderr.strip()}")

    token = secrets.token_hex(16)
    written = _run(["sbx", "exec", name, "--", "sh", "-c", f"echo {token} >{OWNER_TOKEN_PATH}"])
    if written.returncode != 0:
        # sbx run just succeeded, so name now exists but carries no owner
        # token -- left alone, the next invocation would see it as an
        # unowned sandbox and demand a manual `sbx rm --force`, even though
        # we are the ones who just created it moments ago. Clean up after
        # ourselves instead.
        _run(["sbx", "rm", "--force", name])
        raise SandboxError(f"could not record an ownership token in {name!r}: {written.stderr.strip()}")
    return token


def identity(name: str) -> str | None:
    """The owner token left inside `name` at creation, or None if unreadable.

    None covers both "no such sandbox" and "exists but is not ours" (no token
    file) — either way, it cannot be recognised as a sandbox we created.
    """
    result = _run(["sbx", "exec", name, "--", "cat", OWNER_TOKEN_PATH])
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def remove(name: str) -> None:
    """Delete the sandbox called `name`. Only call this on one we own."""
    _run(["sbx", "rm", "--force", name])


def probe(name: str, path: Path) -> bool:
    """A cheap in-VM check that `path` (a workbench mount) is visible in `name`."""
    return _run(["sbx", "exec", name, "--", "test", "-d", str(path)]).returncode == 0


def key_is_proxy_managed(name: str) -> bool:
    """Whether OPENROUTER_API_KEY inside `name` is the proxy-managed sentinel."""
    result = _run(["sbx", "exec", name, "--", "sh", "-lc", 'echo "$OPENROUTER_API_KEY"'])
    return result.returncode == 0 and result.stdout.strip() == "proxy-managed"


class Exec:
    """One streamed `sbx exec`: iterate stdout+stderr lines, then read .returncode."""

    def __init__(self, argv: list[str]) -> None:
        """Start `argv`, ready to iterate over its combined stdout+stderr."""
        self.argv = argv
        self.returncode: int | None = None
        self._proc = subprocess.Popen(  # noqa: S603
            argv,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

    def __iter__(self) -> Iterator[str]:
        """Yield each line as it arrives; sets .returncode once exhausted."""
        assert self._proc.stdout is not None  # noqa: S101
        for line in self._proc.stdout:
            yield line.rstrip("\n")
        self.returncode = self._proc.wait()


def exec_stream(name: str, argv: list[str]) -> Exec:
    """Run `argv` inside `name`, streamed. stdin is always /dev/null — see compile.py."""
    return Exec(["sbx", "exec", name, "--", *argv])


def exec_capture(name: str, argv: list[str]) -> subprocess.CompletedProcess[str]:
    """Run a short `argv` inside `name` and capture it whole (e.g. a hash check)."""
    return _run(["sbx", "exec", name, "--", *argv])


def _ensure_default_sandbox() -> int:
    """`python -m md2okf.sandbox`: ensure the md2okf sandbox exists (maintainers).

    Imports workbench lazily: workbench imports this module at its own top
    level, and by the time this function runs (only from the `__main__`
    guard below) that import has already completed, so the late import here
    just retrieves it from sys.modules rather than re-entering it.
    """
    from md2okf import workbench

    try:
        preflight()
    except SandboxError as exc:
        print(f"md2okf.sandbox: {exc}", file=sys.stderr)
        return 2

    wb = workbench.Workbench.default()
    try:
        # Same lock a real compile run takes: this helper touches the same
        # sandbox, so it must not race a concurrent `md2okf` invocation.
        with workbench.lock():
            wb.ensure_roots()
            state = workbench.ensure_sandbox(wb)
    except workbench.LockHeld:
        print("md2okf.sandbox: another md2okf run is using the sandbox; try again later", file=sys.stderr)
        return 2
    except (workbench.UnownedSandboxError, workbench.KeyNotProxyManagedError, SandboxError) as exc:
        print(f"md2okf.sandbox: {exc}", file=sys.stderr)
        return 2
    print(f"md2okf.sandbox: sandbox {workbench.SANDBOX_NAME!r} {state}")
    return 0


if __name__ == "__main__":
    raise SystemExit(_ensure_default_sandbox())
