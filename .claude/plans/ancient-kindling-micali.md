# Redesign the README hero diagram

## Context

`README.md` is the landing page for `md2okf`, and the Mermaid diagram at
lines 110–134 is the only picture of the project. It has three concrete
problems:

1. **The Ralph loop is invisible.** Iterating one document until the wiki's
   Merkle root hash stops moving is the single most distinctive idea in the
   project, and the current diagram does not draw it at all.
2. **Two edges fight the layout.** `PI -->|"reads"| MD` points backwards
   against the flow (the driver hands the document forward, so this is also
   factually off), and `KIT ~~~ SPEC` is an invisible-link layout bribe that
   re-shuffles whenever GitHub bumps its Mermaid version.
3. **No visual hierarchy.** Every node is the same default grey box, so
   nothing signals what is source, what is agent, what is a gate, what is
   output. It does not read as designed.

It is also buried: at line 110 a new reader scrolls past Requirements and
Quickstart before seeing it.

A second attempt exists at `tmp/screenshot.png` (untracked — note `tmp/` is
**not** gitignored). It fixes the hierarchy problem with three labelled zones
but introduces worse ones: it is ~830×1900px, so it would push the entire
README below the fold, and it carries an empty unlabelled subgraph with no
connections.

**Outcome wanted:** one hero flowchart, promoted to the top of the README,
that a new user reads in seconds without the project being dumbed down —
professional enough to look deliberately designed.

### Decisions already taken

| Decision | Choice |
| --- | --- |
| Scope | Core loop **+ the model routing chain** — Pi → sbx egress proxy → OpenRouter hub → BYOK provider. Shows both that the key never enters the VM and that OpenRouter is a *hub*, not the inference provider. |
| Model chain weight | **Subordinate, not centre stage.** It is a side-channel off the main spine, muted and dotted; the Ralph loop keeps the emphasis. |
| Placement | **Promote to top** — directly under the intro paragraph (~line 20), before `## Contents` |
| Count | **One** hero flowchart; no second diagram |

### Model routing — verified from `pi/files/home/.pi/agent/models.json`

OpenRouter is a **routing hub**, not the thing that runs the model. Every one
of the four models in `models.json` carries a `modelOverrides` block pinning
routing to a single downstream provider:

```json
"compat": { "openRouterRouting": { "only": ["deepinfra"], "allow_fallbacks": false } }
```

Models pinned this way: `qwen/qwen3.6-35b-a3b` (the default, per
`settings.json`), `qwen/qwen3.8-2.4t-a95b`, `deepseek/deepseek-v4-pro`,
`moonshotai/kimi-k3`. **Bring-Your-Own-Keys (BYOK)** is what makes this useful:
attach your own DeepInfra key at OpenRouter and the hub forwards to that
provider on your account. So the honest chain is four hops:

```
Pi agent → sbx egress proxy → OpenRouter (hub) → DeepInfra (pinned, BYOK, no fallbacks)
```

Two things deliberately stay **out** of the diagram and remain prose: the
`litellm` second provider (an off-by-default alternative gateway that bypasses
OpenRouter entirely — a different story from BYOK), and the specific model ids,
which change and would date the picture.

## Verified constraints

- **GitHub's README renderer is the only renderer.** No CI job parses Mermaid
  (`.github/workflows/ci.yml` has no mermaid step). GitHub-flavored Mermaid is
  the compatibility ceiling — no `architecture-beta` (its Iconify icons never
  load), no `block-beta` (v11 beta, syntax has churned), no `@{shape:}` v11.3
  syntax, no Font Awesome, no `click`.
- **Must survive both GitHub themes.** This is the main hazard for a styled
  diagram, addressed under Design decisions below.
- **`MD013: false`** in `.markdownlint-cli2.yaml:2` — long `classDef` lines are
  fine. Still live: MD031 (blank lines around the fence), MD040 (fence needs
  the `mermaid` language tag), MD022/MD032.
- **cspell**: `okf`, `sbx`, `frontmatter`, `inspectmd`, `inspectokf`,
  `sizeokf`, `merkleokf`, `qwen` are already in `.cspell.json`. The fence is
  wrapped in `<!-- cspell:disable -->` / `<!-- cspell:enable -->`, so anything
  inside is safe regardless — **the wrapper must move with the diagram.**
- **Width budget**: GitHub's content column is ~890px and scales larger SVGs
  down, so width is spent on legibility. Target ≤7 ranks, ≤22 chars per label
  line, ≤6 labelled edges.

## Step 1 — Set up a scratch bench

Work in the session scratchpad, **not** `tmp/` (untracked and not ignored, so
files there show up as `?? tmp/` and risk being committed):

```
/tmp/claude-1000/-Users-lars-Code-md2okf/71c06b52-1187-4a0b-b1f7-a2456cc5fa55/scratchpad/
```

`mmdc` (mermaid-cli 11.16.0) is on PATH. Render every variant three ways:

```bash
mmdc -i v03.mmd -o v03-light.png -t default -b white
mmdc -i v03.mmd -o v03-dark.png  -t dark    -b '#0d1117'
```

Then **read the PNGs** and record actual pixel dimensions — aspect ratio and
dark-mode legibility get measured, not guessed. `mmdc` is a close proxy for
GitHub's renderer but not identical; the final check is a real GitHub preview,
which only the user can do.

## Step 2 — Brainstorm 10 variants

Build all ten as `.mmd` files, render, and view. They deliberately vary
diagram type, narrative framing, and detail level — not ten flavours of the
same flowchart.

Every variant carries the model chain, but each solves *subordination*
differently — that is one of the things being compared. Broadly: hang it below
the spine (V1, V3, V7), give it its own muted zone (V4, V6), fold it into a
single annotated node (V2, V8), or let it sit inline and see whether it steals
focus (V5, V9, V10 — useful as a control).

| # | Name | Framing | Type |
| --- | --- | --- | --- |
| V1 | Ralph loop hero | The cycle is the centrepiece; hash decision sits on the host and feeds a short back-edge into the agent | flowchart LR |
| V2 | Contract | Not a pipeline but a capability contract: every read-only input left, the one writable path right | flowchart LR |
| V3 | Hybrid V1+V2 | Permission-labelled inputs on the left rank, VM cluster centre, hash decision and loop on the right | flowchart LR |
| V4 | Trust zones | Three clusters — host / microVM / network — framing the blast radius of letting an LLM write files | flowchart LR |
| V5 | Fixpoint | The compiler as a state machine running to a fixed point | stateDiagram-v2, `direction LR` |
| V6 | Layer cake | Four full-width bands: orchestration / isolation / agent / artifacts | flowchart TD |
| V7 | Minimalist | Five nodes and one loop; everything else left to prose | flowchart LR |
| V8 | Document journey | Follow one `.md` through to its output shape, fanning out to `index.md` / `log.md` / pages | flowchart LR |
| V9 | Filmstrip | The loop unrolled — pass 1, pass 2, pass 3-converged side by side with the hash under each | flowchart LR |
| V10 | Compact vertical | The `tmp/screenshot.png` structure done right: ≤5 ranks, no empty subgraph, landscape-ish | flowchart TD |

## Step 3 — Score them

One table, seven criteria, scored against the rendered PNGs rather than the
source:

1. **Seconds to comprehension** — does the main idea land in under ~5s?
2. **Fidelity** — does it preserve *agent, not transpiler*; the visible Ralph
   loop; the sandbox boundary; `SPEC.md` outranking everything; okf-lint as a
   hard gate; the key never entering the VM; and OpenRouter as a *hub* that
   forwards rather than as the endpoint?
3. **Scope coverage** — all agreed components present without crowding.
4. **Subordination** — is the model chain legible but clearly secondary? Squint
   at the render: if the eye lands on the OpenRouter branch before the Ralph
   loop, the variant has failed this criterion regardless of how it scores
   elsewhere.
5. **Aspect ratio** — measured. Target 1.6:1–2.4:1, height ≲600px when scaled
   to 890px wide. This is where `tmp/screenshot.png` and any wide
   assembly-line layout both fail.
6. **Theme legibility** — readable in both renders, no light-on-light or
   dark-on-dark.
7. **Render risk** — conservative syntax, ≤2 clusters, no invisible links, no
   dependence on `direction` inside a subgraph (silently ignored once an edge
   crosses the boundary).

Expect V3 to lead, with V1 and V4 as the realistic challengers, V5 as the
strongest different-flavour option, and V9/V10 as the likely eliminations.
Score honestly against the renders — if a challenger wins, take it.

## Step 4 — Iterate to a final

Take the top 2–3, fold their best parts into one candidate, re-render,
tighten labels, re-render. Design decisions to carry in:

- **Opaque-card palette.** Always set `fill`, `stroke` *and* `color` together
  on every `classDef`. A near-white pastel fill with dark ink and a saturated
  2px stroke paints its own background, so contrast stops depending on the
  theme; the stroke keeps it from dissolving on white. `fill` without `color`
  is the classic dark-mode break — GitHub sets node text light, which vanishes
  on a pastel fill.
- **Never fill a subgraph.** Use `fill:none` plus a dashed grey stroke so the
  cluster title inherits the theme and stays readable in both.
- **Never set `color:` inside `linkStyle`** — it recolours the edge *label*,
  which sits on a theme-coloured background, guaranteeing invisibility in one
  mode. Restyle edge `stroke` only.
- **No `%%{init}%%` theme block.** It opts out of GitHub's dark adaptation
  entirely and forces you to own every text colour, arrowhead and cluster
  title while GitHub still picks the canvas.
- **One cluster only** (the microVM). Host and network nodes stay unclustered
  — three clusters with bidirectional edges is where dagre visibly draws edges
  through cluster walls. (V4 tests this claim; if it renders cleanly, it is
  back on the table.)
- **Keep the back-edge to 2–3 ranks.** A cycle spanning 2–3 ranks reads as
  intentional; one spanning 5+ reads as broken.
- **Semantic shapes, classic syntax only**: `{{ }}` hexagon for the okf-lint
  gate, `{ }` diamond for the hash decision, `[( )]` cylinder for `okf/`,
  plain `[ ]` for the rest.
- **Fix the two known defects**: drop `KIT ~~~ SPEC` entirely; make the driver
  hand the document *forward* into the agent so no edge points backwards
  except the deliberate loop.
- **Subordinate the model chain by three means at once**, so it reads as a
  side-channel even at a squint:
  1. *Position* — hang it off the agent node on a secondary rank (below the
     spine in an LR layout), never inline between two main-flow nodes.
  2. *Colour* — the muted neutral `classDef` (grey fill, 1.5px grey stroke)
     while the spine keeps the saturated strokes. No accent colour anywhere on
     this branch.
  3. *Edge weight* — dotted `-.->` throughout, against the solid spine and the
     thick `==>` converged edge.
- **Show the hub relationship, not just the hop.** The point is that OpenRouter
  forwards; a single `OpenRouter` endpoint node would misrepresent it. Test
  these three shapes and pick by render:
  - **3 nodes**: `sbx egress proxy · injects key` → `OpenRouter · hub` →
    `DeepInfra · BYOK`. Most honest, most width.
  - **2 nodes**: `sbx proxy · injects key` → `OpenRouter hub → DeepInfra<br/>BYOK · no fallbacks`. Compresses the hub relationship into one label.
  - **2 nodes, edge-carried**: `sbx proxy` → `OpenRouter` with the edge label
    `forwards to DeepInfra · BYOK`. Cheapest on width; risks the label
    colliding on a crowded rank.
  Expect the 3-node form to win on clarity and the 2-node form to win if width
  is tight — decide from the PNG, not from the source.
- Keep the model-chain labels free of specific model ids (`qwen/qwen3.6-35b-a3b`
  and friends). They change, they are long, and they would date the diagram.
- Comment any `linkStyle` index — it is positional and breaks silently when
  edges are reordered.
- Typographic separators (`·`, `→`) instead of emoji, which render as
  per-platform colour glyphs and undercut the designed look.

## Step 5 — Land it in README.md

Single file changed: `README.md`.

1. Insert the final diagram after the intro paragraph (ends line 19, `...it
   outranks any other instructions.`) and before `## Contents` at line 21,
   wrapped in its own `<!-- cspell:disable -->` / `<!-- cspell:enable -->` pair
   with blank lines either side of the fence.
2. Delete the old block at lines 108–136 (fence plus both cspell comments).
3. Re-read the `## How it works` prose at lines 91–106 — it is self-contained
   and should still read correctly with no diagram beneath it. Adjust only if
   it refers to the diagram deictically.
4. No `## Contents` entry needed — the diagram adds no heading.
5. No `docs/` or `assets/` directory and no committed image: the diagram stays
   inline Mermaid, so the `### Repository layout` table at line 138 needs no
   new row.
6. **Consistency check on the BYOK claim.** The diagram will now assert
   something no README prose currently says — that OpenRouter forwards to
   DeepInfra. `## Set up the OpenRouter key` (lines 185–205) covers only the
   key; the routing story lives in `pi/README.md` under *Model configuration*
   and *Using another provider*. Confirm the diagram does not strand a reader:
   either it is self-explanatory from its labels, or one clause is added
   pointing at `pi/README.md`. Prefer the former — the brief is a diagram that
   stands alone, and the README already links the pi kit guide at line 205.

## Verification

```bash
# 1. Renders at all, in both themes, at a sane size
mmdc -i final.mmd -o final-light.png -t default -b white
mmdc -i final.mmd -o final-dark.png  -t dark    -b '#0d1117'
#    → view both PNGs; confirm no unreadable text, no edges through cluster
#      walls, no orphan nodes, and landscape dimensions

# 2. Repo lint (markdownlint + cspell both run over README.md)
make lint

# 3. Confirm the diagram is the only README change
git diff --stat
git diff README.md
```

Then a manual check the user must make: open the branch's `README.md` on
GitHub in **both** light and dark mode and confirm the render matches the
`mmdc` output. `mmdc` 11.16.0 approximates GitHub's Mermaid but the two are
not pinned to each other, and nothing in CI will catch a divergence.
