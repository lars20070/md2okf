# Configuration

What `md2okf` reads from your environment, and what it doesn't read at all.
For installing and a first compile, see [the README](../README.md).

## Environment variables

Three variables matter, and only the first two are read by `md2okf` itself.
`md2okf --help` lists the same three.

| Variable | Read by | What it does |
| --- | --- | --- |
| `MD2OKF_AGENT` | the host driver | Which agent compiles: `pi` (default, also what an unset or empty value means), `claude`, or `codex`. An unrecognized value is refused with exit 2 before anything runs. See [Setup](setup.md#choose-an-agent-and-set-its-credential). |
| `XDG_STATE_HOME` | the host driver | Where session state and the run workbench live. Must be an absolute path — a relative value counts as unset — and defaults to `~/.local/state`. See [Architecture](architecture.md#session-state). |
| `OPENROUTER_API_KEY` | never — checked inside the sandbox only | `md2okf` never reads this from your shell. It's stored with `sbx secret` on the host and checked inside the sandbox before every run. See [Set up the OpenRouter key](setup.md#set-up-the-openrouter-key). |

`MD2OKF_STATE_DIR` and `WORKDIR` are set by `md2okf` itself when it builds
the sandbox. Nothing reads them from your shell; they aren't yours to set.

## No `--model` flag, no config file

`md2okf` takes no `--model` flag and reads no configuration file of its
own. That doesn't mean the agents it drives have no configuration — each
one does, inside its own kit.

The OKF specification cannot be changed either. `md2okf` always compiles
against its own `SPEC.md`, and the checks the agent runs always compare
the wiki against that same file. See [Setup](setup.md#no---model-flag-no-config-file)
and the kit guides it links to.
