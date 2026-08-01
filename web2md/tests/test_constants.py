"""The two top-of-file knobs, and everything derived from them.

SOURCE_URL and OUTPUT_FILE are the only values meant to be edited when pointing
the scraper at a different book. These tests pin the derivation so a change to
SOURCE_URL cannot leave a stale host or book path behind somewhere in the module.
"""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

import pytest

import web2md


def test_source_url_and_output_file_are_the_current_book() -> None:
    assert web2md.SOURCE_URL == "https://developers.google.com/style"
    assert web2md.OUTPUT_FILE == "GoogleDeveloperDocumentationStyleGuide.md"


def test_host_base_and_book_path_derive_from_source_url() -> None:
    assert web2md.HOST == "developers.google.com"
    assert web2md.BASE == "https://developers.google.com"
    assert web2md.BOOK_PATH == "/style"
    assert web2md.BOOK_SLUG == "style"


def test_book_path_is_the_source_url_path() -> None:
    assert f"{web2md.BASE}{web2md.BOOK_PATH}" == web2md.SOURCE_URL


def _derive(source_url: str) -> dict[str, Any]:
    """Re-run the module's top-level derivation for an alternative SOURCE_URL."""
    parsed = urlparse(source_url)
    host = parsed.netloc
    book_path = parsed.path.rstrip("/") or "/"
    return {
        "HOST": host,
        "BASE": f"{parsed.scheme}://{host}",
        "BOOK_PATH": book_path,
        "BOOK_SLUG": book_path.strip("/").rsplit("/", 1)[-1] or "index",
    }


def test_derivation_matches_the_module_for_the_configured_url() -> None:
    derived = _derive(web2md.SOURCE_URL)

    assert derived["HOST"] == web2md.HOST
    assert derived["BASE"] == web2md.BASE
    assert derived["BOOK_PATH"] == web2md.BOOK_PATH
    assert derived["BOOK_SLUG"] == web2md.BOOK_SLUG


@pytest.mark.parametrize(
    ("source_url", "host", "base", "book_path", "book_slug"),
    [
        (
            "https://developers.google.com/style",
            "developers.google.com",
            "https://developers.google.com",
            "/style",
            "style",
        ),
        (
            "https://example.org/docs/handbook/",
            "example.org",
            "https://example.org",
            "/docs/handbook",
            "handbook",
        ),
        ("http://example.org", "example.org", "http://example.org", "/", "index"),
    ],
)
def test_derivation_handles_other_shapes_of_source_url(
    source_url: str, host: str, base: str, book_path: str, book_slug: str
) -> None:
    derived = _derive(source_url)

    assert derived["HOST"] == host
    assert derived["BASE"] == base
    assert derived["BOOK_PATH"] == book_path
    assert derived["BOOK_SLUG"] == book_slug


def test_slug_from_path_uses_book_path_and_book_slug(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(web2md, "BOOK_PATH", "/docs/handbook")
    monkeypatch.setattr(web2md, "BOOK_SLUG", "handbook")

    assert web2md.slug_from_path("/docs/handbook") == "handbook"
    assert web2md.slug_from_path("/docs/handbook/intro") == "intro"


def test_default_output_is_named_by_output_file() -> None:
    assert web2md.DEFAULT_OUTPUT.name == web2md.OUTPUT_FILE
