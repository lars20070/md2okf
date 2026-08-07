# Upgrade md2okf to sbx 0.38.0

## Findings

- Local sbx `v0.38.0` reproduces the five decode failures in
  [`pi/spec.yaml`](../../pi/spec.yaml): `aiFilename`, mapping-form `entrypoint`,
  `caps`, `commands`, and `agentContext` are legacy fields.
- [Docker's v0.38.0 release](https://github.com/docker/sbx-releases/releases/tag/v0.38.0)
  makes schema v2 strict: the loader forks on `schemaVersion`, so a file
  declaring `"2"` must use only the
  [v2 kit grammar](https://docs.docker.com/ai/sandboxes/customize/kit-reference/).
- The migration leaves `schemaVersion: "2"` and therefore the existing
  credential-binding regime unchanged. The current custom-secret workaround
  remains necessary while the referenced upstream sbx issue is open.

## Implementation

1. Migrate [`pi/spec.yaml`](../../pi/spec.yaml) without changing its effective
   behavior:
   - Move `sandbox.aiFilename` and top-level `agentContext` into
     `agentInstructions.filename` and `.content`.
   - Flatten `sandbox.entrypoint.run: [pi]` to `sandbox.entrypoint: [pi]`.
   - Rename `caps.network` to `permissions.network` and `commands.install` to
     `setup.install`.
   - Keep `name: pi-kit`, the image, network hosts, complete OpenRouter
     credential block (including `format: "Bearer %s"`), install command
     bodies/users, and static files unchanged. No `sandbox.command` is needed.
     Update comments to use v2 terminology.
2. Update user setup in [`README.md`](../../README.md): require sbx `>=0.38.0`,
   replace deprecated `sbx secret set -g openrouter` with the
   global-by-default form, and scope `set-custom` with `--sandbox pi-kit`.
   Retain the custom-secret workaround and its upstream issue reference.
3. Update [`pi/README.md`](../../pi/README.md) to reference
   `permissions.network` and use the new `set-custom --sandbox` syntax.
4. Record kit-spec v2 and the sbx `>=0.38.0` minimum in
   [`AGENTS.md`](../../AGENTS.md), including the upgrade hint for old CLIs.
   Update the explanatory comment in
   [`scripts/validate-spec.sh`](../../scripts/validate-spec.sh) with the same
   minimum; no version guard is needed because schema validation already fails
   clearly on older CLIs. Leave the runtime scripts, [`Makefile`](../../Makefile),
   and [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) unchanged:
   their commands remain valid, and CI intentionally testing the latest sbx
   should continue detecting schema drift.

## Verification

- Run `sbx version`, `make validate`, and `sbx kit inspect --json ./pi/`;
  require v0.38.0+, a valid artifact, and no warnings while confirming the same
  entrypoint, image, three allowed hosts, credential, two install commands, and
  copied files.
- Run `make lint` for the YAML-adjacent documentation and repository checks.
- Rebuild the sandbox and smoke-test that `OPENROUTER_API_KEY` is still a
  proxy-managed placeholder, Pi configuration files land under
  `~/.pi/agent/`, and `agentInstructions.content` appears in `~/AGENTS.md`.
  Run `make wiki` only when the configured credential/model is available;
  otherwise report the unperformed external-call check explicitly.
