"""Tests for md2okf.workbench."""

from __future__ import annotations

import os
import shutil
import stat
from pathlib import Path

import pytest

from md2okf import resources, sandbox, workbench

# --- state_home() precedence -------------------------------------------------


def test_state_home_default(monkeypatch, tmp_path):
    monkeypatch.delenv("XDG_STATE_HOME", raising=False)
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert workbench.state_home() == tmp_path / ".local" / "state"


def test_state_home_absolute_export_wins(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", str(tmp_path / "custom"))
    assert workbench.state_home() == tmp_path / "custom"


def test_state_home_relative_value_counts_as_unset(monkeypatch, tmp_path):
    monkeypatch.setenv("XDG_STATE_HOME", "relative/path")
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    assert workbench.state_home() == tmp_path / ".local" / "state"


# --- the lock ------------------------------------------------------------


def test_lock_is_non_blocking_and_exclusive(monkeypatch, tmp_path):
    monkeypatch.setattr(workbench, "LOCK_PATH_TEMPLATE", str(tmp_path / "md2okf-{uid}.lock"))
    with workbench.lock(), pytest.raises(workbench.LockHeld), workbench.lock():
        pass


def test_lock_is_released_and_reusable(monkeypatch, tmp_path):
    monkeypatch.setattr(workbench, "LOCK_PATH_TEMPLATE", str(tmp_path / "md2okf-{uid}.lock"))
    with workbench.lock():
        pass
    with workbench.lock():
        pass


def test_lock_refuses_a_symlinked_lock_path(monkeypatch, tmp_path):
    """The path is predictable and lives in a world-writable directory.

    Without O_NOFOLLOW, a symlink planted there would be followed and opened
    read-write as us.
    """
    monkeypatch.setattr(workbench, "LOCK_PATH_TEMPLATE", str(tmp_path / "md2okf-{uid}.lock"))
    target = tmp_path / "victim"
    target.write_text("keep", encoding="utf-8")
    (tmp_path / f"md2okf-{os.getuid()}.lock").symlink_to(target)

    with pytest.raises(workbench.UnsafeLockFile), workbench.lock():
        pass
    assert target.read_text(encoding="utf-8") == "keep"


def test_lock_refuses_a_lock_path_that_is_not_a_regular_file(monkeypatch, tmp_path):
    monkeypatch.setattr(workbench, "LOCK_PATH_TEMPLATE", str(tmp_path / "md2okf-{uid}.lock"))
    os.mkfifo(tmp_path / f"md2okf-{os.getuid()}.lock")

    with pytest.raises(workbench.UnsafeLockFile, match="not a regular file"), workbench.lock():
        pass


def test_lock_refuses_a_lock_file_owned_by_someone_else(monkeypatch, tmp_path):
    """A squatted file would let its owner hold, or drop, our mutual exclusion."""
    monkeypatch.setattr(workbench, "LOCK_PATH_TEMPLATE", str(tmp_path / "md2okf-{uid}.lock"))
    (tmp_path / f"md2okf-{os.getuid() + 1}.lock").write_text("", encoding="utf-8")
    monkeypatch.setattr(os, "getuid", lambda: os.stat(tmp_path).st_uid + 1)

    with pytest.raises(workbench.UnsafeLockFile, match="owned by uid"), workbench.lock():
        pass


# --- ensure_roots(): created once, inode-preserving ------------------------


def test_ensure_roots_creates_all_five_mount_sources(tmp_path):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    assert wb.work_okf.is_dir()
    assert wb.work_md.is_dir()
    assert wb.work_scripts.is_dir()
    assert wb.work_spec.is_file()
    assert wb.sessions.is_dir()


def test_ensure_roots_secures_the_state_root(tmp_path):
    """Ported from the retired tests/test-sandbox-mounts.sh.

    The state root holds Pi's transcripts and the host-only ownership marker,
    so it is created 0700 rather than at the caller's umask.
    """
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()

    assert stat.S_IMODE(wb.root.stat().st_mode) == 0o700


def test_mounts_are_the_five_workspace_arguments_in_order(tmp_path):
    """Ported from the retired tests/test-sandbox-mounts.sh.

    Order matters to `sbx run`: the first operand is the primary workspace and
    becomes the agent's working directory. The access modes are the invariant
    the guest-side checks rest on -- only okf/ and sessions/ are writable.
    """
    wb = workbench.Workbench(root=tmp_path / "md2okf")

    args = [mount.as_arg() for mount in wb.mounts()]

    assert args == [
        str(wb.work_okf),
        f"{wb.work_md}:ro",
        f"{wb.work_scripts}:ro",
        f"{wb.work_spec}:ro",
        str(wb.sessions),
    ]


def test_ensure_roots_never_replaces_existing_roots(tmp_path):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    inodes_before = {p: p.stat().st_ino for p in (wb.work_okf, wb.work_md, wb.work_scripts, wb.sessions)}
    spec_inode_before = wb.work_spec.stat().st_ino

    wb.ensure_roots()
    for path, inode in inodes_before.items():
        assert path.stat().st_ino == inode
    assert wb.work_spec.stat().st_ino == spec_inode_before


# --- path safety -----------------------------------------------------------


def test_reject_if_unsafe_allows_regular_files_and_dirs(tmp_path):
    regular = tmp_path / "a.md"
    regular.write_text("x", encoding="utf-8")
    workbench.reject_if_unsafe(regular, what="input")
    workbench.reject_if_unsafe(tmp_path, what="input")


def test_reject_if_unsafe_rejects_a_symlink(tmp_path):
    target = tmp_path / "real.md"
    target.write_text("x", encoding="utf-8")
    link = tmp_path / "link.md"
    link.symlink_to(target)
    with pytest.raises(workbench.WorkbenchError):
        workbench.reject_if_unsafe(link, what="input")


def test_reject_if_unsafe_rejects_a_fifo(tmp_path):
    fifo = tmp_path / "pipe"
    os.mkfifo(fifo)
    with pytest.raises(workbench.WorkbenchError):
        workbench.reject_if_unsafe(fifo, what="input")


def test_reject_if_unsafe_ignores_a_missing_path(tmp_path):
    workbench.reject_if_unsafe(tmp_path / "nope.md", what="input")


def test_check_no_overlap_allows_disjoint_paths(tmp_path):
    a = tmp_path / "a"
    b = tmp_path / "b"
    a.mkdir()
    b.mkdir()
    workbench.check_no_overlap([a, b])


def test_check_no_overlap_rejects_nested_paths(tmp_path):
    outer = tmp_path / "outer"
    inner = outer / "inner"
    inner.mkdir(parents=True)
    with pytest.raises(workbench.WorkbenchError):
        workbench.check_no_overlap([outer, inner])


def test_check_no_overlap_rejects_identical_paths(tmp_path):
    a = tmp_path / "a"
    a.mkdir()
    with pytest.raises(workbench.WorkbenchError):
        workbench.check_no_overlap([a, a])


# --- sync_children(): mirror in/out, deletion included ---------------------


def test_sync_children_mirrors_and_deletes_stale_entries(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    (src / "sub").mkdir(parents=True)
    (src / "sub" / "keep.md").write_text("keep", encoding="utf-8")
    dst.mkdir()
    (dst / "stale.md").write_text("stale", encoding="utf-8")

    workbench.sync_children(src, dst)

    assert not (dst / "stale.md").exists()
    assert (dst / "sub" / "keep.md").read_text(encoding="utf-8") == "keep"


def test_sync_children_empties_dst_when_src_is_none(tmp_path):
    dst = tmp_path / "dst"
    dst.mkdir()
    (dst / "old.md").write_text("old", encoding="utf-8")
    workbench.sync_children(None, dst)
    assert list(dst.iterdir()) == []


def test_sync_children_never_deletes_through_a_symlink_in_dst(tmp_path):
    real_target = tmp_path / "elsewhere"
    real_target.mkdir()
    (real_target / "precious.md").write_text("precious", encoding="utf-8")

    dst = tmp_path / "dst"
    dst.mkdir()
    (dst / "link").symlink_to(real_target)

    workbench.sync_children(None, dst)

    assert list(dst.iterdir()) == []
    assert (real_target / "precious.md").exists()


def test_sync_children_rejects_a_symlink_in_src(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "link.md").symlink_to(tmp_path / "does-not-matter")
    dst = tmp_path / "dst"
    dst.mkdir()
    with pytest.raises(workbench.WorkbenchError):
        workbench.sync_children(src, dst)


# --- staging the four helper CLIs -------------------------------------------


def test_stage_clis_copies_only_pyproject_and_src(tmp_path):
    clis_root = tmp_path / "clis"
    project = clis_root / "merkleokf"
    (project / "src" / "merkleokf").mkdir(parents=True)
    (project / "src" / "merkleokf" / "cli.py").write_text("# cli", encoding="utf-8")
    (project / "pyproject.toml").write_text("[project]\nname='merkleokf'\n", encoding="utf-8")
    # Dev clutter a real checkout carries, that must never be staged:
    (project / ".venv" / "bin").mkdir(parents=True)
    (project / ".venv" / "bin" / "python").symlink_to("/usr/bin/python3")
    (project / "tests").mkdir()
    (project / "tests" / "test_cli.py").write_text("# test", encoding="utf-8")
    (project / "uv.lock").write_text("", encoding="utf-8")

    work_scripts = tmp_path / "work_scripts"
    work_scripts.mkdir()
    workbench.stage_clis(clis_root, work_scripts)

    staged = work_scripts / "merkleokf"
    assert (staged / "pyproject.toml").is_file()
    assert (staged / "src" / "merkleokf" / "cli.py").is_file()
    assert not (staged / ".venv").exists()
    assert not (staged / "tests").exists()
    assert not (staged / "uv.lock").exists()


def test_stage_clis_skips_a_project_missing_pyproject_or_src(tmp_path):
    clis_root = tmp_path / "clis"
    (clis_root / "incomplete").mkdir(parents=True)
    work_scripts = tmp_path / "work_scripts"
    work_scripts.mkdir()
    workbench.stage_clis(clis_root, work_scripts)
    assert list(work_scripts.iterdir()) == []


def test_stage_clis_against_the_real_checkout_scripts_dir(tmp_path):
    """Regression: the real scripts/ tree carries per-project .venv/ symlinks."""
    work_scripts = tmp_path / "work_scripts"
    work_scripts.mkdir()
    workbench.stage_clis(resources.clis_dir(), work_scripts)
    for name in ("inspectmd", "inspectokf", "sizeokf", "merkleokf"):
        assert (work_scripts / name / "pyproject.toml").is_file()
        assert (work_scripts / name / "src").is_dir()


# --- staging inputs, spec, and mirroring the wiki ---------------------------


def test_stage_inputs_copies_by_basename_and_stdin_bytes(tmp_path):
    work_md = tmp_path / "md"
    work_md.mkdir()
    source = tmp_path / "elsewhere" / "doc.md"
    source.parent.mkdir()
    source.write_text("# doc", encoding="utf-8")

    workbench.stage_inputs(work_md, [("doc.md", source), ("stdin.md", b"# piped")])

    assert (work_md / "doc.md").read_text(encoding="utf-8") == "# doc"
    assert (work_md / "stdin.md").read_text(encoding="utf-8") == "# piped"


def test_rewrite_spec_truncates_in_place_same_inode(tmp_path):
    work_spec = tmp_path / "SPEC.md"
    work_spec.write_text("old spec, much longer than the new one", encoding="utf-8")
    inode_before = work_spec.stat().st_ino

    source = tmp_path / "SPEC-source.md"
    source.write_text("new", encoding="utf-8")
    workbench.rewrite_spec(work_spec, source)

    assert work_spec.read_text(encoding="utf-8") == "new"
    assert work_spec.stat().st_ino == inode_before


def test_mirror_in_then_out_round_trips(tmp_path):
    output_dir = tmp_path / "wikis" / "alpha"
    output_dir.mkdir(parents=True)
    (output_dir / "index.md").write_text("# index", encoding="utf-8")

    work_okf = tmp_path / "work_okf"
    work_okf.mkdir()

    workbench.mirror_in(work_okf, output_dir)
    assert (work_okf / "index.md").read_text(encoding="utf-8") == "# index"

    (work_okf / "index.md").write_text("# edited", encoding="utf-8")
    workbench.mirror_out(work_okf, output_dir)
    assert (output_dir / "index.md").read_text(encoding="utf-8") == "# edited"


def test_restaging_for_a_second_run_removes_the_first_runs_pages(tmp_path):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    clis_dir = tmp_path / "clis"
    clis_dir.mkdir()
    spec_source = tmp_path / "SPEC.md"
    spec_source.write_text("spec", encoding="utf-8")

    alpha_out = tmp_path / "wikis" / "alpha"
    alpha_out.mkdir(parents=True)
    (alpha_out / "alpha.md").write_text("alpha page", encoding="utf-8")
    (tmp_path / "a.md").write_text("a", encoding="utf-8")

    workbench.restage(
        wb, inputs=[("a.md", tmp_path / "a.md")], clis_dir=clis_dir, spec_source=spec_source, output_dir=alpha_out
    )
    assert (wb.work_okf / "alpha.md").exists()

    beta_out = tmp_path / "wikis" / "beta"
    beta_out.mkdir(parents=True)
    (beta_out / "beta.md").write_text("beta page", encoding="utf-8")
    workbench.restage(
        wb, inputs=[("b.md", tmp_path / "a.md")], clis_dir=clis_dir, spec_source=spec_source, output_dir=beta_out
    )

    assert not (wb.work_okf / "alpha.md").exists()
    assert (wb.work_okf / "beta.md").exists()


def test_mirror_out_failure_names_the_workbench_path(tmp_path, monkeypatch):
    work_okf = tmp_path / "work_okf"
    work_okf.mkdir()
    output_dir = tmp_path / "out"

    def boom(_src, _dst):
        raise OSError("disk full")

    monkeypatch.setattr(workbench, "sync_children", boom)
    with pytest.raises(workbench.MirrorError) as excinfo:
        workbench.mirror_out(work_okf, output_dir)
    assert excinfo.value.workbench_path == work_okf
    # Regression: the path was recorded as an attribute but never actually
    # folded into the message text -- str(exc) is what every caller prints,
    # so a caller reading only the message saw no recovery location at all.
    assert str(work_okf) in str(excinfo.value)


def test_restage_wraps_a_raw_oserror_as_a_workbencherror(tmp_path, monkeypatch):
    """Regression.

    An uncaught OSError from any staging step must not crash a caller that
    only catches WorkbenchError.
    """
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()

    def boom(*_args, **_kwargs):
        raise OSError("permission denied")

    monkeypatch.setattr(workbench, "stage_inputs", boom)
    with pytest.raises(workbench.WorkbenchError):
        workbench.restage(
            wb,
            inputs=[],
            clis_dir=tmp_path / "clis",
            spec_source=tmp_path / "SPEC.md",
            output_dir=tmp_path / "out",
        )


# --- has_markdown() ----------------------------------------------------------


def test_has_markdown(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert workbench.has_markdown(empty) is False
    (empty / "sub").mkdir()
    (empty / "sub" / "x.md").write_text("x", encoding="utf-8")
    assert workbench.has_markdown(empty) is True


# --- ownership adoption rule for -o DIR -------------------------------------


def test_missing_output_is_adoptable(tmp_path):
    assert workbench.is_adoptable_output(tmp_path / "does-not-exist") is True


def test_empty_output_is_adoptable(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    assert workbench.is_adoptable_output(empty) is True


def test_output_with_bare_index_md_is_not_adoptable(tmp_path):
    output_dir = tmp_path / "notes"
    output_dir.mkdir()
    (output_dir / "index.md").write_text("# just a heading\n", encoding="utf-8")
    assert workbench.is_adoptable_output(output_dir) is False
    # And it must not have been modified by the check.
    assert (output_dir / "index.md").read_text(encoding="utf-8") == "# just a heading\n"


def test_output_with_okf_version_only_frontmatter_is_adoptable(tmp_path):
    output_dir = tmp_path / "wiki"
    output_dir.mkdir()
    (output_dir / "index.md").write_text('---\nokf_version: "0.2"\n---\n# Index\n', encoding="utf-8")
    assert workbench.is_adoptable_output(output_dir) is True


def test_output_with_extra_frontmatter_keys_is_not_adoptable(tmp_path):
    output_dir = tmp_path / "wiki"
    output_dir.mkdir()
    (output_dir / "index.md").write_text(
        '---\nokf_version: "0.2"\ntitle: mine\n---\n# Index\n', encoding="utf-8"
    )
    assert workbench.is_adoptable_output(output_dir) is False


def test_output_that_is_a_symlink_is_not_adoptable(tmp_path):
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    link.symlink_to(real)
    assert workbench.is_adoptable_output(link) is False


def test_output_that_is_a_dangling_symlink_is_not_adoptable(tmp_path):
    """Regression.

    exists()/is_dir() follow a symlink, so a dangling one must be checked
    for symlink-ness *before* those, or it reads as "missing".
    """
    link = tmp_path / "dangling"
    link.symlink_to(tmp_path / "nowhere")
    assert not link.exists()  # confirms the target really is missing
    assert workbench.is_adoptable_output(link) is False


# --- fingerprint + ownership marker -----------------------------------------


def test_fingerprint_is_stable_for_the_same_inputs(tmp_path):
    kit_dir = tmp_path / "kit"
    kit_dir.mkdir()
    (kit_dir / "spec.yaml").write_text("kit", encoding="utf-8")
    mounts = [sandbox.Mount(tmp_path / "work_okf"), sandbox.Mount(tmp_path / "work_md", readonly=True)]

    a = workbench.fingerprint(kit_dir, (0, 43, 0), mounts)
    b = workbench.fingerprint(kit_dir, (0, 43, 0), mounts)
    assert a == b


def test_fingerprint_ignores_dotfiles_and_pycache(tmp_path):
    """Regression: editor droppings and bytecode must not move the fingerprint."""
    kit_dir = tmp_path / "kit"
    kit_dir.mkdir()
    (kit_dir / "spec.yaml").write_text("kit", encoding="utf-8")
    mounts = [sandbox.Mount(tmp_path / "work_okf")]
    before = workbench.fingerprint(kit_dir, (0, 43, 0), mounts)

    (kit_dir / ".DS_Store").write_bytes(b"\x00finder noise")
    (kit_dir / "scripts" / "__pycache__").mkdir(parents=True)
    (kit_dir / "scripts" / "__pycache__" / "guard.cpython-312.pyc").write_bytes(b"bytecode")

    after = workbench.fingerprint(kit_dir, (0, 43, 0), mounts)
    assert before == after


def test_fingerprint_changes_when_the_kit_changes(tmp_path):
    kit_dir = tmp_path / "kit"
    kit_dir.mkdir()
    (kit_dir / "spec.yaml").write_text("kit v1", encoding="utf-8")
    mounts = [sandbox.Mount(tmp_path / "work_okf")]
    before = workbench.fingerprint(kit_dir, (0, 43, 0), mounts)

    (kit_dir / "spec.yaml").write_text("kit v2", encoding="utf-8")
    after = workbench.fingerprint(kit_dir, (0, 43, 0), mounts)
    assert before != after


def test_ownership_marker_round_trips_atomically(tmp_path):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.root.mkdir(parents=True)
    assert workbench.read_ownership_marker(wb) is None

    workbench.write_ownership_marker(wb, "fingerprint-value", "identity-value")
    assert workbench.read_ownership_marker(wb) == ("fingerprint-value", "identity-value")
    assert not wb.fingerprint_path.with_name(wb.fingerprint_path.name + ".tmp").exists()


# --- resolve_sandbox_state() and ensure_sandbox() ---------------------------


def test_resolve_sandbox_state_creates_when_no_sandbox_exists(tmp_path, fake_sbx):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    assert workbench.resolve_sandbox_state(wb, "md2okf", "fp") == "create"


def test_resolve_sandbox_state_rejects_an_unowned_sandbox(tmp_path, fake_sbx):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    fake_sbx.register("md2okf")  # exists, but we hold no marker for it
    with pytest.raises(workbench.UnownedSandboxError):
        workbench.resolve_sandbox_state(wb, "md2okf", "fp")


def test_resolve_sandbox_state_rejects_a_matching_fingerprint_with_wrong_identity(tmp_path, fake_sbx):
    """A marker on disk is not enough: the live identity must also match."""
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    fake_sbx.register("md2okf")
    workbench.write_ownership_marker(wb, "fp", "some-other-token")
    with pytest.raises(workbench.UnownedSandboxError):
        workbench.resolve_sandbox_state(wb, "md2okf", "fp")


def test_resolve_sandbox_state_reuses_when_everything_matches(tmp_path, fake_sbx):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    token = sandbox.create("md2okf", tmp_path / "kit", [], {})
    workbench.write_ownership_marker(wb, "fp", token)
    assert workbench.resolve_sandbox_state(wb, "md2okf", "fp") == "reuse"


def test_resolve_sandbox_state_recreates_on_fingerprint_change(tmp_path, fake_sbx):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    token = sandbox.create("md2okf", tmp_path / "kit", [], {})
    workbench.write_ownership_marker(wb, "old-fp", token)
    assert workbench.resolve_sandbox_state(wb, "md2okf", "new-fp") == "create"


def test_resolve_sandbox_state_recreates_when_probe_fails(tmp_path, fake_sbx):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    token = sandbox.create("md2okf", tmp_path / "kit", [], {})
    workbench.write_ownership_marker(wb, "fp", token)
    fake_sbx.probe_ok = False
    assert workbench.resolve_sandbox_state(wb, "md2okf", "fp") == "create"


def test_resolve_sandbox_state_fresh_recreates_an_owned_sandbox(tmp_path, fake_sbx):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    token = sandbox.create("md2okf", tmp_path / "kit", [], {})
    workbench.write_ownership_marker(wb, "fp", token)
    assert workbench.resolve_sandbox_state(wb, "md2okf", "fp", fresh=True) == "create"


def test_resolve_sandbox_state_fresh_does_not_widen_deletion_authority(tmp_path, fake_sbx):
    """--fresh recreates a sandbox we own; it must not bypass the ownership check."""
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    fake_sbx.register("md2okf")
    with pytest.raises(workbench.UnownedSandboxError):
        workbench.resolve_sandbox_state(wb, "md2okf", "fp", fresh=True)


def test_ensure_sandbox_creates_and_writes_the_marker(tmp_path, fake_sbx):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    assert workbench.ensure_sandbox(wb) == "created"
    assert workbench.read_ownership_marker(wb) is not None


def test_stage_tooling_fills_the_empty_spec_placeholder(tmp_path):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    assert wb.work_spec.stat().st_size == 0
    inode_before = wb.work_spec.stat().st_ino

    workbench.stage_tooling(wb)

    assert wb.work_spec.read_bytes() == resources.spec_md().read_bytes()
    # The bind mount resolves this inode, so the fill must not replace the file.
    assert wb.work_spec.stat().st_ino == inode_before


def test_stage_tooling_leaves_an_already_staged_spec_alone(tmp_path):
    """A compile's --spec survives the --shell/--agent that follows it."""
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    wb.work_spec.write_text("# Custom spec\n\n**Version 0.3**\n", encoding="utf-8")

    workbench.stage_tooling(wb)

    assert wb.work_spec.read_text(encoding="utf-8") == "# Custom spec\n\n**Version 0.3**\n"


def test_stage_tooling_converts_an_unreadable_spec_to_workbench_error(tmp_path, monkeypatch):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    monkeypatch.setattr(resources, "spec_md", lambda: tmp_path / "missing" / "SPEC.md")

    with pytest.raises(workbench.WorkbenchError, match="staging the sandbox tooling failed"):
        workbench.stage_tooling(wb)


def test_ensure_sandbox_reuses_a_previously_created_one(tmp_path, fake_sbx):
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    workbench.ensure_sandbox(wb)
    run_calls_before = len([c for c in fake_sbx.calls if c[:3] == ["sbx", "run", "--detached"]])
    assert workbench.ensure_sandbox(wb) == "reuse"
    run_calls_after = len([c for c in fake_sbx.calls if c[:3] == ["sbx", "run", "--detached"]])
    assert run_calls_after == run_calls_before


def test_ensure_sandbox_writes_marker_even_when_the_key_check_fails(tmp_path, fake_sbx):
    """Regression.

    A sandbox we really did create must be recognised as ours on the next
    run, even if OPENROUTER_API_KEY was not yet proxy-managed -- not force
    a manual `sbx rm --force` just to fix a secret.
    """
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    fake_sbx.openrouter_key = "sk-literal-value"

    with pytest.raises(workbench.KeyNotProxyManagedError):
        workbench.ensure_sandbox(wb)

    assert workbench.read_ownership_marker(wb) is not None

    # Fixing the secret and running again must reuse, not demand a manual
    # `sbx rm --force` first.
    fake_sbx.openrouter_key = "proxy-managed"
    fingerprint_value = workbench.fingerprint(resources.kit_dir(), sandbox.version(), wb.mounts())
    assert workbench.resolve_sandbox_state(wb, workbench.SANDBOX_NAME, fingerprint_value) == "reuse"


def test_key_not_proxy_managed_error_names_the_openrouter_commands():
    """Regression.

    This used to tell the user to run a GitHub secret command for an
    OpenRouter key problem -- the wrong provider entirely.
    """
    message = str(workbench.KeyNotProxyManagedError("md2okf"))
    assert "sbx secret set openrouter" in message
    assert "sbx secret set-custom" in message
    assert "openrouter.ai" in message
    assert "github" not in message.lower()


def test_ensure_sandbox_clears_markers_when_a_recreation_fails(tmp_path, fake_sbx):
    """Regression (code review finding 1).

    A prior successful create() leaves a valid marker. If a later
    recreation attempt's `sbx run` fails, create()'s first step
    (`sbx rm --force`) has already torn down that sandbox generation, so
    the old marker must not survive to describe a sandbox that is gone.
    """
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    assert workbench.ensure_sandbox(wb) == "created"
    assert workbench.read_ownership_marker(wb) is not None

    fake_sbx.run_fail_names.add(workbench.SANDBOX_NAME)
    with pytest.raises(sandbox.SandboxError):
        workbench.ensure_sandbox(wb, fresh=True)

    assert workbench.read_ownership_marker(wb) is None
    assert not wb.fingerprint_path.exists()
    assert not wb.identity_path.exists()


def test_ensure_sandbox_stages_tooling_for_every_caller(tmp_path, fake_sbx):
    """Regression, found by the live stage 3 run.

    stage_clis() had exactly one call site — restage() — so the compile
    path worked while `python -m md2okf.sandbox` produced a sandbox with
    an empty scripts mount and four broken CLI shims. Staging tooling is
    part of ensure_sandbox() now precisely so a caller cannot forget it.
    """
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    assert list(wb.work_scripts.iterdir()) == []

    workbench.ensure_sandbox(wb)

    assert (wb.work_scripts / "merkleokf" / "pyproject.toml").is_file()


def test_ensure_sandbox_restages_tooling_when_reusing(tmp_path, fake_sbx):
    """A reused sandbox whose staged tooling was wiped must get it back."""
    wb = workbench.Workbench(root=tmp_path / "state" / "md2okf")
    wb.ensure_roots()
    workbench.ensure_sandbox(wb)

    for child in wb.work_scripts.iterdir():
        shutil.rmtree(child)
    assert list(wb.work_scripts.iterdir()) == []

    assert workbench.ensure_sandbox(wb) == "reuse"
    assert (wb.work_scripts / "merkleokf" / "pyproject.toml").is_file()
