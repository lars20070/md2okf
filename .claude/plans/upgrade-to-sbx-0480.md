# Upgrade sbx 0.45.0 → 0.48.0

## Context

md2okf requires sbx 0.45.0 (`SBX_VERSION`). We want to move to 0.48.0 and,
where an upstream issue is now fixed, delete its workaround outright. I
checked each issue's status upstream:

| Upstream | Status at 0.48.0 | Effect here |
| --- | --- | --- |
| 0.48 CLI refactor: `sbx run --detached` is rejected | breaking | rename to `--detach` |
| #420: startup steps not replayed after a daemon restart | **fixed** | the startup step alone covers every start: remove the entrypoint call site **and** the `md2okf-agent` wrapper (user's choice) |
| #25: sandbox-scoped credentials | **fixed**, closed | drop the second `sbx secret set-custom` OpenRouter step |
| #685: `sbx kit validate` needs a daemon and `sbx login` since 0.47 | `--offline` exists only in 0.49 release candidates; confirmed here that 0.48.0 fails with "not signed in to Docker" | keep `kit validate`, switch off CI's `validate-kit` job (user's choice) |
| #629 virtiofs cache, #553 `kit sign` on GHCR | fixed | not used in md2okf, nothing to do |

Already checked against 0.48.0, no change needed:
- `sbx ls -q` still prints names only.
- `sbx rm --force` and `sbx exec` keep their flags.
- `sbx secret set --oauth` is still "openai/global only", so the Claude remark stays true.
- No kit declares an agent-context directory, so `../CLAUDE.md` stays where it is.

The kit fingerprint (`workbench.fingerprint`) hashes the sbx version and the
kit tree, so every existing sandbox rebuilds on first use. That is expected.

## Changes

### 1. Version floor
- `SBX_VERSION` → `0.48.0`.
- `.github/workflows/ci.yml` `validate-kit`: `expected_sha256` →
  `609a2e4b881ba9a7fd21543077e53d3b863a6b99eebee1f208e51a097ab56a05`
  (`DockerSandboxes-linux.tar.gz`, v0.48.0). With the pin current, re-enabling
  the job only means deleting `if: false`.
- `README.md` "Install sbx": `0.45.0` → `0.48.0`.

### 2. `--detached` → `--detach`
- `src/md2okf/sandbox.py:149` (`create`) and `src/md2okf/cli.py:158` (dry-run line).
- `tests/conftest.py:155` (the fake's dispatch), plus every
  `["sbx", "run", "--detached"]` and `sbx run --detached` string in
  `tests/test_cli.py`, `tests/test_sandbox.py` and `tests/test_workbench.py`.

### 3. #420: one trace-bind call site, the startup step
In each of `kits/{pi,claude,codex}/spec.yaml`:
- **Entrypoint.** Pi: replace the `sh -c` block with `entrypoint: [pi]`.
  Claude and Codex: delete the entrypoint override (their whole `sandbox:`
  section and its comment), so the parent kit's own entrypoint applies.
- **Startup comment.** Rewrite the `startup:` comment: bind mounts do not
  survive a stop, and this step runs on every start, including after a daemon
  restart, so it is the only call site. `mount-state.sh` stays idempotent.
- **Shim.** Delete the `/home/agent/.local/bin/md2okf-agent` entry from
  `setup.files`.
- Delete `kits/*/files/home/.local/lib/md2okf/md2okf-agent.sh` (three copies).
- `mount-state.sh` itself is unchanged: the already-bound `stat` check still
  makes a repeated start a no-op.

### 4. Remove the wrapper from the driver
- `src/md2okf/agents.py`: delete `WRAPPER` and its comment. `compile_args` and
  `interactive_args` start with the agent binary again (`pi`, `claude`,
  `codex`). This is the same argv shape Pi used before the wrapper (commit
  `37bae96^`). The Claude and Codex credential checks already run their
  binaries through a plain `sbx exec`.

### 5. #25: one OpenRouter secret
- `README.md` "Set up the OpenRouter key": keep only
  `echo "$OPENROUTER_API_KEY" | sbx secret set openrouter`. Delete the
  `set-custom` block and the "twice" wording, and adjust the sentence about
  the `export` ("the two `sbx` commands").
- `src/md2okf/agents.py` `_pi_check_credentials`: drop the `set-custom` line
  from the remedy, and "two-step" from the docstring.
- `tests/test_agents.py:134`: assert that the remedy does **not** contain
  `set-custom`, and still contains `sbx secret set openrouter` and the rebuild
  hint.
- `kits/pi/README.md` LiteLLM `set-custom` is **kept**: a custom gateway is
  not a built-in service, so this is not a #25 workaround.

### 6. #685: validation needs a host sign-in for now
- `scripts/validate-spec.sh` header: replace "static … no Docker, no `sbx
  login`, no network" with a note that since sbx 0.47, `kit validate` needs
  the daemon and `sbx login` (docker/sbx-releases#685) until a stable
  `--offline` ships. The logic is unchanged.
- `.github/workflows/ci.yml` `validate-kit`: add `if: false`, with a short
  comment naming #685 and when to re-enable (a stable release with
  `kit validate --offline`, passed by `make validate`).
- `AGENTS.md` "Always validate…": `make validate` needs a host with
  `sbx login`. Inside a sandbox, use `sbx kit pack <kit> --output
  <scratch>.zip` as an offline schema stand-in and ask the user to run
  `make validate` on the host. Also update the "same check runs in CI"
  sentence.
- `CONTRIBUTING.md`:
  - The CI jobs paragraph: six active jobs; `validate-kit` is off until #685
    ships.
  - "Touch anything under `kits/`…": needs `sbx login`.
  - The sbx-minimum paragraph: still pin the checksum.

### 7. Tests for the new shape
- `tests/test-mount-state.sh`:
  - Delete the `md2okf-agent.sh` wrapper section and its `WRAPPER` variable.
  - Reduce `check_kit` to static assertions: exactly **one**
    `lib/md2okf/mount-state.sh` call in the spec, in the `startup:` block,
    relocating `"$HOME/<trace>" sessions` and run as `user: "agent"`; no
    `md2okf-agent` shim in the spec.
  - Drop the entrypoint execution, and the `binary` argument if nothing
    still uses it.
- `tests/test_kits.py`: `_SHARED_HELPERS` → `mount-state.sh` only; delete
  `test_every_kit_puts_the_wrapper_on_path`.
- `tests/test_agents.py`:
  - Delete `test_every_agent_process_starts_with_the_wrapper` and
    `test_every_registered_kit_ships_the_wrapper_shim`.
  - Drop `"md2okf-agent"` from the expected argvs (lines ~73, 77, 163, 177,
    246, 259).
- Drop the `md2okf-agent` prefix from:
  - `tests/test_cli.py` (lines ~105, 410, 606, 633, 651, 704)
  - `tests/test_compile.py:255`
  - the stub agents in `tests/test_protocol_claude.py:155` and
    `tests/test_protocol_codex.py:123`
- `tests/test-sandbox.sh`: delete the wrapper host check (lines ~68–79); keep
  the trace-probe check.
- `tests/test-sandbox-guest-common.sh`: delete the two `md2okf-agent` checks
  (lines ~133–137).

### 8. Docs
- `AGENTS.md`:
  - Repo-map paragraph about the wrapper (~L155–160): replace it with one
    sentence. Each kit's `setup.startup` step bind-mounts the agent's native
    trace directory onto state on every start, and the driver runs the agent
    binary directly with `sbx exec`. The agent's flags stay in `agents.py`.
  - Line ~152: test-mount-state.sh covers the bind helper only.
  - The `make test-shell` line.
- `CONTRIBUTING.md` ~L209–213: the same edit as the `AGENTS.md` repo-map
  paragraph.
- `kits/claude/README.md`, `kits/codex/README.md`: intro line (no wrapper),
  the command example without the `md2okf-agent` prefix, and "Transcripts"
  (only the startup step binds).
- `Makefile` `test-shell` comment: it already says "session bind helper",
  so check it and leave it as is.

### 9. CHANGELOG.md, under `[Unreleased]`
- **Changed:**
  - sbx 0.48.0 required (was 0.45.0).
  - `sbx run --detach`.
  - OpenRouter needs one secret (#25 fixed).
  - `make validate` needs `sbx login`, and CI kit validation is off until
    #685's `--offline` ships.
  - Expect one sandbox rebuild.
- **Removed:**
  - The entrypoint trace relocation in every kit (#420 fixed).
  - The `md2okf-agent` wrapper, its shims and `md2okf-agent.sh`. Agents now
    start directly.

No `VERSION` bump. Per `AGENTS.md`, I stage the changes and draft the commit
message, and you commit.

## Verification

In the sandbox:
- `make lint`, `make test-md2okf`, `make test-shell`, `make dist`.
- `sbx kit pack kits/<k> --output <scratchpad>/<k>.zip` for pi, claude and
  codex: an offline schema check of the edited specs.
- `rg -- '--detached|md2okf-agent|issues/25|WRAPPER'` over the tree. Only
  CHANGELOG history should match.

On the host (needs `sbx login`, which I can't do here):
1. `make validate`.
2. For each agent: `sbx rm --force md2okf-<agent> && make test-sandbox
   AGENT=<agent>`. For Pi, this also checks #25: the rebuilt sandbox has only
   the global `openrouter` secret, and the credential check must pass.
3. #420: `sbx daemon restart`, then `make test-sandbox AGENT=pi` again (it
   reuses the sandbox). The trace-probe check proves the bind came back with
   no entrypoint and no wrapper.
4. Smoke run: `uv run md2okf -o "$(mktemp -d)" tests/fixtures/smoke.md`.
