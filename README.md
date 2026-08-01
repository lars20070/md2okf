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

Both `models.json` copies carry a second provider, `litellm`, switched off by
default. It points at a LiteLLM gateway, or at anything else that speaks the
OpenAI protocol: `api: "openai-completions"` is the wire format OpenRouter uses
too. The example model is `gemini-3.1-pro-preview`.

Switching the sandbox to it takes four steps.

1. **Name the gateway.** In `pi/sandbox/files/home/.pi/agent/models.json`, put
   your gateway's URL in `baseUrl` in place of the `litellm.example.com`
   placeholder, and the model you want in `models`.
2. **Choose it.** In `pi/sandbox/files/home/.pi/agent/settings.json`, set
   `"defaultProvider": "litellm"` and `"defaultModel"` to the model id. Pi needs
   both, and both must match an entry in `models.json`.
3. **Open the road.** Add the gateway's host to `caps.network.allow` in
   `pi/sandbox/spec.yaml`, and give it a `credentials` entry like the OpenRouter
   one: `header: Authorization`, `format: "Bearer %s"`, which is how LiteLLM
   authenticates too.
4. **Hand over the key**, then run `make wiki-sandbox`, which builds a fresh kit
   and copies the config in.

```bash
sbx secret set-custom pi-kit --host <your-gateway-host> \
  --env LITELLM_API_KEY --value "$LITELLM_API_KEY"
```

Only `set-custom` here. Plain `set` knows a fixed list of built-in services;
OpenRouter is on it, a gateway is not. Note that sbx still marks `set-custom`
experimental. It has no stdin form either, so the key is visible to anything
that can list processes for as long as the command runs. Reading it from an
exported variable, as above, at least keeps it out of your shell history.

#### Why this entry spells out its numbers

Pi ships a catalogue of 33 providers. OpenRouter is one of them; LiteLLM is not.
The advice above about the `models` array therefore turns on its head here.
Leave the array out for `openrouter` and the catalogue fills in real figures. Do
the same for `litellm` and there is nothing to fill in, so Pi falls back to 128K
of context, 16,384 output tokens and no reasoning.

That output cap is shared, which makes it tighter than it looks. Thinking
tokens come out of the same budget as the answer, so a small cap can buy a lot
of thought and no words at all: the gateway returns 200 and an empty `choices`
array. Hence the explicit numbers in the entry. `modelOverrides` is no help,
because it patches ids Pi already knows and drops the rest without a word.

Two of those numbers are guesses. `cost` feeds Pi's own usage tracking and says
nothing about what your gateway charges. `thinkingLevelMap` folds Pi's seven
thinking levels onto `low`, `medium` and `high`, which a gateway fronting Gemini
takes as `reasoning_effort`. If yours rejects a level, change the map, or set
`"reasoning": false` and Pi will stop sending one.

#### Two things to check before you debug the wrong one

First, that the provider is there at all:

```bash
sbx exec pi-kit -- pi --list-models litellm
```

The filter matches the provider name, so this lists your models and nothing
else. An empty list means the key never reached Pi, which drops a provider whose
`apiKey` resolves to nothing without an error or a warning. Beware that the
listing and the lookup disagree: Pi will still choose the model when it runs,
because the lookup that resolves `settings.json` pays no attention to keys. So a
missing key shows up not here but at the first request.

Second, that the gateway is reachable. A host that `caps.network` allows may
still be out of reach, because lifting sbx's own policy does not give the
microVM a route to it. Ask from inside, not from your shell:

```bash
sbx exec pi-kit -- curl -sS -o /dev/null -w '%{http_code}\n' \
  https://<your-gateway-host>/v1/models
```

`200` or `401` means the path works, `401` being a credential problem rather
than a routing one. A hang or a DNS failure means it does not.

#### The container runtime, in short

The same, minus the sandbox's plumbing. Make the first two edits in
`pi/container/agent/`, which is bind-mounted, so they land on the next run
rather than the next build. Steps 3 and 4 have no counterpart: the container has
plain bridge networking, so there is no allowlist to widen, and `compose.yaml`
passes `LITELLM_API_KEY` through from your shell.

One snag. Three checks still demand `OPENROUTER_API_KEY` — in `compose.yaml`,
`scripts/compile-wiki-container.sh` and `scripts/bash-container.sh` — so give it
any value until you drop them. To check the provider, open a throwaway shell
with `./scripts/bash-container.sh` and run `pi --list-models litellm`.

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
make test       # pytest, the web2md scraper suite
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

Python tooling is thin and split across three dependency groups: `dev` (ruff),
`test` (pytest) and `web2md` (the scraper's four runtime deps). CI installs one
group per job with `--only-group`, so neither the lint job nor the test job ever
pulls in the heavy project dependencies (marker-pdf / torch).

The only first-party Python is the web2md scraper, which follows a per-tool
layout: the module in [web2md/src/](web2md/src/), its pytest suite in
[web2md/tests/](web2md/tests/). There is no `[build-system]` and nothing is
installed — `make scrape` runs the module by path, and pytest imports it through
`pythonpath` in `pyproject.toml`. `make test` runs the suite, and CI runs the
same command in its `test` job. The suite is offline, so it needs no network and
never touches `web2md/cache/`.

## Starting from a PDF

`md/` wants clean, structured Markdown, and a PDF is rarely that. `marker` turns
one into the other with the help of a language model, either a local Ollama
model or a cloud model through OpenRouter. Expect to check its output:
`prettier`, `markdownlint-cli2` and `cspell` catch most of what it gets wrong,
but none of this runs unattended. [pdf2md/README.md](pdf2md/README.md) has the
commands.

## Starting from a website

When the source is a documentation site rather than a file, `make scrape` walks
it and writes one Markdown document into `md/`. Unlike the PDF step this is
deterministic — no model involved — and it caches the fetched HTML under
`web2md/cache/`, so re-running is cheap and `--refresh` is what goes back to the
network.

Which book it fetches and what the result is called are two constants at the top
of [web2md/src/web2md.py](web2md/src/web2md.py):

```python
SOURCE_URL = "https://developers.google.com/style"
OUTPUT_FILE = "GoogleStyleGuide.md"
```

Everything URL-shaped in the scraper is derived from `SOURCE_URL`, so retargeting
it is a one-line edit — though the HTML selectors and sanity thresholds describe
this particular book and would need revisiting.
[web2md/README.md](web2md/README.md) has the details.
