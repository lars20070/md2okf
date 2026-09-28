"""Tests for the gate's frontmatter guard: it checks against md2okf's own SPEC.md.

The guard ships in every kit; tests/test_kits.py holds the copies
byte-identical, so these exercise Pi's copy only, as a subprocess, the way
check-okf.sh runs it. What they pin: the expected okf_version comes from
md2okf's own spec -- the repository's on the host, the mount beside the
workspace in the sandbox -- and never from a spec placed beside the checked
wiki, nor from the SPEC_MD variable an older release honoured.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_GUARD = _REPO / "kits/pi/files/home/.pi/agent/skills/compile-okf/scripts/frontmatter-guard.py"
_CANONICAL = re.search(r"^\*\*Version\s+(\d+\.\d+)\*\*", (_REPO / "SPEC.md").read_text(encoding="utf-8"), re.M)
CANONICAL_VERSION = _CANONICAL.group(1) if _CANONICAL else ""
PLANTED_VERSION = "9.9"


def _bundle(path: Path, version: str) -> Path:
    """A wiki the guard finds nothing wrong with, apart from its declared okf_version."""
    path.mkdir(parents=True)
    (path / "beans.md").write_text(
        "---\n"
        "type: Chapter\n"
        'title: "Beans"\n'
        'description: "Why to grind whole beans just before brewing."\n'
        "tags: [coffee]\n"
        'generated: { by: pi/test-model, at: "2026-09-28T00:00:00Z" }\n'
        "---\n\n# Beans\n\nGrind them just before brewing.\n",
        encoding="utf-8",
    )
    (path / "index.md").write_text(
        f'---\nokf_version: "{version}"\n---\n# Index\n\n* [Beans](beans.md)\n', encoding="utf-8"
    )
    (path / "log.md").write_text(
        "# Update Log\n\n## 2026-09-28\n* **Creation**: Added [Beans](/beans.md).\n", encoding="utf-8"
    )
    return path


def _spec(path: Path, version: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# Open Knowledge Format (OKF)\n\n**Version {version}**\n", encoding="utf-8")
    return path


def _run(guard: Path, bundle: Path, **env: str) -> subprocess.CompletedProcess[str]:
    environment = {key: value for key, value in os.environ.items() if key not in {"SPEC_MD", "WORKDIR"}}
    environment.update(env)
    return subprocess.run(
        [sys.executable, str(guard), str(bundle)],
        capture_output=True,
        text=True,
        env=environment,
        check=False,
    )


def _guard_at(path: Path) -> Path:
    path.parent.mkdir(parents=True)
    shutil.copy2(_GUARD, path)
    return path


def _sandbox_guard(tmp_path: Path) -> Path:
    """The guard where the kit copies it in the sandbox: under the home directory, outside any kit tree."""
    return _guard_at(tmp_path / "home/agent/.pi/agent/skills/compile-okf/scripts/frontmatter-guard.py")


def _package_guard(package: Path) -> Path:
    """The guard where a checkout or an installed md2okf keeps it: inside kits/<agent>/files/."""
    return _guard_at(package / "kits/pi/files/home/.pi/agent/skills/compile-okf/scripts/frontmatter-guard.py")


def _workspace(root: Path, version: str) -> Path:
    """A sandbox workspace with the driver-staged spec mounted beside it."""
    workspace = root / "work" / "okf"
    workspace.mkdir(parents=True)
    _spec(workspace.parent / "SPEC.md", version)
    return workspace


def test_the_repository_spec_has_a_version():
    assert CANONICAL_VERSION, "SPEC.md has no '**Version X.Y**' line"


def test_the_canonical_spec_wins_over_a_planted_sibling_and_spec_md(tmp_path):
    planted = _spec(tmp_path / "SPEC.md", PLANTED_VERSION)
    wiki = _bundle(tmp_path / "wiki", CANONICAL_VERSION)

    result = _run(_GUARD, wiki, SPEC_MD=str(planted))

    assert result.returncode == 0, result.stdout + result.stderr
    assert "OK:" in result.stdout


def test_a_wiki_matching_only_a_planted_spec_fails(tmp_path):
    """The review's reproduction: a sibling 9.9 spec used to make a 9.9 wiki pass."""
    planted = _spec(tmp_path / "SPEC.md", PLANTED_VERSION)
    wiki = _bundle(tmp_path / "wiki", PLANTED_VERSION)

    result = _run(_GUARD, wiki, SPEC_MD=str(planted))

    assert result.returncode == 1, result.stdout + result.stderr
    assert f"okf_version: index.md declares '{PLANTED_VERSION}'" in result.stdout


def test_no_canonical_spec_is_exit_2_even_with_spec_md_set(tmp_path):
    guard = _sandbox_guard(tmp_path)
    valid = _spec(tmp_path / "data" / "SPEC.md", CANONICAL_VERSION)
    wiki = _bundle(tmp_path / "data" / "wiki", CANONICAL_VERSION)

    result = _run(guard, wiki, SPEC_MD=str(valid))

    assert result.returncode == 2, result.stdout + result.stderr
    assert "cannot find md2okf's SPEC.md" in result.stderr


@pytest.mark.parametrize(("declared", "expected"), [(CANONICAL_VERSION, 0), (PLANTED_VERSION, 1)])
def test_in_the_sandbox_the_spec_beside_the_workspace_decides(tmp_path, declared, expected):
    guard = _sandbox_guard(tmp_path)
    workspace = _workspace(tmp_path, CANONICAL_VERSION)
    _spec(tmp_path / "elsewhere" / "SPEC.md", PLANTED_VERSION)
    wiki = _bundle(tmp_path / "elsewhere" / "wiki", declared)

    result = _run(guard, wiki, WORKDIR=str(workspace))

    assert result.returncode == expected, result.stdout + result.stderr


@pytest.mark.parametrize(("declared", "expected"), [(CANONICAL_VERSION, 0), (PLANTED_VERSION, 1)])
def test_a_spec_in_the_sandbox_home_does_not_override_the_workspace_mount(tmp_path, declared, expected):
    """Regression: the guard used to take the first SPEC.md above itself, so ~/SPEC.md won."""
    guard = _sandbox_guard(tmp_path)
    _spec(tmp_path / "home" / "agent" / "SPEC.md", PLANTED_VERSION)
    workspace = _workspace(tmp_path, CANONICAL_VERSION)
    wiki = _bundle(tmp_path / "elsewhere" / "wiki", declared)

    result = _run(guard, wiki, WORKDIR=str(workspace))

    assert result.returncode == expected, result.stdout + result.stderr


def test_the_package_spec_decides_on_the_host(tmp_path):
    """Inside the kit tree, neither an ancestor spec nor WORKDIR is consulted."""
    package = tmp_path / "outer" / "md2okf"
    guard = _package_guard(package)
    _spec(package / "SPEC.md", CANONICAL_VERSION)
    _spec(tmp_path / "outer" / "SPEC.md", PLANTED_VERSION)
    workspace = _workspace(tmp_path, PLANTED_VERSION)
    wiki = _bundle(tmp_path / "data" / "wiki", CANONICAL_VERSION)

    result = _run(guard, wiki, WORKDIR=str(workspace))

    assert result.returncode == 0, result.stdout + result.stderr


def test_a_missing_package_spec_is_exit_2_not_a_search_further_up(tmp_path):
    """Regression: with the package's own spec gone, an unrelated ancestor spec used to be accepted."""
    package = tmp_path / "outer" / "md2okf"
    guard = _package_guard(package)
    _spec(tmp_path / "outer" / "SPEC.md", CANONICAL_VERSION)
    workspace = _workspace(tmp_path, CANONICAL_VERSION)
    wiki = _bundle(tmp_path / "data" / "wiki", CANONICAL_VERSION)

    result = _run(guard, wiki, WORKDIR=str(workspace))

    assert result.returncode == 2, result.stdout + result.stderr
    assert f"cannot find md2okf's SPEC.md at {package.resolve() / 'SPEC.md'}" in result.stderr
