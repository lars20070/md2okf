# Development

How md2okf is linted, tested, packaged and released, and how this knowledge graph stays true. [[CONTRIBUTING.md]] has the commands.

## Workflow

`make` is the task runner for every gate. Each target drives its checks from `git ls-files`, so a new file is covered as soon as it is tracked, and not before.

`make lint` runs markdownlint, `jq`, yamllint, shellcheck, cspell, ruff once per uv project, and `lat check` on this graph. It also checks that `VERSION` matches the latest `CHANGELOG.md` release and every subproject's declared version. The linters run through `npx` or `uv tool run` with pinned versions, so only markdownlint needs a local install. [[Makefile]] documents each exclusion beside the rule.

On Linux, `make` exports `UV_PROJECT_ENVIRONMENT=.venv-linux`. A development sandbox shares the tree with a macOS host, and a venv is not portable across platforms. The value stays relative so each of the seven uv projects gets its own environment, where an absolute path would merge them into one and break the zero-overlap rule.

The default branch is `master`. Agents stage changes and draft the commit message, and never commit or push; the maintainer does that (see [[AGENTS.md]]).

## Keeping the graph current

Keeping `lat.md/` true is a review responsibility. `lat check` proves that links resolve and sections are well formed, not that the prose still describes the code.

A change to behaviour updates the section that describes it in the same change. Reviewers read the prose against the tests it links. A section names its tests beside each guarantee so that this check is concrete. Source code points back with `# @lat:` comments in [[src/md2okf]].

Each cross-cutting invariant has one home that holds its reason, its boundary and its tests, and other pages link there instead of restating it. For example, what survives an interrupted mirror lives in [[workbench#Mirror failure recovery]]. This keeps a behaviour change to one section.

The review steps:

- **A changed behaviour**: run `lat refs 'path/to/file.py#symbol'` to find every section that links the changed symbol, then reread each one against its linked tests.
- **A renamed or moved section**: run `lat refs '<section>'` before the edit to find its inbound links. Afterwards run `lat refs '<section>' --scope=code` to confirm its source back-reference still resolves.

The second check matters because `lat check` validates the back-references that exist but does not require any. A deleted `# @lat:` comment leaves `lat check` green, and only `lat refs` shows it is gone.

The kits carry no back-references, because any kit edit changes the sandbox fingerprint and the shared shim hook must stay byte-identical. Option lists, credential setup and release commands stay in the user and contributor docs, and this graph links to them rather than copying them.

## Testing

Every pytest suite runs offline, and each project has its own. A shell suite and the kit build cover what pytest cannot reach.

- **Driver suite** (`make test-md2okf`, [[tests]]): [[tests/conftest.py]] replaces the one sbx seam with a fake, so every module above it is exercised without a sandbox (see [[sandbox#The sbx seam]]).
- **Kit contract**: [[tests/test_kits.py]] holds every kit to the shared authoring contract (see [[lat.md/kits#Shared contract]]).
- **Package**: [[tests/test_package.py]] inspects the built wheel for the bundled kits, spec, sbx pin and CLI sources, and for the absence of virtual environments and caches. `make dist` builds the wheel from the sdist and runs it outside the checkout, so a file the sdist drops fails there rather than after a release.
- **Live sandbox** (`make test-sandbox`, host only): [[tests/test-sandbox.sh]] asks the driver for each agent's sandbox, runs that agent's guest script inside it, then checks from the host what only the host can see.
- **Kit build** (`make validate`): [[scripts/validate-spec.sh]] builds every kit with `docker buildx` and checks the artifact with kit-tck, because `sbx kit validate` cannot read a schema v3 source kit. It also fails a mixin that ships an entry owned by anyone but root and the agent. It sees each kit alone; composition shows only in the live sandbox suite.
- **CLIs and web2md** (`make test-clis`, `make test-web2md`): one suite per project, run with that project's own config.

## Packaging

The wheel carries the driver and everything it needs at runtime, so an installed md2okf compiles without a checkout. That makes the wheel's contents part of the design.

[[pyproject.toml]] force-includes each registered kit, `SPEC.md`, `SBX_VERSION`, and the `pyproject.toml` and `src/` of each helper CLI. Naming a CLI's directory would pull in its venv and caches, since a force-included directory ignores `.gitignore`. The sdist excludes the agent-tool directories at the root that hold vendored third-party skills. Those patterns are anchored with a leading slash, so they never match a kit's own dot-directories, such as `files/home/.pi/`.

### Lookup order

The driver finds its kits, spec, sbx pin and CLI sources in the installed package first, and falls back to the checkout, so `uv run md2okf` needs no build step.

[[src/md2okf/resources.py#_installed_root]] returns the installed package directory only when it carries a `kits/` directory. Otherwise [[src/md2okf/resources.py#kit_dir]], [[src/md2okf/resources.py#spec_md]], [[src/md2okf/resources.py#clis_dir]] and [[src/md2okf/resources.py#sbx_version_file]] resolve against the checkout. A missing checkout path raises an error naming the likely cause, a wheel built without its assets, rather than a vague "not a file" later.

## Release

One `VERSION` file versions the whole repository. `SBX_VERSION` is separate: it sets the sbx floor that the driver, `make validate` and CI enforce.

The root project reads [[VERSION]] directly. Every other project carries a literal that [[scripts/sync-versions.sh]] writes, and `make lint` fails on any project left behind. A dynamic read of `../../VERSION` would not work, because the driver stages each CLI as only its `pyproject.toml` and `src/` (see [[workbench#Staging]]), where no path above the project root exists.

[[SBX_VERSION]] is the minimum the driver's preflight accepts and the exact release CI installs to validate the kits. Raising it touches more than that file.

CI runs lint, each pytest suite, the mount test, the package build and kit validation as separate jobs in [[.github/workflows/ci.yml]]. Pushing a `vX.Y.Z` tag runs [[.github/workflows/release.yml]]. It checks the tag against `VERSION`, runs `make lint`, builds both artifacts once, publishes them to PyPI by trusted publishing, and creates a GitHub Release with the matching changelog section as its notes. [[CONTRIBUTING.md]] has the release steps.
