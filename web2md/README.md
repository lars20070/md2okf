# web2md

Sometimes clean, structured Markdown files are not available, so they must be
fetched from a website and converted. This directory holds a deterministic
scraper for the [Google developer documentation style
guide](https://developers.google.com/style). The output is one file under
`md/`, ready for `make wiki-sandbox`.

The result is a dated snapshot of a living document. Re-run with `--refresh` to
update it.

## What it fetches, and what it writes

Two constants at the top of `src/web2md.py` are the only things to edit when
pointing the scraper somewhere else:

```python
SOURCE_URL = "https://developers.google.com/style"
OUTPUT_FILE = "GoogleDeveloperDocumentationStyleGuide.md"
```

`SOURCE_URL` is the book's landing page. The host, the site base URL, and the
path prefix that decides which links count as in-book (`BOOK_PATH`) are all
derived from it, so there is no second place to keep in step. `OUTPUT_FILE` is a
bare filename; the scraper always writes it into `md/`, and `--output`
overrides the whole path for a one-off run.

Changing `SOURCE_URL` to a different book will need the DevSite selectors
(`NAV`, `BODY`, `DROP`) and the sanity thresholds (page count, size band, and
the `word-list` term count in `validate_output`) revisited — they describe this
book, not the site in general.

## Layout

| Path | Contents |
| --- | --- |
| `src/web2md.py` | the scraper — a single module, run by path, not installed |
| `tests/` | the pytest suite (see below) |
| `cache/` | fetched HTML, gitignored; reused unless you pass `--refresh` |

There is no `[build-system]` and no installable package. pytest imports the
module through `pythonpath = ["web2md/src"]` in the repo's `pyproject.toml`.

## Fetch and convert

```bash
# Install scraper deps (separate from the heavy marker-pdf stack)
uv sync --group web2md

# Fetch (or reuse web2md/cache/) and write md/*.md
make scrape

# Or call the module directly:
uv run --group web2md python web2md/src/web2md.py
uv run --group web2md python web2md/src/web2md.py --refresh
```

## Tests

```bash
make test                                              # the whole suite
uv run --group test --group web2md pytest web2md/tests # the same, directly
```

The suite is fully offline: HTTP is served by `httpx.MockTransport`, so no test
opens a socket, and the only files written go to pytest's `tmp_path`. It covers
the pure helpers (slugs, anchors, link rewriting, the Markdown converter,
assembly, and every `validate_output` error branch), the constants above and
what is derived from them, the fetch retry and caching logic, and one end-to-end
`run()` over a synthetic 72-page site. CI runs it in the `test` job.

## Markdown linting

The generated file under `md/` can be checked manually with the same tools as
`pdf2md`. The filename below is the current `OUTPUT_FILE`:

```bash
prettier --check md/GoogleDeveloperDocumentationStyleGuide.md
prettier --write md/GoogleDeveloperDocumentationStyleGuide.md  # Edits in place!

markdownlint-cli2 md/GoogleDeveloperDocumentationStyleGuide.md
markdownlint-cli2 --fix md/GoogleDeveloperDocumentationStyleGuide.md  # Edits in place!

cspell md/GoogleDeveloperDocumentationStyleGuide.md
```
