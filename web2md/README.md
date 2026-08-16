# web2md

`md/` wants clean, structured Markdown. When the source is a documentation site
rather than a file, this scraper walks it and writes one Markdown document into
`md/`, ready for `make wiki`. It targets the [Google developer documentation
style guide](https://developers.google.com/style).

No language model is involved, so the result is deterministic — unlike the PDF
step next door. It is a dated snapshot of a living document; re-run with
`--refresh` to update it.

## What it fetches, and what it writes

Two constants at the top of `src/web2md.py` are the only things to edit when
pointing the scraper somewhere else:

```python
SOURCE_URL = "https://developers.google.com/style"
OUTPUT_FILE = "GoogleStyleGuide.md"
```

`SOURCE_URL` is the book's landing page. The host, the site base URL, and the
path prefix that decides which links count as in-book (`BOOK_PATH`) are all
derived from it, so there is no second place to keep in step. `OUTPUT_FILE` is a
bare filename; the scraper always writes it into `md/`, and `--output` overrides
the whole path for a one-off run.

Point `SOURCE_URL` at a different book and you will also need to revisit the
DevSite selectors (`NAV`, `BODY`, `DROP`) and the sanity thresholds (page count,
size band, and the `word-list` term count in `validate_output`). They describe
this book, not the site in general.

## Layout

| Path | Contents |
| --- | --- |
| `src/web2md.py` | the scraper — a single module, run by path, not installed |
| `tests/` | the pytest suite (see below) |
| `cache/` | fetched HTML, gitignored; reused unless you pass `--refresh` |

This is the only first-party Python in the repo, and its own uv project:
`web2md/pyproject.toml` holds the scraper's dependencies, the pytest config and
the only `[tool.ruff]` in the repo, with a `uv.lock` of its own. Nothing is
shared with `pdf2md` — the heavy `marker` stack cannot reach this project.
There is still no `[build-system]` and no installable package: `make scrape`
runs the module by path, and pytest imports it through `pythonpath = ["src"]`,
relative to `web2md/pyproject.toml`.

## Fetch and convert

```bash
# Install scraper deps (its own project, so no marker-pdf stack in sight)
uv sync --project web2md

# Fetch (or reuse web2md/cache/) and write md/*.md
make scrape

# Or call the module directly:
uv run --project web2md python web2md/src/web2md.py
uv run --project web2md python web2md/src/web2md.py --refresh
```

## Tests

```bash
make test-web2md   # the whole suite

# The same, directly. -c points pytest at this project's config, whose
# testpaths and pythonpath are relative to it.
uv run --project web2md --group test pytest -c web2md/pyproject.toml
```

The suite is offline: HTTP is served by `httpx.MockTransport`, so no test opens
a socket, and the only files written go to pytest's `tmp_path`. It never touches
`web2md/cache/`. It covers the pure helpers (slugs, anchors, link rewriting, the
Markdown converter, assembly, and every `validate_output` error branch), the
constants above and what is derived from them, the fetch retry and caching
logic, and one end-to-end `run()` over a synthetic 72-page site. CI runs it in
the `test-web2md` job.

## Markdown linting

Check the generated file under `md/` by hand, with the same tools as `pdf2md`.
The filename below is the current `OUTPUT_FILE`:

```bash
prettier --check md/GoogleStyleGuide.md
prettier --write md/GoogleStyleGuide.md  # Edits in place!

markdownlint-cli2 md/GoogleStyleGuide.md
markdownlint-cli2 --fix md/GoogleStyleGuide.md  # Edits in place!

cspell md/GoogleStyleGuide.md
```
