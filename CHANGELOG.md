# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.3.2] - 2026-10-22

### Added

- **Pi can use GitHub's MCP server in `md2okf --agent`.** Pi has had a
  built-in MCP client since 0.99.0
  ([earendil-works/pi#10040](https://github.com/earendil-works/pi/pull/10040)).
  The kit now installs `github-mcp-server` `1.12.2` (pinned by SHA-256) and
  configures it in `~/.pi/agent/mcp.json`. Its tools are deferred: `tool_search`,
  switched on in `settings.json`, loads the ones a task needs.
  `autoEnableCodemode` is off, so MCP does not switch codemode on by itself.
  Compile turns get none of this: they run with `--no-mcp --tools -tool_search`,
  the counterpart of Claude's `--strict-mcp-config` and Codex's gateway
  override, so their tool set is the one they had on Pi 0.86.1.
- **The Pi kit declares an optional `github` credential.** `GH_TOKEN` is the
  proxy-managed sentinel, injected as a bearer token on `api.github.com` and as
  `x-access-token` basic auth on `github.com`. The entrypoint and the Pi kit's
  `md2okf-agent` shim export it as `GITHUB_TOKEN` and
  `GITHUB_PERSONAL_ACCESS_TOKEN` for `mcp.json`. Binding it is optional, and
  `api.github.com` joins the allowlist. See
  [GitHub MCP server](https://github.com/lars20070/md2okf/blob/master/kits/pi/README.md#github-mcp-server)
  in the Pi kit guide.
- `settings.json` and `models.json` declare Pi's published `$schema`, for editor
  completion and validation. Pi itself ignores it.
- `make test-sandbox AGENT=pi` checks the image's provenance (exactly one Pi,
  at the pinned version), the new config, and the token exports through
  `md2okf-agent`. With a GitHub secret bound, it also checks `gh`, the MCP
  server's connection and one authenticated, read-only `get_me` call.
  `REQUIRE_GITHUB=1` turns a missing secret from a skip into a failure.
- The Pi parser is now tested against a real Pi 1.4.0 `--mode json` stream
  (`tests/fixtures/protocols/pi/`), run with the compile's own flags against a
  scripted local model. It confirmed that md2okf's view is unchanged. 1.4.0
  adds a `role: "system"` message, which the parser drops, as it should.

### Changed

- **md2okf now requires sbx 0.49.2 (was 0.48.0).** `SBX_VERSION`, CI's pinned
  checksum and the README move together. sbx 0.49.2 is a security release that
  rebuilds its built-in template images with updated CA certificates, after a
  certificate authority compromise; it changes no kit-spec or CLI
  flags. The kit fingerprint hashes the sbx version, so every existing sandbox
  is rebuilt once, automatically, on its first use after the upgrade, and the
  rebuild is what picks up the new images.
- **`make validate` runs `sbx kit validate --offline`, and CI's `validate-kit`
  job is switched back on.** sbx 0.49.2 fixes
  [docker/sbx-releases#685](https://github.com/docker/sbx-releases/issues/685):
  `--offline` skips the daemon-backed kit policy, so validating a kit needs
  neither a running daemon nor an `sbx login`. `make validate` therefore works
  inside a sandbox and on a CI runner as well as on a signed-in host, and the
  job (deleted `if: false`) checks every `kits/*/spec.yaml` on each pull request
  against the schema of the exact sbx release in `SBX_VERSION`. Checked with
  sbx 0.49.2 against all three kits. This reverses the 0.3.1 entry that
  switched the job off.
- `make lint` skips a `tmp/` folder: markdownlint and cspell leave tracked
  Markdown under it alone, and cspell ignores `tmp/**`. For scratch notes and
  plans.
- **Pi `1.4.0`, up from `0.86.1`.** Pi now comes prebuilt in Docker's own Pi
  image, `docker.io/sbx/pi-image`
  ([`docker/sbx-kits-contrib`](https://github.com/docker/sbx-kits-contrib/tree/main/pi)),
  pinned by digest, instead of a kit-time `npm install -g`. Pi stopped shipping
  a lockfile in 1.0.1, so npm no longer pins Pi's dependencies: the image's
  install resolved them when Docker built it, and the digest freezes that. The
  digest also freezes the `shell-docker` template beneath it, which used to
  float, so template fixes now arrive only with a digest bump. `fd` comes from
  the image too, as both `fd` and `fdfind`. Pi's changelog shows no change to
  the `--mode json` events md2okf reads, or to the session format (still
  version 3). Since Pi
  1.0.0 the TUI in `md2okf --agent` runs fullscreen; set `tuiMode` to
  `"regular"` to keep the terminal's own scrollback. Everything else is in
  [Pi's changelog](https://github.com/earendil-works/pi/blob/v1.4.0/packages/coding-agent/CHANGELOG.md),
  0.87.0 to 1.4.0.
- The Context7 Pi package is `0.1.3`, up from `0.1.2`. Upstream only updated
  the examples in its tool descriptions.
- `read-pi-session-traces` reads Pi `1.4.0` traces. `inspect` now counts
  standalone `usage` entries, such as prompt-cache warming, under a new
  `auxiliary` source and in a new `usage.total`; before, that spend was
  silently left out. It counts a codemode script's inner tool calls under
  `nestedTools`, apart from direct calls. `show` lists system messages by
  section and tool names only, never their prompt text, and marks an entry
  that a later `context_edit` hides or replaces. Its examples point at
  md2okf's own session directory.
- The Pi kit README no longer warns off `deepseek/deepseek-v4-flash` for its
  4.1K output cap: Pi 1.4.0's catalogue lists 943.7K. It now says to check a
  model's limits with `pi --list-models` before switching.

### Security

- **A bound GitHub secret is usable by every process in the `md2okf-pi`
  sandbox, compile turns included.** The sbx proxy injects it into every
  request to `api.github.com` and `github.com`, and a compile turn has `bash`,
  so a source document that steers one could make authenticated GitHub requests
  with `curl`, `gh` or `git`, with the token's full scope. `--no-mcp` keeps the
  MCP tools out of a compile; it is not a credential boundary. Bind a
  fine-grained, read-only token scoped to the repositories you need, or none.
  `gh auth token | sbx secret set github` hands over the GitHub CLI's own
  credential with every scope it has.
- GitHub MCP results are not inspected or filtered. Treat them as untrusted
  input, like a source document.
- Trusting a project in `md2okf --agent` now also applies its `.pi/mcp.json`,
  which can add MCP servers (a stdio server is an arbitrary command), override
  the kit's, and switch `autoEnableCodemode` back on. Pi asks before it trusts
  a project, and compile turns run in JSON mode, which skips project config.
  The wiki is written by compile turns, so decline unless you put that file
  there yourself.

### Upgrading

- Upgrade sbx to 0.49.2 or newer first (`brew upgrade sbx`): md2okf refuses an
  older one. To rebuild a sandbox at once instead, run `md2okf --fresh` or
  `sbx rm --force md2okf-<agent>`.
- The next run rebuilds `md2okf-pi` on its own, because the kit changed.
- A `github` secret you already set globally, for another sbx kit, binds to
  `md2okf-pi` at that rebuild. Check with `sbx secret ls`, and read the
  Security entry above before keeping it.

## [0.3.1] - 2026-10-18

### Added

- **A `/read-pi-session-traces` skill for Claude Code** (`.claude/skills/`, a
  development tool that is not shipped in the wheel or sdist). It lists,
  searches and summarises Pi's JSON Lines session traces by streaming them,
  so a long trace is never loaded whole, and has its own offline test suite.

### Changed

- **md2okf now requires sbx 0.48.0 (was 0.45.0).** `SBX_VERSION`, CI's pinned
  checksum and the README move together. The kit fingerprint hashes the sbx
  version, so every existing sandbox is rebuilt once, automatically, on its
  first use after the upgrade.
- **Sandboxes are created with `sbx run --detach`.** sbx 0.48 renamed the flag
  and rejects the old `--detached`, so an older md2okf cannot create a sandbox
  on sbx 0.48. `--dry-run` prints the new spelling.
- **The OpenRouter key needs only one secret.** Until now the README and Pi's
  credential remedy also asked for a sandbox-scoped copy,
  `sbx secret set-custom --sandbox md2okf-pi --host openrouter.ai …`, and cited
  [docker/sbx-releases#25](https://github.com/docker/sbx-releases/issues/25) as
  the reason. That issue was about GitHub credentials, not OpenRouter, and sbx
  fixed it in 0.38.0. On sbx 0.48.0, the global `sbx secret set openrouter` alone
  is enough. This was checked live, with no custom secret in any scope: a
  freshly built `md2okf-pi` passed `make test-sandbox`, and a real compile of
  `tests/fixtures/smoke.md` went through OpenRouter. The README and the remedy
  now name only the global secret. See Upgrading to remove an old copy.
- **`make validate` needs an active `sbx login`, and CI no longer validates
  the kits.** Since sbx 0.47, `sbx kit validate` needs a running daemon and a
  Docker sign-in, even for a local directory
  ([docker/sbx-releases#685](https://github.com/docker/sbx-releases/issues/685)).
  Upstream has closed the issue, but its `--offline` flag exists only in a dev
  build and did not make it into 0.48.0. CI's `validate-kit` job is therefore
  switched off (`if: false`), with its checksum still pinned to `SBX_VERSION`.
  It comes back once a stable release ships `kit validate --offline`. Until
  then, run `make validate` on a signed-in host. Inside a sandbox,
  `sbx kit pack` is an offline stand-in.
- **The trace-bind call sites stay, although their upstream bug is fixed.**
  [docker/sbx-releases#420](https://github.com/docker/sbx-releases/issues/420),
  where `sbx daemon restart` stopped a kit's startup steps from running, was
  fixed upstream after our old 0.45.0 floor, so 0.48.0 has the fix. The kit's
  startup step therefore now also binds the
  agent's trace directory after a daemon restart, including for sessions that
  start no agent, such as `md2okf --shell`. The two other call sites still
  bind as before, and were never only a workaround for #420. The kit
  entrypoint binds synchronously for `sbx run`, and `md2okf-agent` does the
  same for compile turns and `md2okf --agent`. Docker documents that startup
  commands do not gate the entrypoint, and documents no ordering guarantee for
  `sbx exec` at all. So both guards remain, and an agent starts only after a
  successful bind: either guard refuses to start it when the bind fails. The
  driver's other `sbx exec` calls, such as the `merkleokf` hash and the
  credential check, start no agent and go through neither. Only the comments in
  each `kits/*/spec.yaml` and `tests/test-mount-state.sh` that justified them
  with #420 changed.
- The Context7 MCP server for host development tools (`.mcp.json`) moves from
  `@upstash/context7-mcp` 4.0.0 to 4.1.1. Pi's separate sandbox integration,
  `@upstash/context7-pi`, is unchanged.
- The README overview diagram pins Mermaid's `dagre` layout, so it keeps
  rendering as before. The diagram's caption is now spell-checked, because the
  `cspell:enable` marker moved up to directly after the diagram.

### Fixed

- **`uv run md2okf --version` no longer reports a stale version after
  `VERSION` changes.** uv rebuilds a project only when a cache key changes, and
  `VERSION` was not one, so a checkout kept its old build. `pyproject.toml` now
  lists `VERSION` beside itself in `[tool.uv] cache-keys`.

### Upgrading

- Upgrade sbx to 0.48.0 or newer first: md2okf refuses an older one, and the
  next run rebuilds each agent's sandbox on its own.
- If you set the OpenRouter key twice, remove the custom copy before that
  rebuild. Find its placeholder with `sbx secret ls --sandbox md2okf-pi`, run
  `sbx secret rm --sandbox md2okf-pi --placeholder <placeholder>`, and check
  that `sbx secret ls --sandbox md2okf-pi` no longer lists it. Then run
  `sbx rm --force md2okf-pi`. Name the sandbox both times: without
  `--sandbox`, `sbx secret rm --placeholder` searches only the global scope,
  and exits 0 even when it finds nothing there. A sandbox-scoped
  secret overrides the global one, so a stale copy would keep being used even
  after you rotate the global key. Keep the global `sbx secret set openrouter`.

## [0.3.0] - 2026-09-28

### Added

- **`MD2OKF_AGENT` selects the agent framework.** `pi` is the default (unset or
  empty means `pi`); anything unregistered is refused with
  exit 2 before any work starts. It is what runs Claude Code and Codex
  through the same compile pipeline as Pi: everything that
  differs between agents — command lines, first-turn prompt, credential check,
  event-stream parser — now belongs to the agent, not to the driver. `--dry-run`
  prints the resolved agent.
- **`md2okf-agent`, a wrapper every agent process now starts through.** Each
  compile turn and `md2okf --agent` session runs `md2okf-agent pi …` rather
  than `pi …`. `sbx exec` bypasses the kit's entrypoint, so the wrapper is what
  guarantees, per process, that the agent's traces are bind-mounted onto
  host-backed state before it starts — and it refuses to start the agent when
  they are not. The script is shared by every kit; each kit's shim names its
  own trace directory.
- **Credential remedies now end by rebuilding the sandbox**
  (`sbx rm --force md2okf-<agent>`): sbx injects a credential only when a
  sandbox is created, so fixing the secret alone left the old sandbox unready.
- **`MD2OKF_AGENT=claude`: Claude Code**, through its own kit (`kits/claude/`,
  on sbx's built-in `claude` parent) and sandbox (`md2okf-claude`). It logs in
  with the host's `anthropic` secret — a `/login` inside a Claude sandbox
  (`sbx run claude`) for a subscription, or `sbx secret set anthropic` for an
  API key — and needs sbx 0.45.0. Compile turns run
  `claude -p --output-format stream-json` with no MCP servers
  (`--strict-mcp-config`), and a `result` event reporting `is_error` fails the
  turn. Verified live: the sandbox checks pass, and a compile of
  `tests/fixtures/smoke.md` converges and passes the gate. See
  `kits/claude/README.md`.
- **`MD2OKF_AGENT=codex`: Codex**, through its own kit (`kits/codex/`, on sbx's
  built-in `codex` parent) and sandbox (`md2okf-codex`). It logs in with the
  host's `openai` secret — `sbx secret set openai --oauth` for a ChatGPT
  subscription, or an API key — and needs sbx 0.45.0. The OKF contract ships
  as Codex's global `~/.codex/AGENTS.md`, because Codex does not read
  instructions from outside a git project. Compile turns run
  `codex exec --json` with the parent's MCP gateway switched off, and
  `turn.failed` fails the turn. Verified live: a compile of
  `tests/fixtures/smoke.md` converges and passes the gate. See
  `kits/codex/README.md`.
- **`tests/fixtures/smoke.md`**, a short document for cheap live smoke runs:
  `uv run md2okf -o "$(mktemp -d)" tests/fixtures/smoke.md`.
- **`.env.example`** with the three variables `md2okf --help` lists. Nothing
  loads it automatically; export it with `set -a; . ./.env; set +a`.

### Changed

- **Pi now requires sbx 0.45.0 (was 0.43.0).** Every agent shares one floor,
  `SBX_VERSION`, which is also the exact release CI validates the kits with.
  The old 0.43.0 floor was never exercised by CI.
- **One sandbox and one workbench per agent.** The sandbox is now called
  `md2okf-pi` rather than `md2okf`, and the workbench moved from
  `$XDG_STATE_HOME/md2okf/` to `$XDG_STATE_HOME/md2okf/pi/`, so agents can
  coexist side by side. They still never compile at the same time: one lock
  serialises every run.
- **The kit moved from `kits/md2okf/` to `kits/pi/`** (and inside the wheel from
  `md2okf/kit/` to `md2okf/kits/pi/`); its `name:` is now `pi`.
- **The credential check also runs when a sandbox is reused**, not only when
  one is created. Before, a sandbox whose key stopped being proxy-managed was
  reused silently. `md2okf --shell` now opens even when the check fails, with
  the remedy printed as a warning; a compile and `--agent` still refuse.
- **A failure the agent reports in its own event stream fails the turn** even
  when the process exits 0, and is named in the error. Claude Code's and Codex's
  parsers report such failures; Pi's reports none, so Pi runs behave as before.
- **A failed turn's message keeps lines that were cut short.** The diagnostic
  tail used to drop every line starting with `{`, including a truncated JSON
  line that may be the only clue. Now only whole JSON objects — the agent's own
  protocol events — and lines the agent's parser knows to be noise (Codex's
  stdin notice) are left out.
- **`make test-sandbox` checks every registered agent**, or one with
  `AGENT=pi`; `tests/test-sandbox.sh` now requires the agent as its argument,
  and the guest checks live in `tests/test-sandbox-guest-pi.sh`. It now also
  checks from the host that a trace written through the agent's native path
  reached the workbench's `sessions/`, and runs the wrapper through a plain
  `sbx exec`, exactly as the driver does.
- **`make validate` checks every `kits/*/spec.yaml`**, not just Pi's, so a kit
  being authored is validated before it is ever registered.
- **`tests/test_kit.py` is now `tests/test_kits.py`** and runs over every kit:
  the shared OKF authoring contract, the kit's own `generated.by` producer, no
  other agent's config paths, every file the instructions name, and helpers
  that are byte-identical across kits.
- **The README is shorter; its reference material moved to `docs/`.** The
  README keeps a Quickstart (including how to switch agents), installing sbx
  and setting up the OpenRouter key, and links the rest from a "Further
  documentation" table. `docs/usage.md` covers what you can compile, reading
  the output, the wiki's layout, and every CLI flag and exit code;
  `docs/configuration.md` choosing an agent, credentials for Claude Code and
  Codex, and models and providers; `docs/architecture.md` the run loop, the
  sandbox's mounts, credentials, session state and the repository layout.
- **`md2okf --help` names all three agents** and how each signs in, explains
  every option in plain words, and lists the exit codes.
- **`web2md/` and `pdf2md/` moved to `extras/`.** Both are optional,
  clone-only helpers that prepare Markdown for `md/`, and neither is part of a
  compile. `make scrape` and `make test-web2md` work as before; run the
  scraper and marker by hand with `--project extras/web2md` or
  `--project extras/pdf2md`. The scraper's cache moved to
  `extras/web2md/cache/`; git does not move an ignored cache, so keep an
  existing one with `mv web2md/cache extras/web2md/cache`, or `make scrape`
  fetches the whole site again.

### Fixed

- **Editing the kit's agent config now rebuilds the sandbox.** The kit
  fingerprint skipped every path containing a dot-directory, which left only
  `README.md` and `spec.yaml` in the hash: edits to `AGENTS.md`, the skills,
  `settings.json` or `mount-state.sh` never triggered a rebuild, and a stale
  sandbox was reused. Only host clutter (`.DS_Store`, `._*` AppleDouble files,
  `__pycache__`) is skipped now. Expect one rebuild on upgrade.
- **The sdist no longer strips a kit's `.claude` directory.** The exclusion
  meant for the repository's own tool directories (`.claude`, `.cursor`) was
  unanchored, so it matched at any depth. It is now anchored to the root.

### Removed

- **`--spec` and `SPEC_MD`.** `md2okf`, every sandbox and the gate now always
  use md2okf's own `SPEC.md`. The kits' instructions, the frontmatter guard and
  the pinned okfctl all target OKF v0.2, so another spec could only say the same
  thing or contradict them. The workbench's `SPEC.md` is rewritten with the
  bundled spec before every run and session, replacing anything a `--spec` run
  left there. The frontmatter guard no longer reads a spec found beside the
  wiki it checks, nor any other file of that name: on the host it uses the one
  beside md2okf's `kits/` directory (the repository's, or the packaged copy), in
  the sandbox the read-only mount beside the workspace, and a missing spec is an
  error. A copied wiki is therefore checked in place, against the same spec.
  Drop `--spec` from any script that passed it; it is now an unknown option.

### Upgrading

The old `md2okf` sandbox and workbench are not reused. Remove the sandbox with
`sbx rm --force md2okf`. In `$XDG_STATE_HOME/md2okf/` (by default
`~/.local/state/md2okf/`), everything except the new `pi/` folder is left over
and can be deleted: `work/`, `sandbox-fingerprint`, `sandbox-identity`, and
`sessions/` — which holds your old Pi transcripts, so move it to
`pi/sessions/` first if you want to keep them. If you set the OpenRouter key
with `sbx secret set-custom --sandbox md2okf …`, run it again with
`--sandbox md2okf-pi`.

## [0.2.1] - 2026-09-21

### Added

- **`md2okf --shell` and `md2okf --agent`, which open the sandbox.** Both build
  or refresh it first when none exists or the running one no longer matches
  `kits/md2okf/`, so the prerequisite behind the bare
  `sbx exec -it md2okf -- bash` — knowing to run `python -m md2okf.sandbox`
  first, and that a stale sandbox is entered silently — is gone. The terminal
  is handed over with `execvp` rather than a child process, so the TTY, job
  control, Ctrl-C and the exit code are the guest's own. These are for
  inspecting the sandbox, not authoring in it: they do not restage a compile
  run. Helper CLIs are refreshed, an empty spec mount gets the bundled spec, and
  prior workbench content otherwise remains. The next compile replaces
  `work/okf`; Pi transcripts persist. The workbench lock stays held until the
  interactive session exits, so a concurrent compile or `--fresh` invocation
  is refused. Only `--fresh` combines with them; every other compile option is
  refused rather than ignored. The flag is `--agent` rather than `--pi` so that
  changing the agent framework later would not change a published interface.

### Changed

- **The default model is now `deepseek/deepseek-v4-pro`**, in place of
  `qwen/qwen3.6-35b-a3b`. Every compile runs on it unless `settings.json` says
  otherwise, so the cost and the quality of a run both move with this. The
  routing pin it needs was already in `models.json` — DeepInfra only, no
  fallbacks — and, being a model Pi's catalogue knows, it keeps the catalogue's
  1M context and 384K output rather than the 16,384-token default that truncates
  a long `write` mid-argument.
- **One version for the whole repository.** `VERSION` now governs every project
  in the tree, not just the driver: the four host CLIs (`inspectmd`,
  `inspectokf`, `sizeokf`, `merkleokf`), `web2md` and `pdf2md` all move from
  their standalone `0.1.0` to the repo version. `./scripts/sync-versions.sh`
  writes the literal into each `pyproject.toml` and refreshes each `uv.lock`,
  and `make lint` runs its `--check` form, so a release cannot ship a CLI whose
  `--version` disagrees with the tag. The version stays a literal rather than a
  dynamic read of `../../VERSION` because the CLIs are also built from a staged
  copy holding only `pyproject.toml` and `src/`, where no path above the project
  root exists.
- Bump the pinned Pi coding agent from 0.85.1 to 0.86.1, and pin `cacheWarming`
  to `"streaming"` alongside it. 0.86 adds cost-aware prompt-cache warming and
  defaults it on, so the kit states its position rather than inheriting one
  that can move again on the next bump. Nothing else in the release reaches
  this project: the `--mode json` wire format is unchanged, and all three of
  0.86.0's breaking changes are extension- or SDK-level.
- The `inspect-md` skill now states what its section ranges actually cover: a
  span ends at the next heading of **any** level, so a parent section does not
  contain its children and each has to be read by its own index. It also records
  that `-L` filters the map without renumbering `Index`, and that frontmatter
  and headings inside fenced code are left out.
- `tree` is documented as a host requirement for `inspectokf`, and
  `make install-clis` now warns when it is missing rather than leaving the
  binary to report it at first use. Only the host is affected: the sandbox
  installs its own copy, so a compile never needed one.
- Linux gets its own uv environments. A venv is not portable across platforms
  and a direct-mode sandbox shares the tree with the macOS host, so `make`
  exports `UV_PROJECT_ENVIRONMENT=.venv-linux` on Linux and the default `.venv/`
  stays macOS-only. The value is relative on purpose: each of the seven uv
  projects then gets its own, where an absolute path would collapse them into
  one shared environment.
- The README overview diagram names the agent's skills by their skill ids
  (`inspect-md`, `inspect-okf`, `size-okf`, `merkle-okf`, `curate-okf`) rather
  than by the binaries behind four of them, which is the distinction every one
  of those skills makes in its own first paragraph. `curate-okf` joins the
  diagram, and the session-state node names the `sessions` directory the driver
  actually mounts.

### Fixed

- **`--shell` and `--agent` no longer mount an empty `SPEC.md`.** `ensure_roots`
  can only create the spec mount empty — sbx cannot mount a path that does not
  exist — and only a compile's `restage` filled it, so an interactive session on
  a workbench that had never compiled handed the agent a 0-byte `../SPEC.md`.
  That is the one file outranking every instruction it has, and an agent reading
  it empty wrote a wiki declaring `okf_version: ""`, which `okfctl index build`
  then dropped, leaving the frontmatter guard and the index check looking as
  though they contradicted each other. `stage_tooling` now floors the mount with
  the bundled spec, filling it only when empty, so a compile's `--spec` still
  governs the session that follows it.
- Stale documentation left over from 0.2.0. `AGENTS.md` described the release
  workflow as creating a notes-only GitHub Release, from before it built,
  published to PyPI and attached the artifacts; `CONTRIBUTING.md` described
  `make lint` as checking `VERSION` against `CHANGELOG.md` alone, from before it
  also checked every subproject; and the `pdf2md` and `web2md` guides still sent
  their output to `make wiki`, a target `md2okf` replaced. `CONTRIBUTING.md`
  also documents the per-platform venv rule that until now only `AGENTS.md`
  carried, so a contributor on Linux is told before `uv` writes the wrong one.

### Removed

- **`scripts/sync-descriptions.py`.** It rewrote each `index.md` entry's
  description from the linked page's frontmatter, from before `okfctl` owned
  the indexes. `okfctl index build` now regenerates them inside the sandbox, so
  the script was a second implementation of a job already done — and an unwired
  one: nothing in `make`, the kit or any skill invoked it.

## [0.2.0] - 2026-09-20

### Added

- **`md2okf`, one command in place of `make wiki` and three launcher scripts.**
  Files or folders in, a directory out: `md2okf [-o DIR] [--spec FILE] [-n N]
  [--fresh] [--dry-run] [-q|-v] [FILE|DIR ...]`. stdout carries one TSV row per
  document (`path  iterations  hash-before  hash-after`) and nothing else,
  diagnostics go to stderr, and the exit status is the verdict: 0 every
  document converged (a hash-stable first pass included — that is the
  idempotent re-run), 1 the run failed, 2 usage or environment, decided before
  any work starts. The driver is stdlib-only Python with a pytest suite that
  fakes the one `sbx` seam, so the Ralph loop, the prompts and the event
  rendering are testable without a paid sandbox run.
- **A workbench, so one sandbox serves any input and output.** sbx fixes a
  sandbox's mounts at creation, so runs are staged through
  `$XDG_STATE_HOME/md2okf/work` instead: inputs copied in, the target wiki
  mirrored in before the run and back out after every iteration, the five mount
  paths never changing. The sandbox is rebuilt only when the kit it was built
  from changes, when the recorded configuration no longer matches, or on
  `--fresh` — and one that cannot be proven to belong to the driver is reported,
  never deleted.
- **Publication to PyPI.** `md2okf` is now installable with
  `uv tool install md2okf` (or runnable with `uvx md2okf`), with the sandbox
  kit, `SPEC.md` and the four helper CLI projects carried inside the wheel, so
  it compiles without a checkout. A `vX.Y.Z` tag builds the wheel and sdist
  once, publishes them by trusted publishing — OIDC, no stored token — and then
  creates the GitHub Release with those same artifacts attached.
- `NOTICE-OKF-SPEC.md` and `LICENSE-OKF-SPEC.txt`, recording that the bundled
  `SPEC.md` is the Open Knowledge Format v0.2 specification, taken verbatim from
  `GoogleCloudPlatform/open-knowledge-format` and licensed Apache-2.0. Both ship
  in the wheel and the sdist beside md2okf's own MIT licence. Package metadata
  gains the README as its long description, an SPDX licence expression, project
  URLs and classifiers, and the sdist no longer carries the agent-tool
  directories and their vendored third-party skills.
- `make install` (the command onto PATH), `make test-md2okf` (the driver suite,
  also in `make test`) and `make dist` (wheel and sdist, plus a smoke test of
  the built artifact from outside the checkout). CI gains `test-md2okf` and
  `build-package` jobs.
- `okfctl` (pinned 0.4.0, checksummed release archive) to the sandbox toolchain,
  and a `curate-okf` skill covering it. It replaces `okf-lint` as the wiki's
  gate and takes ownership of the reserved `index.md` files: the agent runs
  `okfctl index build` instead of writing link lists by hand, and the gate's
  `okfctl index check` fails closed on a stale or hand-edited index.
- `compile-okf/scripts/check-okf.sh`, one gate with two call sites — the agent
  runs it before finishing, `make check-okf` runs the same file on the host. It
  combines `okfctl validate`, a new dependency-free `frontmatter-guard.py`,
  `okfctl lint`, `okfctl analyze` for links that resolve to nothing, and
  `okfctl index check`. Lint defects (`broken-link`, `orphan`, `type-hygiene`,
  `status-lifecycle`, `spec-version`) block; `missing-xref` and `coverage-gap`
  are printed as advice, since they are judgment calls and the gate runs
  unattended inside the compile loop.

### Changed

- Host requirements are now `sbx` and `uv`; `make` and `jq` are developer tools
  rather than user ones. The Quickstart is `uv tool install .` then
  `md2okf my-document.md`.
- The writable state mount narrows from the state root to
  `$XDG_STATE_HOME/md2okf/sessions`, so the host-side ownership marker and the
  staged read-only inputs are outside the sandbox's namespace. The environment
  variable the guest helper reads is renamed `MD2OKF_STATE_DIR`, and the
  per-user lock moves to `/tmp/md2okf-<uid>.lock`, outside the configurable
  state directory.
- `merkleokf --nolog` now skips the root `log.md` whatever the wiki directory is
  called, instead of only when it is named `okf` — the hash call is what decides
  convergence, and `-o` can name any directory.
- Migrate the wiki to **OKF v0.2**, following `SPEC.md`: every page's legacy
  `timestamp` becomes `generated: { by, at }` (§5.2) with the actor recorded as
  `pi/<model-id>` (§7), and the bundle-root `index.md` marker moves to `"0.2"`.
  Index links are now relative, which is what `okfctl index build` writes;
  cross-links in page prose stay bundle-absolute.

- Persist Pi's native `~/.pi/agent/sessions` tree in
  `$XDG_STATE_HOME/md2okf/sessions`, bind-mounted from host state instead of a
  repository-local `logs/sessions/`. An exported `XDG_STATE_HOME` takes
  precedence over the gitignored `.env`, with `~/.local/state` as the fallback;
  changing it requires rebuilding the sandbox. Existing legacy transcripts are
  not migrated.
- Mount only what the agent needs into the sandbox, instead of the whole
  repository read-write: `okf/` and the external session-state directory
  read-write, and `md/`, `scripts/` and `SPEC.md` read-only. Nothing else in the
  repository is visible inside the microVM, so the agent's restriction to
  `okf/` is now enforced by the filesystem rather than by instructions alone.
  The mount list lives in `scripts/lib/sandbox-mounts.sh`, shared by every
  script that creates the sandbox.
- `okf/` is the primary mount and therefore the working directory inside the
  VM, so the agent's config and the `compile-okf` lint wrapper now address the
  read-only mounts as `../md/`, `../scripts/` and `../SPEC.md`.
- Move the Docker Sandbox kit from `pi/` to `kits/md2okf/`. Scripts, tests, and
  docs now point at `./kits/md2okf/`.
- Bump the documented minimum `sbx` version from 0.42.0 to 0.43.0.

### Fixed

- Ensure the `compile-okf` check script is executable after kit setup (`chmod`
  in `kits/md2okf/spec.yaml`), so `make test-sandbox` passes when the static
  `files/home/` copy drops the exec bit.

### Removed

- The shell compile path: `scripts/compile-okf.sh`, `scripts/bash.sh`,
  `scripts/pi.sh`, `scripts/lib/sandbox-mounts.sh` and the `make wiki` target.
  `md2okf` replaces the first, `sbx exec -it md2okf -- bash` (or `-- pi`) the
  next two, and `src/md2okf/workbench.py` the mount list. `jq` and `make` leave
  the user-facing requirements with them.
- `.env` and `.env.example`. A tool that is not tied to a checkout has no
  repository to read a `.env` from, so an exported absolute `XDG_STATE_HOME` is
  the one knob, with `~/.local/state` as the default.
- `tests/test-sandbox-mounts.sh`, whose subject moved into the driver: the
  state-path and mount-list cases are `tests/test_workbench.py`, and its check
  that the agent's runtime instructions never call the wiki `../okf` is
  `tests/test_kit.py`.
- `okf-lint` (`@thisismydesign/okf-lint`) and its `okf/.okflintrc.json` rule
  file, superseded by `okfctl` and the frontmatter guard. The guard re-implements
  the rules okfctl's spec floor deliberately leaves open — title, description,
  tags, provenance, the `okf_version` marker and the log's date headings — and
  adds a format check on provenance timestamps. `prefer-absolute-links` retires
  with it, for index files only.

## [0.1.0] - 2026-09-07

### Added

- `VERSION` and `CHANGELOG.md`, with `make lint` failing when they disagree.
- Notes-only GitHub Releases: pushing a `vX.Y.Z` tag runs
  `.github/workflows/release.yml`, which creates a Release whose body is the
  matching `CHANGELOG.md` section (`scripts/check-release-tag.sh`,
  `scripts/release-notes.sh`). Documented in `CONTRIBUTING.md`.
- `/skill-creator` and `/readme` skills for Claude Code and Cursor.

### Changed

- Bump the pinned Pi coding agent from 0.84.2 to 0.85.1.
- Bump the documented minimum `sbx` version from 0.38.0 to 0.42.0.
- `scripts/bash.sh`, `scripts/pi.sh`, `scripts/compile-okf.sh` and
  `tests/test-sandbox.sh` now invoke `sbx run` with the kit path as the
  positional operand (`sbx run --name "${kit_name}" ./pi/`) instead of the
  deprecated `--kit <ref> <name>` form, which `sbx` v0.42.0 warns about on
  every invocation.
- Simplify the README Mermaid overview diagram (layout and helper-tool
  colours).

### Fixed

- README quickstart warning now names this project (`md2okf`) when saying a
  later `sbx` may break it.
- Cursor `/skill-creator` now points at `.cursor/skills/` (paths and validate
  command), not `.claude/skills/`.
- `/skill-creator` `quick_validate.py`: require a full-line closing `---` for
  frontmatter (not a `---` prefix), and validate `compatibility` when the key
  is present rather than only when it is truthy.
