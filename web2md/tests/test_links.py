"""Internal link rewriting and anchor injection."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from bs4 import Tag

import web2md

# The page under review, the book's pages keyed by path, and the anchor map.
LinkContext = tuple[web2md.Page, dict[str, web2md.Page], dict[tuple[str, str], str]]


@pytest.fixture
def link_context(make_page: Callable[..., web2md.Page]) -> LinkContext:
    """A two-page book with one known anchor on each page."""
    here = make_page("word-list", title="Word list")
    there = make_page("tense", title="Tense")
    home = make_page("style", title="Overview", path="/style")
    pages_by_path = {p.path: p for p in (here, there, home)}
    anchor_map = {
        ("word-list", "abbreviations"): "word-list--abbreviations",
        ("tense", "present"): "tense--present",
    }
    return here, pages_by_path, anchor_map


def test_same_page_fragment_resolves_to_the_namespaced_anchor(link_context: LinkContext) -> None:
    here, pages_by_path, anchor_map = link_context
    unresolved: list[str] = []

    result = web2md.rewrite_internal_href(
        "#abbreviations", here, pages_by_path, anchor_map, unresolved
    )

    assert result == "#word-list--abbreviations"
    assert unresolved == []


def test_unknown_same_page_fragment_falls_back_to_an_absolute_url(
    link_context: LinkContext,
) -> None:
    here, pages_by_path, anchor_map = link_context
    unresolved: list[str] = []

    result = web2md.rewrite_internal_href("#missing", here, pages_by_path, anchor_map, unresolved)

    assert result == "https://developers.google.com/style/word-list#missing"
    assert len(unresolved) == 1


def test_empty_fragment_is_returned_untouched(link_context: LinkContext) -> None:
    here, pages_by_path, anchor_map = link_context

    assert web2md.rewrite_internal_href("", here, pages_by_path, anchor_map, []) == ""


def test_cross_page_fragment_resolves(link_context: LinkContext) -> None:
    here, pages_by_path, anchor_map = link_context
    unresolved: list[str] = []

    result = web2md.rewrite_internal_href(
        "/style/tense#present", here, pages_by_path, anchor_map, unresolved
    )

    assert result == "#tense--present"
    assert unresolved == []


def test_cross_page_fragment_on_an_unknown_page_is_absolutised(link_context: LinkContext) -> None:
    here, pages_by_path, anchor_map = link_context
    unresolved: list[str] = []

    result = web2md.rewrite_internal_href(
        "/style/nowhere#x", here, pages_by_path, anchor_map, unresolved
    )

    assert result == "https://developers.google.com/style/nowhere#x"
    assert len(unresolved) == 1


@pytest.mark.parametrize("href", ["/style/tense", "/style/tense/"])
def test_cross_page_without_fragment_becomes_a_page_anchor(
    link_context: LinkContext, href: str
) -> None:
    here, pages_by_path, anchor_map = link_context

    assert web2md.rewrite_internal_href(href, here, pages_by_path, anchor_map, []) == "#tense"


def test_book_root_link_becomes_the_overview_anchor(link_context: LinkContext) -> None:
    here, pages_by_path, anchor_map = link_context

    assert web2md.rewrite_internal_href("/style", here, pages_by_path, anchor_map, []) == "#style"


def test_unknown_style_page_without_fragment_is_absolutised(link_context: LinkContext) -> None:
    here, pages_by_path, anchor_map = link_context
    unresolved: list[str] = []

    result = web2md.rewrite_internal_href(
        "/style/nowhere", here, pages_by_path, anchor_map, unresolved
    )

    assert result == "https://developers.google.com/style/nowhere"
    assert len(unresolved) == 1


@pytest.mark.parametrize(
    "href",
    [
        "https://example.com/page",
        "mailto:someone@example.com",
        "relative/thing",
    ],
)
def test_external_and_non_http_links_are_untouched(link_context: LinkContext, href: str) -> None:
    here, pages_by_path, anchor_map = link_context

    assert web2md.rewrite_internal_href(href, here, pages_by_path, anchor_map, []) == href


@pytest.mark.parametrize(
    ("href", "expected"),
    [
        ("/docs/something", "https://developers.google.com/docs/something"),
        (
            "https://developers.google.com/docs/something",
            "https://developers.google.com/docs/something",
        ),
    ],
)
def test_non_style_google_links_are_absolutised(
    link_context: LinkContext, href: str, expected: str
) -> None:
    here, pages_by_path, anchor_map = link_context

    assert web2md.rewrite_internal_href(href, here, pages_by_path, anchor_map, []) == expected


def test_apply_anchors_emits_a_shared_id_once_and_strips_it(
    frag: Callable[[str], Tag], make_page: Callable[..., web2md.Page]
) -> None:
    # DevSite repeats the same id on a section and the heading inside it.
    body = frag('<section id="terms"><h2 id="terms">Terms</h2></section>')
    page = make_page("word-list")
    anchor_map = {("word-list", "terms"): "word-list--terms"}

    web2md.apply_anchors_and_links(body, page, {page.path: page}, anchor_map, [])

    anchors = body.find_all("a", id=True)
    assert [a["id"] for a in anchors] == ["word-list--terms"]
    assert body.find(attrs={"id": "terms"}) is None


def test_apply_anchors_rewrites_hrefs_and_absolutises_images(
    frag: Callable[[str], Tag], make_page: Callable[..., web2md.Page]
) -> None:
    body = frag('<p><a href="#abbr">jump</a><img src="/images/x.png" alt="x"></p>')
    page = make_page("word-list")
    anchor_map = {("word-list", "abbr"): "word-list--abbr"}

    web2md.apply_anchors_and_links(body, page, {page.path: page}, anchor_map, [])

    assert body.a["href"] == "#word-list--abbr"
    assert body.img["src"] == "https://developers.google.com/images/x.png"


def test_apply_anchors_ignores_ids_absent_from_the_map(
    frag: Callable[[str], Tag], make_page: Callable[..., web2md.Page]
) -> None:
    body = frag('<h2 id="unmapped">Heading</h2>')
    page = make_page("word-list")

    web2md.apply_anchors_and_links(body, page, {page.path: page}, {}, [])

    assert body.find("a") is None
    assert body.h2["id"] == "unmapped"
