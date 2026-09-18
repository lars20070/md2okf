"""Tests for md2okf.resources."""

from pathlib import Path

import pytest

from md2okf import resources


def test_checkout_fallback_finds_the_real_kit_and_spec():
    assert resources.kit_dir().is_dir()
    assert (resources.kit_dir() / "spec.yaml").is_file()
    assert resources.spec_md().is_file()
    assert resources.clis_dir().is_dir()
    assert (resources.clis_dir() / "merkleokf" / "pyproject.toml").is_file()


def test_installed_root_preferred_when_it_carries_a_kit(tmp_path: Path, monkeypatch):
    fake_root = tmp_path / "installed" / "md2okf"
    (fake_root / "kit").mkdir(parents=True)
    (fake_root / "clis").mkdir()
    (fake_root / "SPEC.md").write_text("fake spec\n", encoding="utf-8")

    monkeypatch.setattr(resources, "_installed_root", lambda: fake_root)

    assert resources.kit_dir() == fake_root / "kit"
    assert resources.spec_md() == fake_root / "SPEC.md"
    assert resources.clis_dir() == fake_root / "clis"


def test_installed_root_is_none_without_a_bundled_kit(tmp_path: Path, monkeypatch):
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.setattr(resources, "files", lambda _name: bare)

    assert resources._installed_root() is None
    assert resources.kit_dir() == resources._CHECKOUT_ROOT / "kits" / "md2okf"


def test_neither_installed_nor_checkout_raises_a_clear_error(tmp_path: Path, monkeypatch):
    """Regression (code review finding 5).

    `uv tool install .` today (packaging/force-include lands in a later
    stage) installs a wheel with no bundled kit -- _installed_root() is
    None, and __file__ resolves under site-packages, not a checkout, so
    the naive fallback silently computed a path that could never exist.
    Every caller downstream then failed with a generic, unhelpful
    "not a file" error. This must fail immediately, with the real cause.
    """
    bare = tmp_path / "bare"  # no "kit" subdir -> not an installed bundle
    bare.mkdir()
    monkeypatch.setattr(resources, "files", lambda _name: bare)
    monkeypatch.setattr(resources, "_CHECKOUT_ROOT", tmp_path / "site-packages")  # not a real checkout either

    for lookup in (resources.kit_dir, resources.spec_md, resources.clis_dir):
        with pytest.raises(resources.ResourcesError, match="checkout"):
            lookup()
