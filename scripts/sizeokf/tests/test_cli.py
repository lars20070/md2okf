"""Tests for sizeokf.cli."""

from pathlib import Path

import pytest

from sizeokf import __version__
from sizeokf.cli import main

FRONTMATTER_DOC = '---\ntype: PodcastEpisode\ntitle: "X"\n---\n\n# X\n\nBody.\n'


def _wiki(tmp_path: Path) -> Path:
    root = tmp_path / "okf"
    (root / "cat").mkdir(parents=True)
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "cat" / "page.md").write_text(FRONTMATTER_DOC, encoding="utf-8")
    return root


def test_main_prints_table_with_rooted_paths(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert not out.startswith("okf: ")
    assert "Words" in out
    assert "Files" in out
    assert "okf/" in out
    assert "okf/cat/" in out
    assert "okf/index.md" in out


def test_main_excludes_frontmatter_from_the_count(tmp_path: Path, capsys):
    """Body is three words (#, X, Body.); frontmatter tokens are not counted."""
    root = tmp_path / "okf"
    root.mkdir()
    (root / "page.md").write_text(FRONTMATTER_DOC, encoding="utf-8")
    assert len(FRONTMATTER_DOC) == 52
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert "okf/" in out
    assert "okf/page.md" in out
    # Both the root and the page row report 3 words.
    data_rows = [ln for ln in out.splitlines() if "okf/" in ln]
    assert all(ln.lstrip().startswith("3") for ln in data_rows)


def test_main_level_limits_rows(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root), "-L", "1"]) == 0
    out = capsys.readouterr().out
    assert "okf/cat/" in out
    assert "page.md" not in out


@pytest.mark.parametrize("flag", ["-L", "--level"])
def test_main_level_spellings_agree(flag: str, tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root), flag, "1"]) == 0
    assert "okf/cat/" in capsys.readouterr().out


@pytest.mark.parametrize("level", ["0", "-1"])
def test_main_level_below_one_rejected(level: str, tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root), "-L", level]) == 2
    assert "--level" in capsys.readouterr().err


def test_main_missing_dir(capsys):
    assert main(["/no/such/wiki"]) == 2
    assert "not a directory" in capsys.readouterr().err


def test_main_no_markdown(tmp_path: Path, capsys):
    root = tmp_path / "okf"
    root.mkdir()
    (root / "notes.txt").write_text("ignored", encoding="utf-8")
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert "Words" in out
    assert "okf/" in out
    assert "(no Markdown files)" not in out


def test_main_empty_dir(tmp_path: Path, capsys):
    """A fresh empty okf/ root succeeds with a single root row."""
    root = tmp_path / "okf"
    root.mkdir()
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert "Words" in out
    assert "okf/" in out
    assert "(no Markdown files)" not in out


def test_main_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out == f"sizeokf {__version__}\n"


def test_main_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    assert "usage: sizeokf" in capsys.readouterr().out


def test_main_unknown_flag(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--nope"])
    assert exc_info.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err
