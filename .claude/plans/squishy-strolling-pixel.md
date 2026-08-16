# Move the four CLI tool guides out of `AGENTS.md` into per-tool skills

## Context

The Pi config states a clean split (root `AGENTS.md:78`): **`AGENTS.md` holds
what every task must respect; each procedure lives in its own skill.** The four
CLI tools have drifted away from that — `inspectmd`, `inspectokf`, `sizeokf` and
`merkleokf` each grew a `###` section inside `pi/files/home/.pi/agent/AGENTS.md`,
so it now carries 79 lines of tool procedure (lines 152–230) that every run pays
for whether or not it touches those tools.

This change extracts each into its own skill under
`pi/files/home/.pi/agent/skills/`, leaving `AGENTS.md` as pure convention plus a
skill list. Confirmed with the user: **all four convert now** (not just
`inspectokf`), the `AGENTS.md` sections are **replaced by pointers** rather than
duplicated, and each skill teaches **usage + workflow + limits**, not just flags.

Single source of truth is the point: with a section *and* a skill, the two drift
apart the next time a tool gains a flag — as `-L`/`--level` was added to three of
them this week.

## New skills

Four directories, each a `SKILL.md` only (no scripts — unlike `compile-okf`,
these wrap CLIs already on `PATH` via the `setup.files` shims in `pi/spec.yaml`):

| Skill | Tool | Purpose |
| --- | --- | --- |
| `inspect-md` | `inspectmd` | heading map of a long `md/` source, for ranged reads |
| `inspect-okf` | `inspectokf` | wiki directory tree — what exists |
| `size-okf` | `sizeokf` | content chars excluding frontmatter — how much is written |
| `merkle-okf` | `merkleokf` | Merkle hashes — what changed |

Frontmatter matches `compile-okf/SKILL.md:1-4` — `name` and `description`, where
the description says **when** to reach for it, since these are read proactively
rather than named by a run.

Each `SKILL.md` carries four sections:

1. **Invocation** — flags, defaults, exit codes. Source of truth is each tool's
   own `README.md` (e.g. `inspectokf/README.md`), already accurate and current.
2. **Workflow** — the shallow-first pattern: `-L 1`, then descend into the one
   directory that matters. All four share `-L`/`--level`, default `okf/`
   (`inspectmd` takes a file), and reject a level below `1`.
3. **Reading the output** — what a row means, carried over from the prose being
   removed from `AGENTS.md` (the `inspectmd` column table at lines 162–171 moves
   verbatim).
4. **Limits** — the honest caveats, which is the part `AGENTS.md` never had room
   for:
   - `inspectokf` hides dotfiles, so `.okflintrc.json` is invisible; slugs are
     lossy (`1981.md`, `exams.md` say nothing about content); and **a page listed
     here may still be unreachable in the wiki** if no `index.md` links it —
     `okf-lint` does not catch that either.
   - `sizeokf` counts content only, so it says nothing about frontmatter.
   - `merkleokf` hashes raw bytes, so a timestamp bump counts as a change; and a
     moved hash proves *that* something changed, never that it is correct.
   - `inspectmd` maps ATX headings only, and the map is a plan for reads — not
     permission to paraphrase source prose (the fidelity rule still governs).

## `pi/files/home/.pi/agent/AGENTS.md`

- **Delete lines 152–230** — all four `###` tool sections. `### Slugs and file
  names` (147) then runs straight into `### Idempotency` (232).
- **Extend the skill list** (lines 18–22) to six entries. Each line must say when
  to read it, because nothing in a run will name these:

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

- Add one sentence under that list: tool skills are read **when the work calls
  for them**, not only when a run names one.

## `compile-okf/SKILL.md` — wire the skills into the procedure

The extraction exposes a gap already noted when reviewing this skill: step 3 says
"Survey the existing wiki" with no method attached, and step 7 verifies with
`okf-lint` only.

- **Step 3** — point at `inspect-okf` (and `size-okf` where judging whether a
  page is thin).
- **Step 4** — point at `inspect-md` for reading long sources in ranges, which
  reinforces the existing "Write in bounded chunks" section.
- **Step 7** — add `merkle-okf` as a check that the edits landed where intended,
  alongside the existing lint gate. Keep lint as the gate that must pass.

## Repo wiring

- `tests/test-sandbox-guest.sh` — after the `compile-okf` checks (lines 95–96),
  add a `check_file` for each of the four new `SKILL.md` paths. Config is copied
  at kit build time, so a layout slip otherwise leaves Pi with no skill and no
  error.
- `AGENTS.md` (root, lines 78–83) — the split paragraph currently reads "Task
  skill today: `compile-okf`. Helper skill: `context7-docs`". Rewrite to name the
  four tool skills and state the rule: **a tool gets a skill, not an `AGENTS.md`
  section.**
- `README.md` (~line 112) — same update to the parallel sentence.
- `pi/spec.yaml:31` needs no change; it names the `compile-okf` skill only, which
  is still correct.

## Verification

```bash
make validate    # REQUIRED: pi/ changed
make lint        # markdownlint + cspell over the new SKILL.md files
```

Then confirm the extraction is faithful and complete:

```bash
# No tool guidance left behind in AGENTS.md
rg -n 'inspectmd|inspectokf|sizeokf|merkleokf' pi/files/home/.pi/agent/AGENTS.md
# expect: only the skill-list lines

# Every skill has frontmatter with a name matching its directory
for d in pi/files/home/.pi/agent/skills/*/; do
  echo "$(basename "$d"): $(rg -N '^name:' "$d/SKILL.md")"
done

# Every command shown in a SKILL.md actually works
inspectmd -L 2 md/GoogleStyleGuide.md | head -3
inspectokf -L 1
sizeokf -L 1 | head -3
merkleokf -L 1 | head -3
```

That last check matters: these files teach an agent to run commands, so every
invocation printed in them must be executed once against the real wiki. The
`-L 1` forms should show 15 rows for `okf/`.

Finally, on the host — new files under `pi/files/`, copied at kit build time, and
the guest test now checks four paths that only exist in a fresh sandbox:

```bash
sbx rm --force md2okf && make test-sandbox
```
