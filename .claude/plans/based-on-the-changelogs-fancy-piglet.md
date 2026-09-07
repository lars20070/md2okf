# Migrate md2okf from sbx v0.38.0 to v0.42.0

## Context

md2okf's documented minimum is sbx 0.38.0 (the first release that understands
the kit-spec v2 grammar `pi/spec.yaml` uses). The user has since upgraded a
different, unrelated project (`lars20070/sbxagent`) to sbx v0.42.0 and merged
[PR #5](https://github.com/lars20070/sbxagent/pull/5) there. Reading that PR's
diff of `kits/sbxpi/spec.yaml` — the closest structural analog to
`pi/spec.yaml` in this repo (bare `docker/sandbox-templates:shell-docker`
image, no `extends:`, plain `entrypoint: [pi]`) — plus the v0.39.0 and v0.42.0
sbx-releases changelogs, gives a concrete list of what does and doesn't apply
here.

**What does not apply**, and why (confirmed by grepping the whole repo, not
just `.sh`/`Makefile`/`.md`/`.yaml`):
- Pinning/bumping an in-sandbox `sbx` binary version+SHA — that only exists in
  `sbxagent`'s meta-kits (which run `sbx` inside themselves). `pi/spec.yaml`
  never installs `sbx`.
- The `extends:`/`setup:`-merge fix for docker/sbx-releases#415 — only affects
  kits using `extends:`; `pi/spec.yaml` has none.
- `python3-yaml` — nothing under `pi/` does `import yaml`.
- `tree` — already installed in `pi/spec.yaml`'s `setup.install`.
- The v0.42.0 `ports --publish` default change (`tcp` → `tcp4`) —
  `pi/spec.yaml` declares no `ports:` and no script calls `sbx ports`.
- `SANDBOX_VM_ID` deprecation — never referenced in this repo.
- `scripts/validate-spec.sh` and `.github/workflows/ci.yml` are already
  version-agnostic by design (they use whatever `sbx` is installed/`latest`),
  so neither needs a code change.

**What does apply**: v0.42.0 deprecates the `sbx run <name> --kit <ref>` /
`sbx create <name> --kit <ref>` form in favor of `sbx run <ref>` /
`sbx create <ref>` (kit reference as the positional operand; the agent is now
read from the kit's own spec, so no trailing name operand is needed). Exactly
4 files in this repo use the old form, each with a redundant trailing
`"${kit_name}"` operand.

## Changes

### 1. Fix the deprecated `sbx run` invocation in 4 files

In each of:
- `scripts/bash.sh:28`
- `scripts/pi.sh:28`
- `scripts/compile-okf.sh:45`
- `tests/test-sandbox.sh:27`

Replace:
```bash
sbx run --detached --name "${kit_name}" --kit ./pi/ "${kit_name}"
```
with:
```bash
sbx run --detached --name "${kit_name}" ./pi/
```

No other logic in these scripts changes.

### 2. Bump the documented minimum sbx version to 0.42.0

Update "0.38.0 or newer" / "0.38.0" → "0.42.0 or newer" / "0.42.0" in:
- `README.md:92` (Requirements list)
- `README.md:233` (Troubleshooting: "unknown fields from `pi/spec.yaml`")
- `AGENTS.md:75`
- `CONTRIBUTING.md:38`

Keep the surrounding sentences (kit-spec v2 grammar rationale, `brew upgrade
sbx` remedy) as-is — only the version number changes.

### 3. Introduce project versioning: `VERSION` and `CHANGELOG.md`

md2okf has no existing `VERSION` or `CHANGELOG.md`. Per the user's decision,
this migration becomes the first tracked release:

- **`VERSION`** (repo root): a single line, `0.1.0`.
- **`CHANGELOG.md`** (repo root): [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)
  format, [Semantic Versioning](https://semver.org/spec/v2.0.0.html) — same
  structure as `sbxagent`'s `CHANGELOG.md`. Starts clean (no backfilled
  history from prior commits) with:

  ```markdown
  # Changelog

  All notable changes to this project will be documented in this file.

  The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
  and this project adheres to
  [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

  ## [Unreleased]

  ## [0.1.0] - 2026-09-07

  ### Changed

  - Bump the documented minimum `sbx` version from 0.38.0 to 0.42.0.
  - `scripts/bash.sh`, `scripts/pi.sh`, `scripts/compile-okf.sh` and
    `tests/test-sandbox.sh` now invoke `sbx run` with the kit path as the
    positional operand (`sbx run --name "${kit_name}" ./pi/`) instead of the
    deprecated `--kit <ref> <name>` form, which `sbx` v0.42.0 warns about on
    every invocation.
  ```

  (No `AGENTS.md` mention of `VERSION`/`CHANGELOG.md` is required — they are
  root project files, not part of the sandbox kit under `pi/`.)

## Verification

1. `make validate` — static kit-spec check, unaffected by this migration but
   confirms nothing else broke.
2. `sbx rm --force md2okf && make test-sandbox` — forces a fresh sandbox build
   using the corrected `sbx run` invocation (via `tests/test-sandbox.sh`) and
   runs the full `tests/test-sandbox-guest.sh` toolchain/config checks against
   it end-to-end. Requires sbx v0.42.0 installed and an active `sbx login`
   session.
3. Manually confirm `scripts/bash.sh` and `scripts/pi.sh` still attach to the
   same rebuilt sandbox without error (both reuse `md2okf` by name, so no
   separate rebuild needed once step 2 has created it).
4. `git grep -n "0.38.0\|--kit ./pi/"` — should return no hits, confirming the
   old version pin and syntax are fully replaced.
