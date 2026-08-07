# Upgrade md2okf to Docker Sandbox (sbx) v0.38.0

## Context

`make validate` fails on sbx 0.38.0:

```text
INVALID: artifact: invalid spec.yaml: yaml: unmarshal errors:
  line 11: field aiFilename not found in type spec.sandboxBlockV2
  line 16: cannot unmarshal !!map into []string
  line 22: field caps not found in type spec.specFileV2
  line 43: field commands not found in type spec.specFileV2
  line 68: field agentContext not found in type spec.specFileV2
```

**Root cause.** sbx embeds the kit-spec library `github.com/docker/sbx-kits-contrib`.
Through sbx 0.37.1 it embedded **v0.11.0**, which had a single decode struct shared by
`schemaVersion: "1"` and `"2"` — the version tag selected a couple of validation rules,
not the set of accepted field names. So [pi/spec.yaml](pi/spec.yaml), which declares
`schemaVersion: "2"` but spells its top-level blocks the old way (`caps:`, `commands:`,
`agentContext:`, `sandbox.aiFilename`, `sandbox.entrypoint.run`), loaded fine.

sbx 0.38.0 embeds **v0.12.0**, whose tag commit is literally
`feat(spec): fork decoder on schemaVersion for clean v2 grammar (#136)`. It adds
`spec/v2.go` (absent at v0.11.0) and forks `parseArtifactBytes` on `peekSchemaVersion`,
decoding `"2"` through a separate `specFileV2` struct with `yaml.KnownFields(true)`:

> the loader forks on schemaVersion (see `peekSchemaVersion`), so v1 and v2 never share a
> decode struct: v2 is a clean grammar with no legacy shims

Precisely, v2 still accepts the old spellings of the *leaf* types — `Credential`,
`ApiKeyInject`, `InstallCommand`, `InitFile`, `MountSpec` are reused verbatim, which is
why the whole `credentials:` block and every `command:`/`user:`/`description:` key inside
the installs decode without complaint. What v2 rejects is the **top-level and
sandbox-level container keys**. That is exactly the five reported lines, and nothing else
in the file.

**Proof of the diagnosis.** Changing nothing but `schemaVersion: "2"` → `"1"` makes the
current file validate on 0.38.0, because that routes it to the legacy decoder that still
knows all five keys. The file is a correctly-meaning spec wearing the wrong version label.

**Intended outcome.** Re-spell `pi/spec.yaml` in the real v2 grammar (rather than
relabelling it v1), fix the docs and CLI invocations 0.38.0 also deprecated, and record
the new minimum sbx version. `make validate` and the CI `validate-kit` job go green.

**Not local-only.** `.github/workflows/ci.yml` installs `sbx-releases/latest` by design,
so the `validate-kit` job is broken on `master` right now and stays broken until this
lands. Per your decision, CI keeps installing `latest` — it is the drift detector, and
it worked.

**Version trivia worth knowing:** there is no sbx 0.36.0. The line is 0.35.0 (2026-07-10)
→ 0.37.0 (2026-07-24) → 0.37.1 (2026-07-29) → 0.38.0 (2026-08-06); only an empty-bodied
`v0.36.0-rc1` exists. Nothing between 0.35.0 and 0.37.1 affects this repo.

## Already verified

I built the migrated spec in a scratchpad copy (the repo was not touched) and checked it
against the installed 0.38.0 binary:

- `sbx kit validate` → **VALID**, zero load-time warnings. (`sbx kit validate` does emit
  `WARN:` lines for genuinely deprecated fields — the migrated spec triggers none.)
- `sbx kit inspect --json` on the migrated v2 spec vs. the *current* spec forced down the
  legacy path differ in **exactly one field**, `schemaVersion` (`"1"` → `"2"`). Everything
  else in the canonical artifact is identical: `binary: pi`,
  `template: docker/sandbox-templates:shell-docker`, `aiFilename: AGENTS.md`,
  `runOptions: null`, `interactiveOptions: null`, 3 network allows, 1 credential,
  1 proxy-managed env var, 2 install commands, 5 files under `home`.
- `scheme: bearer` and `format: "Bearer %s"` produce byte-identical canonical artifacts.
  Per your decision we keep the explicit `format`.

An independent check ran the same comparison with sbx **0.37.1**'s binary on an untouched
copy of `pi/`: VALID there, INVALID on 0.38.0 — confirming 0.38.0 is where the break
lands and that nothing in the kit's meaning is wrong.

## The change

### 1. `pi/spec.yaml` — re-spell in v2 grammar

| current spelling | v2 spelling |
| --- | --- |
| `sandbox.aiFilename` | `agentInstructions.filename` |
| `agentContext:` (top level) | `agentInstructions.content` |
| `sandbox.entrypoint: {run: [pi]}` | `sandbox.entrypoint: [pi]` (plain list) |
| `caps.network.allow` | `permissions.network.allow` |
| `commands.install` | `setup.install` |

`schemaVersion`, `kind: sandbox`, `name`, `displayName`, `description`, the entire
`credentials:` block and both `install` command bodies are unchanged. `sandbox.command`
is not needed — the kit passes no args to `pi`.

The exact file that validates clean:

```yaml
schemaVersion: "2"
kind: sandbox
name: pi-kit
displayName: Pi kit
description: >
  Runs the Pi terminal coding agent in a Docker Sandbox microVM, configured for
  OpenRouter with DeepSeek defaults and proxy-managed API credentials.

sandbox:
  image: "docker/sandbox-templates:shell-docker"
  # Model and provider come from the kit's own config (files/home/.pi/agent/
  # settings.json + models.json), delivered to ~/.pi/agent/ in the VM. No
  # --provider/--model flags here — Pi resolves defaults from settings.json,
  # so entrypoint is the bare binary with no argument tail.
  entrypoint: [pi]

# The AI profile Pi reads, and the text appended to it. v2 folds the former
# sandbox.aiFilename and top-level agentContext into this one block.
agentInstructions:
  filename: AGENTS.md
  content: |
    ## Sandbox environment
    You are Pi running inside a Docker Sandbox microVM. The user's project is
    mounted as your workspace, and edits apply directly to the host working tree.
    `sudo` is passwordless. If a host is blocked by policy, ask the user to allow
    it with `sbx policy allow network "<host>"`.

# Outbound egress allowlist. Default-deny: every host the kit reaches must be
# listed. Model calls need openrouter.ai, Pi service bootstrap uses pi.dev.
# Pointing Pi at a different provider means adding its host here too — see
# "Using another provider" in the README.
permissions:
  network:
    allow:
      - registry.npmjs.org
      - openrouter.ai
      - pi.dev

# Credentials declare WHAT the kit needs and how the proxy injects it — not
# where it lives on the host (that comes from the user bindings / host env).
# proxyManaged: true sets OPENROUTER_API_KEY inside the container as a
# proxy-managed sentinel.
credentials:
  - service: openrouter
    apiKey:
      name: OPENROUTER_API_KEY
      proxyManaged: true
      inject:
        - domain: openrouter.ai
          header: Authorization
          format: "Bearer %s"

setup:
  install:
    # ... both existing install entries move here verbatim, unchanged ...
```

Both `setup.install` entries keep their `command`, `user: "1000"` and `description`
exactly as today.

Two traps in the comments, both verified:

- The current line 18 comment — `# Outbound egress allowlist (v2 caps.network replaces
  network.allowedDomains).` — must not be "corrected" to call `caps.network` the *v1*
  spelling. It never was: v1 was `network.allowedDomains`, and `caps.network` was an
  intermediate v2 draft. (0.38.0 itself still prints `WARN: deprecated field
  "network.allowedDomains": use 'caps.network.allow' instead (kit-spec v2)`, so upstream's
  own warning text is stale.) Dropping the version archaeology, as above, avoids the
  whole question.
- Do **not** rename `name: pi-kit`. For a `kind: sandbox` kit, sbx enforces that the agent
  positional in `sbx run … --kit ./pi/ pi-kit` equals the kit's `name:`. Renaming it would
  break [scripts/compile-wiki.sh:48](scripts/compile-wiki.sh#L48) and
  [scripts/bash.sh:28](scripts/bash.sh#L28), and orphan the sandbox-scoped secret.

### 2. `pi/README.md` — three stale references

- **Line 56** (`Using another provider`, step 3): `caps.network.allow` →
  `permissions.network.allow`. This one is user-facing instruction that, followed
  verbatim today, produces the exact INVALID spec we are fixing.
- **Line 109**: "A host that `caps.network` allows" → `permissions.network`.
- **Line 64**: `sbx secret set-custom pi-kit --host …` →
  `sbx secret set-custom --sandbox pi-kit --host …`. 0.38.0 dropped the positional
  sandbox name; custom secrets are global by default and `--sandbox` scopes them. Keeping
  `--sandbox pi-kit` preserves the existing scope, so the key already stored on this
  machine (`sbx secret ls` shows a `pi-kit`-scoped custom secret for `openrouter.ai`)
  keeps working with no re-entry.

**Do not global-replace `caps` in this file.** Line 39 — "catalogue caps its output at
4.1K" — is the English verb.

The surrounding prose about `set-custom` being experimental and having no stdin form is
still accurate on 0.38.0 (checked against `sbx secret set-custom --help`).

### 3. `README.md` — the once-only setup block (~lines 38–49)

- `sbx secret set -g openrouter` → `sbx secret set openrouter`. Verified: 0.38.0 prints
  `Flag --global has been deprecated, global is now the default for service secrets…` on
  every invocation.
- `sbx secret set-custom pi-kit \` → `sbx secret set-custom --sandbox pi-kit \`.
- The workaround comment **stays**: `docker/sbx-releases` issue #25 is still open (last
  activity 2026-07-17), so the second, custom secret is still required.

### 4. Record the sbx ≥ 0.38.0 floor

The migrated spec is **not** loadable by sbx ≤ 0.37.1: under contrib v0.11.0's single
`decodeSpecFile` with `KnownFields(true)`, `permissions:`, `setup:` and
`agentInstructions:` have no yaml tags at all and strict decoding rejects them. The
cutover is hard in both directions, so it needs writing down in three places:

- `AGENTS.md` — in the sandbox-kit paragraph and/or the "Always validate the sandbox kit
  spec" section: the kit is authored in **kit-spec v2 grammar and requires sbx ≥ 0.38.0**;
  `brew upgrade sbx` if `make validate` reports unknown fields.
- `README.md` — one line in the Development section beside the existing `make validate`
  guidance.
- [scripts/validate-spec.sh:6-8](scripts/validate-spec.sh#L6-L8) — the comment currently
  claims "Whatever schema the installed `sbx` bundles is the schema we check against, so
  keeping `sbx` current keeps the check current." That is now only half true: current is
  fine, *older* is not. Note the 0.38.0 floor. Optionally add a version guard next to the
  existing `command -v sbx` check, but the comment fix is the necessary part.

### 5. Files that need no change

`Makefile`, `scripts/compile-wiki.sh`, `scripts/bash.sh`, `.github/workflows/ci.yml`,
`.coderabbit.yaml`, `.markdownlint-cli2.yaml`, `pi/files/**`.

Specifically verified against 0.38.0, because each looked like a candidate:

- `sbx run --detached` still parses. The flag is now **hidden** from `sbx run --help`'s
  Flags list and survives only in the prose — do not "fix" it out of the scripts on the
  strength of its absence from `--help`.
- `sbx exec … -- pi …`, `sbx exec -it … -- bash`, `sbx rm --force`, `sbx ls -q`: unchanged.
- `sbx exec` stdin handling is unchanged since 0.32.0, so the `</dev/null` at
  [scripts/compile-wiki.sh:95](scripts/compile-wiki.sh#L95) stays and its comment block
  remains accurate.
- 0.38.0 added an error about `--detached` naming an existing sandbox; it is reachable
  only on the `--cloud` code path, which this repo never takes.

## Verification

```bash
make validate     # sbx kit validate ./pi/  → VALID
make lint         # markdownlint over the edited READMEs + AGENTS.md, shellcheck, jq, ruff
```

Then confirm the migration is behavior-preserving rather than merely valid:

```bash
sbx kit inspect ./pi/
# Name: pi-kit | Kind: sandbox | Schema: v2 | Binary: pi
# Template: docker/sandbox-templates:shell-docker | AI File: AGENTS.md
# Network: 3 allow, 0 deny | Credentials: 1 | Environment: 1 proxy-managed
# Commands: 2 install, 0 startup, 0 init files | Files: 5 home

sbx kit inspect --json ./pi/ | jq '.warnings // "none"'   # → "none"
```

Then an end-to-end run, which rebuilds the sandbox from the migrated kit:

```bash
make wiki                                               # builds a fresh pi-kit sandbox
sbx exec pi-kit -- sh -lc 'echo "$OPENROUTER_API_KEY"'  # a placeholder, never the real key
sbx exec pi-kit -- pi --list-models deepseek            # config reached ~/.pi/agent/
sbx exec pi-kit -- cat ~/AGENTS.md                      # agentInstructions.content is appended
```

The last two are the only genuinely new risk surface. `agentInstructions` is a different
decode path from the `aiFilename` + `agentContext` pair even though it normalizes to the
same artifact fields, so the AI profile is worth eyeballing once.

One thing this migration explicitly does **not** touch: `Manifest.SchemaVersion` stays
`"2"`, which is the value the engine keys its credential-binding regime on. The current
kit already declares `"2"`, so the proxy-managed `OPENROUTER_API_KEY` path — the repo's
only credential surface — is on the same regime before and after. That is also why
relabelling the file to `schemaVersion: "1"`, though it validates in one character, is
the wrong fix: it would be the only change here that actually moves runtime behavior.
