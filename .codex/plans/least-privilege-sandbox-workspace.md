# Least-Privilege Sandbox Workspace Plan

## Summary and reasoning

Replace the repository-wide read/write mount with an explicit `sbx run`
workspace contract while preserving the existing full `kind: sandbox` kit.

The sandbox will receive only:

| Host path | Access | Purpose |
| --- | --- | --- |
| `okf/` | read/write, primary workspace | Generated wiki |
| `logs/sessions/` | read/write | Persistent Pi transcripts |
| Selected source directory under `md/` | read-only | Current compilation input |
| `SPEC.md` | read-only | Authoritative OKF specification |
| Four helper projects under `scripts/` | read-only | `inspectmd`, `inspectokf`, `sizeokf`, and `merkleokf` |

Docker Sandboxes mounts each workspace at the same absolute path inside the VM.
The implementation can therefore pass explicit absolute paths without copying
files, duplicating source, or creating a staging directory. Unrelated repository
files—including `.git`, CI configuration, host drivers, tests, and
documentation—will not be visible.

Keep `sbx run` rather than adopting `sbxenv.yaml`: the current kit is a full
sandbox kit, whereas an environment file's `kits:` entries must be mixins.
Converting the kit would broaden this security change into a runtime architecture
migration.

## Runtime interface

Introduce these non-secret environment variables in every sandbox:

```text
MD2OKF_SOURCE_DIR=<absolute mounted source directory>
MD2OKF_OKF_DIR=<absolute mounted okf directory>
MD2OKF_SPEC_FILE=<absolute mounted SPEC.md path>
MD2OKF_TOOLS_DIR=<absolute scripts directory containing mounted tool projects>
MD2OKF_SESSION_DIR=<absolute mounted transcript directory>
```

Keep existing user-facing commands unchanged:

```text
make wiki
./scripts/compile-okf.sh [md-folder]
./scripts/bash.sh
./scripts/pi.sh
make test-sandbox
```

Restrict the optional source argument to `md/` or one of its descendants after
resolving symlinks. Reject paths that escape that tree, preventing a caller from
accidentally restoring repository-wide visibility.

Use `okf/` as the primary workspace, so `sbx exec` and interactive shells start
there. Pass the source, specification, and each helper project as `:ro`
additional workspaces; pass `logs/sessions/` as the one additional writable
workspace.

## Staged implementation

### Stage 1 — Centralize sandbox creation

Add one host-side Bash library used by the compiler, interactive launchers, and
sandbox test driver.

It will:

- Resolve the repository root and all mount paths to canonical absolute paths.
- Validate that `SPEC.md`, `okf/`, and the four helper projects exist.
- Validate that the selected source directory is `md/` or a descendant.
- Create `logs/sessions/` before sandbox creation.
- Build the `sbx run` invocation with Bash arrays so spaces in paths remain
  safe.
- Pass the full environment-variable contract and ordered workspace list.
- Support both "create if absent" and "remove then create" behavior without
  duplicating mount definitions.

Update `compile-okf.sh` to recreate the sandbox through this library, as it does
today. Update `bash.sh`, `pi.sh`, and `test-sandbox.sh` to create it through the
same library when it is absent.

### Stage 2 — Remove repository-root assumptions inside the VM

Update the kit's Pi instructions and skills to use the environment contract:

- Read the specification from `$MD2OKF_SPEC_FILE`.
- Treat `$MD2OKF_SOURCE_DIR` as read-only input.
- Treat `$MD2OKF_OKF_DIR` as the only wiki output.
- Pass explicit wiki paths to `inspectokf`, `sizeokf`, and `merkleokf`.
- Describe the interactive working directory as the `okf/` mount rather than
  the repository root.
- Retain the rule that source material and the specification cannot authorize
  writes.

Update the kit-generated CLI shims to load projects from:

```text
$MD2OKF_TOOLS_DIR/inspectmd
$MD2OKF_TOOLS_DIR/inspectokf
$MD2OKF_TOOLS_DIR/sizeokf
$MD2OKF_TOOLS_DIR/merkleokf
```

Make each shim fail clearly when `MD2OKF_TOOLS_DIR` is unset. Update the bundled
OKF lint wrapper to default to `$MD2OKF_OKF_DIR` and fail clearly when the
variable or directory is missing.

Change the compiler prompt and Ralph-loop hash command to use canonical absolute
document and wiki paths. Keep transcript persistence, but direct Pi to
`$MD2OKF_SESSION_DIR`.

### Stage 3 — Adapt sandbox tests

Stop relying on `tests/` being mounted. Pipe `test-sandbox-guest.sh` into a login
shell over `sbx exec`, allowing the test body to execute inside the VM without
exposing the host test directory.

Extend the guest checks to verify:

- Every runtime variable is present and absolute.
- The source directory, specification, and helper projects are readable but not
  writable.
- The wiki and transcript directories are writable.
- The four workspace-backed CLIs execute successfully.
- `SPEC.md` is readable at the declared path.
- Representative unrelated paths such as `README.md`, `Makefile`, `.git/`,
  `kits/`, and `tests/` are absent inside the repository parent.
- The compile lint wrapper can locate and lint `$MD2OKF_OKF_DIR`.
- The existing toolchain, Pi configuration, Context7 extension, and
  proxy-managed credential checks still pass.

Do not write probes into read-only mounts. Use permission tests there and, if an
actual write probe is needed for output mounts, create a uniquely named
temporary file and remove only that exact file.

### Stage 4 — Documentation

Update the README, contributor guide, repository agent instructions, kit guide,
and changelog to document:

- The least-privilege mount table.
- The new `okf/` interactive working directory.
- Persistent transcripts as a separate writable output.
- The source-directory restriction.
- How to inspect the effective mount list with `sbx inspect md2okf`.
- That changes to mounts require sandbox recreation.

Set the documented minimum to `sbx 0.43.0`, matching the workspace and
single-file read-only behavior used by this implementation.

### Stage 5 — Validation and acceptance

Run static and host-side checks:

```bash
make lint
make validate
make test-web2md
make test-clis
```

Then test a fresh sandbox:

```bash
sbx rm --force md2okf
make test-sandbox
sbx inspect md2okf
```

Inspect output must show exactly the declared workspace set and access modes,
with no repository-root mount.

Finally, run one representative compilation through `scripts/compile-okf.sh`
and confirm:

- Pi reads the selected source and `SPEC.md`.
- All four helper CLIs work.
- Only `okf/` and `logs/sessions/` change on the host.
- The Ralph loop reaches a stable hash.
- The OKF lint summary is clean.
- No unrelated repository path is accessible from an interactive sandbox
  shell.

Because the kit and host scripts change, repeat `make validate` after the final
edits and use a freshly recreated sandbox for the conclusive runtime test.

## Assumptions

- All sandboxes created with the old repository-wide mount will be discarded
  and rebuilt; no backward-compatibility detection or migration path is needed.
- The full sandbox kit remains a `kind: sandbox`; no `sbxenv.yaml` or mixin
  conversion is included.
- Session transcripts remain a supported output and therefore receive their own
  writable mount.
- Custom source folders remain supported only within the repository's `md/`
  tree.
- `okf/` remains the primary workspace and the only writable content output.
- Host CLI projects remain the single source of truth and are mounted read-only
  rather than copied into the kit.
- Git commits and pushes remain the user's responsibility.
