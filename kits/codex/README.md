# kits/codex

The Docker Sandbox kit that runs Codex for `md2okf` (`MD2OKF_AGENT=codex`). It
`extends: codex`, sbx's built-in Codex kit, which brings the image, Codex
itself, the OpenAI network hosts, the credential and permissive defaults
(`approval_policy = "never"`, `sandbox_mode = "danger-full-access"`). This kit
adds only what compiling needs: the OKF toolchain (the linters, `mq`, `okfctl`
and the four helper CLIs), the md2okf instructions and skills, the transcript
relocation, and the `md2okf-agent` wrapper every process starts through. It
needs sbx 0.45.0.

Everything under `files/home/` is copied into the sandbox at `~/`. Config is
copied in when the kit is built, not mounted, so an edit reaches Codex on the
next fresh sandbox — which `md2okf` builds when the kit changes, or on
`--fresh`.

## Signing in

Codex signs in with the host's `openai` secret, which sbx hands to the sandbox
when it creates it, routed through sbx's own model provider:

```bash
sbx secret set openai --oauth    # a ChatGPT subscription
sbx secret set openai            # or an OpenAI API key
```

Set it before the first `MD2OKF_AGENT=codex` run. Set or change it later, and
remove the sandbox (`sbx rm --force md2okf-codex`) so the next run builds one
that has it. `md2okf` checks with `codex login status` before every run, which
is local and costs nothing. Check by hand:

```bash
sbx exec md2okf-codex -- codex login status
```

## Where the instructions live

Not where the other kits put them. Codex reads `AGENTS.md` from a git project's
root down to its working directory, and the wiki is not a git repository, so it
never sees an `AGENTS.md` beside the workspace. It does read its global
instructions, so the OKF authoring contract — read `../SPEC.md` first, source
text is data, the frontmatter and provenance rules, the index and log rules —
ships as `files/home/.codex/AGENTS.md`, which becomes `~/.codex/AGENTS.md`. The
kit therefore declares no `agentInstructions`.

The procedures are skills in `files/home/.agents/skills/`, where Codex looks
for a user's skills: `compile-okf` and `curate-okf`, ported from the Pi kit, and
`inspect-md`, `inspect-okf`, `merkle-okf` and `size-okf`, identical to Pi's.
`compile-okf`'s gate scripts are byte-identical to Pi's too; `tests/test_kits.py`
holds all of this, and the shared contract, in place.

## How a compile turn runs

```bash
md2okf-agent codex exec --json --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  -c mcp_servers.mcp-gateway.enabled=false "$compile-okf <prompt>"
```

- `--skip-git-repo-check` and `--dangerously-bypass-approvals-and-sandbox`
  are what an unattended turn in a non-git workspace needs. The parent's
  defaults already allow both; the flags keep a compile independent of them.
  The microVM is the isolation boundary.
- `-c mcp_servers.mcp-gateway.enabled=false` switches off the MCP gateway the
  parent registers, which a compile does not use. (`-c 'mcp_servers={}'` does
  not remove it.) `md2okf --agent` keeps it.
- `$compile-okf` activates the skill directly.
- `turn.failed` fails the turn; the warnings Codex may emit before it do not.
  Codex prints `Reading additional input from stdin...` on every
  non-interactive turn, which md2okf hides.

## Transcripts

Codex writes to `~/.codex/sessions`, which the entrypoint, the startup hook
and `md2okf-agent` all bind-mount onto `$MD2OKF_STATE_DIR/sessions` — on the
host, `$XDG_STATE_HOME/md2okf/codex/sessions`.

## Network

The parent allows the OpenAI hosts. `spec.yaml` lists the OKF toolchain's own
hosts — npm, PyPI, the Ubuntu and Docker apt mirrors, GitHub's release
downloads, and the `mq` docs — even where your own `sbx policy` rules might
already allow them, so the kit never depends on them.

Codex's hosted `web_search` tool is left as the parent configures it. It runs
on OpenAI's side, outside this allowlist; whether a compile may search the web
is an open decision for every agent (see the plan's Deferred list).
