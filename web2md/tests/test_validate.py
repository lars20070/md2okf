"""`validate_output` — the OK path and every error branch.

The real thresholds expect a ~0.5 MB document with ~598 word-list terms, so each
test relaxes them via monkeypatch and then breaks exactly one rule.
"""

from __future__ import annotations

from collections.abc import Callable

import pytest

import web2md

# The discovered pages and their converted bodies, as validate_output takes them.
Book = tuple[list[web2md.Page], dict[str, str]]


@pytest.fixture(autouse=True)
def relaxed_thresholds(monkeypatch: pytest.MonkeyPatch) -> None:
    """Neutralise the size and word-list guards so fixtures can stay tiny."""
    monkeypatch.setattr(web2md, "SIZE_MIN", 0)
    monkeypatch.setattr(web2md, "SIZE_MAX", 10_000_000)
    monkeypatch.setattr(web2md, "WORD_LIST_TERM_EXPECTED", 0)
    monkeypatch.setattr(web2md, "WORD_LIST_TERM_TOLERANCE", 0)


@pytest.fixture
def book(make_page: Callable[..., web2md.Page]) -> Book:
    """A one-page book whose body carries a single resolvable anchor."""
    pages = [make_page("tense", section="Language", title="Tense")]
    bodies = {"tense": '<a id="tense--present"></a>\n\n**present**\n\nUse the present tense.'}
    return pages, bodies


def _md(body: str) -> str:
    return f"# Guide\n\n{body}\n"


def test_valid_output_passes(book: Book, capsys: pytest.CaptureFixture[str]) -> None:
    pages, bodies = book
    md = _md(f'<a id="tense"></a>\n\n{bodies["tense"]}\n\n[Present](#tense--present)')

    web2md.validate_output(md, pages, bodies)

    assert "Validation OK" in capsys.readouterr().err


def test_missing_page_body_is_reported(make_page: Callable[..., web2md.Page]) -> None:
    pages = [make_page("tense"), make_page("voice")]

    with pytest.raises(SystemExit):
        web2md.validate_output(_md("text"), pages, {"tense": "body"})


def test_broken_internal_link_is_reported(
    book: Book, capsys: pytest.CaptureFixture[str]
) -> None:
    pages, bodies = book
    md = _md('[Nowhere](#does-not-exist)')

    with pytest.raises(SystemExit):
        web2md.validate_output(md, pages, bodies)

    assert "broken internal links" in capsys.readouterr().err


def test_page_slug_anchors_count_as_valid_targets(book: Book) -> None:
    pages, bodies = book

    web2md.validate_output(_md("[Tense](#tense)"), pages, bodies)


def test_devsite_leftovers_outside_a_fence_are_reported(
    book: Book, capsys: pytest.CaptureFixture[str]
) -> None:
    pages, bodies = book

    with pytest.raises(SystemExit):
        web2md.validate_output(_md("a devsite-toc leaked through"), pages, bodies)

    assert "devsite-" in capsys.readouterr().err


def test_devsite_markup_inside_a_fence_is_allowed(book: Book) -> None:
    pages, bodies = book

    web2md.validate_output(_md("```\n<devsite-toc></devsite-toc>\n```"), pages, bodies)


def test_pandoc_definition_markers_are_reported(
    book: Book, capsys: pytest.CaptureFixture[str]
) -> None:
    pages, bodies = book

    with pytest.raises(SystemExit):
        web2md.validate_output(_md(":   a definition body"), pages, bodies)

    assert "Pandoc-style definition list markers" in capsys.readouterr().err


def test_headings_deeper_than_h6_are_reported(
    book: Book, capsys: pytest.CaptureFixture[str]
) -> None:
    pages, bodies = book

    with pytest.raises(SystemExit):
        web2md.validate_output(_md("####### Seven"), pages, bodies)

    assert "deeper than h6" in capsys.readouterr().err


@pytest.mark.parametrize(("low", "high"), [(10_000_000, 20_000_000), (0, 5)])
def test_output_size_outside_the_band_is_reported(
    book: Book, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str],
    low: int, high: int,
) -> None:
    pages, bodies = book
    monkeypatch.setattr(web2md, "SIZE_MIN", low)
    monkeypatch.setattr(web2md, "SIZE_MAX", high)

    with pytest.raises(SystemExit):
        web2md.validate_output(_md("text"), pages, bodies)

    assert "outside" in capsys.readouterr().err


def test_word_list_term_count_is_checked(
    make_page: Callable[..., web2md.Page],
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    monkeypatch.setattr(web2md, "WORD_LIST_TERM_EXPECTED", 100)
    monkeypatch.setattr(web2md, "WORD_LIST_TERM_TOLERANCE", 5)
    pages = [make_page("word-list")]
    bodies = {"word-list": '<a id="word-list--a"></a>\n\n**a**'}

    with pytest.raises(SystemExit):
        web2md.validate_output(_md(bodies["word-list"]), pages, bodies)

    assert "word-list term count 1 outside 95–105" in capsys.readouterr().err


def test_word_list_terms_within_tolerance_pass(
    make_page: Callable[..., web2md.Page], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(web2md, "WORD_LIST_TERM_EXPECTED", 3)
    monkeypatch.setattr(web2md, "WORD_LIST_TERM_TOLERANCE", 1)
    pages = [make_page("word-list")]
    body = "\n\n".join(f'<a id="word-list--{n}"></a>\n\n**{n}**' for n in "abc")
    bodies = {"word-list": body}

    web2md.validate_output(_md(body), pages, bodies)
