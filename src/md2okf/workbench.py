"""The workbench: a fixed staging area for one sandbox to serve any run.

It reproduces the sibling layout `kits/md2okf`'s agent config assumes for
whatever -o/inputs a run is given. See .claude/plans/interface-plan.md,
"The workbench".
"""

from __future__ import annotations

import contextlib
import fcntl
import hashlib
import os
import shutil
import stat
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from md2okf import resources, sandbox

LOCK_PATH_TEMPLATE = "/tmp/md2okf-{uid}.lock"  # noqa: S108 -- deliberately outside XDG_STATE_HOME
SANDBOX_NAME = "md2okf"


class WorkbenchError(Exception):
    """A checked failure preparing, staging, or mirroring the workbench."""


class UnsafeLockFile(WorkbenchError):
    """The per-user lock path is not a regular file this user owns."""


class LockHeld(WorkbenchError):
    """Another md2okf run already holds the sandbox lock."""


class UnownedSandboxError(WorkbenchError):
    """A sandbox called `name` exists but cannot be proven to be ours.

    Never auto-deleted -- the fix is the removal command in the message.
    """

    def __init__(self, name: str) -> None:
        """Build the message naming the manual removal command."""
        super().__init__(
            f"a sandbox called {name!r} exists but is not recognisably ours; "
            f"remove it yourself first: sbx rm --force {name}"
        )
        self.name = name


class KeyNotProxyManagedError(WorkbenchError):
    """OPENROUTER_API_KEY inside a freshly created sandbox is not proxy-managed."""

    def __init__(self, name: str) -> None:
        """Build the message naming the two `sbx secret` remediation commands.

        Regression: this used to name `sbx secret set github ...` -- the
        wrong provider entirely, copied from an unrelated GitHub-auth
        pattern. The actual two-step OpenRouter setup is README.md's
        "Set up the OpenRouter key" section.
        """
        super().__init__(
            f"OPENROUTER_API_KEY inside {name!r} is not proxy-managed.\n"
            "  Set it via sbx secret (see README.md, \"Set up the OpenRouter key\"):\n"
            '  echo "$OPENROUTER_API_KEY" | sbx secret set openrouter\n'
            f"  sbx secret set-custom --sandbox {name} --host openrouter.ai "
            '--env OPENROUTER_API_KEY --value "$OPENROUTER_API_KEY"'
        )
        self.name = name


class MirrorError(WorkbenchError):
    """Mirroring the wiki out to -o DIR failed; the good copy stays here."""

    def __init__(self, message: str, workbench_path: Path) -> None:
        """Record where the still-good copy of the wiki was left."""
        super().__init__(message)
        self.workbench_path = workbench_path


def state_home() -> Path:
    """XDG_STATE_HOME with its documented precedence.

    An exported absolute value wins, a relative value counts as unset, and
    the default is ~/.local/state.
    """
    raw = os.environ.get("XDG_STATE_HOME", "")
    if raw and Path(raw).is_absolute():
        return Path(raw)
    return Path.home() / ".local" / "state"


@contextlib.contextmanager
def lock():
    """Acquire the non-blocking, per-user sandbox lock.

    Raises LockHeld immediately rather than queueing behind another run.
    Deliberately not under XDG_STATE_HOME: two shells with different
    XDG_STATE_HOME values must still race on the one lock, not take two.

    That fixed, predictable path sits in a world-writable directory, so the
    file it names is not trusted until it has been checked: O_NOFOLLOW refuses
    a symlink another user planted there, and the fstat that follows refuses a
    FIFO or a file somebody else owns -- which would otherwise let them hold
    this lock for ever, or drop it and let two of our own runs share the one
    sandbox. Both are refusals, never a silent unlink: removing a file we do
    not own is the caller's decision, not ours.
    """
    path = Path(LOCK_PATH_TEMPLATE.format(uid=os.getuid()))
    try:
        fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    except OSError as exc:
        raise UnsafeLockFile(f"cannot open the lock file {path}: {exc.strerror}; remove it and retry") from exc
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode):
            raise UnsafeLockFile(f"the lock path {path} is not a regular file; remove it and retry")
        if info.st_uid != os.getuid():
            raise UnsafeLockFile(f"the lock file {path} is owned by uid {info.st_uid}, not by you; remove it and retry")
    except BaseException:
        os.close(fd)
        raise
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise LockHeld(str(path)) from exc
        yield
    finally:
        with contextlib.suppress(OSError):
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


@dataclass(frozen=True)
class Workbench:
    """The fixed staging layout for one host, rooted at state_home()/md2okf."""

    root: Path

    @classmethod
    def default(cls) -> Workbench:
        """The workbench rooted at the current XDG_STATE_HOME."""
        return cls(root=state_home() / "md2okf")

    @property
    def work(self) -> Path:
        """Parent of the three workspace-backed mounts; never mounted itself."""
        return self.root / "work"

    @property
    def work_okf(self) -> Path:
        """The primary, read-write mount: the wiki, mirrored to/from -o DIR."""
        return self.work / "okf"

    @property
    def work_md(self) -> Path:
        """Read-only mount: this run's staged input documents."""
        return self.work / "md"

    @property
    def work_scripts(self) -> Path:
        """Read-only mount: the four helper CLI projects."""
        return self.work / "scripts"

    @property
    def work_spec(self) -> Path:
        """Read-only mount: the OKF spec for this run."""
        return self.work / "SPEC.md"

    @property
    def sessions(self) -> Path:
        """Read-write mount: Pi's persistent transcripts. The only mounted state path."""
        return self.root / "sessions"

    @property
    def fingerprint_path(self) -> Path:
        """Host-only: the last successful create's configuration fingerprint."""
        return self.root / "sandbox-fingerprint"

    @property
    def identity_path(self) -> Path:
        """Host-only: the last successful create's recorded sandbox identity."""
        return self.root / "sandbox-identity"

    def mounts(self) -> list[sandbox.Mount]:
        """The five `sbx run` workspace arguments, in the fixed order."""
        return [
            sandbox.Mount(self.work_okf),
            sandbox.Mount(self.work_md, readonly=True),
            sandbox.Mount(self.work_scripts, readonly=True),
            sandbox.Mount(self.work_spec, readonly=True),
            sandbox.Mount(self.sessions),
        ]

    def ensure_roots(self) -> None:
        """Create the five mount sources if missing; never replace one that exists.

        Must run before the first `sbx run` -- sbx cannot mount a path that
        does not exist -- and never again touches these root objects, only
        their contents (see restage()).
        """
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        os.chmod(self.root, 0o700)
        self.work.mkdir(mode=0o700, exist_ok=True)
        self.work_okf.mkdir(mode=0o700, exist_ok=True)
        self.work_md.mkdir(mode=0o700, exist_ok=True)
        self.work_scripts.mkdir(mode=0o700, exist_ok=True)
        if not self.work_spec.exists():
            self.work_spec.touch(mode=0o600)
        self.sessions.mkdir(mode=0o700, exist_ok=True)


def reject_if_unsafe(path: Path, *, what: str) -> None:
    """Reject a symlink or special file (device, socket, FIFO) at `path`.

    A missing path is not an error here -- callers that need existence check
    it themselves with a clearer message.
    """
    try:
        info = path.lstat()
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode):
        raise WorkbenchError(f"{what} may not be a symlink: {path}")
    if not (stat.S_ISREG(info.st_mode) or stat.S_ISDIR(info.st_mode)):
        raise WorkbenchError(f"{what} may not be a device, socket, or FIFO: {path}")


def check_no_overlap(paths: Iterable[Path]) -> None:
    """Refuse when any two of `paths`, resolved, are equal or one nests the other.

    Without this, an output inside an input (or either inside the
    workbench) would become a recursive copy or a run that eats its own
    output.
    """
    originals = list(paths)
    resolved = [p.resolve() for p in originals]
    for i in range(len(resolved)):
        for j in range(len(resolved)):
            if i != j and (resolved[i] == resolved[j] or resolved[j] in resolved[i].parents):
                raise WorkbenchError(f"paths overlap: {originals[i]} and {originals[j]}")


def has_markdown(directory: Path) -> bool:
    """Whether `directory` contains at least one *.md file, at any depth."""
    return next(directory.rglob("*.md"), None) is not None


def _clear_children(root: Path) -> None:
    for child in root.iterdir():
        if child.is_symlink() or child.is_file():
            child.unlink()
        else:
            shutil.rmtree(child)


def _copy_tree_children(src: Path, dst: Path) -> None:
    for child in sorted(src.iterdir()):
        reject_if_unsafe(child, what="a mirrored source entry")
        target = dst / child.name
        if child.is_dir():
            target.mkdir()
            _copy_tree_children(child, target)
        else:
            shutil.copy2(child, target)


def sync_children(src: Path | None, dst: Path) -> None:
    """Make dst's children exactly mirror src's, without replacing dst itself.

    `src=None` (or a missing path) empties dst. Never creates or follows a
    symlink; a symlink or special file met while clearing dst is removed by
    name, never through it, and one met while copying from src is rejected.
    """
    _clear_children(dst)
    if src is not None and src.exists():
        reject_if_unsafe(src, what="a mirror source")
        _copy_tree_children(src, dst)


def stage_inputs(work_md: Path, items: Iterable[tuple[str, Path | bytes]]) -> None:
    """Clear work_md and copy each (basename, source) pair into it.

    `source` is a filesystem path to copy, or raw bytes (stdin's content,
    staged as stdin.md).
    """
    _clear_children(work_md)
    for basename, source in items:
        target = work_md / basename
        if isinstance(source, bytes):
            target.write_bytes(source)
        else:
            reject_if_unsafe(source, what="an input document")
            shutil.copy2(source, target)


def stage_clis(clis_root: Path, work_scripts: Path) -> None:
    """Stage the four helper CLI projects into work_scripts.

    Only pyproject.toml and src/ per project, mirroring what the installed
    package ships (see "Packaging" in the plan) -- never a project's .venv,
    caches, tests, or lockfile, which the checkout's scripts/ carries but a
    sandboxed `uv tool run --from` never needs. This is what keeps a stray
    .venv symlink from ever reaching sync_children's symlink rejection.
    """
    _clear_children(work_scripts)
    if not clis_root.exists():
        return
    for project in sorted(clis_root.iterdir()):
        if not project.is_dir() or project.is_symlink():
            continue
        pyproject = project / "pyproject.toml"
        src = project / "src"
        if not pyproject.is_file() or not src.is_dir():
            continue
        reject_if_unsafe(pyproject, what="a helper CLI's pyproject.toml")
        target = work_scripts / project.name
        target.mkdir()
        shutil.copy2(pyproject, target / "pyproject.toml")
        target_src = target / "src"
        target_src.mkdir()
        _copy_tree_children(src, target_src)


def rewrite_spec(work_spec: Path, spec_source: Path) -> None:
    """Rewrite work_spec's content in place -- truncate and write, never rename over it."""
    reject_if_unsafe(spec_source, what="--spec")
    work_spec.write_bytes(spec_source.read_bytes())


def mirror_in(work_okf: Path, output_dir: Path) -> None:
    """Mirror -o DIR into work_okf, so an existing wiki is continued, not restarted."""
    sync_children(output_dir if output_dir.exists() else None, work_okf)


def mirror_out(work_okf: Path, output_dir: Path) -> None:
    """Mirror work_okf back out to -o DIR. A failure here is a failed run."""
    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        sync_children(work_okf, output_dir)
    except OSError as exc:
        # The workbench path is folded into the message itself, not left as
        # an attribute a caller has to know to read: str(exc) is what every
        # caller actually prints, and the whole point of naming it is that
        # the completed work is recoverable from there.
        raise MirrorError(
            f"mirroring the wiki out to {output_dir} failed: {exc}; the completed work is still at {work_okf}",
            work_okf,
        ) from exc


def restage(
    wb: Workbench,
    *,
    inputs: Iterable[tuple[str, Path | bytes]],
    clis_dir: Path,
    spec_source: Path,
    output_dir: Path,
) -> None:
    """Refill the workbench's children for one run.

    Never replaces the five mount root objects (see Workbench.ensure_roots);
    only their contents change, which is why one sandbox can serve any number
    of runs against different inputs and outputs. Any OSError along the way
    (disk full, a permission error) becomes a WorkbenchError, so a caller
    that only catches WorkbenchError still gets a clean failure rather than
    a bare traceback.
    """
    try:
        stage_inputs(wb.work_md, inputs)
        stage_clis(clis_dir, wb.work_scripts)
        rewrite_spec(wb.work_spec, spec_source)
        mirror_in(wb.work_okf, output_dir)
    except OSError as exc:
        raise WorkbenchError(f"staging the workbench failed: {exc}") from exc


def is_adoptable_output(output_dir: Path) -> bool:
    """Whether -o DIR may be adopted: missing, empty, or a recognised OKF bundle root.

    Mirroring out propagates deletions, so anything else is refused outright
    -- adoption is proved, never guessed. The symlink check must come before
    exists()/is_dir(), which follow a symlink rather than report it: a
    *dangling* symlink named as -o would otherwise read as "missing" and
    slip through as adoptable.
    """
    if output_dir.is_symlink():
        return False
    if not output_dir.exists():
        return True
    if not output_dir.is_dir():
        return False
    if not any(output_dir.iterdir()):
        return True
    return _is_okf_bundle_root(output_dir)


def _is_okf_bundle_root(output_dir: Path) -> bool:
    index = output_dir / "index.md"
    if not index.is_file() or index.is_symlink():
        return False
    frontmatter = _parse_simple_frontmatter(index.read_text(encoding="utf-8"))
    return frontmatter is not None and list(frontmatter) == ["okf_version"]


def _parse_simple_frontmatter(text: str) -> dict[str, str] | None:
    """A minimal, flat `key: value` frontmatter reader.

    Just enough to check the bundle-root marker (OKF spec §12) without a
    YAML dependency -- md2okf is stdlib-only at runtime.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    result: dict[str, str] = {}
    for line in lines[1:]:
        stripped = line.strip()
        if stripped == "---":
            return result
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            return None
        key, _, value = stripped.partition(":")
        result[key.strip()] = value.strip()
    return None


def _hash_tree(root: Path) -> str:
    """Hash every regular file under root, keyed by its relative path.

    Skips dotfiles/dotdirs and __pycache__ at any depth -- editor droppings
    (.DS_Store) or bytecode left by running kits/md2okf's own
    frontmatter-guard.py locally must not move the fingerprint and force an
    unnecessary sandbox rebuild.
    """
    digest = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root)
        if any(part.startswith(".") or part == "__pycache__" for part in relative.parts):
            continue
        if path.is_file() and not path.is_symlink():
            digest.update(str(relative).encode("utf-8"))
            digest.update(path.read_bytes())
    return digest.hexdigest()


def fingerprint(kit_dir: Path, sbx_version: tuple[int, int, int] | None, mounts: Iterable[sandbox.Mount]) -> str:
    """A configuration fingerprint: kit tree hash + tool version + mount set."""
    parts = [
        _hash_tree(kit_dir),
        ".".join(str(part) for part in (sbx_version or (0, 0, 0))),
        "\n".join(mount.as_arg() for mount in mounts),
    ]
    return hashlib.sha256("\x00".join(parts).encode("utf-8")).hexdigest()


def _atomic_write(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, path)


def write_ownership_marker(wb: Workbench, fingerprint_value: str, identity_value: str) -> None:
    """Record a successful create's fingerprint and identity. Only call this after create() succeeds."""
    _atomic_write(wb.fingerprint_path, fingerprint_value)
    _atomic_write(wb.identity_path, identity_value)


def read_ownership_marker(wb: Workbench) -> tuple[str, str] | None:
    """The last recorded (fingerprint, identity), or None if never written."""
    if not (wb.fingerprint_path.is_file() and wb.identity_path.is_file()):
        return None
    fingerprint_value = wb.fingerprint_path.read_text(encoding="utf-8").strip()
    identity_value = wb.identity_path.read_text(encoding="utf-8").strip()
    return fingerprint_value, identity_value


def resolve_sandbox_state(wb: Workbench, name: str, fingerprint_value: str, *, fresh: bool = False) -> str:
    """Decide "create" or "reuse" for `name`, proving ownership before reuse.

    Reuse requires the name to resolve to the same identity we recorded,
    the fingerprint to match, and a cheap in-VM probe to pass; anything
    else that still exists under this name raises UnownedSandboxError
    rather than being silently reused or deleted. --fresh recreates a
    sandbox we own; it never widens deletion authority.
    """
    if not sandbox.exists(name):
        return "create"

    marker = read_ownership_marker(wb)
    if marker is None:
        raise UnownedSandboxError(name)
    marker_fingerprint, marker_identity = marker
    current_identity = sandbox.identity(name)
    if current_identity is None or current_identity != marker_identity:
        raise UnownedSandboxError(name)

    if fresh:
        return "create"
    if marker_fingerprint != fingerprint_value:
        return "create"
    if not sandbox.probe(name, wb.work_okf):
        return "create"
    return "reuse"


def _clear_ownership_marker(wb: Workbench) -> None:
    """Remove any existing marker before attempting a (re)creation.

    create()'s first step is `sbx rm --force`, so the moment we decide to
    (re)create, any marker already on disk describes a sandbox generation
    that is about to be torn down. Clearing it first means a failed
    create() leaves the state directory honestly reflecting "no proven
    sandbox" instead of a stale reference to a generation that no longer
    exists -- even though that staleness was never actually exploitable
    (resolve_sandbox_state re-checks exists() before ever reading the
    marker, and a torn-down sandbox reads as not existing).
    """
    wb.fingerprint_path.unlink(missing_ok=True)
    wb.identity_path.unlink(missing_ok=True)


def stage_tooling(wb: Workbench) -> None:
    """Stage the helper CLI projects the kit's shims resolve against.

    Deliberately not part of restage(): this content does not vary per run.
    It is the packaged CLI sources, identical for every invocation, whereas
    work/md, work/SPEC.md and work/okf are the run's own inputs and output.

    A sandbox whose work/scripts is empty still starts, and its mounts are
    still correct — but every inspectmd/inspectokf/sizeokf/merkleokf shim in
    it fails, because each one is `uv tool run --from
    $(dirname $WORKDIR)/scripts/<cli>` (kits/md2okf/spec.yaml). That makes
    this part of "the sandbox is usable", which is why ensure_sandbox() does
    it for every caller rather than leaving each one to remember.
    """
    stage_clis(resources.clis_dir(), wb.work_scripts)


def ensure_sandbox(wb: Workbench, *, fresh: bool = False) -> str:
    """Reuse or (re)create the sandbox named SANDBOX_NAME. Returns "reuse" or "created".

    Raises UnownedSandboxError, sandbox.SandboxError, or
    KeyNotProxyManagedError on failure. The ownership marker is written as
    soon as create() itself succeeds -- even if the key check that follows
    it fails -- so a sandbox we really did create is always recognised as
    ours on the next run, rather than forcing a manual `sbx rm --force`
    just because a secret was not yet configured.
    """
    name = SANDBOX_NAME
    kit_dir = resources.kit_dir()
    fingerprint_value = fingerprint(kit_dir, sandbox.version(), wb.mounts())

    # Before the sandbox exists, so it never observes an empty scripts mount.
    # Unconditional rather than create-only: a reused sandbox whose staged
    # tooling was wiped must get it back too.
    stage_tooling(wb)

    state = resolve_sandbox_state(wb, name, fingerprint_value, fresh=fresh)
    if state == "reuse":
        return "reuse"

    _clear_ownership_marker(wb)
    token = sandbox.create(name, kit_dir, wb.mounts(), {"MD2OKF_STATE_DIR": str(wb.root)})
    write_ownership_marker(wb, fingerprint_value, token)
    if not sandbox.key_is_proxy_managed(name):
        raise KeyNotProxyManagedError(name)
    return "created"
