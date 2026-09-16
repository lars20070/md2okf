# Least-Privilege Sandbox Mount

## Context

Today every launcher (`scripts/compile-okf.sh`, `scripts/bash.sh`, `scripts/pi.sh`,
`tests/test-sandbox.sh`) calls `sbx run --detached --name md2okf ./kits/md2okf/`
with no workspace `PATH` arguments, so `sbx` defaults to mounting the whole repo
root read-write. Pi's restriction to `okf/` is enforced only by
`AGENTS.md`/skill instructions, not by the filesystem — the sandbox can read
`.git`, CI config, `.claude/`, and every other repo file, and could write
anywhere in the repo.

The user wants an actual least-privilege mount: `okf/` read-write (the wiki
Pi produces), and `md/`, `scripts/`, `SPEC.md` read-only (source input,
host CLI projects, and the spec Pi must read). Everything else in the repo
becomes invisible to the sandbox. Session transcripts (`logs/sessions/`,
used by `compile-okf.sh`'s `pi --session-dir`) need to keep persisting across
`sbx rm`, so that gets a fifth, narrowly-scoped read-write mount.

Researched via Context7 (`/docker/docs`) and confirmed against the installed
`sbx` (0.43.0): `sbx run`/`sbx create` take `[SANDBOX_KIT] [PATH...]`
positionally — the first `PATH` is the read-write primary workspace (and the
sandbox's default working directory); further `PATH`s are additional
workspaces, `:ro`-suffixed for read-only, and a `:ro` argument may name a
single file. This is stable, non-experimental CLI surface. The kit spec
(`kind: sandbox`, schemaVersion "2") has no native `workspace`/`mount` key —
mounting is purely a CLI-invocation concern.

Three mounting mechanisms were compared:

1. **Inline `sbx run` PATH args in each launcher** — simplest diff, but the
   mount list is duplicated across 4 files with no single source of truth.
2. **Centralized host-side helper** — same stable CLI mechanism, factored
   into one shared function so the mount list is defined once. **Recommended.**
3. **Declarative `sbxenv.yaml`** — self-documenting and reviewable via
   `sbx env plan`, but the feature is explicitly experimental, `kits:`
   entries must be mixins (this kit is `kind: sandbox`, not a mixin — adopting
   this would mean a much bigger, riskier kit-kind migration), and
   `additionalWorkspaces.path` is documented only as "directory to mount"
   (unclear whether a bare `SPEC.md` file works the way it does for `sbx run`).

Option 2 is the recommended approach: it gets the single-source-of-truth
benefit without the experimental-feature risk or the kit-kind migration.

**Consequence that must be fixed alongside the mount change:** making `okf/`
the *primary* workspace also makes it the sandbox's default working
directory. Every in-VM reference that currently assumes cwd = repo root
(`AGENTS.md`, the `compile-okf` skill, `lint-okf.sh`'s default path, the four
CLI shims' `${WORKDIR}/scripts/...`, and `compile-okf.sh`'s own `merkleokf`
call and document-path prompt) would silently resolve to the wrong path
otherwise. This plan fixes all of them in the same pass.

Explicitly out of scope (narrower than the earlier, now-deleted
`.codex/plans/least-privilege-sandbox-workspace.md`): the whole `md/`
directory is mounted read-only (not restricted to one selected document), and
no `MD2OKF_*` environment-variable contract is introduced — plain "one level
up" relative paths are enough for this simpler mount set.

## Implementation

**1. New file `scripts/lib/sandbox-mounts.sh`**
A small function, e.g. `sandbox_workspace_args`, that `mkdir -p logs/sessions`
(so the mount source exists before `sbx run`/`sbx create`) and prints the
ordered workspace `PATH` list:
```
./okf ./md:ro ./scripts:ro ./SPEC.md:ro ./logs/sessions
```
All callers already `cd` to the repo root before invoking `sbx`, so relative
paths here are correct.

**2. `scripts/compile-okf.sh`**
- Source the new lib; append its workspace args to the existing
  `sbx run --detached --name "${kit_name}" ./kits/md2okf/` call.
- Fix `wiki_root_hash()`: `merkleokf --nolog -L 0 okf/` → `merkleokf --nolog -L 0 .`
  (cwd is now the wiki root itself, not its parent).
- Fix the document loop so the path embedded in `compile_prompt` still
  resolves correctly from Pi's new cwd (one level below the repo root):
  iterate absolute paths, e.g. `for document in "${repo_root}/${markdown_folder}"/*.md`,
  instead of the current relative glob.
- Drop the now-redundant later `mkdir -p "${session_dir}"` (the lib already
  creates `logs/sessions` before the sandbox is created).

**3. `scripts/bash.sh`, `scripts/pi.sh`**
- Source the lib; append its workspace args to each script's
  `sbx run --detached --name "${kit_name}" ./kits/md2okf/` call.

**4. `tests/test-sandbox.sh`**
- Source the lib; same change to its `sbx run` line.
- `tests/` is no longer mounted, so replace
  `sbx exec "${kit_name}" -- sh -lc './tests/test-sandbox-guest.sh'` with
  piping the script over stdin instead of referencing a mounted path:
  `sbx exec "${kit_name}" -- sh -l -s < "${repo_root}/tests/test-sandbox-guest.sh"`.
  Keep the login-shell (`-l`) semantics — `test-sandbox-guest.sh`'s own header
  comment notes it depends on login-shell PATH setup for `~/.local/bin` and
  the npm prefix.

**5. `kits/md2okf/spec.yaml`**
- The four CLI shims under `setup.files` (`inspectmd`, `inspectokf`,
  `sizeokf`, `merkleokf`): `${WORKDIR}` will now resolve to the mounted
  `okf/` path (the new primary workspace), so
  `"${WORKDIR}/scripts/inspectmd"` etc. must become
  `"$(dirname "${WORKDIR}")/scripts/inspectmd"` to keep reaching the sibling
  `scripts/` mount.
- `agentInstructions.content`, "Sandbox environment" section: replace "The
  user's project is mounted as your workspace" with an accurate description —
  the workspace *is* `okf/` (read-write); `../md/`, `../scripts/`, and
  `../SPEC.md` are read-only siblings; `../logs/sessions/` is writable for
  transcripts; no other repository file is visible.

**6. `kits/md2okf/files/home/.pi/agent/AGENTS.md`**
- "OKF ... knowledge base held under `okf/` in your workspace" → "... *is*
  your workspace" (cwd is the wiki root directly now).
- `SPEC.md` references (prose and `cat SPEC.md`) → `../SPEC.md` /
  `cat ../SPEC.md`; "root of your workspace" → "one level above your
  workspace".
- "Workspace boundaries" section: `md/` → `../md/`, `SPEC.md` → `../SPEC.md`.

**7. `kits/md2okf/files/home/.pi/agent/skills/compile-okf/SKILL.md`**
- Step 1: `cat SPEC.md` → `cat ../SPEC.md`; "at the workspace root" → "one
  level above your workspace".
- Step 2: "under `md/`" → "under `../md/`".

**8. `kits/md2okf/files/home/.pi/agent/skills/compile-okf/scripts/lint-okf.sh`**
- Default bundle: `./okf` → `.` (cwd is the wiki root itself now); update the
  usage comment (`bundle wiki root to lint (default: ./okf, relative to the
  workspace)`) to match.

**9. `README.md`**
- Update the sandbox/repo-layout description so it documents the new scoped
  mount (matching the rewritten `agentInstructions` in `spec.yaml`) instead of
  implying a whole-repo mount.

## Verification

- `./scripts/validate-spec.sh` (`make validate`) after touching
  `kits/md2okf/spec.yaml`.
- `sbx rm --force md2okf && make test-sandbox` — exercises the new mounts and
  the stdin-piped guest script; must pass.
- After a fresh `sbx run`, inspect the mount from an interactive session
  (`./scripts/bash.sh`) and confirm only `okf/`, `md/`, `scripts/`, `SPEC.md`,
  `logs/sessions/` are visible (with `okf/` and `logs/sessions/` writable, the
  rest read-only) and that `.git`, `README.md`, `Makefile`, `tests/`,
  `kits/`, `.github/`, `.claude/`, `CLAUDE.md` are absent.
- Run one real compile end-to-end (`./scripts/compile-okf.sh` /
  `make wiki`) against the existing `md/GoogleStyleGuide.md`: confirm Pi
  reads `../SPEC.md`, only `okf/` and `logs/sessions/` change on the host,
  the Ralph loop reaches a stable hash, and `make lint-okf` is clean
  afterward.
- `make lint` as a final static pass, since multiple shell scripts changed.
