"""Command-line interface for merkleokf."""

from __future__ import annotations

import argparse

from merkleokf import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="merkleokf",
        description="Print a Merkle hash tree for an OKF wiki folder.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Parse argv. Returns a process exit code.

    A scaffold: the parser is the whole contract for now. Hashing is added
    later, and should not need anything outside this project.
    """
    _build_parser().parse_args(argv)
    return 0


def entrypoint() -> None:
    """Console-script entry: exit with ``main``'s return code."""
    raise SystemExit(main())
