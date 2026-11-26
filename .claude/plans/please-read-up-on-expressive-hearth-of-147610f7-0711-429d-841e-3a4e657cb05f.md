# Plan: fill the lat.md/ knowledge base for md2okf

## Context

The user is adding [lat.md](https://www.lat.md) (lat 0.13.11, already installed)
as a developer tool. They run `lat init` themselves first. In 0.13.11 that
command scaffolds only `lat.md/lat.md`: a single paragraph with no heading and
no index. It also writes agent integrations, chosen interactively. Depending on
those choices, it can create:

- a block in `AGENTS.md`;
- `.agents/skills/lat-md/SKILL.md` and `.codex/skills/lat-md/SKILL.md`;
- `.claude/` skills and hooks;
- an MCP entry;
- a `.pi` line in `.gitignore`.

This plan does four things:

- fills `lat.md/` with a validated knowledge graph of md2okf (design, rationale
  and invariants, with wiki links into the code and the behavioural tests);
- adds `# @lat:` back-references in `src/md2okf/`;
- wires `lat check` into `make lint` and CI;
- repairs what `lat init` breaks in the existing gates.

Both scope choices were confirmed by the user. The layout follows section 6 of
`review-plan.md`, and its other points were checked and folded in.

What goes where:

- `lat.md/` holds **design decisions and how the parts connect**.
- Option lists, credentials and release commands stay where they are already
  maintained: `docs/usage.md`, `docs/configuration.md` and CONTRIBUTING.md. The
  graph links to them and records only the decision behind each one.

## lat.md rules the layout must satisfy (verified)

- **Index files.** Every directory in `lat.md/`, the root included, needs an
  index file named after the directory: `lat.md/lat.md` and
  `lat.md/driver/driver.md`. The index lists every visible entry as
  `- [[name]] — one sentence`. Only `.md` files may sit there, plus `.gitignore`
  and `config.local.yaml`. Hidden entries (`.cache`, `.DS_Store`) are skipped.
- **Leading paragraphs.** Every section needs a leading paragraph of at most 250
  characters, not counting `[[...]]` text, placed before any child heading.
- **Section ids.** They take the form `file#Heading#Sub`, so file stems must be
  unique.
- **Code links.** Python symbol links work for functions, constants and nested
  methods, for example `[[src/md2okf/workbench.py#Workbench#mounts]]`. Shell and
  YAML files take path links only. Name the symbol and link it; don't copy its
  literal value. The review confirmed all of these against lat 0.13.11.
- **Content.** Keep it a current-state snapshot, not a journal. Use prose, and a
  Mermaid diagram only when more than 7 parts interact.
- **Repository lint.** Tracked `lat.md/**/*.md` goes through markdownlint and
  cspell. Every file therefore starts with an H1 and has one H1 only, and a new
  word goes into `.cspell.json`. Never put `[[x|alias]]` inside a table cell,
  because the pipe breaks the table.

## Folder and file structure (10 files)

```text
lat.md/
├── lat.md               # root index: purpose, end-to-end pipeline, authority order, repo map
├── driver/
│   ├── driver.md        # index: the host driver (src/md2okf) and how its modules split work
│   ├── cli.md
│   ├── compile-loop.md
│   ├── workbench.md
│   ├── sandbox.md
│   └── agents.md
├── kits.md
├── tools.md
└── development.md
```

There is no separate glossary. Each term gets a heading where its behaviour is
explained, so `lat locate "Ralph loop"` finds both the definition and its rule.
Two risks to check during implementation:

- A link to `[[kits]]` could clash with the `kits/` repo directory. If
  `lat check` reports it as ambiguous, use `[[lat.md/kits]]` in prose links.
- Run `lat check index` to confirm the root bullet stays `[[kits]]`.

## Content per file

Every heading listed below gets a leading paragraph. Link the behavioural tests
**beside** each lifecycle or compile guarantee, so a reviewer has something
concrete to check the prose against. All link targets below were verified to
exist.

### `lat.md` (root index)

- H1 "md2okf knowledge base", then a short paragraph on purpose and use
  (`lat search` / `lat locate` / `lat check`).
- *Pipeline*: `md/` → per-agent workbench → sbx sandbox → one agent turn per
  iteration → convergence → mirror into `-o`. Each stage links to its driver
  page.
- *Authority order*: [[SPEC.md]] (OKF v0.2, fixed and never edited) outranks the
  kit instructions, which outrank the skills.
- *Repository map*:
  - the seven independent uv projects and the zero-overlap rule;
  - `okf/` is generated and gitignored, while `md/` is tracked;
  - links to [[docs/architecture.md]], [[docs/usage.md]],
    [[docs/configuration.md]], [[AGENTS.md]] and [[CONTRIBUTING.md]].
- Bullets: `[[driver]]`, `[[kits]]`, `[[tools]]` and `[[development]]`.

### `driver/driver.md` (index)

One paragraph on how the modules split the work:

- `cli` orchestrates.
- `compile` loops.
- `workbench` stages.
- `sandbox` is the only sbx seam.
- `agents` holds everything agent-specific.

Then the five bullets.

### `driver/cli.md`

Covers [[src/md2okf/cli.py#main]].

- *Modes*: compile, dry run, shell and agent. Link [[docs/usage.md]] for the full
  option list instead of repeating it.
- *Option rules*: [[src/md2okf/cli.py#_reject_compile_only_options]] refuses
  rather than ignores, and compares values against the parser defaults.
- *Interactive sessions*: [[src/md2okf/cli.py#_enter_sandbox]] checks for a TTY
  before preflight and keeps the lock through `execvp`.
- *Dry run*: [[src/md2okf/cli.py#_print_dry_run]] needs no sbx, takes no lock and
  costs nothing.
- *Exit codes*:
  - 0: every document compiled.
  - 1: failed after work started.
  - 2: refused before any work.

  The `UnsafeLockFile` catch is deliberately narrow, and Ctrl-C exits 1.
- *Output streams*: TSV rows go to stdout and progress goes to stderr.
- The `MD2OKF_AGENT` environment variable versus the `--agent` flag.

### `driver/compile-loop.md`

- *Document resolution*: [[src/md2okf/compile.py#resolve_documents]] covers
  stdin, directories and basename clashes.
- *Ralph loop*: [[src/md2okf/compile.py#compile_document]], with
  [[src/md2okf/compile.py#CONTINUATION_PROMPT]] and
  [[src/md2okf/compile.py#DEFAULT_MAX_ITERATIONS]]. Tests:
  `test_loop_runs_until_hash_stabilises`,
  `test_continuation_prompt_appended_from_iteration_two` and
  `test_iteration_cap_is_a_failure_naming_the_document`, all in
  [[tests/test_compile.py]].
- *Convergence*: [[src/md2okf/compile.py#wiki_root_hash]] runs
  `merkleokf --nolog -L 0`.
  - A malformed hash never counts as converged.
  - A stable hash means the agent stopped changing the wiki, not that the wiki
    is correct.
- *Turn verdict*: a turn fails on a protocol failure, a nonzero exit, or zero
  tool calls. Tests:
  - `test_exit_zero_with_a_protocol_failure_fails_and_mirrors_nothing`
  - `test_zero_tool_calls_is_a_failure`
- *Mirroring cadence*: the wiki is mirrored out only after a completed
  iteration. Tests:
  - `test_mirrors_out_after_every_iteration`
  - `test_ctrl_c_mid_stream_does_not_mirror_a_partial_iteration`
- *Errors*: `UsageError` versus `CompileError`.

### `driver/workbench.md`

- *Why a fixed workbench*: sbx fixes mounts when the sandbox is created.
- *Layout and mounts*: [[src/md2okf/workbench.py#Workbench#mounts]].
  - Five mounts in a fixed order.
  - Read-only versus read-write.
  - No read-write mount contains a read-only one.
- *Run lock*: [[src/md2okf/workbench.py#lock]].
  - Per uid in `/tmp`, not under `XDG_STATE_HOME`.
  - Opened with `O_NOFOLLOW`, then checked with `fstat`.
  - Non-blocking.
  - `survive_exec` keeps it across `execvp`.

  Tests: the `test_lock_*` group in [[tests/test_workbench.py]].
- *Staging*: [[src/md2okf/workbench.py#restage]],
  [[src/md2okf/workbench.py#stage_clis]] (copies only `pyproject.toml` and
  `src/`) and [[src/md2okf/workbench.py#rewrite_spec]] (rewrites in place,
  because the mount binds the inode).
- *Output adoption*: [[src/md2okf/workbench.py#is_adoptable_output]].
  - Mirroring propagates deletions, so `-o` must be proven adoptable.
  - Adoptable means missing, empty, or a bundle root whose `index.md`
    frontmatter is exactly `okf_version`.

  Tests: the `test_output_*` group.

  This answers the question "may md2okf overwrite this folder?", and it lives
  here, separate from sandbox replacement.
- *Path safety*: `reject_if_unsafe` and `check_no_overlap`.
- *Mirror failure recovery*: `MirrorError` names where the good copy is.

### `driver/sandbox.md`

This page answers "will the next run destroy my sandbox?". It corrects the
earlier draft.

- *The sbx seam*: every subprocess goes through `sandbox.py`
  ([[src/md2okf/sandbox.py#_run]], `Exec`, `exec_interactive`).
  [[tests/conftest.py]] fakes exactly that seam.
- *Preflight*: [[src/md2okf/sandbox.py#preflight]] and the `SBX_VERSION` floor.
- *Fingerprint*: [[src/md2okf/workbench.py#fingerprint]] is the kit tree hash +
  the sbx version + the mount arguments. `_is_hash_noise` is why dotfiles
  count: an edited skill must trigger a rebuild.
- *Create or reuse*: [[src/md2okf/workbench.py#resolve_sandbox_state]]. Write
  the branches out explicitly:
  1. **No sandbox under the name**: create it.
  2. **Ownership not proven** (no marker, or the live owner token is missing or
     doesn't match): `UnownedSandboxError`. The sandbox is never deleted, and
     `--fresh` doesn't change that.
  3. **Ownership proven, plus `--fresh`, a changed fingerprint, or a failed
     probe**: replace it. [[src/md2okf/sandbox.py#create]] starts with
     `sbx rm --force`, so the old sandbox is **destroyed**.
  4. **Ownership proven and everything matches**: reuse it.

  Each branch is followed by its `test_resolve_sandbox_state_*` test, including
  `…_fresh_does_not_widen_deletion_authority`.
- *Ownership token*: `OWNER_TOKEN_PATH`. Its threat model:
  - It guards against accidental reuse only, not against an attacker.
  - It fails safe: the worst case is a false rejection, never a false
    acceptance.
  - The marker is cleared before a recreate, and written as soon as the create
    succeeds. Tests:
    - `test_ensure_sandbox_writes_marker_even_when_the_credential_check_fails`
    - `test_ensure_sandbox_clears_markers_when_a_recreation_fails`
- *Credential check*: [[src/md2okf/workbench.py#ensure_sandbox]] runs it on
  every create and every reuse (`test_credentials_are_checked_on_reuse_too`).
  `--shell` downgrades a failure to a warning. Link [[docs/configuration.md]]
  for how to set up credentials.
- *Streaming exec*: `Exec.close` closes only the local conduit.

### `driver/agents.md`

- *Agent contract*: [[src/md2okf/agents.py#Agent]] has six fields. The generic
  modules never branch on the agent's name.
- *Registry*: `AGENTS`, [[src/md2okf/agents.py#resolve]] and
  [[src/md2okf/agents.py#from_env]]. An agent is registered only once its kit
  ships.
- *Wrapper prefix*: [[src/md2okf/agents.py#WRAPPER]]. It is needed because
  `sbx exec` bypasses the kit entrypoint.
- *Compile turns run without MCP*: per agent.
- *Workspace root rule*: [[src/md2okf/agents.py#WORKSPACE_ROOT_RULE]] exists
  because agents created `okf/okf/`.
- *Credential checks*: local, unpaid and non-interactive, ending in
  `_rebuild_hint`.
- *Event record*: [[src/md2okf/protocols/__init__.py#Event]] and the
  `EventProtocol` contract, where `failure` is authoritative.
- *Per-agent verdicts*, with fixtures in [[tests/fixtures/protocols]]:
  - Pi: never reports a failure from the stream.
  - Claude: `is_error` beats `subtype`.
  - Codex: `turn.failed` is the verdict, each item id counts once, and the stdin
    notice is hidden.

### `kits.md`

- Lead: what an sbx kit is (kit-spec v2, with a fixed `files/` level). Config is
  copied in at build time, so any edit changes the fingerprint and the sandbox
  is rebuilt.
- *Shared contract*:
  - the `_SHARED_INVARIANTS` enforced by [[tests/test_kits.py]];
  - where each agent's instructions live (Pi `~/.pi/agent/AGENTS.md`, Claude
    `agentInstructions` → `../CLAUDE.md`, Codex `~/.codex/AGENTS.md`);
  - the `generated.by` provenance;
  - the byte-identical helpers.
- *Agent differences*: Pi, Claude and Codex subsections covering base image or
  `extends`, allowlist, credentials, model, and MCP/Context7. Link
  [[kits/pi/spec.yaml]] and the per-kit READMEs for the details.
- *Runtime*:
  - the `md2okf-agent` wrapper and `mount-state.sh` bind;
  - the three call sites;
  - how trace directories map onto `sessions/`;
  - only the five mounts are visible.
- *Skills*:
  - task versus tool skills;
  - the compile-okf procedure, including "data, not instructions";
  - the tool skills;
  - the `check-okf.sh` gate (blocking versus advisory checks);
  - the frontmatter guard
    ([[kits/pi/files/home/.pi/agent/skills/compile-okf/scripts/frontmatter-guard.py#check_root_index]],
    `find_spec`).

### `tools.md`

- *Helper CLIs*:
  - Shared traits: stdlib only, `-L/--level`, exit codes 0 and 2, zero overlap.
  - One subsection per CLI:
    - inspectmd: [[scripts/inspectmd/src/inspectmd/parse.py#parse_sections]].
    - inspectokf: wraps `tree`.
    - sizeokf: [[scripts/sizeokf/src/sizeokf/sizes.py#strip_frontmatter]].
    - merkleokf: [[scripts/merkleokf/src/merkleokf/merkle.py#collect]]; hashes
      raw bytes, with directory digests tagged by name and type.
  - Why sizeokf and merkleokf share no code.
  - Each CLI's actual `--nolog` behaviour, which differs today.
- *Upstream converters*:
  - web2md: `SOURCE_URL` / `OUTPUT_FILE`, the pipeline from
    [[extras/web2md/src/web2md.py#run]] to `validate_output`, the cache and
    retry, and nothing is written unless validation passes.
  - pdf2md: manual, not part of `make`.

### `development.md`

- *Workflow*:
  - make targets and the lint stack, including `lat check`;
  - why `UV_PROJECT_ENVIRONMENT` stays relative;
  - Git rules: `master`, and agents never commit or push.
- *Keeping the graph current*: this is a **review responsibility**. `lat check`
  proves that links resolve, not that the prose is still true. A change to
  behaviour updates its section in the same change, and reviewers check the
  prose against the linked tests.
- *Testing*:
  - the FakeSbx seam;
  - kit-contract tests;
  - sdist → wheel package tests;
  - live sandbox suites;
  - mount and wrapper shell tests;
  - the CLI and web2md suites.
- *Packaging*:
  - Wheel force-includes in [[pyproject.toml]].
  - *Lookup order* (nested here): [[src/md2okf/resources.py#_installed_root]]
    looks in the installed package, then falls back to the checkout. Covers
    `kit_dir`, `spec_md`, `clis_dir` and `sbx_version_file`.
- *Release*:
  - the single `VERSION` and `sync-versions.sh`, with literals kept because of
    `stage_clis`;
  - `SBX_VERSION` as the floor;
  - the CI jobs and the release workflow, with the commands linked to
    [[CONTRIBUTING.md]] rather than copied.

## Code back-references in `src/md2okf/` (user-approved scope)

Put one `# @lat:` comment directly above each target listed below. Nothing
outside `src/md2okf/` gets annotated. Kit files stay untouched: an edit there
changes the kit hash, and the shared helpers must stay byte-identical.

| Code | Section |
| --- | --- |
| `cli.py` `main` | `cli#Exit codes` |
| `cli.py` `_enter_sandbox` | `cli#Interactive sessions` |
| `cli.py` `_print_dry_run` | `cli#Dry run` |
| `compile.py` `resolve_documents` | `compile-loop#Document resolution` |
| `compile.py` `compile_document` | `compile-loop#Ralph loop` |
| `compile.py` `wiki_root_hash` | `compile-loop#Convergence` |
| `workbench.py` `lock` | `workbench#Run lock` |
| `workbench.py` `Workbench` | `workbench#Layout and mounts` |
| `workbench.py` `is_adoptable_output` | `workbench#Output adoption` |
| `workbench.py` `fingerprint` | `sandbox#Fingerprint` |
| `workbench.py` `resolve_sandbox_state` | `sandbox#Create or reuse` |
| `workbench.py` `ensure_sandbox` | `sandbox#Credential check` |
| `sandbox.py` `_run` | `sandbox#The sbx seam` |
| `sandbox.py` `create` | `sandbox#Ownership token` |
| `agents.py` `Agent` | `agents#Agent contract` |
| `protocols/__init__.py` `Event` | `agents#Event record` |
| `resources.py` `_installed_root` | `development#Packaging#Lookup order` |

Each section id must match its heading exactly. Lines stay under ruff's 120.

## Wiring and gate repairs

**`lat check` in lint and CI**

- **Makefile**: add `LAT ?= npx --yes lat.md@0.13.11` next to `CSPELL`, with a
  header comment like the other launchers. Then add `$(LAT) check` to `lint:`
  after cspell.
- **`ci.yml`**: rename the lint step to "...ruff, lat". ubuntu-latest already has
  npx.
- **`release.yml`**: `verify` runs `make lint`, so it inherits the check.

**`AGENTS.md` lint repair** (review point 1)

- Unchanged, the generated block adds eight H1s (MD025), and its opening marker
  touches a heading (MD022).
- Wrap the block in `<!-- markdownlint-disable MD022 MD025 -->` …
  `<!-- markdownlint-enable MD022 MD025 -->`, with blank lines between each
  directive and its lat marker, and put both directives **outside** the
  markers. A later `lat init` can then still refresh the block.
- Add any cspell words the template needs.

**Generated skills** (point 1)

- If `.agents/skills/lat-md/SKILL.md` or `.codex/skills/lat-md/SKILL.md` will be
  tracked, add `':!.agents/skills/lat-md/' ':!.codex/skills/lat-md/'` to both
  `*.md` pathspecs in `lint:`. The vendored template triggers MD032.
- Extend the sdist `exclude` in [[pyproject.toml]] with the anchored
  `"/.agents/skills/lat-md"` and `"/.codex/skills/lat-md"`. This follows the
  existing policy of not republishing vendored skills. Check with
  `tar tzf dist/*.tar.gz`, because `test_package.py` inspects only the wheel.

**`.gitignore` `.pi` rule** (point 3)

- If init appended a bare `.pi`, it ignores `kits/pi/files/home/.pi/` at any
  depth. Anchor it as `/.pi/`.
- Then check that `git check-ignore -v --no-index kits/pi/files/home/.pi/agent/skills/x/SKILL.md`
  prints nothing.

**Hook and MCP commands** (point 3)

- Review what init wrote to `.mcp.json`, `.claude/settings.json` and `.cursor/`.
  Do not stage a machine-local absolute path or `npx lat.md@latest`. Use
  `npx --yes lat.md@0.13.11` to match CI, or a bare `lat` with its prerequisite
  documented.
- A new `.mcp.json` server is only active if it is also added to
  `enabledMcpjsonServers` in `.claude/settings.json`.

**Docs**

- **AGENTS.md**: add a short `lat.md/` paragraph to the repo map, and mention
  lat in the `make lint` comment.
- **CONTRIBUTING.md**: in the Commands comment and the tools sentence, say lat
  runs via npx, so nothing needs installing.
- **CHANGELOG.md** `[Unreleased]`: add `### Added`.
- **`.cspell.json`**: the new words.

## Execution order

1. The user runs `lat init`. Inspect `git status` and `git diff`, and apply the
   gate repairs above (`.gitignore`, hooks/MCP, the AGENTS.md wrapper, skill
   exclusions).
2. Make sure nothing under `lat.md/.cache` shows up in `git status`. If it does,
   add `.cache/` to `lat.md/.gitignore`.
3. Write the root and `driver/` index files, then the driver pages, then kits,
   tools and development. Run `lat check` after each.
4. Add the 17 `# @lat:` comments.
5. Do the Makefile, CI, docs, CHANGELOG and cspell wiring.
6. `git add` the intended files **before** the final `make lint`. Its markdown
   and cspell passes use `git ls-files`, so untracked files would otherwise pass
   without being checked.
7. Hand the user a drafted commit message. Never commit or push.

## Verification

- `lat check` passes all six checks: md, links, code-refs, index, sections and
  diagrams.
- **Backlinks are checked in the direction they point.** `lat check` stays green
  even when an annotation is missing, so verify each table row with
  `lat refs '<section>' --scope=code`. It must list the intended file and the
  line above the intended symbol, for example `lat refs 'workbench#Run lock'
  --scope=code` → `src/md2okf/workbench.py` at `lock`.
- Forward links: `lat refs 'src/md2okf/workbench.py#lock'` lists `workbench#Run
  lock`. `lat locate "Ralph loop"` finds `compile-loop#Ralph loop`.
- `make lint` passes with everything staged: markdownlint, cspell, ruff and
  `lat check` via npx, including the generated AGENTS.md block.
- `make test-md2okf` and `make dist` pass. `tar tzf` on the sdist shows no
  generated lat skills. `make validate` passes as a sanity check (no kit file
  touched).

## Pre-existing inconsistencies (report only, don't fix here)

- The `--nolog` semantics differ between sizeokf and merkleokf, while
  CONTRIBUTING.md:179 describes them as the same.
- `extras/web2md/README.md:46-48` has stale "only first-party Python" and "only
  `[tool.ruff]`" claims.
- The `src/md2okf/__init__.py` docstring mentions only Pi.
- Driver docstrings cite `.claude/plans/interface-plan.md` and
  `generalise-agent-framework.md`, which don't exist. lat.md must not link to
  them.
