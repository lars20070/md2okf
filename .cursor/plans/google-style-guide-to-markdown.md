# Google developer documentation style guide as one Markdown file

## Context

`md/` wants clean, structured Markdown. The Google developer documentation
style guide (<https://developers.google.com/style>) is published as a DevSite
book with no single-file download, so it needs a fetch-and-convert step of its
own — a sibling to `pdf2md/`, which does the same job for PDFs. The output is
one file in `md/`, and from there the existing pipeline takes over: `make
wiki-sandbox` runs Pi once per `md/*.md` file and folds it into `okf/`.

This supersedes
[.cursor/plans/google_style_guide_scraper_plan.md](.cursor/plans/google_style_guide_scraper_plan.md).
Its overall shape — discover, fetch, clean, convert, normalize links, assemble,
validate — is right and is kept. Its facts about the site are not, and its
reference script would not run. Both are corrected below against measurements
taken from the live site on 2026-07-31.

## What the site actually is (measured)

Ten pages were fetched and analysed: the landing page, `word-list`, `tone`,
`notices`, `lists`, `tables`, `code-samples`, `code-syntax`, `highlights`.

- **70 pages, not "hundreds."** The book nav is server-rendered in the HTML of
  every page: 71 `/style` anchors (one is the "Guides" tab, pointing at `/style`
  a second time) inside `.devsite-book-nav-wrapper`, grouped by 10
  `li.devsite-nav-heading` labels — Introduction, Key resources, General
  principles, Language and grammar, Punctuation, Formatting and organization,
  Linking, Computer interfaces, HTML and CSS, Names and naming. No JavaScript,
  no lazy-loaded subtree: one fetch yields the whole ordered outline.
- **`robots.txt` allows it.** `User-agent: *` with a single `Disallow:
  /youtube/partner/`. A truthful, non-browser User-Agent is served normally
  (checked: `200`), so there is no reason to spoof Mozilla as the old plan did.
- **Roughly 1.2 MB of article HTML.** Article bodies measured 5–33 KB each,
  except `word-list` at 251 KB. Extrapolated: ~1.2 MB of body HTML, which
  converts to about **0.5–0.9 MB of Markdown** — not the 1.5–4 MB the old plan
  asserts as its size check.
- **No shortcut exists.** `?print=1` returns the same single page (byte-for-byte
  the same size), `/style/_book.yaml`, `/style/_toc.yaml`, `/llms.txt` and
  `.txt` suffixes all 404, and `.md` / `?format=markdown` return the HTML page
  with `Content-Type: text/html`. The `<devsite-llm-tools>` element on each page
  is an empty JS-driven widget with no server endpoint behind it. Scraping HTML
  is the only route.
- **Every page carries an AI-generated summary inside the article body.**
  `<devsite-key-takeaways-panel>` ("Page Summary", tooltip "Generated with AI")
  sits inside `div.devsite-article-body` on all 10 sampled pages. It is not
  source content and must be stripped — the old plan's removal list misses it,
  along with `<devsite-recommendations>`, `<devsite-feedback>` and
  `<devsite-thumb-rating>`, which are also inside or adjacent to the body.
- **90% of internal links carry a fragment.** 838 of 936 `/style` links in the
  sampled bodies point at `#anchor` targets. The old plan strips fragments and
  maps every link to a bare page slug, which throws away almost all of the
  cross-referencing the guide is built on.
- **Anchor ids collide across pages.** `examples` occurs on 3 sampled pages;
  `politeness-and-use-of-please`, `list-or-table`,
  `some-things-to-avoid-where-possible` and
  `some-techniques-and-approaches-to-consider` each on 2. Merging 70 pages into
  one file therefore needs namespaced anchors, not the raw ids.
- **The word list is a definition list, and it is 40% of the guide.** 26 `<dl>`
  blocks, 598 `<dt>` terms, every one with an `id` (only 2 are not slug-safe:
  `+` and `google-play-services-SDK`). markdownify 1.2.3 does convert `dt`/`dd`,
  but into Pandoc/PHP-Markdown-Extra syntax (`term` then `:   definition`,
  source lines 521–556) that GitHub and most renderers do not support.
- **Some meaning exists only in CSS.** Counted in the sample:
  `<span class="icon-dontuse">` 148 times, `icon-avoid` 93, plus `icon-android`
  27, `icon-cloud` 9, `icon-workspace` 3. These spans are **empty** — a naive
  conversion silently drops "don't use this term" from hundreds of word-list
  entries. By contrast `compare-better` (158) and `compare-worse` (91) wrap the
  words "Recommended" / "Not recommended", so those survive on their own.
- **`material-icons` leaks the word "link" 600+ times.** Each `<dt>` ends with
  `<a href="#id"><span class="material-icons" aria-hidden="true">link</span></a>`;
  `word-list` alone has 603 occurrences.
- **Code blocks have no language.** Every one is
  `<devsite-code><pre class="devsite-click-to-copy">…</pre></devsite-code>`, and
  no `lang-*` or `language-*` class appears anywhere in the sample. The old
  plan's language extraction has nothing to extract; plain fences are correct.
- **Body headings run h2 to h4 only** (60 h2, 37 h3, 5 h4 in the sample), and
  there are 10 images, all with site-relative `src`.

## Where the old reference script breaks

- `convert_aside(self, el, text, convert_as_inline)` is the pre-1.0 markdownify
  signature. Since 1.0 the hook is `convert_<tag>(self, el, text, parent_tags)`
  (markdownify is at 1.2.3), so the method would never be called with the
  arguments it expects.
- Several string literals contain raw newlines inside non-triple quotes, and an
  f-string embeds unescaped `"` — the file as written is not valid Python.
- It declares async, concurrency, caching and retries in the prose, then fetches
  with a bare synchronous `httpx.get` in a loop, with no cache and no retry.
- `nav = soup.find("ul", class_="devsite-nav-section-list") or soup` — that class
  does not exist on the page, so the fallback silently harvests every `/style`
  link in the whole document, in DOM order rather than nav order, and loses the
  10 section groups entirely.
- Nothing removes the AI summary panel, and nothing handles `dl`/`dt`/`dd`, the
  empty semantic spans, or the icon text.

## `marker` and LLMs: no for converting, yes for checking

`marker` is the wrong tool here, and the reason is structural, not a matter of
tuning. Its job is to **recover** structure a PDF has already lost — reading
order, table geometry, headings inferred from font size — and it leans on a
language model to guess well. This source has lost nothing: DevSite ships
semantic HTML carrying the exact `id` attributes that 838 cross-links depend on.
Routing HTML through a headless-browser PDF print and then `marker` would
destroy every `href` and anchor, turn a 598-term definition list into guessed
headings or tables, cost one LLM call per page, and produce a different file on
every run — so `git diff` on a refresh would be unreadable. Deterministic HTML
parsing is lossless, free and fast (~25 s for 70 pages).

What `pdf2md` does contribute is its **checking** chain, which applies verbatim:
`prettier --check`, `markdownlint-cli2` and `cspell` over the generated file, as
documented in [pdf2md/README.md](pdf2md/README.md). Reuse it rather than
inventing a new "syntax check."

An LLM is still worth one optional, off-by-default pass: `--audit N` samples N
pages, hands the model the cleaned HTML text beside the emitted Markdown, and
asks what content disappeared. That is exactly the class of bug the CSS-only
`icon-dontuse` spans represent, and it is cheap on a sample. It must stay out of
the write path so the output stays reproducible.

The genuinely useful LLM stage is the one that already exists downstream:
`make wiki-sandbox` folds the file into OKF. Keeping the scraper deterministic
leaves that as the only nondeterministic stage in the chain. One caveat worth
watching: a ~0.6 MB source is roughly 150K tokens for a single Pi run — fine on
the 1M-context catalogue models the README describes, but the first run is the
place to confirm it.

## Decisions

- **One output file**, `md/GoogleDeveloperDocumentationStyleGuide.md`, matching
  the existing `md/TheEconomistStyleGuide2023.md` naming.
- **New `web2md/` directory**, mirroring `pdf2md/`: one Python module plus a
  README, wired into `make lint` and a `make` target.
- **Sequential fetch with an on-disk cache.** 70 pages at ~200 ms is ~25 s; the
  old plan's concurrency is complexity without a payoff, and a cache makes
  re-runs of the conversion free.
- **Deterministic output.** Same input, same bytes, so a refresh diffs cleanly.
- **Scraper dependencies in their own dependency group**, so CI's
  `uv run --only-group dev ruff` stays untouched and nobody needs `marker-pdf`
  (and torch) to scrape a website.

## Changes

### `web2md/google_style_guide.py` (new)

One module, argparse CLI, six stages. DevSite-specific selectors live in
constants at the top so pointing it at another DevSite book is a config change.

```python
BASE = "https://developers.google.com"
BOOK = f"{BASE}/style"
LOCALE = {"hl": "en"}          # pin the locale; the page honours ?hl=en
UA = "md2okf-web2md/0.1 (+https://github.com/<owner>/md2okf)"
NAV = ".devsite-book-nav-wrapper"
BODY = "div.devsite-article-body"
DROP = (
    "devsite-key-takeaways-panel", "devsite-recommendations",
    "devsite-feedback", "devsite-thumb-rating", "devsite-toc",
    ".devsite-rating-container", ".devsite-content-footer",
    ".material-icons", "[aria-hidden=true]",
    "script", "style", "noscript", "iframe",
)
```

1. **Discover.** Fetch `BOOK`, walk `li` elements under `NAV` in document
   order; `li.devsite-nav-heading` sets the current section, every other
   `li.devsite-nav-item` appends `{section, title, slug, url}`. Dedupe by URL,
   first-seen order. Assert `60 <= len(pages) <= 200` and `len(sections) >= 5`,
   and fail loudly otherwise — a silent 3-page run is the worst outcome.
2. **Fetch.** One `httpx.Client(headers={"User-Agent": UA},
   follow_redirects=True)`, `params=LOCALE`, ~200 ms between requests. Cache to
   `web2md/cache/{slug}.html`; only `--refresh` re-fetches. Retry 429 and 5xx
   with exponential backoff in an explicit loop — note that
   `httpx.HTTPTransport(retries=…)` retries connection errors only, not status
   codes.
3. **Clean.** Take `BODY`, drop everything in `DROP`, unwrap `<devsite-code>` to
   the `<pre>` it contains. Before dropping, replace the empty semantic spans
   with text: `icon-dontuse` → `Don't use:`, `icon-avoid` → `Avoid:`,
   `icon-android`/`icon-cloud`/`icon-workspace` → `(Android)`/`(Cloud)`/
   `(Workspace)`. Take the page title from the nav, not from the `h1` — the `h1`
   lives outside the article body.
4. **Convert.** Subclass `MarkdownConverter` (1.2.3 signature,
   `convert_<tag>(self, el, text, parent_tags)`; hyphens in tag names become
   underscores in method names, so `<devsite-code>` would be
   `convert_devsite_code` if it were not unwrapped in stage 3).
   - `convert_aside`: `note` → `> [!NOTE]`, `caution` → `> [!CAUTION]`,
     `warning` → `> [!WARNING]`, `success` → `> [!TIP]`, anything else →
     `> [!NOTE]` plus a warning to stderr. All four classes are confirmed
     present on `/style/notices`.
   - `convert_dt` / `convert_dd`: override the Pandoc-style default. Emit
     `<a id="{anchor}"></a>**{term}**` followed by the definition as an indented
     paragraph, so the 598 word-list ids stay reachable and the file renders on
     GitHub.
   - `convert_hN`: shift by +2 and **reuse DevSite's own `id`**, never a
     synthesized slug — the 838 fragment links target those exact strings,
     including oddities like `formatting,-punctuation,-and-organization`.
   - `convert_img`: absolutise `src` against `BASE`, keep the alt text.
   - `<pre>`: plain triple-backtick fences, no language tag.
5. **Anchors and links.** Collect every `id` in every cleaned body (759 in the
   sample — sections, headings and `dt` terms all carry them) into one map:
   `(slug, id) -> f"{slug}--{sanitize(id)}"`, where `sanitize` maps anything
   outside `[A-Za-z0-9._-]` to a stable replacement (2 cases in the whole guide:
   `+` and `google-play-services-SDK`). Emit an explicit `<a id="…"></a>` at
   each target, then rewrite:
   - `/style/x#y` and `https://developers.google.com/style/x#y` → `#x--y`
   - `/style/x` → `#x`
   - bare `#y` on page `x` → `#x--y`
   - anything else, or a `/style` target missing from the map → absolute URL,
     logged to stderr with a count.
6. **Assemble.** Frontmatter written directly (five static lines: `title`,
   `source`, `generated_at`, `pages`, `format` — no `pyyaml` dependency for
   that), then the `h1` document title, then a TOC grouped by the 10 nav
   sections, then per page an `h2` section heading, an `h3` page title, a
   `*Source: <url>*` line and the
   body. Depth budget: `#` document, `##` section, `###` page, body h2→h4,
   h3→h5, h4→h6. That lands exactly on markdownify's h6 clamp, which is why
   validation asserts no body heading is deeper than h4.

### `web2md/README.md` (new)

Same shape as `pdf2md/README.md`: what it does, the commands, and the
`prettier` / `markdownlint-cli2` / `cspell` check chain pointed at the generated
file. State plainly that the output is a snapshot of a living document and that
`--refresh` is how you update it.

### `pyproject.toml`

```toml
[dependency-groups]
dev = ["ruff>=0.8"]
web2md = [
  "httpx>=0.28.1",
  "beautifulsoup4>=4.15.0",
  "lxml>=6.1.1",
  "markdownify>=1.2.3",
]
```

Run it as `uv run --group web2md python web2md/google_style_guide.py`. `pyyaml`
from the old plan is not needed.

### `Makefile`

- Add `"web2md/README.md"` to the `markdownlint-cli2` list in `lint`.
- Add a target:

```make
# Fetch the Google developer documentation style guide into md/ as one file.
style-guide:
	uv run --group web2md python web2md/google_style_guide.py
```

`ruff check .` already covers the new module.

### `.gitignore`

Add `web2md/cache/` — raw HTML snapshots are throwaway. The generated Markdown
needs no rule; it lands in `md/`, which is ignored already.

### `.github/workflows/ci.yml` (optional)

The `paths` anchor lists no `pdf2md/**` today, so a `web2md/**` entry is a
choice rather than a fix. Add it if you want CI to lint scraper-only changes.

## Validation

In-script, exiting non-zero on failure:

1. Pages written equals pages discovered; list any that failed.
2. Every `#…` link target resolves to an emitted anchor; print the offenders.
3. No `devsite-`, no `material-icons`, and no stray Pandoc definition lines (a
   colon followed by indent) survive in the output; no body heading deeper than
   `h4` was seen.
4. Size between 0.4 MB and 1.2 MB, from the ~1.2 MB of measured body HTML —
   replacing the old 1.5–4 MB guess.
5. Word-list term count within a tolerance of the 598 measured, since a silent
   `dl` regression there would gut 40% of the guide.

Then, by hand on the host, the `pdf2md` chain:

```bash
prettier --check md/GoogleDeveloperDocumentationStyleGuide.md
markdownlint-cli2 md/GoogleDeveloperDocumentationStyleGuide.md
cspell md/GoogleDeveloperDocumentationStyleGuide.md
```

Finish with `make lint`, and a `make wiki-sandbox` run to confirm the file works
as a Pi source document. `make validate` is not needed: nothing under `pi/` or
`scripts/` changes.

## Risks

- **The nav is one selector deep.** Everything hinges on
  `.devsite-book-nav-wrapper`. Hence the count assertions in stage 1: a DevSite
  redesign should stop the run, not quietly produce a stub.
- **The guide changes under you.** The output is a dated snapshot. `whats-new`
  is part of the book, so the file records its own currency.
- **CSS-only semantics may be wider than measured.** The 10-page sample found
  five such classes. The optional `--audit` pass exists for exactly this, and a
  cheap guard is to log every `class` attribute value dropped during cleaning,
  so a new one shows up as a line of output rather than as missing content.
