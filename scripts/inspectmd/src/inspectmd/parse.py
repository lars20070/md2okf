"""Parse ATX Markdown headings into a section map.

Only ATX headings (``#`` … ``######``) count. Setext underlines are ignored on
purpose: both producers in this repo emit ATX (``web2md`` sets
``heading_style = ATX``, and Marker output under ``md/`` is ATX throughout).
Headings inside fenced code blocks (backticks or tildes) are ignored. A leading
YAML frontmatter block is skipped so its ``---`` lines are not mistaken for
content. Text between the frontmatter and the first heading is section 0, the
preamble.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass

_ATX_RE = re.compile(r"^( {0,3})(#{1,6})(?:[ \t]+(.*))?$")
_CLOSING_HASHES_RE = re.compile(r"[ \t]+#*[ \t]*$")
_FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
_NON_ALNUM_RE = re.compile(r"[^a-z0-9]+")


@dataclass(frozen=True)
class Section:
    """One preamble or ATX-headed region of a Markdown document."""

    index: int
    """0 is the preamble, if any; otherwise the first section is 0."""

    level: int
    """1–6 for ATX headings; 0 for the preamble."""

    title: str
    slug: str
    """Kebab-case slug matching the AGENTS.md file-name convention."""

    start: int
    """1-based inclusive line number (the heading line itself, or first body)."""

    end: int
    """1-based inclusive line number."""

    words: int
    """Whitespace-split word count of the section's lines."""


def count_words(text: str) -> int:
    """Count whitespace-separated tokens in ``text``."""
    return len(text.split())


def slugify(title: str) -> str:
    """Reduce a heading title to a kebab-case slug.

    Lowercases ASCII letters, strips combining marks from non-ASCII characters,
    replaces any remaining non ``[a-z0-9]`` run with a single hyphen, and trims
    leading/trailing hyphens. Empty input yields an empty string.
    """
    normalized = unicodedata.normalize("NFKD", title)
    ascii_only = "".join(c for c in normalized if not unicodedata.combining(c))
    return _NON_ALNUM_RE.sub("-", ascii_only.casefold()).strip("-")


def split_frontmatter(text: str) -> tuple[int, str]:
    """Strip a leading YAML frontmatter block.

    Returns ``(last_frontmatter_line, remainder)``. Line numbers are 1-based:
    ``last_frontmatter_line`` is the closing ``---`` line, or ``0`` when there
    is no frontmatter. The remainder starts at the first content line.
    """
    if text.startswith("\ufeff"):
        text = text[1:]

    if not text.startswith("---"):
        return 0, text

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return 0, text

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return i + 1, "".join(lines[i + 1 :])
    return 0, text


def _fence_opener(line: str) -> tuple[str, int] | None:
    """Return ``(fence_char, length)`` if ``line`` opens a fenced code block."""
    match = _FENCE_RE.match(line.rstrip("\n"))
    if match is None:
        return None
    marker = match.group(2)
    return marker[0], len(marker)


def _fence_closer(line: str, char: str, length: int) -> bool:
    """True if ``line`` closes a fence opened with ``char`` × ``length``."""
    match = _FENCE_RE.match(line.rstrip("\n"))
    if match is None:
        return False
    marker = match.group(2)
    info = match.group(3)
    if marker[0] != char or len(marker) < length:
        return False
    # Closing fences may only carry trailing whitespace as "info".
    return info.strip() == ""


def _parse_atx(line: str) -> tuple[int, str] | None:
    """Return ``(level, title)`` for an ATX heading line, else ``None``."""
    match = _ATX_RE.match(line.rstrip("\n"))
    if match is None:
        return None
    hashes = match.group(2)
    rest = match.group(3)
    if rest is None:
        return len(hashes), ""
    title = _CLOSING_HASHES_RE.sub("", rest).strip()
    return len(hashes), title


def parse_sections(text: str, *, line_offset: int = 0) -> list[Section]:
    """Parse ``text`` into sections.

    ``line_offset`` is the number of lines already consumed before ``text``
    (typically the frontmatter). Section line numbers are 1-based in the full
    file: the first line of ``text`` is ``line_offset + 1``.
    """
    lines = text.splitlines(keepends=True)
    if not lines:
        return []

    headings: list[tuple[int, int, str]] = []
    fence: tuple[str, int] | None = None

    for i, line in enumerate(lines):
        if fence is not None:
            char, length = fence
            if _fence_closer(line, char, length):
                fence = None
            continue
        opener = _fence_opener(line)
        if opener is not None:
            fence = opener
            continue
        atx = _parse_atx(line)
        if atx is not None:
            headings.append((i, atx[0], atx[1]))

    sections: list[Section] = []

    def text_between(start_i: int, end_i: int) -> str:
        return "".join(lines[j] for j in range(start_i, end_i + 1))

    first_heading_i = headings[0][0] if headings else None

    if first_heading_i is None:
        body = "".join(lines)
        if body.strip():
            sections.append(
                Section(
                    index=0,
                    level=0,
                    title="(preamble)",
                    slug="preamble",
                    start=line_offset + 1,
                    end=line_offset + len(lines),
                    words=count_words(body),
                )
            )
        return sections

    if first_heading_i > 0:
        preamble_text = "".join(lines[:first_heading_i])
        if preamble_text.strip():
            sections.append(
                Section(
                    index=0,
                    level=0,
                    title="(preamble)",
                    slug="preamble",
                    start=line_offset + 1,
                    end=line_offset + first_heading_i,
                    words=count_words(preamble_text),
                )
            )

    for idx, (start_i, level, title) in enumerate(headings):
        end_i = headings[idx + 1][0] - 1 if idx + 1 < len(headings) else len(lines) - 1
        next_index = sections[-1].index + 1 if sections else 0
        display_title = title if title else "(empty)"
        display_slug = slugify(title) if title else "empty"
        sections.append(
            Section(
                index=next_index,
                level=level,
                title=display_title,
                slug=display_slug,
                start=line_offset + start_i + 1,
                end=line_offset + end_i + 1,
                words=count_words(text_between(start_i, end_i)),
            )
        )

    return sections


def inspect_markdown(text: str) -> list[Section]:
    """Split frontmatter and parse the remainder into sections."""
    offset, body = split_frontmatter(text)
    return parse_sections(body, line_offset=offset)
