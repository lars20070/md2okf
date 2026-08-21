# Task: Rewrite `README.md` for the `md2okf` repository

You are working inside the `md2okf` repository (branch `lars20070/furtherchanges`).
Rewrite the root `README.md` to be a clear, reader-first front door. Do NOT change
any code. Only edit `README.md` (and, where instructed, create `CONTRIBUTING.md`
and/or files under `docs/`). Preserve the project's factual accuracy above all.

## Goal and audiences
The README's job is to let a newcomer answer, within one screen: **What is this?
Why would I use it? How do I run it in ~2 minutes? Where do I get help?** Write for
three audiences, in priority order:
1. **Evaluator** — a developer deciding in <60 seconds whether this is relevant.
2. **First-time user** — wants to compile a wiki with the least friction.
3. **Contributor** — wants to change the code, run tests, and understand internals.
Serve audiences 1 and 2 in the README body; push most of audience 3's material into
`CONTRIBUTING.md` or `docs/`, linked from the README.

## Guiding principles
- The README is the **map, not the territory**. It gets people started and links out
  to depth (Diátaxis: don't mix tutorial + how-to + reference + explanation on one page).
- **Show, don't tell.** Prefer a working command + its output over paragraphs.
- **Define jargon on first use** with a short gloss or a link: OKF, Pi, kit, sbx,
  "Ralph loop", Merkle hash.
- **Verify every fact against the source** (see "Facts to verify"). Never invent a
  command, flag, version, or license.

## Target structure (use exactly this order; omit a section only if truly N/A)
1. **`# md2okf`** — the H1, matching the repo name. (Exactly one H1 in the file.)
2. **Badges** (optional, max 3, immediately under the title): CI/build status
   (the `validate-kit` workflow), license, and — only if the project is published —
   a package-version badge. Generate via shields.io. No other badges. Each badge
   must link to its source (e.g., the workflow or the LICENSE file).
3. **One-line description** — a single sentence (<120 chars) stating what it does.
   Reuse/refine the existing opener, e.g. "Compile Markdown files into an OKF
   knowledge base with a coding agent." Follow it with 2–4 sentences of context:
   what OKF is (one clause + link), what goes in (`md/`) and what comes out (`okf/`),
   and the one-run-per-document model.
4. **Table of Contents** — required because the file will exceed ~100 lines. Use
   anchor links; keep to top-level sections.
5. **Requirements / Prerequisites** — a short bullet list stated up front: macOS +
   Homebrew, Docker, an OpenRouter API key, and `sbx >= 0.38.0`. Verify each.
6. **Quickstart** — the 30-second path: the minimal commands to install prerequisites
   and run `make wiki` on the bundled sample, plus a one-line note on where output
   lands (`okf/`). Move the full OpenRouter secret setup OUT of here (see Setup).
7. **How it works** — keep the Mermaid diagram and a tight (~5–8 line) explanation:
   host driver → agent in an sbx microVM → writes `okf/` → lint must pass; note that
   `SPEC.md` outranks all instruction files.
8. **What lands in `okf/`** — keep the existing output-tree block and the short
   frontmatter/slug/link rules (this is useful reference; keep it concise).
9. **Getting Markdown in** — keep the `pdf2md` / `web2md` summary, but trim to 2–3
   lines each and link to their sub-READMEs for detail.
10. **Configuration / Setup (detailed)** — move the full `sbx login` + OpenRouter
    secret steps (including the known-bug workaround) here, below the quickstart, OR
    into `docs/setup.md` / `pi/README.md` and link to it.
11. **Troubleshooting** (optional) — the sbx-version mismatch note and "tests the
    sandbox you have" caveat belong here or in `docs/`.
12. **Development / Contributing** — replace the long Development section with a short
    paragraph + a link to `CONTRIBUTING.md`. Move the Makefile-target list,
    per-subproject `uv` layout, and `make validate`/`make test-sandbox` details into
    `CONTRIBUTING.md` (create it if absent).
13. **Getting help** — one or two lines: where to file issues, and any contact/discussion channel.
14. **License** — state the license name explicitly and link to the `LICENSE` file.
    If no `LICENSE` file exists, flag this in your PR description and do NOT invent one.

## Style and formatting rules
- **Voice:** second person, active voice, present tense; conversational but concise
  (Google developer style). No marketing fluff ("powerful", "blazing-fast", "simply").
- **Length:** aim for the README body under ~200 lines. Any section that grows beyond
  ~15 lines of prose is a candidate to move to `docs/` or `CONTRIBUTING.md`.
- **Headings:** one `#` H1 only; sections are `##`; subsections `###`. Never skip a
  level (no `##` → `####`). Use sentence case.
- **Code blocks:** every command/example in a fenced block with a language tag
  (```bash, ```text, ```yaml). Commands must be copy-pasteable and must not include
  a leading `$` prompt on lines meant to be copied. Show expected output where it
  aids understanding, in a separate ```text block.
- **Links:** descriptive link text, never bare URLs; use repo-relative links for
  in-repo files (e.g., `[SPEC.md](SPEC.md)`, `[contributing guide](CONTRIBUTING.md)`).
- **Images/diagrams:** every image needs descriptive alt text. The Mermaid diagram is
  fine; ensure any screenshot/GIF added has meaningful alt text.
- **Jargon:** first use of OKF, Pi, sbx, kit, Ralph loop, Merkle hash gets a 3–8 word
  gloss or link. Don't rely on emoji to convey meaning.
- **No changelog** in the README; if version history matters, link to `CHANGELOG.md`.

## Repo-specific keep / rewrite / move / delete
- **KEEP (lightly edit):** the opening one-liner; the directory table; the "What lands
  in okf/" tree and its frontmatter/slug/link notes; the Mermaid architecture diagram;
  the `pdf2md`/`web2md` links.
- **REWRITE:** the intro into a true description + context block with a one-clause
  gloss of OKF and a link to the OKF spec
  (https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf).
- **MOVE to Setup/`docs/` (below quickstart):** the OpenRouter secret export +
  `sbx secret set` + `set-custom` bug-workaround block; the sbx-version upgrade notes.
- **MOVE to `CONTRIBUTING.md`:** the entire "Development" section (Makefile targets,
  per-subproject `uv`/ruff/pytest layout, `make validate` vs `make test-sandbox`,
  `./scripts/bash.sh` / `./scripts/pi.sh`, the `proxy-managed` check).
- **ADD:** Requirements block, Table of Contents, Getting help, License section,
  up-to-3 badges.
- **DELETE:** nothing factual; only remove redundancy created by moving content.

## Facts to VERIFY against the source (do not assume)
Confirm each by reading the actual files/commands in the repo; if you cannot confirm,
flag it in the PR description rather than guessing:
1. **License** — does a `LICENSE`/`LICENSE.md` exist, and which license? Use its exact
   name. If absent, note it as an open item.
2. **Install/run commands** — that `brew install docker/tap/sbx`, `sbx login`, and
   `make wiki` are current; check the `Makefile` for the real target names and any
   others worth surfacing.
3. **Prerequisite versions** — the required `sbx` version (README says >= 0.38.0);
   Python version(s); Docker requirement. Cross-check against `pi/spec.yaml` and any
   `pyproject.toml`/`.python-version`.
4. **Helper CLI names/flags** — `inspectmd`, `inspectokf`, `sizeokf`, `merkleokf`,
   and flags like `merkleokf --nolog -L 0` and `RALPH_MAX` default (README says 10):
   confirm against `scripts/` and each tool's `--help`.
5. **CI** — the workflow name/jobs (README says `validate-kit`); read
   `.github/workflows/` to get the exact job name for the badge and Development text.
6. **OKF** — keep the OKF description accurate and linked; do not overstate.
7. **Whether it's installable** — confirm there is no PyPI/`pip`/`uv` install path and
   that `make wiki` is the entry point, so the README doesn't imply a package install.

## Verification steps (perform before finishing)
1. **Run the linter:** `markdownlint` (or `markdownlint-cli2`) on `README.md`; fix all
   findings, especially MD041 (first line = H1), MD045 (image alt text), MD051 (valid
   link fragments), MD025 (single H1), and heading-increment rules.
2. **Check every link resolves** — internal repo-relative links and external URLs
   (e.g., a `markdown-link-check` pass). No dead links or broken anchors.
3. **Dry-run the commands** you document (at least the quickstart and any CLI examples)
   in a scratch environment where feasible; confirm CLI examples match actual `--help`
   output. If a command can't be run, mark it clearly as unverified in the PR.
4. **Render check** — confirm it renders correctly on GitHub (headings, the Mermaid
   diagram, the table, code fences, the auto-generated outline/ToC).
5. **Screen-one test** — verify that description, what/why, and the quickstart entry
   are all visible within the first screen of content.

## Final review checklist (all must be ticked before you finish)
- [ ] Exactly one H1, matching the repo name; no skipped heading levels.
- [ ] One-line description (<120 chars) present as the first text after the title.
- [ ] OKF (and Pi/sbx/kit/Ralph loop) glossed or linked on first use.
- [ ] Requirements/prerequisites listed up front.
- [ ] A 30-second quickstart appears before deep setup/internals.
- [ ] <=3 meaningful badges (CI, license, [version]); no badge soup; each links out.
- [ ] License section present and accurate (or open item flagged if no LICENSE file).
- [ ] Getting-help / issues pointer present.
- [ ] Long Development content moved to `CONTRIBUTING.md`; secret-setup moved below
      quickstart or to `docs/`.
- [ ] All commands verified or explicitly marked unverified; no invented flags.
- [ ] Every image has descriptive alt text; links use descriptive text, not bare URLs.
- [ ] `markdownlint` passes; all links resolve; renders correctly on GitHub.
- [ ] README body is roughly under 200 lines; deeper material is linked, not inlined.
- [ ] No changelog, no "coming soon" sections, no marketing fluff.
- [ ] PR description lists every fact you could not verify against the source.
