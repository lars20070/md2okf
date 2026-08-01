"""`discover_pages` — nav parsing and its guard rails."""

from __future__ import annotations

from collections.abc import Callable

import pytest

import web2md


def test_discovers_every_nav_item_with_its_section(nav_html: Callable[..., str]) -> None:
    pages = web2md.discover_pages(nav_html(sections=6, per_section=12))

    assert len(pages) == 72
    assert pages[0].section == "Section 0"
    assert pages[0].title == "Page 0.0"
    assert pages[0].slug == "page-0-0"
    assert pages[0].path == "/style/page-0-0"
    assert pages[0].url == "https://developers.google.com/style/page-0-0"
    assert {p.section for p in pages} == {f"Section {i}" for i in range(6)}


def test_skips_book_picker_tabs_above_the_first_heading(nav_html: Callable[..., str]) -> None:
    pages = web2md.discover_pages(nav_html())

    # The leading "/docs/guides" item precedes any heading and must be dropped.
    assert all(p.path.startswith("/style") for p in pages)
    assert all(p.title != "Guides" for p in pages)


def test_ignores_non_style_links_and_deduplicates_repeats(nav_html: Callable[..., str]) -> None:
    extra = (
        '<li class="devsite-nav-item"><a href="/docs/elsewhere">Elsewhere</a></li>'
        '<li class="devsite-nav-item"><a href="/style/page-0-0">Duplicate</a></li>'
        '<li class="devsite-nav-item"><a href="/style/page-0-0?hl=en#frag">Query dup</a></li>'
        '<li class="devsite-nav-item"><span>No link</span></li>'
    )
    pages = web2md.discover_pages(nav_html(extra_items=extra))

    assert len(pages) == 72
    assert [p.slug for p in pages].count("page-0-0") == 1
    assert all("elsewhere" not in p.path for p in pages)


def test_missing_navigation_is_fatal() -> None:
    with pytest.raises(SystemExit, match="navigation not found"):
        web2md.discover_pages("<html><body><p>no nav here</p></body></html>")


def test_too_few_pages_is_fatal(nav_html: Callable[..., str]) -> None:
    with pytest.raises(SystemExit, match="unexpected page count"):
        web2md.discover_pages(nav_html(sections=5, per_section=2))


def test_too_many_pages_is_fatal(nav_html: Callable[..., str]) -> None:
    with pytest.raises(SystemExit, match="unexpected page count"):
        web2md.discover_pages(nav_html(sections=6, per_section=40))


def test_too_few_sections_is_fatal(nav_html: Callable[..., str]) -> None:
    with pytest.raises(SystemExit, match="unexpected section count"):
        web2md.discover_pages(nav_html(sections=4, per_section=20))
