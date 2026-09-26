"""Tests for what the built wheel carries.

An installed md2okf has no checkout to fall back on: resources.py looks for
kits/<agent>/, SPEC.md and clis/ beside itself, and only the wheel's
force-include puts them there. That mapping is easy to get subtly wrong and
impossible to notice from a checkout, where every lookup finds the real tree
anyway -- so this builds the wheel for real and reads it back.

It builds the way a release does: the sdist first, then the wheel *from the
sdist*. That second hop is where an over-broad sdist exclude bites -- an
unanchored ".claude" pattern also strips a kit's own files/home/.claude/.
"""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from pathlib import Path

import pytest

from md2okf import agents

_REPO_ROOT = Path(__file__).resolve().parents[1]

# What an installed md2okf needs in order to work with no checkout: the driver
# itself, the kit (spec plus the agent config it carries), the OKF spec, and
# one helper CLI project standing in for all four.
_REQUIRED = (
    "md2okf/cli.py",
    "md2okf/workbench.py",
    "md2okf/kits/pi/spec.yaml",
    "md2okf/kits/pi/files/home/.pi/agent/AGENTS.md",
    "md2okf/kits/pi/files/home/.local/lib/md2okf/mount-state.sh",
    "md2okf/SPEC.md",
    "md2okf/clis/merkleokf/pyproject.toml",
    "md2okf/clis/merkleokf/src/merkleokf/merkle.py",
)

# A force-included *directory* is recursed without regard for .gitignore, so
# naming scripts/<cli> rather than its pyproject.toml and src/ would drag in
# ~40 MB of .venv and caches around 172 KB of source.
_FORBIDDEN = (".venv", ".ruff_cache", ".pytest_cache", "__pycache__", "uv.lock", ".DS_Store")


@pytest.fixture(scope="module")
def wheel_names(tmp_path_factory) -> list[str]:
    """Build the sdist and the wheel from it once for this module; return the wheel's paths."""
    if shutil.which("uv") is None:
        pytest.skip("uv is not installed; the wheel cannot be built here")
    out_dir = tmp_path_factory.mktemp("dist")
    subprocess.run(  # noqa: S603
        ["uv", "build", "--out-dir", str(out_dir)],  # noqa: S607
        cwd=_REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    wheels = list(out_dir.glob("*.whl"))
    assert len(wheels) == 1, f"expected one wheel, got {wheels}"
    with zipfile.ZipFile(wheels[0]) as archive:
        return archive.namelist()


def test_wheel_carries_the_driver_and_its_bundled_assets(wheel_names):
    missing = [path for path in _REQUIRED if path not in wheel_names]
    assert not missing, f"the wheel is missing {missing}"


def _is_host_clutter(path: Path) -> bool:
    return path.name == ".DS_Store" or path.name.startswith("._") or "__pycache__" in path.parts


@pytest.mark.parametrize("agent", sorted(agents.AGENTS))
def test_wheel_carries_every_file_of_every_registered_kit(wheel_names, agent):
    """Hidden directories included: an agent's whole runtime config lives under files/home/.<agent>."""
    tracked = subprocess.run(  # noqa: S603
        ["git", "ls-files", "-z", "--", f"kits/{agent}"],  # noqa: S607
        cwd=_REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.split("\0")
    expected = [
        f"md2okf/kits/{agent}/{Path(name).relative_to(f'kits/{agent}').as_posix()}"
        for name in tracked
        if name and not _is_host_clutter(Path(name))
    ]
    assert any("/." in name for name in expected), "the kit has no hidden files; this test proves nothing"
    missing = [name for name in expected if name not in wheel_names]
    assert not missing, f"the wheel is missing kit files: {missing}"


def test_wheel_still_carries_the_python_modules_beside_the_assets(wheel_names):
    """The assets must never displace the package itself.

    hatchling currently finds src/md2okf by name even with force-include set,
    so `packages` in pyproject.toml is explicit rather than load-bearing --
    but a wheel of assets with no importable package installs cleanly and
    only fails at the entry point, which is late. Pin it here instead.
    """
    modules = [name for name in wheel_names if name.startswith("md2okf/") and name.endswith(".py")]
    assert "md2okf/__init__.py" in modules
    assert len(modules) >= 7, f"only {len(modules)} driver modules in the wheel: {modules}"


def test_wheel_excludes_local_state_and_test_trees(wheel_names):
    polluted = [name for name in wheel_names for bad in _FORBIDDEN if bad in name]
    assert not polluted, f"the wheel carries local state: {polluted}"
    assert not [name for name in wheel_names if name.startswith("md2okf/clis/") and "/tests/" in name]


def test_wheel_stays_small(wheel_names):
    """A few hundred KB, not tens of MB -- the check that catches an over-broad include."""
    assert len(wheel_names) < 200, f"{len(wheel_names)} files suggests an over-broad force-include"
