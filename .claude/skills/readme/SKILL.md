---
name: readme
description: Write, restructure, review or improve README.md files. Use whenever the user mentions a README, asks how to document a project, asks for a project description or "front page", is open-sourcing a repository or preparing a package for release, or wants a repo made approachable to new users and contributors — and also whenever you are about to create or substantially edit a README as part of some other task, even if the user never used the word "README".
---

A README is an evaluation document, not a manual. The reader's task in the
first thirty seconds is to work out whether to *disqualify* the project.
Structure for fast, honest disqualification, not for persuasion.

The failure mode of a generated README is not bad prose. It is fluent,
well-formatted and unverified. Weight verification at least as heavily as
composition.

## Grounding rules

These are constraints, not suggestions.

1. **Read before writing.** The manifest, the license file, the CI config, the
   tests, existing docs, and the current README if there is one. A README
   written without reading the repository is the defining artefact of the slop
   problem.
2. **Every claim traces to an artefact.** If you cannot point at the file that
   establishes a claim, the claim does not go in.
3. **Flag, do not fabricate.** Where a human must supply something the repo
   cannot provide — support channel, roadmap, maintainer contact, the
   motivation behind a design decision — leave a visible `<!-- TODO: … -->`
   marker and say so in your response. Silent invention is the failure;
   visible gaps are not. One gap outranks the others: a repo with no license
   file cannot legally be reused, so raise that as blocking rather than
   listing it alongside cosmetic TODOs.
4. **Preserve the author's voice.** When improving an existing README, make
   the smallest change that fixes the identified defect. Many good READMEs are
   idiosyncratic — humour, opinion, a personal register. Normalising them into
   template voice is a regression even when the structure improves.

## Workflow

1. **Classify the repository type.** Read `references/repo-types.md` and use
   only the section that applies. Applying library structure to a non-library
   project is the single biggest weakness of template-driven READMEs.
2. **Extract the facts.** Work through the facts table in
   `references/verification.md` before drafting a line. Almost everything a
   README asserts is derivable from manifests, workflow files and tests.
3. **Decide the mode.** Creating from scratch, or improving what is there? If
   improving, diagnose specific defects and make targeted edits. Do not
   rewrite a working README to impose a preferred shape. **Reorder before you
   reword.** Moving setup plumbing and contributor detail below the quick
   start usually fixes the largest reader problem on its own, and it costs
   none of the author's existing prose. Only then consider wording.
4. **Draft the first screen first**, and iterate the one-line description
   explicitly. It is the highest-leverage sentence in the repository and the
   one most worth spending tokens on. Read `references/prose.md` before
   writing sentences — structure decides whether a README is usable, prose
   decides whether it is trusted.
5. **Select sections by applicability**, not by template completeness. Prefer
   omitting a section to stubbing it. An empty heading is worse than no
   heading — it signals abandonment.
6. **Ground the examples.** Pull usage snippets from `examples/`, tests or
   doctests, ideally code that CI executes. Do not invent them.
7. **Verify** against the checklist in `references/verification.md`.
8. **Report** what you verified, what you assumed, and what the human must
   fill in.

Derive what you can. Ask at most **one** consolidated question — usually about
motivation, target audience or support channel — and `TODO`-flag the rest.
Interrupting the user twice costs more than it is worth.

## The first screen

Everything above roughly 25 rendered lines. It must answer: what is this, and
is it for me.

1. **Title** — `# project-name`, matching the repository and published package
   name exactly. Explain any mismatch.
2. **One-line description** — under 120 characters, no heading, plain
   sentence. Name the *category* of thing it is ("a CLI for…", "a Rust library
   that…") and its distinguishing property.
3. **Badges** — three to five, one line, each answering a question a user
   actually has at decision time. Never stack rows.
4. **Two to four sentences of context** — the *why*. What problem, for whom,
   and what the alternatives are. This is the most commonly missing element in
   real READMEs. Write it even when it feels obvious to you. Give every piece
   of project jargon and every named tool, format or concept a short gloss or
   a link on first use — a niche project's own vocabulary is invisible to its
   author and opaque to everyone else.
5. **Quick start** — the install command and a minimal working example that
   produces visible output, as one continuous block.

Test: a competent developer in the target ecosystem, reading only this, can
correctly decide to keep reading or leave, and would not feel misled either
way.

## Body and tail

A menu, not an outline. Below are the sections that *can* exist, in the order
they go when they are present. **Most repos need fewer than half of them.**
Pick by what the repository actually supports. An empty heading is worse than
a missing one — it signals abandonment.

- Table of contents — only above about 100 lines.
- Features — a short list, each item verifiable in the code. Cut anything
  aspirational.
- Installation, expanded — prerequisites with version ranges, platform notes,
  alternative channels, and a verification step. State the prerequisites
  rather than implying them; ecosystem fluency the author has and the reader
  lacks is where "run `make install`" goes wrong.
- Usage — progressively fuller examples, each runnable as written, each
  showing expected output. Commands go in a fenced block with no leading `$`
  prompt, so a reader can select and paste the whole block; expected output
  goes in its own `text` block rather than mixed in with the commands.
- Configuration — options, environment variables, config schema.
- API reference, or a link to one. Never paste generated API docs in.
- How it works — a paragraph or a Mermaid diagram, for anything non-obvious.
- Limitations and caveats — when you know of real ones. Never invent them to
  fill the section.
- Comparison with alternatives — say honestly when to prefer them.
- Roadmap or project status — only if one already exists in writing.

Every tail section is gated on an artefact that already exists in the repo. No
artefact, no section:

- Contributing — needs `CONTRIBUTING.md`, issue templates, or a history of
  accepted pull requests.
- Security — needs `SECURITY.md`. Link it; do not restate it.
- Support — needs a real channel: issue tracker, discussions, chat. State
  response expectations honestly ("side project, replies may be slow").
- Maintainers — needs `CODEOWNERS`, `MAINTAINERS.md` or manifest `authors`.
  Who to ping, one contact route each. Skip it when the repo has one obvious
  owner the title already makes clear.
- Acknowledgements — only when there is something specific to credit.

## Settled questions

- **Install before usage, or after?** Neither. Use one combined quick start
  showing install and first successful use as a continuous block.
- **Length.** Not a word count. The README owns evaluation, first success, and
  where to go next. A section serving none of those three moves out of the
  file — see Scope for where it goes. Most single-purpose libraries need
  60–150 rendered lines, not 400.

## What not to produce

These read as unreviewed generated output and cost the maintainer trust:

- An emoji on every `##` heading.
- The exact sequence Features → Installation → Usage → Contributing → License
  in neutral marketing voice, with no section that required reading the code.
- Badge rows that convey nothing a user needs.
- Feature tables generated from the directory listing, describing files rather
  than capabilities.
- "Blazingly fast", "production-ready", "enterprise-grade", "seamlessly" —
  where no benchmark, no deployment and no enterprise exist. Everybody claims
  these, so none of them carries information. Cut them and let the facts do
  the work.
- A Contributing section on a repo with no `CONTRIBUTING.md`, no issue
  templates and no history of accepted pull requests.
- Sections of uniform length regardless of whether there is anything to say.
- Project jargon used before it is defined, and prerequisites left implied.
- Confident specifics that were never checked: version numbers, function
  signatures, config keys, CLI flags.
- Critical information carried only by a screenshot or GIF.

None of this calls for flat, opinion-free prose. A README may carry a point of
view, an argument, even a joke. What it may not carry is marketing filler and
superlatives nobody checked. Aim for prose that reads as though a person who
understands the project wrote it — `references/prose.md` is how.

The goal is not output that *looks* good. It is output a maintainer would not
have to check.

## Scope

`README.md` is for humans evaluating or onboarding. Content that serves none
of evaluation, first success, or where-to-go-next moves out of the file. It
does not get deleted, and it does not get compressed into a stub:

- **`docs/<topic>.md`** — the default destination for whatever the README
  outgrew: the full configuration reference, deployment and setup guides,
  troubleshooting, architecture notes, migration guides. Create `docs/` in the
  repository root if it does not exist yet. Name each file for its topic —
  `docs/configuration.md`, `docs/deployment.md` — and never `docs/README.md`,
  which the platform treats as a README candidate and which can shadow the
  real one.
- **`CONTRIBUTING.md`** — build steps, test invocations, the release process,
  and anything else aimed at people changing the code.
- **`AGENTS.md`** — operational instructions for coding agents: setup
  commands, lint rules, project constraints.
- **`CHANGELOG.md`** — version history. Never inline it.

A move is a two-part edit and both halves are mandatory: write the content
into the new file intact, then replace the README section with a one-line
pointer that links to it. Content that leaves the README without landing
somewhere has been deleted rather than moved, and deletion is a change the
user did not ask for. Name every file you created and every section you
relocated in your report.
