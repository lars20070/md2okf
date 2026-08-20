"""Tests for sizeokf.sizes."""

from pathlib import Path

from sizeokf.sizes import collect, count_words, strip_frontmatter

FRONTMATTER_DOC = '---\ntype: PodcastEpisode\ntitle: "X"\n---\n\n# X\n\nBody.\n'
"""Nine lines like a real wiki page; the body is everything from the blank line on."""

BODY = "\n# X\n\nBody.\n"
"""Frontmatter-stripped body of FRONTMATTER_DOC: three words (#, X, Body.)."""


def test_strip_frontmatter_removes_block():
    assert strip_frontmatter(FRONTMATTER_DOC) == BODY


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


def test_count_words_whitespace_split():
    assert count_words("# Index\n") == 2
    assert count_words(BODY) == 3


def _wiki(tmp_path: Path) -> Path:
    root = tmp_path / "okf"
    (root / "cat").mkdir(parents=True)
    (root / "index.md").write_text("# Index\n", encoding="utf-8")  # 2 words
    (root / "cat" / "page.md").write_text(FRONTMATTER_DOC, encoding="utf-8")  # 3 words of body
    (root / "cat" / "notes.txt").write_text("ignored entirely", encoding="utf-8")
    return root


def test_collect_counts_only_markdown(tmp_path: Path):
    entries, total = collect(_wiki(tmp_path))
    assert total.files == 2  # notes.txt excluded
    assert total.words == count_words("# Index\n") + count_words(BODY)
    assert not any("notes.txt" in e.path for e in entries)


def test_collect_directory_total_is_recursive(tmp_path: Path):
    entries, _ = collect(_wiki(tmp_path))
    cat = next(e for e in entries if e.path == "cat/")
    assert cat.is_dir
    assert cat.words == count_words(BODY)
    assert cat.files == 1


def test_collect_max_level_limits_listing_not_totals(tmp_path: Path):
    entries, total = collect(_wiki(tmp_path), max_level=1)
    assert sorted(e.path for e in entries) == ["cat/", "index.md"]
    # The nested page is not listed, but its words still reach both totals.
    cat = next(e for e in entries if e.path == "cat/")
    assert cat.words == count_words(BODY)
    assert total.files == 2


def test_collect_sorts_largest_first_then_alphabetically(tmp_path: Path):
    root = tmp_path / "okf"
    root.mkdir()
    (root / "big.md").write_text(" ".join(["x"] * 50) + "\n", encoding="utf-8")
    (root / "b-tie.md").write_text(" ".join(["y"] * 5) + "\n", encoding="utf-8")
    (root / "a-tie.md").write_text(" ".join(["z"] * 5) + "\n", encoding="utf-8")
    entries, _ = collect(root)
    assert [e.path for e in entries] == ["big.md", "a-tie.md", "b-tie.md"]


def test_collect_empty_directory_reports_zero(tmp_path: Path):
    root = tmp_path / "okf"
    (root / "empty").mkdir(parents=True)
    entries, total = collect(root)
    assert [(e.path, e.words, e.files) for e in entries] == [("empty/", 0, 0)]
    assert total.words == 0


def test_collect_skips_symlinks(tmp_path: Path):
    """Symlinks are ignored so cycles and escapes cannot be scanned."""
    root = tmp_path / "okf"
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "secret.md").write_text("# secret\n", encoding="utf-8")
    (root / "real").mkdir(parents=True)
    (root / "real" / "page.md").write_text("# page\n", encoding="utf-8")
    (root / "link-dir").symlink_to(outside)
    (root / "link.md").symlink_to(outside / "secret.md")
    (root / "cycle").symlink_to(root)

    entries, total = collect(root)
    assert total.files == 1
    assert total.words == count_words("# page\n")
    assert sorted(e.path for e in entries) == ["real/", "real/page.md"]


def test_collect_unreadable_directory_is_skipped(tmp_path: Path, monkeypatch):
    """OSError from iterdir warns and contributes zero, matching file skips."""
    root = tmp_path / "okf"
    bad = root / "bad"
    bad.mkdir(parents=True)
    (root / "ok.md").write_text("# ok\n", encoding="utf-8")

    real_iterdir = Path.iterdir

    def flaky_iterdir(self: Path):
        if self == bad:
            raise PermissionError("denied")
        return real_iterdir(self)

    monkeypatch.setattr(Path, "iterdir", flaky_iterdir)
    entries, total = collect(root)
    assert total.files == 1
    assert total.words == count_words("# ok\n")
    bad_row = next(e for e in entries if e.path == "bad/")
    assert bad_row.words == 0
    assert bad_row.files == 0
