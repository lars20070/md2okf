"""Command-line interface for inspectmd."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from inspectmd import __version__
from inspectmd.parse import Section, inspect_markdown


def format_table(sections: Sequence[Section], *, max_level: int | None = None) -> str:
    """Render sections as a fixed-width table.

    When ``max_level`` is set, only the preamble (level 0) and headings with
    ``level <= max_level`` are shown.
    """
    visible = [
        s
        for s in sections
        if max_level is None or s.level == 0 or s.level <= max_level
    ]
    if not visible:
        return "(no sections at this depth)\n"

    headers = ("Index", "Level", "Lines", "Characters", "Slug", "Title")
    rows: list[tuple[str, str, str, str, str, str]] = []
    for s in visible:
        rows.append(
            (
                str(s.index),
                str(s.level),
                f"{s.start}-{s.end}",
                str(s.chars),
                s.slug,
                s.title,
            )
        )

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(row: tuple[str, ...]) -> str:
        return "  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row))

    lines = [fmt(headers), fmt(tuple("-" * w for w in widths))]
    lines.extend(fmt(row) for row in rows)
    return "\n".join(lines) + "\n"


def format_section_range(section: Section) -> str:
    """One section as ``start:end`` plus size, for a ranged read."""
    return f"{section.start}:{section.end}  {section.chars} chars\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inspectmd",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Print a Markdown heading map with line ranges and sizes.",
        epilog="""\
Output columns (default table):
  Index       Section number in document order (0 = preamble when present).
              Pass this value to --section.
  Level       Heading depth: 0 for the preamble, 1 for #, 2 for ##, …, 6 for ######.
  Lines       1-based inclusive line range of the section (start-end).
  Characters  Character count of that range (including newlines).
  Slug        Kebab-case slug derived from the heading title (OKF file-name style).
  Title       Heading text as written (or "(preamble)" / "(empty)").

--section N prints only "start:end  N chars" for ranged reads.
""",
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Markdown file to inspect",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "--section",
        type=int,
        metavar="N",
        help="print only section N as start:end and size",
    )
    parser.add_argument(
        "-L",
        "--level",
        type=int,
        metavar="N",
        help="show only headings at this level or above (1=H1, …)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse argv and print the heading map. Returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    path: Path = args.file
    if not path.is_file():
        print(f"inspectmd: not a file: {path}", file=sys.stderr)
        return 2

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"inspectmd: {exc}", file=sys.stderr)
        return 2

    line_count = text.count("\n") + (0 if text.endswith("\n") or text == "" else 1)
    if text == "":
        line_count = 0
    sections = inspect_markdown(text)

    if args.section is not None:
        match = next((s for s in sections if s.index == args.section), None)
        if match is None:
            print(
                f"inspectmd: section {args.section} out of range "
                f"(0..{sections[-1].index if sections else 'none'})",
                file=sys.stderr,
            )
            return 2
        sys.stdout.write(format_section_range(match))
        return 0

    summary = (
        f"{path.name}: {line_count} lines, {len(text)} chars, {len(sections)} sections"
    )
    sys.stdout.write(summary + "\n")
    if not sections:
        sys.stdout.write("(no headings)\n")
        return 0

    sys.stdout.write(format_table(sections, max_level=args.level))
    return 0


def entrypoint() -> None:
    """Console-script entry: exit with ``main``'s return code."""
    raise SystemExit(main())
