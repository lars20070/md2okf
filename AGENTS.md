# Agent Instructions

> **Scope:** these are instructions for **development agents** working *on* this
> repository (e.g. Claude Code) — how to build, lint, and validate it. They are
> not Pi's task instructions. Pi runs inside the sandbox with the repo root as
> its workspace and may read this file as a project document; if you are Pi, your
> role and rules live in your own agent config (`~/.pi/agent/AGENTS.md`, authored
> from `pi/sandbox/files/home/.pi/agent/AGENTS.md`) — nothing here changes that,
> and the Context7 / GitHub MCP tooling below is not available to you.

## Repository map

md2okf compiles Markdown into an OKF wiki with the Pi coding agent: one source
document per file in `md/`, one Pi run per file, folded into the wiki under
`okf/`. Both directories are gitignored; only `okf/.okflintrc.json` is tracked.
`SPEC.md` at the repo root is the OKF revision the wiki is built against — the
agent reads it at the start of every run, and it outranks any instruction file,
including the runtime agent configs. `pdf2md/` is the optional upstream step
that turns a PDF into Markdown with `marker`; it is manual and not wired into
the `make` pipeline.

There are **two independent Pi runtimes**, each self-contained and carrying its
**own copy** of the Pi config (`AGENTS.md`, `settings.json`, `models.json`,
`skills/`):

- `pi/sandbox/` — Docker Sandbox (sbx) kit; its config lives in
  `pi/sandbox/files/home/.pi/agent/`. The one to reach for: the agent has
  `bash`, so it lints its own output and dates its log entries, and the
  OpenRouter key stays outside the VM (proxy-managed by sbx). Config is copied
  in at kit build time, so edits only land in a fresh sandbox — which
  `make wiki-sandbox` always builds.
- `pi/container/` — Docker Compose runtime; its config lives in
  `pi/container/agent/` and is bind-mounted, so edits apply on the next run.
  Pi runs with `-xt bash`: no lint step, no dates in `okf/log.md`. Never add
  `read` to that denylist, or Pi stops advertising the skill at all.

Either runtime compiles the same wiki, but their `okf/log.md` formats differ, so
don't mix the two for one wiki.

The two config copies are deliberately **not** a single source of truth. When a
change should apply to both runtimes, edit **both** copies by hand and keep them
aligned. The runtimes share no code path, so deleting one never touches the
other.

Within each config, the split is: `AGENTS.md` holds what every task must respect
(OKF conventions, the writable directories, `SPEC.md` outranking both), while
each task's procedure lives in its own skill directory under `skills/`. There is
one today, `compile-wiki`. A new task gets a new skill, not more rules in
`AGENTS.md`.

## Commands

```bash
make lint            # markdownlint + shellcheck + ruff + hadolint (default goal)
make validate        # validate the sandbox kit spec (runs scripts/validate-spec.sh)
make wiki-sandbox    # compile the OKF wiki via the sandbox runtime (preferred)
make wiki-container  # compile the OKF wiki via the container runtime
make lint-okf        # lint the generated okf/ wiki (okf-lint via pnpm dlx)
```

```bash
./scripts/bash-sandbox.sh                            # shell into the existing sandbox
./scripts/bash-container.sh                          # throwaway container shell
./scripts/compile-wiki-container.sh md/other-books   # container run, different source folder
```

`make lint-okf` is host-only and needs a generated `okf/`; it sits outside
`make lint` and outside CI because `okf/` is gitignored output, and neither
driver calls it. `make wiki-container` needs `OPENROUTER_API_KEY` exported in
your shell; `make wiki-sandbox` takes it from `sbx secret` instead (see the
README for the two-step setup).

## Always validate the sandbox kit spec before finishing

Whenever you change anything under `pi/` or `scripts/`, you MUST validate the Pi
Sandbox Kit spec before considering the task complete:

```bash
./scripts/validate-spec.sh   # or: make validate
```

This checks `pi/sandbox/spec.yaml` against the current Sandbox Kit schema (a
static schema check — no Docker, login, or network required). The same check runs
in CI (see `.github/workflows/ci.yml`, job `validate-kit`), so validating locally
first avoids CI failures. Do not finish a task until it passes. If the `sbx` CLI
is not installed, install it with `brew install docker/tap/sbx`.

## Library documentation (Context7 MCP)

Before writing or modifying any code that uses a third-party library, package,
or framework, fetch its current docs via the Context7 MCP server — do not rely
on training data for external APIs.

- Call `resolve-library-id` with the library name to get its Context7 ID, then
  `query-docs` with that ID and a specific `topic` (e.g. "middleware",
  "query invalidation").
- If you already know the exact ID (e.g. `/vercel/next.js`), skip resolving and
  call `query-docs` directly. Match the version in our manifest
  (package.json / requirements.txt / go.mod) when the library moves fast.
- Verify the library ID and version reported in the tool output before trusting
  the result; Context7 falls back to "latest" if a pinned version isn't indexed.
- Prefer a focused `topic` query to keep the pull small (~5k tokens/call).

If Context7 has no entry for a library, say so and fall back to your best
knowledge — do not block. You can also trigger a lookup manually by adding
"use context7" to a request.

## Debugging third-party libraries (GitHub MCP)

When you hit an error, crash, or unexpected behavior that appears to come from
an external dependency (not our own code), check whether it's a known bug
BEFORE building a workaround.

1. Identify the upstream repo (`owner/repo`) from the manifest — the
   `repository` field in package.json, project URL in PyPI/pyproject.toml,
   the Go module path, or Cargo.toml. Do not guess the repo.
2. Use the GitHub MCP server (issues toolset) to search that repo:
   - `search_issues` with a distinctive substring of the error message plus
     `is:issue is:open` (or `state:open`). Search the key symbol/message, not
     the whole stack trace.
   - Open the best matches with `issue_read` (`method: "get"` for the issue
     body, then `method: "get_comments"` — a separate call — for maintainer
     replies and any linked fix or workaround; `get` alone won't surface
     comments).
3. Also skim recently closed issues / merged PRs with `search_pull_requests`.
   A fix may exist in a newer release.
4. Report back: whether it's a known issue, the issue number + status, the full
   URL (`https://github.com/<owner>/<repo>/issues/<number>`), and any suggested
   workaround. Only then implement a local fix, and reference the issue number
   in a code comment.
