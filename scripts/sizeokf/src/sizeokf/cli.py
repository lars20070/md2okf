"""Command-line interface for sizeokf."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from sizeokf import __version__
from sizeokf.sizes import Entry, collect


def format_table(entries: Sequence[Entry]) -> str:
    """Render entries as a fixed-width table, one row per file or directory."""
    if not entries:
        return "(no Markdown files)\n"

    headers = ("Words", "Files", "Path")
    rows = [(f"{e.words:,}", f"{e.files:,}", e.path) for e in entries]

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(cells: tuple[str, ...]) -> str:
        # Counts right-aligned so magnitudes line up; the path column trails.
        return "  ".join(
            cell.rjust(widths[i]) if i < 2 else cell.ljust(widths[i]) for i, cell in enumerate(cells)
        ).rstrip()

    lines = [fmt(headers), fmt(tuple("-" * w for w in widths))]
    lines.extend(fmt(row) for row in rows)
    return "\n".join(lines) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sizeokf",
        description="Report Markdown content word counts for an OKF wiki folder, excluding YAML frontmatter.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("okf"),
        help="wiki directory to measure (default: okf)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.add_argument(
        "-L",
        "--level",
        type=int,
        metavar="N",
        help="list entries at most N directory levels deep (default: unlimited; 0 = walk root only)",
    )
    parser.add_argument(
        "--nolog",
        action="store_true",
        help="ignore okf/log.md (omit from listing and totals)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse argv and print the size table. Returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Checked before the path so the message is the same wherever it is run from.
    level: int | None = args.level
    if level is not None and level < 0:
        print(f"sizeokf: --level must be 0 or greater (got {level})", file=sys.stderr)
        return 2

    path: Path = args.path
    if not path.is_dir():
        print(f"sizeokf: not a directory: {path}", file=sys.stderr)
        return 2

    entries, _ = collect(path, max_level=level, nolog=args.nolog)
    sys.stdout.write(format_table(entries))
    return 0


def entrypoint() -> None:
    """Console-script entry: exit with ``main``'s return code."""
    raise SystemExit(main())
