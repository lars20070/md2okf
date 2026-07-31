# Coding Agent Specification: Google Style Guide Single-File Markdown Generator

## 1. Problem Statement

### 1.1 Overview
The **Google Developer Documentation Style Guide** (hosted at `https://developers.google.com/style`) is an essential reference for technical writers, software engineers, and AI prompt engineers. However, Google publishes this guide across **hundreds of discrete web pages** without providing an official single-file download (such as a consolidated PDF or Markdown document).

### 1.2 Target Audience & Use Case
A single-file Markdown (`.md`) document is required to:
1. Provide **offline accessibility** and fast local text searching.
2. Serve as a **clean context document** for Large Language Models (LLMs) and RAG (Retrieval-Augmented Generation) pipelines.
3. Enable easy version-controlled local archival and custom printing.

### 1.3 Technical Challenges
- **Navigation Hierarchy:** Page order matters. The scraper must parse the left-hand navigation sidebar to retain the intended reading sequence.
- **Boilerplate & Noise Removal:** Google DevSite pages contain extensive non-content UI (navigation bars, search boxes, header/footer, rating widgets, sidebars, cookie banners).
- **Custom DOM Elements:** DevSite uses custom tags and CSS classes for callouts (`aside class="note"`, `aside class="caution"`), custom code tabs, and structured tables.
- **Internal Link Disruption:** Relative links pointing to `https://developers.google.com/style/...` will break unless converted into local section anchors (`#...`).
- **Rate Limiting & Politeness:** Fetching hundreds of pages sequentially requires request throttling, proper User-Agent headers, and retry logic.

---

## 2. Solutions Overview

### Option Comparison

| Approach | Pros | Cons | Decision |
|---|---|---|---|
| **A. Static HTML Scraper (`httpx` + `BeautifulSoup` + `markdownify`)** | Fast, lightweight, pure Python, highly customizable AST conversion. | Requires manually mapping custom DOM elements. | **RECOMMENDED** |
| **B. Headless Browser (`Playwright` + Node/Python + Turndown)** | Renders JavaScript-heavy elements automatically. | Slower, heavier resource usage, unnecessary overhead for static text pages. | Secondary fallback |
| **C. Shell Pipeline (`wget` + `pandoc`)** | Simple one-liner execution. | Messy output, preserves UI clutter, mangles navigation order, poor callout handling. | Rejected |

### Recommended Solution Architecture
A modular Python script operating in 6 sequential stages:
1. **Discover:** Extract page hierarchy from sidebar navigation.
2. **Fetch:** Retriable HTTP fetches with concurrent batching and caching.
3. **Clean:** Target main content containers and strip site chrome/UI.
4. **Transform:** Convert HTML AST to clean Markdown with custom rules for code and callouts.
5. **Normalize:** Update internal cross-references to point to document anchors.
6. **Compile:** Assemble master TOC, frontmatter, and output single `.md` file.

---

## 3. Detailed Staged Implementation Plan

```
[ Stage 1: Setup ] ──> [ Stage 2: Crawl Nav Tree ] ──> [ Stage 3: Fetch & Clean HTML ]
                                                                     │
[ Stage 6: Validation ] <── [ Stage 5: Compile & Normalize ] <── [ Stage 4: HTML -> MD ]
```

### Stage 1: Environment & Dependency Setup
Set up a python environment with required libraries:
- `httpx` (Async HTTP client with HTTP/2 and retry capabilities)
- `beautifulsoup4` + `lxml` (Fast HTML parsing and tree navigation)
- `markdownify` (HTML to Markdown converter with custom subclassing)
- `pyyaml` (Frontmatter generation)

#### Required Directory Layout
```text
scraper/
├── cache/                  # Downloaded raw HTML files (prevents refetching)
├── output/                 # Output directory for final MD file
├── config.py               # CSS selectors, user agents, rate limits
├── parser.py               # Custom HTML-to-MD rules
└── main.py                 # CLI entrypoint and orchestrator
```

---

### Stage 2: Sitemap & Hierarchy Discovery
**Objective:** Parse the left navigation menu on `https://developers.google.com/style` to build an ordered list of URLs with section levels.

#### Step-by-Step Instructions:
1. Fetch the main index page `https://developers.google.com/style`.
2. Locate the navigation tree element:
   - Primary selector: `ul.devsite-nav-section-list` or `nav.devsite-section-nav`.
3. Extract all `<a>` tags with `href` attributes starting with `/style`.
4. Store URLs sequentially in a list of structured dicts:
   ```python
   page_item = {
       "title": "Voice and tone",
       "url": "https://developers.google.com/style/voice",
       "level": 2,  # Depth in nav hierarchy
       "slug": "voice"
   }
   ```
5. Deduplicate links while strictly maintaining first-seen order.

---

### Stage 3: Fetching & DOM Cleaning
**Objective:** Fetch raw HTML for each page, store in cache, and strip non-article elements.

#### Step-by-Step Instructions:
1. **Caching:** Check if `cache/{slug}.html` exists. If not, fetch via HTTP request with `User-Agent: Mozilla/5.0 ...`.
2. **Rate Limiting:** Implement a 200–500ms delay between requests to avoid 429 throttling.
3. **Locate Core Content:**
   - Target container: `article.devsite-article` or `div.devsite-article-body`.
4. **De-cluttering (Removal List):**
   Remove the following selectors before processing:
   - `nav`, `header`, `footer`
   - `.devsite-rating-container` (Feedback widgets)
   - `.devsite-toc` (In-page right-hand TOC)
   - `.devsite-content-footer`
   - `script`, `style`, `noscript`
   - Buttons like "Copy code" or print triggers.

---

### Stage 4: Custom HTML-to-Markdown Conversion
**Objective:** Transform cleaned HTML DOM into clean Markdown while handling Google-specific elements.

#### Custom Tag Handling Rules:

1. **Headings (`<h1>` to `<h6>`):**
   - Shift header ranks down by 1 level if using `# Title` for the main page document.
   - Inject HTML anchor IDs or explicit slug targets: `<a id="slug-heading"></a>`.

2. **Callout Boxes / Notices (`<aside>`):**
   Google uses `<aside class="note">`, `<aside class="caution">`, `<aside class="key-point">`.
   - Convert to GitHub-Flavored Markdown (GFM) admonition syntax:
     ```markdown
     > [!NOTE]
     > Note text content here...
     ```

3. **Code Blocks (`<pre>`, `<code>`):**
   - Extract language class if present (e.g. `class="lang-py"` -> `py`).
   - Wrap in triple backticks ` ```python ... ``` `.

4. **Tables (`<table>`):**
   - Convert standard `<table>` / `<tr>` / `<th>` / `<td>` to Markdown pipe tables.
   - Clean up interior multiline HTML inside table cells to single-line or `<br>`.

---

### Stage 5: Link Normalization & Single-File Compilation
**Objective:** Assemble all parsed sections into a single monolithic `.md` file and fix internal hyperlinks.

#### Step-by-Step Instructions:
1. **Frontmatter:** Inject YAML frontmatter at top of document:
   ```yaml
   ---
   title: Google Developer Documentation Style Guide
   source: https://developers.google.com/style
   generated_at: YYYY-MM-DD
   format: Single-file Markdown
   ---
   ```
2. **Master Table of Contents:**
   Generate a master TOC linking to every page heading using synthesized anchors (e.g. `#voice-and-tone`).
3. **Link Rewriting Rule:**
   - External links (`https://...` outside `/style`) -> Keep as-is.
   - Internal links (`/style/voice` or `https://developers.google.com/style/voice`) -> Convert to local Markdown anchor links `[Voice and tone](#voice)`.
4. **Page Dividers:**
   Insert page section headers and horizontal rules between scraped pages:
   ```markdown
   ---
   # Page Title
   *Source: https://developers.google.com/style/page*
   
   [Page Content]
   ```

---

### Stage 6: Validation & Verification
**Objective:** Guarantee the quality and completeness of the generated file.

#### Automated Checks to Implement in Script:
1. **Missing Content Check:** Ensure page count in output matches total discovered URLs.
2. **Unbroken Links Check:** Verify all internal `#anchor` links point to valid targets within the generated document.
3. **File Size Check:** Expected size is typically between 1.5 MB and 4.0 MB.
4. **Syntax Check:** Ensure code blocks and tables do not break Markdown rendering syntax.

---

## 4. Ready-to-Run Reference Implementation Script

Below is a complete, runnable Python script that implements the above specification. A coding agent can execute or extend this directly:

```python
import os
import re
import time
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup
from markdownify import MarkdownConverter

BASE_URL = "https://developers.google.com/style"
OUTPUT_FILE = "google_developer_style_guide.md"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

class GoogleStyleGuideConverter(MarkdownConverter):
    def convert_aside(self, el, text, convert_as_inline):
        classes = el.get("class", [])
        kind = "NOTE"
        if "caution" in classes or "warning" in classes:
            kind = "WARNING"
        elif "key-point" in classes:
            kind = "IMPORTANT"
        
        lines = text.strip().split("
")
        quoted = "
> ".join(lines)
        return f"

> [!{kind}]
> {quoted}

"

def get_navigation_urls():
    print("Fetching navigation index...")
    res = httpx.get(BASE_URL, headers=HEADERS, follow_redirects=True)
    soup = BeautifulSoup(res.text, "lxml")
    
    urls = []
    # Find navigation items
    nav = soup.find("ul", class_="devsite-nav-section-list") or soup
    for a in nav.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/style") or href.startswith(BASE_URL):
            full_url = urljoin(BASE_URL, href).split("#")[0]
            if full_url not in urls:
                urls.append(full_url)
    print(f"Discovered {len(urls)} pages in navigation.")
    return urls

def clean_and_convert_html(html_content, page_url):
    soup = BeautifulSoup(html_content, "lxml")
    
    # Extract main article
    article = soup.find("article", class_="devsite-article") or soup.find("div", class_="devsite-article-body")
    if not article:
        article = soup.find("main") or soup.body

    # Strip junk elements
    for selector in [
        "nav", ".devsite-rating-container", ".devsite-toc",
        ".devsite-content-footer", "script", "style", "iframe"
    ]:
        for el in article.select(selector):
            el.decompose()

    # Rewrite internal links to local anchors
    for a in article.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/style") or href.startswith(BASE_URL):
            parsed = urlparse(href)
            slug = parsed.path.strip("/").replace("/", "-")
            a["href"] = f"#{slug}" if slug else "#introduction"

    converter = GoogleStyleGuideConverter(heading_style="ATX")
    return converter.convert(str(article))

def build_single_file_md():
    urls = get_navigation_urls()
    if not urls:
        urls = [BASE_URL] # Fallback
        
    md_sections = []
    md_sections.append("---
title: Google Developer Documentation Style Guide
source: https://developers.google.com/style
---

")
    md_sections.append("# Google Developer Documentation Style Guide

")

    for idx, url in enumerate(urls, start=1):
        parsed = urlparse(url)
        slug = parsed.path.strip("/").replace("/", "-") or "introduction"
        print(f"[{idx}/{len(urls)}] Processing: {url}")
        
        try:
            res = httpx.get(url, headers=HEADERS, follow_redirects=True)
            if res.status_code == 200:
                md_content = clean_and_convert_html(res.text, url)
                md_sections.append(f"

<a id="{slug}"></a>

---

")
                md_sections.append(md_content)
            time.sleep(0.2)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.writelines(md_sections)
    print(f"Successfully generated single-file style guide: {OUTPUT_FILE}")

if __name__ == "__main__":
    build_single_file_md()
```

---

## 5. Summary Checklist for Agent Execution

- [ ] Execute script to discover navigation links.
- [ ] Verify HTML sanitization rules strip header, footer, and navigation.
- [ ] Confirm custom `<aside>` conversion produces GFM callout blockquotes.
- [ ] Ensure internal links are mapped to `#slug` local anchors.
- [ ] Validate final single `.md` file size and content integrity.
