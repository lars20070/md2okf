# OKF consumption test — design

**Date:** 2026-07-31
**Status:** approved, for implementation

## Problem

`md2okf` is verified end to end as a *producer*: a 382 KB book compiles into a
38-page OKF wiki that passes `okf-lint`. Nothing verifies the wiki is any
*use*. Completeness and well-formedness are not usefulness, and OKF's own goals
name consumption explicitly:

> Inform how **consumption agents** should read and traverse it.
> — `SPEC.md`, Goals §2

So: can an agent holding only the compiled wiki apply the knowledge in it, and
can we tell the difference between it having done so and it having guessed?

## The prior-knowledge problem

This is the crux. A capable model already knows roughly what Economist house
style is. Hand it a badly written paragraph and a wiki, and a good rewrite
proves nothing — it may never have opened a page.

Two mitigations, both required:

1. **Arbitrary rulings.** Cases are built on house rulings a model cannot
   derive from general knowledge, several of which invert the common
   convention. The strongest is `%`: most style guides prefer spelling out
   "per cent", and this one requires the sign. A model working from priors gets
   it backwards.
2. **Verified citations.** Every change must cite the page it came from, and
   grading checks the cited page *actually says so*. A plausible citation to a
   page that does not support the claim fails.

There is deliberately **no A/B control arm** (running each case again with the
wiki absent). It would be the cleanest evidence of contribution, but it doubles
the runs, and the counterintuitive rulings already give the test the ability to
fail when the wiki is unread. Recorded as a known limitation, not an oversight.

## Isolation

A second Compose service, `pi-consume`, reusing the existing image:

| Mount | Compile run | Consumption run |
| --- | --- | --- |
| `md/` | read-only | **absent** |
| `okf/` | read-write | **read-only** |

`md/` is unmounted so the agent cannot reach the source book — only the compiled
wiki. `okf/` is read-only because consumption must not mutate the artefact under
test; it also means the run needs no writable mount at all.

The driver passes `--provider` and `--model` explicitly rather than editing
`settings.json`, so the test states which model it exercised and leaves repo
config untouched.

## Output contract

The agent writes nothing. Its final message is the result, captured from
`pi -p` stdout, and must end with a fenced `json` block:

```json
{
  "rewrite": "the corrected paragraph",
  "changes": [
    {
      "before": "per cent",
      "after": "%",
      "ruling": "Use the sign % instead of per cent.",
      "citation": "/part-2/7-sweating-the-small-stuff-punctuation-mechanics-and-conventions.md"
    }
  ]
}
```

The grader reads the **last** fenced `json` block, so surrounding prose is
harmless. A missing or unparseable block fails the case explicitly rather than
scoring zero silently.

## Grading

Three mechanical assertions per case. No LLM judge — every check is a string or
filesystem operation, so the result is deterministic and reproducible.

1. **applied** — every `expect_present` string appears in `rewrite`, and every
   `expect_absent` string does not.
2. **cited** — at least one `changes[].citation` resolves to a file that exists
   in the bundle.
3. **grounded** — that cited file contains the case's `grounding` text.

A case passes only when all three hold. Assertion 3 is what makes hallucinated
citations fail: getting the edit right by luck and inventing a source still
fails the case.

## Cases

All eight are verified present in the compiled wiki. `ch6` is
`/part-2/6-confusables-and-cuttables-individual-rulings.md`.

| # | Ruling | Page | Discriminates because |
| --- | --- | --- | --- |
| 1 | `%` not "per cent" | ch7 | inverts the usual convention |
| 2 | do not verb "impact" | ch9 | house prohibition, not grammar |
| 3 | "due to" modifies nouns only | ch6 | prefers *because of* / *owing to* |
| 4 | "decimate" = a significant proportion | ch6 | not total destruction |
| 5 | "fewer" for countables | ch6 | common error, explicit ruling |
| 6 | no sentence-initial "Hopefully," | ch6 | explicitly *not* a grammar rule |
| 7 | "alibi" ≠ excuse | ch6 | semantic ruling |
| 8 | "compared with" for evaluation | ch6 | fine distinction against *compared to* |

## Failure taxonomy

Infrastructure failure must never read as "the wiki is bad". The driver exits:

- `0` — all cases passed
- `1` — at least one case failed on its assertions (a real result)
- `2` — infrastructure trouble: missing key, gateway error, no wiki, no cases

## Components

| Path | Purpose |
| --- | --- |
| `pi/{container,sandbox}/…/skills/apply-house-style/SKILL.md` | the consumption task, one copy per runtime, aligned by hand |
| `tests/house-style/cases.yaml` | fixtures: input, assertions, expected page, grounding |
| `tests/house-style/grade.py` | the three assertions, table output, exit code |
| `scripts/test-house-style.sh` | driver: one Pi run per case, then grade |
| `pi/container/compose.yaml` | adds the `pi-consume` service |

## Non-goals

- **Navigability.** The container ships `ripgrep` and `fd`, so the agent will
  likely grep rather than traverse `index.md` files. This test says nothing
  about whether the index structure works.
- **Prose quality.** Only the specific rulings are graded, not whether the
  rewrite reads well.
- **The sandbox runtime.** Implemented for parity, exercised on the container
  runtime only, matching how every other result in this repo was obtained.
