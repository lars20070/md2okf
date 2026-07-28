---
name: compile-wiki
description: Compile one Markdown source document from md/ into the OKF wiki under okf/. Use when a run asks you to create or update the wiki from a source document.
---

# Compile a source document into the OKF wiki

Translate one Markdown source document under `md/` into well-structured OKF
pages under `okf/`. You are invoked **once per source document**: integrate that
document into the existing wiki without disturbing unrelated pages.

The OKF conventions in `AGENTS.md` — page frontmatter, `index.md` link lists, the
update log format, kebab-case slugs, bundle-absolute links, idempotency — apply
to everything you write here and are not restated below.

## Procedure

1. **Read `SPEC.md`** at the workspace root before writing anything, using your
   **`read` tool** (there is no `bash` tool here, so `cat` is not an option).
   Read it in full — if the call truncates, continue with `offset`/`limit` — and
   follow the revision you read.
2. **Read the source document** named in your prompt. It is read-only material
   under `md/` — never modify it.
3. **Survey the existing wiki** before writing. Look for pages that already
   cover the topics in this document; updates are idempotent, so update those in
   place rather than creating a second page on the same topic.
4. **Write the content pages**, organised into directories by topic, each with
   the frontmatter required by `AGENTS.md`. Observe the fidelity rule below and
   write in bounded chunks — see "Write in bounded chunks".
5. **Regenerate the affected `index.md` link lists** — the page's own directory
   index and any parent index that must link to it — so navigation stays
   correct.
6. **Prepend to `okf/log.md`**, one entry per page you created or updated,
   inserted directly beneath the `# Update Log` heading so the newest entries
   come first. Write **no date and no `##` heading** — see "Update log" in
   `AGENTS.md`. Create the file if it does not exist.

## Write in bounded chunks

A tool call is part of your reply, so it is subject to the same output limit as
your prose. If you try to write a long page in one `write` call, the call is cut
off mid-argument, fails validation (typically `must have required properties
path`), and **all of that content is lost** — nothing reaches disk.

- Build a long page **incrementally**: `write` the frontmatter plus the first
  section, then `edit` the file to append the next section, and so on. Each call
  should carry a section or two, not a whole chapter.
- Read long sources the same way — in ranges, rather than pulling an entire book
  into one call. Your `read` tool takes `offset` and `limit` for exactly this.
- If a call does get truncated, do not retry it unchanged. Split the content and
  write it in smaller pieces.

## Fidelity

- **Preserve the source prose verbatim.** Do not paraphrase, summarise, or
  rewrite the substance of the source. Structure and annotate it; never alter its
  wording.
