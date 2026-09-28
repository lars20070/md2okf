# How md2okf works

How `md2okf` drives an agent inside a sandbox, what that sandbox can see, and
where its state lives. To install `md2okf` and compile a first wiki, see
[the README](../README.md).

## Contents

- [The run loop](#the-run-loop)
- [What the sandbox can reach](#what-the-sandbox-can-reach)
- [Credentials stay on the host](#credentials-stay-on-the-host)
- [Session state](#session-state)
- [Inspecting the sandbox](#inspecting-the-sandbox)
- [Repository layout](#repository-layout)

## The run loop

`md2okf` runs on your machine, the host, and drives a coding agent inside a
microVM: a small virtual machine that `sbx` creates. The host coordinates;
the agent does all its work inside the microVM.

Each agent has one sandbox, which every run with that agent reuses:
`md2okf-pi`, `md2okf-claude` or `md2okf-codex`. `sbx` fixes a sandbox's mounts
when it creates the sandbox, so mounting your own folders would mean
rebuilding the sandbox for every new `-o`, or writing into the first wiki.
Instead, `md2okf` stages each run through a fixed *workbench* under
`$XDG_STATE_HOME/md2okf/<agent>/`:

1. It copies your input documents into the workbench.
2. It copies the existing wiki from the `-o` directory into the workbench, so
   new documents extend that wiki rather than start a new one.
3. It runs the agent on each document in turn.
4. After every completed agent turn, it copies the wiki back to the `-o`
   directory, which then matches the workbench exactly: pages the agent
   deleted are deleted there too.

Because the mount paths never change, one sandbox serves any input and output
folder. `md2okf` rebuilds a sandbox only when the kit it was built from, the
`sbx` version or the mount paths change, when a quick check inside the VM
fails, or when you pass `--fresh`.

For each document, `md2okf` runs the agent repeatedly — a *Ralph loop* — until
the wiki stops changing. After each turn it hashes the wiki with
`merkleokf --nolog -L 0`, inside the sandbox. `merkleokf` builds a Merkle hash
tree, with one hash per Markdown file and per directory, so a change to any
page changes the root hash. `--nolog` leaves out the wiki's top-level
`log.md`, so a turn that only adds a log entry does not count as a change.
When the root hash is the same after a turn as before it, the document is
done. That includes a first turn that changes nothing: the document was
already in the wiki.

The loop stops with an error when the document needs more than `-n` turns
(default 10), when a turn fails, when a turn makes no tool calls, or when the
wiki is still empty at the end. An error stops the whole run, so later
documents are not compiled. Since `md2okf` copies the wiki back only after a
completed turn, an interrupted run leaves the `-o` directory as it was after
the last completed turn.

The agent can write only to the wiki and to its own transcripts. Its
instructions tell it to read `SPEC.md` first, which outranks every other
instruction, and to pass the [okfctl](https://github.com/cwest/okfctl) checks
before it stops. `md2okf` itself never runs `okfctl`. A stable hash means only
that the agent stopped changing the wiki, not that the wiki is complete or
correct.

A default run prints two progress lines per turn: the document and turn
number, then the root hash before and after. `-v` also streams the agent's tool
calls and messages. Either way, the agent writes a full transcript (see
[Session state](#session-state)).

## What the sandbox can reach

The sandbox gets neither your repository nor your own folders. `sbx` mounts
five paths into it, all inside the workbench. Nothing else from your machine
is visible inside the microVM: not `.git`, not the `Makefile`, not the kit
directory. (The kit's configuration is copied into the sandbox when it is
built; the kit directory itself is never mounted.)

Paths are relative to the workbench, `$XDG_STATE_HOME/md2okf/<agent>/`:

| Mount | Access | Contents |
| --- | --- | --- |
| `work/okf` | read-write | the wiki, and the agent's working directory |
| `work/md` | read-only | the staged source documents |
| `work/scripts` | read-only | the source of the four helper CLIs the agent runs |
| `work/SPEC.md` | read-only | the OKF specification, which outranks every other instruction |
| `sessions` | read-write | the agent's transcripts |

The agent therefore never sees one of your paths: it edits the staged wiki in
`work/okf`, and `md2okf` copies the result to your `-o` directory. The
workbench root itself is not mounted, because it also holds the record that
proves the sandbox belongs to `md2okf` (see [Session state](#session-state)).
No read-write mount contains a read-only one, so `work/md` and `work/SPEC.md`
stay read-only even to root inside the VM.

The mounts are defined in one place,
[`src/md2okf/workbench.py`](../src/md2okf/workbench.py). To see what a running
sandbox actually received, run `sbx inspect md2okf-<agent>`. `work/okf` is the
primary mount, so it is also the agent's working directory inside the VM. That
is why the agent refers to the other mounts as `../md/`, `../scripts/` and
`../SPEC.md`.

## Credentials stay on the host

`sbx` keeps model credentials out of the microVM. Its host-side proxy adds them
to outgoing requests, so, in the words of
[Docker's security documentation](https://docs.docker.com/ai/sandboxes/security/),
"credential values never enter the VM". With Pi you can see this directly:
inside the sandbox, `$OPENROUTER_API_KEY` reads `proxy-managed`, not your key.
Claude Code and Codex sign in differently, but `sbx` treats their credentials
the same way.

`sbx` gives a sandbox its credential only when it creates the sandbox. After
you set or change a credential, remove the sandbox with
`sbx rm --force md2okf-<agent>`, so that the next run builds one that has it.

## Session state

Each agent writes transcripts to its usual place inside the sandbox: Pi to
`~/.pi/agent/sessions`, Claude Code to `~/.claude/projects` and Codex to
`~/.codex/sessions`. That directory is bind-mounted onto
`$XDG_STATE_HOME/md2okf/<agent>/sessions` on the host, so transcripts survive
`sbx rm` and keep the agent's own layout.

Transcripts are kept apart per agent, not per project. Each agent has one
workbench and one sessions directory for all your projects, so compiling two
different repositories with the same agent writes to the same place. Every
`md2okf` installation or clone that uses the same state home shares it too.

`md2okf` finds the state home as follows: an exported `XDG_STATE_HOME` if it is
an absolute path, otherwise `~/.local/state`. The XDG specification requires
an absolute path, so a relative value counts as unset. Paths containing
spaces work.

The state home and the mounts are fixed when a sandbox is created. `md2okf`
records what it built — the sandbox's identity and a fingerprint of its
configuration — in the workbench root. It reuses the sandbox only when both
match and a quick check inside the VM succeeds. The fingerprint covers the
kit's files, the `sbx` version and the mount paths, so editing the kit or
upgrading `sbx` rebuilds the sandbox on the next run.

Changing `XDG_STATE_HOME` is the exception. The new state home holds no
record, so `md2okf` cannot prove that the existing `md2okf-<agent>` sandbox is
its own. It stops with exit code 2 rather than delete a sandbox it may not
own. `--fresh` does not change that: it only rebuilds a sandbox that `md2okf`
can prove it owns. Remove the sandbox yourself with
`sbx rm --force md2okf-<agent>`, then run again.

## Inspecting the sandbox

`md2okf --shell` opens a shell in the sandbox, in the wiki directory.
`md2okf --agent` opens an interactive session with the agent. Both are for
looking around, not for editing the wiki:

- They do not stage a new run. They restage the helper CLIs and the bundled
  `work/SPEC.md`; the rest of the workbench stays as the last compile left
  it.
- Nothing is copied back to your `-o` directory, and the next compile replaces
  `work/okf`, so changes made in either session are lost. Transcripts are kept.
- The session holds the lock until you exit, so any other `md2okf` run, with
  any agent, is refused until then.
- Only `--fresh` can be combined with them, and both need a terminal.
- `--shell` opens even when the agent's credential check fails, and prints the
  fix as a warning; `--agent` refuses to start.

## Repository layout

| Path | Contents |
| --- | --- |
| `md/` | the source documents compiled in this repository |
| `okf/` | the generated wiki, and the default for `-o`; not tracked by git |
| `src/md2okf/` | the `md2okf` command: the CLI, the agent definitions, the workbench, the calls to `sbx` and the Ralph loop |
| `scripts/` | the four helper CLIs the agent runs (`inspectmd`, `inspectokf`, `sizeokf`, `merkleokf`), plus scripts for repository chores |
| `kits/<agent>/` | one Docker Sandbox kit per agent (`pi`, `claude`, `codex`): the sandbox definition and the configuration it copies in |
| `tests/` | the driver's pytest suite and the shell tests for the sandbox |
| `Makefile` | developer tasks: lint, validate, tests and installs |
| `docs/` | reference pages: this page and [usage](usage.md) |
| `SPEC.md` | the [OKF specification](https://github.com/GoogleCloudPlatform/open-knowledge-format) the wiki is built against, vendored verbatim under Apache-2.0; see [NOTICE-OKF-SPEC.md](../NOTICE-OKF-SPEC.md) |
| `AGENTS.md` | instructions for coding agents working *on this repository*, not for the agents `md2okf` drives |
| `CONTRIBUTING.md` | how to develop, test and release `md2okf` |
| `extras/pdf2md/` | optional: converts a PDF into Markdown for `md/` |
| `extras/web2md/` | optional: scrapes a documentation site into one Markdown file in `md/` |
