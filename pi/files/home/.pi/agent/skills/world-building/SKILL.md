---
name: worldbuilding-wiki
description: Construct and maintain a fictional-world knowledge base as a conformant Open Knowledge Format (OKF) v0.1 bundle — a git-backed tree of markdown concepts — that keeps a world internally consistent across many stories, and check new drafts against that canon. Use this skill whenever the user mentions a story bible, series bible, worldbuilding wiki, canon, continuity, lore database, shared universe, or OKF bundle, or wants to track characters/locations/factions/timelines across multiple novels or short stories — and also when they ask you to write, review, or continue a story set in an existing world, since the first job there is loading and respecting canon.
---

# Worldbuilding Wiki (OKF v0.1)

Build a fictional world's canon as an **OKF knowledge bundle**: a directory of markdown concepts with YAML frontmatter, cross-linked with standard markdown links, readable by a human with `cat` and by an agent without an SDK.

## The core idea

Professional continuity operations (Lucasfilm's Holocron, Sanderson's Dragonsteel wiki, TV writers' room bibles) converge on three primitives:

1. **A single source of truth** — one concept per entity, referenced everywhere, redefined nowhere.
2. **A named owner or gate** — one person or review step decides what becomes canon.
3. **Explicit canon tiers** — draft vs. hard canon vs. retconned is a field, not a vibe.

OKF supplies the container for all three, and the discipline it imposes happens to be exactly what continuity needs: every document self-describes its `type`, relationships are explicit links, claims carry citations, and the whole bundle diffs cleanly in git.

Make as many checks as possible *deterministic*. Language models are unreliable at long-range recall — which is why canon must live in structured frontmatter an agent looks up, not prose it must remember. Reserve semantic judgment for what queries cannot express.

## OKF conformance: the rules that actually bind

A bundle conforms to OKF v0.1 if, and only if:

1. Every non-reserved `.md` file has a parseable YAML frontmatter block.
2. Every frontmatter block has a non-empty `type`.
3. `index.md` and `log.md`, where present, follow their defined structures.

Everything else in the spec is soft guidance. Do not invent additional hard constraints and do not build a validator that rejects bundles for anything beyond these three, since consumers are required to be permissive.

Four consequences worth internalizing before you write a single file:

- **The concept ID is the file path minus `.md`.** `characters/mara-thorne.md` *is* `characters/mara-thorne`. Do not add an `id:` field — it would be a second source of truth for identity, which is the exact failure this whole system exists to prevent. Paths are therefore stable identifiers: change `title` to rename something, never the filename.
- **`index.md` and `log.md` are reserved at every level.** An in-world location called "Log" or a story titled "Index" cannot use those filenames. Disambiguate (`locations/log-the-settlement.md`) and set `title` accordingly.
- **Links are standard markdown, not wikilinks.** Prefer bundle-relative form beginning with `/`: `[Mara Thorne](/characters/mara-thorne.md)`. In Obsidian, turn off "Use [[Wikilinks]]" and set new-link format to absolute path, or the vault will silently emit non-conformant links.
- **Broken links are legal.** The spec says a link to a nonexistent concept "may simply represent not-yet-written knowledge." So a dangling link is a *signal*, not an error — treat it as a worldbuilding to-do, and never let a validator fail a build over one.

## Before building: interview

Do not scaffold blind. Establish:

- **Scale** — one novel or a twenty-book universe? Small projects need five concept types, not twenty.
- **Editors** — solo, small team, agents in the loop? This decides whether you need a git PR gate.
- **Existing material** — if prose already exists, canon must be *extracted* from it (see "Retrofitting"), not invented.
- **Interoperability** — is the bundle going to be consumed by other tools or handed to another organization? If yes, conformance matters strictly and you should avoid exotic extension keys. If it is only ever read by this team, extensions are cheap.

State the plan and confirm before writing files. The wrong ontology is expensive to undo.

## Bundle structure

```
world/
├── index.md                  # bundle root index; carries okf_version
├── log.md                    # chronological history of canon changes
├── characters/
│   ├── index.md
│   └── mara-thorne.md
├── locations/
├── factions/
├── items/
├── events/                   # one concept per timeline event
├── rules/                    # magic/tech/physical invariants
├── stories/                  # one concept per novel or story
│   ├── index.md
│   └── drafts/               # work in progress
├── continuity/
│   ├── index.md
│   ├── open-questions.md     # undecided canon
│   └── contradictions.md     # known unresolved tensions
├── decisions/                # canon decision records, incl. retcons
└── references/               # mirrored external source material, if any
```

Omit directories the world does not need yet — an empty folder is an invitation to busywork. Filenames are kebab-case, since they are the concept IDs.

Note that `continuity/contradictions.md` is a *concept* (it needs frontmatter and a `type`), not a reserved log file. `log.md` has a fixed date-grouped format and a different job: recording what changed in the bundle, not what is inconsistent in the world.

## Concept frontmatter

`type` is the only required field. Use descriptive, self-explanatory values — the spec deliberately has no registry, and consumers must tolerate unknown types:

`Character`, `Location`, `Faction`, `Item`, `Event`, `World Rule`, `Story`, `Canon Decision`, `Register`.

Layer OKF's recommended fields on top (`title`, `description`, `tags`, `timestamp`, and `resource` where a real URI exists), then add the continuity extensions. OKF §4.1 explicitly permits producer-defined keys and requires consumers to preserve them, so these are conformant:

- `canon:` — `hard | soft | draft | non-canon | retconned`
- `established_in:` — link to the story concept that made this canon
- `provenance:` — `human | ai-proposed | ai-approved`

Two traps: `timestamp` is the ISO 8601 real-world last-modified time, never an in-world date — keep those in separate fields like `in_world_date`. And `resource` is for a canonical URI of an underlying asset (a published story's URL, say); leave it out entirely for the abstract concepts that make up most of a fictional world.

**Character**
```yaml
---
type: Character
title: "Mara Thorne"
description: "Grey Warden of Ostreve; POV of The Drowned City."
tags: [ebb-court, ostreve, pov-character]
timestamp: 2026-08-16T10:00:00Z
canon: hard
status: alive              # alive | dead | unknown
aliases: ["The Grey Warden"]
birth_date: "742 TR"       # in-world
death_date:
eye_color: grey
home: /locations/ostreve.md
faction: [/factions/ebb-court.md]
established_in: /stories/the-drowned-city.md
provenance: human
---
```

**Event** — `sort_key` is a plain number so chronology sorts reliably whatever the in-world calendar does.
```yaml
---
type: Event
title: "The Breaking of the Bells"
description: "The night the Drowned Abbey's bells were silenced."
tags: [tide-war]
timestamp: 2026-08-16T10:00:00Z
canon: hard
in_world_date: "368 TR"
sort_key: 368.0
location: /locations/drowned-abbey.md
participants: [/characters/mara-thorne.md]
established_in: /stories/the-drowned-city.md
provenance: human
---
```

**World Rule** — the invariants that must never be contradicted.
```yaml
---
type: World Rule
title: "Tide-magic requires saltwater contact"
description: "No tide-working is possible without skin contact with seawater."
tags: [magic]
timestamp: 2026-08-16T10:00:00Z
canon: hard
invariant: true
established_in: /stories/the-drowned-city.md
provenance: human
---
```

**Story** — the concept that *sources* other concepts.
```yaml
---
type: Story
title: "The Drowned City"
description: "Novel. Mara returns to Ostreve as the Ebb Court fractures."
resource: https://example.com/books/the-drowned-city
tags: [novel, tide-war]
timestamp: 2026-08-16T10:00:00Z
canon: hard
status: published         # draft | revising | published
in_world_span: "742 TR, spring"
pov: [/characters/mara-thorne.md]
provenance: human
---
```

**Canon Decision** — write one for every retcon or contested ruling.
```yaml
---
type: Canon Decision
title: "Mara's brother renamed Edran (was Aldric)"
description: "Retcon resolving a name collision with a faction leader."
timestamp: 2026-08-16T10:00:00Z
status: accepted
supersedes: [/characters/aldric-thorne.md]
---
```

Locations, factions and items follow the same shape. Give items a `status` (`intact | damaged | destroyed | lost`) plus `status_since`, because object state is a classic continuity trap.

Quote ambiguous scalars (`"NO"`, `"742 TR"`) so YAML does not coerce them into booleans or numbers.

## Concept bodies

Favor structural markdown — headings, tables, lists — over freeform prose; it helps both human scanning and agent retrieval. Use OKF's conventional headings where they fit, and add worldbuilding-specific ones consistently across concepts of the same type:

```markdown
# Description
Prose that a writer can actually absorb before drafting a scene.

# Appearances
* [The Drowned City](/stories/the-drowned-city.md) — ch. 1–14, POV.

# Relationships
Brother of [Edran Vale](/characters/edran-vale.md). Sworn to the
[Ebb Court](/factions/ebb-court.md).

# Open Questions
* Does she know who drowned the Abbey? Unresolved — see
  [open questions](/continuity/open-questions.md).

# Citations
[1] [The Drowned City](/stories/the-drowned-city.md) — ch. 3, bell-tower scene.
[2] [Canon decision: Edran rename](/decisions/cdr-0007.md)
```

The `# Citations` section is the load-bearing part. OKF already asks that claims sourced from external material be cited; in fiction, *the stories are the external material*. Every non-obvious canon fact should trace to a story and chapter. A fact without a citation cannot be adjudicated when two stories disagree, and citations are the line between canon and a writer's private assumption.

## Index files

Every directory gets an `index.md` for progressive disclosure — it lets an agent see what exists before opening thirty files. Index files carry **no frontmatter**, with exactly one exception: the bundle-root index may declare the version.

Root `index.md`:
```markdown
---
okf_version: "0.1"
---

# Entities

* [Characters](characters/) - everyone who appears or is named in canon.
* [Locations](locations/) - places, from continents to single rooms.
* [Factions](factions/) - courts, orders, guilds, and their allegiances.

# Canon Machinery

* [Stories](stories/) - the published works that source all canon.
* [Rules](rules/) - invariants the world must never contradict.
* [Continuity](continuity/) - open questions and known contradictions.
* [Decisions](decisions/) - rulings and retcons, with rationale.
```

Subdirectory `index.md` files list their concepts, reusing each concept's `description` verbatim so the two never drift:

```markdown
# Characters

* [Mara Thorne](mara-thorne.md) - Grey Warden of Ostreve; POV of The Drowned City.
* [Edran Vale](edran-vale.md) - Mara's brother; Ebb Court archivist.
```

Generate these rather than hand-maintaining them once the bundle passes ~30 concepts.

## The log

Maintain `log.md` at the bundle root, newest first, with ISO 8601 date headings:

```markdown
# Canon Update Log

## 2026-08-16
* **Update**: Retconned Aldric to [Edran Vale](/characters/edran-vale.md); see [CDR-0007](/decisions/cdr-0007.md).
* **Creation**: Added [The Breaking of the Bells](/events/breaking-of-the-bells.md).

## 2026-08-02
* **Initialization**: Established bundle structure and root index.
```

Add a scoped `log.md` inside a subdirectory only if that area changes often enough to be worth its own history.

## Consistency dashboard

Put these in `continuity/dashboard.md` (a concept — give it `type: Register`). They are the mechanical half of continuity enforcement and cost nothing to run.

**Conformance — the three hard rules:**
````
```dataview
TABLE type FROM ""
WHERE !type AND !contains(file.name, "index") AND !contains(file.name, "log")
```
````

**Uncited canon:**
````
```dataview
TABLE canon, established_in
FROM "characters" OR "locations" OR "factions" OR "events"
WHERE canon = "hard" AND !established_in
```
````

**The dead, for cross-checking against drafts:**
````
```dataview
TABLE death_date, established_in
FROM "characters"
WHERE status = "dead"
SORT death_date ASC
```
````

**AI-proposed content awaiting review:**
````
```dataview
TABLE type, timestamp FROM ""
WHERE provenance = "ai-proposed"
```
````

**Timeline, for spotting impossible orderings:**
````
```dataview
TABLE in_world_date, location, participants, established_in
FROM "events"
SORT sort_key ASC
```
````

Two caveats. Dataview indexes markdown links in `file.outlinks`, so the link graph still works under OKF, but bundle-relative frontmatter values are plain strings rather than link objects — put relationships you want to traverse in the body as well as the frontmatter. And Dataview cannot do cross-file arithmetic reliably, so age and interval math (a character is twelve at an event predating their birth) belongs in a script.

## Canon workflow

Write these rules into the root index or a `continuity/policy.md` concept, and enforce them in review:

- **One concept per entity.** Stories reference entities; they never redefine them.
- **Every canon fact cites its story and chapter.**
- **Drafts stay `canon: draft`** until the story establishing them is finished.
- **Unknowns go in `continuity/open-questions.md`,** so two writers do not independently invent conflicting answers.
- **Retcons are recorded, not erased.** Set the superseded concept to `canon: retconned`, write a Canon Decision with `supersedes`, add a `log.md` entry, then update dependents. Silently overwriting canon destroys the audit trail that makes later contradictions resolvable.

For a team, add a git gate: `main` is canon, writers work on branches, and promotion to `canon: hard` goes through a pull request carrying this checklist:

- [ ] Every new named entity has a concept with `type`, `canon`, and `established_in`.
- [ ] Every claim about existing canon matches its concept, or a Canon Decision records the change.
- [ ] No character appears after their `death_date` outside a flashback or mention.
- [ ] New events added with `sort_key`.
- [ ] No `invariant: true` rule violated.
- [ ] Affected `index.md` files and `log.md` updated.

The Obsidian Git plugin has a track record of clobbering pushes across machines; use it for solo backup and real git for anything with more than one editor.

## Agent instructions

Write a short, hand-authored `AGENTS.md` at the repo root — outside the bundle if the bundle is a subdirectory, since it is tooling instruction rather than world knowledge. Bloated context files measurably degrade agent performance, so include only what cannot be inferred:

- That this is an OKF v0.1 bundle and what the three conformance rules are.
- The `type` vocabulary in use and the canon tiers.
- The link convention (bundle-relative markdown, no wikilinks).
- That concept IDs are file paths, so filenames must not change casually.
- **The write gate:** agents may create concepts at `canon: draft` with `provenance: ai-proposed`, and may never set `canon: hard` or alter an existing hard-canon fact without explicit human approval.

## Continuity checking

Run deterministic checks first. A query that catches a dead character walking is free, instant, and cannot hallucinate; send the model in only for what the query cannot express.

**Checking a draft against canon:**

> Read the draft at `<path>`. Start from `/index.md` and the relevant subdirectory indexes rather than opening every file. For every factual claim the draft makes about an existing concept — people, places, items, factions, rules, dates — open that concept and compare. Output a table: claim | concept path | canon value | MATCH / CONTRADICTION / NOT-IN-CANON. For contradictions, quote both the draft line and the canon line. For NOT-IN-CANON, propose frontmatter but do not create the file. Check specifically for: characters appearing after `death_date`; violations of any rule with `invariant: true`; timeline claims inconsistent with `sort_key` order; characters knowing something before the scene where they learn it; object state contradicting `status_since`.

**Proposing concepts from a finished draft:**

> Extract every new named entity introduced in `<story>`. For each, write a conformant OKF concept with a descriptive `type`, `title`, `description`, `canon: draft`, `provenance: ai-proposed`, `established_in` pointing at this story, and a `# Citations` section giving the chapter. Update the relevant `index.md` and add a `log.md` entry. Do not set `canon: hard`.

Report findings by path and line, and separate hard contradictions from stylistic drift — a reviewer handed a flat list of forty "issues" stops reading.

## Guardrails on agent writes

- Mark all agent-authored content `provenance: ai-proposed`.
- Never promote to canon without a human step.
- Reject any proposed fact with no citation.
- When uncertain whether something is established canon or your own inference, say so rather than writing it to a file. A hallucinated fact that reaches `canon: hard` silently corrupts every story written afterward.

## Retrofitting existing work

Read the stories in publication order, extract entities and claims, and build concepts whose `# Citations` point at where each fact appeared. Contradictions *between existing stories* will surface immediately. Do not resolve them unilaterally — log them in `continuity/contradictions.md` and bring them to the author, since deciding which story is right is an authorial call.

## Phasing

1. **Foundation** — bundle skeleton, root `index.md` with `okf_version`, five concept types (Character, Location, Faction, Event, Story), the dashboard, `AGENTS.md`. Sufficient for most single-author projects.
2. **Collaboration** — git repo, branch-per-writer, PR checklist, `log.md`, decisions, open questions, contradictions.
3. **Automation** — a validator for the three conformance rules plus your own required extensions, index generation, a timeline/age script, wired into CI.

## What not to build

The dominant failure mode for small projects is elaborate machinery around an unwritten book. Resist:

- A validator stricter than OKF conformance. Missing optional fields, unknown types, and broken links are all explicitly legal; failing a build on them fights the format.
- Triple stores, RDF, or graph databases. Emulate fact-validity intervals with `status_since` / `status_until` fields instead.
- RAG pipelines for a few hundred files. Indexes, filesystem reads, and grep are faster and more accurate at that scale.
- More than about four canon tiers.
- Concept types for things that have never appeared in a story.

If the user starts refining taxonomy before any prose exists, say so plainly and steer them back to writing. The bundle exists to serve the stories.

# Citations

[1] [Open Knowledge Format specification, Version 0.1](https://raw.githubusercontent.com/lars20070/md2okf/refs/heads/master/SPEC.md)
