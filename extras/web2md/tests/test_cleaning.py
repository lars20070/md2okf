"""DOM cleaning: icon spans, devsite-code, noise removal, body extraction, ids."""

from __future__ import annotations

from collections.abc import Callable

import pytest
from bs4 import Tag

import web2md


def _body(inner: str) -> str:
    return f'<html><body><div class="devsite-article-body">{inner}</div></body></html>'


def test_icon_spans_inside_dt_become_text(frag: Callable[[str], Tag]) -> None:
    body = frag(
        '<dl><dt><span class="icon-dontuse"></span>whitelist</dt>'
        "<dd>Use allowlist.</dd></dl>"
    )
    web2md.replace_icon_spans(body)

    assert "Don't use: whitelist" in body.get_text(" ", strip=True)


def test_icon_spans_outside_dt_are_left_alone(frag: Callable[[str], Tag]) -> None:
    # The word-list legend uses the same empty spans next to prose that already
    # explains them; rewriting there would duplicate the explanation.
    body = frag('<p><span class="icon-dontuse"></span> means don\'t use this term.</p>')
    web2md.replace_icon_spans(body)

    assert "Don't use:" not in body.get_text(" ", strip=True)


@pytest.mark.parametrize(
    ("class_name", "label"),
    sorted(web2md.ICON_TEXT.items()),
)
def test_every_icon_mapping_is_applied(
    frag: Callable[[str], Tag], class_name: str, label: str
) -> None:
    body = frag(f'<dl><dt><span class="{class_name}"></span>term</dt></dl>')
    web2md.replace_icon_spans(body)

    assert body.dt.get_text(" ", strip=True).startswith(label)


def test_devsite_code_is_replaced_by_its_pre(frag: Callable[[str], Tag]) -> None:
    body = frag("<devsite-code><pre>print(1)</pre></devsite-code>")
    web2md.unwrap_devsite_code(body)

    assert body.find("devsite-code") is None
    assert body.pre is not None
    assert body.pre.get_text() == "print(1)"


def test_devsite_code_without_pre_is_unwrapped(frag: Callable[[str], Tag]) -> None:
    body = frag("<devsite-code>bare text</devsite-code>")
    web2md.unwrap_devsite_code(body)

    assert body.find("devsite-code") is None
    assert body.get_text() == "bare text"


@pytest.mark.parametrize("selector", web2md.DROP)
def test_every_drop_selector_removes_its_element(
    frag: Callable[[str], Tag], selector: str
) -> None:
    if selector.startswith("."):
        markup = f'<div class="{selector[1:]}">noise</div>'
    elif selector.startswith("["):
        markup = '<div aria-hidden="true">noise</div>'
    else:
        markup = f"<{selector}>noise</{selector}>"
    body = frag(f"<p>keep</p>{markup}")

    web2md.drop_noise(body, set())

    assert "noise" not in body.get_text()
    assert "keep" in body.get_text()


def test_drop_noise_records_the_class_values_it_removed(frag: Callable[[str], Tag]) -> None:
    body = frag('<div class="devsite-rating-container extra">noise</div>')
    dropped: set[str] = set()

    web2md.drop_noise(body, dropped)

    assert dropped == {"devsite-rating-container", "extra"}


def test_empty_permalink_anchors_are_dropped_but_image_links_survive(
    frag: Callable[[str], Tag],
) -> None:
    body = frag(
        '<a href="#section"></a>'
        '<a href="#other"><img src="/i.png" alt="pic"></a>'
        '<a href="/style/tense">Tense</a>'
    )
    web2md.drop_noise(body, set())

    hrefs = [a["href"] for a in body.find_all("a", href=True)]
    assert hrefs == ["#other", "/style/tense"]


def test_clean_body_runs_the_full_pipeline(make_page: Callable[..., web2md.Page]) -> None:
    html = _body(
        '<h2 id="intro">Intro</h2>'
        '<devsite-code><pre>code</pre></devsite-code>'
        '<devsite-feedback>rate me</devsite-feedback>'
        '<dl><dt><span class="icon-avoid"></span>term</dt></dl>'
    )
    dropped: set[str] = set()

    body = web2md.clean_body(html, make_page(), dropped)

    text = body.get_text(" ", strip=True)
    assert "rate me" not in text
    assert "Avoid: term" in text
    assert body.find("devsite-code") is None


def test_clean_body_without_article_body_is_fatal(make_page: Callable[..., web2md.Page]) -> None:
    with pytest.raises(SystemExit, match="missing article body"):
        web2md.clean_body("<html><body><p>nope</p></body></html>", make_page(), set())


@pytest.mark.parametrize("tag", ["h5", "h6"])
def test_clean_body_rejects_headings_deeper_than_h4(
    make_page: Callable[..., web2md.Page], tag: str
) -> None:
    with pytest.raises(SystemExit, match="heading deeper than h4"):
        web2md.clean_body(_body(f"<{tag}>too deep</{tag}>"), make_page(), set())


def test_clean_body_rejects_an_h1_that_would_rival_the_document_title(
    make_page: Callable[..., web2md.Page],
) -> None:
    with pytest.raises(SystemExit, match="unexpected <h1>"):
        web2md.clean_body(_body("<h1>Page title</h1>"), make_page(), set())


def test_clean_body_allows_the_key_takeaways_panel_title(
    make_page: Callable[..., web2md.Page],
) -> None:
    # DevSite gives that panel an h1; it is dropped as noise, not rejected.
    html = _body('<h1 id="key-takeaways-panel-title">Key takeaways</h1><h2>Real</h2>')

    body = web2md.clean_body(html, make_page(), set())

    assert "Real" in body.get_text()


@pytest.mark.parametrize("tag", ["h2", "h3", "h4"])
def test_clean_body_accepts_the_expected_heading_range(
    make_page: Callable[..., web2md.Page], tag: str
) -> None:
    body = web2md.clean_body(_body(f"<{tag}>Fine</{tag}>"), make_page(), set())

    assert body.find(tag) is not None


def test_collect_ids_namespaces_every_id(frag: Callable[[str], Tag]) -> None:
    body = frag('<section id="terms"><h2 id="terms">Terms</h2><dt id="a b">x</dt></section>')
    anchor_map: dict[tuple[str, str], str] = {}

    web2md.collect_ids(body, "word-list", anchor_map)

    assert anchor_map == {
        ("word-list", "terms"): "word-list--terms",
        ("word-list", "a b"): "word-list--au0020b",
    }


def test_collect_ids_skips_the_key_takeaways_panel(frag: Callable[[str], Tag]) -> None:
    body = frag('<h2 id="key-takeaways-panel-title">Key takeaways</h2>')
    anchor_map: dict[tuple[str, str], str] = {}

    web2md.collect_ids(body, "page", anchor_map)

    assert anchor_map == {}
