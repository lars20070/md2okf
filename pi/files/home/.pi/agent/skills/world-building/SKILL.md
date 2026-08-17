---
name: worldbuilding-wiki
description: Construct and maintain a fictional-world knowledge base as a conformant Open Knowledge Format (OKF) v0.1 bundle — a git-backed tree of markdown concepts — that keeps a world internally consistent across many stories, captures narrative arcs, character tension, open plots and unwritten futures, and checks new drafts against canon. Use this skill whenever the user mentions a story bible, series bible, worldbuilding wiki, canon, continuity, lore database, plot threads, character arcs, shared universe, or OKF bundle, or wants to track characters/locations/factions/timelines across multiple novels or short stories — and also when they ask you to write, review, or continue a story set in an existing world, since the first job there is loading and respecting canon.
---

# Worldbuilding Wiki (OKF v0.1)

Build a fictional world's canon as an **OKF knowledge bundle**: a directory of markdown concepts with YAML frontmatter, cross-linked with standard markdown links, readable by a human with `cat` and by an agent without an SDK.

A wiki that only holds *entities* becomes an encyclopedia of nouns — accurate and inert. This skill also models the things that move: arcs, tension, unresolved plots, and futures not yet written.

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
- **Broken links are legal.** The spec says a link to a nonexistent concept "may simply represent not-yet-written knowledge." So a dangling link is a *signal*, not an error — treat it as a worldbuilding to-do, and never let a validator fail a build over one. This is what lets a canon event point at a payoff nobody has written yet.

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
│
│   # ── WHAT EXISTS ──
├── characters/
│   ├── index.md
│   └── mara-thorne.md
├── locations/
├── factions/
├── items/
├── events/                   # one concept per timeline event: what HAS happened
├── rules/                    # magic/tech/physical invariants
│
│   # ── WHAT MOVES ──
├── arcs/                     # the shape of a change over story-time
├── threads/                  # open questions and unfired setups
├── fronts/                   # pressure ticking toward a future disaster
├── relationships/            # a pair of characters, and how it changes
│
│   # ── MACHINERY ──
├── stories/                  # one concept per novel or story
│   ├── index.md
│   ├── the-drowned-city.md
│   ├── the-drowned-city.beats.md   # optional beat sheet (see "Reading order")
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

`Character`, `Location`, `Faction`, `Item`, `Event`, `World Rule`, `Story`, `Arc`, `Thread`, `Front`, `Relationship`, `Beat Sheet`, `Canon Decision`, `Register`.

Layer OKF's recommended fields on top (`title`, `description`, `tags`, `timestamp`, and `resource` where a real URI exists), then add these extensions. OKF §4.1 explicitly permits producer-defined keys and requires consumers to preserve them, so they are conformant:

- `canon:` — `hard | soft | draft | non-canon | retconned`
- `tense:` — `past | open | future`
- `established_in:` — link to the story concept that made this canon
- `provenance:` — `human | ai-proposed | ai-approved`

**`canon` and `tense` are orthogonal, and keeping them separate is the decision that makes everything else work.** `canon` answers *is this true?*; `tense` answers *when, relative to now?* A planned future disaster is `canon: draft, tense: future` — recorded, plannable, queryable, and unmistakably not history. Resist adding `planned` or `speculative` to the canon vocabulary; they are `draft` plus a tense, and five tiers is already the ceiling.

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
tense: past
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
tense: past
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

---

# Narrative structure: the four folders that hold what moves

Entity folders answer *what exists*. These four answer *what is happening, what is unresolved, and what is coming*. Each comes from a body of practice that already solved the problem: arcs from story-craft's promise/progress/payoff, threads from the serial "dangling plot," fronts from tabletop RPG design, relationships from Dramatica's relationship throughline and Egri's unity of opposites.

Create them lazily. A short story needs none; a five-book series needs all four.

## `arcs/` — the shape of a change

An arc is a change tracked over story-time: a character who ends different from how they began, a plot that escalates, a theme that turns. Entity pages cannot hold this, because an entity page describes a *state* and an arc describes a *trajectory*. Arcs routinely span several stories, which is why they need their own concept rather than living inside one story's notes.

Track three things: the **promise** (what the reader was led to expect), the **progress** (beats that move it), and the **payoff** (where it lands). An arc whose payoff link is broken is an arc you have not written yet — which is legal, and queryable.

```markdown
---
type: Arc
title: "Mara's Redemption"
description: "Mara moves from vendetta to mercy across two books."
tags: [character-arc, tide-war]
timestamp: 2026-08-16T10:00:00Z
canon: draft
tense: open
arc_kind: character            # character | plot | thematic | relationship
subject: /characters/mara-thorne.md
spans_stories:
  - /stories/the-drowned-city.md
  - /stories/ashfall.md
value_start: vengeance
value_end: mercy
payoff_event: /events/mara-spares-the-regent.md   # broken link = unwritten
provenance: human
---

# Promise
*The Drowned City* ch.1 — Mara defines herself entirely by the vendetta. The
reader is promised she will one day have to choose.

# Progress
* [x] [She refuses the truce](/events/mara-refuses-the-truce.md) — digs in. (ch.9)
* [ ] Midpoint: learns the Regent spared her sister. *Planned, unwritten.*
* [ ] Crisis: vengeance or mercy, and she cannot have both.

# Payoff
Planned: [Mara spares the Regent](/events/mara-spares-the-regent.md) —
`canon: draft`, `tense: future`.

# Citations
[1] [The Drowned City](/stories/the-drowned-city.md) — ch. 1, ch. 9.
```

## `threads/` — open questions and unfired setups

A thread is anything the story has opened and not yet closed. Two kinds share the folder because they share a lifecycle — raised, dangling, resolved:

- **Questions** the reader is waiting to see answered. *Who poisoned the well?*
- **Setups** — Chekhov's guns, promises, planted objects — that have not yet fired. *Why did the narrative pause to describe that locket?*

Keeping them together means one query answers the most useful question a series author can ask: *what have I opened and not closed?*

```markdown
---
type: Thread
title: "Who poisoned the Verge well?"
description: "The poisoning that opens Book 1 is still unattributed."
tags: [mystery, the-verge]
timestamp: 2026-08-16T10:00:00Z
canon: hard                    # the question is canon; the answer is not
tense: open
thread_kind: question          # question | setup | promise
raised_in: /stories/the-drowned-city.md
raised_at: /events/well-poisoning-discovered.md
involves: [/characters/mara-thorne.md, /factions/the-ashen-covenant.md]
last_touched: /stories/the-drowned-city.md
resolved_by: null              # null = still open
provenance: human
---

# The question
Discovered in ch.2. Forty dead in the Verge; no culprit named by the end of Book 1.

# Candidate answers — speculative, not canon
* The Ashen Covenant, to discredit the crown. *(leading)*
* Mara's sister, off-page, for reasons not yet invented.

# Citations
[1] [The Drowned City](/stories/the-drowned-city.md) — ch. 2.
```

The setup variant is the same shape with the gun in it:

```yaml
---
type: Thread
title: "The silver locket"
description: "Mara pockets her sister's locket in ch.3. It has not been opened."
canon: hard
tense: open
thread_kind: setup
element: /items/the-silver-locket.md
raised_in: /stories/the-drowned-city.md
fired: false                   # false = unfired Chekhov's gun
intended_payoff: /stories/ashfall.md
provenance: human
---
```

## `fronts/` — pressure that is ticking

Threads are open. Fronts are *advancing*. This structure is borrowed wholesale from tabletop RPG design (Apocalypse World and Dungeon World's Fronts, Blades in the Dark's clocks), because it is the only well-documented format for representing a future that arrives whether or not anyone intervenes.

A front is an antagonistic force with an **impulse** (what it wants), an ordered list of **portents** (the steps it takes), a **doom** (what happens if unopposed), and a **clock** (how close it is). It answers the hardest question — *how do I record a plot line I have not written?* — because a front is not a prediction, it is a mechanism. Advance it when a story shows it advancing; consult it when a story needs pressure.

```markdown
---
type: Front
title: "The Ashen Covenant"
description: "A cult draining the leyline wells to wake a drowned god."
tags: [antagonist, tide-war]
timestamp: 2026-08-16T10:00:00Z
canon: draft
tense: future
impulse: "Restore the old god by draining the leyline wells."
driver: /factions/the-ashen-covenant.md
threatens: [/locations/the-verge.md, /characters/mara-thorne.md]
clock_segments: 6
clock_filled: 2
doom: /events/the-ashen-dawn.md   # broken link until written
provenance: human
---

# Portents, in order
1. [x] Poison the Verge well — [done](/events/well-poisoning-discovered.md)
2. [x] Recover the first leyline key
3. [ ] **Next:** assassinate the Warden of the Verge
4. [ ] Open the conduit beneath the Drowned Abbey
5. [ ] The Ashen Dawn — the doom

# If nobody stops it
The leyline dies, Ostreve's tide-magic fails, and the Ebb Court loses its only
defence. Book 3 territory.

# Citations
[1] [The Drowned City](/stories/the-drowned-city.md) — ch. 2, ch. 17.
```

Start with **one** front holding all simmering pressure. Split it only when two threats genuinely advance on independent schedules.

## `relationships/` — a pair, and how it changes

Tension lives between characters, not inside them, and it *moves* — enemies become allies, siblings become rivals. A field on a character page can hold "brother of Edran"; it cannot hold "hostile allies since the siege, and the question of Book 2 is whether that becomes trust."

Name the file after both characters, alphabetically, joined by `--`. The body carries a dated state log, newest first.

**Only create these for load-bearing pairs** — the three or four relationships that actually carry the drama. A document per dyad is bookkeeping, not worldbuilding.

```markdown
---
type: Relationship
title: "Mara Thorne ⇄ Callen Vane"
description: "Enemies turned hostile allies; the axis is vengeance vs. mercy."
tags: [core-dyad]
timestamp: 2026-08-16T10:00:00Z
canon: hard
tense: open
between: [/characters/mara-thorne.md, /characters/callen-vane.md]
axis: "vengeance vs. mercy"
charge: hostile-allies         # the current state, one short term
nature: unity-of-opposites     # neither can concede without ceasing to be themselves
governing_arc: /arcs/mara-redemption.md
provenance: human
---

# State log
* **Ashfall ch.2** *(planned)* — hostile allies → wary respect.
* **The Drowned City ch.20** — enemies → hostile allies, after the siege.
* **The Drowned City ch.1** — open enemies.

# Why it generates tension
Callen embodies the mercy Mara has refused her whole life. Neither can yield
without abandoning the thing that defines them, so the conflict cannot resolve
by compromise — only by one of them changing.

# Open
Whether respect becomes trust is the question of Book 2. See
[Mara's Redemption](/arcs/mara-redemption.md).

# Citations
[1] [The Drowned City](/stories/the-drowned-city.md) — ch. 1, ch. 20.
```

## Reading order vs. world order

`events/` holds the world's chronology: what happened, in the order it happened. That is not the order the reader learns it — a flashback in ch.7 may describe the earliest event in the world.

If a story's structure matters (mysteries, non-linear narratives, anything with a withheld revelation), add an optional beat sheet beside the story: `stories/the-drowned-city.beats.md`, `type: Beat Sheet`. It lists beats in *reading* order, each linking to the event it reveals, and notes what the reader now knows that the characters do not — which is all dramatic irony is:

```markdown
3. **Flashback, ch.7** — reveals [the sister abandoned](/events/the-sister-abandoned.md)
   (in-world: 738 TR, six years before ch.1).
   *Reader now knows Mara has a sister. Callen does not learn this until ch.19.*
```

Skip beat sheets entirely for linear stories. They earn their keep only when reading order and world order diverge on purpose.

---

## Concept bodies

Favor structural markdown — headings, tables, lists — over freeform prose; it helps both human scanning and agent retrieval. Use OKF's conventional headings where they fit, and keep them consistent across concepts of the same type:

```markdown
# Description
Prose a writer can absorb before drafting a scene.

# Appearances
* [The Drowned City](/stories/the-drowned-city.md) — ch. 1–14, POV.

# Relationships
Brother of [Edran Vale](/characters/edran-vale.md). Sworn to the
[Ebb Court](/factions/ebb-court.md). Core dyad:
[Mara ⇄ Callen](/relationships/mara-thorne--callen-vane.md).

# Open
* Does she know who drowned the Abbey? See
  [who poisoned the Verge well](/threads/who-poisoned-the-verge-well.md).

# Citations
[1] [The Drowned City](/stories/the-drowned-city.md) — ch. 3, bell-tower scene.
```

The `# Citations` section is load-bearing. OKF asks that claims sourced from external material be cited; in fiction, *the stories are that material*. Every non-obvious canon fact should trace to a story and chapter. A fact without a citation cannot be adjudicated when two stories disagree, and citations are the line between canon and a writer's private assumption.

## Completeness: nothing essential may be lost

When building the wiki from source material — manuscripts, drafts, published stories — **the finished bundle must contain every essential fact the source establishes.** A wiki that quietly drops details is worse than no wiki, because writers will trust it and then contradict the book.

Work chapter by chapter rather than skimming whole stories, and sweep deliberately for the categories that get dropped:

- Exact names, spellings, titles, and forms of address.
- Numbers: distances, dates, ages, counts, prices, durations.
- Physical and sensory detail already fixed on the page — eye colour, scars, the smell of a place.
- Stated rules and limits, especially magic or technology costs.
- Who was present, and who was *not*.
- Emotional states and shifts in a relationship, not just plot events.
- Anything the narrative lingered on without explaining. That is usually a setup; make it a thread.

**Verbatim quotation is permitted for small, essential passages.** Where the exact wording *is* the fact — a prophecy, an oath, a law, a precise spelling, a line of dialogue that defines a character — reproduce it exactly rather than paraphrasing, because a paraphrase silently invents a variant that later stories may contradict. Keep such quotations short, mark them as blockquotes, and always cite the story and chapter:

```markdown
# The Oath of the Ebb

> "Salt in the hand, salt in the mouth, and the tide takes what it is owed."

Sworn on investiture. Wording is fixed; Mara's variation in ch.19 is deliberate
and plot-relevant.

# Citations
[1] [The Drowned City](/stories/the-drowned-city.md) — ch. 4.
```

Everything else gets paraphrased. Do not transcribe scenes, chapters, or long passages into the wiki — the bundle is a reference layer over the stories, not a copy of them. If you are quoting more than a few lines from one source, you are duplicating the manuscript rather than indexing it.

After processing each chapter, report two lists to the author: what you extracted, and what you judged inessential and deliberately left out. The second list is the more useful one — it is where a lost fact gets caught while the chapter is still fresh.

## Index files

Every directory gets an `index.md` for progressive disclosure — it lets an agent see what exists before opening thirty files. Index files carry **no frontmatter**, with exactly one exception: the bundle-root index may declare the version.

Root `index.md`:
```markdown
---
okf_version: "0.1"
---

# What exists

* [Characters](characters/) - everyone who appears or is named in canon.
* [Locations](locations/) - places, from continents to single rooms.
* [Factions](factions/) - courts, orders, guilds, and their allegiances.
* [Events](events/) - what has happened, in world order.
* [Rules](rules/) - invariants the world must never contradict.

# What moves

* [Arcs](arcs/) - changes tracked from promise to payoff.
* [Threads](threads/) - questions opened and setups not yet fired.
* [Fronts](fronts/) - pressure advancing toward a future disaster.
* [Relationships](relationships/) - the pairs that carry the tension.

# Machinery

* [Stories](stories/) - the works that source all canon.
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

**Unfired Chekhov's guns:**
````
```dataview
TABLE raised_in, element, intended_payoff
FROM "threads"
WHERE thread_kind = "setup" AND fired = false
```
````

**Threads left dangling:**
````
```dataview
TABLE raised_in, last_touched
FROM "threads"
WHERE tense = "open" AND !resolved_by
SORT last_touched ASC
```
````

**Arcs with no payoff written:**
````
```dataview
TABLE subject, value_start, value_end, payoff_event
FROM "arcs"
WHERE tense = "open"
```
````

**Clocks nearly full:**
````
```dataview
TABLE clock_filled, clock_segments, doom
FROM "fronts"
WHERE clock_filled / clock_segments >= 0.6
SORT clock_filled DESC
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

Two caveats. Dataview indexes markdown links in `file.outlinks`, so the link graph works under OKF, but bundle-relative frontmatter values are plain strings rather than link objects — put relationships you want to traverse in the body as well as the frontmatter. And Dataview cannot do cross-file arithmetic reliably, so age and interval math (a character is twelve at an event predating their birth) belongs in a script.

## Canon workflow

Write these rules into the root index or a `continuity/policy.md` concept, and enforce them in review:

- **One concept per entity.** Stories reference entities; they never redefine them.
- **Every canon fact cites its story and chapter.**
- **Drafts stay `canon: draft`** until the story establishing them is finished.
- **Speculation is labelled, never asserted.** Candidate answers, planned beats, and undecided futures live under a body heading that says so, on a concept marked `canon: draft`. A canon concept may link to a speculative one; it may never state it as history.
- **Unknowns go in `continuity/open-questions.md`,** so two writers do not independently invent conflicting answers.
- **Retcons are recorded, not erased.** Set the superseded concept to `canon: retconned`, write a Canon Decision with `supersedes`, add a `log.md` entry, then update dependents. Silently overwriting canon destroys the audit trail that makes later contradictions resolvable.

For a team, add a git gate: `main` is canon, writers work on branches, and promotion to `canon: hard` goes through a pull request carrying this checklist:

- [ ] Every new named entity has a concept with `type`, `canon`, and `established_in`.
- [ ] Every claim about existing canon matches its concept, or a Canon Decision records the change.
- [ ] No character appears after their `death_date` outside a flashback or mention.
- [ ] New events added with `sort_key`.
- [ ] No `invariant: true` rule violated.
- [ ] Threads opened or closed are created or updated; setups fired are marked `fired: true`.
- [ ] Fronts this story advanced have their portents ticked.
- [ ] Relationship state logs updated for any dyad that shifted.
- [ ] Affected `index.md` files and `log.md` updated.

The Obsidian Git plugin has a track record of clobbering pushes across machines; use it for solo backup and real git for anything with more than one editor.

## Agent instructions

Write a short, hand-authored `AGENTS.md` at the repo root — outside the bundle if the bundle is a subdirectory, since it is tooling instruction rather than world knowledge. Bloated context files measurably degrade agent performance, so include only what cannot be inferred:

- That this is an OKF v0.1 bundle and what the three conformance rules are.
- The `type` vocabulary in use, the canon tiers, and the `tense` values.
- The link convention (bundle-relative markdown, no wikilinks).
- That concept IDs are file paths, so filenames must not change casually.
- The completeness rule, and that short verbatim quotation is allowed where wording is the fact.
- **The write gate:** agents may create concepts at `canon: draft` with `provenance: ai-proposed`, and may never set `canon: hard` or alter an existing hard-canon fact without explicit human approval.

## Continuity checking

Run deterministic checks first. A query that catches a dead character walking is free, instant, and cannot hallucinate; send the model in only for what the query cannot express.

**Checking a draft against canon:**

> Read the draft at `<path>`. Start from `/index.md` and the relevant subdirectory indexes rather than opening every file. For every factual claim the draft makes about an existing concept — people, places, items, factions, rules, dates — open that concept and compare. Output a table: claim | concept path | canon value | MATCH / CONTRADICTION / NOT-IN-CANON. For contradictions, quote both the draft line and the canon line. For NOT-IN-CANON, propose frontmatter but do not create the file. Check specifically for: characters appearing after `death_date`; violations of any rule with `invariant: true`; timeline claims inconsistent with `sort_key` order; characters knowing something before the scene where they learn it; object state contradicting `status_since`. Then check narrative state: which threads this draft opens or closes, which setups it fires, which fronts it advances, and which relationships change charge.

**Proposing concepts from a finished draft:**

> Extract every new named entity introduced in `<story>`, and every new thread, arc beat, front advance, and relationship shift. For each, write a conformant OKF concept with a descriptive `type`, `title`, `description`, `canon: draft`, `provenance: ai-proposed`, `established_in` pointing at this story, and a `# Citations` section giving the chapter. Then report what you extracted and what you judged inessential, per the completeness rule. Update the relevant `index.md` and add a `log.md` entry. Do not set `canon: hard`.

Report findings by path and line, and separate hard contradictions from stylistic drift — a reviewer handed a flat list of forty "issues" stops reading.

## Guardrails on agent writes

- Mark all agent-authored content `provenance: ai-proposed`.
- Never promote to canon without a human step.
- Reject any proposed fact with no citation.
- Keep speculation in speculative places. A candidate answer to a thread belongs under a heading that names it as such, never in the `description` field where a later reader will take it for canon.
- When uncertain whether something is established canon or your own inference, say so rather than writing it to a file. A hallucinated fact that reaches `canon: hard` silently corrupts every story written afterward.

## Retrofitting existing work

Read the stories in publication order, extract entities and claims, and build concepts whose `# Citations` point at where each fact appeared. Apply the completeness rule chapter by chapter. Then make a second pass for narrative structure, which is far easier to see once the entities exist: what questions each story opened and whether they ever closed, which objects were planted and never used, which relationships changed and when.

Contradictions *between existing stories* will surface immediately. Do not resolve them unilaterally — log them in `continuity/contradictions.md` and bring them to the author, since deciding which story is right is an authorial call.

## Phasing

1. **Foundation** — bundle skeleton, root `index.md` with `okf_version`, the entity types, `canon`/`tense`, the dashboard, `AGENTS.md`. Sufficient for a single novel.
2. **Narrative** — add `arcs/` and `threads/` first; they pay for themselves fastest and answer "what have I promised and not delivered." Add `relationships/` for the core dyads only.
3. **Series** — add `fronts/` once a future spans books, and beat sheets only where reading order diverges from world order.
4. **Automation** — a validator for the three conformance rules plus your own required extensions, index generation, a timeline/age script, wired into CI.

## What not to build

The dominant failure mode for small projects is elaborate machinery around an unwritten book. Resist:

- A validator stricter than OKF conformance. Missing optional fields, unknown types, and broken links are all explicitly legal; failing a build on them fights the format.
- A relationship document for every pair of characters. Three or four load-bearing dyads, no more.
- Beat sheets for linear stories.
- Multiple fronts before one is full.
- Triple stores, RDF, or graph databases. Emulate fact-validity intervals with `status_since` / `status_until` fields instead.
- RAG pipelines for a few hundred files. Indexes, filesystem reads, and grep are faster and more accurate at that scale.
- Concept types for things that have never appeared in a story.

A concept type you create but never query is pure overhead. If nothing ever runs the unfired-setups query, delete `threads/` and stop maintaining it.

If the user starts refining taxonomy before any prose exists, say so plainly and steer them back to writing. The bundle exists to serve the stories.

# Citations

[1] [Open Knowledge Format specification, Version 0.1](https://raw.githubusercontent.com/lars20070/md2okf/refs/heads/master/SPEC.md)
