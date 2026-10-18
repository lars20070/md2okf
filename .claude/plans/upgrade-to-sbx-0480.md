# Upgrade sbx 0.45.0 → 0.48.0

## Context

md2okf requires sbx 0.45.0 (`SBX_VERSION`). We want to move to 0.48.0 and,
where an upstream issue is now fixed, delete its workaround outright. I
checked each issue's status upstream:

| Upstream | Status at 0.48.0 | Effect here |
| --- | --- | --- |
| 0.48 CLI refactor: `sbx run --detached` is rejected | breaking | rename to `--detach` |
| #420: startup steps not replayed after a daemon restart | fixed | **keep all three trace-bind call sites**; only fix their stale rationale (see §3) |
| #25: GitHub sandbox-scoped credentials | fixed in 0.38, before our 0.45 floor; not about OpenRouter | remove the second OpenRouter secret **only if** a live test without it passes (see §5) |
| #685: `sbx kit validate` needs a daemon and `sbx login` since 0.47 | `--offline` exists only in 0.49 release candidates; confirmed here that 0.48.0 fails with "not signed in to Docker" | keep `kit validate`, switch off CI's `validate-kit` job |
| #629 virtiofs cache, #553 `kit sign` on GHCR | fixed | not used in md2okf, nothing to do |

Already checked against 0.48.0, no change needed:
- `sbx ls -q` still prints names only.
- `sbx rm --force` and `sbx exec` keep their flags.
- `sbx secret set --oauth` is still "openai/global only", so the Claude remark stays true.
- No kit declares an agent-context directory, so `../CLAUDE.md` stays where it is.

The kit fingerprint (`workbench.fingerprint`) hashes the sbx version and the
kit tree, so every existing sandbox rebuilds on first use. That is expected.

### Why the trace binds stay (correction to the earlier decision)

The earlier choice, "startup step only", rested on a wrong premise: that the
entrypoint and `md2okf-agent` binds exist only to cover #420. Docker's kit-v2
documentation says otherwise. Startup commands "don't gate the agent's
entrypoint: the agent launches once startup commands have been dispatched,
regardless of `background`". Nothing documents them gating `sbx exec` either.

So the startup step can never be a synchronous guarantee. The two other call
sites are that guarantee:
- the entrypoint, for `sbx run` launches;
- `md2okf-agent`, for every process the driver starts with `sbx exec`.

Each one binds before `exec`-ing the agent and refuses to start the agent if
the bind fails. Replacing them with an equivalent mechanism would rebuild the
same thing somewhere else, so they stay unchanged. #420 being fixed only means
the startup step now also reaches sessions that start no agent, such as a
shell, after a daemon restart.

## Changes

### 1. Version floor
- `SBX_VERSION` → `0.48.0`.
- `.github/workflows/ci.yml` `validate-kit`: `expected_sha256` →
  `609a2e4b881ba9a7fd21543077e53d3b863a6b99eebee1f208e51a097ab56a05`
  (`DockerSandboxes-linux.tar.gz`, v0.48.0). With the pin current,
  re-enabling the job only means deleting `if: false`.
- `README.md` "Install sbx": `0.45.0` → `0.48.0`.

### 2. `--detached` → `--detach`
- `src/md2okf/sandbox.py:149` (`create`) and `src/md2okf/cli.py:158` (dry-run line).
- `tests/conftest.py:155` (the fake's dispatch), plus every
  `["sbx", "run", "--detached"]` and `sbx run --detached` string in
  `tests/test_cli.py`, `tests/test_sandbox.py` and `tests/test_workbench.py`.

### 3. Trace binds: fix the rationale, keep the mechanism
The code is unchanged: the entrypoints, the startup steps, `md2okf-agent.sh`,
the shims and `agents.WRAPPER` all stay. Only the comments that justify the
second call site with "starts where the hook is not replayed" (the #420
reasoning) change:
- `kits/{pi,claude,codex}/spec.yaml`, the comment above `startup:`.
  - The startup step does not gate the entrypoint or `sbx exec`. It covers
    sessions that launch no agent.
  - The entrypoint (for `sbx run`) and `md2okf-agent.sh` (for the driver's
    `sbx exec`) each bind synchronously and refuse to start the agent on
    failure.
  - The helper is idempotent.
- `tests/test-mount-state.sh` ~L220–222: the same correction in the
  `check_kit` header comment. The assertions stay.

### 4. #25 / OpenRouter: decide by a live test, not by the issue closure
The `set-custom` step dates from July 2026 (commit `3c994d7`). It cites #25,
which concerns GitHub credentials and was fixed in 0.38. Neither the closure
nor anything in the repository shows that the global `openrouter` secret alone
is enough. 0.48.0 also lets a sandbox-scoped custom secret override a global
one, so a leftover custom secret would hide the answer. The removal is
therefore gated on host verification step 2.

- **If step 2 passes** (no custom secret anywhere, real authenticated compile
  succeeds):
  - `README.md` "Set up the OpenRouter key": keep only
    `echo "$OPENROUTER_API_KEY" | sbx secret set openrouter`. Delete the
    `set-custom` block and the "twice" wording, and fix the sentence about
    `export` ("the two `sbx` commands").
  - `src/md2okf/agents.py` `_pi_check_credentials`: drop the `set-custom`
    line from the remedy, and "two-step" from the docstring.
  - `tests/test_agents.py:134`: assert that the remedy does **not** contain
    `set-custom`, and still contains `sbx secret set openrouter` and the
    rebuild hint.
- **If step 2 fails**, the workaround stays. Only the misleading citation
  changes: replace the #25 link in `README.md` with a plain statement that
  sbx 0.48.0 still needs the sandbox-scoped custom secret for OpenRouter. The
  remedy is unchanged.
- In both cases, the LiteLLM `set-custom` in `kits/pi/README.md` stays. A
  custom gateway is not a built-in service.

### 5. #685: validation needs a host sign-in for now
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

### 6. CHANGELOG.md, under `[Unreleased]`
- **Changed:**
  - sbx 0.48.0 required (was 0.45.0).
  - Sandboxes are created with `sbx run --detach`.
  - `make validate` needs `sbx login`, and CI kit validation is off until
    #685's `--offline` ships.
  - Expect one sandbox rebuild.
  - If §4 passes: OpenRouter needs one secret. Tell users with an existing
    setup to remove the old custom secret.

No `VERSION` bump. Per `AGENTS.md`, I stage the changes and draft the commit
message, and you commit.

## Verification

In the sandbox:
- `make lint`, `make test-md2okf`, `make test-shell`, `make dist`.
  - `test-shell` already runs each kit's real entrypoint, and the wrapper,
    against a failing bind, and asserts that the agent never starts.
  - Both gates call `mount-state.sh` synchronously before `exec`, so a slow
    bind delays the agent rather than racing it; a delay test would add
    nothing.
- `sbx kit pack kits/<k> --output <scratchpad>/<k>.zip` for pi, claude and
  codex: an offline schema check of the edited specs.
- `rg -- '--detached'` over the tree. Only CHANGELOG history should match.

On the host (needs `sbx login`, which I can't do here):
1. `make validate`.
2. **OpenRouter without the custom secret.** This gates §4.
   1. `sbx secret ls --sandbox md2okf-pi`, then remove any `openrouter.ai` /
      `OPENROUTER_API_KEY` custom entry, using the name or placeholder the
      listing shows (`sbx secret rm --placeholder <value>`).
   2. `sbx secret ls` (all scopes): check that no custom secret for
      `openrouter.ai` remains in any scope, and that the global `openrouter`
      secret is present.
   3. `sbx rm --force md2okf-pi`, then run `sbx secret ls` again to confirm
      that nothing came back.
   4. `make test-sandbox AGENT=pi`: the rebuild, the sentinel check, and the
      trace-probe check.
   5. `MD2OKF_AGENT=pi uv run md2okf -o "$(mktemp -d)" tests/fixtures/smoke.md`:
      a real, authenticated OpenRouter compile in that same configuration.
      The explicit `MD2OKF_AGENT=pi` matters: an exported `claude` or `codex`
      would let the compile succeed without ever reaching OpenRouter.

   If 4 or 5 fails, take the "fails" branch of §4 and restore the custom
   secret.
3. `sbx rm --force md2okf-<agent> && make test-sandbox AGENT=<agent>` for
   claude and codex.
4. `sbx daemon restart`, then `make test-sandbox AGENT=pi` (it reuses the
   sandbox). This confirms that #420's fix rebinds the trace directory for a
   plain `sbx exec` session after a restart. It is not evidence of gating:
   §3's tests cover that.
