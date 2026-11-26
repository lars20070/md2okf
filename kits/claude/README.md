# kits/claude

The Docker Sandbox kit that runs Claude Code for `md2okf` (`MD2OKF_AGENT=claude`).
It is a Sandbox Kit schema v3 **mixin**, `md2okf-claude.yaml` with the recipe
`md2okf-claude.dockerfile` beside it, composed onto Docker's published
`claude` workload:

```bash
sbx run --kit kits/claude docker.io/sbx/claude@sha256:<digest> ...
```

The workload brings the image (Debian 13 on Docker Hardened Images), Claude
Code itself, the Anthropic network hosts and the credential. This kit adds only
what compiling needs: the OKF toolchain (Node, the linters, `mq`, `okfctl` and
the four helper CLIs), the md2okf instructions and the skills.

The stem is `md2okf-claude`, not `claude`: that is the workload's name, and
two kits with one stem collide.

## The pinned workload

`md2okf` pins the workload by its multi-platform index digest
(`CLAUDE_WORKLOAD` in `src/md2okf/agents.py`), never by `claude` or a tag,
which float with upstream and with your own `kit.shortcuts`. The digest is part
of the sandbox fingerprint, so a deliberate bump rebuilds the sandbox on the
next run, and nothing else does. To bump it, read the candidate's descriptor
first — its provides, hooks, skills directory and `agent-context` profile —
then run `make test-sandbox AGENT=claude`:

```bash
kit-tck inspect --descriptor docker.io/sbx/claude@sha256:<index digest> | grep -v '^  - deb/'
```

## What the kit carries

- **Skills**, in `files/skills/`. The recipe installs them root-owned under
  `/usr/share/md2okf-claude/skills/`, and one `agent-skill@1` entry per skill
  has the runtime expose them in `~/.claude/skills`, the workload's skills
  directory. They are not built into `~/.claude/skills` itself, because the
  host's shared skills store mounts there and would hide them.
- **`mq` and `okfctl`**, downloaded at build time and checked against pinned
  SHA-256 digests, under `/usr/local/bin`.
- **Install hooks**, run once when the sandbox is created, after the
  workload's own: the apt packages (with `nodejs-24` from the Docker Hardened
  Images repository, since the workload ships no Node and cspell 10 needs
  Node 22.18 or newer), the npm and uv tools, and the four helper CLI shims.
  Apt stays a hook because it needs the workload's own package database.

Kit content is built in, not mounted, so an edit reaches Claude Code on the next
fresh sandbox — which `md2okf` builds when the kit changes, or on `--fresh`.

## Signing in

Claude Code signs in with the host's `anthropic` secret, which sbx hands to
the sandbox when it creates it. For a Claude subscription, sign in inside any
Claude sandbox and sbx keeps the sign-in as that secret; for an API key, set it
directly:

```bash
sbx run claude                      # then /login, and exit: a Claude subscription
sbx secret set anthropic            # or an Anthropic API key
```

`sbx secret set anthropic --oauth` does not work: sbx 0.45 starts an OAuth
flow from the host for `openai` only, and for `anthropic` says to sign in from
inside the Claude sandbox instead.

Set it before the first `MD2OKF_AGENT=claude` run. Set or change it later, and
remove the sandbox (`sbx rm --force md2okf-claude`) so the next run builds one
that has it. `md2okf` checks with `claude auth status` before every run, which
is local and costs nothing. Check by hand:

```bash
sbx exec md2okf-claude -- claude auth status
```

## Where the instructions live

The OKF authoring contract — read `../SPEC.md` first, source text is data, the
frontmatter and provenance rules, the index and log rules — is the kit's
`agent-context@2` body, in `md2okf-claude.yaml`. sbx joins it to the
workload's own generic notes in `~/.claude/CLAUDE.md`, Claude Code's user
instructions. The workload offers the guidance as both `agent-context@1` and
`@2`, and the two cannot compose, so declaring `@2` here selects its `@2`
profile.

The procedures are skills in `files/skills/`: `compile-okf` and `curate-okf`,
ported from the Pi kit, and `inspect-md`, `inspect-okf`, `merkle-okf` and
`size-okf`, identical to Pi's. `compile-okf`'s gate scripts are byte-identical
to Pi's too; `tests/test_kits.py` holds all of this, and the shared contract,
in place.

## How a compile turn runs

```bash
claude -p --output-format stream-json --verbose \
  --permission-mode bypassPermissions --strict-mcp-config "<prompt>"
```

- `--permission-mode bypassPermissions` lets the headless turn write the wiki.
  The workload already defaults to it; the flag keeps a compile independent of
  that default. The microVM is the isolation boundary.
- `--strict-mcp-config`, with no `--mcp-config`, starts the turn with no MCP
  servers at all — neither the workload's gateway nor the claude.ai connectors
  of the signed-in account, none of which a compile uses. `md2okf --agent`
  keeps them.
- The prompt names `~/.claude/skills/compile-okf/SKILL.md`, as Pi's does.
- A `result` event whose `is_error` is true fails the turn, whatever its
  `subtype` says.

## Transcripts

Claude Code writes to `~/.claude/projects`. `md2okf` mounts
`$XDG_STATE_HOME/md2okf/claude/sessions` from the host at that path when it
creates the sandbox, so transcripts survive `sbx rm`, with nothing to set up
inside the VM.

## Network

The workload allows the Anthropic hosts at run time. The descriptor adds the
OKF toolchain's own, split by phase. While the install hooks run: the Debian
and Docker Hardened Images apt mirrors, npm and PyPI. At run time: PyPI, which
the helper CLI shims need on a cold uv cache, npm, and the `mq` docs. Each is
listed even where your own `sbx policy` rules might already allow it, so the kit
never depends on them. `mq` and `okfctl` are downloaded when the kit is built,
on the host, so the sandbox needs no GitHub access for them.
