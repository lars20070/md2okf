# Move the Ralph pass loop into the Pi agent with `ralph-loop-pi`

## Context

[scripts/compile-wiki.sh:85-120](scripts/compile-wiki.sh#L85-L120) is a host-side
Ralph loop: for one source document it runs `sbx exec … pi -p …` repeatedly, each
run a fresh Pi process with a fresh context, resuming from what the previous run
left in `okf/`, stopping when a pass adds no bytes or `MAX_PASSES` is reached.

The goal is to run that loop **inside** the Pi agent instead, using a Pi package.
The package is [`ralph-loop-pi`](https://pi.dev/packages/ralph-loop-pi) v1.0.5,
which registers an agent-callable `ralph_loop` tool that runs each iteration as a
**subagent** and evaluates a shell `conditionCommand` between iterations —
stdout `true` continues, anything else stops. That maps onto the current design
almost exactly: subagent-per-iteration preserves fresh context per pass, and
`conditionCommand` is where the byte fixpoint goes.

Two earlier, still-uncommitted plans in this tree
([.cursor/plans/ralph-loop-redesign.md](.cursor/plans/ralph-loop-redesign.md) and
[.claude/plans/sprightly-stargazing-sparrow.md](.claude/plans/sprightly-stargazing-sparrow.md))
argued the opposite direction — a *host-side* Python driver — on the grounds that
a loop the agent controls cannot be an independent oracle of its own progress.
This plan keeps that objection answered rather than ignored: the stop condition
stays a **deterministic shell script the agent does not write**, and the host
keeps sandbox lifecycle, per-document iteration, and crash retry. What moves in
is the pass loop itself, nothing more.

## The one thing the research report does not cover

Pi's subagents **do not inherit the parent session's `AGENTS.md` or its skills**.
An agent definition is a Markdown file whose body *is* the subagent's entire
system prompt. `ralph-loop-pi` defaults to a bundled `worker` agent.

So without a kit-supplied agent definition, every pass would run with no OKF
conventions, no writable-directory boundary, and no `compile-wiki` skill — it
would silently produce garbage. `pi/files/home/.pi/agent/agents/wiki-pass.md` is
therefore not a nicety; it is what makes the whole thing work. It is kept short
and delegates by path so `AGENTS.md` and `SKILL.md` stay the single source of
truth rather than being duplicated into a third file.

## What moves, what stays

```text
HOST  scripts/compile-wiki.sh                 (stays)
 ├─ sbx rm --force / sbx run --detached       (stays, unchanged)
 └─ for document in md/*.md                   (stays, unchanged)
     └─ retry ≤ MAX_RETRIES, backoff          (stays — a provider 502 kills the
         │                                     whole in-VM loop, so the outer
         │                                     retry must survive it)
         └─ sbx exec md2okf -- pi -p "…call ralph_loop…" </dev/null
              ▼ VM
              ralph_loop tool                 ← was lines 85-120
                ├─ iter 1 → subagent wiki-pass (FRESH context) → one compile pass
                │    conditionCommand → "true"
                ├─ iter 2 → subagent wiki-pass (FRESH context) → one compile pass
                │    conditionCommand → "true"
                └─ iter 3 → subagent wiki-pass (FRESH context) → one compile pass
                     conditionCommand → ""   ⇒ loop ends, pi exits
```

`MAX_PASSES` is enforced **inside the gate script**, not only via the tool's
`maxIterations` argument. `maxIterations` defaults to `Number.MAX_SAFE_INTEGER`
when omitted, so if the model ever drops that argument the loop would otherwise
run unbounded. The gate owns the hard cap; `maxIterations` is belt-and-braces.

## Step 0 — spike first, in a throwaway sandbox

Four things are undocumented and each has a defined fallback. Do this before
writing anything, via `./scripts/bash.sh`:

| # | Question | How to check | Fallback if it fails |
|---|---|---|---|
| 1 | Exact `ralph_loop` parameter names/types | `pi install npm:ralph-loop-pi@1.0.5`, then read the installed `~/.pi/agent/npm/**/ralph-loop.ts` `registerTool` schema | none needed — read the schema and use it |
| 2 | Does the tool run under `pi -p`? (extensions do; subagent spawning in print mode is unverified) | `pi -p "call ralph_loop with prompt 'echo hi', conditionCommand 'echo', maxIterations 1"` `</dev/null` | fall back to `--mode json` and parse; if the tool cannot spawn subagents headlessly at all, the package is unusable → revert to the host loop |
| 3 | Is `conditionCommand` evaluated **before** iteration 1 or only between iterations? | count gate invocations vs iterations in the spike above | gate counts its own invocations and stops at `> max_passes`, so an off-by-one under-runs nothing either way |
| 4 | Does the package write state into the workspace (e.g. `.ralph/`)? | `git status` in the VM after a spike loop | add the directory to `.gitignore` |

Also confirm `pi list` shows the extension enabled after install. If it does not,
add its path to the `extensions` array in the kit's `settings.json` (see step 2).

## Changes

### 1. `pi/spec.yaml` — install the package at kit build time

Add a third entry to `setup.install`, following the existing retry-loop pattern
verbatim (`user: "1000"`, 5 attempts, `--fetch-timeout`), pinned:

```yaml
    - command: >-
        RALPH_LOOP_VERSION=1.0.5;
        attempt=1;
        until pi install "npm:ralph-loop-pi@${RALPH_LOOP_VERSION}"; do
        …same retry shape as the okf-lint block…
        done
      user: "1000"
      description: "Install the ralph-loop-pi extension (the in-agent pass loop)"
```

`pi install` runs `npm install` under the hood and lands the package in
`~/.pi/agent/npm/`. No `permissions.network.allow` change is needed:
`registry.npmjs.org` and `pi.dev` are already on the allowlist. **Nothing else
can be installed** — the allowlist has no distro repos, so anything not on npm
is out of reach.

### 2. `pi/files/home/.pi/agent/settings.json` — only if spike #1 requires it

`pi install` mutates `settings.json`, and the kit copies its own `settings.json`
over `~`; depending on whether the copy runs before or after `setup.install`,
that mutation may be clobbered. If `pi list` does not show the extension, make it
order-independent by declaring the path explicitly:

```json
{
  "defaultProvider": "openrouter",
  "defaultModel": "qwen/qwen3.6-35b-a3b",
  "extensions": ["<path confirmed in step 0>"]
}
```

`make lint` runs `jq empty` over every tracked JSON file, so keep it valid.

### 3. `pi/files/home/.pi/agent/agents/wiki-pass.md` — **new, load-bearing**

The subagent definition each iteration runs as. Frontmatter takes `name`,
`description`, and optionally `tools` / `model` / `thinking`; **omit `tools`** so
the subagent inherits the parent session's active tools (it needs read, write,
edit and bash). The body is the whole system prompt, so it delegates by path
instead of restating conventions:

```markdown
---
name: wiki-pass
description: Runs one pass of the compile-wiki loop over a single source document.
---

You are one pass of a multi-pass wiki compile. You do not inherit the parent
session's configuration, so read these two files first, in this order, and follow
them:

1. `~/.pi/agent/AGENTS.md` — the OKF conventions and your writable directories.
2. `~/.pi/agent/skills/compile-wiki/SKILL.md` — the procedure for this task.

`SPEC.md` at the workspace root outranks both; read it as `AGENTS.md` instructs.

Earlier passes may already have done most of the work. `okf/` on disk is the
record of what is done — compare the source against it and continue at the first
gap. Never start over. Ending a pass part-way through a document is expected;
leave the wiki clean and honest rather than complete-looking.
```

Discovery order is bundled → user → project, so this **user** agent sits
alongside the package's bundled `worker` and is selected by passing
`agent: "wiki-pass"`. If the spike shows the model drops that argument
unreliably, name the file `worker.md` instead so it *overrides* the bundled
default and is used even when the argument is omitted.

### 4. `pi/files/home/.pi/agent/skills/compile-wiki/scripts/coverage-gate.sh` — new

The `conditionCommand`. This is the ported byte fixpoint from `wiki_size()`
([scripts/compile-wiki.sh:71-77](scripts/compile-wiki.sh#L71-L77)), with two
changes that the port cannot do without. Modelled on the sibling
[lint-okf.sh](pi/files/home/.pi/agent/skills/compile-wiki/scripts/lint-okf.sh):
`set -euo pipefail`, usage block, documented contract.

```bash
#!/usr/bin/env bash
set -euo pipefail

# Loop condition for ralph-loop-pi's `ralph_loop` tool.
#
# Usage: coverage-gate.sh <source> <max-passes> [bundle]
#
# CONTRACT: print exactly `true` on stdout to run another iteration; print
# anything else — including nothing — to stop the loop. Every diagnostic
# therefore goes to stderr, and the script always exits 0: the loop reads
# stdout, and a non-zero exit is not part of its contract.

source_document="${1:?usage: coverage-gate.sh <source> <max-passes> [bundle]}"
max_passes="${2:?usage: coverage-gate.sh <source> <max-passes> [bundle]}"
bundle="${3:-./okf}"

# State lives outside the workspace, so nothing lands in the host working tree,
# and it survives a host-side retry into the same sandbox — which is what makes
# MAX_PASSES a bound on the whole compile rather than on one lucky streak.
state_dir="${HOME}/.cache/md2okf"
state_file="${state_dir}/$(printf '%s' "${source_document}" | tr -c '[:alnum:]' '-').state"
mkdir -p "${state_dir}"

# Total bytes of wiki content. log.md is EXCLUDED: AGENTS.md requires every pass
# to append to the log, so a metric that counted it would grow on every pass and
# the fixpoint could never fire.
wiki_size() {
	if [[ ! -d "${bundle}" ]]; then
		echo 0
		return
	fi
	find "${bundle}" -name '*.md' ! -name log.md -exec cat {} + | wc -c | tr -d ' '
}

previous=-1
checks=0
[[ -f "${state_file}" ]] && read -r previous checks < "${state_file}"

current="$(wiki_size)"
checks=$((checks + 1))
printf '%s %s\n' "${current}" "${checks}" > "${state_file}"

if [[ "${checks}" -gt "${max_passes}" ]]; then
	echo "gate: reached MAX_PASSES (${max_passes}); stopping." >&2
	exit 0
fi
if [[ "${current}" -eq "${previous}" ]]; then
	echo "gate: pass added nothing; ${source_document} is done." >&2
	exit 0
fi
echo "gate: pass ${checks}, ${current} bytes (was ${previous}); continuing." >&2
echo true
```

Two deviations from a literal port, both required:

- **`log.md` is excluded.** `AGENTS.md` mandates "Every run appends to the log",
  so the current host metric grows on every pass by construction — the fixpoint
  it implements can only ever fire by accident. A literal port would never
  terminate.
- **A persisted counter enforces `MAX_PASSES`.** Today the host owns the pass
  count; once the loop is inside the VM, nothing else can bound it.

### 5. `scripts/compile-wiki.sh` — replace lines 85-120

Delete `wiki_size()` (lines 71-77) and the `while` loop; keep the sandbox
lifecycle, the `for` loop, `MAX_RETRIES`, and the backoff. The body becomes one
guarded exec:

```bash
	if ! sbx exec "${kit_name}" -- pi \
		-p "Start the compile loop for ${document}. Call the ralph_loop tool exactly once, with agent \"wiki-pass\", a prompt telling the subagent to compile ${document} into the OKF wiki under okf/ (this may be a continuation — compare the source against what is on disk and continue at the first gap, do not start over), conditionCommand \"\$HOME/.pi/agent/skills/compile-wiki/scripts/coverage-gate.sh ${document} ${max_passes}\", and maxIterations ${max_passes}. Do not compile anything yourself — the tool's subagents do the work. When it returns, report the iteration count and stop." \
		</dev/null; then
		# …existing retry/backoff/abandon block, unchanged…
	fi
```

Keep the `</dev/null` and its comment block (lines 61-65) exactly as is — the
stdin hazard is unchanged.

Add one check the host cannot do without any more: the model could return
without ever calling the tool. After a successful exec, assert the gate actually
ran, and treat "it did not" as a failed pass so the retry path handles it:

```bash
	if ! sbx exec "${kit_name}" -- test -f "\$HOME/.cache/md2okf/…state"; then
		# the loop never started — count it as a failure, not a success
	fi
```

Also fix the latent bug the loop already had while the code is open: reaching
`MAX_PASSES` with the wiki still growing prints a warning but does not increment
`failed_documents`, so the script exits 0 on a known-incomplete document
([scripts/compile-wiki.sh:115-118](scripts/compile-wiki.sh#L115-L118)). The gate
now owns that condition; surface it to the host by having the driver check the
persisted counter after the exec and count the document as failed when it hit
the cap.

Update the header comment block (lines 10-17): `MAX_PASSES` is now passed into
the VM and enforced by the gate; `MAX_RETRIES` still tolerates crashes of the
whole in-VM loop.

### 6. Supporting edits

- **`pi/files/home/.pi/agent/AGENTS.md`** — under "Workspace boundaries", note
  that `~/.cache/md2okf/` is loop state written by the gate script, not by the
  agent, and is not part of the wiki. Add `wiki-pass` to the "Available skills"
  area as the agent the pass loop runs as.
- **`pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md`** — "The driver will
  run you again" (line ~348) is still true but now means the in-VM loop; adjust
  the wording and say that the loop stops when a pass adds no bytes outside
  `log.md`, so a pass that only rewrites the log reads as no progress. Leave the
  rest of the procedure alone.
- **`.gitignore`** — add whatever spike #4 shows the package writes into the
  workspace (likely `.ralph/`).
- **`.cspell.json`** — add `ralph`.
- **Docs** — `README.md` ("How the agent knows what to do", and the repo-map row
  for `md/` which still says "one Pi run each"), root
  [AGENTS.md](AGENTS.md) ("There is one today, `compile-wiki`" is no longer the
  whole story), and [pi/README.md](pi/README.md) (the "two pinned installs"
  sentence becomes three, plus a paragraph on the agents directory).

## Verification

1. **Static, mandatory.** `make lint` then `make validate`. The lint globs
   already cover the new files: `pi/files/home/.pi/agent/**/*.md` picks up
   `agents/wiki-pass.md`, and `skills/*/scripts/*.sh` picks up
   `coverage-gate.sh` — provided it lives in the skill's `scripts/` directory.
   `make validate` is required by `AGENTS.md` for any change under `pi/`.
2. **Gate script in isolation, on the host.** It is plain bash and needs no VM.
   Point it at a fixture and drive it by hand:

   ```bash
   HOME=/tmp/gate-test ./pi/files/home/.pi/agent/skills/compile-wiki/scripts/coverage-gate.sh \
     md/sample.md 3 ./okf
   ```

   Assert: prints `true` on first call; prints `true` after adding a page; prints
   **nothing** when only `okf/log.md` changed between calls; prints nothing on
   the call after the cap. This is the one part of the change that can be tested
   without a sandbox, and it is the part that decides termination — test it
   properly.
3. **Spike checks from step 0**, re-run against the real kit via
   `./scripts/bash.sh`.
4. **End-to-end, small.** `MAX_PASSES=2 make wiki` against a short document in a
   scratch `md/` folder. Confirm from the output that two subagent iterations
   ran, that the gate printed its stderr diagnostics, and that `okf/` is
   conformant: `make lint-okf`.
5. **End-to-end, real.** `make wiki` on `md/GoogleStyleGuide.md` (611 KB), the
   case the multi-pass design exists for. Confirm the loop terminates on the
   fixpoint rather than the cap, and that `okf/log.md` has one dated entry per
   pass.

CI cannot cover any of this — no job runs a real sandbox — so steps 3-5 are
manual and must actually be run before this is called done.

## Risks

- **`ralph_loop` may not spawn subagents under `pi -p`.** Undocumented; spike #2
  decides it. If it fails, `--mode json` is the next thing to try, and if that
  also fails the package is unusable here and the host loop stays.
- **The model must call the tool correctly.** Mitigated by the gate owning the
  hard pass cap (a dropped `maxIterations` cannot run away) and by the host
  asserting the gate ran at all.
- **The loop is now inside the thing it measures.** The gate script is the
  mitigation: the agent never writes it, never reads its own progress claim back,
  and cannot reach `~/.cache/md2okf/` through any instruction in the wiki.
- **Rollback is one revert.** All the host-side change is in
  `scripts/compile-wiki.sh`; the kit additions are inert if the driver stops
  calling `ralph_loop`.
