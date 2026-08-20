"""Tests for merkleokf.cli."""

from pathlib import Path

import pytest

from merkleokf import __version__
from merkleokf.cli import escape_display_path, format_table, main
from merkleokf.merkle import DISPLAY_WIDTH, Entry


def _wiki(tmp_path: Path) -> Path:
    root = tmp_path / "okf"
    (root / "cat").mkdir(parents=True)
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / "cat" / "page.md").write_text("# Page\n", encoding="utf-8")
    return root


def test_main_prints_table_with_rooted_paths(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert not out.startswith("okf: ")
    assert "Hash" in out
    assert "okf/" in out
    assert "okf/cat/" in out
    assert "okf/index.md" in out


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


def test_main_level_zero_root_only(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root), "-L", "0"]) == 0
    paths = [ln.split()[-1] for ln in capsys.readouterr().out.splitlines() if "okf/" in ln]
    assert paths == ["okf/"]


def test_main_level_below_zero_rejected(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    assert main([str(root), "-L", "-1"]) == 2
    err = capsys.readouterr().err
    assert "--level" in err
    assert "0 or greater" in err


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
    row = next(ln for ln in capsys.readouterr().out.splitlines() if ln.endswith("okf/index.md"))
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
    assert "Hash" in out
    assert "okf/" in out
    assert "(no Markdown files)" not in out


def test_main_version(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--version"])
    assert exc_info.value.code == 0
    assert capsys.readouterr().out == f"merkleokf {__version__}\n"


def test_main_single_file_nolog_still_hashes_log(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    log = root / "log.md"
    log.write_text("# log\n", encoding="utf-8")
    assert main([str(log), "--nolog"]) == 0
    out = capsys.readouterr().out.rstrip("\n")
    digest, name = out.split("  ")
    assert name == "log.md"
    assert len(digest) == DISPLAY_WIDTH


def test_main_nolog_omits_okf_log(tmp_path: Path, capsys):
    root = _wiki(tmp_path)
    (root / "log.md").write_text("# log\n", encoding="utf-8")
    assert main([str(root), "--nolog"]) == 0
    out = capsys.readouterr().out
    assert "okf/log.md" not in out
    assert "okf/index.md" in out


def test_main_help(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])
    assert exc_info.value.code == 0
    out = capsys.readouterr().out
    assert "usage: merkleokf" in out
    assert "--nolog" in out


def test_main_unknown_flag(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main(["--nope"])
    assert exc_info.value.code == 2
    assert "unrecognized arguments" in capsys.readouterr().err


def test_escape_display_path_newlines_and_ansi():
    assert escape_display_path("a\nb.md") == "a\\nb.md"
    assert escape_display_path("c\x1b[31md.md") == "c\\x1b[31md.md"
    assert escape_display_path("plain.md") == "plain.md"


def test_format_table_escapes_controls_before_width():
    """Newlines/ANSI must not break the table or inflate display width wrongly."""
    entries = [
        Entry(path="a\nb.md", is_dir=False, digest=b"\x00" * 32, files=1, depth=1),
        Entry(path="c\x1b[31md.md", is_dir=False, digest=b"\x01" * 32, files=1, depth=1),
    ]
    out = format_table(entries)
    assert "\x1b" not in out
    assert "\\n" in out
    assert "\\x1b" in out
    # One header, one rule, two data rows — a raw newline in the path would add lines.
    assert len(out.splitlines()) == 4


def test_main_escapes_control_chars_in_paths(tmp_path: Path, capsys):
    root = tmp_path / "okf"
    root.mkdir()
    (root / "a\nb.md").write_text("# nl\n", encoding="utf-8")
    (root / "c\x1b[31md.md").write_text("# ansi\n", encoding="utf-8")
    assert main([str(root)]) == 0
    out = capsys.readouterr().out
    assert "\x1b" not in out
    assert "\\n" in out
    assert "\\x1b" in out
