"""Tests for merkleokf.cli."""

from pathlib import Path

import pytest

from merkleokf import __version__
from merkleokf.cli import main
from merkleokf.merkle import DISPLAY_WIDTH


def _wiki(tmp_path: Path) -> Path:
    root = tmp_path / "okf"
    (root / "cat").mkdir(parents=True)
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "cat" / "page.md").write_text("# Page\n", encoding="utf-8")
    return root


def test_main_prints_summary_and_table(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert out.startswith("okf: ")
    assert ", 2 files\n\n" in out
    assert "Hash" in out
    assert "cat/" in out
    assert "index.md" in out


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


def test_main_single_file(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root / "index.md")]) == 0
    out = capsys.readouterr().out.rstrip("\n")
    digest, name = out.split("  ")
    assert name == "index.md"
    assert len(digest) == DISPLAY_WIDTH


def test_main_file_hash_matches_the_table_row(tmp_path: Path, capsys):
    """The single-file form must agree with the same file's row in a walk."""
    root = _wiki(tmp_path)
    main([str(root / "index.md")])
    single = capsys.readouterr().out.split("  ")[0]
    main([str(root), "-L", "1"])
    row = next(ln for ln in capsys.readouterr().out.splitlines() if ln.endswith("index.md"))
    assert row.startswith(single)


def test_main_missing_path(capsys):
    assert main(["/no/such/wiki"]) == 2
    assert "not a file or directory" in capsys.readouterr().err


def test_main_no_markdown(tmp_path: Path, capsys):
    root = tmp_path / "okf"
    root.mkdir()
    (root / "notes.txt").write_text("ignored", encoding="utf-8")
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert ", 0 files" in out
    assert "(no Markdown files)" in out


def test_main_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out == f"merkleokf {__version__}\n"


def test_main_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    assert "usage: merkleokf" in capsys.readouterr().out


def test_main_unknown_flag(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--nope"])
    assert exc_info.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err
