"""Tests for sizeokf.sizes."""

from pathlib import Path

from sizeokf.sizes import collect, strip_frontmatter

FRONTMATTER_DOC = '---\ntype: PodcastEpisode\ntitle: "X"\n---\n\n# X\n\nBody.\n'
"""Nine lines like a real wiki page; the body is everything from the blank line on."""


def test_strip_frontmatter_removes_block():
    assert strip_frontmatter(FRONTMATTER_DOC) == "\n# X\n\nBody.\n"


def test_strip_frontmatter_absent_is_unchanged():
    text = "# Heading\n\nBody.\n"
    assert strip_frontmatter(text) == text


def test_strip_frontmatter_strips_bom():
    assert strip_frontmatter("﻿---\na: 1\n---\nBody\n") == "Body\n"


def test_strip_frontmatter_unterminated_is_unchanged():
    text = "---\na: 1\nno closing delimiter\n"
    assert strip_frontmatter(text) == text


def test_strip_frontmatter_ignores_later_rules():
    """A `---` in the body is only a closer when a block was actually opened."""
    text = "# Title\n\n---\n\nMore.\n"
    assert strip_frontmatter(text) == text


def test_strip_frontmatter_empty_file():
    assert strip_frontmatter("") == ""


def test_strip_frontmatter_only_frontmatter():
    assert strip_frontmatter("---\na: 1\n---\n") == ""


def _wiki(tmp_path: Path) -> Path:
    root = tmp_path / "okf"
    (root / "cat").mkdir(parents=True)
    (root / "index.md").write_text("# Index\n", encoding="utf-8")  # 8 chars
    (root / "cat" / "page.md").write_text(FRONTMATTER_DOC, encoding="utf-8")  # 15 chars of body
    (root / "cat" / "notes.txt").write_text("ignored entirely", encoding="utf-8")
    return root


def test_collect_counts_only_markdown(tmp_path: Path):
    entries, total = collect(_wiki(tmp_path))
    assert total.files == 2  # notes.txt excluded
    assert total.chars == len("# Index\n") + len("\n# X\n\nBody.\n")
    assert not any("notes.txt" in e.path for e in entries)


def test_collect_directory_total_is_recursive(tmp_path: Path):
    entries, _ = collect(_wiki(tmp_path))
    cat = next(e for e in entries if e.path == "cat/")
    assert cat.is_dir
    assert cat.chars == len("\n# X\n\nBody.\n")
    assert cat.files == 1


def test_collect_max_level_limits_listing_not_totals(tmp_path: Path):
    entries, total = collect(_wiki(tmp_path), max_level=1)
    assert sorted(e.path for e in entries) == ["cat/", "index.md"]
    # The nested page is not listed, but its characters still reach both totals.
    cat = next(e for e in entries if e.path == "cat/")
    assert cat.chars == len("\n# X\n\nBody.\n")
    assert total.files == 2


def test_collect_sorts_largest_first_then_alphabetically(tmp_path: Path):
    root = tmp_path / "okf"
    root.mkdir()
    (root / "big.md").write_text("x" * 100, encoding="utf-8")
    (root / "b-tie.md").write_text("y" * 10, encoding="utf-8")
    (root / "a-tie.md").write_text("z" * 10, encoding="utf-8")
    entries, _ = collect(root)
    assert [e.path for e in entries] == ["big.md", "a-tie.md", "b-tie.md"]


def test_collect_empty_directory_reports_zero(tmp_path: Path):
    root = tmp_path / "okf"
    (root / "empty").mkdir(parents=True)
    entries, total = collect(root)
    assert [(e.path, e.chars, e.files) for e in entries] == [("empty/", 0, 0)]
    assert total.chars == 0
