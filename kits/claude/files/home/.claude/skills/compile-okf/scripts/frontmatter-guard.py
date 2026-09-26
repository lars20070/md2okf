#!/usr/bin/env python3
"""Check the wiki conventions that the OKF spec floor deliberately leaves open.

`okfctl validate` enforces the floor: every concept node carries a non-empty
`type` (OKF v0.2 §11). Everything beyond that is a producer's choice, so the
conventions this wiki settled on -- a title, a description, tags, provenance,
and a well-formed update log -- need their own check. This is that check.

Usage: frontmatter-guard.py [bundle]
  bundle  wiki root to check (default: ., the workspace, which IS the wiki root)

Exit codes:
  0  clean
  1  findings (one per line on stdout)
  2  usage or runtime error (bad path, or SPEC.md could not be found)

SPEC.md is read to learn which okf_version the root index must declare, so the
check moves with the spec instead of hard-coding a number. It is looked up as
the sibling of the bundle directory, which is one rule that covers both layouts:
on the host the bundle is `./okf` and the spec is `./SPEC.md`; in the sandbox the
workspace IS the bundle and the spec is the read-only `../SPEC.md` mount. Set
SPEC_MD to override.

Deliberately dependency-free: the sandbox installs a bare python3, so PyYAML is
not available and the frontmatter is parsed directly. The parser understands the
small YAML subset this wiki uses and reports anything it cannot read, rather than
passing it silently.
"""

from __future__ import annotations

import itertools
import os
import re
import sys
from pathlib import Path

RESERVED = {"index.md", "log.md"}

# §5: "Every timestamp-valued key in OKF is an ISO 8601 datetime with an explicit
# UTC offset". A bare date is what the okfctl migrate bug produces, so rejecting
# it here is load-bearing, not pedantry.
ISO_UTC = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)

# §7 actor convention: <producer>/<version>, human:<id>, or process:<id>.
ACTOR = re.compile(r"^([^\s:/]+/[^\s:/]+|human:[^\s]+|process:[^\s]+)$")

# The spec states its own revision as, e.g., "**Version 0.2**".
SPEC_VERSION = re.compile(r"^\*\*Version\s+(\d+\.\d+)\*\*\s*$", re.MULTILINE)

DATE_HEADING = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", re.MULTILINE)


def strip_quotes(value: str) -> str:
    """Unwrap a quoted scalar, honouring the \\" escape the wiki's titles use."""
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        inner = value[1:-1]
        return inner.replace('\\"', '"') if value[0] == '"' else inner
    return value


def split_flow(body: str) -> list[str]:
    """Split a flow collection's body on commas that are not inside quotes."""
    items, current, quote = [], [], ""
    for char in body:
        if quote:
            if char == quote:
                quote = ""
            current.append(char)
        elif char in "\"'":
            quote = char
            current.append(char)
        elif char == ",":
            items.append("".join(current))
            current = []
        else:
            current.append(char)
    items.append("".join(current))
    return [item for item in (i.strip() for i in items) if item]


def parse_scalar(value: str) -> object:
    """Parse one YAML value: a flow sequence, a flow mapping, or a scalar."""
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        return [strip_quotes(item) for item in split_flow(value[1:-1])]
    if value.startswith("{") and value.endswith("}"):
        mapping = {}
        for item in split_flow(value[1:-1]):
            key, sep, val = item.partition(":")
            if sep:
                mapping[key.strip()] = strip_quotes(val)
        return mapping
    return strip_quotes(value)


def parse_frontmatter(text: str) -> dict | None:
    """Return the frontmatter block as a dict, or None when there is no block.

    Handles the shapes this wiki uses: `key: value`, flow sequences and mappings,
    a one-level block mapping (`generated:` with indented `by:`/`at:`), and a
    block sequence of plain strings. A value is always split on the FIRST colon,
    so a URL or a timestamp keeps its colons.
    """
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[4 : end + 1]

    data: dict[str, object] = {}
    key: str | None = None
    for raw in block.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw[0] not in " \t-":
            name, sep, value = raw.partition(":")
            if not sep:
                continue
            key = name.strip()
            data[key] = parse_scalar(value) if value.strip() else {}
        elif key is not None:
            item = raw.strip()
            if item.startswith("- "):
                existing = data.get(key)
                if not isinstance(existing, list):
                    existing = []
                    data[key] = existing
                existing.append(strip_quotes(item[2:]))
            else:
                name, sep, value = item.partition(":")
                if sep and isinstance(data.get(key), dict):
                    data[key][name.strip()] = strip_quotes(value)  # type: ignore[index]
    return data


def spec_version(bundle: Path) -> str:
    """The okf_version the root index must declare, read from SPEC.md."""
    override = os.environ.get("SPEC_MD")
    spec = Path(override) if override else bundle.resolve().parent / "SPEC.md"
    if not spec.is_file():
        sys.exit(
            f"Error: SPEC.md not found at {spec}. It is looked up as the sibling "
            "of the bundle; set SPEC_MD to override."
        )
    match = SPEC_VERSION.search(spec.read_text(encoding="utf-8"))
    if not match:
        sys.exit(f"Error: no '**Version X.Y**' line in {spec}.")
    return match.group(1)


def check_node(path: Path, rel: str, findings: list[str]) -> None:
    """Check one concept node's frontmatter."""
    data = parse_frontmatter(path.read_text(encoding="utf-8"))
    if data is None:
        findings.append(f"frontmatter: {rel} has no parseable YAML frontmatter block")
        return

    for field in ("title", "description"):
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            findings.append(f"{field}: {rel} has no non-empty {field}")

    tags = data.get("tags")
    if not isinstance(tags, list) or not tags:
        findings.append(f"tags: {rel} has no tags list (a non-empty YAML list)")
    elif not all(isinstance(tag, str) and tag.strip() for tag in tags):
        findings.append(f"tags: {rel} has a tags list with a non-string entry")

    check_provenance(rel, data, findings)


def check_provenance(rel: str, data: dict, findings: list[str]) -> None:
    """Check §5.2 `generated: { by, at }`.

    The wiki was migrated to v0.2, so the legacy v0.1 `timestamp` key is a
    finding rather than an accepted fallback: §13.1 lets a *consumer* fall back
    to it, but a producer writing new v0.2 pages has no reason to emit one, and
    silently accepting it would let the corpus drift back.
    """
    generated = data.get("generated")
    if isinstance(generated, dict) and generated:
        by = str(generated.get("by", "")).strip()
        at = str(generated.get("at", "")).strip()
        if not ACTOR.match(by):
            findings.append(
                f"generated.by: {rel} has {by!r}, not a §7 actor "
                "(<producer>/<version>, human:<id>, or process:<id>)"
            )
        if not ISO_UTC.match(at):
            findings.append(
                f"generated.at: {rel} has {at!r}, not an ISO 8601 datetime with "
                "an explicit UTC offset (§5)"
            )
        return

    if data.get("timestamp"):
        findings.append(
            f"generated: {rel} carries a legacy v0.1 `timestamp`; v0.2 §13.1 "
            "supersedes it with `generated: { by, at }` (§5.2)"
        )
        return

    findings.append(
        f"generated: {rel} records no provenance (§5.2 `generated: {{ by, at }}`)"
    )


def check_root_index(bundle: Path, findings: list[str]) -> None:
    """§12: the bundle-root index declares okf_version, and nothing else."""
    index = bundle / "index.md"
    if not index.is_file():
        findings.append("index: the bundle root has no index.md")
        return
    data = parse_frontmatter(index.read_text(encoding="utf-8"))
    if data is None:
        findings.append(
            "okf_version: index.md carries no frontmatter block; the bundle-root "
            "index declares the spec version (§12)"
        )
        return
    want = spec_version(bundle)
    got = str(data.get("okf_version", "")).strip()
    if got != want:
        findings.append(
            f"okf_version: index.md declares {got!r} but SPEC.md is version {want!r}"
        )
    extra = sorted(key for key in data if key != "okf_version")
    if extra:
        findings.append(
            "okf_version: index.md frontmatter may contain only okf_version (§12); "
            f"found {', '.join(extra)}"
        )


def check_log(bundle: Path, findings: list[str]) -> None:
    """§9: log.md exists, and its date headings are ISO 8601, newest first."""
    log = bundle / "log.md"
    if not log.is_file():
        findings.append("log: the bundle root has no log.md (§9)")
        return
    dates = DATE_HEADING.findall(log.read_text(encoding="utf-8"))
    if not dates:
        findings.append("log: log.md has no '## YYYY-MM-DD' date headings (§9)")
        return
    for earlier, later in itertools.pairwise(dates):
        if earlier < later:
            findings.append(
                f"log: log.md heading {later} follows {earlier}; dates run "
                "newest first (§9)"
            )


def main(argv: list[str]) -> int:
    bundle = Path(argv[1] if len(argv) > 1 else ".")
    if not bundle.is_dir():
        sys.exit(f"Error: wiki bundle not found: {bundle}")

    findings: list[str] = []
    for path in sorted(bundle.rglob("*.md")):
        if path.name in RESERVED:
            continue
        check_node(path, str(path.relative_to(bundle)), findings)
    check_root_index(bundle, findings)
    check_log(bundle, findings)

    if not findings:
        print("OK: frontmatter, provenance and log conventions hold")
        return 0
    for finding in findings:
        print(finding)
    print(f"{len(findings)} guard finding(s)")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except SystemExit as exc:
        # sys.exit(str) prints the message and exits 1; this guard's contract
        # reserves 1 for findings and 2 for "could not run", so remap.
        if isinstance(exc.code, str):
            print(exc.code, file=sys.stderr)
            sys.exit(2)
        raise
