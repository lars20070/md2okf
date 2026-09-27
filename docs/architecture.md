# How md2okf works

The run loop, the sandbox's view of your files, where session state lives, and
the repository layout. For installing and a first compile, see
[the README](../README.md).

## The run loop

`md2okf` runs on the host and drives the agent inside a microVM, repeatedly,
until a hash of the output stops moving. The host drives; everything else
happens inside the sandbox.

One sandbox per agent serves every run with that agent — `md2okf-pi`,
`md2okf-claude`, `md2okf-codex`. Rather than mounting your folders — sbx fixes
a sandbox's mounts when it is created, so a second `-o` would mean either a
rebuild or writing into the first wiki — the command stages each run through a
fixed workbench under `$XDG_STATE_HOME/md2okf/<agent>/work`: your inputs are
copied in, the target wiki is mirrored in before the run and back out after
every iteration, and the mount paths never change. The sandbox is rebuilt only
when the kit it was built from changes, when the configuration no longer
matches, or on `--fresh`.

It runs the agent once per document, re-running the same document (a *Ralph
loop*) until `merkleokf --nolog -L 0` reports an unchanged wiki root hash.
`merkleokf` prints a Merkle hash tree, one hash per file and per directory, so a
change to any page moves the root hash and an unchanged root means the run added
nothing — which on a first pass is the idempotent re-run, not a failure. The
loop is capped by `-n` (default 10). The agent's only writable content output is
`okf/`, the [okfctl](https://github.com/cwest/okfctl) check must pass before it
finishes, and `SPEC.md` outranks every instruction file. Each run streams
tool names and assistant text as it goes, and the agent writes its transcript
through its native path into persistent host state.

## Inspecting the sandbox

`md2okf --shell` and `md2okf --agent` are for inspecting the sandbox rather
than authoring in it. They do not
restage a compile run: helper CLIs are refreshed, an empty spec mount gets the
bundled spec, and prior workbench content otherwise remains. The next compile
replaces `work/okf`; the agent's transcripts persist. The workbench lock remains held
until the session exits, so a concurrent compile or `--fresh` invocation is
refused. Only `--fresh` combines with them.

## What the sandbox can reach

The sandbox does not get the repository, and it does not get your folders
either. It gets five named mounts, all of them inside the workbench, and
nothing else of yours is visible inside the microVM — not `.git`, not the
`Makefile`, not the kit that built it:

| Mount | Access | Why |
| --- | --- | --- |
| `work/okf` | read-write | the wiki, and the agent's working directory |
| `work/md` | read-only | the staged source documents, read as data and never modified |
| `work/scripts` | read-only | the four helper CLI projects the agent runs |
| `work/SPEC.md` | read-only | the specification that outranks every instruction |
| `$XDG_STATE_HOME/md2okf/<agent>/sessions` | read-write | the agent's persistent transcripts |

Every one of them is under `$XDG_STATE_HOME/md2okf/<agent>`, so the agent never sees a
path of yours: it works on the staged copies, and the driver mirrors the wiki
back out. The state *root* is deliberately not mounted — it also holds the
host-side ownership marker — and no read-write mount is an ancestor of a
read-only one, so `work/md` and `work/SPEC.md` stay read-only even against root
in the guest. The mount list lives in one place,
[`src/md2okf/workbench.py`](../src/md2okf/workbench.py); `sbx inspect md2okf-<agent>` shows
what a running sandbox actually got. Because `work/okf` is the primary mount it
is also the working directory inside the VM, which is why the agent addresses
its siblings as `../md/`, `../scripts/` and `../SPEC.md`.

## Session state

Each agent writes transcripts through its own native path — Pi to
`~/.pi/agent/sessions`, Claude Code to `~/.claude/projects`, Codex to
`~/.codex/sessions`. Inside the sandbox that directory is bind-mounted onto the
host's `$XDG_STATE_HOME/md2okf/<agent>/sessions`, so transcripts survive
`sbx rm` and keep the agent's native layout. All md2okf clones using the same
state home intentionally share this directory; each agent's own layout
separates their working directories.

State location follows this precedence: an exported absolute `XDG_STATE_HOME`,
then `~/.local/state`. XDG requires an absolute path, so a relative value counts
as unset. Paths containing spaces are supported.

The state location and the mounts are fixed when a sandbox is created. `md2okf`
records what it built — the sandbox's identity and the configuration
fingerprint — *under that state root*, and reuses the sandbox only when the
recorded identity, the fingerprint and a cheap in-VM probe all agree. Edit the
kit, or change anything else the fingerprint covers, and the next run rebuilds
by itself.

Changing `XDG_STATE_HOME` is the exception, because it moves the record out of
view: the new state root has no marker, so a sandbox still named
`md2okf-<agent>` cannot be proved to be ours. `md2okf` stops with exit 2 rather
than deleting something it may not own, and `--fresh` does not override that —
it recreates a sandbox we *can* prove is ours. Run
`sbx rm --force md2okf-<agent>` yourself, then use the new state home.

## Repository layout

| Path | Description |
| --- | --- |
| `md/` | source documents, one agent run each |
| `okf/` | the generated wiki, `-o`'s default |
| `src/md2okf/` | the `md2okf` command: workbench, sbx seam, Ralph loop |
| `Makefile` | the developer tasks — lint, validate, tests, installs |
| `scripts/` | the four helper CLIs the agent runs (`inspectmd`, `inspectokf`, `sizeokf`, `merkleokf`), plus repository chores |
| `kits/<agent>/` | what the driver runs: one Docker Sandbox kit per agent (`pi`, `claude`, `codex`) and the config it carries |
| `docs/` | reference pages split out of the README: this page, [configuration](configuration.md), [troubleshooting](troubleshooting.md) |
| `SPEC.md` | the [OKF specification](https://github.com/GoogleCloudPlatform/open-knowledge-format) the wiki is built against — vendored verbatim, Apache-2.0, see [NOTICE-OKF-SPEC.md](../NOTICE-OKF-SPEC.md) |
| `AGENTS.md` | instructions for coding agents working *on this repo*, not for the agents md2okf drives |
| `pdf2md/` | optional: converts a PDF into `md` |
| `web2md/` | optional: scrapes a documentation site into `md` |
