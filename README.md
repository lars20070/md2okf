# md2okf

Drop a folder of Markdown files into `md/`, run `make wiki-sandbox`, and the Pi
coding agent writes you an OKF knowledge base in `okf/`. It takes one source
document per run and folds it into the wiki: a page per topic, an index in every
directory, links between them and a log of what each run changed.

OKF, the Open Knowledge Format, is a tree of Markdown files with YAML
frontmatter and nothing else. No schema registry, no server, no tooling you have
to install. `SPEC.md` at the repo root is the revision this wiki is built
against, and the agent reads it at the start of every run, so the spec has the
last word over anything written here.

## Compile a wiki

### Set up, once

```bash
brew install docker/tap/sbx
```

sbx keeps the OpenRouter key out of the virtual machine. It holds the real
string on the host and swaps it into requests at its proxy, so inside the
sandbox `$OPENROUTER_API_KEY` reads `proxy-managed`. Set it twice:

```bash
export OPENROUTER_API_KEY=sk-or-...

echo "$OPENROUTER_API_KEY" | sbx secret set -g openrouter

# And again as a custom secret, to work around a known sbx bug:
# https://github.com/docker/sbx-releases/issues/25
sbx secret set-custom pi-kit \
  --host openrouter.ai \
  --env OPENROUTER_API_KEY \
  --value "$OPENROUTER_API_KEY"
```

`pi-kit` here is the kit's name, which comes from `pi/sandbox/spec.yaml`.

### Run it

Put your Markdown files in `md/`, then:

```bash
make wiki-sandbox
```

The driver throws the old sandbox away and builds a fresh one, so the current
kit and secrets apply, then runs Pi once for each `md/*.md` file. Both `md/` and
`okf/` are gitignored, so your sources and the wiki stay out of the repo. Only
`okf/.okflintrc.json` is tracked.

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
`/glossary/verb.md` rather than `glossary/verb.md`. The root `index.md` declares
the spec version the agent read. Pages are updated in place instead of being
duplicated, so compiling the same document twice is safe.

## How the agent knows what to do

The instructions come in two parts. `AGENTS.md` holds what every task must
respect: the OKF conventions, the directories the agent may write to, and the
rule that `SPEC.md` outranks both. Each task's procedure lives in a skill of its
own. There is one today, `compile-wiki`, and a new task gets a new directory
rather than more rules in `AGENTS.md`.

A skill is a directory holding a `SKILL.md`, which is YAML frontmatter with a
`name` and `description` followed by the instructions, plus any scripts it
needs. Pi picks skills up from `~/.pi/agent/skills/`.

Both drivers name the path to `SKILL.md` in the prompt rather than calling
`/skill:compile-wiki`. `pi -p` passes a prompt through as typed and never
expands a slash command.

## The two runtimes

Either runtime compiles the same wiki. Reach for the sandbox: it lints its own
output, and it keeps the API key out of the virtual machine.

| Runtime | Directory | Pi config | Command |
| --- | --- | --- | --- |
| Docker Sandbox (sbx) | `pi/sandbox/` | `pi/sandbox/files/home/.pi/agent/` | `make wiki-sandbox` |
| Docker Compose | `pi/container/` | `pi/container/agent/` | `make wiki-container` |

Each runtime carries its own copy of the Pi config: `AGENTS.md`,
`settings.json`, `models.json` and `skills/`. Neither copy is generated from the
other. When a change belongs in both, make it twice, by hand. They share no
code, so deleting one runtime leaves the other untouched.

The copies differ where the runtimes differ.

| | Sandbox | Container |
| --- | --- | --- |
| Skill source | `pi/sandbox/files/home/.pi/agent/skills/` | `pi/container/agent/skills/` |
| Delivery | copied in when the kit is built | bind-mounted by `compose.yaml` |
| Edits take effect | on a fresh sandbox, which `make wiki-sandbox` always builds | on the next run, no rebuild |
| `bash` tool | yes | no, excluded by `-xt bash` |
| Lint step | yes, via `scripts/lint-okf.sh` | none |
| Update log | `##` date headings | flat bullets, no dates |
| API key | proxy-managed by sbx | `OPENROUTER_API_KEY` in your shell |
| `SPEC.md` | already in the workspace | copied into the image |

Stay with one runtime for a given wiki. Their logs are shaped differently, and
mixing the two leaves `okf/log.md` half in one format and half in the other.

### The container runtime

It needs Docker and the key in your own shell:

```bash
export OPENROUTER_API_KEY=sk-or-...
make wiki-container

# ...or point it at a different source folder:
./scripts/compile-wiki-container.sh md/other-books
```

`scripts/compile-wiki-container.sh` runs Pi with `-xt bash`, which takes the
bash tool away, and the rest of what marks this runtime out follows from that.
The agent cannot run `okf-lint`, so its skill has no lint step. It cannot run
`date`, so its log carries no dates, a guessed date being worse than none. It
keeps `read`, and that is what lets it open `SKILL.md` and `SPEC.md`. Never add
`read` to that denylist, or Pi stops advertising the skill in the system prompt
at all.

### Model configuration, sandbox only

The `openrouter` entry in `pi/sandbox/files/home/.pi/agent/models.json` names the
provider and stops there. It carries no `models` array, which is deliberate, and
JSON has nowhere to put the reason. So here it is. (The `litellm` entry alongside
it does carry one, for a reason that is the mirror image of this — see
[Using another provider](#using-another-provider).)

Pi merges a custom `models` entry by `id`, and that entry replaces the built-in
catalogue entry it matches. Name a model Pi already knows, such as `{"id":
"deepseek/deepseek-v4-pro", "name": "…"}`, and you throw its real metadata away.
What you get instead are Pi's defaults: 128K context, 16,384 max output tokens,
no reasoning. That output cap cuts a long `write` call off mid-argument and
takes the run down with it. Leave the array out and the catalogue values apply:
1M context, 384K max output.

Check after any change:

```bash
sbx exec pi-kit -- pi --list-models deepseek
```

To change a single field of a catalogue model, use `modelOverrides`, not a
`models` entry. And whatever else you do, avoid `deepseek/deepseek-v4-flash` for
this work: the catalogue caps its output at 4.1K.

### Using another provider

Both `models.json` copies also carry a `litellm` provider, switched off by
default. It points at a LiteLLM gateway — or at anything else speaking the OpenAI
protocol, `api: "openai-completions"` being the same wire format OpenRouter uses
— and it is there mostly as a worked example of what a provider Pi does *not*
ship needs.

Which is the part worth reading before copying it. The advice above inverts here.
`openrouter` is in Pi's catalogue, so omitting `models` inherits real metadata.
`litellm` is not, so there is nothing to inherit and the fallback applies instead:
128K context, 16,384 max output, no reasoning — the same truncation trap, reached
from the opposite direction. Hence the explicit entry, and hence `modelOverrides`
being no use here: it patches ids Pi already knows and ignores the rest silently.

To switch to it:

1. Put your gateway's URL in `baseUrl`, replacing the `litellm.example.com`
   placeholder, and the model you want in `models` — `gemini-3.1-pro-preview` is
   there as an example. Each runtime keeps its own copy, so edit both.
2. Point `settings.json` at it: `"defaultProvider": "litellm"` and
   `"defaultModel": "<your model id>"`. Both copies again.
3. Export `LITELLM_API_KEY`. The container runtime still fails fast on
   `OPENROUTER_API_KEY`, so give that one any value until you drop the check.
4. For the sandbox, add the gateway's host to `caps.network.allow` in
   `pi/sandbox/spec.yaml` and give it a `credentials` entry mirroring the
   OpenRouter one — `header: Authorization`, `format: "Bearer %s"`, which is how
   LiteLLM authenticates too — then register the secret:

```bash
sbx secret set-custom pi-kit --host <your-gateway-host> \
  --env LITELLM_API_KEY --value "$LITELLM_API_KEY"
```

Only `set-custom` here, and no `sbx secret set -g` line to go with it: `set`
knows a fixed list of built-in services — `openrouter` is on it, a gateway is
not — and `set-custom` is what covers everything else. It has no stdin form
either, so the value is visible to anything that can list processes for as long
as the command runs; sbx labels `--value` "less secure" for that reason. Reading
it from an exported variable, as above, keeps it out of shell history at least.

Two fields in the example entry are estimates rather than measured facts. `cost`
feeds usage tracking only and says nothing about what a gateway charges. And
`thinkingLevelMap` folds Pi's seven thinking levels onto `low`, `medium` and
`high`, those being what a reasoning-effort field reliably accepts through an
OpenAI-compatible shim; if yours rejects a level, correct it there or set
`"reasoning": false` to stop Pi sending one at all.

A gateway on a private network can be allowed by `caps.network` and still be
unreachable — that lifts sbx's own policy without giving the microVM a route to
it. Check from inside the runtime rather than from your shell:

```bash
sbx exec pi-kit -- curl -sS -o /dev/null -w '%{http_code}\n' \
  https://<your-gateway-host>/v1/models
```

`200` or `401` means the network path works, `401` being a credential problem
rather than a routing one. A hang or a DNS failure means it does not.

## Linting the wiki

[okf-lint](https://github.com/thisismydesign/okf-lint) checks the wiki against
the spec. Rules live in `okf/.okflintrc.json`, which is tracked and un-ignored
by name so it survives the `okf/*` rule in `.gitignore`.

- **On the host**, `make lint-okf` runs it through `pnpm dlx`, so there is
  nothing to install. `okf/` is generated and gitignored, which is why this sits
  outside `make lint` and outside CI, and why neither driver calls it.
- **In the sandbox**, the kit installs okf-lint at a pinned `OKF_LINT_VERSION`
  (`pi/sandbox/spec.yaml`) and the `compile-wiki` skill wraps it in
  `scripts/lint-okf.sh`. The agent lints its own output and fixes what the
  linter reports before it finishes.
- **In the container**, okf-lint is installed too, pinned independently by
  `pi/container/Dockerfile` with no cross-check against the sandbox, but the
  agent is never told to use it, because it cannot run a binary. `make lint-okf`
  on the host takes its place.

## Development

```bash
make lint       # markdownlint, shellcheck, ruff, hadolint
make validate   # check pi/sandbox/spec.yaml against the Sandbox Kit schema
make lint-okf   # lint the generated wiki
```

Touch anything under `pi/` or `scripts/` and run `make validate` before you call
the job done. It checks the kit spec against the schema bundled in your `sbx`
binary, and needs no Docker, no login and no network. CI runs the same check in
its `validate-kit` job, so catching a break locally saves a red build.

To look inside either runtime:

```bash
./scripts/bash-sandbox.sh    # reuses the sandbox and whatever a run left behind
./scripts/bash-container.sh  # a throwaway container shell
```

Once a sandbox exists, this should print `proxy-managed` rather than your key:

```bash
sbx exec pi-kit -- sh -lc 'echo "$OPENROUTER_API_KEY"'
```

Python tooling is thin. A `dev` dependency group holds ruff and nothing else,
and there is no first-party package yet. When real Python code lands, adopt
`src/md2okf/` and `tests/` with pytest, add a `make test` target and switch on
the reserved `test` job in CI.

## Starting from a PDF

`md/` wants clean, structured Markdown, and a PDF is rarely that. `marker` turns
one into the other with the help of a language model, either a local Ollama
model or a cloud model through OpenRouter. Expect to check its output:
`prettier`, `markdownlint-cli2` and `cspell` catch most of what it gets wrong,
but none of this runs unattended. [pdf2md/README.md](pdf2md/README.md) has the
commands.
