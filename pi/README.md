# pi

The Docker Sandbox kit that runs Pi. `spec.yaml` declares the image, the network
allowlist, the credentials and the two pinned installs. Everything under
`files/home/` is copied into the sandbox at `~/`, so `files/home/.pi/agent/`
becomes Pi's config directory: `AGENTS.md`, `settings.json`, `models.json` and
`skills/`.

The `files/` level is fixed by the Sandbox Kit schema. It cannot be renamed or
moved.

Config is copied in when the kit is built, not mounted, so an edit reaches Pi on
the next fresh sandbox — which `make wiki` always builds.

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
sbx exec md2okf -- pi --list-models deepseek
```

To change a single field of a catalogue model, use `modelOverrides`, not a
`models` entry. And avoid `deepseek/deepseek-v4-flash` for this work: the
catalogue caps its output at 4.1K.

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
3. **Open the road.** Add the gateway's host to `permissions.network.allow` in
   `spec.yaml`, and give it a `credentials` entry like the OpenRouter one:
   `header: Authorization`, `format: "Bearer %s"`, which is how LiteLLM
   authenticates too.
4. **Hand over the key**, then run `make wiki`, which builds a fresh kit and
   copies the config in.

```bash
sbx secret set-custom --sandbox md2okf --host <your-gateway-host> \
  --env LITELLM_API_KEY --value "$LITELLM_API_KEY"
```

Only `set-custom` here. Plain `set` knows a fixed list of built-in services;
OpenRouter is on it, a gateway is not. sbx still marks `set-custom`
experimental. It has no stdin form either, so the key is visible to anything
that can list processes for as long as the command runs. Reading it from an
exported variable, as above, at least keeps it out of your shell history.

## Context7 docs extension

The kit installs `@upstash/context7-pi` (pinned in `setup.install` and listed
under `packages` in `settings.json`). That is a native Pi package — not MCP —
and registers `resolve-library-id`, `query-docs`, and the `context7-docs` skill.
Egress to `context7.com` is allowlisted in `spec.yaml`.

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
sbx exec md2okf -- pi --list-models litellm
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
sbx exec md2okf -- curl -sS -o /dev/null -w '%{http_code}\n' \
  https://<your-gateway-host>/v1/models
```

`200` or `401` means the path works, `401` being a credential problem rather
than a routing one. A hang or a DNS failure means it does not.
