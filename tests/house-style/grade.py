#!/usr/bin/env python3
"""Grade the OKF consumption test.

Reads one agent transcript per case and applies three mechanical assertions.
There is no model in the loop here: every check is a string or filesystem
operation, so a run is reproducible and a failure is inspectable.

    applied   every expect_present appears, no expect_absent appears, and at
              least one expect_any appears when that list is non-empty
    cited     some changes[].citation resolves to a file inside the wiki
    grounded  one of those resolved pages actually contains the case's
              grounding text

`grounded` is the one that matters most. Without it an agent could produce the
right edit from memory, attach a plausible-looking path, and score full marks
without ever opening the wiki.

Usage: grade.py <wiki-dir> <cases.json> <transcripts-dir>
Exit:  0 all passed, 1 one or more failed, 2 could not run.
"""

import json
import re
import sys
from pathlib import Path

FENCE = re.compile(r"```json\s*(.*?)\s*```", re.DOTALL)


def extract_payload(text):
    """Return the last fenced json block as a dict, or None."""
    blocks = FENCE.findall(text)
    if not blocks:
        return None
    try:
        payload = json.loads(blocks[-1])
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def resolve(wiki, citation):
    """Map a bundle-absolute citation to a file on disk, or None."""
    if not isinstance(citation, str) or not citation.strip():
        return None
    rel = citation.strip().lstrip("/")
    # Tolerate an okf/ prefix even though the skill asks for bundle-absolute.
    if rel.startswith(f"{wiki.name}/"):
        rel = rel[len(wiki.name) + 1:]
    path = wiki / rel
    return path if path.is_file() else None


def grade(case, text, wiki):
    """Return (passed, detail) for one case."""
    payload = extract_payload(text)
    if payload is None:
        return False, "no parseable json block in the reply"

    rewrite = payload.get("rewrite")
    if not isinstance(rewrite, str) or not rewrite.strip():
        return False, "json block has no 'rewrite' string"
    hay = rewrite.lower()

    missing = [s for s in case["expect_present"] if s.lower() not in hay]
    present = [s for s in case["expect_absent"] if s.lower() in hay]
    any_opts = case.get("expect_any") or []
    any_ok = (not any_opts) or any(s.lower() in hay for s in any_opts)

    if missing:
        return False, f"applied: missing {missing}"
    if present:
        return False, f"applied: still contains {present}"
    if not any_ok:
        return False, f"applied: none of {any_opts} present"

    changes = payload.get("changes")
    if not isinstance(changes, list) or not changes:
        return False, "cited: no changes reported"

    resolved = []
    for ch in changes:
        if isinstance(ch, dict):
            hit = resolve(wiki, ch.get("citation", ""))
            if hit is not None:
                resolved.append(hit)
    if not resolved:
        cited = [c.get("citation") for c in changes if isinstance(c, dict)]
        return False, f"cited: no citation resolves to a page ({cited})"

    # A ruling may appear on more than one page — the book rules on verbing
    # nouns in both chapter 1 and chapter 9, for instance — so `grounding`
    # accepts a list and any one of them grounds the citation.
    grounding = case["grounding"]
    needles = [grounding] if isinstance(grounding, str) else list(grounding)
    for path in resolved:
        body = path.read_text(errors="replace").lower()
        for needle in needles:
            if needle.lower() in body:
                return True, f"cited {path.name}"

    names = ", ".join(p.name for p in resolved)
    return False, f"grounded: no cited page contains any of {needles} (cited {names})"


def main():
    if len(sys.argv) != 4:
        print(__doc__.strip().splitlines()[-2], file=sys.stderr)
        return 2

    wiki, cases_file, outdir = (Path(a) for a in sys.argv[1:4])
    if not wiki.is_dir():
        print(f"error: wiki directory not found: {wiki}", file=sys.stderr)
        return 2
    if not cases_file.is_file():
        print(f"error: cases file not found: {cases_file}", file=sys.stderr)
        return 2

    cases = json.loads(cases_file.read_text())["cases"]
    if not cases:
        print("error: no cases defined", file=sys.stderr)
        return 2

    width = max(len(c["id"]) for c in cases)
    results = []
    for case in cases:
        transcript = outdir / f"{case['id']}.txt"
        if not transcript.is_file():
            passed, detail = False, "no transcript (the run did not produce output)"
        else:
            passed, detail = grade(case, transcript.read_text(errors="replace"), wiki)
        results.append(passed)
        mark = "PASS" if passed else "FAIL"
        print(f"  {mark}  {case['id']:<{width}}  {detail}")

    ok = sum(results)
    print(f"\n{ok}/{len(results)} cases passed")
    return 0 if ok == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
