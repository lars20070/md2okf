# kits/claude

The Docker Sandbox kit that runs Claude Code for `md2okf` (`MD2OKF_AGENT=claude`).
It `extends: claude`, sbx's built-in Claude Code kit, which brings the image,
Claude Code itself, the Anthropic network hosts and the credential. This kit
adds only what compiling needs: the OKF toolchain (the linters, `mq`,
`okfctl` and the four helper CLIs), the md2okf instructions and skills, the
transcript relocation, and the `md2okf-agent` wrapper every process starts
through. It needs sbx 0.45.0.

Everything under `files/home/` is copied into the sandbox at `~/`, so
`files/home/.claude/skills/` becomes six of Claude Code's skills. Config is
copied in when the kit is built, not mounted, so an edit reaches Claude Code
on the next fresh sandbox — which `md2okf` builds when the kit changes, or on
`--fresh`.

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
`agentInstructions`, in `spec.yaml`. sbx writes it as `CLAUDE.md` into the
workspace's parent directory, beside `../md/` and `../SPEC.md`, after sbx's own
generic notes on the sandbox; Claude Code loads it from there. It is outside
the wiki, so it never becomes part of the output.

The procedures are skills in `files/home/.claude/skills/`: `compile-okf` and
`curate-okf`, ported from the Pi kit, and `inspect-md`, `inspect-okf`,
`merkle-okf` and `size-okf`, identical to Pi's. `compile-okf`'s gate scripts are
byte-identical to Pi's too; `tests/test_kits.py` holds all of this, and the
shared contract, in place.

## How a compile turn runs

```bash
md2okf-agent claude -p --output-format stream-json --verbose \
  --permission-mode bypassPermissions --strict-mcp-config "<prompt>"
```

- `--permission-mode bypassPermissions` lets the headless turn write the wiki.
  The parent already defaults to it; the flag keeps a compile independent of
  that default. The microVM is the isolation boundary.
- `--strict-mcp-config`, with no `--mcp-config`, starts the turn with no MCP
  servers at all — neither the parent's gateway nor the claude.ai connectors
  of the signed-in account, none of which a compile uses. `md2okf --agent`
  keeps them.
- The prompt names `~/.claude/skills/compile-okf/SKILL.md`, as Pi's does.
- A `result` event whose `is_error` is true fails the turn, whatever its
  `subtype` says.

## Transcripts

Claude Code writes to `~/.claude/projects`, which the entrypoint, the startup
hook and `md2okf-agent` all bind-mount onto `$MD2OKF_STATE_DIR/sessions` — on
the host, `$XDG_STATE_HOME/md2okf/claude/sessions`.

## Network

The parent allows the Anthropic hosts. `spec.yaml` lists the OKF toolchain's
own hosts — npm, PyPI, the Ubuntu and Docker apt mirrors, GitHub's release
downloads, and the `mq` docs — even where your own `sbx policy` rules might
already allow them, so the kit never depends on them.
