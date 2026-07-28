# Refactor the container agent's instructions into a `compile-wiki` skill

## Context

The sandbox runtime already works this way. Commit `4735d60` split
[pi/sandbox/files/home/.pi/agent/AGENTS.md](pi/sandbox/files/home/.pi/agent/AGENTS.md)
into a task-agnostic constitution (identity, workspace boundaries, OKF format
conventions) plus a `compile-wiki` skill holding the **procedure**. Adding a
future task ("consolidate the wiki") becomes a new skill directory rather than
more rules in an always-on instruction file.

The container runtime never got that treatment.
[pi/container/agent/AGENTS.md](pi/container/agent/AGENTS.md) is still one flat
100-line file mixing identity, conventions and workflow, and
`pi/container/agent/skills/compile-wiki/SKILL.md` exists as a **0-byte
untracked stub**. This plan fills that stub and slims AGENTS.md to match the
sandbox's shape.

**The constraint that shapes everything below:**
[scripts/compile-wiki-container.sh:52](scripts/compile-wiki-container.sh#L52)
passes `-xt bash`, which excludes the bash tool outright. (The sandbox dropped
that flag in commit `6318bdd` precisely so its agent could run a linter.) The
container agent therefore cannot run `okf-lint`, `cat SPEC.md`, or `date +%F`.
`-xt bash` stays; the container skill is written to live within it.

**`read` survives `-xt bash`.** Verified against the installed Pi package rather
than assumed: `-xt` is a per-tool-name denylist, and `read` is a built-in
separate from `bash` — the CLI tagline is "AI coding assistant with read, bash,
edit, write tools", and `docs/extensions.md:1847` enumerates the built-ins as
`read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`. The `read` tool takes
`{ path, offset?, limit? }` (`docs/extensions.md:709`), so the agent can open
`SPEC.md` directly **and** read long sources in ranges. Losing bash costs the
agent `okf-lint` and `date`, not file access.

**Keeping `read` is also what keeps skills working.** In
`dist/core/system-prompt.js`, the skills section is appended only under
`if (hasRead && skills.length > 0)` — Pi advertises a skill in the system prompt
**only when the `read` tool is available**, since a skill is useless if the model
cannot open its `SKILL.md`. `-xt bash` leaves `read` intact, so `compile-wiki`
will be advertised normally. The rule this implies for the future: never add
`read` to the `-xt` list, or the skill silently vanishes from the prompt.

Consequences, all confirmed with the user:

- **No `okf-lint` anywhere** in the container skill or AGENTS.md — the whole
  "Check your output with `okf-lint`" section and the `lint-okf.sh` wrapper are
  omitted. The `SPEC.md` references stay: `SPEC.md` is baked into the image at
  `/workspace/SPEC.md` ([pi/container/Dockerfile:26](pi/container/Dockerfile#L26))
  and read with the `read` tool, not fetched.
- **A `log.md`, but with no dates.** The agent writes `okf/log.md` and prepends
  each run's entries so the newest are first — but the entries carry no
  datestamps, because on the pinned Pi version the container agent has **no way
  to learn the date**. Verified in the 0.82.1 tarball, not assumed:
  `buildSystemPrompt` in `dist/core/system-prompt.js` appends only
  `Current working directory` — no date. It used to append
  `Current date: YYYY-MM-DD`, but release **0.80.7** (2026-07-14) removed it:
  *"Fixed system prompt cache invalidation across dates by removing the current
  date from the default prompt"* (CHANGELOG, issue \#6621). Both runtimes pin
  0.82.1 ([Dockerfile](pi/container/Dockerfile), [spec.yaml](pi/sandbox/spec.yaml)),
  so both are past that change. Without bash there is no `date +%F` either, so an
  agent told to datestamp would have to invent the date — the exact failure the
  "never take a version from memory" rule exists to prevent. A dateless log is
  the honest form. (This also explains why the sandbox skill's `date +%F` call is
  load-bearing rather than belt-and-braces.)
- **No `scripts/` directory** in the container skill — nothing to wrap.

### The dateless log must carry no `##` headings

This constraint is not stylistic — it is what keeps the result lint-clean, and it
was read out of the pinned `okf-lint@0.1.0` source rather than guessed:

- **`log-date-format` is severity `error`**, and it fires on **every** `##`
  heading in `log.md` that is not an ISO date — not merely on headings that look
  like dates. A heading such as `## Chapter 3` produces
  *"Log entry headings must use ISO 8601 `YYYY-MM-DD` form"*. It is **not**
  disabled in [okf/.okflintrc.json](okf/.okflintrc.json), so it is live.
- If `log.md` contains **no `##` headings at all**, the rule collects nothing and
  stays silent. `log-date-order` likewise filters to ISO-dated headings, so it is
  inert too.
- `recommended-log` only checks that `log.md` **exists**; it never inspects the
  format.

So the container's log is a **flat bullet list under a single `#` heading**, with
no sub-headings, newest entries prepended at the top.

#### Worked example

This is the target shape, written out at realistic length. It shows the state
after **three** compile runs against the Economist Style Guide source, so the
accumulation is visible. Reproduce this example in `AGENTS.md` so the agent has a
concrete model rather than a description:

```markdown
# Update Log

* **Update**: Expanded [8. What's in a name](/part-2/8-whats-in-a-name.md) with
  the sections on place names, corporate names, and the treatment of titles.
* **Creation**: Added
  [9. American and British English](/part-2/9-american-and-british-english.md),
  covering spelling, vocabulary and punctuation differences.
* **Deprecation**: Folded the standalone `/part-2/hyphens.md` into
  [7. Punctuation, mechanics and conventions](/part-2/7-punctuation-mechanics-conventions.md)
  and removed its entry from [the Part 2 index](/part-2/index.md).
* **Update**: Regenerated [the Part 2 index](/part-2/index.md) so it lists the
  chapters above.
* **Creation**: Added [Part 2](/part-2/index.md) with chapters
  [6. Confusables and cuttables](/part-2/6-confusables-and-cuttables.md) and
  [10. Reference](/part-2/10-reference.md).
* **Creation**: Added [the Glossary](/glossary/index.md) with 18 grammatical
  term definitions, among them [verb](/glossary/verb.md),
  [noun phrase](/glossary/noun-phrase.md) and
  [subordinate clause](/glossary/subordinate-clause.md).
* **Update**: Added the glossary to [the root index](/index.md).
* **Creation**: Added [Part 1](/part-1/index.md) with chapters
  [1. Old and short: words](/part-1/1-old-and-short-words.md) through
  [5. Editing](/part-1/5-editing.md).
* **Creation**: Added [the Introduction](/introduction.md), presenting Orwell's
  six rules and the principles of clarity, concision, honesty, humility and
  lucidity.
* **Creation**: Initialised the wiki from `md/TheEconomistStyleGuide2023.md` and
  added [the root index](/index.md) declaring `okf_version` 0.1.
```

How to read it, and the points the agent must copy:

- **One `#` heading, no `##` anywhere.** Every entry is a top-level `*` bullet.
  Runs are not separated by headings, rules, or blank-line groups.
- **Newest first.** The bottom four bullets are the first run (initialisation,
  Introduction, Part 1, glossary); the middle are the second; the top two are the
  most recent. Each run **prepends** directly beneath `# Update Log` and leaves
  everything below untouched.
- **No dates, anywhere** — not in headings, not inline in the prose.
- **One bullet per page created or updated**, plus a bullet for an index
  regenerated as a consequence. A run that touches five pages adds roughly five
  bullets, not one summary bullet.
- **Wrapped bullets continue with a two-space indent**, as in the
  `8. What's in a name` and `Deprecation` entries.
- **Links are bundle-absolute and point at a real `.md` file** —
  `/part-2/index.md` rather than `/part-2/`. This is a robustness choice, not a
  lint requirement: `valid-links` skips any target that does not end in `.md`
  (`if (!stripped.toLowerCase().endsWith('.md')) continue`), so a directory-style
  link like `/glossary/` is never checked at all. It will not be reported — but
  it also gets no protection, so a renamed directory leaves a silently dead link.
  Linking to `/glossary/index.md` puts the link under the rule's coverage.
  Verified: the sandbox's existing `okf/log.md` uses the directory form and
  `make lint-okf` reports `✓ No problems found.`
- **The leading bold word carries the change type** (`**Creation**`,
  `**Update**`, `**Deprecation**`) — a convention, not a requirement, but it is
  the only signal of what kind of change an entry records once dates are gone.

Note that "newest first" cannot be machine-checked here — with no dated headings
`log-date-order` has nothing to compare — so it rests entirely on the instruction
to prepend, and on the two-run check in Verification below.

### One spec tension to state openly

`SPEC.md` §7 describes the log as *"a flat list of date-grouped entries, newest
first"*, and §9.3 makes conformance depend on `log.md` following §7 "when
present". A dateless log keeps the flat-list-newest-first shape but drops the
date grouping, so it departs from the format §7 illustrates. The normative `MUST`
in §7 constrains only the *form of date headings* (`YYYY-MM-DD`), and with no
headings at all nothing violates it — which is why the linter passes.

This matters for instruction design, not just pedantry: `AGENTS.md` tells the
agent **"where the spec and these conventions disagree, the spec wins"**. If
AGENTS.md simply said "write a log without dates", a careful agent reading §7
could reconcile the conflict by inventing dates. So the container's log section
must **name the exception explicitly** — see change 1 below. This is your call
and is implemented as asked; it is flagged only so the instructions do not fight
each other.

## Changes

### 1. `pi/container/agent/AGENTS.md` — slim to shared invariants

Keep, with wording unchanged where possible: *The OKF specification is the
source of truth*, *Workspace boundaries*, *OKF wiki conventions* (structure,
`okf_version` frontmatter on `okf/index.md`, per-directory `index.md` link
lists, content-page frontmatter, kebab-case slugs, idempotency + index
regeneration).

Four edits:

- **Core identity** — reword from "reads source Markdown … one document at a
  time" to a maintainer of the wiki under `okf/` that receives one task per run,
  mirroring the sandbox copy.
- **Add a "Your task arrives as a skill" section**, modelled on the sandbox's:
  skills live under `~/.pi/agent/skills/`, one directory per task, each with a
  `SKILL.md`; when a run names one, read its `SKILL.md` first and follow it;
  available skills: `compile-wiki`. Note that `AGENTS.md` gives the conventions,
  the skill gives the procedure.
- **Workspace boundaries** — drop the "You are invoked once per source document"
  bullet; that is compile-specific and moves into the skill's intro.
- **Remove the `### Fidelity` section** — it moves verbatim into the skill.

Two fixes on top of the split:

- **Fix the `cat SPEC.md` fence — it cannot work under `-xt bash`.** This is the
  highest-value edit in the file: the agent's output is only as good as its grasp
  of the spec, and today the one instruction that loads the spec names a tool the
  container does not have. Silent failure here degrades every page it writes.
  Replace the fenced block with an explicit `read`-tool instruction — spell out
  the tool by name rather than saying "read the file":

  > **At the start of every run, read `SPEC.md` before writing anything.** Open
  > it with your **`read` tool**, path `SPEC.md` at the workspace root (absolute:
  > `/workspace/SPEC.md`). Do **not** try to `cat` it — this runtime has no
  > `bash` tool. `SPEC.md` is ~460 lines and fits in a **single `read` call**;
  > read it in full rather than skimming. If you ever do need it in pieces, the
  > `read` tool takes `offset` and `limit`.

  Keep the surrounding rules verbatim: take the version from the spec's
  "Versioning" section (§11, `SPEC.md:391`) for `okf_version`; where spec and
  these conventions disagree, the spec wins; if `SPEC.md` is missing or
  unreadable, leave the `okf_version` in `okf/index.md` unchanged and say so in
  the final message.
- **Add the bundle-absolute-links bullet** to `### Structure`, ported verbatim
  from [the sandbox copy](pi/sandbox/files/home/.pi/agent/AGENTS.md): links are
  rooted at the wiki root (`/glossary/verb.md`, not `glossary/verb.md`) and only
  ever point at a page that exists on disk right now.

Then add the log convention — new to the container, and deliberately **not** a
verbatim port of the sandbox's:

- **`### Structure`** gains the `okf/log.md` bullet: the bundle root carries
  `log.md`, the update log; keep it present and current.
- **A new `### Update log` section**, adapted from the sandbox's but dateless.
  It must state four things, and must name the spec exception outright so the
  "spec wins" rule cannot push the agent into inventing dates:

  > The bundle root carries `okf/log.md`, a record of what each run changed.
  > `index.md` and `log.md` are reserved filenames — `log.md` carries **no** YAML
  > frontmatter and is never listed as a content entry in an index.
  >
  > - The log is a **flat bullet list under a single `# Update Log` heading**,
  >   **newest first**. Every run **prepends** its entries directly beneath that
  >   heading; never rewrite or reorder entries from earlier runs.
  > - **Write no dates and no `##` headings.** This runtime cannot determine the
  >   current date — it has no `bash` tool — and a guessed date is worse than
  >   none. This **overrides** the date-grouped example in `SPEC.md` §7: it is
  >   the one place where these conventions deliberately depart from the spec's
  >   illustration. Do not add date headings to reconcile them.
  > - Entries are short prose. The leading bold word (`**Creation**`,
  >   `**Update**`, `**Deprecation**`) is a convention, not a requirement. Links
  >   inside entries follow the same rules as everywhere else: bundle-absolute,
  >   and pointing only at pages that exist on disk.
  > - If `okf/log.md` does not exist yet, create it in this run.

  Include the worked example from the Context section above so the shape is
  unambiguous.

### 2. `pi/container/agent/skills/compile-wiki/SKILL.md` — fill the empty stub

Frontmatter matching the sandbox's (`name` must be lowercase/digits/hyphens;
`description` says *when* to use the skill):

```yaml
---
name: compile-wiki
description: Compile one Markdown source document from md/ into the OKF wiki under okf/. Use when a run asks you to create or update the wiki from a source document.
---
```

Body — same structure as
[the sandbox SKILL.md](pi/sandbox/files/home/.pi/agent/skills/compile-wiki/SKILL.md),
minus the bash and lint steps:

- **Intro** — translate one document under `md/` into OKF pages under `okf/`;
  invoked once per source document; integrate without disturbing unrelated
  pages. Note that the conventions in `AGENTS.md` apply and are not restated —
  keep `update log format` in that list of deferred conventions, as the sandbox
  does, since the container now has one.
- **Procedure**, five steps. Step 1 carries the same explicit `read`-tool
  wording as AGENTS.md — the sandbox's step 1 is a `cat SPEC.md` fence, and
  copying it across would hand the container agent a command it cannot run:

  > 1. **Read `SPEC.md`** at the workspace root before writing anything, using
  >    your **`read` tool** (there is no `bash` tool here, so `cat` is not an
  >    option). Read it in full — it is ~460 lines — and follow the revision you
  >    read.

  Then: read the source document named in the prompt, read-only under `md/` →
  survey the existing wiki for pages already covering these topics and update in
  place → write the content pages by topic with the frontmatter `AGENTS.md`
  requires, in bounded chunks → regenerate the affected `index.md` link lists.

  **Step 6 is the log**, replacing the sandbox's `date +%F` step:

  > 6. **Prepend to `okf/log.md`**, one entry per page you created or updated,
  >    inserted directly beneath the `# Update Log` heading so the newest entries
  >    come first. Write **no date and no `##` heading** — see "Update log" in
  >    `AGENTS.md`. Create the file if it does not exist.

- **"Write in bounded chunks"** — port verbatim. This matters *more* here than
  in the sandbox: a truncated `write` call loses all its content.
- **"Fidelity"** — port verbatim, moved out of AGENTS.md.

Omit entirely: the `date +%F` call, the lint step, and the
"Check your output with `okf-lint`" section.

### 3. `scripts/compile-wiki-container.sh` — name the skill in the prompt

Without this the refactor is inert: Pi's print mode passes `-p` verbatim, so
there is no slash-command expansion and models do not reliably load a skill from
its `description` alone. Follow the sandbox driver's phrasing, using the
container's in-image path (compose sets `HOME: /home/node`, so `~` resolves, but
prefer the explicit path for clarity):

```bash
docker compose -f "${compose_file}" run --rm -T pi \
	-xt bash \
	-p "Load the compile-wiki skill: read /home/node/.pi/agent/skills/compile-wiki/SKILL.md, then follow it to compile ${document_inside} into the OKF wiki under okf/." \
	</dev/null
```

Keep `-xt bash` and `</dev/null` exactly as they are. Update the header comment
to say the workflow now lives in the skill.

### 4. Repo wiring

- **Delete** `pi/container/agent/skills/.gitkeep` — the directory now has real
  content, matching what the sandbox refactor did.
- **`git add`** the previously untracked
  `pi/container/agent/skills/compile-wiki/`.
- **No [compose.yaml](pi/container/compose.yaml) change.** The skills mount
  already exists at
  [compose.yaml:49](pi/container/compose.yaml#L49) (`./agent/skills:/home/node/.pi/agent/skills:ro`),
  so the new file is picked up on the next run with no rebuild.
- **No [Makefile](Makefile) change.** markdownlint already globs
  `pi/container/agent/**/*.md`, so `SKILL.md` is covered; the container skill
  ships no shell scripts, so the shellcheck glob stays sandbox-only.
- **No [Dockerfile](pi/container/Dockerfile) change.** `okf-lint` stays
  installed in the image — the agent is simply never told to use it. Ripping the
  install out is a separate call, not part of this refactor.
- **[README.md](README.md)** — the section at line 121 is titled
  "Skills (sandbox only)"; retitle it and add a short paragraph that the
  container carries its own copy under `pi/container/agent/skills/`, delivered
  by bind mount (so edits apply on the next run with no rebuild, unlike the
  sandbox's copy-at-build), and that the container skill has no lint step
  because its driver runs `-xt bash`. Also amend the "Inside the runtimes"
  bullet at line 198 so it no longer implies both runtimes lint.

## Deliberately out of scope

- **Removing `-xt bash`** from the container driver. That is the premise of this
  design, not an obstacle to it.
- **Changing the sandbox's log format.** The sandbox keeps its dated,
  `##`-grouped log — it has bash and `date +%F`, so it can. The two runtimes will
  therefore produce **different log shapes** from the same wiki. That is a
  deliberate consequence of the container's tool restriction, not drift to be
  reconciled later. Worth knowing before anyone runs both drivers against one
  `okf/`: a dated sandbox run and a dateless container run would interleave two
  formats in one file, and the sandbox's `##` date headings would remain valid
  while the container's flat entries sit above or below them.
- **`pi/container/agent/models.json`** — the `models` array that capped output at
  16,384 tokens is **already removed** in your working tree, matching the
  sandbox. Worth folding in while you are there: the file currently ends without
  a trailing newline.

## Verification

1. `make lint` — markdownlint over the new `SKILL.md` and the edited
   `AGENTS.md`, shellcheck over the edited driver.
2. `make validate` — required by [AGENTS.md](AGENTS.md) for any change under
   `pi/` or `scripts/`. Nothing under `pi/sandbox/` changes, so it should stay
   `VALID`.
3. Confirm the skill reaches the container (needs `OPENROUTER_API_KEY` set, but
   makes no model call):

   ```bash
   docker compose -f pi/container/compose.yaml build
   docker compose -f pi/container/compose.yaml run --rm -T --entrypoint sh pi \
     -c 'ls -l /home/node/.pi/agent/skills/compile-wiki/ && head -4 /home/node/.pi/agent/skills/compile-wiki/SKILL.md' </dev/null
   ```

   Expect `SKILL.md` non-empty with its frontmatter, and no `scripts/` directory.
4. Confirm no `okf-lint` reference survives on the container side:

   ```bash
   grep -rn "okf-lint" pi/container/agent/ scripts/compile-wiki-container.sh
   ```

   Expect no matches.
5. End-to-end on a cheap input rather than the 391 KB book in `md/`: put one
   short Markdown file in a scratch folder and run
   `./scripts/compile-wiki-container.sh <that-folder>`. In the transcript, check
   specifically that:
   - the agent issues a **`read` tool call on `SKILL.md`**, then one on
     **`SPEC.md`** — no failed `bash`/`cat` attempt in between. A blocked-tool
     error here is the signal that a `cat` fence survived somewhere;
   - `okf/index.md` declares an `okf_version` matching the spec's §11
     ("Versioning", `SPEC.md:391`) — proof the agent actually read the spec
     rather than working from memory;
   - new pages plus their `index.md` entries appear, with bundle-absolute links;
   - `okf/log.md` exists, carries a `# Update Log` heading, and has **no `##`
     headings and no dates**:

     ```bash
     grep -n '^## ' okf/log.md || echo "clean: no sub-headings"
     ```

   Run the driver a **second** time on a different short document and confirm the
   new entries land **above** the previous ones, and that the earlier entries are
   left untouched — that is the only real check of "newest first" and of
   idempotency.

   This writes into the real `okf/` (gitignored apart from `.okflintrc.json`), so
   snapshot `okf/` first if you want the current wiki back.
6. `make lint-okf` on the host — the independent check that replaces the
   in-agent lint gate the container cannot run. Watch specifically for
   **`log-date-format`** (severity `error`): any hit means the agent wrote a `##`
   heading in `log.md`, which is the one way this design fails the linter.
   `recommended-log` should now be silent, since `log.md` exists.
