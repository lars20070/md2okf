# Upgrade md2okf to sbx 0.38.0

## Findings

- Local sbx `v0.38.0` reproduces the five decode failures in
  [`pi/spec.yaml`](../../pi/spec.yaml): `aiFilename`, mapping-form `entrypoint`,
  `caps`, `commands`, and `agentContext` are legacy fields.
- [Docker's v0.38.0 release](https://github.com/docker/sbx-releases/releases/tag/v0.38.0)
  makes schema v2 strict: the loader forks on `schemaVersion`, so a file
  declaring `"2"` must use only the
  [v2 kit grammar](https://docs.docker.com/ai/sandboxes/customize/kit-reference/).
- Third-party v2 kit credentials require a host-side binding. Because
  `make wiki` launches detached, setup must establish that binding
  interactively once while retaining the existing custom-secret workaround.

## Implementation

1. Migrate [`pi/spec.yaml`](../../pi/spec.yaml) without changing its effective
   behavior:
   - Move `sandbox.aiFilename` and top-level `agentContext` into
     `agentInstructions.filename` and `.content`.
   - Flatten `sandbox.entrypoint.run: [pi]` to `sandbox.entrypoint: [pi]`.
   - Rename `caps.network` to `permissions.network` and `commands.install` to
     `setup.install`.
   - Keep the image, network hosts, OpenRouter credential injection, install
     command bodies/users, and static files unchanged; update comments to use
     v2 terminology.
2. Update user setup in [`README.md`](../../README.md): require sbx `>=0.38.0`,
   replace deprecated `sbx secret set -g openrouter` with the
   global-by-default form, scope `set-custom` with `--sandbox pi-kit`, and add a
   one-time interactive custom-kit launch to approve the v2 OpenRouter
   credential binding before detached `make wiki` runs.
3. Update [`pi/README.md`](../../pi/README.md) to reference
   `permissions.network`, use the new `set-custom --sandbox` syntax, and explain
   that another provider also needs one-time v2 credential approval before
   unattended use.
4. Record kit-spec v2 and the sbx `>=0.38.0` minimum in
   [`AGENTS.md`](../../AGENTS.md), including the upgrade hint for old CLIs.
   Leave [`scripts/validate-spec.sh`](../../scripts/validate-spec.sh),
   [`Makefile`](../../Makefile), and
   [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml) unchanged:
   their commands remain valid, and CI intentionally testing the latest sbx
   should continue detecting schema drift.

## Verification

- Run `sbx version`, `make validate`, and `sbx kit inspect --json ./pi/`;
  require v0.38.0+, a valid artifact, and no warnings while confirming the same
  entrypoint, image, three allowed hosts, credential, two install commands, and
  copied files.
- Run `make lint` for the YAML-adjacent documentation and repository checks.
- After the one-time binding approval, rebuild the sandbox and smoke-test that
  `OPENROUTER_API_KEY` is still a proxy-managed placeholder, Pi configuration
  files land under `~/.pi/agent/`, and `agentInstructions.content` appears in
  `~/AGENTS.md`. Run `make wiki` only when the configured credential/model is
  available; otherwise report the unperformed external-call check explicitly.
