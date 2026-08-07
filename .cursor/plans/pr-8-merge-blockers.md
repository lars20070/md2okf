# PR 8 merge blockers

Review target: [PR 8](https://github.com/lars20070/md2okf/pull/8),
`master...lars20070/somechanges` at `e3de034`.

## Recommendation

Do not merge the PR in its current form. The design goal is sound, but the
implementation can report success for an incomplete document, can trust partial
output from a failed pass, and has no reliable per-source completion record.
The committed test suite does not exercise any of the new driver behavior.

The items below are required before merge. They include all seven unresolved
CodeRabbit findings plus additional issues found by reviewing the complete diff,
the runtime instructions, repository documentation, and CI.

## 1. Define a reliable per-source completion protocol

Affected:

- `scripts/compile-wiki.sh:67-77`
- `scripts/compile-wiki.sh:110-113`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:11-21`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:360-367`

The driver currently treats an unchanged byte count across all Markdown files
under `okf/` as proof that the current source document is complete. That does
not prove coverage:

- an agent can stop early and write nothing while source sections remain;
- a split, rewrite, rename, or deletion can leave the total byte count unchanged;
- changes to shared files such as `okf/log.md` can look like source progress;
- output belonging to another source is included in the measurement;
- an empty wiki is called done after two successful no-op passes.

A path-and-content fingerprint would detect more changes than a byte count, but
it still would not prove source coverage. Completion needs an explicit,
machine-readable, per-source signal produced only after coverage, lint, and
structural validation succeed.

Required changes:

- Persist a stable source identity and its completion/coverage state under
  `okf/`, or return an equally reliable structured status that the driver can
  consume.
- Scope progress fingerprints to the current source. Include paths and content;
  exclude unrelated source output and shared bookkeeping.
- Require both an explicit complete status and a stable validated fingerprint
  before printing that a document is done.
- Treat a successful Pi process with incomplete or missing status as incomplete,
  not as success.
- Define how the status is invalidated when the source changes.

## 2. Scope resume detection and preserve source provenance

Affected:

- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:77-95`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:219-233`

The skill says to scan every `okf/**/*.md` before it resolves where the current
source belongs. It then equates “a section has a page” with “the section is
done.” In a wiki built from multiple sources, an unrelated page with a similar
topic or heading can therefore suppress required work.

Scoping only to a topic directory is insufficient when sources intentionally
overlap and update the same topic. Pages need enough provenance to determine
which source section they cover and which source revision they were generated
from.

Required changes:

- Resolve the current source identity and destination before discovering prior
  work.
- Compare against only pages attributed to that source.
- Record source section boundaries or equivalent coverage data so page
  existence alone is not used as proof of completion.
- Specify safe behavior for two source documents that contribute to the same
  page or subtree.

## 3. Make failed-pass recovery safe

Affected:

- `scripts/compile-wiki.sh:88-106`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:87-94`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:346-367`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:369-384`

The driver preserves all files after a failed `sbx exec`, while the next run is
told to trust existing pages and not revisit them. A page assembled through
several tool calls can be left syntactically valid but incomplete if the pass
fails between calls. The retry can then skip that page permanently.

Required changes:

- Make page completion atomic, or persist a completion marker only after the
  whole source section is written and validated.
- Track files touched by a failed pass and revalidate or regenerate them before
  resuming.
- Never infer that a page is complete merely because it exists or passes
  frontmatter lint.
- Add a regression test in which a failed pass leaves a partial page and the
  retry repairs it rather than skipping it.

## 4. Distinguish retryable infrastructure failures from content failures

Affected: `scripts/compile-wiki.sh:93-106`.

Every non-zero `sbx exec` result is currently labeled a possible provider error
and retried. Authentication failures, invalid configuration, agent failures,
lint errors, and failed structural gates are not necessarily transient provider
errors. Retrying them wastes the budget and eventually reports the wrong cause.

Required changes:

- Establish an exit/status contract that distinguishes retryable infrastructure
  failures, incomplete-but-valid work, and deterministic validation failures.
- Retry only failures classified as transient.
- Fail fast, or report an accurate non-provider failure, for deterministic
  errors.
- Preserve the policy of continuing with other documents, but return a final
  non-zero status if any document failed or remained incomplete.

## 5. Return non-zero when the pass budget is exhausted

Affected: `scripts/compile-wiki.sh:115-129`.

When the final pass still changes the wiki, the script prints `INCOMPLETE` and
then exits zero unless another document had repeated process failures. `make
wiki` can therefore report success for known incomplete output.

Required changes:

- Track documents that exhaust `MAX_PASSES`.
- Include their count and paths in the final summary.
- Exit non-zero when either failed or incomplete documents exist.
- Keep completed output on disk so a later invocation can resume.

## 6. Make pass and retry limits truthful and validate them

Affected:

- `scripts/compile-wiki.sh:10-17`
- `scripts/compile-wiki.sh:30-31`
- `scripts/compile-wiki.sh:83-120`

`MAX_PASSES` is documented as the maximum number of Pi runs, but failed
invocations do not increment `pass`. It is therefore a successful-pass limit,
not an invocation or cost limit. `MAX_PASSES=0` and non-numeric values can also
skip all work and exit successfully.

Required changes:

- Decide and document whether `MAX_PASSES` limits all invocations or only
  successful content passes.
- If it is a cost bound, count every invocation separately while retaining a
  consecutive-failure counter.
- Validate `MAX_PASSES` and `MAX_RETRIES` as positive integers before creating
  the sandbox.
- Test zero, negative, empty, and non-numeric values.

## 7. Fix the large-source procedure order

Affected:

- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:42-56`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:97-113`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:148-168`

Numbered step 2 tells the agent to read the source, while step 4 says to measure
and outline it before reading any prose. A literal execution reads a book-sized
source before deciding to process it by section, consuming the context that the
PR is intended to preserve.

Required change: make step 2 identify the source and establish its trust
boundary without reading the body. Measure and extract structure first; read
prose only section by section during the writing phase.

## 8. Replace the incomplete Markdown heading parser

Affected: `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:108-113`.

The proposed `awk` command toggles only on lines beginning with three backticks.
It does not support tilde fences, indentation permitted by Markdown, or matching
the opening fence character and minimum length. A shorter delimiter or a
backtick-looking line inside a longer fence can close it incorrectly, causing
code comments to become phantom source headings.

Required changes:

- Use a Markdown parser or a tested extractor that follows fence character,
  length, indentation, and closing rules.
- Use the same extracted heading positions to calculate section line ranges.
- Test backtick and tilde fences, longer nested-looking delimiters, info
  strings, indentation, and headings immediately outside fences.

## 9. Make deferred cross-page links recoverable and validate them correctly

Affected:

- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:255-279`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:341-344`
- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:456-458`

The skill tells an early pass to remove a link whose target page does not exist,
then says a later pass will restore it. The resume rules simultaneously tell
later passes not to revisit correct existing pages, so there is no guaranteed
restoration step.

Gate 4 only catches malformed fragments containing `.md` or `/`. It misses the
normal stale form `[Highlights](#highlights)` when `highlights` moved to another
page.

Required changes:

- Persist unresolved-link work or require a repair pass when new target pages
  are added.
- Resolve every fragment against headings on the current page and the final page
  map; preserve genuine in-page anchors and flag fragments whose target moved.
- Add tests for valid local anchors, stale bare fragments, half-rewritten
  `#page.md` links, missing targets, and restoration after a later pass.

## 10. Complete the structural and coverage gates

Affected: `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:430-471`.

The four gates do not verify all structure the skill and runtime instructions
require:

- a directory containing pages but missing `index.md` passes;
- an existing index can omit pages or subdirectories and still pass;
- a page can be orphaned from all indexes;
- the one-H1 rule is not checked;
- source coverage is reported only in natural language and is invisible to the
  driver.

Required changes:

- Add a missing-index check for every directory containing content.
- Verify index entries exactly cover the direct pages and subdirectories they
  are meant to enumerate, with no missing or nonexistent targets.
- Check each content page has exactly one H1 and that it agrees with frontmatter
  title according to the project rule.
- Feed machine-readable coverage into the completion protocol from section 1.
- Keep the current empty-directory, empty-index, and page/directory collision
  checks.

## 11. Reconcile whole-wiki linting with per-source scope

Affected:

- `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:386-428`
- `okf/.okflintrc.json:2-12`

The skill lints the whole shared wiki, says to fix every error, and later says to
leave unrelated findings alone. Tightening optional rules to errors means legacy
pages from another source can make the current source pass fail. The agent must
then either modify unrelated work or finish with a failing mandatory lint step.

Required changes:

- Define whether a compile pass owns whole-bundle conformance or only pages and
  indexes affected by the current source.
- Provide a migration path for existing generated pages when severities are
  promoted.
- Ensure the final completion status cannot be emitted while the selected lint
  contract fails.
- Change `SKILL.md:420` from “`recommended-log` warning” to “error” to match
  `okf/.okflintrc.json`.
- Make the numbered procedure explicitly include required ancestor-index
  refreshes, not only the current directory index.

## 12. Add real behavioral tests and run them in CI

The PR description says retry and convergence behavior is covered by
stubbed-`sbx` tests. No test file is present in `master...HEAD`; `make test` and
CI run only `web2md/tests`.

Add a committed, offline driver test harness with a fake `sbx` and temporary
workspace. At minimum, cover:

- transient infrastructure failure followed by success;
- persistent retryable failure, preserving output, continuing other documents,
  and final exit 1;
- deterministic agent or validation failure not mislabeled as a provider error;
- missing `okf/` on the first pass;
- empty/no-op output not being declared complete;
- explicit completion after productive passes;
- byte-stable rename, split, rewrite, and deletion;
- log-only changes not counting as source progress;
- two sources with overlapping headings and separate provenance;
- a failed pass leaving a partial page that is repaired;
- `MAX_PASSES` exhaustion returning non-zero;
- the chosen pass/attempt counting semantics;
- invalid limit environment variables;
- heading-fence and cross-page-link cases from sections 8 and 9;
- missing and incomplete indexes from section 10.

Wire these tests into `make test` and CI. Update the PR description to describe
only tests that are committed and reproducible.

## 13. Update architecture and operator documentation

Affected:

- `README.md:3-6`
- `README.md:13-16`
- `README.md:51-62`
- `AGENTS.md:13-15`
- `scripts/compile-wiki.sh:45-46`

These locations still state that there is one Pi run per source file. The new
driver performs multiple isolated Pi runs per file.

Required changes:

- Document the multi-pass and resume model accurately.
- Document `MAX_PASSES`, `MAX_RETRIES`, their exact semantics, exit behavior,
  and how to resume incomplete output.
- Explain that partial output is retained and that a non-zero result may be
  resumable.
- Keep developer-agent repository guidance in `AGENTS.md` synchronized with the
  runtime architecture.

## 14. Reconcile the default-model change with kit documentation

Affected:

- `pi/files/home/.pi/agent/settings.json:2-3`
- `pi/spec.yaml:5-7`
- `pi/README.md:15-39`

The default changes to `qwen/qwen3.6-35b-a3b`, but the kit description still
says “DeepSeek defaults.” The model documentation's verification command still
lists DeepSeek, and its stated 1M context/384K output values describe the old
catalog entry rather than Qwen's current OpenRouter metadata.

Required changes:

- Update the kit description and model documentation for Qwen.
- Verify the exact model ID through the pinned Pi version, not only through
  OpenRouter.
- Record the effective context, output, reasoning, and tool-use behavior that
  matters to this workflow.
- Update the documented model-list smoke test to verify the selected default.

## 15. Correct misleading PR and committed-plan claims

Affected:

- PR 8 description
- `.claude/plans/fix-empty-index-scaffolding.md`

The PR and plan currently contain claims that do not match the diff:

- “stubbed-`sbx` tests” are not committed;
- the PR says seven lint rules were promoted but lists and changes eight;
- plan lines 417-418 say `okf/.okflintrc.json` is not changed, but it is;
- the plan's regression section is a manual recipe, not an automated test;
- the plan remains tied to the Google Style Guide sample despite a commit
  claiming it was made generic.

Required changes:

- Correct the PR description after implementation and tests are final.
- Update or remove stale parts of the committed plan.
- Clearly distinguish manual experiment results from automated regression
  coverage.

## 16. Resolve unrelated changes before merge

The `lat` MCP removal and deletion of
`.claude/plans/remove-container-runtime.md` are unrelated to resumable wiki
compilation. They increase review scope and make rollback less precise.

Required action: either split them into separate changes with their own
motivation, or explicitly justify and review them as part of this PR before
merge.

## Verification already performed

The following pass on the current branch:

- `make lint`
- `make test` — 149 `web2md` tests only
- `./scripts/validate-spec.sh`
- current GitHub `lint`, `test`, and `validate-kit` checks

These results establish syntax, style, the existing scraper behavior, and kit
schema validity. They do not verify the new compilation loop, resumability,
completion, retry classification, or coverage guarantees.

## Definition of merge-ready

The PR is merge-ready only when:

- every required item above is resolved or deliberately removed from PR scope;
- driver behavior is covered by committed offline tests and CI;
- an interrupted run demonstrably leaves only validated resumable work;
- an incomplete document always produces a non-zero final result;
- a complete multi-source compile has a per-source, machine-verifiable coverage
  record;
- repository and PR documentation match the final behavior;
- `make lint`, `make test`, `make validate`, and `make lint-okf` pass.
