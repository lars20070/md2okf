# Plan: upgrade sbx 0.50.0 → 0.54.0 and kits schema v2 → v3

## Context
Since sbx v0.51.0 the built-in agents (`claude`, `codex`, …) are published schema-v3 kits (`docker.io/sbx/<name>:latest`), and v1/v2 kits cannot be combined with v3. Our `claude` and `codex` kits are v2 `extends:` kits and no longer load. `pi` is a standalone v2 kit on its own image. Nothing in the driver uses the removed flags (`exec --detach/--privileged`, `sbx ports`, `logout`), and `sbx run --detach` still works. Pin **0.54.0** (v0.54.1 only fixes removal of macOS secrets saved before an upgrade; untested).

Decisions (user): **Pi → v3 workload** (keep the pinned `pi-image` digest in the recipe `FROM`); **Claude/Codex → v3 mixins**; **traces → additional workspace** `HOST_SESSIONS:/home/agent/<trace dir>`, deleting the in-sandbox bind scripts.

This plan absorbs the rough upgrade guide from another project (`upgrade-sbx.md`, now deleted) and the review in `review-plan.md`. Claims marked **(seen)** were observed in that other project and still need to be re-checked here. Claims marked **(verified)** were checked against this repo, the v0.54.0 release assets or the published OCI descriptors.

## Facts established offline (verified)
- v0.54.0 `DockerSandboxes-linux.tar.gz` SHA-256 = `eded29017121a857c98d4a91cad593f6a9e00f4010e830679bd385f4a5edba4d` (same bytes as `-linux-amd64.tar.gz`). CI keeps the `DockerSandboxes-linux.tar.gz` asset name.
- v0.54.0 bundles `sandbox-kit-spec/v3 v3.0.0-m.12`. Use kit-tck from that tag.
- Published workloads (as of 2026-11-26): `docker.io/sbx/claude@sha256:a91195e9e3b6f316fda9afd5228b26d65abd486dc6e627682c2aabbd59747886` provides `claude@2.1.332`; `docker.io/sbx/codex@sha256:eb621d203636085c03be079c27439c805c8e46927c27f5daf6210ed8e6c62cd8` provides `codex@0.172.0`. Both are on Debian 13/DHI, provide `python@3.14`, `uv@0.13`, `ripgrep`, `jq`, `tree`, `curl`, `gh` and Docker, and do **not** provide Node or npm. Both offer `agent-context@1` and `@2`. Claude's v2 profile is `~/.claude/CLAUDE.md`, not `../CLAUDE.md`. Both declare their own API-key credential, so the mixins must not redeclare it.
- `pi-image@sha256:134b48cf…` (amd64) is Ubuntu 26.04 built from `shell-docker`. It has `User agent`, `WorkingDir /home/agent`, label `com.docker.sandboxes.start-docker=true`, and `NPM_CONFIG_PREFIX=/usr/local/share/npm-global` on PATH.
- Driver facts: `workbench.sandbox_name()` hard-codes `md2okf-<agent>`, and `tests/test-sandbox.sh` repeats it. `sandbox.create()` runs `sbx rm --force <name>` **before** `sbx run`. `_run` uses `stdin=DEVNULL` with captured output. The fingerprint includes the sbx version. `compile.py` passes the host path `wb.work_md/<doc>` in the prompt and runs guest `merkleokf … wb.work_okf`, and `resolve_sandbox_state` probes `wb.work_okf` in the guest. All of these assume each workspace is mounted at its host path.
- `--shell` deliberately warns and opens when the credential check fails (`cli.py` ~L181–190).
- All four helper CLIs build with Hatchling. The shims run `uv tool run --from …`, so a cold cache needs PyPI and `files.pythonhosted.org` at **runtime**.
- `MD2OKF_STATE_DIR/sessions` is referenced in the claude kit's `agentInstructions`, `kits/codex/files/home/.codex/AGENTS.md`, the Pi `agentInstructions`, `tests/test-sandbox-guest-common.sh`, `docs/configuration.md`, `cli.py` and `workbench.py`.
- `validate-spec.sh` already fails on zero matches. Tests that name `spec.yaml` explicitly: `test_kits.py:23,89,171`, `test_agents.py:36,111`, `test_resources.py:14`, `test_package.py:33`, and `test_workbench.py` (fixtures only). Wrapper references: `agents.py:142-182`, `tests/test_compile.py:256`, `tests/test_protocol_claude.py:155-156`. The CI job `test-shell` runs `make test-shell`.

## Release-note actions that apply here (from the guide, still to be confirmed live)
| Release | Change | Action |
| --- | --- | --- |
| 0.50 | Each local source kit rebuilds once after upgrade | Expect one slow create |
| 0.50 | Persistent volumes may survive `sbx rm`; the v3 spec says removal deletes them | Treat `sbx rm` as destructive |
| 0.50 | `--mount HOST:PATH` binds only `host-mount@1` targets | Use positional workspaces, not `--mount` |
| 0.51 | Additional workspaces accept `PATH:TARGET[:ro]` | Basis of the trace mount |
| 0.51 | Custom secrets without destination hosts no longer substitute | Every credential names its inject domains |
| 0.51 | A failed startup command only warns | No startup hook as a gate |
| 0.51 | Install logs in `/var/log/sbx-kits/<kit>/install-<n>.log` | Read them on a failed create |
| 0.53 | `sbx run <agent> -- <args>` keeps entrypoint args | No duplicated subcommand |
| 0.53 | Argument-list install hooks are passed literally | Use string commands when a shell is needed |
| 0.53 | Update notices and previews go to stderr | Don't parse stderr as data |
| 0.54 | Startup refuses a saved mount whose source resolves elsewhere | `sbx umount` it and mount again |
| 0.54 | Existing kit permissions may need confirmation again | See work step 2e |

## Work, in order

0. **Safety before the host runs 0.54.0** (user, host). The first `md2okf` run under 0.54.0 with the usual state directory sees a fingerprint mismatch and `sbx rm --force md2okf-<agent>` **before** the new sandbox builds. So:
   - Confirm that the transcripts in `$XDG_STATE_HOME/md2okf/<agent>/sessions` are on the host and complete. Copy out anything that lives only in a sandbox.
   - Do not run `md2okf`, `python -m md2okf.sandbox` or `make test-sandbox` against the default name or state until cutover (step 11).
   - Retire old sandboxes one by one by exact name (`sbx rm --force md2okf-claude`, …) after checking each, never by glob.

1. **Version bump** (no live effect): `SBX_VERSION` → `0.54.0`; `README.md:144`; `ci.yml` `expected_sha256` → `eded2901…ba4d`; CHANGELOG `[Unreleased]` (sbx 0.54.0, kit schema v3, Debian base for Claude/Codex, hook/trace changes); follow the CONTRIBUTING "The sbx minimum" checklist.

2. **Pilot: the `claude` mixin, end to end, isolated.** An unchanged launcher cannot exercise the new composition, so the pilot includes the minimum driver and harness changes. Read `WORKSPACE_DIR` live before deriving any path from it.
   a. **Isolation plumbing.** Add a maintainer-only override for the sandbox name, e.g. `MD2OKF_SANDBOX_NAME`, honoured by `workbench.sandbox_name()` and by `tests/test-sandbox.sh` (which then asks the driver for the name instead of repeating the rule). Run the pilot with that name **and** a temporary `XDG_STATE_HOME`. Changing only the state dir leaves the name occupied and loses its ownership marker, so the driver refuses with `UnownedSandboxError`. Changing only the name would reuse the real workbench.
   b. **Kit.** `kits/claude/md2okf-claude.yaml` + `kits/claude/md2okf-claude.dockerfile`, with unique stems that are not `claude`. Same-stem kits collide **(seen)**, and v0.54.0's offline validator accepted a `claude/md2okf-claude.yaml` layout as a v3 source kit (review). Settings:
      - `kind: mixin`, `requires: ["claude"]`, `sourceUrl`, no `name:` (strict decoding rejects unknown keys).
      - `network-policy@1` split into `install` and `runtime`, compared host by host with the v2 list. Apt goes to `deb.debian.org` and `dhi.io`. **Runtime** keeps `pypi.org` and `files.pythonhosted.org` for the `uv tool run` shims, plus npm, GitHub and mqlang as needed. An absent phase grants nothing, and workload grants may not cover our install phase **(seen)**.
      - Instructions as an `agent-context@2` body-only contribution, which lands in `~/.claude/CLAUDE.md`. Don't mix `@1` and `@2`.
      - `lifecycle@1` install hooks with an explicit `env:` list: the proxy vars (`HTTP_PROXY HTTPS_PROXY NO_PROXY http_proxy https_proxy no_proxy`), `NPM_CONFIG_PREFIX` where npm runs, and `WORKSPACE_DIR` where used. Hooks get only a small baseline otherwise, which the guide calls the most common migration bug.
      - **Node/npm**: the workload provides none. Install `nodejs-24` from DHI (or Debian's `nodejs`/`npm`) in a root hook **before** the agent-user npm hook. cspell 10.0.1 needs Node ≥ 22.18.0, so verify the version.
      - `fd-find` package with the executable `fdfind`. Check whether `python3` is on PATH or only `python3.14`.
      - mq, okfctl: pinned, checksummed downloads. Move them into the recipe where possible, which drops the install-time GitHub grant. Apt stays a hook because it needs the real base's package DB.
      - Skills tree and `check-okf.sh` (with `chmod 0755`) go into the recipe layer. `/home` is owned by root, and `/home/agent` and `~/.claude` by uid 1000. Our layer's directory owners replace the base's. Don't ship any file the workload ships or writes (settings, MCP config); merge via a hook instead.
      - Helper shims (`inspectmd`, `inspectokf`, `sizeokf`, `merkleokf`): `$VAR` stays literal in v3 `lifecycle@1` files. Either write them from an install hook with `env: [WORKSPACE_DIR]`, or keep `$WORKSPACE_DIR` for runtime expansion and make sure it exists under both the agent session and plain `sbx exec`.
      - Drop the entrypoint, the startup hook and the `md2okf-agent` shim. A mixin's entrypoint, command, user and workdir are ignored anyway.
   c. **Driver, the minimum for the pilot.** Add per-agent `kit_dir`, `workload_ref` and `trace_target` fields to `Agent`. The launch for claude/codex becomes `sbx run --detach --name N [-e …] --kit <abs mixin dir> <workload_ref> <work_okf> <mounts…>`. Local kits need `./` or an absolute path, and `--kit` takes mixins only. The mount `sessions` becomes `HOST_SESSIONS:/home/agent/.claude/projects`, writable, created by `ensure_roots` before launch. Keep the order (okf rw first; md, scripts and SPEC.md `:ro`). Use **one argv builder** for `create()` and for the `--dry-run` rendering.
   d. **Guest paths (review #4).** Under plain `sbx exec`, check `pwd` and `WORKSPACE_DIR`, read the staged document by the exact host path the prompt uses and the sibling `SPEC.md`, run `merkleokf --nolog -L 0 <wb.work_okf>`, and run ensure twice to prove reuse (the probe passes and there's no recreate). If guest paths differ from host paths, map host→guest consistently in mounts, prompts, the hash, the probe and the dry run.
   e. **First-run approval (review #3).** In a clean permission state, create through the **driver**: `stdin=/dev/null` and captured output, as the driver really runs it. If sbx needs a kit-permission confirmation, find the supported one-time host action for this composition, document it, make `create()` surface sbx's actionable diagnostic instead of a bare failure, and prove that a retry through md2okf succeeds. A manual interactive launch alone doesn't count.
   f. **Instructions and skills.** Update `tests/test-sandbox-guest-claude.sh`, which reads `../CLAUDE.md`, to check `~/.claude/CLAUDE.md` for both the OKF contract and the workload's own guidance. Confirm skill discovery with the host shared-skills store enabled and with it empty.

3. **`codex` mixin**, same pattern: `kits/codex/md2okf-codex.{yaml,dockerfile}`, `requires: ["codex"]`, trace target `/home/agent/.codex/sessions`. **Instructions**: the workload offers `agent-context@2`, which writes `~/.codex/AGENTS.md`, so the old "outside a git project" reason for a static file no longer applies. Prefer `agent-context@2`. If we keep a shipped `~/.codex/AGENTS.md` instead, it overlaps a workload-managed file, so prove that both the OKF contract and the workload guidance survive creation and restart.

4. **`pi` workload**: `kits/pi/md2okf-pi.{yaml,dockerfile}`.
   - Recipe: `FROM docker.io/sbx/pi-image@sha256:134b48cf…` (index digest, both archs), `USER agent`, `WORKDIR` matching the old layout (don't derive the workspace from it), `ENTRYPOINT ["pi"]`. Check for `bash`, `sh`, `git`, `curl`, CA certs and uid-1000 `agent`. Test both launch modes. Headless is `ENTRYPOINT`+`CMD`. Interactive is `ENTRYPOINT`+`lifecycle@1 interactive` (or `CMD`). A `CMD` that repeats the command becomes a stray argument.
   - The base is **Ubuntu 26.04, not Debian**. Keep the Ubuntu apt hosts (`archive`/`security`/`ports.ubuntu.com:80`) and `download.docker.com` in `install`, for both architectures. **Decide** whether to keep the in-sandbox Docker engine via `dockerd@1`, which replaces the `start-docker` label. Recommendation: drop it unless something uses Docker inside Pi.
   - Capabilities: `sbx@1`; `network-policy@1` with `install` + `runtime`, covering every v2 host incl. openrouter.ai, pi.dev, api.github.com, github.com, context7.com and runtime PyPI for the shims.
   - **Credentials (review #2)**: v3 credentials are required by default, and a required unbound service can stop creation before the VM exists. That would break `--shell`'s warn-and-open contract. So declare `credential@1` **openrouter with `optional: true`**, keep the driver's sentinel check (`key_is_proxy_managed`) on create and reuse, and keep **github `optional: true`** independently. Every inject domain must appear literally in the allow list of every phase the credential declares. Name the GitHub variable what consumers expect (`GITHUB_TOKEN`, or `GH_TOKEN` plus recipe `ENV`/arg), and verify under plain exec that `gh` and the stdio `github-mcp-server` (via `GITHUB_PERSONAL_ACCESS_TOKEN` in `mcp.json`) both get it. That replaces the entrypoint/wrapper exports.
   - Carry over everything Pi ships: `settings.json`, `models.json`, `mcp.json`, `AGENTS.md`, `skills/`, the four shims, the npm proxy config, markdownlint-cli2/cspell, ruff/yamllint, mq, okfctl and github-mcp-server (SHA-256 pinned), plus `pi install` context7. Fold the v2 `agentInstructions` environment text into the shipped `~/.pi/agent/AGENTS.md`, or a declared profile, without the `$MD2OKF_STATE_DIR` wording. Trace target: `/home/agent/.pi/agent/sessions`.

5. **Shared helpers**: delete `files/home/.local/lib/md2okf/{mount-state,md2okf-agent}.sh` in all kits. Remove `WRAPPER` from `agents.py` (nothing else relies on it once credential exports move to the kit). Update `tests/test_compile.py:256`, `tests/test_protocol_claude.py:155-156` and `tests/test_kits.py` `_SHARED_HELPERS`.

6. **Driver, the rest** (`sandbox.py`, `cli.py`, `workbench.py`, `resources.py`, `agents.py`):
   - Pi launch: `sbx run --detach --name N [-e …] <abs workload dir> <work_okf> <mounts…>`. Keep argv starting `sbx run --detach`.
   - Remove the `MD2OKF_STATE_DIR` injection if nothing else consumes it. Fix every instruction and doc that still points agents at `$MD2OKF_STATE_DIR/sessions`.
   - **Workload update policy**: bare names resolve through local `kit.shortcuts` and float. Hashing the literal name cannot detect a changed upstream. Recommendation: pin `workload_ref` to the tested multi-platform kit **index digest** (above) and hash it in `fingerprint()`; bumping it is a deliberate change. If we follow upstream instead, document when a cached or reused sandbox advances, what `--fresh` does, and that `--pull always` only affects creation (default `--pull missing` for v3).
   - Update `_format_sbx_run`/the dry-run text and the `WORKDIR` mentions (`cli.py:44`, `workbench.py:566`, `docs/configuration.md:28`).

7. **Validation** (`scripts/validate-spec.sh`, CI `validate-kit`, `.coderabbit.yaml` `**/spec.yaml`). `sbx kit validate` fails on v3 source kits ("…has no kit builder configured") **(seen)**. Build each kit and check the artifact instead:
   ```bash
   layout="$(mktemp -d)"
   docker buildx build --platform linux/amd64,linux/arm64 \
     --provenance=mode=max,version=v1 \
     -f "$kit_dir/$stem.yaml" \
     --output "type=oci,dest=$layout,tar=false,name=$stem" "$kit_dir"
   kit-tck validate --layout "$layout" latest
   ```
   - kit-tck from the v3.0.0-m.12 release, checksum-verified. Pin the `# syntax=docker/sandbox-kit:3@sha256:…` frontend by digest in each descriptor. The builder must support OCI export, and a foreign architecture needs QEMU or a native builder. The runner needs Docker but not `sbx`.
   - Validate each **registered** agent's kit by name, and also discover unregistered kits under development. Fail on any missing registered kit or zero kits; a "≥3" count can hide a missing one. Keep SBX_VERSION enforcement.
   - Don't call it "offline": a cold build pulls images and the frontend. Document local Buildx, builder and TCK requirements. This host-Docker validation is separate from the end user's sbx source-kit builder (`sbx-kit-builder`), which needs no host Docker.
   - OCI validation checks one kit at a time and cannot see mixin/workload composition, file or credential conflicts. Only the live pilot can.

8. **Tests**: update `FakeSbx` (`conftest.py`), `test_sandbox.py`, `test_cli.py`, `test_workbench.py`, `test_kits.py`, `test_agents.py`, `test_resources.py`, `test_package.py`, `test_compile.py` and the protocol-test fixtures to the new layout and argv. Delete `tests/test-mount-state.sh`, `make test-shell` and the CI `test-shell` job. Adapt `test-sandbox*.sh`: read `WORKSPACE_DIR`, the trace mount is a host-side bind, no `sudo mount`, no wrapper check. **Keep** the host-side trace write probe, the read-only-input checks and the host-only ownership-marker checks (today partly in the deleted bind tests). Add helper runs on real input from a cold cache, and Pi's no-GitHub and `--no-mcp` compile cases.

9. **Packaging**: `pyproject.toml` force-includes the whole kit dirs. Confirm that descriptors, recipes, dotfiles and `.dockerignore` land in **both** wheel and sdist, keep the sdist→wheel asset check, and run `make dist`. Then install the package outside the checkout and do a detached create with the packaged launcher.

10. **Docs**: README (incl. the mermaid node), AGENTS.md (kit-spec v2 wording, validation section, the 0.49.2 note, the `md2okf-agent` paragraph, `make test-shell`), CONTRIBUTING (validation, the minimum), `docs/architecture.md`, `docs/configuration.md`, `docs/usage.md`, kit READMEs (Pi "Bumping Pi", gateway instructions, workload digest bump) and `lat.md/` (kits, sandbox fingerprint/create, development release/testing). Remove `kits/pi/.DS_Store`.

11. **Cutover** (user, host): after all three pilots pass, retire each old `md2okf-<agent>` by exact name, then run each agent with `MD2OKF_AGENT` set explicitly against the usual state, so the existing `sessions/` carries over.

## Verification
- **Offline (agent)**: `make lint`, `make validate` (buildx + kit-tck), `make test-md2okf`, `make test-clis`, `make dist`, `uv run md2okf --dry-run md/`.
- **Live (user, host)**: `sbx --version` = 0.54.0 and `sbx login`. For each agent, under the pilot name and temp state: `make test-sandbox AGENT=<a>`, then this checklist:
  - [ ] Create (through the driver, clean permission state), attach, detached create, `sbx exec`, stop, start again
  - [ ] Workspace order, `:ro` inputs, working dir; prompt doc path, `SPEC.md`, `merkleokf` on `work_okf`; second ensure **reuses**
  - [ ] Every tool and helper shim, on real input from a cold cache, in the agent session **and** under plain `sbx exec`
  - [ ] Agent loads its instructions (Claude `~/.claude/CLAUDE.md`, Codex `~/.codex/AGENTS.md`, Pi `~/.pi/agent/AGENTS.md`); skills found with the shared store on and off
  - [ ] Owners of `/home`, `/home/agent`, the config dir and the trace dir; the agent can write its config beside the trace mount
  - [ ] An allowed host works and an undeclared host is refused
  - [ ] Credentials: a **fresh unbound Pi** sandbox — `--shell` warns and opens; compile, `--agent` and `python -m md2okf.sandbox` exit 2 with the OpenRouter remedy. GitHub bound and unbound (`gh`, MCP)
  - [ ] Traces appear on the host; an existing trace survives recreation and restart
  - [ ] The packaged install from outside the checkout
  - [ ] Smoke run `MD2OKF_AGENT=<a> md2okf -o "$(mktemp -d)" tests/fixtures/smoke.md`
- Per repo rules: no `git commit`/`git push`; stage the changes and hand over a drafted commit message.

## References (pinned to the spec v0.54.0 bundles)
- Migration skill: https://github.com/docker/sandbox-kit-spec/blob/v3.0.0-m.12/skills/migrate-kit-to-v3/SKILL.md
- Field mapping: https://github.com/docker/sandbox-kit-spec/blob/v3.0.0-m.12/skills/migrate-kit-to-v3/FIELD-MAPPING.md
- Recipe ownership rules: https://github.com/docker/sandbox-kit-spec/blob/v3.0.0-m.12/skills/create-kit-v3/RECIPES.md
- Workload example: https://github.com/docker/sandbox-kit-spec/tree/v3.0.0-m.12/examples/claude
- Capabilities: `credential@1`, `agent-context@2`, `dockerd@1` under https://github.com/docker/sandbox-kit-spec/tree/v3.0.0-m.12/docs/spec/capabilities/com.docker.sandbox
- Inspect a published descriptor without a daemon:
  ```bash
  ref=docker.io/sbx/claude
  digest="$(docker buildx imagetools inspect "$ref:latest" --raw |
    jq -r '[.manifests[] | select(.platform.architecture == "amd64")][0].digest')"
  docker buildx imagetools inspect "$ref@$digest" --raw |
    jq -r '.annotations["vnd.docker.sandbox.kit.descriptor"]' | jq '{provides, capabilities}'
  ```

### v2 → v3 field map
| v2 | v3 |
| --- | --- |
| `spec.yaml` | `<stem>.yaml` + `<stem>.dockerfile` |
| `kind: sandbox` / `extends: X` | `kind: workload` / `kind: mixin` + `requires: ["X"]` |
| `name:` | removed |
| `sourceURL:` | `sourceUrl:` |
| `sandbox.image` / `entrypoint` / `command.default` | recipe `FROM` / `ENTRYPOINT` / `CMD` (workloads only) |
| `sandbox.command.interactive` | `lifecycle@1` `interactive` (one owner per composition) |
| `environment.variables` | recipe `ENV` (last stage), or an arg with `env:` |
| `permissions.network` | `network-policy@1` `install` / `runtime` |
| `credentials` | `credential@1`, one per service (required unless `optional: true`) |
| `setup.install` / `startup` / `files` | `lifecycle@1` |
| `agentInstructions` | `agent-context@2` |
| `start-docker` label | `dockerd@1` |

### Skeletons
Mixin descriptor and recipe:
```yaml
# syntax=docker/sandbox-kit:3@sha256:8561468d43a0466e24dd048e3c6c2115d878ee36d71c4571195f1de2a63c2b5b
schemaVersion: "3"
kind: mixin
version: "1.0.0"
displayName: …
description: …
sourceUrl: https://github.com/…
licenses: [MIT]
requires: ["claude"]
capabilities:
  - type: com.docker.sandbox/network-policy@1
    config:
      install: { allow: ["deb.debian.org", "dhi.io"] }
      runtime: { allow: [ … ] }
  - type: com.docker.sandbox/lifecycle@1
    config:
      install:
        - command: |
            set -eu
            apt-get update
            apt-get install -y --no-install-recommends …
          user: "0"
          env: [HTTP_PROXY, HTTPS_PROXY, NO_PROXY, http_proxy, https_proxy, no_proxy]
          description: …
  - type: com.docker.sandbox/agent-context@2
    config:
      content: |
        …
```
```dockerfile
FROM debian:trixie-slim AS build
COPY files/ /src/
RUN set -eu; \
    install -d -o 0 -g 0 -m 0755 /out/home; \
    install -d -o 1000 -g 1000 -m 0755 /out/home/agent; \
    cp -R /src/home/. /out/home/agent/; \
    chown -R 1000:1000 /out/home/agent
FROM scratch
COPY --from=build /out/ /
```
Optional GitHub credential (Pi):
```yaml
  - type: com.docker.sandbox/credential@1
    optional: true
    config:
      service: github
      phase: runtime
      apiKey:
        name: GITHUB_TOKEN
        proxyManaged: true
        inject:
          - { domain: api.github.com, header: Authorization, format: "Bearer %s" }
          - { domain: github.com, scheme: basic, username: x-access-token }
```
Other v3 traps: `${{ kit.args.x }}` is found by text search, even in YAML comments, and must name a declared arg. With several kits, scope args as `--kit-arg <kit>.<arg>=…`. Two `lifecycle@1` files with the same path are rejected.
