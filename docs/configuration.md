# Configuration

The environment variables `md2okf` reads. For installing and a first compile,
see [the README](../README.md).

## Environment

Four variables are worth knowing about, and only the first three are yours to
set. `md2okf --help` lists the same four.

| Variable | What it does |
| --- | --- |
| `MD2OKF_AGENT` | Optional. The agent that compiles: `pi`, the default (unset or empty means `pi`), `claude` for Claude Code, or `codex` for Codex — see [Choosing an agent](../README.md#choosing-an-agent). An unknown value is refused with exit 2 before anything runs. |
| `OPENROUTER_API_KEY` | Required for `pi`. `md2okf` takes the key from `sbx secret` and refuses to start unless it is proxy-managed — see [Set up the OpenRouter key](../README.md#set-up-the-openrouter-key). |
| `XDG_STATE_HOME` | Optional. Where session state and the run workbench live. Absolute paths only — a relative value counts as unset — and the default is `~/.local/state`. Changing it once a sandbox exists takes one manual step; see [Session state](architecture.md#session-state). |
| `SPEC_MD` | Optional. The spec the frontmatter guard reads, which defaults to the sibling of the bundle root. Needed when checking a wiki outside this repository: `SPEC_MD=/path/to/SPEC.md check-okf.sh /some/wiki`. |

Everything else the sandbox uses is set by `md2okf` itself: `MD2OKF_STATE_DIR`
and `WORKDIR` are injected at creation, and nothing reads them from your shell.
