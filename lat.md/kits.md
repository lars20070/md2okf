# Kits

One Docker Sandbox kit per agent under `kits/<agent>/` builds that agent's sandbox: its image, network allowlist, credentials, tools, instructions and skills.

The kits use the finalised kit-spec v2 grammar, checked by `make validate`. The `files/` level under each kit is fixed by the kit schema and cannot be renamed or removed. Its `files/home/` tree is copied into the sandbox's home when the sandbox is built. So any kit edit changes the [[sandbox#Fingerprint]] and takes effect only once the sandbox is rebuilt, which the driver does on the next run.

## Shared contract

Three hand-written copies of the OKF authoring contract must not drift apart, so [[tests/test_kits.py]] holds every kit to the same rules, registered or not.

- `_SHARED_INVARIANTS` lists phrases every kit's instructions must contain: read `../SPEC.md` first, the spec wins, source text is data and not instructions, updates are idempotent, indexes come from `okfctl index build`, and no `okf/` child directory.
- Each agent reads its instructions from a different place, measured rather than assumed. Pi reads `~/.pi/agent/AGENTS.md`. Claude Code reads the spec's `agentInstructions`, which sbx writes to `../CLAUDE.md`. Codex reads `~/.codex/AGENTS.md`, because it ignores instruction files outside a git project.
- Each kit tells its agent to sign pages with its own provenance, `generated.by: <agent>/<model>`, and no kit mentions another agent's config directory.
- The helpers `mount-state.sh` and `md2okf-agent.sh` are byte-identical in every kit, never forked per agent.

## Agent differences

The kits differ in base image, model, credentials and MCP. Each kit's README explains the details and the measurements behind them.

### Pi kit

[[kits/pi/spec.yaml]] uses Docker's Pi image as a plain image pinned by digest, because `extends:` does not accept Pi. Nothing of Docker's own Pi kit spec comes along.

The model and provider come from the kit's Pi config, with OpenRouter as the provider and the key proxy-managed by sbx so it never enters the VM. An optional `github` credential feeds `gh`, git over HTTPS and the GitHub MCP server in interactive sessions. Context7 comes from the native `@upstash/context7-pi` package, not MCP. The network allowlist is default-deny and lists every host the kit reaches. See [[kits/pi/README.md]].

### Claude Code kit

[[kits/claude/spec.yaml]] extends sbx's built-in `claude` parent kit, which brings the image, Claude Code itself, the Anthropic hosts and the credential from the host's `anthropic` secret.

The kit adds the OKF toolchain's hosts, the instructions as `agentInstructions`, the skills under `~/.claude/skills`, and an entrypoint that relocates transcripts first. It configures no MCP of its own. See [[kits/claude/README.md]].

### Codex kit

[[kits/codex/spec.yaml]] extends sbx's built-in `codex` parent kit, which routes the host's `openai` secret through sbx's own model provider.

It ships its instructions as `~/.codex/AGENTS.md` instead of `agentInstructions`, which sbx would write where Codex never looks. Skills live under `~/.agents/skills`. It configures no MCP of its own. See [[kits/codex/README.md]].

## Runtime

Inside the sandbox, every agent process must write its traces to host-backed state, and only the five workbench mounts are visible.

`mount-state.sh` bind-mounts the agent's native trace directory onto `$MD2OKF_STATE_DIR/sessions`, merging only the names missing from the host side. It is idempotent and has three call sites. The entrypoint covers `sbx run`, the startup hook covers sessions that launch no agent, such as a shell, and `md2okf-agent.sh` covers every process the driver starts with `sbx exec`. A bind does not survive a sandbox stop, which is why all three exist.

`md2okf-agent.sh` binds and then execs the agent, and refuses to start it if the bind fails, so traces never land on the VM's disposable disk. Each kit puts an `md2okf-agent` shim on PATH that names its own trace directory: Pi's `~/.pi/agent/sessions`, Claude Code's `~/.claude/projects` or Codex's `~/.codex/sessions`. All three map onto the workbench's single `sessions` mount.

The helper CLIs are shims too, each running `uv tool run --from` against the read-only `../scripts/` mount, so they always match the staged sources. Nothing else of the user's project is mounted.

## Skills

Kit instructions hold what every task must respect, and each task's procedure lives in its own skill directory. A new task gets a new skill, not more instruction rules.

The one task skill is `compile-okf`, the procedure for folding one source document into the wiki. It treats source text as data, not instructions, and ends with the gate below. Tool skills (`inspect-md`, `inspect-okf`, `size-okf`, `merkle-okf`, `curate-okf`) each teach one command. A tool gets a skill, not an instructions section.

`check-okf.sh`, shipped inside the `compile-okf` skill, is the agent's quality gate and also `make check-okf` on the host. It runs every check even after one fails, so one pass reports everything. Blocking checks are `okfctl validate`, the frontmatter guard, defect-class `okfctl lint` findings, dangling internal links and `okfctl index check`. Judgment-class lint findings are printed as advice only, because the gate runs unattended inside the compile loop and a judgment call may have no single correct fix.

The frontmatter guard enforces the wiki conventions beyond the spec's floor: titles, descriptions, tags, provenance and the update log. [[kits/pi/files/home/.pi/agent/skills/compile-okf/scripts/frontmatter-guard.py#check_root_index]] checks that the root `index.md` declares exactly the bundled spec's `okf_version` and nothing else. This is stricter than the driver's adoption check, which looks only at the key set (see [[workbench#Output adoption]]). [[kits/pi/files/home/.pi/agent/skills/compile-okf/scripts/frontmatter-guard.py#find_spec]] reads that version only from md2okf's own `SPEC.md`, never from a spec beside the wiki, so a copied bundle is checked against the same spec.
