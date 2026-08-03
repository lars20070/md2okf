# Improve the `compile-wiki` skill: one concept per page, nested structure, self-rooted headings

## Context

`pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md` is a first draft. It gets
conformance right — every generated page has parseable frontmatter, a `type`,
bundle-absolute links, and `okf-lint` passes — but it says almost nothing about
**how knowledge should be shaped**, and the output shows it.

One source document (`md/GoogleStyleGuide.md`) compiled into 15 flat pages:

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

**Design direction (set by the repo owner, and consistent with the research
below):** state the rule as *one concept per page*, discourage flat structures,
require an H1 at the top of every page including in subdirectories — and express
all of it **without hard-coded thresholds**. No lines-per-page number, no
target page count, no children-per-directory cap. Numbers of that kind are
unverifiable by the agent, wrong for the next source document, and invite
box-ticking instead of judgement.

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

**So: page shape is a producer convention. It is ours to set, and nobody will
set it for us.** Nothing in `SPEC.md` or `okf-lint` will ever complain about a
2,081-line page.

### 2. The ecosystem convention is "one concept per file" — with split detection as a first-class lint

Two months in, the OKF tool directory (`okf.md/tools`) lists "One concept per
file" and "'Split candidates' detectable via link graph visualization" under file
organization, plus "Hierarchical layout mirrors resource structure". The
community linter `okflint` ships an `audit` mode producing "an X-ray of your base
including broken links, **split candidates**, and stats".

Notably, nobody in the ecosystem publishes a line or word threshold. The
convention that has actually taken hold is qualitative — one concept, one file —
with tooling that *detects* over-broad pages from the link graph rather than
from a size limit. Our linter (`thisismydesign/okf-lint`) has no such rule, so
the judgement has to live in the skill.

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
and the depth absorbs growth), not smaller pages. This directly supports
discouraging flat structures, and it is why splitting a page must always create a
directory with its own `index.md` rather than more siblings in one folder.

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
reference material, but the more durable finding is the *procedure*: "split
first on major boundaries (sections, paragraphs), then recursively split large
sections". The boundary that matters is semantic, and the best available signal
for it is the structure the source's own author already imposed.

That is decisive for this corpus. Verified: in every generated page, the count of
H3 headings exactly equals the count of `*Source: <url>*` lines — **each H3
corresponds to exactly one original Google style-guide page with its own
canonical URL.** The source is a concatenation of separately-authored documents,
and their boundaries survive as headings. The agent should be told to look for
that signal rather than to count lines.

### 6. The closest existing tool solves an easier problem

`chapter42/okf-convert` (Markdown/web → OKF) is the nearest analogue. It maps
**one input file to one concept**, goes deliberately flat, derives `title` from
H1/filename, `description` from an LLM pass or the body's first sentence, and
`timestamp` from file mtime. It never splits a document — which is exactly why it
is the wrong model for a book-length source. What it does that we don't: it
always emits `timestamp`, and it groups indexes by tag rather than as one flat
list.

### 7. `okf-lint` rules we are not using

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
though `AGENTS.md` makes both mandatory. There is no rule for page shape,
heading structure, or nesting, and there never will be — so those checks belong
in the skill's own procedure.

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

3. **Page boundaries were taken mechanically from source H2s**, one level above
   the real concept boundary (finding 5), so six upstream documents landed in one
   file and their canonical URLs were buried in body prose instead of becoming
   `resource:` frontmatter.

4. **Heading levels were copied verbatim.** Nothing told the agent that a page is
   a document in its own right, so the source's `##`/`###`/`#####` levels came
   through untouched and most pages have no H1 at all.

5. **No `resource`, no `timestamp`, no `# Citations` anywhere** — three of the
   spec's recommended affordances, unused.

6. **Ad-hoc splitting produced incoherent slugs.** The word list was split under
   output pressure into `word-list.md` (which actually covers A–G),
   `word-list-h-n.md`, `word-list-o-z.md`. The first name does not say what it
   holds — the signature of splitting as an accident rather than a plan.

7. **Indexes carry no structure.** Spec §6 explicitly supports multiple `#`
   sections per index; both of ours are a single ungrouped list.

---

## Plan

### 1. Add an outline pass before any writing

New step in `SKILL.md`, between "Survey the existing wiki" and "Write the content
pages". This is the single change most likely to have prevented the current
output — the agent never formed a view of the whole document before it started
writing prose.

- Read the source's **heading tree only** first, not its body:
  `grep -n '^#\{1,6\} ' <source>`
- From that tree, identify the level at which each section is a **self-contained
  topic** — one thing a reader would look up by name. Tell the agent what signals
  mark that level, rather than naming a level:
  - the section carries its own canonical URL, byline, or "Source:" line — it was
    a separate document upstream;
  - its subsections only make sense underneath it, not on their own;
  - you can describe it in one sentence without the word "and".
- Write the planned page tree — path and title per page — into the final message
  **before** writing any page, and sanity-check it against the rules below.
- Warn that headings inside fenced code blocks and example blocks are not real
  sections (the source contains several, e.g. `# Several lines of code are
  omitted here.`); verify a heading is real before it becomes a page.

### 2. Replace step 4 with a "One concept per page" section

The load-bearing addition, stated qualitatively.

- **One concept per page.** A page covers exactly one topic that a reader would
  look up by name. If the page's `description` needs an "and" to be truthful, it
  is two concepts and belongs in two pages.
- **Prefer the source's own boundaries.** Where the source marks a section as a
  separate document — its own URL, its own source line — that is a concept
  boundary; use it rather than inventing one.
- **A page a reader would only ever want part of is too big.** If someone
  consulting it would reliably skip most of what they loaded, split it.
- **Split along the heading tree, never mid-section.** Never split a table, a
  fenced code block, or a numbered procedure across pages.
- **Splitting creates a directory, not more siblings.** `foo.md` becomes `foo/`
  with an `index.md` and one child per subsection. Never leave both `foo.md` and
  `foo/`. This is what keeps indexes readable as the wiki grows (finding 3).
- **Name every page for what it contains.** If a slug does not tell you the
  page's coverage, it is wrong — `word-list.md` must not mean "A–G".
- **Reference lists split along their own axis.** A glossary or word list splits
  by letter, an API reference by symbol group; each resulting page is named for
  the range it covers.

### 3. Add a "Mirror the source's depth — never go flat" section

The user-visible failure is the flat directory, so it gets its own rule rather
than a clause inside another one:

- The wiki's directory depth should **track the source's topic hierarchy**. A
  source whose real structure is chapters → topics → sub-topics produces
  directories, not one folder of long files.
- **A directory holding only leaf pages is a smell** when its subject has
  internal structure. Ask whether a reader would navigate its contents in groups;
  if so, those groups are subdirectories.
- **Every directory gets an `index.md`** — that is what makes depth navigable
  rather than merely deep.
- **Depth is cheap; breadth is not.** When a directory's listing stops being
  scannable at a glance, the fix is a new level, not a longer list.

### 4. Add a "Every page starts with an H1" section

Currently absent, and the reason pages open at `##`, `###`, or `#####`.

- **Every content page opens with exactly one H1**, and it matches the page's
  `title` frontmatter. This holds at every depth — a page in a subdirectory is a
  document in its own right, not a fragment of its parent.
- **Re-root the source's headings.** The section that becomes the page becomes
  its H1; its subsections shift up to `##`, `###`, and so on, so the page's
  heading tree starts at the top and is internally consistent. This falls out of
  splitting naturally: when a section is promoted to its own page, its heading is
  promoted with it.
- **Re-rooting is not a fidelity violation** — see step 5. Heading *text* is
  preserved verbatim; only its level changes.
- Conventional spec headings (`# Citations`, `# Schema`, `# Examples`, §4.2/§8)
  become `##` so the one-H1 rule holds. The heading *name* is what carries the
  convention, and the spec's examples take their title from frontmatter rather
  than an H1, which is why they show these at `#`. **Flagging this as the one
  place the plan knowingly diverges from the spec's example formatting** — say so
  in the skill so a future reader does not "fix" it back.

### 5. Clarify that fidelity governs wording, not structure

The fidelity rule and the splitting/re-rooting rules will otherwise appear to
conflict:

> Fidelity governs **wording**, not structure. Moving a section onto its own
> page, changing a heading's level, adding frontmatter, and adding cross-links
> are not fidelity violations. Rewriting, condensing, or paraphrasing the
> source's sentences is.

### 6. Demote "Write in bounded chunks"

Keep the mechanical advice — the failure mode it describes is real — but
subordinate it so it stops reading as licence to grow:

> The chunking below is a workaround for a **tool output limit**. It is not a way
> to build a big page. If a page keeps needing more chunks, that is evidence it
> covers more than one concept — split it per "One concept per page" instead.

### 7. Use the spec's recommended frontmatter and citations

- `resource:` — the section's canonical URL where the source gives one. In this
  corpus that is the `*Source: <url>*` line the current output buries in the
  body; it belongs in frontmatter.
- `timestamp:` — ISO 8601, taken from the environment (`date -u +%FT%TZ`), never
  from memory.
- `## Citations` — spec §8, numbered, at the bottom of any page whose content
  comes from an external source.
- Tags carry the split's axis, so a tag-based view stays coherent after a page
  becomes a directory (every child of `word-list/` still tagged `word-list`).

### 8. Specify index structure at every level

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

### 9. Tune `okf/.okflintrc.json`

The one tracked file this touches. Enable what the conventions already require:

| Rule | Now | After | Why |
| --- | --- | --- | --- |
| `recommended-timestamp` | `off` | `error` | Step 7 makes timestamps mandatory; this is why none exist today |
| `timestamp-format` | default warn | `error` | Deterministic, cheap |
| `recommended-title` | default warn | `error` | `AGENTS.md` mandates `title`, and step 4 ties the H1 to it |
| `recommended-description` | `warning` | `error` | `AGENTS.md` mandates it, and indexes depend on it |
| `prefer-absolute-links` | default warn | `error` | `AGENTS.md` mandates bundle-absolute links |
| `tags-type` | default warn | `error` | `AGENTS.md` mandates a YAML list |
| `log-date-order` | default warn | `error` | `AGENTS.md` mandates newest-first |
| `valid-links`, `okf-version-declared` | `error` | unchanged | |
| `recommended-log` | `warning` | unchanged | |

The skill's "never edit `.okflintrc.json`" instruction stays and stays correct —
it binds the Pi agent at runtime. This is a host-side change to the tracked
config, made here and not by the agent; add one clarifying clause to the skill so
the two do not read as contradictory.

Also update the skill's error/warning triage text, which currently tells the
agent it may ignore warnings on untouched pages — with these promoted to errors,
the first run against an existing wiki will surface real work.

`okf-lint` cannot check any of steps 2–4, so the skill ends with its own
structural self-check (see Verification) rather than treating a clean lint report
as proof the wiki is well shaped.

### Files

| File | Change |
| --- | --- |
| `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md` | Main rewrite (steps 1–8) |
| `okf/.okflintrc.json` | Rule severities (step 9) |

`pi/files/home/.pi/agent/skills/compile-wiki/scripts/lint-okf.sh` is unchanged.

---

## Deliberately out of scope — flagged for a follow-up

Scoped to `SKILL.md` plus the lint config. Both of these limit how much the
rewrite can achieve:

1. **The `type` taxonomy in `AGENTS.md` is chapter-shaped.**
   `Chapter | GlossaryTerm | Section` was written for a wiki of chapter-sized
   pages and quietly argues for exactly the output we are trying to stop. The
   rewritten skill will use `Section` for split child pages and `GlossaryTerm`
   for glossary entries — workable, but `Chapter` will end up on pages that are
   not chapters. A concept-shaped taxonomy belongs in a follow-up.

2. **One Pi run per document is still the ceiling.** `scripts/compile-wiki.sh`
   feeds the whole source through a single `pi -p` invocation on
   `qwen/qwen3.6-35b-a3b`. The outline pass makes that run far more likely to
   produce a good tree, but it still has to read a book and write the whole
   subtree within one context. If output is still uneven afterwards, the next
   lever is a two-pass driver — one run writing an outline manifest into `okf/`,
   then one run per outline branch.

---

## Verification

```bash
./scripts/validate-spec.sh      # required: SKILL.md lives under pi/
make lint                       # markdownlint on the rewritten SKILL.md
```

Then a clean recompile — `okf/` is gitignored output, so regenerate rather than
patch:

```bash
rm -rf okf/google-style-guide
make wiki
make lint-okf                   # must exit 0 with the promoted severities
```

`okf-lint` cannot see page shape, so check the four things this plan is actually
about. These are structural assertions, not thresholds:

```bash
# 1. Not flat: subdirectories exist below the top level
find okf -mindepth 2 -type d

# 2. Every directory is navigable
find okf -type d -exec test ! -e '{}/index.md' \; -print          # must print nothing

# 3. Every content page opens with an H1 (prints any page that does not)
find okf -name '*.md' ! -name index.md ! -name log.md -print0 |
  xargs -0 -I{} sh -c 'awk "/^---$/{n++;next} n>=2 && NF {print; exit}" "{}" |
    grep -q "^# " || echo "{}"'

# 4. Exactly one H1 per page (prints any page with more)
find okf -name '*.md' ! -name index.md ! -name log.md -print0 |
  xargs -0 grep -c '^# ' | grep -v ':1$'

# 5. The spec's recommended fields are actually written
grep -rL '^resource:'  okf --include='*.md' | grep -Ev 'index.md|log.md'
grep -rL '^timestamp:' okf --include='*.md' | grep -Ev 'index.md|log.md'
```

Then read the result the way a consumer would, which is the check that matters
and cannot be scripted:

- Open `okf/index.md`, then one directory index, then one leaf page. At each hop
  the listing should tell you what to open next without opening anything.
- Pick one leaf page and confirm it is a single concept — its `description` is
  true without an "and", it opens with an H1 matching its `title`, its heading
  tree starts at the top, its prose matches the source verbatim, and it carries
  `resource:` plus a `## Citations` block pointing at the upstream URL.
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
