"""Tests for inspectmd.parse."""

from inspectmd.parse import inspect_markdown, parse_sections, slugify, split_frontmatter


def test_slugify_basic():
    assert slugify("Hello World") == "hello-world"
    assert slugify("  Spaces   and---punct!! ") == "spaces-and-punct"
    assert slugify("CamelCase") == "camelcase"


def test_slugify_non_ascii():
    assert slugify("Café résumé") == "cafe-resume"
    assert slugify("你好") == ""


def test_slugify_empty():
    assert slugify("") == ""


def test_split_frontmatter_present():
    text = "---\ntitle: x\n---\n\n# Hi\n"
    offset, body = split_frontmatter(text)
    assert offset == 3
    assert body == "\n# Hi\n"


def test_split_frontmatter_absent():
    text = "# Hi\n"
    offset, body = split_frontmatter(text)
    assert offset == 0
    assert body == text


def test_split_frontmatter_unclosed():
    text = "---\ntitle: x\n# still body\n"
    offset, body = split_frontmatter(text)
    assert offset == 0
    assert body == text


def test_atx_levels_and_closing_hashes():
    text = "# One\n## Two ##\n### Three\n"
    sections = parse_sections(text)
    assert [s.level for s in sections] == [1, 2, 3]
    assert sections[0].title == "One"
    assert sections[1].title == "Two"
    assert sections[0].start == 1
    assert sections[0].end == 1
    assert sections[2].end == 3


def test_leading_spaces_up_to_three():
    text = "   # Indented\n"
    sections = parse_sections(text)
    assert len(sections) == 1
    assert sections[0].title == "Indented"


def test_four_spaces_not_heading():
    text = "    # Code\n"
    sections = parse_sections(text)
    assert sections == [] or (len(sections) == 1 and sections[0].level == 0)


def test_setext_not_heading():
    text = "Title\n=====\n\nAnother\n-----\n"
    sections = parse_sections(text)
    assert all(s.level == 0 for s in sections)
    assert not any(s.title == "Title" and s.level > 0 for s in sections)


def test_fence_backticks_ignored():
    text = "# Real\n\n```\n# Not a heading\n```\n\n## Also real\n"
    sections = parse_sections(text)
    assert [s.title for s in sections] == ["Real", "Also real"]


def test_fence_tildes_and_info_string():
    text = "# Real\n\n~~~python\n# Not\n~~~\n"
    sections = parse_sections(text)
    assert [s.title for s in sections] == ["Real"]


def test_closing_fence_must_be_long_enough():
    text = "````\n# Still fenced\n```\n# Still fenced\n````\n# Out\n"
    sections = parse_sections(text)
    assert [s.title for s in sections if s.level > 0] == ["Out"]


def test_preamble_is_section_zero():
    text = "intro paragraph\n\n# First\nbody\n"
    sections = parse_sections(text)
    assert sections[0].index == 0
    assert sections[0].level == 0
    assert sections[0].slug == "preamble"
    assert sections[0].start == 1
    assert sections[0].end == 2
    assert sections[1].index == 1
    assert sections[1].title == "First"
    assert sections[1].start == 3
    assert sections[1].end == 4


def test_section_runs_to_next_heading_any_level():
    text = "# A\n## B\n# C\n"
    sections = parse_sections(text)
    assert sections[0].end == 1
    assert sections[1].start == 2
    assert sections[1].end == 2
    assert sections[2].start == 3


def test_empty_file():
    assert parse_sections("") == []
    assert inspect_markdown("") == []


def test_whitespace_only_no_sections():
    assert parse_sections("   \n\n") == []


def test_no_headings_preamble_only():
    text = "just text\nmore\n"
    sections = parse_sections(text)
    assert len(sections) == 1
    assert sections[0].level == 0
    assert sections[0].end == 2


def test_frontmatter_offset_in_inspect_markdown():
    text = "---\ntitle: x\n---\n\n# Hi\n"
    sections = inspect_markdown(text)
    assert sections[0].title == "Hi"
    assert sections[0].start == 5
    assert sections[0].index == 0


def test_chars_include_newlines():
    text = "# A\nabc\n"
    sections = parse_sections(text)
    assert sections[0].chars == len("# A\nabc\n")
