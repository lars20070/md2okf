# web2md

Sometimes clean, structured Markdown files are not available, so they must be
fetched from a website and converted. This directory holds a deterministic
scraper for the [Google developer documentation style
guide](https://developers.google.com/style). The output is one file under
`md/`, ready for `make wiki-sandbox`.

The result is a dated snapshot of a living document. Re-run with `--refresh` to
update it.

## Fetch and convert

```bash
# Install scraper deps (separate from the heavy marker-pdf stack)
uv sync --group web2md

# Fetch (or reuse web2md/cache/) and write md/GoogleDeveloperDocumentationStyleGuide.md
make style-guide

# Or call the module directly:
uv run --group web2md python web2md/web2md.py
uv run --group web2md python web2md/web2md.py --refresh
```

## Markdown linting

The generated file under `md/` can be checked manually with the same tools as
`pdf2md`:

```bash
prettier --check md/GoogleDeveloperDocumentationStyleGuide.md
prettier --write md/GoogleDeveloperDocumentationStyleGuide.md  # Edits in place!

markdownlint-cli2 md/GoogleDeveloperDocumentationStyleGuide.md
markdownlint-cli2 --fix md/GoogleDeveloperDocumentationStyleGuide.md  # Edits in place!

cspell md/GoogleDeveloperDocumentationStyleGuide.md
```
