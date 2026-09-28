# Configuration

How to choose an agent, give it a credential, and set the few things `md2okf`
reads from your environment. To install `md2okf` and `sbx` and compile a first
wiki, see [the README](../README.md).

## Contents

- [Environment variables](#environment-variables)
- [Choosing an agent](#choosing-an-agent)
- [Credentials](#credentials)
- [Models and providers](#models-and-providers)
- [Other ways to install](#other-ways-to-install)

## Environment variables

`md2okf --help` lists three variables. `md2okf` reads the first two; it never
reads the third.

| Variable | What it does |
| --- | --- |
| `MD2OKF_AGENT` | Which agent compiles: `pi` (the default, and what an unset or empty value means), `claude` or `codex`. Any other value is refused with exit code 2 before anything runs. See [Choosing an agent](#choosing-an-agent). |
| `XDG_STATE_HOME` | Where session state and the workbench live. It must be an absolute path; a relative value counts as unset. The default is `~/.local/state`. See [Session state](architecture.md#session-state). |
| `OPENROUTER_API_KEY` | Pi's key. `md2okf` never reads it from your shell: you store it with `sbx secret`, and `md2okf` checks inside the sandbox that it arrived. See [Set up the OpenRouter key](../README.md#set-up-the-openrouter-key). |

Two more variables exist inside the sandbox, and neither is yours to set:
`md2okf` sets `MD2OKF_STATE_DIR` when it creates the sandbox, and `sbx` sets
`WORKDIR` to the wiki workspace.

## Choosing an agent

| `MD2OKF_AGENT` | Agent | Sandbox | Credential |
| --- | --- | --- | --- |
| `pi` (default) | [Pi](https://pi.dev) | `md2okf-pi` | an OpenRouter API key |
| `claude` | [Claude Code](https://code.claude.com) | `md2okf-claude` | a Claude subscription or an Anthropic API key |
| `codex` | [Codex](https://github.com/openai/codex) | `md2okf-codex` | a ChatGPT subscription or an OpenAI API key |

For example, to compile the folder `md/`
into `okf/` with Claude Code instead of Pi:

```bash
MD2OKF_AGENT=claude md2okf md/ -o okf/        # for this one command
export MD2OKF_AGENT=claude                    # or for the rest of the shell session
md2okf md/ -o okf/
```

Setting the variable in front of the command applies it to that run only;
`export` keeps it for every later `md2okf` command in the same shell. Either
way, the run uses Claude Code's own sandbox, `md2okf-claude`, which the first
run builds, so Claude Code needs its credential first (see
[Claude Code](#claude-code)). Pi's sandbox is left untouched, and unsetting
the variable (`unset MD2OKF_AGENT`) switches back to Pi.

Don't confuse `MD2OKF_AGENT` with the `--agent` flag, which opens an
interactive session with whichever agent is already chosen.

Before every run, `md2okf` checks that the agent's credential has reached
its sandbox, and prints the commands that fix it if not. Every iteration of a
compile calls the agent's model, which uses API credit or subscription
allowance, so start with a small document.

## Credentials

Set a credential before the first run with an agent. `sbx` passes it to a
sandbox only when it creates the sandbox, so after setting or changing one,
remove that agent's sandbox as described in
[Credentials stay on the host](architecture.md#credentials-stay-on-the-host).

### Pi

Pi uses an OpenRouter API key; see
[Set up the OpenRouter key](../README.md#set-up-the-openrouter-key).

### Claude Code

Claude Code signs in with the host's `anthropic` secret:

```bash
sbx run claude                      # then /login, and exit: a Claude subscription
sbx secret set anthropic            # or an Anthropic API key
```

`sbx secret set anthropic --oauth` does not work. `sbx` starts an OAuth flow
from the host only for `openai`; for `anthropic` it asks you to sign in from
inside a Claude sandbox, which is what the first command does.

### Codex

Codex signs in with the host's `openai` secret, which `sbx` routes through its
own model provider:

```bash
sbx secret set openai --oauth    # a ChatGPT subscription
sbx secret set openai            # or an OpenAI API key
```

## Models and providers

`md2okf` has no `--model` flag and no configuration file. The model is set in
each agent's kit. To choose another OpenRouter model for Pi, or to point Pi at
a different provider, see [the Pi kit guide](../kits/pi/README.md). The Claude
Code and Codex kits set no model, so those agents use their own defaults; see
the [Claude Code](../kits/claude/README.md) and
[Codex](../kits/codex/README.md) kit guides.

The OKF specification is fixed as well: `md2okf` always compiles against its
own `SPEC.md`, and the checks the agent runs compare the wiki against that
same file.

## Other ways to install

Besides the PyPI install in the README, `uv` can install the latest commit or
a clone you have edited:

```bash
uv tool install git+https://github.com/lars20070/md2okf   # the latest commit (needs git)
uv tool install .                                          # a clone you have edited
```
