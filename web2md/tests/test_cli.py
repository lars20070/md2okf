"""Command-line parsing and the default cache / output locations."""

from __future__ import annotations

from pathlib import Path

import pytest

import web2md

# <repo>/web2md/src/web2md.py -> <repo>
REPO_ROOT = Path(web2md.__file__).resolve().parents[2]


def test_default_cache_sits_beside_the_src_directory() -> None:
    # Guards the move into web2md/src/: a ROOT off by one level would silently
    # relocate the cache to web2md/src/cache/.
    assert web2md.DEFAULT_CACHE == REPO_ROOT / "web2md" / "cache"


def test_default_output_goes_to_the_repo_level_md_directory() -> None:
    assert web2md.DEFAULT_OUTPUT == (
        REPO_ROOT / "md" / "GoogleDeveloperDocumentationStyleGuide.md"
    )


@pytest.fixture
def calls(monkeypatch: pytest.MonkeyPatch) -> list[dict[str, object]]:
    recorded: list[dict[str, object]] = []
    monkeypatch.setattr(web2md, "run", lambda **kwargs: recorded.append(kwargs))
    return recorded


def test_no_arguments_uses_the_defaults(calls: list[dict[str, object]]) -> None:
    web2md.main([])

    assert calls == [
        {
            "refresh": False,
            "cache_dir": web2md.DEFAULT_CACHE,
            "output": web2md.DEFAULT_OUTPUT,
        }
    ]


def test_refresh_flag_is_forwarded(calls: list[dict[str, object]]) -> None:
    web2md.main(["--refresh"])

    assert calls[0]["refresh"] is True


def test_cache_dir_and_output_are_parsed_as_paths(
    calls: list[dict[str, object]], tmp_path: Path
) -> None:
    web2md.main(["--cache-dir", str(tmp_path / "c"), "--output", str(tmp_path / "o.md")])

    assert calls[0]["cache_dir"] == tmp_path / "c"
    assert calls[0]["output"] == tmp_path / "o.md"


def test_unknown_option_exits(calls: list[dict[str, object]]) -> None:
    with pytest.raises(SystemExit):
        web2md.main(["--nope"])

    assert calls == []
