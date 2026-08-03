# Fix the empty-scaffolding failure in `compile-wiki`

## Context

The rewritten skill fixed the *shape* problem: `make wiki` now produces a proper
nested tree with directories per topic, one concept per page, H1-rooted pages and
bundle-absolute links. That part works and this plan does not touch it.

It also introduced a worse problem. Of the 16,514-line source, **only lines
1–2,554 (15%) were compiled**. The remaining 85% is nine directories containing
nothing but a one-line stub index:

```text
okf/google-style-guide/key-resources/index.md      →  "# Key resources"   (1 line)
okf/google-style-guide/punctuation/index.md        →  "# Punctuation"     (1 line)
…9 directories, 0 content pages between them
```

| | |
| --- | --- |
| Source | 16,514 lines |
| Wiki produced | 1,477 lines (**9%**) |
| Content pages | 5 |
| `index.md` files | 12, of which **10 are a bare heading** |
| Topic directories | 9, of which **9 contain zero content pages** |
| Internal links | **537 malformed**, 11 correct |

### Every gate passed

This is the part that matters. The run did not report a failure:

```text
$ pnpm dlx @thisismydesign/okf-lint ./okf
✓ No problems found.

$ find okf -type d -exec test ! -e '{}/index.md' \; -print     # the skill's own shape check
                                                               # (prints nothing = passes)
```

`okf-lint` has no rule for an empty index, an empty directory, or missing
coverage, and the skill's own structural check tests that an index **exists**,
never that it has entries. So the agent finished, both gates went green, and its
final message would have honestly reported `✓ No problems found`.

### The log shows it stopped deliberately

`okf/log.md`, last entry:

> **Creation**: Added index and directory structure for general-principles,
> key-resources (including word-list), language-and-grammar, punctuation,
> formatting-and-organization, linking, computer-interfaces, html-and-css, and
> names-and-naming.

It did not crash mid-write — `whats-new.md` ends cleanly at its last release
entry. It worked front-to-back through the source, reached `### Word list` at
line 2558 (a single 4,134-line section), created the skeleton for everything
remaining, **logged the skeleton as a deliverable**, and stopped.

**Intended outcome:** the wiki that exists is always real content, a run that
cannot finish says so instead of faking coverage, and repeated runs converge on
a complete wiki — with the directory structure from point 1 unchanged.

---

## Root cause: what in `SKILL.md` caused this

Eight causes, all in the current file. The first four produced the scaffolding;
the last four let it pass as success.

### C1 — "You are invoked **once per source document**" (line 9)

The single most damaging sentence. It tells the agent this is its only chance at
the document. Faced with a budget that covers 15% of the source, an agent told it
gets one shot will rationally prefer *something covering everything* — a
skeleton — over *part of it done properly*. It is also now simply false: this
source needs roughly ten runs.

### C2 — The outline is delivered to the final message, not to disk (lines 97–98)

> **Write the planned page tree** — path and title per page — into your final
> message *before* you write any page

The final message is produced at the *end* of the run. So for the whole run there
is no artifact recording planned-vs-done — and when the budget ran out, the only
remaining way to "deliver the page tree" was to build it out of directories.
**The empty skeleton is the outline, materialised.** The instruction asked for a
tree; it got a tree.

### C3 — Indexes are mandated, empty ones are never forbidden (lines 163, 239)

> **Every directory gets an `index.md`**, which is what makes depth navigable

> Every directory, including every new subdirectory, has an `index.md`.

Nothing says a directory may exist only once it holds content, or that an index
must list something. Nine directories with stub indexes satisfy both rules
literally.

### C4 — Index-writing is a separate phase, unbound from the pages (procedure step 6)

Indexes are regenerated as their own step, with nothing tying an index to files
that actually exist beneath it. Writing an index for pages that were never
written is not ruled out.

### C5 — Coverage is checked at outline time, never at exit (lines 99–101)

> **Check the outline covers the source.**

That is an outline-time check. There is no end-of-run check that each planned
page exists on disk.

### C6 — The structural check tests existence, not content (lines 321–324)

```bash
find okf -type d -exec test ! -e '{}/index.md' \; -print
```

Passes on a directory whose index is one heading and whose content is nothing.
Verified against the broken wiki: prints nothing.

### C7 — The definition of done is the linter, and the linter is blind here (lines 61–62, 335–337)

> Do not declare the run finished before this step passes.

> End your final message with the linter's summary line.

`okf-lint` checks conformance. A 91%-empty bundle is perfectly conformant.

### C8 — Nothing says what to do when the budget runs out

There is no rule for stopping cleanly, no instruction to report partial coverage,
and no statement that a later run will continue. "Create the structure, log it,
stop" was the most plausible terminal move available.

### C9 — Nothing says what to do with links that already exist in the source

The most pervasive defect in the run, and it is not about emptiness at all.

The source is one concatenated page, so all of its cross-references are anchors
into itself — **1,236 of them**, in the form `[Highlights](#highlights)`. When
the compile splits that page into many, every one of those anchors has to become
a bundle-absolute path to wherever the target landed.

The agent got this **half right**, which is worse than getting it wrong:

```markdown
source:   [Highlights](#highlights)
produced: [Highlights](#highlights.md)              ← target resolved, "#" kept
correct:  [Highlights](/google-style-guide/highlights.md)
```

It correctly worked out which page each target had become — and then kept the
leading `#`, because the skill's fidelity rule says *preserve the source prose
verbatim* and nothing tells it that a link is structure rather than wording. The
result: **537 broken links against 11 correct ones**, wiki-wide.

`okf-lint` cannot see any of it. `prefer-absolute-links` and `valid-links` both
read a leading `#` as an in-page fragment, so there is no path to resolve and
nothing to report — which is the third reason the run came back clean.

### Two further faults, same run

- **`okf/google-style-guide.md` and `okf/google-style-guide/` both exist.** The
  no-collision rule (lines 140–142) is phrased for *splitting an existing page*
  and does not cover the case where the source document itself becomes a
  directory.
- **`whats-new.md` is 1,257 lines** — a changelog written as one page. It is 85%
  of everything the run produced, and it is what consumed the budget before the
  real content began.

---

## Research findings

### 1. This cannot be fixed by prompting — the arithmetic forbids it

The fidelity rule requires verbatim transcription, so output must roughly equal
input. The empirical measurement from this run: **one run of
`qwen/qwen3.6-35b-a3b` produced 1,477 lines of wiki.** Covering 16,514 lines
therefore needs on the order of **ten to twelve runs**. No wording change to
`SKILL.md` alters that. The skill can only decide what a run does with the budget
it has, and whether the next run can pick up the thread.

### 2. The established fix is progress-on-disk plus resumption

The long-running-agent literature converges on one pattern: context windows are
finite regardless of size, and long tasks exhaust them; the answer is to write
intermediate state to disk and resume from it. *"Sessions remember the
conversation. Checkpointing remembers the files."* On resume, an agent mounts the
workspace from its last known state, reads what previous attempts left behind,
and continues.

Our case is the easy version of this: **the wiki itself is the progress file.** A
source section with no page on disk is unfinished work. No new artifact is
needed — which is why this plan adds no manifest and no state file, and why the
existing idempotency rule already carries most of the semantics.

This is also why **empty scaffolding is actively harmful rather than merely
untidy**: it destroys the only signal of what remains. A directory that exists
but is empty is indistinguishable from a directory that is finished, so the next
run cannot tell where to resume.

### 3. Skills need exit criteria, not more rules

The strongest finding for the fix, from a production-skills field guide:

> **Weak:** "Write better React components."
> **Strong:** "Before finishing, run the local checks, verify the responsive
> states, preserve existing user edits, avoid new dependencies unless justified,
> **and report what was not verified**."

Exit criteria are described as observable behavioural gates covering "what the
agent must check before finishing" and "what evidence it should return", with a
handoff receipt listing *files changed, commands run, **commands not run**, risks
left open*. A companion pattern requires the agent to identify the proof command,
run it fresh in the session, read the full output, confirm it proves the claim,
then report with evidence.

Our skill has a proof command that cannot fail. That is the gap.

### 4. The wiki-compiler ecosystem does not attempt this in one pass either

`atomicstrata/llm-wiki-compiler` runs concept extraction and page generation as
**parallel compile runs under a configurable cap**, not one monolithic pass. The
Karpathy-lineage tools ingest one source at a time and expect a single ingest to
touch a bounded number of pages. Nobody compiles a book in one agent turn.

---

## Plan

Two files. The skill stops producing scaffolding and starts reporting honestly;
the driver supplies the runs the arithmetic demands.

### A. `SKILL.md` — never scaffold

**A1. Replace "invoked once per source document" (C1) with resumption.** New
framing in the intro:

> You may be **one of several runs** against the same source document. The wiki
> on disk is the record of what is already done: a section of the source with no
> page beneath it is work remaining. Begin by comparing the source's heading tree
> with what exists under `okf/`, and continue at the first gap. Never start over,
> and never rebuild what is already correct.

**A2. A directory exists only because it has content (C3, C4).** New hard rule in
"Mirror the source's structure" and "Index files":

> **Never create an empty directory, and never write an index for pages that do
> not exist yet.** A directory comes into being when you write its first content
> page. Write the pages, then write or refresh the index **from the files
> actually on disk**.
>
> An index whose list is empty, or a directory holding no page, is a **defect** —
> worse than the directory not existing, because it hides the fact that the work
> is outstanding and stops a later run from finding it.

**A3. Delete the "write the page tree into your final message" instruction (C2)**
and replace it with the same information delivered as work, not as a picture:

> Hold the outline as your plan for this run. Do not materialise it as empty
> directories, placeholder pages, or index entries pointing at files you have not
> written. The tree becomes visible as pages appear.

The final message still reports what it compiled — but as coverage (A5), not as a
tree of intentions.

**A4. Finish one branch before starting another.** New rule in "Reading the
source":

> Work depth-first: take one branch of the outline, write every page in it,
> refresh its index, and only then move to the next. A run that ends part-way
> should leave a **smaller correct wiki**, never a hollow one.

Plus, for the section that stalled this run:

> A section far larger than its siblings is not a reason to defer it. It is a
> directory whose children are the unit of work — take them one at a time. A
> changelog splits by release, a glossary by letter, a reference by symbol group.

**A5. Stop cleanly and say so (C8).** New section, "When you run out of room":

> Running out of budget mid-document is expected and is not a failure. When you
> are close to the limit:
>
> 1. Finish the page in hand — never leave a half-written page.
> 2. Refresh the indexes for what now exists on disk.
> 3. Append to `okf/log.md` only what you actually wrote. **Never log the
>    creation of structure as an achievement.**
> 4. End your message with an explicit coverage statement: which source sections
>    are compiled, which remain, and the line number to resume from.
>
> Do not compress, summarise, or stub the remainder to make the run look
> complete. A later run will continue from what you leave on disk.

**A6. Exit criteria that can fail (C5, C6, C7).** Replace the existence check in
"Check the shape of what you wrote":

```bash
# 1. Directories with no content anywhere beneath them — must print nothing
find okf -mindepth 1 -type d | while read -r d; do
  [ -z "$(find "$d" -name '*.md' ! -name index.md)" ] && echo "EMPTY DIR: $d"
done

# 2. Indexes that list nothing — must print nothing
find okf -name index.md | while read -r f; do
  grep -q '^\* \[' "$f" || echo "EMPTY INDEX: $f"
done

# 3. A page sitting alongside a directory of the same name — must print nothing
find okf -mindepth 1 -type d | while read -r d; do
  [ -f "${d}.md" ] && echo "COLLISION: ${d}.md and ${d}/"
done

# 4. Cross-page links left as anchors — must print nothing.
#    Matches only anchors whose target names a file or a path, so genuine
#    in-page anchors like [see below](#voice-and-tone) are not flagged.
grep -rnE '\]\(#[^)]*(\.md|/)' okf --include='*.md'
```

And an explicit reframing of what "done" means:

> A clean `okf-lint` report means the wiki is **conformant**. It does not mean it
> is **complete** — the linter has no rule for an empty index, an empty
> directory, or missing coverage. Never present a clean lint report as evidence
> that the document was compiled. Report coverage separately and honestly,
> including what you did not do.

**A7. The document-root collision rule.** In "One concept per page":

> When the source document as a whole becomes a directory, it does **not** also
> get a page beside that directory. Its front matter, abstract, or introduction
> becomes a named page **inside** the directory (`about.md`, `overview.md`),
> listed first in the directory's index.

**A8. Rewriting the source's own links (C9).** New section, "Links inherited
from the source" — the fix for 537 of the 548 links in the run:

> A source document that was one page carries cross-references as **anchors into
> itself** — `[Highlights](#highlights)`. Splitting it into many pages relocates
> every one of those targets, so every such link must be **rewritten** to the
> bundle-absolute path of the page the target now lives on:
>
> ```markdown
> source:   [Highlights](#highlights)
> rewrite:  [Highlights](/google-style-guide/highlights.md)
> ```
>
> - **Rewriting a link is a structure change, not a wording change.** The
>   fidelity rule does not protect the anchor — it protects the link *text*.
>   Leave `[Highlights]` exactly as written; replace only the target.
> - **Never keep the `#` while changing the target.** `](#highlights.md)` is
>   neither an anchor nor a path. It resolves to nothing, and `okf-lint` cannot
>   warn you: a leading `#` reads as an in-page fragment, so `valid-links` and
>   `prefer-absolute-links` both skip it silently.
> - **A `#` is correct only for a heading inside the same page.** If the target
>   is on another page, it is a path.
> - **If the target page does not exist yet**, leave the link text in place and
>   drop the link rather than pointing at a file that is not there — a later run
>   restores it when it writes that page.

**A9. Link form in indexes.** In "Index files":

> Every internal link is bundle-absolute and points at a file:
> `/google-style-guide/highlights.md`. Never `#highlights.md`, and never a bare
> fragment for a cross-page link.

### B. `scripts/compile-wiki.sh` — loop until coverage stops improving

The driver currently runs Pi exactly once per document. Replace that with a
bounded retry loop that keeps calling Pi while the wiki keeps growing:

```bash
max_passes="${MAX_PASSES:-20}"

for document in "${markdown_folder}"/*.md; do
	echo "Compiling document ${document}"
	previous=0
	pass=1
	while [ "${pass}" -le "${max_passes}" ]; do
		echo "  pass ${pass}"
		sbx exec "${kit_name}" -- pi \
			-p "Load the compile-wiki skill: read ~/.pi/agent/skills/compile-wiki/SKILL.md, then follow it to compile ${document} into the OKF wiki under okf/. This may be a continuation — okf/ already holds the work of earlier passes. Compare the source against what is on disk and continue at the first gap; do not start over." \
			</dev/null
		current=$(find okf -name '*.md' -exec cat {} + 2>/dev/null | wc -c)
		if [ "${current}" -eq "${previous}" ]; then
			echo "  no progress on pass ${pass}; moving to the next document"
			break
		fi
		previous="${current}"
		pass=$((pass + 1))
	done
done
```

Notes for the implementer:

- **Progress metric is bytes of wiki content**, not page count — a pass that only
  splits a page or fills an index still counts as progress. Exact equality is the
  stop condition, so a pass that removes bytes (a split that deletes the original)
  correctly continues.
- **`MAX_PASSES` caps the cost.** Each pass re-reads `SPEC.md`, `AGENTS.md`,
  `SKILL.md` and re-surveys the wiki, so passes are not free; the cap is the
  guard against a pathological loop. Default 20, override per invocation.
- `</dev/null` stays on the `sbx exec` call — for the reason the existing comment
  gives.
- Keep the `while` counter rather than `for … $(seq …)`; `make lint` runs
  shellcheck over `scripts/*.sh`.

### Files

| File | Change |
| --- | --- |
| `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md` | A1–A8 |
| `scripts/compile-wiki.sh` | B — bounded retry loop, `MAX_PASSES` |

`okf/.okflintrc.json` is **not** changed: no `okf-lint` rule can express "index
has entries" or "directory has content", so these checks stay in the skill.

### Explicitly preserved

Point 1 of the feedback — the subfolder structure — is untouched. The outline
step, the concept level, "mirror the source's structure", one-concept-per-page,
H1 re-rooting and the index conventions all stay exactly as they are. The only
change to structure is **when** directories come into existence: as their pages
are written rather than ahead of them. The tree after a converged run is the same
tree.

---

## Verification

```bash
./scripts/validate-spec.sh      # required: SKILL.md lives under pi/
make lint                       # markdownlint on SKILL.md + shellcheck on the driver
```

Clean recompile — `okf/.okflintrc.json` is tracked, everything else there is
generated:

```bash
find okf -mindepth 1 -maxdepth 1 ! -name '.okflintrc.json' -exec rm -rf {} +
make wiki                       # now loops per document
make lint-okf
```

Then the four gates the skill now applies to itself — **each must print
nothing**:

```bash
find okf -mindepth 1 -type d | while read -r d; do
  [ -z "$(find "$d" -name '*.md' ! -name index.md)" ] && echo "EMPTY DIR: $d"
done
find okf -name index.md | while read -r f; do
  grep -q '^\* \[' "$f" || echo "EMPTY INDEX: $f"
done
find okf -mindepth 1 -type d | while read -r d; do
  [ -f "${d}.md" ] && echo "COLLISION: ${d}.md and ${d}/"
done
grep -rnE '\]\(#[^)]*(\.md|/)' okf --include='*.md'
```

All four were confirmed against the current broken wiki before this plan was
written — they fire on exactly the defects above (10 empty directories, 10 empty
indexes, 1 collision, 495 lines of malformed links) and produce no false
positives on the 4 legitimate in-page anchors. They are regression tests, not
guesses.

Also confirm links were actually rewritten rather than merely un-anchored:

```bash
# bundle-absolute links should now vastly outnumber in-page anchors
echo "absolute: $(grep -roE '\]\(/[^)]+\)' okf --include='*.md' | wc -l)"   # was 11
echo "anchors:  $(grep -roE '\]\(#[^)]+\)' okf --include='*.md' | wc -l)"   # was 541
```

And coverage, which is the actual point:

```bash
echo "source: $(wc -l < md/GoogleStyleGuide.md) lines"
echo "wiki:   $(find okf -name '*.md' -exec cat {} + | wc -l) lines"
```

A verbatim compile should land in the same order of magnitude as the source —
roughly 15,000–20,000 lines once frontmatter and indexes are counted, against
1,477 today. Anything near the current figure means the loop is exiting early.

Also confirm by reading:

- No directory is a stub. Open two or three at random.
- `okf/google-style-guide.md` no longer exists beside `okf/google-style-guide/`.
- The largest section (`Word list`, 4,134 source lines) has become a directory of
  per-letter pages rather than being skipped.
- The driver's per-pass output shows progress falling to zero and stopping, not
  hitting `MAX_PASSES`. If it hits the cap, coverage is still incomplete.

**Test resumption directly**, since that is the new load-bearing behaviour:

```bash
MAX_PASSES=2 make wiki          # deliberately stop early
find okf -mindepth 1 -type d | while read -r d; do
  [ -z "$(find "$d" -name '*.md' ! -name index.md)" ] && echo "EMPTY DIR: $d"
done                            # must STILL print nothing — partial ≠ hollow
make wiki                       # resumes and continues from disk
```

The first command must leave a smaller *correct* wiki, and the second must add to
it rather than restart. That pair is the regression test for this whole plan.

---

## Sources

- [Agent Skills Need Exit Criteria, Not More Prompt Lore](https://www.developersdigest.tech/blog/agent-skills-production-checklist) — exit criteria as observable gates; "report what was not verified"; handoff receipt listing commands *not* run
- [Long-Running AI Agent Runtime in 2026: Sessions, Sandboxes, Checkpoints, and Harnesses](https://slavadubrov.github.io/blog/2026/05/26/ai-agent-runtime/) — "Sessions remember the conversation. Checkpointing remembers the files."; checkpoint granularity
- [How to Resume an Interrupted Long-Running AI Agent Task](https://knightli.com/en/2026/07/10/ai-agent-long-task-resume-guide/) — resume by mounting the workspace and reading what the previous attempt left behind
- [7 State Persistence Strategies for Long-Running AI Agents in 2026](https://www.indium.tech/blog/7-state-persistence-strategies-ai-agents-2026/) — write intermediate state to disk, checkpoint every N units of work
- [Claude Agent SDK Checkpointing: Your Agent Hit Its Turn Limit Halfway Through](https://medium.com/@richardhightower/claude-agent-sdk-checkpointing-your-agent-hit-its-turn-limit-halfway-through-71a36515c602) — turn-limit exhaustion as the expected case, resume rather than restart
- [atomicstrata/llm-wiki-compiler](https://github.com/atomicstrata/llm-wiki-compiler) — parallel compile runs under a configurable cap; nobody compiles a corpus in one turn
- [thisismydesign/okf-lint](https://github.com/thisismydesign/okf-lint) — rule set confirming no coverage, empty-index or empty-directory rule exists
- [OKF v0.1 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) — vendored as `SPEC.md`; §6 index files, §9 conformance
