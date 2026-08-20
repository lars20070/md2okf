"""Tests for merkleokf.merkle."""

from pathlib import Path

from merkleokf.merkle import DISPLAY_WIDTH, collect, hash_file, short


def _wiki(tmp_path: Path, name: str = "okf") -> Path:
    """Two categories, two pages each, plus a root page and ignorable noise."""
    root = tmp_path / name
    for category in ("alpha", "beta"):
        (root / category).mkdir(parents=True)
        for page in ("one", "two"):
            (root / category / f"{page}.md").write_text(f"# {category} {page}\n", encoding="utf-8")
    (root / "index.md").write_text("# Index\n", encoding="utf-8")
    (root / ".DS_Store").write_bytes(b"\x00finder noise")
    (root / "alpha" / "notes.txt").write_text("not markdown", encoding="utf-8")
    return root


def _by_path(entries) -> dict[str, bytes]:
    return {e.path: e.digest for e in entries}


def test_digest_is_deterministic(tmp_path: Path):
    a = _wiki(tmp_path / "a")
    b = _wiki(tmp_path / "b")
    _, root_a = collect(a)
    _, root_b = collect(b)
    assert root_a.digest == root_b.digest


def test_leaf_change_propagates_to_root_and_only_its_parent(tmp_path: Path):
    """The property the tool exists for: change localises to one chain."""
    root = _wiki(tmp_path)
    before, root_before = collect(root)

    (root / "alpha" / "one.md").write_text("# alpha one EDITED\n", encoding="utf-8")
    after, root_after = collect(root)

    assert root_after.digest != root_before.digest
    b, a = _by_path(before), _by_path(after)
    assert a["okf/alpha/"] != b["okf/alpha/"]
    assert a["okf/alpha/one.md"] != b["okf/alpha/one.md"]
    # Everything else is provably untouched.
    assert a["okf/beta/"] == b["okf/beta/"]
    assert a["okf/alpha/two.md"] == b["okf/alpha/two.md"]
    assert a["okf/index.md"] == b["okf/index.md"]
    assert a["okf/"] != b["okf/"]


def test_rename_changes_the_parent_digest(tmp_path: Path):
    """Names feed the digest, so a pure rename is not invisible."""
    root = _wiki(tmp_path)
    _, before = collect(root)
    (root / "alpha" / "one.md").rename(root / "alpha" / "renamed.md")
    _, after = collect(root)
    assert after.digest != before.digest


def test_file_and_directory_of_same_name_differ(tmp_path: Path):
    """The type tag keeps `x.md` as a file distinct from `x.md` as a directory."""
    as_file = tmp_path / "a" / "okf"
    as_file.mkdir(parents=True)
    (as_file / "x.md").write_text("", encoding="utf-8")

    as_dir = tmp_path / "b" / "okf"
    (as_dir / "x.md").mkdir(parents=True)

    _, file_root = collect(as_file)
    _, dir_root = collect(as_dir)
    assert file_root.digest != dir_root.digest


def test_non_markdown_and_dotfiles_are_ignored(tmp_path: Path):
    root = _wiki(tmp_path)
    entries, before = collect(root)
    assert not any("notes.txt" in p or ".DS_Store" in p for p in _by_path(entries))

    # Touching either must not move a single hash.
    (root / ".DS_Store").write_bytes(b"\x00different finder noise")
    (root / "alpha" / "notes.txt").write_text("edited", encoding="utf-8")
    _, after = collect(root)
    assert after.digest == before.digest


def test_max_level_limits_listing_not_coverage(tmp_path: Path):
    root = _wiki(tmp_path)
    shallow, shallow_root = collect(root, max_level=1)
    deep, deep_root = collect(root)

    assert sorted(_by_path(shallow)) == ["okf/", "okf/alpha/", "okf/beta/", "okf/index.md"]
    assert shallow_root.digest == deep_root.digest
    assert shallow_root.files == deep_root.files == 5
    # The nested pages are unlisted but still cover the directory digest.
    assert _by_path(shallow)["okf/alpha/"] == _by_path(deep)["okf/alpha/"]


def test_max_level_zero_lists_root_only(tmp_path: Path):
    root = _wiki(tmp_path)
    entries, root_entry = collect(root, max_level=0)
    deep, deep_root = collect(root)
    assert [e.path for e in entries] == ["okf/"]
    assert root_entry.digest == deep_root.digest
    assert root_entry.files == deep_root.files


def test_nolog_skips_okf_log_only(tmp_path: Path):
    root = _wiki(tmp_path)
    (root / "log.md").write_text("# root log\n", encoding="utf-8")
    (root / "alpha" / "log.md").write_text("# nested log\n", encoding="utf-8")

    with_log, root_with = collect(root)
    without_log, root_without = collect(root, nolog=True)
    paths_with = _by_path(with_log)
    paths_without = _by_path(without_log)

    assert "okf/log.md" in paths_with
    assert "okf/log.md" not in paths_without
    assert "okf/alpha/log.md" in paths_without
    assert root_without.files == root_with.files - 1
    assert root_without.digest != root_with.digest

    (root / "log.md").unlink()
    _, baseline = collect(root)
    assert root_without.digest == baseline.digest
    assert root_without.files == baseline.files


def test_nolog_ignores_log_under_other_roots(tmp_path: Path):
    root = _wiki(tmp_path, name="wiki")
    (root / "log.md").write_text("# counted\n", encoding="utf-8")
    entries, root_entry = collect(root, nolog=True)
    assert "wiki/log.md" in _by_path(entries)
    assert root_entry.files == 6  # 5 from _wiki + log.md


def test_nolog_keeps_log_under_a_nested_okf_directory(tmp_path: Path):
    """The exclusion is anchored to the walk root, not to every directory named okf."""
    root = _wiki(tmp_path)
    (root / "log.md").write_text("# root log\n", encoding="utf-8")
    (root / "nested" / "okf").mkdir(parents=True)
    (root / "nested" / "okf" / "log.md").write_text("# deep log\n", encoding="utf-8")

    entries, root_entry = collect(root, nolog=True)
    paths = _by_path(entries)

    assert "okf/log.md" not in paths
    assert "okf/nested/okf/log.md" in paths
    assert root_entry.files == 6  # 5 from _wiki + the nested log.md


def test_empty_directory_reports_zero_files(tmp_path: Path):
    root = tmp_path / "okf"
    (root / "empty").mkdir(parents=True)
    entries, root_entry = collect(root)
    assert [(e.path, e.files) for e in entries] == [("okf/", 0), ("okf/empty/", 0)]
    assert root_entry.files == 0


def test_hash_file_matches_sha256_of_raw_bytes(tmp_path: Path):
    """Raw bytes, frontmatter included — this is the integrity tool."""
    import hashlib

    page = tmp_path / "page.md"
    page.write_text("---\ntimestamp: 2026-08-11\n---\n\nBody.\n", encoding="utf-8")
    assert hash_file(page) == hashlib.sha256(page.read_bytes()).digest()


def test_frontmatter_change_moves_the_hash(tmp_path: Path):
    """Deliberate counterpart to sizeokf, which would report no change here."""
    page = tmp_path / "page.md"
    page.write_text("---\ntimestamp: 2026-08-11\n---\n\nBody.\n", encoding="utf-8")
    before = hash_file(page)
    page.write_text("---\ntimestamp: 2026-09-01\n---\n\nBody.\n", encoding="utf-8")
    assert hash_file(page) != before


def test_short_truncates_to_display_width(tmp_path: Path):
    page = tmp_path / "page.md"
    page.write_text("x", encoding="utf-8")
    digest = hash_file(page)
    assert short(digest) == digest.hex()[:DISPLAY_WIDTH]
    assert len(short(digest)) == DISPLAY_WIDTH
