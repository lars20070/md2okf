"""Measure Markdown content size, excluding YAML frontmatter.

Only ``*.md`` files count. A file's size is the number of characters after its
leading frontmatter block is removed — characters, not bytes, so the figure is
comparable across pages regardless of how much non-ASCII text they carry. A
directory's size is the sum over every Markdown file beneath it, recursively.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path


def strip_frontmatter(text: str) -> str:
    """Return ``text`` without its leading YAML frontmatter block.

    The block must open on the very first line with exactly ``---`` and close on
    a later line that is also exactly ``---``; the body is everything after the
    closing line, so a blank line following it still counts. Text with no such
    block — including an *unterminated* one — is returned unchanged, which is
    the same rule ``inspectmd`` applies when mapping headings.
    """
    if text.startswith("﻿"):
        text = text[1:]

    if not text.startswith("---"):
        return text

    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return text

    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "".join(lines[i + 1 :])
    return text


@dataclass(frozen=True)
class Entry:
    """One listed file or directory, with its content size."""

    path: str
    """Display path, relative to the walked root. Directories end in ``/``."""

    is_dir: bool
    chars: int
    """Characters of Markdown content, frontmatter excluded. Recursive for directories."""

    files: int
    """Number of Markdown files counted. Always 1 for a file."""

    depth: int
    """1 for entries directly inside the root."""


def _measure_file(path: Path) -> int:
    """Characters of content in one Markdown file, frontmatter excluded.

    A file that cannot be read is reported on stderr and counted as zero rather
    than aborting the walk — one unreadable page must not cost the rest.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"sizeokf: skipping {path}: {exc}", file=sys.stderr)
        return 0
    return len(strip_frontmatter(text))


def collect(root: Path, *, max_level: int | None = None) -> tuple[list[Entry], Entry]:
    """Walk ``root``, returning ``(listed_entries, root_total)``.

    Every directory total is recursive regardless of ``max_level``; the level
    only decides which entries get listed. ``max_level=1`` lists the entries
    directly inside ``root``, matching ``inspectokf -L 1``.
    """
    entries: list[Entry] = []

    def walk(directory: Path, depth: int) -> tuple[int, int]:
        """Return ``(chars, files)`` for ``directory``, recording listed entries."""
        chars = files = 0
        for child in sorted(directory.iterdir(), key=lambda p: p.name):
            if child.is_dir():
                child_chars, child_files = walk(child, depth + 1)
                chars += child_chars
                files += child_files
                if max_level is None or depth <= max_level:
                    entries.append(
                        Entry(
                            path=f"{child.relative_to(root)}/",
                            is_dir=True,
                            chars=child_chars,
                            files=child_files,
                            depth=depth,
                        )
                    )
            elif child.suffix == ".md":
                child_chars = _measure_file(child)
                chars += child_chars
                files += 1
                if max_level is None or depth <= max_level:
                    entries.append(
                        Entry(
                            path=str(child.relative_to(root)),
                            is_dir=False,
                            chars=child_chars,
                            files=1,
                            depth=depth,
                        )
                    )
        return chars, files

    total_chars, total_files = walk(root, 1)
    total = Entry(path=f"{root.name}/", is_dir=True, chars=total_chars, files=total_files, depth=0)

    # Largest first; ties broken by path so repeated runs are byte-identical.
    entries.sort(key=lambda e: (-e.chars, e.path))
    return entries, total
