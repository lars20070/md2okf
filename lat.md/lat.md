# md2okf knowledge base

The design graph of md2okf: why each part is built the way it is, and how the parts connect. Use `lat locate`, `lat search` and `lat refs` to navigate, and `lat check` to validate.

This graph records decisions, invariants and the links between them. Option lists, credential setup and release steps stay in the user and contributor docs it links to, so each fact has one home.

- [[driver]] — the host driver in `src/md2okf/` and how its modules split the work.
- [[kits]] — the sbx kits that build each agent's sandbox, its runtime helpers and skills.
- [[tools]] — the four helper CLIs the agent uses, and the upstream converters that feed `md/`.
- [[development]] — workflow, testing, packaging and release, and how this graph is kept current.

## Pipeline

One run takes Markdown documents through a fixed workbench into a sandboxed agent, one document at a time, and mirrors the wiki out to `-o`.

The stages run in this order, each owned by one part of the driver:

1. [[cli]] resolves the agent, the documents and `-o`, refuses anything unsafe ([[workbench#Output adoption]], [[workbench#Path safety]]), runs the sbx preflight and takes the [[workbench#Run lock]].
2. The workbench creates its mount roots if they are missing ([[workbench#Layout and mounts]]).
3. The sandbox ensure stages the helper CLIs and the spec, reuses or creates the sandbox once ownership is proven, and checks the agent's credential ([[sandbox#Create or reuse]], [[sandbox#Credential check]]).
4. Only then does the workbench stage this run's documents and mirror the existing wiki in from `-o` ([[workbench#Staging]]).
5. [[compile-loop]] runs one agent turn per iteration on each document until the wiki's root hash stops changing.
6. After every completed iteration the workbench wiki is mirrored out to `-o` ([[compile-loop#Mirroring cadence]]).

So a credential failure at stage 3 can leave a newly created sandbox and freshly staged tooling, while the workbench still holds the previous run's documents and wiki. What `-o` holds after an interruption or a failed copy is set out in [[workbench#Mirror failure recovery]].

What differs between Pi, Claude Code and Codex is confined to [[agents]] and to each agent's kit.

## Authority order

When instructions conflict, [[SPEC.md]] wins over the kit's agent instructions, which win over any skill. The spec is OKF v0.2 and is never edited here.

The agent reads the spec at the start of every run from its read-only mount. The kit instructions carry the authoring contract every task must respect, and each task's procedure lives in its own skill (see [[lat.md/kits#Skills]]).

## Repository map

The repository holds seven independent uv projects that share no code, plus the kits, the docs and this graph.

- The root project is the `md2okf` driver ([[pyproject.toml]], [[src/md2okf]]).
- Four helper CLI projects live under [[scripts]]; see [[tools#Helper CLIs]].
- Two upstream converters live under [[extras]]; see [[tools#Upstream converters]].
- Each project has its own lockfile, ruff config and tests. Under the zero-overlap rule nothing is imported across projects, even where two carry near-identical code.
- `md/` holds the tracked source documents. `okf/` is the generated wiki and is gitignored in full.
- `kits/` holds one sbx kit per agent; see [[lat.md/kits]].

User-facing reference lives in [[docs/architecture.md]], [[docs/usage.md]] and [[docs/configuration.md]]. Contributor rules live in [[AGENTS.md]] and [[CONTRIBUTING.md]].
