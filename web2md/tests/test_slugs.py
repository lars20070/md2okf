"""Slug, anchor, and URL helpers."""

from __future__ import annotations

import pytest
from bs4 import BeautifulSoup

import web2md


@pytest.mark.parametrize(
    ("path", "expected"),
    [
        ("/style", "style"),
        ("/style/", "style"),
        ("/style/word-list", "word-list"),
        ("/style/tense", "tense"),
        ("/style/a/b", "a/b"),
    ],
)
def test_slug_from_path(path: str, expected: str) -> None:
    assert web2md.slug_from_path(path) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("plain", "plain"),
        ("keeps.dots_and-dashes", "keeps.dots_and-dashes"),
        ("has space", "hasu0020space"),
        ("café", "cafu00e9"),
        ("a/b", "au002fb"),
    ],
)
def test_sanitize_id_escapes_only_unsafe_characters(raw: str, expected: str) -> None:
    assert web2md.sanitize_id(raw) == expected


def test_sanitize_id_falls_back_for_empty_input() -> None:
    assert web2md.sanitize_id("") == "id"


def test_namespaced_anchor_prefixes_with_page_slug() -> None:
    assert web2md.namespaced_anchor("word-list", "abbreviations") == "word-list--abbreviations"
    assert web2md.namespaced_anchor("word-list", "a b") == "word-list--au0020b"


@pytest.mark.parametrize(
    ("href", "expected"),
    [
        ("/style/tense", "https://developers.google.com/style/tense"),
        ("https://example.com/x", "https://example.com/x"),
        ("//example.com/x", "https://example.com/x"),
    ],
)
def test_absolutize_url(href: str, expected: str) -> None:
    assert web2md.absolutize_url(href) == expected


def test_nav_text_prefers_the_devsite_span() -> None:
    el = BeautifulSoup(
        '<a href="/style/x">ignored<span class="devsite-nav-text">Real title</span></a>',
        "lxml",
    ).a
    assert web2md.nav_text(el) == "Real title"


def test_nav_text_falls_back_to_full_text_and_unescapes() -> None:
    el = BeautifulSoup('<a href="/style/x">Do&amp;Don&#39;t</a>', "lxml").a
    assert web2md.nav_text(el) == "Do&Don't"
