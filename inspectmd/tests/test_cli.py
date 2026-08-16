"""Tests for inspectmd.cli."""

from pathlib import Path

import pytest

from inspectmd import __version__
from inspectmd.cli import format_section_range, format_table, main
from inspectmd.parse import Section


def test_format_table_columns():
    sections = [
        Section(0, 0, "(preamble)", "preamble", 1, 2, 10),
        Section(1, 1, "Hello", "hello", 3, 5, 20),
    ]
    out = format_table(sections)
    assert "Index" in out
    assert "preamble" in out
    assert "hello" in out
    assert "1-2" in out


def test_format_table_max_depth():
    sections = [
        Section(1, 1, "Alpha", "alpha", 1, 1, 1),
        Section(2, 2, "Beta", "beta", 2, 2, 1),
        Section(3, 3, "Gamma", "gamma", 3, 3, 1),
    ]
    out = format_table(sections, max_depth=2)
    assert "Alpha" in out
    assert "Beta" in out
    assert "Gamma" not in out
    assert "gamma" not in out


def test_format_section_range():
    s = Section(3, 2, "Intro", "intro", 16, 42, 891)
    assert format_section_range(s) == "16:42  891 chars\n"


def test_main_success(tmp_path: Path, capsys):
    path = tmp_path / "doc.md"
    path.write_text("# Title\n\n## Sub\n", encoding="utf-8")
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "doc.md:" in out
    assert "Title" in out
    assert "Sub" in out


def test_main_section(tmp_path: Path, capsys):
    path = tmp_path / "doc.md"
    path.write_text("# Title\nbody\n## Sub\n", encoding="utf-8")
    assert main([str(path), "--section", "0"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("1:")
    assert "chars" in out


def test_main_missing_file(capsys):
    assert main(["/no/such/file.md"]) == 2
    err = capsys.readouterr().err
    assert "not a file" in err


def test_main_bad_section(tmp_path: Path, capsys):
    path = tmp_path / "doc.md"
    path.write_text("# Only\n", encoding="utf-8")
    assert main([str(path), "--section", "9"]) == 2
    err = capsys.readouterr().err
    assert "out of range" in err


def test_main_empty_file(tmp_path: Path, capsys):
    path = tmp_path / "empty.md"
    path.write_text("", encoding="utf-8")
    assert main([str(path)]) == 0
    out = capsys.readouterr().out
    assert "(no headings)" in out


def test_main_max_depth(tmp_path: Path, capsys):
    path = tmp_path / "doc.md"
    path.write_text("# Alpha\n## Beta\n### Gamma\n", encoding="utf-8")
    assert main([str(path), "--max-depth", "1"]) == 0
    out = capsys.readouterr().out
    assert "Alpha" in out
    assert "Beta" not in out
    assert "Gamma" not in out


def test_main_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert out == f"inspectmd {__version__}\n"
