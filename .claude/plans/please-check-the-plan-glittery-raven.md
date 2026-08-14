# Add `tests/test-toolchain.sh`

## Context

`pi/spec.yaml` installs the agent's toolchain in four `setup.install` steps
(apt packages at `77-87`, npm globals through a retry wrapper at `91-118`, the
Markdown/spelling linters at `120`, two `uv tool install` lines at `124-129`),
and `agentInstructions` (`27-33`) promises Pi that all of them are on `PATH`.
Nothing verifies that promise. The npm step exists precisely because installs
through the sandbox proxy are flaky, so a sandbox can come up with a tool
silently missing or half-installed; today that surfaces only as a confusing
failure mid-compile, or as Pi quietly working around a tool it was told it had.

The same is true of the agent's config: `pi/files/home/.pi/agent/` is **copied**
at kit build time, not mounted, so a path that stops matching the kit layout
leaves Pi running with no skill and no instructions — and nothing says so.

The last two commits (`Add toolchain to sandbox`, `Refactor the toolchain
installation`) reworked the install block, and `tests/` was created empty in
anticipation of this test. The goal: one host-side script that tears down any
existing `md2okf` sandbox, builds a fresh one from the current kit, checks
everything the kit promises inside it, and reports all failures at once.

Two things are deliberately **not** asserted:

- **Versions.** The pins in `pi/spec.yaml` are free to move without touching
  this test.
- **Base-image tools** (`uv`, `npm`, `node`, `git`, `docker`). They come from
  `docker/sandbox-templates:shell-docker`, not from our spec; this test covers
  what the kit itself is responsible for.

The sandbox is always rebuilt. Reuse would test whatever VM was already running,
which can predate a toolchain edit; a fresh build is the only way the test means
"the current kit delivers what it promises."

## What to build

### 1. `tests/test-toolchain.sh` (new, executable)

A host script in the style of `scripts/bash.sh` — `#!/usr/bin/env bash`,
`set -euo pipefail` on line 2, tab indentation, a usage/rationale header comment.

**Host side:**

1. Resolve `repo_root` from `${BASH_SOURCE[0]}` and `cd` there — the same two
   lines as `scripts/bash.sh:14-15` — so the script works from any CWD.
2. Guard on `command -v sbx`, printing the same `brew install docker/tap/sbx`
   hint the other three scripts print.
3. Always destroy and recreate, copying the idiom from
   `scripts/compile-wiki.sh:35-36` — not the reuse path in `scripts/bash.sh`.
   Keep `kit_name="md2okf"` with the same "keyed to `name:` in pi/spec.yaml"
   comment:

   ```bash
   sbx rm --force "${kit_name}" || true
   sbx run --detached --name "${kit_name}" --kit ./pi/ "${kit_name}"
   ```

   `sbx rm --force` is a no-op when nothing exists (`|| true`). `sbx run` is what
   executes `setup.install`; `sbx exec` then waits until that has finished, the
   same assumption `compile-wiki.sh` already makes.

   The header comment must state both costs plainly: a run takes **minutes**
   (apt + npm retries + uv), and it **destroys any existing `md2okf` sandbox**,
   including state a compile session left behind that `scripts/bash.sh` would
   otherwise have preserved.
4. Run every check in **one** `sbx exec`, not one per tool:

   ```bash
   sbx exec "${kit_name}" -- sh -lc "${checks}" </dev/null
   ```

   - `sh -lc` (login shell) is required: the uv tools land in `~/.local/bin` and
     the npm globals in the user prefix, neither of which is on a non-login
     `PATH`. `README.md:159` already uses this form.
   - `</dev/null` for the reason documented in `scripts/compile-wiki.sh:42-46` —
     `sbx exec` hands the guest a pipe for stdin that never reaches EOF. It also
     contains any tool that decides to prompt.
   - Add a comment recording the load-bearing assumption: the npm and uv steps
     run as `user: "1000"`, so this only works because `sbx exec` lands as the
     agent user and not as root. If the checks come back all-`MISSING`, suspect
     that before suspecting the install steps.

**Guest side** — build `checks` with a quoted heredoc
(`checks="$(cat <<'EOS' … EOS)"`) so nothing expands on the host. Do **not**
`set -e` inside it: every check runs, all failures are reported in one pass, then
a summary line and `exit 1` if `failures` is non-zero.

Three helpers, each incrementing a `failures` counter:

- `check <tool>` — `command -v` first (`MISSING <tool>`), then a smoke run.
  The smoke run is uniform, with no per-tool arguments and no per-tool special
  cases: `timeout 20 "$1" --version`, and if that exits non-zero,
  `timeout 20 "$1" --help`. Either succeeding prints `ok <tool>`; both failing
  prints `BROKEN <tool>`. `timeout` guards a tool that waits rather than prints.
  Output is discarded and never compared, so no version is asserted.

  The `--version`-then-`--help` fallback is what makes the CLIs with unknown
  flag support (`pi`, `okf-lint`, `markdownlint-cli2`, `cspell`) safe to check
  without inventing fixture files or hard-coding which flag each one accepts.
- `check_file <path>` — `[ -f ]`, printing `ok`/`MISSING <path>`.
- `check_exec <path>` — `[ -x ]`, printing `ok`/`MISSING <path>`. The kit copies
  files in, so a lost exec bit is a real failure mode.

What gets checked, grouped with comments that name the `pi/spec.yaml` lines they
mirror, so a spec edit has an obvious counterpart here:

| Group | Source | Checks |
| --- | --- | --- |
| apt | `pi/spec.yaml:77-87` | `curl`, `jq`, `python3`, `rg`, `shellcheck`, `tree` |
| npm (retry wrapper) | `pi/spec.yaml:91-118` | `pi`, `okf-lint` |
| npm (linters) | `pi/spec.yaml:120` | `markdownlint-cli2`, `cspell` |
| uv | `pi/spec.yaml:124-129` | `ruff`, `yamllint` |
| config delivery | `pi/files/home/.pi/agent/` | `~/.pi/agent/AGENTS.md`, `settings.json`, `models.json`, `skills/compile-wiki/SKILL.md`; `check_exec` on `skills/compile-wiki/scripts/lint-okf.sh` |
| credentials | `pi/spec.yaml:62-70` | `OPENROUTER_API_KEY` is the proxy-managed sentinel |

Two notes on the tool list:

- It must match **both** spec lists — the install steps *and* the
  `agentInstructions` prose at `pi/spec.yaml:27-33`. That prose is the actual
  promise being tested; a tool installed but not promised (or promised but not
  installed) is itself the bug. Say so in the script's grouping comment.
- `rg` is the command; the apt package is `ripgrep`. Check the command.

The credential check must **never print the value**. Case-match instead and
print only a verdict: empty → `MISSING OPENROUTER_API_KEY`; a value not matching
the proxy-managed sentinel → `BROKEN OPENROUTER_API_KEY (literal value in the
VM, expected the proxy-managed sentinel)`; otherwise `ok`. This automates the
manual check at `README.md:156-160`. The exact sentinel string is the one thing
to confirm empirically on the first green run — match on it loosely (`*proxy*`)
until then, and pin the comparison once observed.

### 2. `Makefile`

Add a host-only `test-toolchain` target after `test`, and its name to `.PHONY`
(line 26). Comment it above the target in the same style as `lint-okf` / `wiki`:
it needs an sbx runtime and an `sbx login` session, which is why it sits outside
`make test` and outside CI; and like `wiki` it always destroys and rebuilds the
`md2okf` sandbox, so it tests the current kit.

```make
test-toolchain:
	./tests/test-toolchain.sh
```

### 3. Docs

- `README.md` Development section: add the line to the command block, plus a
  sentence noting it needs `sbx login`, takes minutes, and **destroys any
  existing `md2okf` sandbox** — the opposite of `./scripts/bash.sh` two
  paragraphs below, which preserves it. Since the script now automates
  `README.md:156-160`, reframe that snippet as the manual equivalent rather than
  leaving two unlinked instructions.
- `AGENTS.md` Commands section: add the line to the first code block, and extend
  the sentence at `AGENTS.md:65-70` that already names `make lint-okf` as
  host-only so `make test-toolchain` is named there too.
- `AGENTS.md` Repository map: one clause recording that `tests/` holds host-side
  shell tests for the sandbox, distinct from the pytest suite in `web2md/tests/`
  (`pyproject.toml` sets `testpaths = ["web2md/tests"]`, so pytest never
  collects `tests/`).

## Verification

```bash
make lint            # shellcheck picks up tests/*.sh via `git ls-files`
make test-toolchain  # the real check; needs `sbx login`
```

`make lint` only covers the new script once it is `git add`ed — the lint targets
are driven off `git ls-files`. Confirm it is executable (`chmod +x`, matching
`scripts/*.sh`).

For `make test-toolchain`, one run is the test: every invocation is a cold
build, so the green path *is* the cold-start path. Expect every line to read
`ok` and the exit code to be 0. Two things to settle on that first run:

1. If a smoke command fails only because a CLI rejects both `--version` and
   `--help`, fix the helper's fallback — not the tool list.
2. Pin the `OPENROUTER_API_KEY` sentinel comparison to whatever the VM actually
   reports.

Exercise the failure path once during development with a fake name
(`check definitely-not-a-tool`) and confirm it prints `MISSING`, the remaining
checks still run, and the script exits 1. That is enough; do not mutate a real
tool inside the sandbox to prove it, since every run reinstalls anyway.

`make validate` is not required — nothing lands under `pi/` or `scripts/`.

## Changes from the superseded plan

- Location and name: `tests/test-toolchain.sh`, kebab-case like every other
  shell script here, not the pytest-style `test_toolchain.sh`.
- Dropped the `markdownlint-cli2` / `cspell` throwaway-fixture fallback and the
  per-tool flag caveats; one uniform `--version` → `--help` fallback replaces
  them.
- Dropped the "mutate `tree` with `sudo mv` and restore it" verification step
  and the "rebuild is not a no-op" step — the latter re-tests two lines that
  `make wiki` exercises on every run.
- Added config-delivery and proxy-managed-key checks, which cost nothing once
  the sandbox is built and cover the kit's other silent failure mode.
- Added the `sbx exec`-runs-as-user-1000 assumption and a louder warning that
  the target destroys an existing sandbox.
