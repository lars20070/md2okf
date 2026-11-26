# Tools

The four helper CLIs the agent uses to inspect sources and the wiki, and the two upstream converters that turn other formats into Markdown for `md/`.

## Helper CLIs

`inspectmd`, `inspectokf`, `sizeokf` and `merkleokf` are each an independent uv project under [[scripts]], installable on the host and staged into every sandbox.

They share a set of traits by convention, not by shared code:

- Standard library only, so the sandbox runs them with `uv tool run` and nothing to resolve.
- `-L`/`--level` caps the listing depth.
- Exit 0 on success and 2 on a usage or runtime error.
- Zero overlap: no project imports another, even where two need the same logic.

In the sandbox each CLI is a shim over the read-only scripts mount (see [[lat.md/kits#Runtime]]), and the driver stages only each project's `pyproject.toml` and `src/` (see [[workbench#Staging]]). [[CONTRIBUTING.md]] has the command table.

### inspectmd

Prints a Markdown file's heading map: line ranges, word counts and kebab-case slugs, so the agent can read a large source one section at a time.

[[scripts/inspectmd/src/inspectmd/parse.py#parse_sections]] parses ATX headings while skipping fenced code, after splitting off any frontmatter.

### inspectokf

Prints the wiki's directory tree by wrapping `tree`, defaulting to `okf/` with unlimited depth.

An empty or dotfile-only directory is printed without calling `tree` at all, so a fresh wiki cannot fail on a missing binary or on `tree`'s exit-code quirks.

### sizeokf

Reports Markdown word counts per file and per folder, recursively, with YAML frontmatter excluded, so the numbers measure prose rather than metadata.

[[scripts/sizeokf/src/sizeokf/sizes.py#strip_frontmatter]] uses the same rule as `inspectmd`: a block must open on the first line and close on a later `---` line, or the text is left unchanged.

### merkleokf

Prints a Merkle hash tree, one hash per `*.md` file and per directory, so a change to any page moves its parents' hashes and nothing else. The driver's convergence check is built on it.

[[scripts/merkleokf/src/merkleokf/merkle.py#collect]] hashes raw bytes, frontmatter included. Directory digests mix in each child's name and a file-or-directory tag, so a rename is visible and a file never collides with a directory of the same name. Children are sorted by name so digests are reproducible across filesystems. Dotfiles, symlinks and non-Markdown files are skipped.

### Why sizeokf and merkleokf share no code

The two answer opposite questions: `merkleokf` asks "did this change", so it hashes every byte, while `sizeokf` asks "how much prose is here", so it strips frontmatter.

Each keeps its own walk under the zero-overlap rule. `sizeokf` also carries its own frontmatter stripper rather than importing `inspectmd`'s, and tests on both sides pin the two to the same behaviour.

### The --nolog flag

Both `sizeokf` and `merkleokf` take `--nolog`, which leaves a wiki's `log.md` out, but they decide which `log.md` differently.

`merkleokf` skips the walk root's own `log.md`, whatever the root is called. `sizeokf` skips it only when the walk root is named `okf`. Nested `log.md` files are counted by both. The driver's convergence check runs `merkleokf` on the workbench's `work/okf`, so it is unaffected either way.

## Upstream converters

Two optional steps produce Markdown for `md/`. Neither is part of the compile run, and each is its own uv project under [[extras]].

### web2md

A deterministic scraper that fetches one documentation site into a single Markdown file under `md/`, driven by `make scrape`.

Which site and which output file are the two constants [[extras/web2md/src/web2md.py#SOURCE_URL]] and [[extras/web2md/src/web2md.py#OUTPUT_FILE]]. [[extras/web2md/src/web2md.py#run]] discovers the pages from the site's navigation, fetches each one and cleans and converts it, then rewrites internal anchors and links, and assembles one book.

[[extras/web2md/src/web2md.py#fetch_html]] caches every successful response in a gitignored cache, and retries with exponential backoff, honouring `Retry-After`. [[extras/web2md/src/web2md.py#validate_output]] must pass before anything is written, so a failed run leaves the previous snapshot intact. Its test suite is offline, with HTTP mocked.

### pdf2md

A manual, optional step that converts a PDF to Markdown with `marker` and a language model. It is not wired into `make`.

Marker's output needs checking before it goes into `md/`. [[extras/pdf2md/README.md]] has the commands.
