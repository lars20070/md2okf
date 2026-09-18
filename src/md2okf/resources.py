"""Locate the kit, the OKF spec, and the helper CLI sources this package ships.

Prefers the installed package's own bundled copies (importlib.resources);
falls back to the checkout's layout so `uv run md2okf` works with no build
step. The checkout fallback is a second code path and is tested on its own.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

# src/md2okf/resources.py -> parents[0]=src/md2okf, [1]=src, [2]=repo root.
_CHECKOUT_ROOT = Path(__file__).resolve().parents[2]


class ResourcesError(Exception):
    """md2okf cannot locate its own kit, spec, or helper CLI sources."""


def _installed_root() -> Path | None:
    """The installed package's own directory, if it carries a bundled kit.

    A checkout (this package imported via `pythonpath`, with no wheel build)
    has no ``kit/`` sibling next to ``resources.py``, so this returns None and
    every lookup below falls back to the checkout's own layout.
    """
    try:
        candidate = Path(str(files("md2okf")))
    except (ModuleNotFoundError, TypeError):
        return None
    if (candidate / "kit").is_dir():
        return candidate
    return None


def _checkout_path(relative: str, what: str) -> Path:
    """The checkout fallback location for `relative`, verified to exist.

    Packaging (force-include of kit/SPEC.md/clis into the wheel) is stage
    4's job, not stage 2's -- a wheel built today carries the Python modules
    only. Installed that way (e.g. via `uv tool install .`), _installed_root
    returns None, and __file__ resolves somewhere under site-packages: a
    silent parents[2] would compute a path that does not exist and cannot
    ever exist, and every caller downstream would report a generic "not a
    file" error with no clue why. Fail here instead, with the actual cause.
    """
    candidate = _CHECKOUT_ROOT / relative
    if not candidate.exists():
        raise ResourcesError(
            f"cannot locate {what} ({candidate}). This looks like an installed "
            "md2okf built without its bundled kit (packaging lands in a later "
            "stage), and not a development checkout either. Run from a "
            "checkout with `uv run md2okf`, or install a release that bundles "
            "the kit."
        )
    return candidate


def kit_dir() -> Path:
    """The md2okf sandbox kit: the installed ``md2okf/kit``, else ``kits/md2okf``."""
    root = _installed_root()
    return root / "kit" if root is not None else _checkout_path("kits/md2okf", "the sandbox kit")


def spec_md() -> Path:
    """The bundled OKF spec: the installed ``md2okf/SPEC.md``, else the checkout's."""
    root = _installed_root()
    return root / "SPEC.md" if root is not None else _checkout_path("SPEC.md", "the OKF spec")


def clis_dir() -> Path:
    """The four helper CLI projects: the installed ``md2okf/clis``, else ``scripts/``."""
    root = _installed_root()
    return root / "clis" if root is not None else _checkout_path("scripts", "the helper CLI projects")
