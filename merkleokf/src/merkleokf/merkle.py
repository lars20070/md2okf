"""Build a Merkle hash tree over an OKF wiki.

Every ``*.md`` file is hashed over its **raw bytes**, and every directory over
its children's digests, so a change to any leaf propagates to exactly one chain
of parent directories and nowhere else. That is what makes change localisation
cheap: compare one root hash, and if it moved, descend into the single subtree
whose hash also moved.

Raw bytes, not frontmatter-stripped content: this is the integrity tool, so a
timestamp bump counts as a change. ``sizeokf`` is the one that measures prose.
"""

from __future__ import annotations

import hashlib
import sys
from dataclasses import dataclass
from pathlib import Path

DISPLAY_WIDTH = 12
"""Hex characters shown per digest. 48 bits — collision odds ~8e-11 at 217 files,
~2e-7 at 10,000. Full digests are always computed; only the display truncates."""


def hash_file(path: Path) -> bytes:
    """SHA-256 over a file's raw bytes.

    An unreadable file is reported on stderr and contributes an all-zero digest
    rather than aborting the walk — one bad page must not cost the rest.
    """
    try:
        return hashlib.sha256(path.read_bytes()).digest()
    except OSError as exc:
        print(f"merkleokf: skipping {path}: {exc}", file=sys.stderr)
        return bytes(32)


def short(digest: bytes) -> str:
    """Truncate a digest to its displayed hex prefix."""
    return digest.hex()[:DISPLAY_WIDTH]


@dataclass(frozen=True)
class Entry:
    """One listed file or directory, with its digest."""

    path: str
    """Display path, relative to the walked root. Directories end in ``/``."""

    is_dir: bool
    digest: bytes
    """Full SHA-256. For a directory, the Merkle digest over its children."""

    files: int
    """Markdown files covered. Always 1 for a file."""

    depth: int
    """1 for entries directly inside the root."""


def collect(root: Path, *, max_level: int | None = None) -> tuple[list[Entry], Entry]:
    """Walk ``root``, returning ``(listed_entries, root_entry)``.

    Directory digests always cover the full subtree regardless of ``max_level``;
    the level only decides which entries get listed. ``max_level=1`` lists the
    entries directly inside ``root``, matching ``inspectokf -L 1``.
    """
    entries: list[Entry] = []

    def walk(directory: Path, depth: int) -> tuple[bytes, int]:
        """Return ``(digest, files)`` for ``directory``, recording listed entries."""
        # Sorted so the digest is reproducible across filesystems, which do not
        # agree on readdir order.
        children = sorted(directory.iterdir(), key=lambda p: p.name)
        acc = hashlib.sha256()
        files = 0

        for child in children:
            if child.name.startswith("."):
                continue
            # is_dir() follows symlinks; is_symlink() first keeps cycles out.
            if child.is_symlink():
                continue

            if child.is_dir():
                digest, child_files = walk(child, depth + 1)
                files += child_files
                # The type tag keeps a file and a directory of the same name
                # apart; the name keeps a pure rename from being invisible.
                acc.update(b"d" + child.name.encode("utf-8") + digest)
                listed = Entry(
                    path=f"{child.relative_to(root)}/",
                    is_dir=True,
                    digest=digest,
                    files=child_files,
                    depth=depth,
                )
            elif child.suffix == ".md":
                digest = hash_file(child)
                files += 1
                acc.update(b"f" + child.name.encode("utf-8") + digest)
                listed = Entry(
                    path=str(child.relative_to(root)),
                    is_dir=False,
                    digest=digest,
                    files=1,
                    depth=depth,
                )
            else:
                continue

            if max_level is None or depth <= max_level:
                entries.append(listed)

        return acc.digest(), files

    root_digest, root_files = walk(root, 1)
    root_entry = Entry(
        path=f"{root.name}/",
        is_dir=True,
        digest=root_digest,
        files=root_files,
        depth=0,
    )

    # Alphabetical, so two runs diff line by line — the whole point of hashing.
    entries.sort(key=lambda e: e.path)
    return entries, root_entry
