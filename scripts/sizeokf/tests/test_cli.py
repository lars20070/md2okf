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


def test_main_prints_summary_and_table(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("okf: 5 words, 2 files\n\n")
    assert "Words" in out
    assert "Files" in out
    assert "cat/" in out
    assert "index.md" in out


def test_main_excludes_frontmatter_from_the_count(tmp_path: Path, capsys):
    """Body is three words (#, X, Body.); frontmatter tokens are not counted."""
    root = tmp_path / "okf"
    root.mkdir()
    (root / "page.md").write_text(FRONTMATTER_DOC, encoding="utf-8")
    assert len(FRONTMATTER_DOC) == 52
    assert main([str(root)]) == 0
    assert "okf: 3 words, 1 files" in capsys.readouterr().out


def test_main_level_limits_rows(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root), "-L", "1"]) == 0
    out = capsys.readouterr().out
    assert "cat/" in out
    assert "page.md" not in out


@pytest.mark.parametrize("flag", ["-L", "--level"])
def test_main_level_spellings_agree(flag: str, tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root), flag, "1"]) == 0
    assert "cat/" in capsys.readouterr().out


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
    assert "okf: 0 words, 0 files" in out
    assert "(no Markdown files)" in out


def test_main_empty_dir(tmp_path: Path, capsys):
    """A fresh empty okf/ root succeeds with zero totals."""
    root = tmp_path / "okf"
    root.mkdir()
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert "okf: 0 words, 0 files" in out
    assert "(no Markdown files)" in out


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
