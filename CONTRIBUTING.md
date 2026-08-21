# Contributing to md2okf

This guide covers working *on* the repository: the task runner, the test
suites, the sandbox kit, and how the agent's own configuration is laid out. If
you only want to compile a wiki, [the README](README.md) is enough.

`AGENTS.md` holds the same ground rules for coding agents working on this repo.

## Commands

```bash
make lint                # markdownlint, jq, yamllint, shellcheck, cspell, ruff
make validate            # check pi/spec.yaml against the Sandbox Kit schema
make test-web2md         # pytest, the web2md scraper suite
make test-clis           # pytest, the four host CLI suites
make install-clis        # install the four host CLIs onto PATH
make test-sandbox        # check the sandbox has the tools, config and key it promises
make lint-okf            # lint the generated wiki
make scrape              # fetch the website into md/ as one file
make wiki                # compile the OKF wiki
```

markdownlint needs `brew install markdownlint-cli2`; yamllint and ruff run via
`uv tool run` and cspell via `npx`, so none of them needs a separate install.
`make lint-okf` needs `pnpm`.

CI (`.github/workflows/ci.yml`) runs four jobs on every pull request: `lint`,
`test-web2md`, `test-clis`, and `validate-kit`. Each one reuses the matching
`make` target, so a green `make lint && make validate && make test-web2md &&
make test-clis` locally means a green build.

## Validate the kit spec before you finish

Touch anything under `pi/` or `scripts/*.sh` and run `make validate` before you
call the job done. It checks the kit spec against the schema bundled in your
`sbx` binary, and needs no Docker, no login and no network. CI runs the same
check in its `validate-kit` job, so catching a break locally saves a red build.
The current kit requires sbx 0.38.0 or newer; `brew upgrade sbx` fixes unknown
field errors from an older install.

`make test-sandbox` asks the other question: does the sandbox actually have
every tool `pi/spec.yaml` installs, the agent config copied in from `pi/files/`,
and a proxy-managed key? It needs an `sbx login` session. Like the scripts
below it reuses the sandbox — fast, and nothing a compile left behind is lost —
and only builds one if none exists. That also means it tests the sandbox you
have, which may be older than your last `pi/` edit. To check the current kit
from scratch, throw the sandbox away first with `sbx rm --force md2okf`;
building the next one takes minutes.

## Working inside the sandbox

```bash
./scripts/bash.sh                       # interactive shell in the existing sandbox
./scripts/pi.sh                         # interactive Pi in the same sandbox
./scripts/compile-okf.sh md/other-docs  # compile a different source folder
```

Once a sandbox exists, this should print `proxy-managed` rather than your key:

```bash
sbx exec md2okf -- sh -lc 'echo "$OPENROUTER_API_KEY"'
```

## Python layout

Python tooling is thin. There is no project at the repo root: `pdf2md/`,
`web2md/`, `scripts/inspectmd/`, `scripts/inspectokf/`, `scripts/sizeokf/`, and
`scripts/merkleokf/` are independent uv projects, each with its own
`pyproject.toml` and (where needed) `uv.lock`, and nothing shared between them.
`pdf2md/` exists only to give `marker` a pinned venv; `web2md/` owns the
scraper's dependencies and its pytest/ruff config; the four `scripts/` projects
are installable stdlib-only CLIs with their own ruff and pytest. So the heavy
dependencies (marker-pdf, torch) cannot reach the lint or test jobs at all,
rather than being excluded by flag.

`ruff` and `yamllint` belong to neither project; `make lint` runs them
ephemerally at a pinned version with `uv tool run`, and checks each tracked
subproject in turn — a new subproject carries its own `[tool.ruff]` and needs no
Makefile change.

### Helper CLIs

Four CLIs survey the wiki. The sandbox exposes the same commands to the agent,
and `make install-clis` puts them on your own PATH. All four take `-L`/`--level`
as a depth cap.

| Command | What it prints |
| --- | --- |
| `inspectmd <file>` | a Markdown heading map: line ranges, word counts, kebab-case slugs |
| `inspectokf [path]` | the wiki directory tree, via `tree` (default `okf/`) |
| `sizeokf [path]` | Markdown word counts per file and folder, excluding frontmatter |
| `merkleokf [path]` | a Merkle hash tree, one hash per file and per directory |

`sizeokf` and `merkleokf` also take `--nolog`, which ignores `okf/log.md`.
`merkleokf` hashes raw bytes, deliberately the opposite of `sizeokf`, which
strips frontmatter: `merkleokf` answers "did this change", `sizeokf` answers
"how much prose is here", and they share no code.

## How the agent knows what to do

The instructions come in two parts. `pi/files/home/.pi/agent/AGENTS.md` holds
what every task must respect: the OKF conventions, the directories the agent may
write to, and the rule that `SPEC.md` outranks both. Each task's procedure lives
in a skill of its own. Task skill today: `compile-okf`. Tool skills:
`inspect-md`, `inspect-okf`, `size-okf`, `merkle-okf` — a tool gets a skill, not
an `AGENTS.md` section. The sandbox also installs the `context7-docs` skill via
`@upstash/context7-pi` for library docs lookups. A new task gets a new directory
rather than more rules in `AGENTS.md`.

A skill is a directory holding a `SKILL.md` — YAML frontmatter with a `name` and
`description`, then the instructions, plus any scripts it needs. Pi picks skills
up from `~/.pi/agent/skills/`.

The kit is `pi/`, and the config it carries lives in `pi/files/home/.pi/agent/`.
That config is copied into the sandbox when the kit is built, not mounted, so an
edit reaches Pi on the next fresh sandbox — which `make wiki` always builds.
[The pi kit guide](pi/README.md) covers the model and provider settings.

`tests/` holds shell tests for that sandbox, in pairs: a host-side script
(`test-sandbox.sh`, which owns the sandbox and calls `sbx`) and the POSIX `sh`
script it runs inside the VM (`test-sandbox-guest.sh`).

## Linting the wiki

[okf-lint](https://github.com/thisismydesign/okf-lint) checks the wiki against
the spec. Rules live in `okf/.okflintrc.json`, tracked and un-ignored by name so
it survives the `okf/*` rule in `.gitignore`.

The sandbox installs okf-lint at a pinned version, and the `compile-okf` skill
wraps it in its own `scripts/lint-okf.sh`. The agent lints its own output and fixes what
the linter reports before it finishes. On the host, `make lint-okf` runs the
same tool through `pnpm dlx`. It sits outside `make lint` and outside CI because
`okf/` is generated.
