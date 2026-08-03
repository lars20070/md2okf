# Improve the `compile-wiki` skill: page budgets, split rules, nested indexes

## Context

`pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md` is a first draft. It gets
conformance right — every generated page has parseable frontmatter, a `type`,
bundle-absolute links, and `okf-lint` passes — but it says almost nothing about
**how knowledge should be shaped**, and the output shows it.

One 16,514-line source (`md/GoogleStyleGuide.md`) compiled into 15 flat pages
totalling 12,552 lines:

| Page | Lines |
| --- | --- |
| `computer-interfaces.md` | 2,081 |
| `whats-new.md` | 1,540 |
| `word-list.md` | 1,514 |
| `general-principles.md` | 1,275 |
| `word-list-o-z.md` | 1,205 |
| `punctuation.md` | 1,075 |
| … 9 more | 105–1,040 |

Zero subdirectories. The root index has one entry; the one directory index is a
flat 15-item list. So an agent navigating this wiki gets one hop of progressive
disclosure and then hits a 2,000-line wall — the opposite of what the format is
for.

This plan rewrites `SKILL.md` to make page shape an explicit, checkable part of
the procedure, and tunes `okf/.okflintrc.json` so the linter catches more of what
the conventions require.

---

## Research findings

### 1. OKF itself deliberately declines to specify page size

`SPEC.md` (v0.1, 2026-06-12) requires exactly one thing of a concept: a non-empty
`type`. §9 Conformance lists three rules, none about size. The only shaping
guidance in the whole spec is §4.2:

> Producers SHOULD favor structural markdown — headings, lists, tables, fenced
> code blocks — over freeform prose, since structure aids both human reading and
> agent retrieval.

and §6, which frames `index.md` as existing for **progressive disclosure** —
"letting a human or agent see what is available before opening individual
documents." Google Cloud's launch post says the same and no more: "Each concept
is one file", "the file path serves as the concept's identity". It gives no
granularity rule and explicitly leaves the content model to producers.

**So: page size is a producer convention. It is ours to set, and nobody will set
it for us.** Nothing in `SPEC.md` or `okf-lint` will ever complain about a
2,081-line page.

### 2. The ecosystem convention that has emerged is "one concept per file" — with split detection as a first-class lint

Two months in, the OKF tool directory (`okf.md/tools`) lists "One concept per
file" and "'Split candidates' detectable via link graph visualization" under file
organization, and "Hierarchical layout mirrors resource structure". The
community linter `okflint` ships an `audit` mode whose output is "an X-ray of
your base including broken links, **split candidates**, and stats".

That is the strongest signal available: over-long pages are a recognised OKF
defect that other producers build tooling to detect. Our linter
(`thisismydesign/okf-lint`) has no such rule, so the check has to live in the
skill.

### 3. The Karpathy LLM-wiki lineage: the binding constraint is page *count*, not page size

- Karpathy's own wiki matured at ~100 articles / ~400,000 words — roughly
  4,000 words per article. That is a wiki of *synthesised* prose, not a verbatim
  compile, so it is a weak precedent for us.
- The operative scaling number is about the index, and it is consistent across
  sources: at **~150–200 pages** an agent can no longer hold the wiki in context;
  a master index of one-line summaries plus selective loading extends practical
  capacity to **300+ pages**. `cablate/llm-atomic-wiki` states the same ceiling
  from the other side: "Past that [~200 wiki pages], `index.md` scans degrade and
  you need vector search alongside."

**So: a fully atomic wiki (one page per word-list term ≈ 1,500 pages) would break
navigation.** The target is the low hundreds of pages, which sets a *floor* on
page size just as retrieval sets a ceiling.

### 4. Flat directories are explicitly discouraged; indexes should be tiered

`kfchou/wiki-skills` — the most-referenced Karpathy-pattern skill set, and
OKF-aware since the spec landed:

> a flat-directory containing all wiki pages should be discouraged to facilitate
> the ease of index generation

> one methodology for structuring subdirectories is to divide wiki docs among
> **high level, commonly used, non-overlapping concepts**

and on disclosure:

> token-budgeted, tiered indexes — L0 (~200 tokens, every session), L1 (~1–2K,
> the index at session start), L2 (~2–5K) — instead of one flat index

`llm-atomic-wiki` uses "one folder at repo root per topic", with branches running
23–101 pages each. Both also split lint into a deterministic layer (broken links,
orphans, format) and a semantic layer (contradictions, stale claims).

### 5. Retrieval evidence puts the sweet spot at 400–512 tokens

Current chunking guidance converges on 300–500 tokens for dense reference
material, with **400–512 tokens performing best across most use cases**, and the
splitting heuristic "split first on major boundaries (sections, paragraphs), then
recursively split large sections". 400–512 tokens ≈ 300–400 words ≈ 40–60 lines
of plain prose.

Taken literally that is far too aggressive for us: our content is tables, code
fences and numbered procedures, which cost lines cheaply, and 60-line pages
would produce the 1,500-page explosion that finding 3 rules out. The usable
reading is **one page = one retrievable idea**, sized so that loading it whole is
never wasteful.

### 6. The closest existing tool solves an easier problem

`chapter42/okf-convert` (Markdown/web → OKF, deterministic Python + optional LLM
enrichment) is the nearest analogue. It maps **one input file to one concept**,
goes deliberately flat, derives `title` from H1/filename, `description` from an
LLM pass or the body's first sentence, and `timestamp` from file mtime. It never
splits a document — which is exactly why it is the wrong model for a book-length
source. What it does do that we don't: it always emits `timestamp`, and it
generates indexes grouped by tag rather than as one flat list.

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

Our `okf/.okflintrc.json` configures five rules and turns
`recommended-timestamp` **off** — which is why not one generated page carries a
timestamp. `prefer-absolute-links` and `recommended-title` are left at default
warning even though `AGENTS.md` makes both mandatory. There is no page-length
rule and there never will be, so the budget must be self-checked with `wc -l`.

---

## Diagnosis: why the output came out this shape

1. **The skill has no shaping instruction.** Step 4 says "Write the content
   pages, organised into directories by topic" — no budget, no split axis, no
   depth guidance, no page-count expectation. "Organised into directories by
   topic" is satisfied by one directory, and that is what it got.

2. **"Write in bounded chunks" teaches the wrong lesson.** It is a correct
   workaround for a tool-output limit — build a long page with `write` then
   repeated `edit`. But it is the only place in the skill that discusses page
   length, and it tells the agent how to *grow* an over-long page rather than to
   split it. It is an output-limit rule being read as a content-design rule.

3. **Page boundaries were taken mechanically from source H2s.** The natural
   concept boundary is one level down. Verified: in every generated page, the
   count of H3 headings exactly equals the count of `*Source: <url>*` lines —
   each H3 corresponds to exactly one original Google style-guide page with its
   own canonical URL. There are ~63 such sections in the source. Those URLs are
   the perfect `resource:` value and they are currently buried in body prose.

4. **No `resource`, no `timestamp`, no `# Citations` anywhere** — three of the
   spec's five recommended affordances, unused.

5. **Ad-hoc splitting produced incoherent slugs.** The agent split the word list
   under output pressure and got `word-list.md` (which actually covers A–G),
   `word-list-h-n.md`, `word-list-o-z.md`. The first name does not say what it
   holds. That is the signature of splitting as an accident rather than a plan.

6. **Indexes carry no structure.** Spec §6 explicitly supports multiple `#`
   sections per index; both of ours are a single ungrouped list.

---

## Decision needed: the page budget

You asked what the research says before choosing. It says: **the ceiling comes
from retrieval (~400–512 tokens is optimal, so pages should be small), the floor
comes from navigation (~200–300 pages before the index stops working, so pages
cannot be tiny).** For this source those two constraints intersect cleanly.

**Recommended — one page per source H3 section:**

- Target **120–250 lines** of body; **soft ceiling 400 lines**.
- Yields **~60–90 pages** for `GoogleStyleGuide.md`, well inside the navigation
  budget, with room for several more source documents before the index degrades.
- Every page maps to exactly one original Google style-guide page, so every page
  gets a real `resource:` URL and a meaningful `# Citations` entry — the concept
  boundary is inherited from the source's own authorship, not invented.
- Sections that exceed 400 lines (`command-line-syntax`, `ui-elements`,
  `word-list`, `whats-new`) recurse one level into a subdirectory.

```
okf/google-style-guide/
├── index.md
├── computer-interfaces/
│   ├── index.md
│   ├── api-reference-comments.md        (~230)
│   ├── code-in-text.md                  (~280)
│   ├── code-samples.md                  (~115)
│   ├── command-line-syntax/             (was ~500 → split)
│   │   ├── index.md
│   │   ├── format-a-command.md
│   │   ├── optional-arguments.md
│   │   └── …
│   └── ui-elements/…
└── word-list/
    ├── index.md
    └── a.md, b.md, c.md, …
```

The alternative — fully atomic, one page per H4 / per word-list term — is
rejected on finding 3: ~1,500 pages puts the wiki past every documented index
limit, and `okf-lint` gives no help navigating it.

**If you disagree, the numbers in "Rewrite `SKILL.md`" §2 are the only thing that
changes; the rest of the plan holds.**

---

## Plan

### 0. Copy this plan into the repo

Write it to `.claude/plans/improve-compile-wiki-skill.md` alongside
`remove-container-runtime.md`, research findings included.

### 1. Rewrite `SKILL.md`: add an outline pass before any writing

New step between "Survey the existing wiki" and "Write the content pages". This
is the single change most likely to have prevented the current output — the
agent never formed a view of the whole document before it started writing prose.

- Read the source's **heading tree only** first, not its body:
  `grep -n '^#\{1,4\} ' <source>`
- Choose the concept level: the heading level at which each section is one
  self-contained topic (for a book-length source, typically H3, not H2).
- Write the planned page tree — path, title, estimated line count — as a plain
  list in the final message, and check it against the budget **before** writing
  any page.
- If a planned page exceeds the ceiling, recurse before writing, not after.
- Warn explicitly that headings inside fenced code blocks and example blocks are
  not real sections (the source has several, e.g. `# Several lines of code are
  omitted here.` at line 14396) — verify a heading is real before making it a
  page.

### 2. Rewrite `SKILL.md`: add a "Page size and splitting" section

The load-bearing addition. Replace the current step-4 half-sentence with:

- **Target 120–250 body lines per page. Soft ceiling 400.** A page over the
  ceiling must be split before the run ends.
- **Floor: do not create a page under ~20 lines.** Fold it into its parent index
  or a sibling.
- **Split on the next heading level down, never mid-section.** Never split a
  table, a fenced code block, or a numbered procedure across pages.
- **Splitting turns the page into a directory.** `foo.md` becomes `foo/` with an
  `index.md` and one child per subsection. Never leave both `foo.md` and `foo/`.
- **Name every page for what it contains.** `word-list/a.md`, not `word-list.md`
  meaning A–G. If a slug does not tell you its coverage, it is wrong.
- **Glossaries and word lists split by letter**, one page per letter; merge
  adjacent letters only when a letter has fewer than ~20 entries, and name the
  result for the range (`word-list/x-z.md`).
- **Keep directories under ~30 children**; past that, add a level.
- **Self-check before finishing**, since `okf-lint` has no length rule:
  ```bash
  find okf -name '*.md' -not -name 'index.md' -not -name 'log.md' \
    -exec wc -l {} + | sort -rn | head -20
  ```

### 3. Rewrite `SKILL.md`: demote "Write in bounded chunks"

Keep the mechanical advice — it is true and the failure mode it describes is
real — but subordinate it to the budget so it stops reading as licence to grow:

> The chunking below is a workaround for a **tool output limit**, not a way to
> build a big page. If a page needs more than about three `write`/`edit` calls,
> it is too big — split it per "Page size and splitting" instead.

### 4. Rewrite `SKILL.md`: clarify that fidelity governs wording, not boundaries

The fidelity rule and the splitting rule will otherwise appear to conflict. State
directly:

> Fidelity governs **wording**, not page boundaries. Moving a section onto its
> own page, adding frontmatter, adding headings, and adding cross-links are not
> fidelity violations. Rewriting, condensing, or paraphrasing the source's
> sentences is.

### 5. Rewrite `SKILL.md`: use the spec's recommended frontmatter and citations

- `resource:` — the source section's canonical URL when it has one. In this
  corpus that is the `*Source: <url>*` line the current output buries in the
  body; it belongs in frontmatter.
- `timestamp:` — ISO 8601, from the environment: `date -u +%FT%TZ`.
- `# Citations` — spec §8, numbered, at the bottom of any page whose content
  comes from an external source.
- Tags carry the split's axis so a tag-based view stays coherent across a split
  (e.g. every `word-list/*` page tagged `word-list`).

### 6. Rewrite `SKILL.md`: specify index structure at every level

- Every directory, including every new subdirectory, gets an `index.md`.
- Only the bundle-root `index.md` carries frontmatter, and only `okf_version`
  (`okf-lint` `index-frontmatter` / `index-version-key` are **errors**).
- Group entries under `#` section headings when a directory has more than ~10
  children — spec §6 supports this and it is the whole progressive-disclosure
  mechanism.
- Every entry's description comes from the target's `description` frontmatter, so
  an index read alone tells an agent what to open.
- Subdirectories are listed as `[Name](/path/to/dir/) — description`.
- Splitting an existing page means **repairing inbound links** in sibling pages
  and parent indexes, and removing the old page — spell this out under
  idempotency, which currently only covers "update in place".

### 7. Tune `okf/.okflintrc.json`

The one tracked file this touches. Enable what the conventions already require:

| Rule | Now | After | Why |
| --- | --- | --- | --- |
| `recommended-timestamp` | `off` | `error` | Step 5 makes timestamps mandatory; this is why none exist today |
| `timestamp-format` | default warn | `error` | Deterministic, cheap |
| `recommended-title` | default warn | `error` | `AGENTS.md` mandates `title` |
| `recommended-description` | `warning` | `error` | `AGENTS.md` mandates it, and indexes depend on it |
| `prefer-absolute-links` | default warn | `error` | `AGENTS.md` mandates bundle-absolute links |
| `tags-type` | default warn | `error` | `AGENTS.md` mandates a YAML list |
| `log-date-order` | default warn | `error` | `AGENTS.md` mandates newest-first |
| `valid-links`, `okf-version-declared` | `error` | unchanged | |
| `recommended-log` | `warning` | unchanged | |

The skill's "never edit `.okflintrc.json`" instruction stays and stays correct —
it binds the Pi agent at runtime. This is a host-side change to the tracked
config, made here and not by the agent. Add one clarifying clause to the skill so
the two do not read as contradictory.

Also update the skill's error/warning triage text, which currently tells the
agent that warnings on untouched pages can be ignored — with these promoted to
errors, the first run against the existing wiki will surface real work.

### Files

| File | Change |
| --- | --- |
| `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md` | Main rewrite (steps 1–6) |
| `okf/.okflintrc.json` | Rule severities (step 7) |
| `.claude/plans/improve-compile-wiki-skill.md` | New — this plan (step 0) |

`pi/files/home/.pi/agent/skills/compile-wiki/scripts/lint-okf.sh` is unchanged.

---

## Deliberately out of scope — flagged for a follow-up

You scoped this to `SKILL.md` plus the lint config, so these are not in the plan,
but both limit how much the rewrite can achieve:

1. **The `type` taxonomy in `AGENTS.md` is chapter-shaped.**
   `Chapter | GlossaryTerm | Section` was written for a wiki of chapter-sized
   pages and quietly argues for exactly the output we are trying to stop. The
   rewritten skill will use `Section` for split child pages and `GlossaryTerm`
   for word-list entries — workable, but "Chapter" will end up on pages that are
   not chapters. A concept-shaped taxonomy belongs in a follow-up.

2. **One Pi run per document is still the ceiling.** `scripts/compile-wiki.sh`
   feeds all 16,514 lines through a single `pi -p` invocation on
   `qwen/qwen3.6-35b-a3b`. The outline pass and the split budget make that run
   far more likely to produce a good tree, but the run still has to read a book
   and write ~80 pages within one context. If output quality is still uneven
   after this change, the next lever is a two-pass driver — one run that writes
   an outline manifest into `okf/`, then one run per outline branch.

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

Check the shape, not just conformance:

```bash
# page count in the navigable range (~60–90 expected)
find okf -name '*.md' -not -name index.md -not -name log.md | wc -l

# no page over the 400-line ceiling
find okf -name '*.md' -not -name index.md -not -name log.md \
  -exec wc -l {} + | sort -rn | head -10

# subdirectories exist, and every directory has an index
find okf -type d
find okf -type d -exec test ! -e '{}/index.md' \; -print   # must print nothing

# the spec's recommended fields are actually being written
grep -rL '^resource:' okf --include='*.md' | grep -v index.md | grep -v log.md
grep -rL '^timestamp:' okf --include='*.md' | grep -v index.md | grep -v log.md
```

Spot-check one deep page (`okf/google-style-guide/computer-interfaces/api-reference-comments.md`)
against the source region it came from: prose verbatim, `resource:` pointing at
`https://developers.google.com/style/api-reference-comments`, a `# Citations`
block, and links to its siblings.

---

## Sources

- [OKF v0.1 specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) — vendored as `SPEC.md`; §4.2, §6, §8, §9
- [How the Open Knowledge Format can improve data sharing](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) — Google Cloud, launch post
- [OKF Ecosystem Tools](https://okf.md/tools/) — "one concept per file", split candidates, okflint audit
- [okf.md](https://okf.md/) — spec landing page, v0.1
- [thisismydesign/okf-lint](https://github.com/thisismydesign/okf-lint) — full rule set, severities, exit codes
- [Wiki-Skills gaining traction, now with Google's OKF standard](https://kfchou.github.io/llm-wiki-google-okf/) — flat directories discouraged, tiered L0/L1/L2 indexes
- [kfchou/wiki-skills](https://github.com/kfchou/wiki-skills) — Karpathy-pattern skill set, generated indexes, merge/split skill
- [cablate/llm-atomic-wiki](https://github.com/cablate/llm-atomic-wiki) — atom layer, topic branches, two-layer lint, ~200-page index ceiling
- [atomicstrata/llm-wiki-compiler](https://github.com/atomicstrata/llm-wiki-compiler) — two-phase extract-then-generate, typed pages, prompt budget
- [chapter42/okf-convert](https://github.com/chapter42/okf-convert) — Markdown→OKF converter, closest analogue
- [scaccogatto/okf-skills](https://github.com/scaccogatto/okf-skills) — Claude Code OKF plugin, log-enforcement hook
- [How to Build Karpathy's LLM Wiki](https://blog.starmorph.com/blog/karpathy-llm-wiki-knowledge-base-guide) — ~100 articles/400k words, index-first navigation
- [Karpathy's LLM Wiki: A Knowledge Base That Compounds](https://www.aibuilderclub.com/blog/karpathy-llm-wiki) — 150–200 page context limit, 300+ with a master index
- [How to Build a Knowledge Base for AI Agents: 2026 Guide](https://atlan.com/know/ai-agent/data-for-ai/how-to-build-knowledge-base-for-ai-agents/) — 300–500 token chunks, 400–512 optimum, recursive boundary splitting
