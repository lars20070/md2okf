# Port the wiki driver to Python and give it a real termination condition

## Context

`scripts/compile-wiki.sh` is a Ralph loop: stateless Pi invocations, same prompt every
pass, `okf/` on disk as the only memory. Its termination condition is one number —
`wiki_size()` at `scripts/compile-wiki.sh:71-77`, the total bytes of `okf/**/*.md`,
compared against the previous pass.

That number is not merely crude. It is **unreachable**:

- `wiki_size()` matches `okf/log.md`, and `pi/files/home/.pi/agent/AGENTS.md:135`
  mandates "**Every run appends to the log.**" Every pass therefore grows the byte
  count, `current -eq previous` can never hold, and the loop runs to `MAX_PASSES`
  on every document, every time. `make wiki` currently spends 20 Pi runs per
  document by construction — verified: `okf/log.md` is 5,850 bytes and is one of the
  107 files the metric concatenates.
- Byte count is a poor content hash. A pass that splits a page in two, rewrites a
  link, or swaps a same-length word scores as zero progress → false "done".
- Oscillation (pass N adds 100 bytes, N+1 removes 100) never satisfies *consecutive*
  equality → burns the budget.
- There is no quality signal. The four structural gates at
  `pi/files/home/.pi/agent/skills/compile-wiki/SKILL.md:440-459` run *inside* the
  agent and are self-reported; the driver verifies nothing.
- There is no completeness signal, and `SKILL.md:432-435` says why that matters:
  "an almost entirely empty bundle passes" the linter. An empty `okf/` passes all
  four gates too — verified, there is nothing for them to catch. So "quiescent +
  gates clean" would still call an 8%-complete wiki done, which is exactly the
  failure mode this work exists to fix (upstream `earendil-works/pi#7020`: the agent
  stops early believing it is finished).
- Latent bug: `MAX_PASSES` exhaustion at `scripts/compile-wiki.sh:115-118` only
  prints a warning. It does not increment `failed_documents`, so the script exits
  **0** on a document that never converged — a silent success on known-incomplete
  output.

The intended outcome: a driver that stops for a *reason* it can name — done, stuck,
undercovered, cycling, or budget-exhausted — and that is covered by tests.

## Options considered

### Option A — keep bash, extract only the termination decision into a Python oracle

Bash keeps the sbx lifecycle, per-document loop, retry/backoff and exit codes. A new
Python CLI runs once per pass, owns persisted state, returns a verdict via exit codes.

**Pros.** Smallest diff to a script whose sbx subtleties are hard-won. The complex
logic becomes testable. `make lint` already runs `$(RUFF) check .` repo-wide, so a
new `.py` is linted for free, and `shellcheck scripts/*.sh` still covers the bash.

**Cons.** The oracle must persist manifest history, cycle history and counters to
disk **purely because bash re-invokes a fresh interpreter each pass** — which buys a
schema, a version field, invalidation rules, a `.gitignore` entry and staleness bugs.
Worse, there is no good home for that file: inside `okf/` it is agent-writable (the
agent's `AGENTS.md` grants `okf/` as its only writable output), so the agent could
fabricate its own quiescence — fatal for an independent oracle; outside `okf/` it
survives `rm -rf okf/` and goes stale. Policy also smears: the oracle owns
manifest/cycle/gates while bash owns `MAX_PASSES`, `MAX_RETRIES`, backoff and the
aggregate exit code, so "when do we stop and what did it cost" is answered in two
files in two languages. A 4-verdict exit-code protocol with human-readable reasons
travelling out-of-band on stderr is stringly-typed with no shared enum and no test
spanning the boundary.

### Option B — port the whole driver to Python *(recommended)*

One `scripts/compile_wiki.py`, `subprocess.run` for sbx calls, a single `run_sbx()`
seam that tests monkeypatch with a scripted queue.

**Pros.** The persisted state file *disappears* — manifest history and counters are
within-invocation facts held in a list, so Option A's central liability evaporates
along with the tamper question. One place owns loop policy. Everything is testable
with infrastructure that already exists and is already wired into `make test` and CI.
The clean boundary turns out to be pure↔impure, not bash↔Python, and it lives inside
one module.

**Cons.** Biggest diff. Risks losing the sbx war-stories in translation — mitigated
by porting every comment verbatim. `make wiki` gains a uv dependency (already true of
`make scrape` and `make test`). SIGINT needs explicit handling.

### Option C — move the decision to the agent

`SKILL.md` requires each pass to write a machine-readable `status`/coverage JSON; the
driver reads it.

**Pros.** The richest possible signal: the agent knows what it *intended*, which no
disk diff can infer.

**Cons.** It trusts precisely the judgement this work exists to distrust — `pi#7020`
is "the agent stops early thinking it's done", so a self-reported
`status: complete` is the known-unreliable signal. It also needs a SKILL.md change
plus a kit rebuild, coupling driver and agent versions, and still requires an
independent check — so you build most of B anyway, plus a contract.

**Rejected as a verdict, kept as a future input.** A self-reported claim is worthless
as an authority and useful as a *contradiction detector*: "agent says incomplete" +
"agent changed nothing" = stuck, which quiescence alone cannot distinguish from done.
Out of scope here.

### Why B

The decisive argument is not aesthetics. There are no shell tests in this repo — I
searched the working tree, all ten local and remote branches, and full history — and
there is no plausible path to inventing them for a driver that shells into a microVM.
So under Option A the oracle's tests are Python **anyway**; A does not avoid a Python
suite, it just draws the line through the middle of the driver and leaves the half
containing retry, backoff, `MAX_PASSES` and exit codes permanently untestable. Those
are exactly the four behaviours PR #8's description claims are covered by
"stubbed-`sbx` tests" that do not exist (documented as a merge blocker in
`.cursor/plans/pr-8-merge-blockers.md:275-278`). Option A would ship a test suite and
still leave that claim false.

## Recommended design

### The termination condition

**Manifest.** Per pass, build `{repo_relative_path: sha256(normalised_body)}` over
`okf/**/*.md`. Change detection is manifest inequality, which catches adds, deletes,
renames, rewrites and splits that byte-count misses.

**Normalisation** — two rules, both load-bearing:

- Strip the `timestamp:` line, **only inside the frontmatter block**. A `timestamp:`
  in a fenced code block in the body is content. (Verified: `timestamp:` is the only
  volatile key, present on all 95 content pages; there is no `log:` key.)
- Exclude `okf/log.md` from the change manifest and hash it *separately*. This is the
  fix for the never-converges bug. Tracking it separately still lets the driver say
  "this pass changed only the log", which is correctly scored as no progress and is
  also a useful smell.

Stripping is defensible even though `recommended-log`, `log-date-order` and
`recommended-timestamp` are error-level in `okf/.okflintrc.json`: those rules govern
*conformance*, which okf-lint checks. The manifest answers *did content change*. The
error asymmetry justifies it — for a progress detector, false positives (fake
progress → burn the budget) are the expensive error; stripping volatile fields
removes guaranteed false positives and cannot create a false negative, because any
real edit changes the body too.

**Cycle detection** against the set of *all* previously seen manifest hashes, not
just the immediately previous one: a 3-cycle A→B→C→A is invisible to previous-only
comparison. Check quiescence *before* cycles so A→A is quiescence, not a cycle.

**Gates** — port the four from `SKILL.md:440-459` as stdlib filesystem/regex checks
returning `list[str]`, and add a fifth: a directory holding content pages but no
`index.md` (the dual of gate 1, which already excludes `index.md` when deciding
"empty"). Verified: all five pass on the current wiki, so the fifth won't
false-positive on real output. Highest-value use: **feed findings into the next
pass's prompt.** A pass told `GATE: EMPTY INDEX okf/foo/index.md` can fix it; a
driver that only reports at the end cannot.

**Coverage floor.** The driver's own comment at `scripts/compile-wiki.sh:55` already
asserts the property — "Fidelity means the wiki is about as large as the source" — so
compute `wiki_page_bytes / source_bytes`, excluding `index.md` and `log.md` from the
numerator. Verified on the real completed compile: **0.932** (569,799 / 611,332). A
`MIN_COVERAGE` default of `0.5` is a smoke alarm with enormous headroom. Always print
the ratio so an operator can calibrate, and word the failure as "probably
incomplete". `md/` holds exactly one source document today, so the global ratio is
exact; see Limitations for the multi-source case.

**No patience parameter.** Requiring N quiescent passes hedges against a noisy
detector; with `timestamp` stripped and the log excluded the detector isn't noisy,
each patience pass costs a real Pi run in minutes and dollars, and the invocation
budget already bounds cost. One quiescent pass is enough.

**Verdict matrix.** Repair and nudge are one bounded extra pass each.

| state | action |
| --- | --- |
| changed, gates clean | continue |
| changed, gates failing | continue, gate findings appended to the prompt |
| quiescent, gates failing | one repair pass with findings; still failing → **STUCK**, exit 1 |
| quiescent, clean, coverage < `MIN_COVERAGE` | one nudge pass; still under → **UNDERCOVERED**, exit 1 |
| quiescent, clean, covered | **done**, exit 0 |
| manifest seen before (non-adjacent) | **CYCLE**, exit 1 |
| invocation budget spent, still changing | **INCOMPLETE**, exit 1 (fixes the latent bug) |

Process exit codes stay `0` / `1` / `130` — `make wiki` is not in CI and nobody
scripts it, so the verdict belongs in the summary text, not in a bespoke code space.
Per-document verdicts aggregate into one non-zero exit if any document is not `done`.

**Redefine the budget.** `MAX_PASSES` becomes a bound on Pi *invocations* — a cost
knob that counts failures too — with `MAX_RETRIES` as consecutive-failure patience.
Validate both as positive integers **before** creating the sandbox.

### Module shape

Follow the house style in `web2md/src/web2md.py`: module docstring,
`from __future__ import annotations`, full type hints, Google docstrings,
`@dataclass(frozen=True)`, `argparse` in `main(argv: list[str] | None = None)`,
`print(..., file=sys.stderr)` (no `logging` anywhere in this repo), errors as
`raise SystemExit("message")`, and configuration as module-level UPPER_CASE
constants that tests monkeypatch (`KIT_NAME`, `MAX_PASSES`, `MAX_RETRIES`,
`PASS_TIMEOUT_S`, `MIN_COVERAGE`, `PROMPT_TEMPLATE`, `LOG_FILE`).

**Stdlib only.** That keeps CI unchanged — the `test` job's
`--only-group test --only-group web2md` already provides pytest, and `ci.yml` already
triggers on `scripts/**`, `Makefile` and `pyproject.toml`.

Pure functions — `manifest_for()`, `run_gates()`, `coverage()`, `decide()` — around
one impure seam, `run_sbx()`. Tests monkeypatch the seam; that is the whole test
strategy.

**Subtleties that must survive the port**, each with its comment carried over verbatim:

- `</dev/null` becomes `stdin=subprocess.DEVNULL`. Python's default (inherit)
  reproduces the hang exactly, so the hazard survives — but becomes *assertable*.
- `cwd=subprocess` on every call, from
  `REPO_ROOT = Path(__file__).resolve().parents[1]` (the pattern already used and
  already guarded by an off-by-one test at `web2md/tests/test_cli.py:19`). Pass the
  document to the prompt as a **repo-relative POSIX string**; `SystemExit` if the
  path lies outside the repo. This also fixes a latent flaw — an absolute host path
  today reaches the guest unusable.
- `sorted(folder.glob("*.md"))`. Bash globs are sorted; `Path.glob` is not, and
  without `sorted` document order is irreproducible and the tests flake.
- SIGINT: today's bash has no trap, so Ctrl-C leaves `pi-kit` running detached. In
  Python, SIGINT reaches Pi (same process group) and raises `KeyboardInterrupt` in
  the parent — catch it, print that work is preserved in `okf/` and that `pi-kit` is
  still running (`scripts/bash.sh`, or `sbx rm --force pi-kit`), exit 130. Do **not**
  pass `start_new_session=True`: that would shield Pi from Ctrl-C.
- Add `PASS_TIMEOUT_S` and treat `TimeoutExpired` as a retryable failure. Bash has no
  timeout, and this is the safety net for exactly the `</dev/null` hang class.
- Keep stdout/stderr inherited so Pi streams to the operator as today. Consequence
  worth writing down: the driver cannot read Pi's final message, so any future
  agent-side claim (Option C) has to be a file.
- A failed pass must not abort the loop and must not update the convergence baseline.

### Files

| File | Change |
| --- | --- |
| `scripts/compile_wiki.py` | **New.** The driver, per above. |
| `scripts/compile-wiki.sh` | **Delete.** |
| `scripts/tests/conftest.py` | **New.** Autouse `no_sleep` fixture — copy `web2md/tests/conftest.py:18-21` — plus a `wiki` builder over `tmp_path`. |
| `scripts/tests/test_{manifest,gates,decide,loop,limits}.py` | **New.** See Verification. |
| `pyproject.toml` | `pythonpath += "scripts"`, `testpaths += "scripts/tests"`, per-file-ignores `"scripts/tests/*" = ["D100","D103"]`. |
| `Makefile` | Add `PYTHON ?= uv run --no-project python` (same overridable-launcher pattern as `RUFF`/`PYTEST`; verified it resolves 3.12.12 via `.python-version` and installs no project deps). `wiki:` calls `$(PYTHON) scripts/compile_wiki.py`. Update the `test:` comment — it is no longer web2md-only. |
| `AGENTS.md` | New invocation at line 61: `uv run --no-project python scripts/compile_wiki.py md/other-books`. Amend the lint-okf stance at lines 64-66 (below). Document multi-pass semantics, the env knobs and the exit codes. Note the driver is now first-party Python alongside `web2md/`. |
| `README.md` | Line 15's "one Pi run each" → multi-pass with resume. Document the knobs, that partial output is retained, and that a non-zero result may be resumable. |
| `pi/.../skills/compile-wiki/SKILL.md` | State that the driver runs the same gates independently and will fail the compile. Fix `recommended-log` "warning" → "error" at line 420 to match `okf/.okflintrc.json`. |

No CI change.

### Gates in the driver vs. the AGENTS.md stance

`AGENTS.md:64-66` says the driver deliberately does not call `lint-okf`. Driver-owned
gates do not contradict that, but the file must say why or the next reader sees a rule
and a violation. The distinction is **dependency and authority**, not permission to
inspect output:

- `okf-lint` is a third-party Node CLI, pinned inside the VM and reachable on the host
  only via `pnpm dlx` — network plus pnpm. Putting it on the driver's critical path
  would add a host Node dependency to `make wiki`. That reason still holds. The gates
  are stdlib walks and one regex: no dependencies, deterministic, sub-millisecond.
- The linter checks *conformance to OKF*, which `SPEC.md` owns and the agent must
  satisfy. The gates check *whether the wiki is a usable progress record*, which is
  the **driver's own** concern, because the driver is the thing deciding whether to
  spend another Pi run. An empty directory is not an OKF violation — the spec
  tolerates a missing `index.md` — it is corrupted input to the termination logic.
  A program validating its own input is not scope creep.

Keep the agent's in-sandbox gates too; they exist so problems are fixed before a pass
ends, and the driver's copy is independent verification. Accept the ~20-line
duplication across the host/VM boundary; do **not** ship the Python gates into the kit
to dedupe, which trades a small duplication for cross-boundary coupling.

## Verification

`make lint` (ruff picks up `scripts/*.py` with no config change; shellcheck still has
`bash.sh` and `validate-spec.sh`), `make test`, and `./scripts/validate-spec.sh`.

Pure tests, no subprocess:

- **Normalisation.** `timestamp:` stripped only inside frontmatter; a `timestamp:` in
  a body code fence preserved; a file with no frontmatter (`index.md`) hashed whole;
  `okf/log.md` excluded; non-`.md` (`.okflintrc.json`) ignored; missing `okf/` →
  empty manifest, no crash.
- **Change detection, written as regressions against byte-count.** Split one page in
  two with identical total bytes → detected. Same-length word swap → detected. Rename
  with identical content → detected. Delete → detected. Identical content, different
  timestamps → **no** change. Log-only append → **no** change (the never-converges
  bug).
- **Cycles.** A→B→A flagged with the right pass number; A→B→C→A flagged; A→A
  classified quiescent, not a cycle.
- **Gates.** Empty dir; dir holding only `index.md`; `foo.md` beside `foo/`; index
  with no `* [` lines; dir with pages and no `index.md`; `](#foo.md)` flagged;
  `](#voice-and-tone)` **not** flagged; `](/foo.md)` not flagged. Plus one test
  asserting all five pass on a fixture mirroring the real wiki's shape.
- **Coverage.** Ratio excludes `index.md`/`log.md` from the numerator; a fixture at
  the real 0.932 passes; an empty wiki scores 0 and fails.
- **Limits.** `MAX_PASSES` in `{0, -1, "", "abc"}` → `SystemExit` **before** any sbx
  call (assert the recorder is empty).

Loop tests via a scripted `run_sbx` queue that mutates a `tmp_path` wiki between
calls — the `web2md/tests/test_fetch.py:20-30` queue idiom crossed with the
`test_cli.py:31-35` recorder — so the real manifest and gate logic run end to end:

- One transient failure then success → retried, backoff slept, document completes,
  exit 0.
- `MAX_RETRIES` consecutive failures → abandoned, message mentions preserved work,
  **the next document is still attempted**, final exit 1.
- `MAX_PASSES=1` while still changing → warning **and exit 1** (the latent bug).
- `TimeoutExpired` treated as retryable.
- Quiescent + clean + covered → exit 0 **and exactly N invocations**. Asserting the
  count is what proves the budget is no longer burned.
- Quiescent + gate failure → exactly one repair pass whose recorded prompt **contains
  the gate finding text**, then exit 1 if still failing.
- Quiescent + undercovered → one nudge pass, then exit 1.
- Every recorded call asserts `stdin is subprocess.DEVNULL` and `cwd == REPO_ROOT`.
- Lifecycle: `sbx rm --force` failure tolerated; `sbx run --detached` failure aborts
  before any pass.
- `KeyboardInterrupt` mid-pass → exit 130, message names the sandbox, nothing deleted.
- Missing `md/` folder → `SystemExit` before sandbox creation; empty folder → zero
  passes, exit 0; documents processed in sorted order.

**One gate CI cannot provide:** a single manual `make wiki` smoke run, because no job
here ever touches a real sbx VM. Say that in the PR description instead of what PR #8
said.

## Limitations to document, not solve

- **Coverage attribution.** The ratio is global over `okf/` and `md/`. Exact today
  (one source document); with several sources it becomes a sum and cannot tell which
  source is under-covered. The clean fix is a `source:` frontmatter key —
  `SPEC.md:168` permits additional keys and §9 forbids consumers rejecting unknown
  ones — but it needs a SKILL.md change and a kit rebuild, so it is a follow-up.
- A page that two sources both update gets first-writer-wins under any attribution
  scheme; that is a separate design.
- Stale bare-fragment link detection needs a heading index across the whole bundle.
  Out of scope; gate 4 as written is still worth having.
