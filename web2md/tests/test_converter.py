"""`StyleGuideConverter` — the DevSite-specific HTML → Markdown rules."""

from __future__ import annotations

from collections.abc import Callable

import pytest

import web2md


@pytest.mark.parametrize(
    ("css_class", "kind"),
    sorted(web2md.ASIDE_KIND.items()),
)
def test_asides_become_github_callouts(
    to_md: Callable[..., str], css_class: str, kind: str
) -> None:
    result = to_md(f'<aside class="{css_class}"><p>Careful.</p></aside>')

    assert result == f"> [!{kind}]\n> Careful."


def test_multi_paragraph_aside_quotes_every_line(to_md: Callable[..., str]) -> None:
    result = to_md('<aside class="note"><p>Line one.</p><p>Line two.</p></aside>')

    assert result == "> [!NOTE]\n> Line one.\n> Line two."


def test_unknown_aside_class_warns_and_defaults_to_note(to_md: Callable[..., str]) -> None:
    warnings: list[str] = []

    result = to_md('<aside class="mystery"><p>Hm.</p></aside>', slug="tense", warnings=warnings)

    assert result == "> [!NOTE]\n> Hm."
    assert len(warnings) == 1
    assert "mystery" in warnings[0]
    assert "tense" in warnings[0]


def test_classless_aside_does_not_warn(to_md: Callable[..., str]) -> None:
    warnings: list[str] = []

    assert to_md("<aside><p>Hm.</p></aside>", warnings=warnings) == "> [!NOTE]\n> Hm."
    assert warnings == []


def test_empty_aside_produces_nothing(to_md: Callable[..., str]) -> None:
    assert to_md('<aside class="note"></aside>') == ""


def test_explicit_anchor_survives_conversion(to_md: Callable[..., str]) -> None:
    assert to_md('<a id="word-list--term"></a><p>text</p>').startswith(
        '<a id="word-list--term"></a>'
    )


def test_ordinary_links_still_convert(to_md: Callable[..., str]) -> None:
    assert to_md('<p><a href="#tense">Tense</a></p>') == "[Tense](#tense)"


def test_literal_fences_in_prose_are_escaped(to_md: Callable[..., str]) -> None:
    # Left alone, these would open a fence and swallow the following content.
    assert to_md("<p>use ``` fences</p>") == r"use \`\`\` fences"


def test_fences_inside_pre_are_not_escaped(to_md: Callable[..., str]) -> None:
    assert "\\`" not in to_md("<pre>```</pre>")


def test_definition_lists_become_bold_terms_with_indented_bodies(
    to_md: Callable[..., str],
) -> None:
    result = to_md("<dl><dt>term</dt><dd><p>First.</p><p>Second.</p></dd></dl>")

    assert result == "**term**\n    First.\n\n    Second."


def test_definition_term_whitespace_is_collapsed(to_md: Callable[..., str]) -> None:
    assert to_md("<dl><dt>two\n   words</dt></dl>") == "**two words**"


def test_empty_definition_parts_collapse(to_md: Callable[..., str]) -> None:
    assert to_md("<dl><dt></dt><dd></dd></dl>") == ""


def test_body_headings_shift_down_by_two(to_md: Callable[..., str]) -> None:
    # The document already uses # / ## / ### for title / section / page.
    result = to_md("<h2>Two</h2><p>x</p><h4>Four</h4>")

    assert result == "#### Two\n\nx\n\n###### Four"


def test_heading_depth_is_clamped_at_six(to_md: Callable[..., str]) -> None:
    assert to_md("<h5>Five</h5>") == "###### Five"
    assert to_md("<h6>Six</h6>") == "###### Six"


def test_empty_heading_produces_nothing(to_md: Callable[..., str]) -> None:
    assert to_md("<h2>   </h2>") == ""


def test_images_keep_alt_and_src(to_md: Callable[..., str]) -> None:
    assert to_md('<img src="https://x/i.png" alt="A chart">') == "![A chart](https://x/i.png)"


def test_image_without_src_degrades_to_its_alt_text(to_md: Callable[..., str]) -> None:
    assert to_md('<img alt="A chart">') == "A chart"


def test_pre_becomes_a_fenced_block_with_a_trailing_newline(to_md: Callable[..., str]) -> None:
    assert to_md("<pre>a = 1</pre>") == "```\na = 1\n```"


def test_pre_leading_newline_is_dropped(to_md: Callable[..., str]) -> None:
    assert to_md("<pre>\na = 1\n</pre>") == "```\na = 1\n```"


def test_bullets_use_dashes_and_asterisks_are_not_escaped(to_md: Callable[..., str]) -> None:
    result = to_md("<ul><li>one</li><li>two</li></ul>")

    assert result == "- one\n- two"
    assert to_md("<p>a * b _ c</p>") == "a * b _ c"
