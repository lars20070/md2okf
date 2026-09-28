---
name: curate-okf
description: Check the wiki against the OKF spec and its curation health, and maintain nodes and indexes without breaking links. Use before finishing a run, and whenever adding, moving or removing a page.
---

# Curate the wiki with `okfctl`

Use the `okfctl` CLI (on `PATH`) to check the wiki and to maintain its nodes and
reserved `index.md` files. The skill name is `curate-okf`; the binary is
`okfctl` — never shell the skill id.

## Invocation

```bash
okfctl index build "$PWD"           # after adding, moving or removing a page
okfctl analyze "$PWD"               # where the wiki is weak — advice, never a gate
okfctl node mv old.md new.md --bundle "$PWD"   # rename, rewriting inbound links
```

- **Always name the wiki as `"$PWD"`.** You are already in the wiki root, and
  okfctl's own default is the current directory, but the explicit path keeps a
  command copied into a skill or a log unambiguous.
- `index build` **owns every `index.md`** — never hand-edit one. It regenerates
  the link lists from what is on disk, so an index can never promise a page that
  does not exist.
- `node mv` rewrites every inbound link and preserves each link's existing form,
  so bundle-absolute prose links stay absolute.
- Allowed beyond the above: `validate`, `lint`, `bundle info`, `index check`,
  `node list|show|new|rm`, `search`, `graph export`, `template list|show`,
  `version`.
- Exit codes: `0` ok, `1` findings, `2` usage or runtime error.

## Workflow

Write the pages first, then `okfctl index build`, then the gate —
`~/.claude/skills/compile-okf/scripts/check-okf.sh`, which runs `validate`,
the frontmatter guard, `lint`, the dangling-link check and `index check` in one
pass. Rebuild the index *before* the gate: `index check` fails closed, so a page
added without a rebuild is reported as both a stale index and an orphan.

`okfctl node new` writes `created`/`modified`, **not** the `generated: { by, at }`
this wiki uses — fill the frontmatter in yourself afterwards, as `CLAUDE.md`
describes. The guard catches it if you forget.

## Reading the output

`lint` findings come in two classes, and the gate treats them differently:

| Class | Checks | What to do |
| --- | --- | --- |
| Defect | `broken-link`, `orphan`, `type-hygiene`, `status-lifecycle`, `spec-version` | **Blocks the run.** Each has one correct fix — repair the path, link or rebuild the index. |
| Judgment | `missing-xref`, `coverage-gap` | Printed, never blocking. Act on it when the wiki genuinely reads better for it. |

`analyze` is a report, not a gate: thin pages, uncited pages and tag clusters are
prompts for judgment. It exits `0` however much it finds.

## Limits

- **Never run `log append` or `log show`.** They write a second `# Change Log`
  heading in a flat format that contradicts the spec's dated `##` headings. Write
  `log.md` by hand, as `CLAUDE.md` describes.
- **Never run `migrate`, `eval`, `serve`, `registry`, `connect`, or anything
  semantic** (`okfctl-search`, `lint --semantic`). `migrate` is a one-off the
  maintainers have already run; the rest need a network or a model this sandbox
  does not have.
- A clean gate means the wiki is well-formed and well-linked. It says nothing
  about whether the prose is faithful to the source — that is `compile-okf`'s
  fidelity rule, and it outranks a clean report.
