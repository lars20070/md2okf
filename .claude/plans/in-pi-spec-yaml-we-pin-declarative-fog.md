# Resolve the 7 open CodeRabbit findings on PR #8

> **Note:** The filename is a stale auto-title — this plan does not change
> `pi/spec.yaml`. Scope is driver, skill, and test harness only.

## Context

PR #8 has 7 unresolved CodeRabbit review threads (4 others are already resolved).
They were written against `c1df593`; I verified each against the current head
`dbc99a6`. `SKILL.md` is byte-identical to the reviewed commit and
`scripts/compile-wiki.sh` changed by one line (the kit rename), so **all 7 still
apply**.

Two facts found while verifying reshape the work:

- **The stubbed-`sbx` tests the PR description claims do not exist** — never
  committed, on any branch. `make test` and CI run only `web2md/tests`. Nothing
  exercises the driver, so every driver fix is currently unverifiable.
- **`md/` can hold overlapping sources at two lengths** — e.g.
  `TheRestIsHistory.md` and `TheRestIsHistory-abridged.md` with identical section
  names. The working tree may currently have only the abridged file, but the
  "resume scans the whole wiki" finding is this repo's real configuration when
  both are present, not a hypothetical.

A broader review already exists at `.cursor/plans/pr-8-merge-blockers.md` (16
sections). This plan deliberately covers **only the 7 CodeRabbit items**; where
one maps onto a merge-blocker section it is noted, so the two stay reconcilable.

A follow-up plan review (2026-08-14) confirmed the validity table and design
decisions, and added the **gaps and refinements** woven into §1–§4 below and
summarised in [Review additions](#review-additions-2026-08-14).

## Validity assessment

| # | Finding | Verdict |
|---|---|---|
| A | `compile-wiki.sh:120` — failed invocations don't increment `pass` | **Valid.** `pass` advances only after a success; the failure path `continue`s. `MAX_PASSES` is documented as "most Pi runs" but the real bound is `MAX_PASSES × MAX_RETRIES` = 60 invocations. Cheap fix. |
| B | `compile-wiki.sh:115-129` — exit 0 on exhausted budget | **Valid and the most consequential.** Lines 115-118 print `INCOMPLETE` to stderr but set nothing; line 126 tests only `failed_documents`. `make wiki` reports success on known-incomplete output. |
| C | `compile-wiki.sh:67-77` — byte-count convergence too weak | **Valid, but CodeRabbit's stated mechanism is the weak one.** A split/rewrite landing on an identical *total* byte count is a coincidence. The real defect: a pass where the agent writes nothing gives `current == previous` and is declared **done** — which is precisely Pi issue [#7020](https://github.com/earendil-works/pi/issues/7020), the bug this PR exists to work around. A fingerprint alone does *not* fix that; only an explicit completion signal does. Also, `wiki_size()` spans every source plus `log.md`, so one document's convergence is measured on a global counter. |
| D | `SKILL.md:81-85` — resume detection scans the whole wiki | **Valid.** Prose says "for this document's area" but the command is `find okf -name '*.md'`. With the two `TheRestIsHistory` sources, a page from one can mark the other's section done. |
| E | `SKILL.md:87-94` — pages from failed passes are trusted | **Valid.** The driver preserves `okf/` after failure by design; the skill says "Trust what earlier runs left". `SKILL.md:369-384` has the agent write pages in **bounded chunks**, i.e. several tool calls, so a mid-write failure leaving a partial page is likely, not exotic. Silently drops content. |
| F | `SKILL.md:108-113` — fence-aware heading extraction | **Valid, low real-world risk, near-zero fix cost.** `/^```/` ignores `~~~`, fence length, and indentation. Podcast transcripts won't trigger it; `md/GoogleStyleGuide.md` — a *Markdown* style guide full of nested fence examples — plausibly will. |
| G | `SKILL.md:456-458` — gate 4 misses bare stale fragments | **Valid, and mis-rated by CodeRabbit as heavy.** The regex needs `.md` or `/` in the fragment, so it catches `](#highlights.md)` but not `](#highlights)` after `highlights` moved to another page. Per `SKILL.md:257-260` **every** inherited link starts in exactly that bare form, so the at-risk population is large. Resolving fragments against the page's own headings is ~15 lines. |

Nothing here is safe to ignore as minor. F is the weakest and is kept only
because it is nearly free.

## Design decisions (agreed)

1. **Provenance + explicit status** for C, D, E.
2. **Exit non-zero** when any document is abandoned *or* incomplete.
3. **Extract the gates to a committed script**, enforced by the driver.
4. **Focused fake-`sbx` test harness**, wired into `make test` and CI.

`SPEC.md:169` explicitly permits extension frontmatter keys ("Producers MAY
include any additional keys"), so a `source` field is legal OKF and will not trip
`okf-lint` — the configured rules in `okf/.okflintrc.json` are all
title/description/timestamp/tags/links/log/version.

### Alternatives considered

`.claude/plans/Research_RalphLoopPiAgent_20260810.md` proposes `pi --mode json`
plus an in-kit `mark-complete` tool returning `terminate: true`. That gives a
deterministic stop signal in the JSON stream but depends on Pi non-interactive
skill trust and `--mode json` behaviour. **This plan keeps a file-based status
record** — simpler, inspectable on disk, and enforceable by the host-side driver
without parsing Pi's event stream. Revisit JSON mode only if the agent reliably
ignores the status protocol.

## Review additions (2026-08-14)

Independent review confirmed the plan is implementable as written. These items
were missing or underspecified and are now part of the spec:

| Gap | Resolution (where) |
|---|---|
| Missing/malformed status on driver read | §1 — driver treats absent or bad JSON as incomplete |
| Source edit invalidates stale `complete: true` | §1 — `source_sha256` in status record |
| Agent may set `complete: true` too early | §1 — preconditions in skill; §3 — driver re-runs gates and overrides |
| Stall vs provider-retry share one counter | §1 — separate `MAX_STALLS` env var |
| Legacy pages without `source` frontmatter | §1 — never trust for resume |
| Overlapping sources, same subtree | §1 — one `root` per source; no shared subtree without manual coordination |
| `okf/log.md` skews fingerprint | §1 — exclude shared bookkeeping from fingerprint |
| Driver gate timing and scope | §3 — run on claimed completion, scoped to `root` |
| Test directory layout | §4 — `scripts/tests/` not repo-root `tests/` |
| `covered_through_line` unsound under depth-first compilation | §1 — advisory only; driver must not read it; dropped as a precondition |
| Precondition 2 unimplementable (okf-lint takes a bundle, not a subtree) | §1 — lint the bundle, filter the report by `root` |
| Status-file ownership / write race | §3 — driver is read-only on `okf/.status/` |
| Retries now consume the pass budget | §2 — documented in the script header; consider a higher default |

## Implementation order

Build in this sequence so each slice is independently testable:

1. **Test harness skeleton** — fake `sbx`, one red scenario (B: exit non-zero on
   incomplete). Gives a red/green loop for everything else.
2. **Exit contract (§2)** — attempts counter + `incomplete_documents`; cheap and
   independently valuable.
3. **`check-structure.sh` (§3)** — extract gates + unit tests; no agent behaviour
   required.
4. **Status protocol (§1)** — skill + AGENTS.md + driver fingerprint/stall logic;
   the load-bearing change.
5. **End-to-end verification** — `MAX_PASSES=2` run, `make lint-okf`.

## Implementation

### 1. Completion protocol — fixes C, D, E

**`pi/files/home/.pi/agent/AGENTS.md`** (OKF conventions) and
**`SKILL.md`**: add a required `source` frontmatter field naming the source
document each page was compiled from (workspace-relative path, e.g.
`md/TheRestIsHistory-abridged.md`).

**Status record** written by the skill, one per source, keyed by source basename
to avoid slug drift. Lives under `okf/.status/` (generated output, gitignored
with the rest of `okf/` except `.okflintrc.json`):

```json
// okf/.status/TheRestIsHistory-abridged.json
{
  "source": "md/TheRestIsHistory-abridged.md",
  "source_sha256": "abc123…",
  "root": "okf/the-rest-is-history-abridged",
  "complete": false,
  "covered_through_line": 4820,
  "updated": "2026-08-14"
}
```

- **`source_sha256`** — `sha256sum` of the source file at the time of the last
  status write. On each driver iteration, if the on-disk source hash differs,
  treat `complete` as false regardless of what the record says (merge-blockers
  §1: invalidate when the source changes).
- **`root`** — bundle-relative path to this source's wiki subtree (no trailing
  slash). One source, one root. Two sources that would share a subtree (full +
  abridged both under `okf/the-rest-is-history/`) must use **distinct roots**
  (e.g. `…-abridged`) so resume and fingerprint stay isolated. Deliberately out
  of scope: merging two sources into one shared subtree.
- **`covered_through_line`** — **advisory resume hint only. The driver MUST NOT
  read it, and it proves nothing.** The skill compiles depth-first, one branch at
  a time, so chapter 3 can be finished while chapter 2's subsections are not — a
  single high-water mark would falsely imply everything below it is covered.
  Completion is proven by `complete: true` **plus the driver's own gate run**,
  never by this field.

**Driver: missing or malformed status**

The driver reads the status record **after every successful `sbx exec`**. Treat
the document as **not complete** when:

- `okf/.status/<basename>.json` is absent (first pass, or agent never wrote it);
- the file is not valid JSON;
- required keys (`source`, `root`, `complete`) are missing;
- `source` in the record does not match the document being compiled;
- `source_sha256` does not match the current source file.

Any of the above → same as `complete: false` for stop/stall logic; increment
stall counter if the fingerprint also did not change.

**`scripts/compile-wiki.sh`**: replace `wiki_size()` with `fingerprint()` over
the `root` subtree from the status file:

- Include every `*.md` under `root` **except** `index.md` files if you want
  content-only progress — or include them; pick one and document it in the
  script header. Default: **all `*.md` under `root`**.
- **Exclude** `okf/log.md`, parent indexes outside `root`, and all of
  `okf/.status/` from the fingerprint (shared bookkeeping must not mask stall or
  fake progress).
- Compute: `sha256sum` per path, sorted, hashed again.

Stop condition:

- Agent claims `complete: true` **and** driver gate run passes (§3) → **done**;
- fingerprint changed → productive pass, reset stall counter, continue;
- fingerprint unchanged and not complete → **stalled**, not done. Count stalls
  against `MAX_STALLS` (default: same as `MAX_RETRIES`, overridable separately
  so three 502 retries and three Pi-#7020 no-ops are not conflated);
- stall threshold exceeded → stop, mark incomplete.

This is the load-bearing change: an unchanged wiki can no longer mean "finished".

**When the agent may set `complete: true`** (new skill subsection, tied to
"Before you finish"):

1. Every section of the source has a page attributed to this `source` under
   `root`.
2. `okf-lint` reports **no error whose path is under `root`**. Since okf-lint
   takes a whole bundle and a subtree is not a valid bundle, lint the bundle and
   filter the report by path — an unrelated source's legacy page must not
   deadlock this source's completion. (Whole-bundle conformance stays
   merge-blockers §11, out of scope here.)
3. All four structural gates are silent when run against `root` (§3).
4. The final message's coverage statement names every section as compiled.
   `covered_through_line` is written as a resume hint but is **not** a
   precondition — see the schema note above.

The agent writes/updates the status record as the **last step** before ending the
run, after gates and lint pass. Setting `complete: true` before that is a defect
the driver must not honour.

**`SKILL.md:81-95`**: scope resume discovery to the current source — resolve the
status record and `root` first, list only that subtree, and compare against pages
carrying this source's `source` field. Add:

- A page may be trusted only if it is attributed to this source **and** the
  status record marks its section covered; otherwise revalidate before skipping
  (E).
- **Pages without a `source` field** (legacy output from before this change):
  never trust for resume — treat as uncovered and revalidate or rewrite with
  attribution.

> Maps to merge-blockers §1, §2, §3.

### 2. Exit contract — fixes A and B

**`scripts/compile-wiki.sh`**:

- add an `attempts` counter incremented **before** every `sbx exec`, and bound
  the loop on it (`attempts <= max_passes`), keeping `failures` as the separate
  consecutive-failure counter (A). Correct the `MAX_PASSES` comment at lines
  10-13: it is now an upper bound on **invocations**, not successful passes.
  **Consequence to document:** retries now consume the budget, so a document that
  hits three transient failures gets three fewer productive passes than before.
  Say so in the script header and consider raising the default above 20.
- add an `incomplete_documents` counter, incremented on budget exhaustion,
  stall-out, gate failure after claimed completion, and missing/invalid status
  at loop end; final condition becomes
  `if failed_documents > 0 || incomplete_documents > 0 → summary + exit 1` (B).

> Maps to merge-blockers §5, §6.

### 3. Structural gates — fixes F and G

New **`pi/files/home/.pi/agent/skills/compile-wiki/scripts/check-structure.sh`**,
following the conventions of its sibling `lint-okf.sh` (`set -euo pipefail`,
`bundle` argument defaulting to `./okf`, optional second argument **`scope`**
(default: whole bundle), documented exit codes, `shellcheck` clean). When
`scope` is set (e.g. `okf/the-rest-is-history-abridged`), gates 1–4 run only
under that path. It carries the existing four gates plus the two fixes:

- **Gate 4 rewritten (G):** for each page, slugify its own headings, then flag any
  `](#fragment)` whose fragment is not among them. Keeps genuine in-page anchors,
  catches both `](#highlights)` and `](#highlights.md)`.
- **Heading extractor (F):** a fence-aware pass that tracks the opening fence
  character and length and closes only on a matching delimiter of at least that
  length, allowing up to three spaces of indentation. Handles ``` and `~~~`.
  `SKILL.md:108-113` points at the script instead of inlining awk.
- **Must exclude `okf/.status/`** from gate 1, or the new status directory
  registers as an empty directory. Gate 3 must not false-positive on `.status/`.

**Driver gate enforcement**

After every successful `sbx exec` where the status record has `complete: true`:

```bash
./pi/files/home/.pi/agent/skills/compile-wiki/scripts/check-structure.sh okf "$root"
```

- Exit 0 → accept completion, break the per-document loop.
- Non-silent / non-zero → **do not** accept completion: ignore the claim in
  memory, increment `incomplete_documents` or stall counter, continue or exit per
  stall/budget rules. The driver never trusts agent-claimed completion without its
  own gate run.

**The driver never writes to the status record.** The agent owns
`okf/.status/*.json`; a host process mutating it would race the next pass and
blur which side is authoritative. A rejected completion claim is dropped in the
driver's own state, not by editing the file.

On stall-out or budget exhaustion, run gates once as a **diagnostic** (stderr
only; outcome already incomplete).

`SKILL.md:430-459` keeps a prose description of what each gate checks and calls
the script; the agent runs it scoped to `root` before writing `complete: true`.

> Maps to merge-blockers §8, §9, §10 (partially — §10's missing-index and
> one-H1 checks are **not** in scope here; CodeRabbit did not raise them).

### 4. Test harness

New **`scripts/tests/compile-wiki_test.sh`** — a fake `sbx` placed on `PATH`
writing scripted output into a temporary workspace. No network, no Docker.
Colocated with the driver under `scripts/` rather than a repo-root `tests/`
directory (the only other tests today live in `web2md/tests/`).

Driver scenarios:

- transient failure retried, then success;
- persistent failure abandons the document, preserves `okf/`, exits 1;
- `MAX_PASSES` exhausted → non-zero (B);
- attempts counted across failures, not just successful passes (A);
- no-op pass with `complete != true` treated as stalled, not done (C);
- `complete: true` with passing gates stops the loop;
- `complete: true` with failing gates → not done, incomplete (driver override),
  and the status file is left byte-identical (driver never writes to it);
- missing status file after successful exec → stalled/incomplete;
- malformed status JSON → incomplete;
- `source_sha256` mismatch → treats as incomplete even if `complete: true`;
- missing `okf/` on the first pass.

Plus unit cases for `check-structure.sh`: valid in-page anchor, stale bare
fragment, `#page.md` form, `~~~` fence, nested longer fence, scoped run under
`root`, `.status/` excluded from gate 1.

**`Makefile`**: `test` gains the shell suite alongside `$(PYTEST)`:

```makefile
test:
	$(PYTEST)
	./scripts/tests/compile-wiki_test.sh
```

CI needs no change — the `test` job already runs `make test`.

## Verification

```bash
make lint          # shellcheck + yamllint + cspell over the new scripts
make test          # web2md pytest + the new driver and gate suites
make validate      # kit spec unchanged, but confirm
```

Then, on the host with `sbx` available:

```bash
MAX_PASSES=2 ./scripts/compile-wiki.sh md    # real end-to-end, small budget
make lint-okf                                # generated wiki still conformant
```

Confirm by inspection:

- `okf/.status/*.json` written with `source_sha256`;
- pages carry `source`;
- `check-structure.sh okf "$root"` silent per source;
- exit non-zero if any document is incomplete, stalled-out, or gate-rejected.

Note the live `okf/` currently contains **both** `the-rest-is-history.md` and
`the-rest-is-history/`, which gate 3 should already flag — useful as a first
smoke test that the extracted script actually fires.

## Out of scope

- The other 9 merge-blocker sections (retry classification §4, procedure order §7,
  lint scope §11, docs §13, model reconciliation §14, unrelated changes §16).
- Validating `MAX_PASSES`/`MAX_RETRIES`/`MAX_STALLS` as positive integers
  (merge-blockers §6) — adjacent to fix A and cheap to add while there, but not
  a CodeRabbit finding.
- **Two sources deliberately updating the same page** — distinct roots prevent
  the common full+abridged case; intentional shared-subtree merges need a
  separate design (merge-blockers §2).
- **The PR description must be corrected** before merge: its "stubbed-`sbx`
  tests" claim is false today. It becomes true once §4 above lands.
- SKILL.md changes are prompt engineering: the test harness proves the *driver*,
  not the agent's compliance. Only a real `make wiki` run evidences that.
- **`pi --mode json` + in-kit completion tool** — documented under
  [Alternatives considered](#alternatives-considered); not part of this PR.
