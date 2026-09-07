# Verification

Read this twice: once before drafting, for the facts table, and once after,
for the checklist.

## Facts to derive before writing a line

Almost every claim a README makes already exists somewhere in the repository.
An agent that reads these cannot hallucinate them.

| Fact | Source of truth |
| --- | --- |
| Project name | `package.json` `name`, `pyproject.toml` `[project].name`, `Cargo.toml`, `go.mod` module path, directory name |
| One-line description | Manifest `description`, where the repo has a manifest |
| License | `LICENSE` / `LICENCE` / `COPYING` plus the manifest `license` field; they must agree; emit the SPDX identifier |
| Runtime support | `engines`, `requires-python`, `rust-version`, the `go` directive, and the CI matrix in `.github/workflows/*.yml` |
| Install command | Whether the package is actually published; if not, install-from-source instructions instead |
| Entry points | `bin` in `package.json`, `[project.scripts]`, `cmd/` in Go, `[[bin]]` in `Cargo.toml` |
| Usage examples | `examples/`, `tests/`, doctests, integration fixtures — prefer code that CI executes |
| Available tasks | `scripts` in `package.json`, `Makefile` targets, `justfile`, `tox.ini`, `noxfile.py` |
| CI status and badge targets | The real workflow filenames, and the badge URL shape they imply |
| Dependencies worth naming | Manifest or lockfile — only the unusual or manually installed ones |
| Community files that exist | `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `CHANGELOG.md`, issue templates |
| Support channels | `SUPPORT.md`, `.github/`, existing links, whether Discussions is enabled |
| Maintainers | `CODEOWNERS`, `AUTHORS`, `MAINTAINERS.md`, manifest `authors`, commit history |
| Maturity | Version number (0.x versus 1.x), tag history, commit recency, open issue ratio |

## Verification budget

Checking everything is expensive. Tier it:

- **Always** — internal links resolve to files that exist, and the install
  command matches the actual publication state.
- **When cheap** — external links, badge targets.
- **Always state** — which snippets you ran and which you did not. An
  unverified snippet is acceptable; an unverified snippet presented as
  verified is not.

## Checklist

### Correctness

- [ ] Title matches the repository, directory and package name, or the
      mismatch is explained
- [ ] One-liner is under 120 characters
- [ ] The install command matches the real package name and publication state
- [ ] Every code snippet is either run, or explicitly marked unverified in
      your report
- [ ] Every claimed feature, CLI flag, config key and function signature
      exists in the code
- [ ] Version numbers and runtime ranges match the manifest and the CI matrix
- [ ] No linked file is missing and no badge points at a deleted workflow
- [ ] Anything moved out of the README exists in its new file and is linked
      from the README — nothing was dropped in the name of shortening

### Structure

- [ ] What, why, how, where to get help and who maintains it are all answered
- [ ] The purpose is present — the most commonly missing element
- [ ] The first screen alone supports a keep-or-leave decision
- [ ] Every piece of project jargon is glossed or linked on first use, and
      each concept keeps one name throughout
- [ ] Exactly one H1, and no skipped heading levels below it
- [ ] A table of contents exists above about 100 lines, and every anchor
      resolves

### Rendering

- [ ] No conflicting README in `.github/` or `docs/`
- [ ] Every code fence carries a language tag
- [ ] Every image has alt text, and no information exists only in an image
- [ ] Links use descriptive text, not bare URLs
- [ ] List items and headings are grammatically parallel
- [ ] Command blocks carry no leading `$` prompt, so they paste as written
- [ ] Paths that must survive on a package registry are absolute

### Honesty

- [ ] No superlative without a benchmark or citation behind it, and no
      hedge softening a claim you actually believe
- [ ] Known limitations are stated — the ones you actually found, never
      invented to fill the section
- [ ] A Contributing section appears only if contributions are actually
      accepted
- [ ] Nothing planned is described in the present tense

## Platform mechanics

Rules. These are documented platform behaviour, and getting one wrong is a
visible defect:

- **Resolution order.** If several READMEs exist, the platform shows
  `.github/README.md`, then the repository root, then `docs/`. Adding a root
  README to a repo that already has one in `.github/` produces a file nobody
  sees.
- **Truncation.** Content beyond 500 KiB is not rendered. Prose never hits
  this; embedded base64 images and generated tables do.
- **Headings are navigation.** The outline menu is generated from them, so a
  skipped level degrades it.
- **Relative links** resolve against the current file. Use absolute URLs for
  anything a package-registry audience needs, since the README is reused as
  the package landing page.
- **HTML is sanitised** to a subset: `<div align>`, `<img>`, `<details>`,
  `<summary>`, `<picture>`, `<kbd>`. No `<style>`, no `<script>`.
- **Dark mode** needs `<picture>` with a `prefers-color-scheme: dark` source.
  A logo with a baked-in white background is a defect for half of viewers.

Defaults. Sensible unless the repo has a reason otherwise:

- Mermaid renders natively and beats a committed PNG for architecture
  diagrams, because it stays readable as text and reviewable in a diff.
- `<details>` keeps long content available without making the page harder to
  skim.
- Badge images are proxied and cached, so badge state can lag.
- Keep decorative emoji out of headings — they survive into the generated
  anchors and make hand-written table-of-contents links fragile.
