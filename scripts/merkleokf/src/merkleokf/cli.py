"""Command-line interface for merkleokf."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from merkleokf import __version__
from merkleokf.merkle import Entry, collect, hash_file, short


def escape_display_path(path: str) -> str:
    """Escape controls so a path stays one table cell (no newlines or ANSI)."""
    out: list[str] = []
    for ch in path:
        code = ord(ch)
        if ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif ch == "\r":
            out.append("\\r")
        elif ch == "\t":
            out.append("\\t")
        elif code < 0x20 or code == 0x7F:
            out.append(f"\\x{code:02x}")
        else:
            out.append(ch)
    return "".join(out)


def format_table(entries: Sequence[Entry]) -> str:
    """Render entries as a fixed-width table, one row per file or directory."""
    if not entries:
        return "(no Markdown files)\n"

    headers = ("Hash", "Files", "Path")
    rows = [(short(e.digest), f"{e.files:,}", escape_display_path(e.path)) for e in entries]

    widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def fmt(cells: tuple[str, ...]) -> str:
        # Only the count is right-aligned; hashes are fixed width already.
        return "  ".join(
            cell.rjust(widths[i]) if i == 1 else cell.ljust(widths[i]) for i, cell in enumerate(cells)
        ).rstrip()

    lines = [fmt(headers), fmt(tuple("-" * w for w in widths))]
    lines.extend(fmt(row) for row in rows)
    return "\n".join(lines) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="merkleokf",
        description="Print a Merkle hash tree for an OKF wiki folder, or the hash of one file.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("okf"),
        help="wiki directory or Markdown file to hash (default: okf)",
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
        help="list entries at most N directory levels deep (default: unlimited; ignored for a file)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse argv and print the Merkle tree. Returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Checked before the path so the message is the same wherever it is run from.
    level: int | None = args.level
    if level is not None and level < 1:
        print(f"merkleokf: --level must be 1 or greater (got {level})", file=sys.stderr)
        return 2

    path: Path = args.path

    if path.is_file():
        sys.stdout.write(f"{short(hash_file(path))}  {escape_display_path(path.name)}\n")
        return 0

    if not path.is_dir():
        print(f"merkleokf: not a file or directory: {path}", file=sys.stderr)
        return 2

    entries, _ = collect(path, max_level=level)
    sys.stdout.write(format_table(entries))
    return 0


def entrypoint() -> None:
    """Console-script entry: exit with ``main``'s return code."""
    raise SystemExit(main())
