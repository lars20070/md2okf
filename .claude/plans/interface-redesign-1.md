<!-- cspell:words argparse justfile direnv envrc getopts execvp dataclass subcommand subcommands DEVNULL Popen SBXAGENT -->

# Proposal: a `md2okf` command

How the wiki should be compiled from the command line. Three designs, their
trade-offs, and a recommendation. Scope is the current clone-and-run model:
the repository root is the project, holding `md/`, `okf/`, `SPEC.md`,
`kits/md2okf/` and `scripts/`.

## What is wrong with `make wiki`

`make wiki` and `./scripts/compile-okf.sh` are two spellings of the same job,
and neither is a good interface.

- **`make` is a build tool, and `wiki` is not a build.** The target is `.PHONY`
  with no inputs and no outputs, so make's one strength — skipping work that is
  up to date — is unused, while its weaknesses all apply: parameters only as
  environment variables (`RALPH_MAX=20 make wiki`), no `--help`, and it must be
  run from the repository root.
- **Arguments are split between the two entry points.** The source folder can
  only be passed to the script (`./scripts/compile-okf.sh md/other-books`), the
  iteration cap only through the environment. Neither can compile a single
  document, reuse a sandbox, or show what would run.
- **The options are undiscoverable.** `RALPH_MAX`, the folder positional,
  `XDG_STATE_HOME` and `.env` live in script comments and README prose.
- **Four launchers re-implement the same dance.** `compile-okf.sh`, `bash.sh`,
  `pi.sh` and `tests/test-sandbox.sh` each check for `sbx`, hold the
  `kit_name` constant, and decide whether to rebuild or reuse the sandbox — and
  they already disagree (compile rebuilds, the rest reuse), so a user has to
  remember which command carries which behaviour.
- **The host requirements exist to serve the driver, not the user.** `jq` is
  needed only to render Pi's JSON event stream; `make` only to reach the
  script. `README.md` lists both as prerequisites.
- **Nothing in the driver is tested.** The Ralph loop, the event rendering and
  the prompt construction are exercised only by a live, paid, minutes-long
  sandbox run. Only the mount library has host tests, in ad-hoc shell.

## What every design must keep

- **The sibling layout.** The kit's shims resolve the helper CLIs from
  `$(dirname "${WORKDIR}")/scripts/<cli>`, and the skills address `../md/`
  and `../SPEC.md`. The mounts stay: `okf/` read-write and primary, `md/`,
  `scripts/` and `SPEC.md` read-only, the state directory read-write.
- **The driver is not the agent's business.** It runs on the host, so it must
  not live under `scripts/`, which is mounted into the VM. Mount only what the
  agent needs.
- **`sbx` is the runtime.** The command orchestrates `sbx rm`, `sbx run
  --detached` and `sbx exec`; the OpenRouter key stays in `sbx secret`, keyed
  to the sandbox name `md2okf`.
- **The loop's known sharp edges.** `stdin` must be `/dev/null` for
  non-interactive `pi` or the run hangs; `merkleokf --nolog -L 0` must be given
  the absolute `okf` path, not `.`, or `log.md` is hashed and the loop never
  converges; the continuation prompt applies from the second iteration.
- **State precedence.** An exported `XDG_STATE_HOME` beats `.env`, which beats
  `~/.local/state`; a relative value counts as unset; the directory is created
  mode `0700`.
- **`make` remains the developer task runner** for `lint`, `validate` and the
  test suites. This proposal is about the user-facing runtime commands, not
  about repository chores.

## Proposal A — `bin/md2okf`, a Bash dispatcher

One executable script with subcommands, each the body of an existing launcher.
Installed onto `PATH` by a symlink, so it works from any directory.

```text
bin/md2okf                  dispatcher: parses the subcommand, calls a function
scripts/lib/sandbox.sh      sbx presence check, kit name, ensure_sandbox
                            (fresh|reuse), exec helpers; absorbs
                            sandbox-mounts.sh
```

```bash
md2okf compile [--max-iterations N] [--reuse] [DIR]
md2okf shell
md2okf pi [PI_ARGS...]
md2okf sandbox up [--fresh] | down | status
md2okf --help
```

Installation: `make install` runs `ln -sf "$PWD/bin/md2okf" ~/.local/bin/`,
or a `.envrc` with `PATH_add bin` for direnv users. The script resolves the
repository root from its own real path, so the symlink and the cwd do not
matter.

### Pros

- Smallest diff. Every existing script becomes a subcommand body; shellcheck,
  the Makefile and `tests/test-sandbox-mounts.sh` keep working as they are.
- No new toolchain on the host. Contributors already read and lint Bash here.
- Shippable in a day.

### Cons

- Bash option parsing is the weak point. `getopts` has no long options, so
  every subcommand carries a hand-rolled `while … case` loop and a hand-written
  help block, and the two drift apart.
- Testing stays ad-hoc shell. The Ralph loop, the JSON rendering and the
  prompt construction remain untested, exactly as today.
- `jq` and `make` stay host requirements — one for the event stream, one for
  the install.
- Two install mechanisms: `uv tool install` for the four helper CLIs, a
  symlink for this one.
- The 130-line driver becomes a 300-line dispatcher. Bash does not reward
  that growth; the repository's own Python CLIs show where the line is.

## Proposal B — `md2okf`, a Python CLI project installed with `uv tool`

A fifth stdlib-only uv project, laid out like the four helper CLIs, holding a
real command-line interface. The shell launchers and `sandbox-mounts.sh`
retire into it.

```text
md2okf/                     top-level, beside web2md/ and pdf2md/: the md→okf stage
  pyproject.toml            [project.scripts] md2okf = "md2okf.cli:main"; hatchling; ruff; pytest
  uv.lock
  README.md
  src/md2okf/
    cli.py                  argparse subcommands, --help, exit codes
    project.py              find_root(): walk up for kits/md2okf/spec.yaml;
                            Layout dataclass: md, okf, spec, scripts, kit,
                            state_dir; .env + XDG precedence
    sandbox.py              the one sbx seam: exists(), create(fresh),
                            exec(argv, stdin=DEVNULL, stream=…), remove()
    compile.py              the Ralph loop: documents, root hash, prompts, cap
    events.py               Pi --mode json line → text (replaces the jq filter)
  tests/                    pytest, offline: a fake sbx recorded per test,
                            precedence cases, event rendering, loop convergence
                            and the cap
```

Why a top-level `md2okf/` and not `scripts/md2okf/`: `scripts/` is mounted
read-only into the VM, and the driver must stay invisible to the agent. Why not
a root `pyproject.toml`: `CONTRIBUTING.md` keeps the repository root free of a
project so `uv run` and the lint boundaries stay per-directory; a top-level
project directory follows the `web2md/` and `pdf2md/` precedent. The cost is
`uv tool install ./md2okf` instead of `uv tool install .`.

```bash
md2okf compile [PATH ...] [--max-iterations N] [--reuse] [--dry-run]
md2okf shell                     # bash in the sandbox, reusing it
md2okf pi [-- PI_ARGS...]        # interactive Pi, reusing it
md2okf sandbox up [--fresh] | down | status
md2okf lint [PATH]               # okf-lint on the host, via pnpm dlx
md2okf doctor                    # sbx present and ≥ 0.43, logged in, key set,
                                 # state dir writable, kit spec valid
md2okf --version                 # reads VERSION
```

`compile` takes directories or files: a directory means every `*.md` directly
inside it, sorted; a file means that document alone. With no argument it
compiles `md/`. It rebuilds the sandbox by default, as today; `--reuse` keeps
the existing one, `sandbox up --fresh` is the explicit rebuild for the other
commands. `--dry-run` prints the sandbox command line, the mounts and the
document list without running Pi.

The root is found by walking up from the current directory until
`kits/md2okf/spec.yaml` and `SPEC.md` appear, like `git` finds `.git`;
`--project PATH` overrides. `md2okf compile` therefore works from `md/`, from
`okf/`, or from anywhere under the clone.

Installation: `uv tool install ./md2okf`, one more line in `make install-clis`;
`uv tool` already manages `~/.local/bin` for the helper CLIs. `uvx --from
./md2okf md2okf compile` works with no install at all.

The interactive subcommands (`shell`, `pi`) hand over with `os.execvp` after
ensuring the sandbox exists, so `sbx exec -it` gets the terminal directly and
there is no Python process in the signal path.

### Pros

- A real CLI: `--help` on every subcommand, typed arguments, validated values,
  consistent errors and exit codes. `RALPH_MAX` becomes `--max-iterations`;
  the folder positional becomes a documented argument that also accepts single
  files.
- Consistent with the repository. Same layout, install mechanism, ruff rules
  and pytest harness as the four helper CLIs; `make test-clis` and
  `make install-clis` gain one line each, and CI's `test-clis` job covers it.
- The loop becomes testable offline. A `Sandbox` seam lets tests fake `sbx`
  and assert on the prompt text, the continuation prompt, the hash comparison,
  the iteration cap and the `stdin=DEVNULL` guard — the sharp edges that are
  currently protected by comments alone.
- One implementation of "ensure the sandbox" shared by every subcommand and by
  `tests/test-sandbox.sh`, so rebuild-versus-reuse is a flag, not a property
  of which script you happened to run.
- Native JSON parsing removes `jq`; a real command removes `make` from the
  user-facing requirements. The README prerequisites shrink to `sbx` and `uv`.
- `doctor` turns the README's troubleshooting section into a command that
  checks the four things that actually go wrong.
- `Layout` is the single place that knows the sibling layout. If the project
  later wants to run against any folder, that class and the kit change; the
  loop does not.

### Cons

- The largest diff of the three: roughly 400–600 lines of Python plus tests,
  three scripts and one library retired, `tests/test-sandbox-mounts.sh`
  ported to pytest, `tests/test-sandbox.sh` rewritten to call
  `md2okf sandbox up`. Two to three days.
- `uv` becomes a requirement for compiling, not just for the helper CLIs and
  `make scrape`. It already is a requirement for `make install-clis`, and the
  README already sends users to it, so the practical cost is small.
- Wrapping `sbx exec` from Python adds one layer. `execvp` for the interactive
  commands and `Popen` line iteration for the event stream are the standard
  answers, but they are more code than a pipe into `jq`.
- The host side gains a second language. The guest-side `mount-state.sh` and
  the kit's `setup.install` steps are shell regardless, so contributors read
  both either way.

## Proposal C — replace `make` with `just` as the runner

Keep the scripts, replace the Makefile's runtime targets with a `justfile`
whose recipes take parameters.

```text
wiki dir="md" max="10":
    RALPH_MAX={{max}} ./scripts/compile-okf.sh {{dir}}
shell:
    ./scripts/bash.sh
pi *args:
    ./scripts/pi.sh {{args}}
```

`just wiki`, `just wiki md/other-books 20`, `just --list`. `just` finds the
`justfile` upward, takes positional recipe parameters, has no tab rules and
lists recipes with their parameters.

### Pros

- Half a day. The scripts are untouched.
- Fixes three concrete complaints: parameters, discoverability (`--list`), and
  the cwd requirement.
- Contributors get a readable recipe list instead of Makefile comments.

### Cons

- It is still a task runner. `just wiki md/other-books 20` is positional soup
  with no flags, no validation and no per-recipe `--help`; the interface is the
  runner's, not the project's.
- Another host install (`brew install just`; CI needs a setup action) for no
  functional gain over `make`, and the CI workflow and both guides are rewritten
  to match.
- The four launchers still duplicate the sandbox dance; `jq` stays; nothing
  becomes testable.
- It does not produce the `md2okf` command. The project's interface would be a
  generic runner's name.

## Comparison

| | A: Bash dispatcher | B: Python CLI | C: `just` |
| --- | --- | --- | --- |
| Effort | ~1 day | 2–3 days | ~half a day |
| Argument parsing and `--help` | hand-rolled per subcommand | argparse | positional, `--list` only |
| Works from any cwd | yes, via its own path | yes, walk-up like git | yes, justfile lookup |
| Install | symlink from `make` | `uv tool install`, as the helper CLIs | `brew install just` |
| Tests for the loop | none | pytest, offline, fake `sbx` | none |
| User-facing host requirements | `sbx`, `make`, `jq` | `sbx`, `uv` | `sbx`, `just`, `jq` |
| One "ensure sandbox" implementation | partly, via a shared lib | yes | no |
| Fits an existing convention | the `scripts/` scripts | the `scripts/*` CLI projects | new |
| Risk of drift between commands | medium | low | high |

## Recommendation: B

Build `md2okf/` as a Python CLI project and install it with `uv tool`, the
same way the four helper CLIs are built and installed. It is the only design
that produces a stable command surface, puts the Ralph loop under test, removes
`make` and `jq` from the user's path, and reuses a convention this repository
already enforces. The extra day over A buys `--help`, tests and a single
sandbox implementation, which A would need to grow anyway as soon as a second
flag arrives. C is a sideways move: better ergonomics for the same scripts,
plus a new dependency.

If a working command is needed this afternoon, A is the honest stopgap — but
build it as `md2okf compile`, not as a wrapper that calls `make wiki`, so the
Python version can replace it subcommand for subcommand.

### Behaviour to carry over verbatim

From `scripts/compile-okf.sh` and `scripts/lib/sandbox-mounts.sh`:

- Rebuild before compiling: `sbx rm --force md2okf || true`, then
  `sbx run --detached --name md2okf -e SBXAGENT_STATE_DIR=… <kit> <mounts>`.
- Mounts, in order: `okf` (primary, rw), `md:ro`, `scripts:ro`, `SPEC.md:ro`,
  the state directory (rw). Absolute host paths, so the VM sees the same
  paths.
- Documents named by absolute host path in the prompt, so Pi resolves them
  from any working directory.
- The two prompt strings, and the rule that the continuation prompt is
  appended from iteration 2.
- Hash with `sbx exec md2okf -- merkleokf --nolog -L 0 <abs okf>`, third line,
  first field.
- `pi --mode json` with `stdin=DEVNULL`; render `tool_execution_start` as
  `toolName args` cut to 120 characters, and assistant `message_end` text and
  thinking blocks.
- Cap at ten iterations unless told otherwise; exit 1 with the document name
  when hit.
- The "install with `brew install docker/tap/sbx`" hint when `sbx` is absent.

### Repository changes

- Add `md2okf/` (project, sources, tests, README).
- Retire `scripts/compile-okf.sh`, `scripts/bash.sh`, `scripts/pi.sh`,
  `scripts/lib/sandbox-mounts.sh`.
- `tests/test-sandbox.sh` calls `md2okf sandbox up` and keeps its `sbx exec`
  of the guest script. `tests/test-sandbox-mounts.sh` becomes
  `md2okf/tests/test_project.py`. `tests/test-mount-state.sh` stays: it tests
  the guest-side helper.
- Makefile: `install-clis` and `test-clis` gain the project; `wiki` becomes
  `uv run --project md2okf md2okf compile` for one release as an alias, then
  goes. `make lint` already picks up the new `pyproject.toml`.
- README: Quickstart becomes `uv tool install ./md2okf` then `md2okf compile`;
  Requirements drop `make` and `jq`; Troubleshooting points at
  `md2okf doctor`; the diagram's driver box becomes `md2okf compile`.
- `CONTRIBUTING.md`, `AGENTS.md`, `kits/md2okf/README.md`: command tables and
  the "`make wiki` always builds a fresh sandbox" sentences.
- `CHANGELOG.md` under `[Unreleased]`: Added the `md2okf` CLI; Removed the
  three launchers; Changed the host requirements.
- `.cspell.json`: `argparse` and whatever the sources add.

### Staging

1. Land `md2okf/` with `compile`, `shell`, `pi` and `sandbox`, tests included;
   `make wiki` delegates to it. Nothing else moves.
2. Port `test-sandbox-mounts.sh`, point `test-sandbox.sh` at
   `md2okf sandbox up`, delete the three scripts and the library, update the
   docs.
3. Add `doctor`, `lint` and `--dry-run`.

### Decisions left open

- `md2okf/` versus a root `pyproject.toml`. This proposal prefers the
  directory for consistency; the root form makes `uv tool install .` and
  `uv tool install git+https://github.com/lars20070/md2okf` work directly.
- Whether `make wiki` survives one release as an alias or goes at once.
- Whether `validate` (the kit schema check) joins the CLI as part of `doctor`
  only, or also as its own subcommand. `make validate` stays for CI either way.

### Out of scope

- A standalone tool that runs against any folder, with the kit, `SPEC.md` and
  the helper CLIs bundled in the package. Ruled out for now; `Layout` in
  `project.py` keeps it a contained change later.
- Making `web2md` and `pdf2md` subcommands. They are separate stages with
  their own projects; `make scrape` is untouched.
