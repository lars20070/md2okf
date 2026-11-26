# kits/pi

The Docker Sandbox kit that runs Pi: a Sandbox Kit schema v3 **workload**, the
whole sandbox, in two files. `md2okf-pi.yaml`, the descriptor, declares what
the sandbox needs from the host: the network allowlist per phase, the
credentials, and the install hooks for the linters and the Context7 package.
`md2okf-pi.dockerfile`, the recipe, builds the image: Docker's Pi image, pinned
by digest (see [Bumping Pi](#bumping-pi)), plus the GitHub MCP server and the
`mq` and `okfctl` release binaries, each checked against a pinned SHA-256, and
Pi's config. Everything under `files/home/` lands in the agent's home, so
`files/home/.pi/agent/` becomes Pi's config directory: `AGENTS.md`,
`settings.json`, `models.json`, `mcp.json` and `skills/`. `AGENTS.md` carries
the whole contract, the sandbox layout and the installed tools included; the kit
declares no `agent-context` of its own.

Config is built in, not mounted, so an edit reaches Pi on the next fresh
sandbox — which `md2okf` builds when the kit changes, or on `--fresh`.

The base image starts an in-sandbox Docker engine through a v2 label. Nothing
in md2okf uses Docker inside Pi, so the kit declares no `dockerd@1` and the
recipe turns the label off.

## Bumping Pi

Pi is not installed by a setup step. It comes with Docker's own Pi image,
`docker.io/sbx/pi-image`
([`docker/sbx-kits-contrib`](https://github.com/docker/sbx-kits-contrib/tree/main/pi)),
which the recipe's `FROM` pins by index digest. Since 1.0.1 Pi ships no lockfile, so
npm no longer pins its dependencies; the image resolved them when Docker built
it, and the digest freezes that result, together with the `shell-docker`
template beneath it, for both architectures at once. Template fixes therefore
reach this kit only with a new digest.

The tag is rebuilt nightly against Pi's newest release, so read the version out
of both platform images before pinning. This reads Pi's `package.json` without
running either image, so it needs no CPU emulation, only a running Docker engine:

```bash
docker buildx imagetools inspect docker.io/sbx/pi-image:latest   # note the top "Digest:"
D=sha256:<index digest>
for p in linux/amd64 linux/arm64; do
  c=$(docker create --platform "$p" "docker.io/sbx/pi-image@$D")
  docker cp "$c:/usr/local/share/npm-global/lib/node_modules/@earendil-works/pi-coding-agent/package.json" - \
    | tar -xO | jq -r '"\(.name) \(.version)"'
  docker rm "$c" >/dev/null
done
```

Pin the index digest only if both platforms print the version you want. Then:

1. Put it in the `FROM` line of `md2okf-pi.dockerfile`.
2. Set `EXPECTED_PI_VERSION` in `tests/test-sandbox-guest-pi.sh` to match.
3. Read Pi's changelog for the versions in between, with an eye on
   `--mode json` (which `src/md2okf/protocols/pi.py` parses) and the session
   format (which the `read-pi-session-traces` skill reads). Update that skill's
   pin.
4. Run `sbx rm --force md2okf-pi && make test-sandbox AGENT=pi`.

## Model configuration

The `openrouter` entry in `files/home/.pi/agent/models.json` names the provider
and stops there. It carries no `models` array, which is deliberate, and JSON has
nowhere to put the reason. So here it is. (The `litellm` entry alongside it does
carry one, for the mirror-image reason — see
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
sbx exec md2okf-pi -- pi --list-models deepseek
```

To change a single field of a catalogue model, use `modelOverrides`, not a
`models` entry. Before switching models, check the new one's output limit the
same way. The figures are not fixed: since Pi 1.2.0 the OpenRouter list can
come from your key's own model list, and Pi's catalogue moves with each
release. Pi 0.86's capped `deepseek/deepseek-v4-flash` at 4.1K output, too
little for this work; 1.4.0's lists 943.7K.

## Using another provider

`models.json` carries a second provider, `litellm`, switched off by default. It
points at a LiteLLM gateway, or at anything else that speaks the OpenAI
protocol: `api: "openai-completions"` is the wire format OpenRouter uses too.
The example model is `gemini-3.1-pro-preview`.

Switching to it takes four steps.

1. **Name the gateway.** In `files/home/.pi/agent/models.json`, put your
   gateway's URL in `baseUrl` in place of the `litellm.example.com` placeholder,
   and the model you want in `models`.
2. **Choose it.** In `files/home/.pi/agent/settings.json`, set
   `"defaultProvider": "litellm"` and `"defaultModel"` to the model id. Pi needs
   both, and both must match an entry in `models.json`.
3. **Open the road.** Add the gateway's host to the `runtime` allow list of the
   `network-policy@1` entry in `md2okf-pi.yaml`, and give it a `credential@1`
   entry like the OpenRouter one: `header: Authorization`,
   `format: "Bearer %s"`, which is how LiteLLM authenticates too. Keep it
   `optional: true` unless a missing key should stop the sandbox from being
   created at all.
4. **Hand over the key**, then run `md2okf md/`, which builds the kit and
   copies the config in.

```bash
sbx secret set-custom --sandbox md2okf-pi --host <your-gateway-host> \
  --env LITELLM_API_KEY --value "$LITELLM_API_KEY"
```

Only `set-custom` here. Plain `set` knows a fixed list of built-in services;
OpenRouter is on it, a gateway is not. sbx still marks `set-custom`
experimental. It has no stdin form either, so the key is visible to anything
that can list processes for as long as the command runs. Reading it from an
exported variable, as above, at least keeps it out of your shell history.

## Context7 docs extension

The kit installs `@upstash/context7-pi` (pinned in an install hook and listed
under `packages` in `settings.json`). That is a native Pi package — not MCP —
and registers `resolve-library-id`, `query-docs`, and the `context7-docs` skill.
Egress to `context7.com` is allowlisted in `md2okf-pi.yaml`.

### Why the litellm entry spells out its numbers

Pi ships a catalogue of 33 providers. OpenRouter is one of them; LiteLLM is not.
The advice above about the `models` array therefore turns on its head here.
Leave the array out for `openrouter` and the catalogue fills in real figures. Do
the same for `litellm` and there is nothing to fill in, so Pi falls back to 128K
of context, 16,384 output tokens and no reasoning.

That output cap is shared, which makes it tighter than it looks. Thinking tokens
come out of the same budget as the answer, so a small cap can buy a lot of
thought and no words at all: the gateway returns 200 and an empty `choices`
array. Hence the explicit numbers in the entry. `modelOverrides` is no help,
because it patches ids Pi already knows and drops the rest without a word.

Two of those numbers are guesses. `cost` feeds Pi's own usage tracking and says
nothing about what your gateway charges. `thinkingLevelMap` folds Pi's seven
thinking levels onto `low`, `medium` and `high`, which a gateway fronting Gemini
takes as `reasoning_effort`. If yours rejects a level, change the map, or set
`"reasoning": false` and Pi will stop sending one.

### Two things to check before you debug the wrong one

First, that the provider is there at all:

```bash
sbx exec md2okf-pi -- pi --list-models litellm
```

The filter matches the provider name, so this lists your models and nothing
else. An empty list means the key never reached Pi, which drops a provider whose
`apiKey` resolves to nothing without an error or a warning. Beware that the
listing and the lookup disagree: Pi will still choose the model when it runs,
because the lookup that resolves `settings.json` pays no attention to keys. So a
missing key shows up not here but at the first request.

Second, that the gateway is reachable. A host that `permissions.network` allows
may still be out of reach, because lifting sbx's own policy does not give the
microVM a route to it. Ask from inside, not from your shell:

```bash
sbx exec md2okf-pi -- curl -sS -o /dev/null -w '%{http_code}\n' \
  https://<your-gateway-host>/v1/models
```

`200` or `401` means the path works, `401` being a credential problem rather
than a routing one. A hang or a DNS failure means it does not.

## GitHub MCP server

The kit runs GitHub's MCP server, `github-mcp-server` (pinned in the recipe by
version and SHA-256), locally over stdio. It is configured in
`files/home/.pi/agent/mcp.json`, and authenticates through an optional
`github` credential that `md2okf-pi.yaml` declares. The credential's variable
is `GITHUB_TOKEN`, which `gh` reads and `mcp.json` hands to the server as
`GITHUB_PERSONAL_ACCESS_TOKEN`.

### What a bound token can reach

Binding the `github` secret authorizes **every process in the `md2okf-pi`
sandbox, compile turns included**. The sbx proxy injects the token at the
network level, on every request to `api.github.com` and `github.com`, and every
compile turn has `bash`. A source document that steers a compile turn could
therefore make authenticated GitHub requests with `curl`, `gh` or `git`, with
everything the token allows. A compile runs Pi with `--no-mcp`, which keeps the
`mcp__github__*` *tools* out of it, but that is not a credential boundary.

So bind only a token you would accept that from: a
[fine-grained token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens#creating-a-fine-grained-personal-access-token),
read-only, and scoped to just the repositories you need. Leave the secret
unbound and GitHub stays unauthenticated; nothing else in md2okf needs it.

### Setting it up

Pass the token on stdin, before the sandbox is created:

```bash
# From a secret manager (1Password here)...
op read 'op://Private/md2okf GitHub/token' | sbx secret set github
# ...or from a variable you exported for the purpose
printf '%s\n' "$MD2OKF_GITHUB_TOKEN" | sbx secret set github

sbx rm --force md2okf-pi   # credentials bind at create; the next run rebuilds
```

Never use `-t "$(…)"`, which puts the token in process arguments.
`gh auth token | sbx secret set github` is convenient, but it hands over the
GitHub CLI's own credential with whatever scopes it already has, which is
rarely least privilege. A service secret is global by default, so it also
reaches any other sandbox whose kit declares the `github` service.

### Using it

The server's tools are deferred: nothing declares them to the model until
`tool_search` loads the ones a task needs, which `settings.json` turns on with
`"defaultTools": ["+tool_search"]`. `autoEnableCodemode` is off, so connecting
the server does not switch codemode on by itself. All of this applies to
`md2okf --agent` only. A compile runs with `--no-mcp --tools -tool_search`, so
it has the same tools it had on Pi 0.86. GitHub MCP results are not inspected
or filtered: treat them as untrusted, like a source document.

A project's own `.pi/mcp.json` can add MCP servers or override the kit's (a
stdio server is an arbitrary command) and can switch `autoEnableCodemode` back
on. Pi loads it only for a trusted project. Compile turns run in JSON mode,
where the default `defaultProjectTrust: "ask"` skips it. In `md2okf --agent`,
Pi asks first. The wiki is written by compile turns, so decline unless you put
that file there yourself.

### Diagnosing it

```bash
sbx exec md2okf-pi -- pi mcp list
```

Or run `/mcp` inside `md2okf --agent`. sbx sets `GITHUB_TOKEN` in every
process of the sandbox, a plain `sbx exec` included, so the listing sees what a
real session sees.

`make test-sandbox AGENT=pi` runs the authenticated checks (`gh auth status`,
the server connected, one read-only `get_me` call) when a secret is bound, and
reports them skipped when none is. Set `REQUIRE_GITHUB=1` to turn that skip
into a failure, which is how a release certifies this path.

## Fullscreen TUI

Since Pi 1.0.0 the TUI runs fullscreen by default, which affects
`md2okf --agent` only. To keep the terminal's own scrollback, set
`"tuiMode": "regular"` in `files/home/.pi/agent/settings.json`; the kit leaves
it at Pi's default.
