# Move the four CLI tool guides out of `AGENTS.md` into per-tool skills

## Context

The Pi config states a clean split: **`AGENTS.md` holds what every task must
respect; each procedure lives in its own skill.** The four CLI tools have
drifted away from that — `inspectmd`, `inspectokf`, `sizeokf`, and `merkleokf`
each grew a `###` section inside `pi/files/home/.pi/agent/AGENTS.md`, so every
run pays for ~79 lines of tool procedure whether or not it uses those tools.

This change extracts each into its own skill under
`pi/files/home/.pi/agent/skills/`, leaving `AGENTS.md` as conventions plus a
skill list. Confirmed with the user: **all four convert now**, `AGENTS.md`
sections are **replaced by pointers** (not duplicated), and each skill teaches
**usage + workflow + limits**, not just flags.

Single source of truth matters: a section *and* a skill will drift the next time
a tool gains a flag (as `-L`/`--level` did this week).

## Constraints (from review)

1. **Skill name ≠ CLI name.** Directories/frontmatter use kebab skill ids
   (`inspect-okf`); every invocation in a skill must print the real binary
   (`` `inspectokf` ``, no hyphen). Agents must never try to shell `inspect-okf`.
2. **Skills are self-contained for the agent.** Tool `README.md` files are the
   source of truth for *authors* when writing or updating a skill. The agent
   must not need to open `sizeokf/README.md` mid-run.
3. **Keep each skill short** — roughly the content already in those `AGENTS.md`
   sections: a few example commands, column meanings where useful, and 2–4 limit
   bullets. Do not paste full project READMEs.
4. **`inspect-md` has a different workflow** from the three wiki tools. For
   `inspectmd`, `-L` is **heading** depth on a **file**, not directory depth on
   `okf/`. Do not copy-paste “`-L 1` then descend a folder”.
5. **`merkle-okf` needs before *and* after.** Change detection is useless with
   only a post-write check.

## New skills

Four directories, each a `SKILL.md` only (no scripts — the CLIs are already on
`PATH` via `setup.files` shims in `pi/spec.yaml`):

| Skill | CLI binary | Purpose |
| --- | --- | --- |
| `inspect-md` | `inspectmd` | heading map of a long `md/` source, for ranged reads |
| `inspect-okf` | `inspectokf` | wiki directory tree — what exists |
| `size-okf` | `sizeokf` | content chars excluding frontmatter — how much is written |
| `merkle-okf` | `merkleokf` | Merkle hashes — what changed |

Frontmatter matches `compile-okf/SKILL.md`: `name` (must equal the directory
name) and `description` that says **when** to reach for it — these are read
proactively, not only when a run names one.

Each `SKILL.md` has four short sections:

1. **Invocation** — binary name, flags, defaults, exit codes. Self-contained;
   draft from the tool’s `README.md`, then stop.
2. **Workflow** — tool-specific (see below).
3. **Reading the output** — what a row means. Move the `inspectmd` column table
   from Pi `AGENTS.md` verbatim into `inspect-md`. The other three keep the
   brief column notes already in their `AGENTS.md` sections.
4. **Limits** — honest caveats (the part `AGENTS.md` never had room for):
   - `inspectokf` hides dotfiles (`.okflintrc.json` invisible); slugs are lossy;
     a listed page may still be unreachable if no `index.md` links it (`okf-lint`
     does not catch that either).
   - `sizeokf` counts content only — says nothing about frontmatter.
   - `merkleokf` hashes raw bytes (a timestamp bump counts); a moved hash proves
     *that* something changed, never that it is correct.
   - `inspectmd` maps ATX headings only; the map plans reads — it is not
     permission to paraphrase (fidelity still governs).

### Workflows (do not conflate)

**Wiki tools** (`inspect-okf`, `size-okf`, `merkle-okf`): shallow-first on
directories — `CLI -L 1`, then descend into the one path that matters. Default
path `okf/`; `-L`/`--level` must be ≥ 1; `merkleokf` also accepts a single file.

**`inspect-md`:** map → cut → read.

```bash
inspectmd -L 2 md/<document>.md          # heading map (level cap)
inspectmd --section N md/<document>.md   # line range for one section
# then ranged-read that span — never pull a whole book into one call
```

## `pi/files/home/.pi/agent/AGENTS.md`

- **Delete the four `###` tool sections** between `### Slugs and file names` and
  `### Idempotency` (do not rely on line numbers; they drift).
- **Extend the skill list** so each entry says when to read it:

  ```markdown
  - Available skills:
    - `compile-okf` — compile a Markdown source document from `md/` into the
      wiki under `okf/`.
    - `inspect-md` — map a long source under `md/` before reading it in ranges.
    - `inspect-okf` — survey what the wiki already contains, before writing.
    - `size-okf` — measure how much prose a page or category holds.
    - `merkle-okf` — confirm which pages a run actually changed.
    - `context7-docs` — fetch current library/framework docs via Context7 …
  ```

- One sentence under the list: tool skills are read **when the work calls for
  them**, not only when a run names one.

## `compile-okf/SKILL.md` — wire the skills into the procedure

Extraction alone is not enough; the main task must open them.

- **Step 3 (survey)** — read `inspect-okf` (and `size-okf` when judging whether a
  page or category is thin). Also **capture a `merkleokf -L 1` baseline** (save
  or keep the listing) before writing.
- **Step 4 (write)** — point at `inspect-md` for long sources in ranges,
  reinforcing “Write in bounded chunks”.
- **Step 7 (verify)** — after lint, re-run `merkleokf -L 1` and compare to the
  step-3 baseline; descend only where hashes moved. **Lint remains the gate that
  must pass**; merkle confirms edits landed where intended, not correctness.

## Repo wiring

- `tests/test-sandbox-guest.sh` — after the `compile-okf` checks, add
  `check_file` for each new `SKILL.md`. Config is copied at kit build time; a
  layout slip otherwise leaves Pi with no skill and no error.
- Root `AGENTS.md` (split paragraph) — name the four tool skills and state the
  rule: **a tool gets a skill, not an `AGENTS.md` section.** Keep
  `context7-docs`.
- `README.md` (parallel sentence about task/helper skills) — same update.
- `pi/spec.yaml` — no change required; Installed tools already name the CLIs,
  and the compile-okf skill bullet stays correct.

## Verification

```bash
make validate    # REQUIRED: pi/ changed
make lint        # markdownlint + cspell over the new SKILL.md files
```

Faithfulness checks:

```bash
# No leftover tool procedure in Pi AGENTS.md (skill-list lines only —
# those use skill ids like inspect-okf, not the CLI binary names)
rg -n 'inspectmd|inspectokf|sizeokf|merkleokf' pi/files/home/.pi/agent/AGENTS.md
# expect: no matches

# Frontmatter name matches directory
for d in pi/files/home/.pi/agent/skills/*/; do
  echo "$(basename "$d"): $(rg -N '^name:' "$d/SKILL.md")"
done

# Every command printed in a SKILL.md works (install CLIs first if needed)
inspectmd -L 2 md/GoogleStyleGuide.md | head -3
inspectokf -L 1
sizeokf -L 1 | head -3
merkleokf -L 1 | head -3
```

Smoke the invocations once against a real `okf/`: the `-L 1` wiki forms should
show 15 rows. Every example in a skill is agent-facing — run it before finishing.

Fresh sandbox (new files under `pi/files/`, guest checks new paths):

```bash
sbx rm --force md2okf && make test-sandbox
```
