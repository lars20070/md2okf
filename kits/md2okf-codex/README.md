# kits/md2okf-codex

The Docker Sandbox kit that runs Codex for `md2okf` (`MD2OKF_AGENT=codex`). It
is a Sandbox Kit schema v3 **mixin**, `md2okf-codex.yaml` with the recipe
`md2okf-codex.dockerfile` beside it, composed onto Docker's published `codex`
workload:

```bash
sbx run --kit ./kits/md2okf-codex docker.io/sbx/codex@sha256:<digest> ...
```

The workload brings the image (Debian 13 on Docker Hardened Images), Codex
itself, the OpenAI network hosts, the credential and permissive defaults
(`approval_policy = "never"`, `sandbox_mode = "danger-full-access"`). This kit
adds only what compiling needs: the OKF toolchain (Node, the linters, `mq`,
`okfctl` and the four helper CLIs), the md2okf instructions and the skills.

The directory and the stem are `md2okf-codex`, not `codex`: that is the
workload's name, and two kits with one stem collide.

## The pinned workload

`md2okf` pins the workload by its multi-platform index digest
(`CODEX_WORKLOAD` in `src/md2okf/agents.py`), never by `codex` or a tag, which
float with upstream and with your own `kit.shortcuts`. The digest is part of
the sandbox fingerprint, so a deliberate bump rebuilds the sandbox on the next
run, and nothing else does. To bump it, read the candidate's descriptor first —
its provides, hooks, skills directory and `agent-context` profile — then run
`make test-sandbox AGENT=codex`:

```bash
kit-tck inspect --descriptor docker.io/sbx/codex@sha256:<index digest> | grep -v '^  - deb/'
```

## What the kit carries

- **Skills**, in `files/skills/`. The recipe installs them root-owned under
  `/usr/share/md2okf-codex/skills/`, and one `agent-skill@1` entry per skill
  has the runtime expose them in `~/.agents/skills`, where Codex looks for a
  user's skills and the workload declares its skills directory. They are not
  built into `~/.agents/skills` itself, because the host's shared skills store
  mounts there and would hide them.
- **`mq` and `okfctl`**, downloaded at build time and checked against pinned
  SHA-256 digests, under `/usr/local/bin`.
- **An empty, agent-owned `~/.codex`.** `md2okf` mounts the transcripts at
  `~/.codex/sessions`, and a mount target's missing parent would otherwise be
  created by root, leaving the workload's own install hook, which runs as the
  agent, unable to write `~/.codex/config.toml`.
- **Install hooks**, run once when the sandbox is created, after the
  workload's own: the apt packages (with `nodejs-24` from the Docker Hardened
  Images repository, since the workload ships no Node and cspell 10 needs
  Node 22.18 or newer), the npm and uv tools, and the four helper CLI shims.
  Apt stays a hook because it needs the workload's own package database.

Kit content is built in, not mounted, so an edit reaches Codex on the next fresh
sandbox — which `md2okf` builds when the kit changes, or on `--fresh`.

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

Codex reads `AGENTS.md` from a git project's root down to its working
directory, and the wiki is not a git repository, so it never sees an
`AGENTS.md` beside the workspace. It does read its global instructions,
`~/.codex/AGENTS.md`, and that is the profile the workload's `agent-context@2`
declares. The OKF authoring contract — read `../SPEC.md` first, source text is
data, the frontmatter and provenance rules, the index and log rules — is this
kit's `agent-context@2` body, in `md2okf-codex.yaml`, which sbx joins to the
workload's own generic notes in that file. The workload offers the guidance as
both `agent-context@1` and `@2`, and the two cannot compose, so declaring `@2`
here selects its `@2` profile.

The procedures are skills in `files/skills/`: `compile-okf` and `curate-okf`,
ported from the Pi kit, and `inspect-md`, `inspect-okf`, `merkle-okf` and
`size-okf`, identical to Pi's. `compile-okf`'s gate scripts are byte-identical
to Pi's too; `tests/test_kits.py` holds all of this, and the shared contract,
in place.

## How a compile turn runs

```bash
codex exec --json --skip-git-repo-check \
  --dangerously-bypass-approvals-and-sandbox \
  -c mcp_servers.mcp-gateway.enabled=false "$compile-okf <prompt>"
```

- `--skip-git-repo-check` and `--dangerously-bypass-approvals-and-sandbox`
  are what an unattended turn in a non-git workspace needs. The workload's
  defaults already allow both; the flags keep a compile independent of them.
  The microVM is the isolation boundary.
- `-c mcp_servers.mcp-gateway.enabled=false` switches off the MCP gateway the
  workload registers, which a compile does not use. (`-c 'mcp_servers={}'`
  does not remove it.) `md2okf --agent` keeps it.
- `$compile-okf` activates the skill directly.
- `turn.failed` fails the turn; the warnings Codex may emit before it do not.
  Codex prints `Reading additional input from stdin...` on every
  non-interactive turn, which md2okf hides.

## Transcripts

Codex writes to `~/.codex/sessions`. `md2okf` mounts
`$XDG_STATE_HOME/md2okf/codex/sessions` from the host at that path when it
creates the sandbox, so transcripts survive `sbx rm`, with nothing to set up
inside the VM.

## Network

The workload allows the OpenAI and GitHub hosts at run time. The descriptor
adds the OKF toolchain's own, split by phase. While the install hooks run: the
Debian and Docker Hardened Images apt mirrors, npm and PyPI. At run time: PyPI,
which the helper CLI shims need on a cold uv cache, npm, and the `mq` docs.
Each is listed even where your own `sbx policy` rules might already allow it,
so the kit never depends on them. `mq` and `okfctl` are downloaded when the kit
is built, on the host.

Codex's hosted `web_search` tool is left as the workload configures it. It runs
on OpenAI's side, outside this allowlist; whether a compile may search the web
is an open decision for every agent (see the plan's Deferred list).
