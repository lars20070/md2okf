#!/usr/bin/env python3
"""Sync frontmatter descriptions into the matching `index.md` entries.

Per `SPEC.md` §6 an index entry repeats the description of the concept it links
to. The frontmatter `description` (§4.1) is the ground truth, so this script
rewrites the text after ` — ` on every index entry pointing at a concept file.

Descriptions only: no entry is added, removed or reordered, headings and prose
stay untouched, and directory entries (trailing `/`) are left alone. Anything
that cannot be synced is reported on stderr, not fixed.

    python3 scripts/sync-descriptions.py [PATH] [--check]
"""

import argparse
import os
import re
import sys
from pathlib import Path

import yaml

SEPARATOR = " — "
RESERVED = {"index.md", "log.md"}

# An index entry: bullet, [title], (target), then whatever description follows.
# Titles may contain parentheses, targets may not, so the split is unambiguous.
ENTRY_RE = re.compile(
    r"^(?P<prefix>\s*[*-] \[(?P<title>[^]]*)\]\((?P<target>[^)]*)\))(?P<rest>.*)$"
)
URL_SCHEME_RE = re.compile(r"^[a-z][a-z0-9+.-]*:", re.IGNORECASE)


# ── frontmatter ─────────────────────────────────────────────────────────

def read_description(path: Path):
    """Return `(description, error)` for a concept file; exactly one is None."""
    try:
        lines = path.read_text(encoding="utf-8").split("\n")
    except (OSError, UnicodeDecodeError) as exc:
        return None, f"unreadable ({exc})"

    if not lines or lines[0].strip() != "---":
        return None, "no frontmatter"
    try:
        end = lines.index("---", 1)
    except ValueError:
        return None, "unterminated frontmatter"

    try:
        front = yaml.safe_load("\n".join(lines[1:end]))
    except yaml.YAMLError:
        return None, "invalid YAML frontmatter"
    if not isinstance(front, dict) or "description" not in front:
        return None, "no description in frontmatter"

    description = front["description"]
    if description is None or isinstance(description, (dict, list)):
        return None, "description is not a scalar"
    # Collapse a folded or literal block scalar onto one line; otherwise verbatim.
    description = " ".join(str(description).split())
    if not description:
        return None, "description is empty"
    return description, None


# ── entries ─────────────────────────────────────────────────────────────

def is_concept_link(target: str) -> bool:
    """True for links this script owns: a relative or bundle-absolute `.md` page."""
    target = target.split("#", 1)[0].strip()
    if not target or target.endswith("/") or URL_SCHEME_RE.match(target):
        return False
    return target.endswith(".md") and os.path.basename(target) not in RESERVED


def resolve(target: str, index_path: Path, root: Path) -> Path:
    """Map a link target to a path; a leading `/` means the bundle root."""
    target = target.split("#", 1)[0].strip()
    base = root if target.startswith("/") else index_path.parent
    return Path(os.path.normpath(base / target.lstrip("/")))


def sync_index(index_path: Path, root: Path, stats: dict, warn) -> tuple[str, str]:
    """Return the original and the description-synced content of one index file."""
    original = index_path.read_text(encoding="utf-8")
    updated = []

    for lineno, line in enumerate(original.split("\n"), 1):
        match = ENTRY_RE.match(line)
        if not match:
            updated.append(line)
            continue

        target = match.group("target")
        if not is_concept_link(target):
            stats["skipped"] += 1
            updated.append(line)
            continue

        path = resolve(target, index_path, root)
        if not path.is_file():
            warn(f"{index_path}:{lineno}: link target not found: {target}")
            updated.append(line)
            continue

        description, error = read_description(path)
        if error is not None:
            warn(f"{index_path}:{lineno}: {error}: {target}")
            updated.append(line)
            continue

        entry = f"{match.group('prefix')}{SEPARATOR}{description}"
        stats["current" if entry == line else "stale"] += 1
        updated.append(entry)

    return original, "\n".join(updated)


# ── main ────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync frontmatter descriptions into index.md entries."
    )
    parser.add_argument(
        "path", nargs="?", default=Path("okf"), type=Path,
        help="bundle root (default: okf)",
    )
    parser.add_argument(
        "--check", action="store_true",
        help="write nothing; exit 1 if any entry is out of sync",
    )
    args = parser.parse_args()

    root = args.path
    if not root.is_dir():
        print(f"sync-descriptions: not a directory: {root}", file=sys.stderr)
        return 2

    stats = {"stale": 0, "current": 0, "skipped": 0, "warnings": 0, "files": 0}

    def warn(message: str) -> None:
        stats["warnings"] += 1
        print(f"sync-descriptions: {message}", file=sys.stderr)

    for index_path in sorted(root.rglob("index.md")):
        try:
            original, updated = sync_index(index_path, root, stats, warn)
            if updated != original:
                stats["files"] += 1
                if not args.check:
                    index_path.write_text(updated, encoding="utf-8", newline="\n")
        except (OSError, UnicodeDecodeError) as exc:
            print(f"sync-descriptions: {index_path}: {exc}", file=sys.stderr)
            return 2

    verb = "out of sync" if args.check else "synced"
    print(
        f"sync-descriptions: {stats['stale']} {verb} in {stats['files']} files, "
        f"{stats['current']} already current, "
        f"{stats['skipped']} skipped (directory and non-concept entries), "
        f"{stats['warnings']} warnings"
    )
    return 1 if args.check and stats["stale"] else 0


if __name__ == "__main__":
    sys.exit(main())
