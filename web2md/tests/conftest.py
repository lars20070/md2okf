"""Shared fixtures for the web2md tests.

Every test in this suite is offline: nothing here or in the test modules opens a
socket. HTTP is exercised through `httpx.MockTransport`, and the only filesystem
writes go to pytest's `tmp_path`.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest
from bs4 import BeautifulSoup, Tag

import web2md


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Make the retry backoff instant so fetch tests don't idle for seconds."""
    monkeypatch.setattr(web2md.time, "sleep", lambda _seconds: None)


@pytest.fixture
def frag() -> Callable[[str], Tag]:
    """Parse an HTML fragment into a <div> Tag that is still attached to a soup.

    Attachment matters: `apply_anchors_and_links` walks up to the BeautifulSoup
    root to call `new_tag`, which a detached Tag does not provide.
    """

    def _frag(html: str) -> Tag:
        return BeautifulSoup(f"<div>{html}</div>", "lxml").div

    return _frag


@pytest.fixture
def to_md(frag: Callable[[str], Tag]) -> Callable[..., str]:
    """Convert an HTML fragment through the real converter entry point."""

    def _to_md(html: str, *, slug: str = "page", warnings: list[str] | None = None) -> str:
        return web2md.convert_body(frag(html), slug, warnings if warnings is not None else [])

    return _to_md


@pytest.fixture
def make_page() -> Callable[..., web2md.Page]:
    def _make_page(
        slug: str = "word-list",
        *,
        section: str = "Reference",
        title: str = "Word list",
        path: str | None = None,
    ) -> web2md.Page:
        if path is None:
            path = "/style" if slug == "style" else f"/style/{slug}"
        return web2md.Page(
            section=section,
            title=title,
            slug=slug,
            url=f"{web2md.BASE}{path}",
            path=path,
        )

    return _make_page


def build_nav_html(sections: int = 6, per_section: int = 12, extra_items: str = "") -> str:
    """Build a DevSite book nav big enough to clear `discover_pages`' guards.

    The leading item sits above the first heading, standing in for the
    book-picker tabs that `discover_pages` is meant to skip.
    """
    parts = [
        f'<div class="{web2md.NAV.lstrip(".")}"><ul>',
        '<li class="devsite-nav-item"><a href="/docs/guides">Guides</a></li>',
    ]
    for section in range(sections):
        parts.append(
            '<li class="devsite-nav-heading">'
            f'<span class="devsite-nav-text">Section {section}</span></li>'
        )
        for item in range(per_section):
            parts.append(
                '<li class="devsite-nav-item">'
                f'<a href="/style/page-{section}-{item}">'
                f'<span class="devsite-nav-text">Page {section}.{item}</span></a></li>'
            )
    parts.append(extra_items)
    parts.append("</ul></div>")
    return "".join(parts)


@pytest.fixture
def nav_html() -> Callable[..., str]:
    return build_nav_html
