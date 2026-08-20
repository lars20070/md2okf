"""Command-line interface for inspectokf."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

from inspectokf import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="inspectokf",
        description="Print a directory tree for an OKF wiki folder (via tree).",
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("okf"),
        help="wiki directory to show (default: okf)",
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
        help="descend at most N directory levels (default: unlimited)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse argv and run tree. Returns a process exit code."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    # Checked before the path and tree lookups so the message is the same
    # wherever it is run from, and `tree` need not be installed to get it.
    # tree rejects 0 itself; catching it here keeps the `inspectokf: ` prefix.
    level: int | None = args.level
    if level is not None and level < 1:
        print(f"inspectokf: --level must be 1 or greater (got {level})", file=sys.stderr)
        return 2

    path: Path = args.path
    if not path.is_dir():
        print(f"inspectokf: not a directory: {path}", file=sys.stderr)
        return 2

    tree_bin = shutil.which("tree")
    if tree_bin is None:
        print("inspectokf: 'tree' not found on PATH", file=sys.stderr)
        return 2

    command = [tree_bin]
    if level is not None:
        command += ["-L", str(level)]
    command.append(str(path))

    # Inherit stdio: tree writes directly to this process's stdout/stderr.
    completed = subprocess.run(command, check=False)  # noqa: S603
    return 0 if completed.returncode == 0 else 2


def entrypoint() -> None:
    """Console-script entry: exit with ``main``'s return code."""
    raise SystemExit(main())
