"""Tests for md2okf.resources."""

from pathlib import Path

import pytest

from md2okf import agents, resources


@pytest.mark.parametrize("agent", sorted(agents.AGENTS))
def test_checkout_fallback_finds_every_registered_agents_kit(agent):
    """A registered agent without a kit would pass MD2OKF_AGENT and then fail late."""
    assert resources.kit_dir(agent) == resources._CHECKOUT_ROOT / "kits" / agent
    assert (resources.kit_dir(agent) / "spec.yaml").is_file()


def test_checkout_fallback_finds_the_spec_and_clis():
    assert resources.spec_md().is_file()
    assert resources.clis_dir().is_dir()
    assert (resources.clis_dir() / "merkleokf" / "pyproject.toml").is_file()


def test_installed_root_preferred_when_it_carries_the_kits(tmp_path: Path, monkeypatch):
    fake_root = tmp_path / "installed" / "md2okf"
    (fake_root / "kits" / "pi").mkdir(parents=True)
    (fake_root / "clis").mkdir()
    (fake_root / "SPEC.md").write_text("fake spec\n", encoding="utf-8")

    monkeypatch.setattr(resources, "_installed_root", lambda: fake_root)

    assert resources.kit_dir("pi") == fake_root / "kits" / "pi"
    assert resources.kit_dir("claude") == fake_root / "kits" / "claude"
    assert resources.spec_md() == fake_root / "SPEC.md"
    assert resources.clis_dir() == fake_root / "clis"


def test_installed_root_is_none_without_bundled_kits(tmp_path: Path, monkeypatch):
    bare = tmp_path / "bare"
    bare.mkdir()
    monkeypatch.setattr(resources, "files", lambda _name: bare)

    assert resources._installed_root() is None
    assert resources.kit_dir("pi") == resources._CHECKOUT_ROOT / "kits" / "pi"


def test_the_old_singular_kit_layout_is_not_an_installed_bundle(tmp_path: Path, monkeypatch):
    """A wheel from before per-agent kits carried md2okf/kit/; it must not be mistaken for the new layout."""
    old = tmp_path / "old" / "md2okf"
    (old / "kit").mkdir(parents=True)
    monkeypatch.setattr(resources, "files", lambda _name: old)

    assert resources._installed_root() is None


def test_neither_installed_nor_checkout_raises_a_clear_error(tmp_path: Path, monkeypatch):
    """Regression (code review finding 5).

    `uv tool install .` today (packaging/force-include lands in a later
    stage) installs a wheel with no bundled kit -- _installed_root() is
    None, and __file__ resolves under site-packages, not a checkout, so
    the naive fallback silently computed a path that could never exist.
    Every caller downstream then failed with a generic, unhelpful
    "not a file" error. This must fail immediately, with the real cause.
    """
    bare = tmp_path / "bare"  # no "kits" subdir -> not an installed bundle
    bare.mkdir()
    monkeypatch.setattr(resources, "files", lambda _name: bare)
    monkeypatch.setattr(resources, "_CHECKOUT_ROOT", tmp_path / "site-packages")  # not a real checkout either

    for lookup in (lambda: resources.kit_dir("pi"), resources.spec_md, resources.clis_dir):
        with pytest.raises(resources.ResourcesError, match="checkout"):
            lookup()
