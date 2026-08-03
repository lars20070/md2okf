# Improve the `compile-wiki` skill: one concept per page, structure that mirrors the source, self-rooted headings

## Context

`pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md` is a first draft. It gets
conformance right — every generated page has parseable frontmatter, a `type`,
bundle-absolute links, and `okf-lint` passes — but it says almost nothing about
**how knowledge should be shaped**, and the output shows it.

The sample source (`md/GoogleStyleGuide.md`) compiled into 15 flat pages:

| Page | Lines | First heading |
| --- | --- | --- |
| `computer-interfaces.md` | 2,081 | `## Computer interfaces` |
| `whats-new.md` | 1,540 | `# … : What's New` |
| `word-list.md` | 1,514 | `### Word list` |
| `general-principles.md` | 1,275 | `## General principles` |
| `word-list-o-z.md` | 1,205 | `##### O` |
| `punctuation.md` | 1,075 | `## Punctuation` |
| … 9 more | 105–1,040 | mostly `##`, one `###` |

Three defects are visible in that table alone:

1. **Pages are chapters, not concepts.** `computer-interfaces.md` alone carries
   six independent topics, each of which was its own document upstream.
2. **The structure is flat.** Zero subdirectories. The root index has one entry;
   the one directory index is an ungrouped 15-item list. An agent gets one hop of
   progressive disclosure and then hits a wall of prose — the opposite of what
   `index.md` exists for.
3. **Heading levels were copied verbatim from the source**, so only 2 of 15 pages
   open with an H1. One opens at `#####`. Each page is a slice cut out of a book
   rather than a document that stands on its own.

This plan rewrites `SKILL.md` to make page shape an explicit, checkable part of
the procedure, and tunes `okf/.okflintrc.json` so the linter catches more of what
the conventions require.

### The skill must be source-agnostic

`md/GoogleStyleGuide.md` is a **sample, not the contract**. The README's
instruction is "Drop Markdown files into `md/`", and `scripts/compile-wiki.sh`
runs Pi once per `md/*.md` in glob order, so a run may be handed:

| | |
| --- | --- |
| **One file or many** | Each is a separate run against the same growing wiki |
| **Any size** | A short note, a scraped site, a converted book |
| **Any structure** | `web2md` emits a deep, regular heading tree with per-section source URLs; `pdf2md`/`marker` emits whatever survived PDF conversion — inconsistent levels, missing headings, no URLs; a hand-written file may have almost no structure at all |
| **Any order** | Runs are alphabetical, and a later run may need to nest inside a directory an earlier run created |

So every rule in the Plan below is stated **without reference to the sample**.
Concrete numbers appear only in Research finding 7, which is explicitly a
measurement *of* the sample and exists to justify the rules — none of those
numbers should reach `SKILL.md`.

Two failure modes have to be guarded symmetrically: the observed one, where a
structured source is flattened into a few enormous pages; and its mirror, where a
small or unstructured source is inflated into a deep tree of stubs it does not
warrant.

### Design direction

Set by the repo owner and consistent with the research below: state the rule as
*one concept per page*, discourage flat structures, require an H1 at the top of
every page including in subdirectories — and express all of it **without
hard-coded thresholds**. No lines-per-page number, no target page count, no
children-per-directory cap. Numbers of that kind are unverifiable by the agent,
wrong for the next source document, and invite box-ticking instead of judgement.

**Where the skill is prescriptive vs where it defers:** be explicit about
**mechanics**, defer on **semantics**. Mechanics have one right answer, are cheap
to state as a command, and are exactly what the first draft left vague and the
agent then skipped — "Read long sources … in ranges" produced 2,081-line pages.
Semantics — where a concept boundary falls, what a page is called, how to group
an index — genuinely vary per source and are what an agent is for. So the skill
hard-codes *how to inspect and read a source* and *what shape the output takes*,
and hard-codes no level, no size, and no count. The runtime model is
`qwen/qwen3.6-35b-a3b`, a small MoE; it will not invent a disciplined reading
protocol on its own, and it should not have to.

---

## Research findings

### 1. OKF itself deliberately declines to specify page size

`SPEC.md` (v0.1, 2026-06-12) requires exactly one thing of a concept: a non-empty
`type`. §9 Conformance lists three rules, none about size or shape. The only
shaping guidance in the whole spec is §4.2:

> Producers SHOULD favor structural markdown — headings, lists, tables, fenced
> code blocks — over freeform prose, since structure aids both human reading and
> agent retrieval.

and §6, which frames `index.md` as existing for **progressive disclosure** —
"letting a human or agent see what is available before opening individual
documents." Google Cloud's launch post says the same and no more: "Each concept
is one file", "the file path serves as the concept's identity". It gives no
granularity rule and explicitly leaves the content model to producers.

**So: page shape is a producer convention. It is ours to set, and nobody will set
it for us.** Nothing in `SPEC.md` or `okf-lint` will ever complain about a
2,081-line page.

### 2. The ecosystem convention is "one concept per file" — with split detection as a first-class lint

Two months in, the OKF tool directory (`okf.md/tools`) lists "One concept per
file" and "'Split candidates' detectable via link graph visualization" under file
organization, plus "Hierarchical layout mirrors resource structure". The
community linter `okflint` ships an `audit` mode producing "an X-ray of your base
including broken links, **split candidates**, and stats".

Notably, nobody in the ecosystem publishes a line or word threshold. The
convention that has actually taken hold is qualitative — one concept, one file —
with tooling that *detects* over-broad pages from the link graph rather than from
a size limit. Our linter (`thisismydesign/okf-lint`) has no such rule, so the
judgement has to live in the skill.

### 3. The Karpathy LLM-wiki lineage: the binding constraint is page *count*, not page size

- Karpathy's own wiki matured at ~100 articles / ~400,000 words. That is a wiki
  of *synthesised* prose, not a verbatim compile, so it is a weak precedent for
  page size — but a useful one for scale.
- The operative number across sources concerns the index, not the page: at
  roughly 150–200 pages an agent can no longer hold a wiki in context; a master
  index of one-line summaries plus selective loading extends practical capacity
  well beyond that. `cablate/llm-atomic-wiki` states the same ceiling from the
  other side: "Past that [~200 wiki pages], `index.md` scans degrade and you need
  vector search alongside."

**The lesson is not a page budget — it is that the index is what fails first.**
Which is why the fix for scale is *nesting* (each index lists a manageable set,
and the depth absorbs growth), not smaller pages. This matters more here than in
a single-source wiki, because `md/` accumulates: every run adds to the same
bundle, so the root index is the one thing guaranteed to keep growing.

### 4. Flat directories are explicitly discouraged; indexes should be tiered

`kfchou/wiki-skills` — the most-referenced Karpathy-pattern skill set, and
OKF-aware since the spec landed:

> a flat-directory containing all wiki pages should be discouraged to facilitate
> the ease of index generation

> one methodology for structuring subdirectories is to divide wiki docs among
> **high level, commonly used, non-overlapping concepts**

and on disclosure:

> token-budgeted, tiered indexes … instead of one flat index

`llm-atomic-wiki` uses "one folder at repo root per topic". Both also split lint
into a deterministic layer (broken links, orphans, format) and a semantic layer
(contradictions, stale claims).

### 5. Retrieval evidence: the unit is one idea, and the boundary should come from the source's own structure

Current chunking guidance converges on a few hundred tokens per unit for dense
reference material, but the more durable finding is the *procedure*: "split first
on major boundaries (sections, paragraphs), then recursively split large
sections". The boundary that matters is semantic, and the best available signal
for it is the structure the source's own author already imposed.

The sample demonstrates how strong that signal can be. Verified: in every
generated page, the count of H3 headings exactly equals the count of
`*Source: <url>*` lines — each H3 corresponds to exactly one upstream document
with its own canonical URL. But that signal is an artefact of how `web2md`
concatenates a site; a `marker`-converted PDF will carry nothing like it. **The
rule must therefore be "look for whatever boundary signal this source carries",
not "look for source URLs".**

### 6. The closest existing tool solves an easier problem

`chapter42/okf-convert` (Markdown/web → OKF) is the nearest analogue. It maps
**one input file to one concept**, goes deliberately flat, derives `title` from
H1/filename, `description` from an LLM pass or the body's first sentence, and
`timestamp` from file mtime. It never splits a document — fine for a directory of
small notes, wrong for a converted book. Our skill has to cover both, which is
why the rule is stated as *mirror the source* rather than as a fixed mapping.
What it does that we don't: it always emits `timestamp`.

### 7. Measurements of the sample — evidence for the rules, not rules themselves

Measured on `md/GoogleStyleGuide.md`. **None of these numbers belong in
`SKILL.md`**; they exist to show why the mechanics in steps 1–2 are needed.

| | |
| --- | --- |
| Size | 16,514 lines / 611 KB / 81,572 words ≈ **153k tokens** |
| Heading tree (H1–H4, fence-aware) | 529 headings, 16.8 KB ≈ **4k tokens — 2.6% of the document** |
| Heading-level histogram | 1×H1, 11×H2, 80×H3, 437×H4, 143×H5, 15×H6 |
| Largest single H1–H4 section | 4,092 lines (`### Word list`, which only decomposes at H5) |
| Headings inside fenced code blocks | **13** — false sections a naive `grep '^#'` would pick up |

Four consequences, each stated generally in the Plan:

1. **A source can be far too large to hold in context while writing pages.** At
   ~153k tokens this one leaves no room to write the subtree, whatever the
   model's window. The skill cannot assume either way — it has to **measure
   first** and pick a reading strategy from the measurement.
2. **The heading tree is the map, and it is cheap at any size.** 4k tokens buys
   the complete structure with line numbers. Consecutive heading line numbers
   *are* the section boundaries — the split, computed rather than materialised.
   Physically splitting a source file would require this same analysis first and
   then add an artifact on top of it.
3. **Depth is not uniform within one document.** Here most chapters resolve at
   H3, but one section spans 4,134 lines and only breaks up at H5. A fixed
   heading level is wrong even for a single source, let alone across sources — so
   the concept level must be chosen per branch.
4. **Headings appear inside fenced code blocks.** Any heading extraction must be
   fence-aware or it invents pages from sample code.

**Conclusion: instruct measuring and bounded reading, not file splitting.** `md/`
is read-only, the workspace mount writes through to the host tree, and `/tmp` is
per-run, so chunk files have nowhere good to live and buy nothing a line range
does not already give. The one thing splitting would provide — a guarantee that
no section was skipped — comes instead from checking the outline against the
heading tree, which step 1 requires.

### 8. `okf-lint` rules we are not using

Full rule set of `thisismydesign/okf-lint`:

| Errors (conformance) | Warnings (best practice) |
| --- | --- |
| `frontmatter-present` | `recommended-title`, `recommended-description`, `recommended-timestamp` |
| `frontmatter-parseable` | `tags-type`, `timestamp-format` |
| `type-required` | `recommended-index`, `recommended-log`, `log-date-order` |
| `index-frontmatter` | `valid-links`, `prefer-absolute-links` |
| `index-version-key` | `okf-version-declared`, `okf-version-supported`, `okf-version-format` |
| `log-date-format` | |

Our `okf/.okflintrc.json` configures five rules and turns `recommended-timestamp`
**off** — which is why not one generated page carries a timestamp.
`prefer-absolute-links` and `recommended-title` sit at default warning even
though `AGENTS.md` makes both mandatory. There is no rule for page shape, heading
structure, or nesting, and there never will be — so those checks belong in the
skill's own procedure.

---

## Diagnosis: why the output came out this shape

1. **The skill has no shaping instruction.** Step 4 says "Write the content
   pages, organised into directories by topic" — no concept rule, no split
   guidance, no depth expectation. "Organised into directories by topic" is
   satisfied by one directory, and one directory is what it produced.

2. **"Write in bounded chunks" teaches the wrong lesson.** It is a correct
   workaround for a tool-output limit — build a long page with `write` then
   repeated `edit`. But it is the *only* place in the skill that discusses page
   length, and it tells the agent how to **grow** an over-long page rather than
   to split it. An output-limit rule is being read as a content-design rule.

3. **Page boundaries were taken mechanically from the source's top heading
   level**, one level above the real concept boundary, so several upstream
   documents landed in one file and their canonical URLs were buried in body
   prose instead of becoming `resource:` frontmatter.

4. **Heading levels were copied verbatim.** Nothing told the agent that a page is
   a document in its own right, so the source's `##`/`###`/`#####` levels came
   through untouched and most pages have no H1 at all.

5. **No `resource`, no `timestamp`, no `# Citations` anywhere** — three of the
   spec's recommended affordances, unused.

6. **Ad-hoc splitting produced incoherent slugs.** One section was split under
   output pressure into three pages, the first of which is named for the whole
   section while covering only its first third. That is the signature of
   splitting as an accident rather than a plan.

7. **Indexes carry no structure.** Spec §6 explicitly supports multiple `#`
   sections per index; both of ours are a single ungrouped list.

8. **Nothing tells the agent where a source belongs in the bundle.** It invented
   a top-level directory from the document title, which happened to be
   reasonable — but with `md/` holding several documents, that decision needs a
   rule, not luck.

---

## Plan

Every step below is written to hold for a one-page note and a converted book
alike. Where an example is unavoidable it is marked as an example.

### 1. Measure and outline before writing anything

New step in `SKILL.md`, between "Survey the existing wiki" and "Write the content
pages". This is the single change most likely to have prevented the observed
output — the agent never formed a view of the document before writing prose.

- **Measure the source first.** Cheap at any size, and it decides the reading
  strategy in step 2:

  ```bash
  wc -lc <source>
  ```

- **Extract the heading tree, never the body.** Fence-aware, so headings inside
  code blocks do not become phantom pages:

  ```bash
  awk '/^```/{fence=!fence; next} !fence && /^#{1,6} /{print NR": "$0}' <source>
  ```

- **Identify the concept level from the tree.** This is the level at which a
  section is a **self-contained topic** — one thing a reader would look up by
  name. It **varies between branches of one document and between documents**, so
  choose it per branch rather than fixing it once. Signals that mark it:
  - the section carries its own boundary marker — a canonical URL, a source line,
    a byline — indicating it was a separate document upstream;
  - its subsections only make sense underneath it, not on their own;
  - you can describe it in one sentence without the word "and".
- **When the heading tree is thin, absent, or inconsistent** — common in
  converted PDFs — fall back to the document's other structural signals: a table
  of contents, numbered section labels, bold run-in headings, or consistent topic
  breaks in the prose. **If the document genuinely covers one topic, one page is
  the correct answer**; do not manufacture sections to fill a tree.
- **Write the planned page tree** — path and title per page — into the final
  message *before* writing any page, and sanity-check it against the rules below.
- **Check the outline covers the source**: every section at or above the chosen
  level maps to a page or is deliberately folded into one. This is the coverage
  guarantee, and it removes any need to split the source file.

### 2. Choose a reading strategy from the measurement — never assume

New section, the mechanical counterpart to step 1. The current draft's only
guidance is one soft clause — "Read long sources the same way — in ranges" —
which the agent did not follow. Make it a decision with commands attached.

- **Decide from the measurement, not from habit.** A small source may be read
  whole; a large one must not be. Reading a short document in fragments wastes
  calls, and reading a long one whole leaves no room to write the wiki. There is
  no fixed threshold — compare the measured size against what you can hold while
  still writing the pages the outline calls for.
- **Never read a source in full when the outline shows it will not fit alongside
  the writing.** In that case:
  - **Read one section at a time, by line range.** A section runs from its
    heading to the next heading at the *same or higher* level — not the next
    heading of any level, which would stop at the first subsection:

    ```bash
    sed -n '<start>,<end>p' <source>
    ```

  - **Work section by section**: read one range, write its page, move on. Do not
    accumulate several sections before writing.
  - If a single section is still too large to read in one go, that is evidence it
    contains more than one concept — descend a heading level and take its
    children as the unit, rather than reading it in arbitrary pieces.
- **Never split the source into files.** `md/` is read-only, the workspace writes
  through to the host tree, and `/tmp` does not survive the run. Line ranges give
  everything a chunk file would, without an artifact to keep consistent.

### 3. Replace the skill's step 4 with a "One concept per page" section

The load-bearing addition, stated qualitatively.

- **One concept per page.** A page covers exactly one topic that a reader would
  look up by name. If the page's `description` needs an "and" to be truthful, it
  is two concepts and belongs in two pages.
- **Prefer the source's own boundaries.** Where the source marks a section as
  separately authored — its own URL, source line, or byline — that is a concept
  boundary; use it rather than inventing one.
- **A page a reader would only ever want part of is too big.** If someone
  consulting it would reliably skip most of what they loaded, split it.
- **Split along the heading tree, never mid-section.** Never split a table, a
  fenced code block, or a numbered procedure across pages.
- **Splitting creates a directory, not more siblings.** `foo.md` becomes `foo/`
  with an `index.md` and one child per subsection. Never leave both `foo.md` and
  `foo/`. This is what keeps indexes readable as the bundle grows (finding 3).
- **Name every page for what it contains.** If a slug does not tell you the
  page's coverage, it is wrong — a page named for a whole section must not cover
  only part of it.
- **Reference material splits along its own axis**, and each resulting page is
  named for the range it covers: a glossary by letter, an API reference by symbol
  group, a changelog by release.

### 4. Add a "Mirror the source's structure" section

The observed failure is the flat directory, so this gets its own rule — stated in
both directions so it does not license the opposite mistake.

- **The wiki's shape should track the source's own topic hierarchy.** A source
  whose real structure is chapters → topics → sub-topics produces directories,
  not one folder of long files.
- **Do not flatten structure the source has.** A directory holding only leaf
  pages is a smell when its subject has internal structure: ask whether a reader
  would navigate its contents in groups, and if so, those groups are
  subdirectories.
- **Do not manufacture structure the source lacks.** A short or single-topic
  source produces a small, shallow result — in the limit a single page. Nesting a
  thin document into a tree of stubs is the same defect in the other direction,
  and it costs a reader more hops for less content.
- **Every directory gets an `index.md`** — that is what makes depth navigable
  rather than merely deep.
- **Depth is cheap; breadth is not.** When a directory's listing stops being
  scannable at a glance, the fix is a new level, not a longer list.

### 5. Say where a source lands in the bundle, and how runs compose

Currently unspecified; the agent guessed. With `md/` holding several documents
and one run per file in glob order, this needs a rule.

- **A source document maps to the topic it is about, not to its filename.** Name
  its directory for the subject a reader would look for.
- **Check the existing wiki first** (the survey step already in the skill). If a
  prior run created a directory this document belongs inside, nest into it rather
  than opening a sibling. If it overlaps an existing page's topic, update that
  page in place — the idempotency rule already requires this.
- **A source small enough to be one concept becomes one page at the appropriate
  level**, not a directory containing a single page.
- **Never assume you are the first or last run.** Only link to pages that exist
  on disk now, extend the root `index.md` rather than rewriting it, and append to
  `log.md` without disturbing earlier dates. These rules exist already but are
  written as if there were one run; make the multi-run case explicit.

### 6. Add an "Every page starts with an H1" section

Currently absent, and the reason pages open at `##`, `###`, or `#####`.

- **Every content page opens with exactly one H1**, and it matches the page's
  `title` frontmatter. This holds at every depth — a page in a subdirectory is a
  document in its own right, not a fragment of its parent.
- **Re-root the source's headings.** The section that becomes the page becomes
  its H1; its subsections shift up to `##`, `###`, and so on, so the page's
  heading tree starts at the top and is internally consistent. This falls out of
  splitting naturally: when a section is promoted to its own page, its heading is
  promoted with it.
- **Where the source has no heading for the material** — a page derived from an
  unstructured document — write an H1 from the page's `title`.
- **Re-rooting is not a fidelity violation** — see step 7. Heading *text* is
  preserved verbatim; only its level changes.
- Conventional spec headings (`# Citations`, `# Schema`, `# Examples`, §4.2/§8)
  become `##` so the one-H1 rule holds. The heading *name* is what carries the
  convention, and the spec's examples take their title from frontmatter rather
  than an H1, which is why they show these at `#`. **This is the one place the
  plan knowingly diverges from the spec's example formatting** — say so in the
  skill so a future reader does not "fix" it back.

### 7. Clarify that fidelity governs wording, not structure

The fidelity rule and the splitting/re-rooting rules will otherwise appear to
conflict:

> Fidelity governs **wording**, not structure. Moving a section onto its own
> page, changing a heading's level, adding frontmatter, and adding cross-links
> are not fidelity violations. Rewriting, condensing, or paraphrasing the
> source's sentences is.

### 8. Demote "Write in bounded chunks"

Keep the mechanical advice — the failure mode it describes is real — but
subordinate it so it stops reading as licence to grow:

> The chunking below is a workaround for a **tool output limit**. It is not a way
> to build a big page. If a page keeps needing more chunks, that is evidence it
> covers more than one concept — split it per "One concept per page" instead.

### 9. Use the spec's recommended frontmatter and citations

- `resource:` — the canonical URL for the concept **where the source provides
  one**. Some sources carry a per-section URL, some carry one URL for the whole
  document, some carry none; use the most specific available, and omit the field
  when there is none rather than inventing a link.
- `timestamp:` — ISO 8601, taken from the environment (`date -u +%FT%TZ`), never
  from memory.
- `## Citations` — spec §8, numbered, at the bottom of any page whose content
  comes from an external source.
- Tags carry the split's axis, so a tag-based view stays coherent after a page
  becomes a directory: every child of a split page keeps the parent's topic tag.

### 10. Specify index structure at every level

- Every directory, including every new subdirectory, has an `index.md`.
- Only the bundle-root `index.md` carries frontmatter, and only `okf_version`
  (`okf-lint`'s `index-frontmatter` and `index-version-key` are **errors**).
- Group entries under `#` section headings once a listing is long enough that
  groups help — spec §6 supports this and it is the whole progressive-disclosure
  mechanism.
- Every entry's description is the target's `description` frontmatter verbatim,
  so reading an index alone tells an agent what to open.
- Subdirectories are listed as `[Name](/path/to/dir/) — description`.
- **Splitting an existing page means repairing inbound links** in sibling pages
  and parent indexes, and removing the old page. Spell this out under
  idempotency, which currently covers only "update in place".

### 11. Tune `okf/.okflintrc.json`

The one tracked file this touches. Enable what the conventions already require:

| Rule | Now | After | Why |
| --- | --- | --- | --- |
| `recommended-timestamp` | `off` | `error` | Step 9 makes timestamps mandatory; this is why none exist today |
| `timestamp-format` | default warn | `error` | Deterministic, cheap |
| `recommended-title` | default warn | `error` | `AGENTS.md` mandates `title`, and step 6 ties the H1 to it |
| `recommended-description` | `warning` | `error` | `AGENTS.md` mandates it, and indexes depend on it |
| `prefer-absolute-links` | default warn | `error` | `AGENTS.md` mandates bundle-absolute links |
| `tags-type` | default warn | `error` | `AGENTS.md` mandates a YAML list |
| `log-date-order` | default warn | `error` | `AGENTS.md` mandates newest-first |
| `valid-links`, `okf-version-declared` | `error` | unchanged | |
| `recommended-log` | `warning` | unchanged | |

`resource` is deliberately **not** promoted — step 9 allows omitting it when a
source provides no URL, so a rule would fire on legitimate pages.

The skill's "never edit `.okflintrc.json`" instruction stays and stays correct —
it binds the Pi agent at runtime. This is a host-side change to the tracked
config, made here and not by the agent; add one clarifying clause to the skill so
the two do not read as contradictory.

Also update the skill's error/warning triage text, which currently tells the
agent it may ignore warnings on untouched pages — with these promoted to errors,
the first run against an existing wiki will surface real work.

`okf-lint` cannot check any of steps 1–6, so the skill ends with its own
structural self-check (see Verification) rather than treating a clean lint report
as proof the wiki is well shaped.

### Files

| File | Change |
| --- | --- |
| `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md` | Main rewrite (steps 1–10) |
| `okf/.okflintrc.json` | Rule severities (step 11) |

`pi/files/home/.pi/agent/skills/compile-wiki/scripts/lint-okf.sh` is unchanged.

---

## Deliberately out of scope — flagged for a follow-up

Scoped to `SKILL.md` plus the lint config. Both of these limit how much the
rewrite can achieve:

1. **The `type` taxonomy in `AGENTS.md` is chapter-shaped.**
   `Chapter | GlossaryTerm | Section` was written for a wiki of chapter-sized
   pages and quietly argues for exactly the output we are trying to stop. It also
   does not describe most things `md/` might hold — a converted paper, a runbook,
   a changelog. The rewritten skill will map onto the existing three values as
   best it can, but a concept-shaped taxonomy belongs in a follow-up.

2. **One Pi run per source file is the ceiling, and it binds per file.**
   `scripts/compile-wiki.sh` gives each `md/*.md` a single `pi -p` invocation on
   `qwen/qwen3.6-35b-a3b`. A directory of modest documents is unaffected; a
   single large one still has to be read and compiled inside one context. Steps
   1–2 make that far more survivable, but if output on large sources stays
   uneven, the next lever is a two-pass driver — one run writing an outline
   manifest into `okf/`, then one run per outline branch.

---

## Verification

```bash
./scripts/validate-spec.sh      # required: SKILL.md lives under pi/
make lint                       # markdownlint on the rewritten SKILL.md
```

Then a clean recompile. `okf/` is gitignored output **except `.okflintrc.json`,
which is tracked** — so clear the generated content around it rather than
`rm -rf okf`:

```bash
find okf -mindepth 1 -maxdepth 1 ! -name '.okflintrc.json' -exec rm -rf {} +
make wiki
make lint-okf                   # must exit 0 with the promoted severities
```

`okf-lint` cannot see page shape, so check what this plan is actually about.
These are structural assertions, not thresholds:

```bash
# 1. Every directory is navigable
find okf -type d -exec test ! -e '{}/index.md' \; -print          # must print nothing

# 2. Every content page opens with an H1 (prints any page that does not)
find okf -name '*.md' ! -name index.md ! -name log.md -print0 |
  xargs -0 -I{} sh -c 'awk "/^---$/{n++;next} n>=2 && NF {print; exit}" "{}" |
    grep -q "^# " || echo "{}"'

# 3. Exactly one H1 per page (prints any page with more)
find okf -name '*.md' ! -name index.md ! -name log.md -print0 |
  xargs -0 grep -c '^# ' | grep -v ':1$'

# 4. timestamp is written everywhere (resource is optional by design)
grep -rL '^timestamp:' okf --include='*.md' | grep -Ev 'index.md|log.md'
```

**Test the generalisation, not just the sample.** The driver takes a source
folder argument, so compile a scratch folder of deliberately awkward inputs and
confirm the skill adapts rather than pattern-matching the sample:

```bash
./scripts/compile-wiki.sh <scratch-folder>
```

Cover at least:

| Input | Expected behaviour |
| --- | --- |
| A very short single-topic file | One page, not a directory of stubs |
| A file with no headings at all | No invented sections; one page if it is one topic |
| A file whose heading levels skip or restart (typical `marker` output) | Concept level chosen from meaning, not from the level number |
| Two files whose topics overlap | The second run updates or nests — never duplicates |

Then read the result the way a consumer would, which is the check that matters
and cannot be scripted:

- Open `okf/index.md`, then one directory index, then one leaf page. At each hop
  the listing should tell you what to open next without opening anything.
- Pick one leaf page and confirm it is a single concept — its `description` is
  true without an "and", it opens with an H1 matching its `title`, its heading
  tree starts at the top, and its prose matches the source verbatim.
- Confirm the page tree the agent printed in its outline matches what is on disk.

---

## Sources

- [OKF v0.1 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) — vendored as `SPEC.md`; §4.2, §6, §8, §9
- [How the Open Knowledge Format can improve data sharing](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) — Google Cloud, launch post
- [OKF Ecosystem Tools](https://okf.md/tools/) — "one concept per file", split candidates, okflint audit
- [okf.md](https://okf.md/) — spec landing page, v0.1
- [thisismydesign/okf-lint](https://github.com/thisismydesign/okf-lint) — full rule set, severities, exit codes
- [Wiki-Skills gaining traction, now with Google's OKF standard](https://kfchou.github.io/llm-wiki-google-okf/) — flat directories discouraged, tiered indexes
- [kfchou/wiki-skills](https://github.com/kfchou/wiki-skills) — Karpathy-pattern skill set, generated indexes, merge/split skill
- [cablate/llm-atomic-wiki](https://github.com/cablate/llm-atomic-wiki) — atom layer, topic branches, two-layer lint, index-scan ceiling
- [atomicstrata/llm-wiki-compiler](https://github.com/atomicstrata/llm-wiki-compiler) — two-phase extract-then-generate, typed pages
- [chapter42/okf-convert](https://github.com/chapter42/okf-convert) — Markdown→OKF converter, closest analogue
- [scaccogatto/okf-skills](https://github.com/scaccogatto/okf-skills) — Claude Code OKF plugin, log-enforcement hook
- [How to Build Karpathy's LLM Wiki](https://blog.starmorph.com/blog/karpathy-llm-wiki-knowledge-base-guide) — index-first navigation
- [Karpathy's LLM Wiki: A Knowledge Base That Compounds](https://www.aibuilderclub.com/blog/karpathy-llm-wiki) — index is what fails first as a wiki grows
- [How to Build a Knowledge Base for AI Agents: 2026 Guide](https://atlan.com/know/ai-agent/data-for-ai/how-to-build-knowledge-base-for-ai-agents/) — split on major boundaries first, then recurse
