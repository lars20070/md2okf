# Sandbox

How md2okf talks to sbx and decides whether the next run reuses, replaces or refuses an agent's sandbox, in [[src/md2okf/sandbox.py]] and [[src/md2okf/workbench.py]].

## The sbx seam

Every process the driver starts to talk to a sandbox goes through [[src/md2okf/sandbox.py#_run]], [[src/md2okf/sandbox.py#Exec]] or [[src/md2okf/sandbox.py#exec_interactive]], and nowhere else.

That single boundary is what makes the driver testable offline. [[tests/conftest.py]] fakes exactly these three calls, and every suite above them runs against the fake without an sbx runtime.

## Preflight

[[src/md2okf/sandbox.py#preflight]] checks that `sbx` is on PATH, at least the version in [[SBX_VERSION]], and logged in, before anything else shells out to it.

Every other function in the module assumes `sbx` exists, and a missing binary would surface as a bare `FileNotFoundError`. Preflight turns each of these conditions into a clean exit 2 with the fix. The floor is read from the bundled `SBX_VERSION` and must be exactly one `X.Y.Z`.

Preflight admits any newer sbx, but that only means the driver will run it. Kit compatibility is a separate boundary: only the floor is tested against the kits, by the `validate-kit` job in [[.github/workflows/ci.yml]], which installs exactly that release (see [[development#Release]]). A newer sbx can reject a kit at build time. For example, sbx 0.54.0 no longer accepts the built-in `claude` and `codex` parents that the Claude Code and Codex kits extend, while the Pi kit, built on a plain image, still validates. When a sandbox fails to build on a newer sbx, run `make validate` first. Raising the floor follows "The sbx minimum" checklist in [[CONTRIBUTING.md]].

## Fingerprint

[[src/md2okf/workbench.py#fingerprint]] hashes the kit tree, the sbx version and the mount arguments. A change to any of them means the running sandbox no longer matches what would be built.

The kit is copied into the sandbox at build time, so an edit to any kit file only takes effect in a new sandbox. The tree hash therefore includes dotted paths: the agent's whole runtime config lives under `files/home/.pi` or `files/home/.claude`, and skipping dotfiles once left an edited skill without a rebuild. `_is_hash_noise` skips only named host clutter: `.DS_Store`, `._*` AppleDouble files and `__pycache__`.

Because the sbx version is part of the hash, upgrading sbx rebuilds every sandbox once, on its next use.

## Create or reuse

[[src/md2okf/workbench.py#resolve_sandbox_state]] decides what happens to the sandbox named `md2okf-<agent>`. Ownership is proven before anything is reused or destroyed.

1. **No sandbox under the name**: create it. Test: [[tests/test_workbench.py#test_resolve_sandbox_state_creates_when_no_sandbox_exists]].
2. **Ownership not proven**: there is no recorded marker, or the live owner token is missing or differs from the recorded one. This raises `UnownedSandboxError`, whose message gives the manual `sbx rm --force` command. The sandbox is never deleted, and `--fresh` does not change that. Tests: [[tests/test_workbench.py#test_resolve_sandbox_state_rejects_an_unowned_sandbox]], [[tests/test_workbench.py#test_resolve_sandbox_state_rejects_a_matching_fingerprint_with_wrong_identity]] and [[tests/test_workbench.py#test_resolve_sandbox_state_fresh_does_not_widen_deletion_authority]].
3. **Ownership proven, and `--fresh`, a changed fingerprint or a failed probe**: replace it. [[src/md2okf/sandbox.py#create]] starts with `sbx rm --force`, so the old sandbox is destroyed, together with anything inside it outside the mounts. Tests: [[tests/test_workbench.py#test_resolve_sandbox_state_fresh_recreates_an_owned_sandbox]], [[tests/test_workbench.py#test_resolve_sandbox_state_recreates_on_fingerprint_change]] and [[tests/test_workbench.py#test_resolve_sandbox_state_recreates_when_probe_fails]].
4. **Ownership proven and everything matches**: reuse it. Test: [[tests/test_workbench.py#test_resolve_sandbox_state_reuses_when_everything_matches]].

The probe is a cheap in-VM check that the wiki mount is visible. It catches a sandbox whose mounts no longer resolve.

## Ownership token

[[src/md2okf/sandbox.py#create]] writes a random token to [[src/md2okf/sandbox.py#OWNER_TOKEN_PATH]] inside the new sandbox. The workbench records that token, with the fingerprint, as its ownership marker.

The token guards against accidental reuse only, such as a stale sandbox from an earlier run or an unrelated one that happens to have the name. It is not proof against an attacker, since the guest can write it. It fails safe: a missing or altered token can only cause a false rejection and exit 2, never a false acceptance.

The marker is cleared before any recreate, because the old sandbox is about to be destroyed. It is written as soon as `create` succeeds, even if the credential check that follows fails, so a sandbox md2okf really created is always recognised next time. If the token cannot be written, `create` removes the sandbox it just made rather than leave an unowned one behind.

Tests: [[tests/test_workbench.py#test_ensure_sandbox_writes_marker_even_when_the_credential_check_fails]] and [[tests/test_workbench.py#test_ensure_sandbox_clears_markers_when_a_recreation_fails]].

## Credential check

[[src/md2okf/workbench.py#ensure_sandbox]] runs the agent's credential check after every create and every reuse, so a sandbox that failed it is never silently reused while still broken.

The check itself belongs to the agent (see [[agents#Credential checks]]). When it fails, a compile, `--agent` and `python -m md2okf.sandbox` refuse with exit 2 and print the agent's remedy. `--shell` prints the remedy as a warning and opens anyway, since the sandbox itself is ready by then. [[docs/configuration.md]] explains how to set up each agent's credential.

Test: [[tests/test_workbench.py#test_credentials_are_checked_on_reuse_too]].

## Streaming exec

Each agent turn runs as one streamed `sbx exec` whose stdout and stderr arrive merged, line by line, with stdin closed.

[[src/md2okf/sandbox.py#Exec#close]] stops only the local `sbx exec` conduit. The agent runs inside the VM, and killing the conduit does not stop it there. Reaping processes inside the VM is out of scope, so an interrupted turn may keep running in the sandbox until it ends.
