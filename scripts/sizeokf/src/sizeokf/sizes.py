"""Measure Markdown content size, excluding YAML frontmatter.

Only ``*.md`` files count. A file's size is the number of whitespace-split words
after its leading frontmatter block is removed. A directory's size is the sum
over every Markdown file beneath it, recursively.
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


def count_words(text: str) -> int:
    """Count whitespace-separated tokens in ``text``."""
    return len(text.split())


@dataclass(frozen=True)
class Entry:
    """One listed file or directory, with its content size."""

    path: str
    """Display path, rooted at the walk target's name. Directories end in ``/``."""

    is_dir: bool
    words: int
    """Whitespace-split words of Markdown content, frontmatter excluded. Recursive for directories."""

    files: int
    """Number of Markdown files counted. Always 1 for a file."""

    depth: int
    """1 for entries directly inside the root; 0 for the root itself."""


def _measure_file(path: Path) -> int:
    """Words of content in one Markdown file, frontmatter excluded.

    A file that cannot be read is reported on stderr and counted as zero rather
    than aborting the walk — one unreadable page must not cost the rest.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"sizeokf: skipping {path}: {exc}", file=sys.stderr)
        return 0
    return count_words(strip_frontmatter(text))


def collect(root: Path, *, max_level: int | None = None) -> tuple[list[Entry], Entry]:
    """Walk ``root``, returning ``(listed_entries, root_total)``.

    ``listed_entries`` always includes ``root_total``. Every directory total is
    recursive regardless of ``max_level``; the level only decides which non-root
    entries get listed. ``max_level=0`` lists only the walk root; ``max_level=1``
    lists the entries directly inside ``root``, matching ``inspectokf -L 1``.
    """
    entries: list[Entry] = []
    prefix = f"{root.name}/"

    def walk(directory: Path, depth: int) -> tuple[int, int]:
        """Return ``(words, files)`` for ``directory``, recording listed entries."""
        words = files = 0
        try:
            children = sorted(directory.iterdir(), key=lambda p: p.name)
        except OSError as exc:
            # Same skip policy as an unreadable file: warn and contribute zero.
            print(f"sizeokf: skipping {directory}: {exc}", file=sys.stderr)
            return 0, 0

        for child in children:
            try:
                # is_dir() follows symlinks; skip them so cycles and links
                # outside root cannot be scanned.
                if child.is_symlink():
                    continue
                is_directory = child.is_dir()
            except OSError as exc:
                print(f"sizeokf: skipping {child}: {exc}", file=sys.stderr)
                continue

            if is_directory:
                child_words, child_files = walk(child, depth + 1)
                words += child_words
                files += child_files
                if max_level is None or depth <= max_level:
                    entries.append(
                        Entry(
                            path=f"{prefix}{child.relative_to(root)}/",
                            is_dir=True,
                            words=child_words,
                            files=child_files,
                            depth=depth,
                        )
                    )
            elif child.suffix == ".md":
                child_words = _measure_file(child)
                words += child_words
                files += 1
                if max_level is None or depth <= max_level:
                    entries.append(
                        Entry(
                            path=f"{prefix}{child.relative_to(root)}",
                            is_dir=False,
                            words=child_words,
                            files=1,
                            depth=depth,
                        )
                    )
        return words, files

    total_words, total_files = walk(root, 1)
    total = Entry(path=prefix, is_dir=True, words=total_words, files=total_files, depth=0)
    entries.append(total)

    # Largest first; ties broken by path so repeated runs are byte-identical.
    entries.sort(key=lambda e: (-e.words, e.path))
    return entries, total
