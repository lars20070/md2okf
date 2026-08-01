"""Table of contents, document assembly, and the fence-stripping helper."""

from __future__ import annotations

from collections.abc import Callable

import web2md

TIMESTAMP = "2026-08-01T12:00:00Z"


def _book(make_page: Callable[..., web2md.Page]) -> list[web2md.Page]:
    return [
        make_page("style", section="Overview", title="About", path="/style"),
        make_page("tense", section="Language", title="Tense"),
        make_page("voice", section="Language", title="Voice"),
    ]


def test_build_toc_groups_pages_under_their_section(
    make_page: Callable[..., web2md.Page],
) -> None:
    toc = web2md.build_toc(_book(make_page))

    assert toc.splitlines() == [
        "## Table of contents",
        "",
        "### Overview",
        "",
        "- [About](#style)",
        "",
        "### Language",
        "",
        "- [Tense](#tense)",
        "- [Voice](#voice)",
    ]
    assert toc.endswith("\n")


def test_assemble_writes_frontmatter_and_timestamp(
    make_page: Callable[..., web2md.Page],
) -> None:
    pages = _book(make_page)
    bodies = {p.slug: f"Body of {p.slug}." for p in pages}

    md = web2md.assemble(pages, bodies, timestamp=TIMESTAMP)

    lines = md.splitlines()
    assert lines[0] == "---"
    assert "type: Website" in lines
    assert f"timestamp: {TIMESTAMP}" in lines
    assert f"resource: {web2md.BOOK}" in lines
    assert "# Google Developer Documentation Style Guide" in lines
    assert f"*Snapshot of [{web2md.BOOK}]({web2md.BOOK}) generated 2026-08-01.*" in lines


def test_assemble_emits_each_section_once_with_page_anchors(
    make_page: Callable[..., web2md.Page],
) -> None:
    pages = _book(make_page)
    bodies = {p.slug: f"Body of {p.slug}." for p in pages}

    md = web2md.assemble(pages, bodies, timestamp=TIMESTAMP)

    # Anchored so the TOC's "### Language" heading is not counted too.
    assert md.count("\n## Language\n") == 1
    for page in pages:
        assert f'<a id="{page.slug}"></a>' in md
        assert f"### {page.title}" in md
        assert f"*Source: <{page.url}>*" in md
        assert bodies[page.slug] in md


def test_assemble_drops_the_trailing_divider(make_page: Callable[..., web2md.Page]) -> None:
    pages = _book(make_page)
    bodies = {p.slug: f"Body of {p.slug}." for p in pages}

    md = web2md.assemble(pages, bodies, timestamp=TIMESTAMP)

    assert md.endswith("Body of voice.\n")
    assert not md.rstrip().endswith("---")
    # Two dividers between three pages, plus the frontmatter's closing fence.
    # The opening fence is at offset 0, so it has no leading newline to match.
    assert md.count("\n---\n") == 3


def test_markdown_without_fences_strips_only_fenced_blocks() -> None:
    md = "before\n```\ndevsite-toc\n```\nafter"

    assert web2md.markdown_without_fences(md) == "before\n\nafter"


def test_markdown_without_fences_handles_several_blocks() -> None:
    md = "a\n```\none\n```\nb\n```\ntwo\n```\nc"

    stripped = web2md.markdown_without_fences(md)

    assert "one" not in stripped
    assert "two" not in stripped
    assert "a" in stripped
    assert "b" in stripped
    assert "c" in stripped
