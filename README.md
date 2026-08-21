# md2okf

[![CI](https://github.com/lars20070/md2okf/actions/workflows/ci.yml/badge.svg)](https://github.com/lars20070/md2okf/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Compile Markdown documents into an OKF knowledge base with a coding agent.

Drop Markdown files into `md/`, run `make wiki`, and the [Pi coding
agent](https://pi.dev) writes a wiki into `okf/`: a page per topic, an index in
every directory, links between them, and a log of what each run changed. OKF,
the [Open Knowledge
Format](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf),
is a tree of Markdown files with YAML frontmatter and nothing else — no schema
registry, no server, nothing to install. The agent takes one source document per
run and folds it into the wiki already on disk, so documents accumulate rather
than overwrite. [SPEC.md](SPEC.md) is the OKF specification the wiki is built
against; the agent reads it at the start of every run, and it outranks any
other instructions.

## Contents

- [Requirements](#requirements)
- [Quickstart](#quickstart)
- [How it works](#how-it-works)
- [What lands in okf/](#what-lands-in-okf)
- [Getting Markdown in](#getting-markdown-in)
- [Set up the OpenRouter key](#set-up-the-openrouter-key)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [Getting help](#getting-help)
- [License](#license)

## Requirements

- macOS with [Homebrew](https://brew.sh), or
  Linux with [KVM](https://en.wikipedia.org/wiki/Kernel-based_Virtual_Machine). Docker Desktop is not
  required.
- [sbx](https://github.com/docker/sbx-releases) 0.38.0 or newer — the Docker
  Sandboxes CLI. The kit under `pi/` uses the finalized kit-spec v2 grammar,
  which older releases reject.
- An [OpenRouter](https://openrouter.ai) API key, which pays for the model the
  agent runs on.
- `make`, `git`, and `jq`, which the compile driver uses on the host.

## Quickstart

Install the sandbox CLI and sign in.

[macOS:](https://docs.docker.com/ai/sandboxes/install/#install-on-macos)

```bash
brew trust docker/tap
brew install docker/tap/sbx
sbx login
ln -s /path_to_sbxclaude_repo/scripts/sbxclaude ~/.local/bin/sbxclaude
```

[Linux:](https://docs.docker.com/ai/sandboxes/install/#linux)

```bash
curl -fsSL https://get.docker.com | sudo REPO_ONLY=1 sh
sudo apt-get install docker-sbx
sudo usermod -aG kvm "$USER" && newgrp kvm
sbx login
ln -s /path_to_sbxclaude_repo/scripts/sbxclaude ~/.local/bin/sbxclaude
```

Hand sbx your OpenRouter key once — see [Set up the OpenRouter
key](#set-up-the-openrouter-key). Then put your Markdown in `md/` and compile:

```bash
cp my-document.md md/
make wiki
```

Each document gets its own agent run, and each run reports the wiki's root hash
before and after (tool calls and agent prose stream in between):

```text
Compiling document md/my-document.md (iteration 1)
7f3c1a9d4e02 -> b481d05c6a17
Compiling document md/my-document.md (iteration 2)
b481d05c6a17 -> b481d05c6a17
```

The wiki lands in `okf/`, which is gitignored apart from `okf/.okflintrc.json`,
so the generated pages stay out of the repo. `md/` is tracked and ships with
sample documents, so `make wiki` has something to compile straight away.

## How it works

A shell driver on the host runs the agent inside a microVM, repeatedly, until a
hash of the output stops moving. The host drives; everything else happens inside
the sandbox.

`make wiki` throws the old sandbox away and builds a fresh one, so the current
kit — the `pi/` directory that declares the sandbox image, its network
allowlist and the agent's config — always applies. It then runs the agent once
per `md/*.md` file, re-running the same document (a *Ralph loop*) until
`merkleokf --nolog -L 0` reports an unchanged wiki root hash. `merkleokf` prints
a Merkle hash tree, one hash per file and per directory, so a change to any page
moves the root hash and an unchanged root means the run added nothing. The loop
is capped by `RALPH_MAX` (default 10). The agent's only writable output is
`okf/`, [okf-lint](https://github.com/thisismydesign/okf-lint) must pass before
it finishes, and `SPEC.md` outranks every instruction file. Each run streams
tool names and assistant text as it goes, and writes a session transcript under
`logs/sessions/`.

<!-- cspell:disable -->

```mermaid
flowchart LR
  MD["md/*.md<br/>source documents"]
  DRV["scripts/compile-okf.sh<br/>make wiki"]
  KIT["pi/spec.yaml<br/>+ pi/files/"]
  SPEC["SPEC.md"]
  OKF["okf/<br/>the wiki"]

  subgraph VM["sbx microVM"]
    PI["Pi agent with<br/>compile-okf skill"]
    TOOLS["inspectmd<br/>inspectokf<br/>sizeokf<br/>merkleokf"]
    LINT["okf-lint"]
  end

  KIT ~~~ SPEC
  MD --> DRV
  KIT -->|"builds"| VM
  DRV -->|"sbx exec"| PI
  SPEC -.->|"read first, outranks all"| PI
  PI -->|"reads"| MD
  PI -->|"writes"| OKF
  TOOLS -.->|"survey + verify"| PI
  PI --> LINT
  LINT -.->|"must pass"| OKF
```

<!-- cspell:enable -->

### Repository layout

| Path | Description |
| --- | --- |
| `md/` | source documents, one agent run each |
| `okf/` | the generated wiki |
| `Makefile` | every task worth running; `make wiki` compiles |
| `scripts/` | what the Makefile or the agent call — compile, sandbox shell, sbx kit validation, and the four helper CLIs (`inspectmd`, `inspectokf`, `sizeokf`, `merkleokf`) |
| `pi/` | what the scripts run: the Docker Sandbox kit and the config it carries |
| `SPEC.md` | the [OKF specification](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) the wiki is built against |
| `AGENTS.md` | instructions for coding agents working *on this repo*, not for Pi |
| `pdf2md/` | optional: converts a PDF into `md` |
| `web2md/` | optional: scrapes a documentation site into `md` |

## What lands in okf/

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
the spec version the agent reads. Pages are updated in place, not duplicated, so
compiling the same document twice is safe.

## Getting Markdown in

`md/` wants clean, structured Markdown, and a source document is rarely that.
Two helpers produce it. Both are optional, and neither is part of `make wiki`.

**From a PDF.** `marker` converts one with the help of a language model, either
a local Ollama model or a cloud model through OpenRouter. Expect to check the
output, and run the step by hand — see
[the pdf2md guide](pdf2md/README.md).

**From a website.** `make scrape` walks a documentation site and writes one
Markdown document into `md/`. No model is involved, so the result is
deterministic, and the fetched HTML is cached — see
[the web2md guide](web2md/README.md).

## Set up the OpenRouter key

sbx keeps the key out of the virtual machine. It holds the real string on the
host and swaps it into requests at its proxy, so inside the sandbox
`$OPENROUTER_API_KEY` reads `proxy-managed`. Set it twice:

```bash
export OPENROUTER_API_KEY=sk-or-...

echo "$OPENROUTER_API_KEY" | sbx secret set openrouter

# And again as a custom secret, to work around a known sbx bug:
# https://github.com/docker/sbx-releases/issues/25
sbx secret set-custom --sandbox md2okf \
  --host openrouter.ai \
  --env OPENROUTER_API_KEY \
  --value "$OPENROUTER_API_KEY"
```

`md2okf` is the kit's name, which comes from `pi/spec.yaml`. `make wiki` reads
the key from `sbx secret`, never from your shell environment. To point the agent
at a different provider, see [the pi kit guide](pi/README.md).

## Troubleshooting

**`sbx` reports unknown fields from `pi/spec.yaml`.** Your sbx is older than
0.38.0 and does not know the kit-spec v2 grammar. Run `brew upgrade sbx`.

**A runtime command fails to authenticate.** `make wiki`, `make test-sandbox`,
`./scripts/bash.sh` and `./scripts/pi.sh` need an active `sbx login` session.

**`Error: Ralph loop hit 10 iterations`.** The wiki root hash kept changing.
Raise the cap for one run with `RALPH_MAX=20 make wiki`, or read
`logs/sessions/` to see what the agent was doing.

## Development

Lint, tests, the sandbox checks, the helper CLIs and the per-subproject layout
are covered in [the contributing guide](CONTRIBUTING.md). The short version:
`make lint` checks the source tree, `make validate` checks the sandbox kit spec,
and CI runs both on every pull request. There is no package to install —
`make wiki` is the entry point, and `make install-clis` puts the helper CLIs on
your PATH.

## Getting help

Questions, bugs and feature requests belong in [the issue
tracker](https://github.com/lars20070/md2okf/issues).

## License

Released under the [MIT License](LICENSE).
