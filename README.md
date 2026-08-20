# md2okf

Drop Markdown files into `md/`, run `make wiki`, and the Pi coding agent writes
an OKF knowledge base into `okf/`. It takes one source document per run and
folds it into the wiki: a page per topic, an index in every directory, links
between them, and a log of what each run changed.

OKF, the [Open Knowledge Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf), is a tree of Markdown files with YAML
frontmatter and nothing else. No schema registry, no server, nothing to install.
`SPEC.md` at the repo root is the OKF specification this wiki is built against. The agent
reads it at the start of every run, so the spec outranks anything written here.

| Path | Description |
| --- | --- |
| `md/` | source documents, one Pi run each |
| `okf/` | the generated wiki |
| `Makefile` | every task worth running; `make wiki` compiles |
| `scripts/` | what the Makefile calls — compile, sandbox shell, kit validation, and the four helper CLIs (`inspectmd`, `inspectokf`, `sizeokf`, `merkleokf`) |
| `pi/` | what the scripts run: the Docker Sandbox kit and the config it carries |
| `SPEC.md` | the OKF specification the wiki is built against |
| `AGENTS.md` | instructions for coding agents working *on this repo*, not for Pi |
| `pdf2md/` | optional: converts a PDF into `md` |
| `web2md/` | optional: scrapes a documentation site into `md` |

## Compile a wiki

### Set up, once

```bash
brew install docker/tap/sbx
sbx login
```

The kit uses the finalized kit-spec v2 grammar and requires sbx 0.38.0 or
newer. Run `brew upgrade sbx` if an older installation reports unknown fields
from `pi/spec.yaml`. `sbx login` opens a browser to sign in with a Docker
account; the sandbox runtime requires that host session.

sbx keeps the OpenRouter key out of the virtual machine. It holds the real
string on the host and swaps it into requests at its proxy, so inside the
sandbox `$OPENROUTER_API_KEY` reads `proxy-managed`. Set it twice:

```bash
export OPENROUTER_API_KEY=sk-or-...

echo "$OPENROUTER_API_KEY" | sbx secret set openrouter

# And again as a custom secret, to work around a known sbx bug. https://github.com/docker/sbx-releases/issues/25
sbx secret set-custom --sandbox md2okf \
  --host openrouter.ai \
  --env OPENROUTER_API_KEY \
  --value "$OPENROUTER_API_KEY"
```

`md2okf` is the kit's name, which comes from `pi/spec.yaml`.

### Run it

Put your Markdown in `md/`, then:

```bash
make wiki
```

The driver throws the old sandbox away and builds a fresh one, so the current
kit and secrets apply. It then runs Pi for each `md/*.md` file, re-running the
same document (Ralph loop) until `merkleokf --nolog -L 0` reports an unchanged
wiki root hash, capped by `RALPH_MAX` (default 10). Each run streams tool names
live (`pi --mode json`) and writes session transcripts under `logs/sessions/`.
`okf/` is gitignored apart from `okf/.okflintrc.json`, so the wiki itself stays
out of the repo. `md/` is tracked, and ships with one sample document.

### What lands in okf/

```text
okf/
├── index.md          # root index, the only one carrying frontmatter
├── log.md            # what each run changed, newest first
├── <page>.md         # a content page at the wiki root
└── <topic>/          # one directory per topic, nested as deep as it needs
    ├── index.md      # a plain link list for this directory
    └── <page>.md     # a content page within the topic
```

Content pages carry `type`, `title`, `description` and `tags` in their
frontmatter. Slugs are kebab-case. Links are bundle-absolute, so
`/glossary/verb.md` rather than `glossary/verb.md`. The root `index.md` names
the spec version the agent read. Pages are updated in place, not duplicated, so
compiling the same document twice is safe.

## Getting Markdown in

`md/` wants clean, structured Markdown, and a source document is rarely that.
Two helpers produce it. Both are optional, and neither is part of `make wiki`.

**From a PDF.** `marker` converts one with the help of a language model, either
a local Ollama model or a cloud model through OpenRouter. Expect to check the
output. The step is manual and not wired into `make` —
[pdf2md/README.md](pdf2md/README.md) has the commands.

**From a website.** `make scrape` walks a documentation site and writes one
Markdown document into `md/`. No model is involved, so the result is
deterministic, and the fetched HTML is cached — see
[web2md/README.md](web2md/README.md).

## How the agent knows what to do

The instructions come in two parts. `AGENTS.md` holds what every task must
respect: the OKF conventions, the directories the agent may write to, and the
rule that `SPEC.md` outranks both. Each task's procedure lives in a skill of its
own. Task skill today: `compile-okf`. Tool skills: `inspect-md`, `inspect-okf`,
`size-okf`, `merkle-okf` — a tool gets a skill, not an `AGENTS.md` section. The
sandbox also installs the `context7-docs` skill via `@upstash/context7-pi`
(library docs lookups). A new task gets a new directory rather than more rules in
`AGENTS.md`.

A skill is a directory holding a `SKILL.md` — YAML frontmatter with a `name` and
`description`, then the instructions, plus any scripts it needs. Pi picks skills
up from `~/.pi/agent/skills/`.

The kit is `pi/`, and the config it carries lives in `pi/files/home/.pi/agent/`.
That config is copied into the sandbox when the kit is built, not mounted, so an
edit reaches Pi on the next fresh sandbox — which `make wiki` always builds.
[pi/README.md](pi/README.md) covers the model and provider settings.

## Linting the wiki

[okf-lint](https://github.com/thisismydesign/okf-lint) checks the wiki against
the spec. Rules live in `okf/.okflintrc.json`, tracked and un-ignored by name so
it survives the `okf/*` rule in `.gitignore`.

The sandbox installs okf-lint at a pinned version, and the `compile-okf` skill
wraps it in `scripts/lint-okf.sh`. The agent lints its own output and fixes what
the linter reports before it finishes. On the host, `make lint-okf` runs the
same tool through `pnpm dlx`. It sits outside `make lint` and outside CI because
`okf/` is generated.

## Development

```bash
make lint                # markdownlint, jq, yamllint, shellcheck, cspell, ruff
make validate            # check pi/spec.yaml against the Sandbox Kit schema
make test-web2md         # pytest, the web2md scraper suite
make test-clis           # pytest, the four host CLI suites
make install-clis        # install the four host CLIs onto PATH
make test-sandbox        # check the sandbox has the tools, config and key it promises
make lint-okf            # lint the generated wiki
```

markdownlint needs `brew install markdownlint-cli2`; yamllint and ruff run via
`uv tool run` and cspell via `npx`, so none of them needs a separate install.

Touch anything under `pi/` or `scripts/*.sh` and run `make validate` before you
call the job done. It checks the kit spec against the schema bundled in your
`sbx` binary, and needs no Docker, no login and no network. CI runs the same
check in its `validate-kit` job, so catching a break locally saves a red build.
The current kit requires sbx 0.38.0 or newer.

`make test-sandbox` asks the other question: does the sandbox actually have
every tool `pi/spec.yaml` installs, the agent config copied in from
`pi/files/`, and a proxy-managed key? It needs an `sbx login` session. Like
`./scripts/bash.sh` below it reuses the sandbox — fast, and nothing a compile
left behind is lost — and only builds one if none exists. That also means it
tests the sandbox you have, which may be older than your last `pi/` edit. To
check the current kit from scratch, throw the sandbox away first with
`sbx rm --force md2okf`; building the next one takes minutes.

To look inside the sandbox, or to chat with Pi against the mounted workspace:

```bash
./scripts/bash.sh   # interactive shell; reuses the sandbox and whatever a run left behind
./scripts/pi.sh     # interactive Pi in the same reused sandbox
```

Once a sandbox exists, this should print `proxy-managed` rather than your key:

```bash
sbx exec md2okf -- sh -lc 'echo "$OPENROUTER_API_KEY"'
```

Python tooling is thin. There is no project at the repo root: `pdf2md/`,
`web2md/`, `scripts/inspectmd/`, `scripts/inspectokf/`, `scripts/sizeokf/`, and
`scripts/merkleokf/` are independent uv projects, each with its own
`pyproject.toml` and (where needed) `uv.lock`, and nothing shared between them.
`pdf2md/` exists only to give `marker` a pinned venv; `web2md/` owns the
scraper's dependencies and its pytest/ruff config; `scripts/inspectmd/`,
`scripts/inspectokf/`, `scripts/sizeokf/` and `scripts/merkleokf/` are
installable stdlib-only CLIs with their own ruff and pytest. So the heavy
dependencies (marker-pdf, torch) cannot reach the lint or test jobs at all,
rather than being excluded by flag.

`ruff` and `yamllint` belong to neither project; `make lint` runs them
ephemerally at a pinned version with `uv tool run`, and checks each tracked
subproject in turn — a new subproject carries its own `[tool.ruff]` and needs
no Makefile change.
