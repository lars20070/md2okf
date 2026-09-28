# Usage

How to compile documents with `md2okf`, follow a run, and use the wiki it
produces. To install `md2okf` and `sbx` and set up a credential, see
[the README](../README.md).

## Contents

- [What you can compile](#what-you-can-compile)
- [Compiling](#compiling)
- [Reading the output](#reading-the-output)
- [What lands in `okf/`](#what-lands-in-okf)
- [Reading the result](#reading-the-result)
- [How compiling stops](#how-compiling-stops)
- [Output directory rules](#output-directory-rules)
- [Getting Markdown in](#getting-markdown-in)
- [Inspecting the sandbox](#inspecting-the-sandbox)
- [CLI reference](#cli-reference)
- [Exit codes](#exit-codes)
- [Locking](#locking)

## What you can compile

`md2okf` takes Markdown files, folders or standard input:

- **A file** is compiled as it is.
- **A folder** contributes every `*.md` file directly inside it, sorted by
  name. Subfolders are ignored.
- **`-`, or no argument at all,** reads one document from standard input and
  stages it as `stdin.md`. `md2okf` refuses to read from a terminal, so pipe
  the document in: `cat notes.md | md2okf`. Only one `-` is allowed.
- **Several arguments** are compiled one after another, in the order given.

`md2okf` refuses to start when:

- two different input files have the same name, such as `a/notes.md` and
  `b/notes.md`, because both would be staged as `notes.md`;
- two paths overlap — the same path given twice, one input inside another,
  or the output directory inside an input folder or the other way round. The
  same rule covers `--spec` and `md2okf`'s own workbench. For example,
  `md2okf .` fails, because the default output directory, `okf/`, lies
  inside `.`;
- an input does not exist, or is a symbolic link or a special file;
- nothing is left to compile, for example a folder with no `*.md` files.

## Compiling

```bash
md2okf notes.md                             # one file
md2okf docs/handbook/                        # every *.md directly inside it
md2okf a.md b.md                             # several files, in that order
md2okf -o wikis/handbook docs/handbook/      # a custom output directory
md2okf -n 20 long-document.md                # raise the iteration cap
md2okf --fresh notes.md                      # force a sandbox rebuild first
md2okf --spec my-spec.md notes.md            # compile against a different spec
```

`--spec` sets the OKF specification the agent compiles against; by default it
is the `SPEC.md` bundled with `md2okf`. Don't confuse it with `SPEC_MD`, an
environment variable that `md2okf --help` also lists. `SPEC_MD` only tells the
wiki-checking script, `check-okf.sh`, where to find the specification;
`md2okf` itself never reads it.

## Reading the output

`md2okf` prints progress to standard error: two lines per iteration, naming
the document and the iteration, then giving the wiki's root hash before and
after it.

```text
Compiling document notes.md (iteration 1)
7f3c1a9d4e02 -> b481d05c6a17
Compiling document notes.md (iteration 2)
b481d05c6a17 -> b481d05c6a17
```

Here the first iteration changed the wiki and the second changed nothing, so
the document was done. `-v` adds the agent's tool calls and messages to this
stream, which shows what the agent is doing during a long iteration. `-q`
silences it; only fatal errors still print.

As each document finishes, `md2okf` also prints one tab-separated summary
line for it to standard output (unless `-q`):

```text
notes.md <tab> 2 <tab> 7f3c1a9d4e02 <tab> b481d05c6a17
```

The columns are the path as you gave it (`-` for standard input), the number
of iterations, and the root hash before and after. Because progress goes to
standard error, `md2okf notes.md > results.tsv` captures only the summary
lines.

## What lands in `okf/`

```text
okf/
├── index.md          # root index, the only index with frontmatter
├── log.md            # what each run changed, newest first
├── <page>.md         # a content page at the wiki root
└── <topic>/          # one directory per topic, nested as deep as it needs
    ├── index.md      # a plain list of links for this directory
    └── <page>.md     # a content page within the topic
```

This layout is only an example: the agent chooses the page names and how to
split each document. All file and folder names are kebab-case.

- Every content page starts with YAML frontmatter: `type` (`Chapter`,
  `Section` or `GlossaryTerm`), `title`, `description`, `tags`, and
  `generated`, which records the agent and model that wrote the page, and
  when.
- Every folder, including the root, has an `index.md` that lists the pages
  and folders directly inside it. The agent generates these files with
  `okfctl index build` rather than writing them by hand. Only the root
  `index.md` has frontmatter, with a single key, `okf_version`: the version
  of the OKF specification the wiki follows.
- `log.md` has no frontmatter. It records what each run changed, newest
  entry first.
- Links in page text are *bundle-absolute*: they start at the wiki's root, as
  in `/glossary/verb.md` rather than `glossary/verb.md`. The generated
  indexes use relative links.

`md2okf` never changes your source documents; the agent reads read-only
copies. Each run adds to the wiki already in the output directory. The agent
is told to update an existing page rather than create a duplicate, so
compiling a document again revises the wiki instead of repeating it. The
agent treats `SPEC.md` as outranking every other instruction it receives.

## Reading the result

```bash
cat okf/index.md
```

The wiki is a plain folder of Markdown files; nothing is included to serve or
display it. Read it, keep it under version control, or hand it to your own
coding agent. A line like this in your agent's `AGENTS.md` or `CLAUDE.md`
points it at the wiki instead of the raw source documents:

```markdown
Start at okf/index.md and follow its links before reading anything else.
```

Bundle-absolute links start at the wiki's root folder, so a Markdown viewer
follows them only if it treats that folder as the root. `cat` shows a page's
text, not clickable links.

## How compiling stops

For each document, `md2okf` runs the agent again and again — a *Ralph loop* —
until the wiki stops changing. After each iteration it hashes the wiki inside
the sandbox with `merkleokf --nolog -L 0`. This gives one hash per Markdown
file and per folder, so a change to any page changes the root hash. `--nolog`
leaves out the top-level `log.md`, so an iteration that only adds a log entry
counts as no change. When the root hash is the same after an iteration as
before it, the document is done.

`md2okf` stops with an error when:

- the wiki is still changing after `-n` iterations (default 10);
- an iteration fails: the agent exits with an error or reports a failure;
- an iteration makes no tool calls, which means the agent did not follow its
  instructions;
- copying the wiki to the output directory fails (the message says where the
  completed work is);
- the wiki is still empty after compiling.

An error stops the whole run: documents after the failed one are not
compiled.

A stable hash means only that the agent stopped changing the wiki, not that
the wiki is complete or correct. `md2okf` does not check the wiki's content
itself. The agent does: its instructions require it to run `check-okf.sh`
before it finishes. That script runs `okfctl validate`, `lint`, `analyze` and
`index check`, plus a check of every page's frontmatter, inside the sandbox.

## Output directory rules

The output directory, set with `-o` (default `./okf`), must be one of these:

- a path that does not exist yet, which `md2okf` creates;
- an empty folder;
- a wiki from an earlier run: a folder whose `index.md` frontmatter holds only
  `okf_version`.

Anything else — a file, a symbolic link, or a folder with other content — is
refused, so `md2okf` never overwrites unrelated files.

After every completed iteration, `md2okf` copies the wiki to the output
directory, which then matches the sandbox's copy exactly: a page the agent
deleted is deleted there too. If you interrupt a run with Ctrl-C, the output
directory keeps the result of the last completed iteration.

## Getting Markdown in

`md2okf` works best with clean, structured Markdown, and a source document is
rarely that. Two helpers in this repository can prepare it. Both are
optional, need a clone of the repository, and run separately from `md2okf`.

**From a PDF.** `pdf2md` converts a PDF with `marker`, helped by a language
model: a local Ollama model or a cloud model through OpenRouter. The step is
manual; check its output before compiling. See
[the pdf2md guide](../pdf2md/README.md).

**From a website.** `make scrape` runs `web2md`, which walks a documentation
site and writes it into one Markdown file in `md/`. No language model is
involved, so the result is deterministic, and the fetched pages are cached.
See [the web2md guide](../web2md/README.md).

## Inspecting the sandbox

```bash
md2okf --shell                            # interactive shell in the sandbox's copy of the wiki
md2okf --agent                            # interactive session with the agent
```

Both are for looking around, not for editing the wiki. They do not stage a
new run: they refresh the helper CLIs, fill in the bundled spec if the
workbench has none, and otherwise leave the workbench as the last compile
left it. Nothing is copied back to your output directory, and the next
compile replaces the sandbox's copy of the wiki, so any changes you make are
lost. `--shell` opens even when the agent's credential check fails, and
prints the fix as a warning; `--agent` refuses to start.

See [Architecture](architecture.md#inspecting-the-sandbox) for details, and
[Locking](#locking) for why other runs are refused while a session is open.

## CLI reference

| Flag | Default | Effect |
| --- | --- | --- |
| `FILE\|DIR` (positional) | stdin | Markdown files or folders to compile; `-` means standard input |
| `-o`, `--output DIR` | `okf` | the wiki's output directory |
| `--spec FILE` | the bundled `SPEC.md` | the OKF specification to compile against |
| `-n N` | `10` | the maximum number of iterations per document |
| `--fresh` | off | rebuild the sandbox even if it could be reused |
| `--dry-run` | off | check the inputs and print what would run; creates no sandbox, checks no credential, costs nothing |
| `--shell` | off | open an interactive shell in the sandbox |
| `--agent` | off | open an interactive session with the agent in the sandbox |
| `-q`, `--quiet` | off | hide progress and the summary lines (fatal errors still print) |
| `-v`, `--verbose` | off | also show the agent's tool calls and messages |
| `--version` | — | print the version and exit |
| `-h`, `--help` | — | print help, including the environment variables `md2okf` reads |

`-q` and `-v` exclude each other, as do `--shell` and `--agent`. `--dry-run`
does not even need `sbx`. With `--shell` or `--agent`, only `--fresh` may be
added: input paths are refused, and so is every other option listed above
unless it is left at its default. Both need a terminal on standard input.

`MD2OKF_AGENT` picks the agent: `pi` (the default), `claude` or `codex`.

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | every document compiled |
| `1` | the run started and then failed: a document did not compile, staging or copying the wiki failed, or you pressed Ctrl-C |
| `2` | `md2okf` refused before starting work: bad arguments or inputs, an unknown `MD2OKF_AGENT`, `sbx` missing or too old, another run holding the lock, a credential that is not ready, or a sandbox that could not be created, reused or proved to be `md2okf`'s own |

## Locking

`md2okf` allows one run at a time per user on a machine, whichever agent it
uses. It holds a lock file for as long as it runs; a second compile, or a
`--shell` or `--agent` session, is refused at once with
`md2okf: another md2okf run is using the sandbox; try again later` rather
than queued. `--shell` and `--agent` hold the lock until you leave the
session. `--dry-run` takes no lock, so it works while another run is going.
