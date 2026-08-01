"""End-to-end `run()` over a synthetic site, served by a mock transport.

`run()` builds its own `httpx.Client`, so the client factory is swapped for one
that injects `httpx.MockTransport`. Nothing here touches the network or any path
outside `tmp_path`.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import httpx
import pytest

import web2md

SECTIONS = 6
PER_SECTION = 12

# What httpx.MockTransport expects: a request in, a canned response out.
Handler = Callable[[httpx.Request], httpx.Response]


def _page_html(section: int, item: int) -> str:
    return f"""<html><body>
      <div class="devsite-article-body">
        <section id="s{section}-{item}">
          <h2 id="s{section}-{item}">Heading {section}.{item}</h2>
          <p>Prose for page {section}.{item}.</p>
          <p>A link <a href="/style/page-0-0">home</a> and
             a fragment <a href="#s{section}-{item}">self</a>.</p>
          <devsite-code><pre>example {section}</pre></devsite-code>
          <aside class="note"><p>Remember this.</p></aside>
          <devsite-feedback>rate me</devsite-feedback>
        </section>
      </div>
    </body></html>"""


@pytest.fixture
def requested() -> list[str]:
    """Every path the mock transport was asked for, in order."""
    return []


@pytest.fixture
def site(nav_html: Callable[..., str], requested: list[str]) -> Handler:
    """Serve the synthetic book: the nav at /style, a body at every page path."""
    index = f"<html><body>{nav_html(sections=SECTIONS, per_section=PER_SECTION)}</body></html>"

    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        requested.append(path)
        if path == "/style":
            return httpx.Response(200, text=index)
        _, section, item = path.removeprefix("/style/").split("-")
        return httpx.Response(200, text=_page_html(int(section), int(item)))

    return handler


@pytest.fixture
def offline(monkeypatch: pytest.MonkeyPatch, site: Handler) -> None:
    """Point `run()`'s client at the synthetic site and relax the size guards."""
    real_client = httpx.Client

    def factory(**kwargs: Any) -> httpx.Client:
        return real_client(transport=httpx.MockTransport(site), **kwargs)

    monkeypatch.setattr(web2md.httpx, "Client", factory)
    monkeypatch.setattr(web2md, "SIZE_MIN", 0)
    monkeypatch.setattr(web2md, "SIZE_MAX", 10_000_000)
    monkeypatch.setattr(web2md, "WORD_LIST_TERM_EXPECTED", 0)
    monkeypatch.setattr(web2md, "WORD_LIST_TERM_TOLERANCE", 0)


def test_run_writes_a_complete_document(offline: None, tmp_path: Path) -> None:
    output = tmp_path / "out" / "guide.md"
    cache = tmp_path / "cache"

    web2md.run(refresh=False, cache_dir=cache, output=output)

    md = output.read_text(encoding="utf-8")
    assert md.startswith("---\ntype: Website\n")
    assert "# Google Developer Documentation Style Guide" in md
    assert "## Table of contents" in md
    for section in range(SECTIONS):
        assert f"\n## Section {section}\n" in md
        for item in range(PER_SECTION):
            assert f'<a id="page-{section}-{item}"></a>' in md
            assert f"Prose for page {section}.{item}." in md


def test_run_populates_the_cache_and_then_reuses_it(
    offline: None, tmp_path: Path, requested: list[str]
) -> None:
    output = tmp_path / "guide.md"
    cache = tmp_path / "cache"
    total = SECTIONS * PER_SECTION + 1  # every page, plus the nav index

    web2md.run(refresh=False, cache_dir=cache, output=output)

    cached = {p.name for p in cache.iterdir()}
    assert "_index.html" in cached
    assert len(cached) == total
    assert len(requested) == total

    # A second run must serve everything from disk and issue no further requests.
    requested.clear()
    web2md.run(refresh=False, cache_dir=cache, output=output)

    assert requested == []


def test_refresh_refetches_every_page(offline: None, tmp_path: Path, requested: list[str]) -> None:
    cache = tmp_path / "cache"
    output = tmp_path / "guide.md"
    web2md.run(refresh=False, cache_dir=cache, output=output)
    requested.clear()

    web2md.run(refresh=True, cache_dir=cache, output=output)

    assert len(requested) == SECTIONS * PER_SECTION + 1


def test_run_applies_the_cleaning_and_conversion_rules(offline: None, tmp_path: Path) -> None:
    output = tmp_path / "guide.md"

    web2md.run(refresh=False, cache_dir=tmp_path / "cache", output=output)
    md = output.read_text(encoding="utf-8")

    assert "rate me" not in md            # devsite-feedback dropped
    assert "devsite-code" not in md       # unwrapped to a fenced block
    assert "```\nexample 0\n```" in md
    assert "> [!NOTE]\n> Remember this." in md
    assert "#### Heading 0.0" in md       # h2 shifted down by two
    assert "[home](#page-0-0)" in md      # cross-page link became an anchor


def test_run_creates_missing_parent_directories(offline: None, tmp_path: Path) -> None:
    output = tmp_path / "deeply" / "nested" / "guide.md"

    web2md.run(refresh=False, cache_dir=tmp_path / "c", output=output)

    assert output.is_file()
