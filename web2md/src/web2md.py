"""Fetch the Google developer documentation style guide into one Markdown file."""

from __future__ import annotations

import argparse
import re
import sys
import time
import warnings
from dataclasses import dataclass
from datetime import UTC, datetime
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, NavigableString, Tag
from markdownify import ATX, MarkdownConverter

BASE = "https://developers.google.com"
BOOK = f"{BASE}/style"
LOCALE = {"hl": "en"}
UA = "md2okf-web2md/0.1 (+https://github.com/lars20070/md2okf)"
NAV = ".devsite-book-nav-wrapper"
BODY = "div.devsite-article-body"
DROP = (
    "devsite-key-takeaways-panel",
    "devsite-recommendations",
    "devsite-feedback",
    "devsite-thumb-rating",
    "devsite-toc",
    ".devsite-rating-container",
    ".devsite-content-footer",
    ".material-icons",
    "[aria-hidden=true]",
    "script",
    "style",
    "noscript",
    "iframe",
)
ICON_TEXT = {
    "icon-dontuse": "Don't use:",
    "icon-avoid": "Avoid:",
    "icon-android": "(Android)",
    "icon-cloud": "(Cloud)",
    "icon-workspace": "(Workspace)",
}
ASIDE_KIND = {
    "note": "NOTE",
    "caution": "CAUTION",
    "warning": "WARNING",
    "success": "TIP",
}
REQUEST_DELAY_S = 0.2
MAX_RETRIES = 5
WORD_LIST_TERM_EXPECTED = 598
WORD_LIST_TERM_TOLERANCE = 30
SIZE_MIN = 0.4 * 1024 * 1024
SIZE_MAX = 1.2 * 1024 * 1024

# web2md/ — the module itself lives one level down, in web2md/src/.
ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CACHE = ROOT / "cache"
DEFAULT_OUTPUT = ROOT.parent / "md" / "GoogleDeveloperDocumentationStyleGuide.md"

_SANITIZE_RE = re.compile(r"[^A-Za-z0-9._-]")
_MD_LINK_RE = re.compile(r"\[([^\]]*)\]\((#[^)]+)\)")
# Unbounded run of '#' on purpose: validate_output filters on len(group) > 6, so
# capping the group at 6 would make that check unreachable.
_HEADING_RE = re.compile(r"^(#+)\s+", re.MULTILINE)
_PANDOC_DD_RE = re.compile(r"^:\s{3,}", re.MULTILINE)
_DEVSITE_RE = re.compile(r"devsite-|material-icons", re.IGNORECASE)


@dataclass(frozen=True)
class Page:
    """One page of the book, as listed in the site navigation.

    `slug` is the anchor this page gets in the assembled document; `path` is the
    site-relative URL path used to resolve cross-page links.
    """

    section: str
    title: str
    slug: str
    url: str
    path: str


def slug_from_path(path: str) -> str:
    """Derive a page slug from its URL path; the book root becomes "style"."""
    rest = path.removeprefix("/style").strip("/")
    return rest or "style"


def sanitize_id(raw: str) -> str:
    """Reduce an HTML id to `[A-Za-z0-9._-]`, escaping anything else as uXXXX.

    The escape is reversible enough to stay unique, so two distinct ids never
    collapse onto the same anchor.
    """

    def repl(match: re.Match[str]) -> str:
        return f"u{ord(match.group(0)):04x}"

    cleaned = _SANITIZE_RE.sub(repl, raw)
    return cleaned or "id"


def namespaced_anchor(page_slug: str, raw_id: str) -> str:
    """Scope an id to its page, so ids repeated across pages stay distinct."""
    return f"{page_slug}--{sanitize_id(raw_id)}"


def nav_text(el: Tag) -> str:
    """Read a nav entry's label, preferring its `.devsite-nav-text` span."""
    span = el.select_one(".devsite-nav-text")
    text = span.get_text(" ", strip=True) if span else el.get_text(" ", strip=True)
    return unescape(text)


def discover_pages(html: str) -> list[Page]:
    """List every book page from the nav, in document order.

    Raises SystemExit if the nav is missing or its shape looks wrong, so a
    silently truncated book fails the run instead of producing a short document.
    """
    soup = BeautifulSoup(html, "lxml")
    nav = soup.select_one(NAV)
    if nav is None:
        raise SystemExit(f"navigation not found: selector {NAV!r}")

    pages: list[Page] = []
    seen: set[str] = set()
    sections: list[str] = []
    current_section: str | None = None

    for li in nav.find_all("li", recursive=True):
        classes = li.get("class") or []
        if "devsite-nav-heading" in classes:
            current_section = nav_text(li) or current_section
            if current_section and current_section not in sections:
                sections.append(current_section)
            continue
        if current_section is None:
            # Skip book-picker tabs (e.g. "Guides") that sit above the outline.
            continue
        if "devsite-nav-item" not in classes:
            continue
        link = li.find("a", href=True)
        if link is None:
            continue
        href = link["href"].split("?")[0].split("#")[0]
        if not href.startswith("/style"):
            continue
        full = urljoin(BASE, href)
        if full in seen:
            continue
        seen.add(full)
        path = urlparse(full).path.rstrip("/") or "/style"
        pages.append(
            Page(
                section=current_section,
                title=nav_text(link),
                slug=slug_from_path(path),
                url=full,
                path=path,
            )
        )

    if not (60 <= len(pages) <= 200):
        raise SystemExit(f"unexpected page count: {len(pages)} (want 60–200)")
    if len(sections) < 5:
        raise SystemExit(f"unexpected section count: {len(sections)} (want ≥5)")
    print(f"Discovered {len(pages)} pages in {len(sections)} sections.", file=sys.stderr)
    return pages


def fetch_html(
    client: httpx.Client,
    url: str,
    cache_path: Path,
    *,
    refresh: bool,
) -> str:
    """Return the page HTML, from `cache_path` when possible.

    On a cache miss the request is retried with exponential backoff, bounded by
    MAX_RETRIES and capped at 30s per wait, honouring `Retry-After` on HTTP 429.
    Only a successful response is cached. Raises SystemExit once the retry
    budget is spent.
    """
    if cache_path.exists() and not refresh:
        return cache_path.read_text(encoding="utf-8")

    delay = REQUEST_DELAY_S
    last_error: Exception | None = None
    for attempt in range(MAX_RETRIES):
        try:
            response = client.get(url, params=LOCALE)
            if response.status_code == 429 or response.status_code >= 500:
                retry_after = response.headers.get("Retry-After")
                wait = float(retry_after) if retry_after and retry_after.isdigit() else delay
                print(
                    f"  retry {attempt + 1}/{MAX_RETRIES} after HTTP {response.status_code}"
                    f" ({wait:.1f}s): {url}",
                    file=sys.stderr,
                )
                time.sleep(wait)
                delay = min(delay * 2, 30.0)
                continue
            response.raise_for_status()
            text = response.text
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(text, encoding="utf-8")
            time.sleep(REQUEST_DELAY_S)
            return text
        except httpx.HTTPError as exc:
            last_error = exc
            print(
                f"  retry {attempt + 1}/{MAX_RETRIES} after {exc!r} ({delay:.1f}s): {url}",
                file=sys.stderr,
            )
            time.sleep(delay)
            delay = min(delay * 2, 30.0)

    raise SystemExit(f"failed to fetch {url}: {last_error}")


def replace_icon_spans(body: Tag) -> None:
    """Turn DevSite's empty icon spans into the words they stand for.

    Only inside definition terms: the word-list legend uses the same spans next
    to prose that already explains them, where the replacement would duplicate.
    """
    for class_name, label in ICON_TEXT.items():
        for el in body.select(f".{class_name}"):
            if el.find_parent("dt") is None:
                continue
            el.clear()
            el.append(NavigableString(f"{label} "))


def unwrap_devsite_code(body: Tag) -> None:
    """Replace each <devsite-code> wrapper with the <pre> it holds."""
    for el in body.find_all("devsite-code"):
        pre = el.find("pre")
        if pre is not None:
            el.replace_with(pre.extract())
        else:
            el.unwrap()


def drop_noise(body: Tag, dropped_classes: set[str]) -> None:
    """Strip site chrome listed in DROP, recording removed classes for the log."""
    for selector in DROP:
        for el in body.select(selector):
            for cls in el.get("class") or []:
                dropped_classes.add(cls)
            el.decompose()

    # Permalink icons leave empty <a href="#…"> shells once material-icons go.
    for a in list(body.find_all("a", href=True)):
        if not a.get_text(strip=True) and not a.find("img"):
            a.decompose()


def clean_body(html: str, page: Page, dropped_classes: set[str]) -> Tag:
    """Extract the article body and strip it down to publishable content.

    Raises SystemExit if the body is missing, or if its headings fall outside
    the h2–h4 range the assembled document's +2 shift assumes.
    """
    soup = BeautifulSoup(html, "lxml")
    body = soup.select_one(BODY)
    if body is None:
        raise SystemExit(f"missing article body on {page.url} (selector {BODY!r})")

    replace_icon_spans(body)
    unwrap_devsite_code(body)
    drop_noise(body, dropped_classes)

    # Heading depth check before conversion. The body is expected to use h2–h4:
    # deeper would overflow h6 once assemble() shifts everything down by two,
    # and an h1 would compete with the document title.
    for heading in body.find_all(re.compile(r"^h[1-6]$")):
        level = int(heading.name[1])
        if level > 4:
            raise SystemExit(f"body heading deeper than h4 on {page.url}: <{heading.name}>")
        if level < 2 and heading.get("id") != "key-takeaways-panel-title":
            raise SystemExit(f"unexpected <h1> in the article body on {page.url}")

    return body


def collect_ids(body: Tag, page_slug: str, anchor_map: dict[tuple[str, str], str]) -> None:
    """Record every id on the page as (page_slug, raw_id) -> namespaced anchor."""
    for el in body.find_all(attrs={"id": True}):
        raw_id = el["id"]
        if not raw_id or raw_id == "key-takeaways-panel-title":
            continue
        key = (page_slug, raw_id)
        anchor_map[key] = namespaced_anchor(page_slug, raw_id)


def absolutize_url(href: str) -> str:
    """Resolve a possibly site-relative href against the site base URL."""
    return urljoin(BASE, href)


def rewrite_internal_href(
    href: str,
    page: Page,
    pages_by_path: dict[str, Page],
    anchor_map: dict[tuple[str, str], str],
    unresolved: list[str],
) -> str:
    """Rewrite one href for the single-document output.

    In-book targets become `#anchor` fragments; anything else is left alone or
    made absolute. Targets that cannot be resolved are appended to `unresolved`
    and fall back to an absolute URL, so no link is silently dropped.
    """
    parsed = urlparse(href)
    fragment = parsed.fragment

    # Same-page fragment.
    if (not parsed.scheme and not parsed.netloc and not parsed.path) or href.startswith("#"):
        if not fragment:
            return href
        key = (page.slug, fragment)
        if key in anchor_map:
            return f"#{anchor_map[key]}"
        unresolved.append(f"{page.url} -> {href}")
        return absolutize_url(f"{page.path}#{fragment}")

    # Absolute or site-relative /style/... links.
    if parsed.netloc and parsed.netloc != "developers.google.com":
        return href
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return href

    path = parsed.path.rstrip("/") or "/"
    if not path.startswith("/style"):
        if href.startswith("/") or parsed.netloc == "developers.google.com":
            return absolutize_url(href)
        return href

    target_path = path if path != "/style" else "/style"
    target_page = pages_by_path.get(target_path)
    if target_page is None and target_path == "/style":
        target_page = pages_by_path.get("/style")

    if fragment:
        if target_page is None:
            unresolved.append(f"{page.url} -> {href}")
            return absolutize_url(href)
        key = (target_page.slug, fragment)
        if key in anchor_map:
            return f"#{anchor_map[key]}"
        unresolved.append(f"{page.url} -> {href}")
        return absolutize_url(href)

    if target_page is not None:
        return f"#{target_page.slug}"
    unresolved.append(f"{page.url} -> {href}")
    return absolutize_url(href)


def apply_anchors_and_links(
    body: Tag,
    page: Page,
    pages_by_path: dict[str, Page],
    anchor_map: dict[tuple[str, str], str],
    unresolved: list[str],
) -> None:
    """Emit explicit anchors for id-bearing elements and rewrite links in place.

    Mutates `body`: ids move onto injected <a id="…"> tags, hrefs are rewritten
    for the single-document output, and image sources are made absolute.
    """
    # Inject an explicit anchor before every id-bearing element (sections,
    # headings, dt terms, …). markdownify drops ids on non-heading tags, and
    # many DevSite fragments live on <section id="…"> wrappers. DevSite often
    # repeats the same id on a section and its heading — emit it once.
    soup = body
    while soup.parent is not None:
        soup = soup.parent
    emitted: set[str] = set()
    for el in list(body.find_all(attrs={"id": True})):
        raw_id = el["id"]
        key = (page.slug, raw_id)
        if key not in anchor_map:
            continue
        namespaced = anchor_map[key]
        if namespaced not in emitted:
            anchor_tag = soup.new_tag("a", attrs={"id": namespaced})
            el.insert_before(anchor_tag)
            emitted.add(namespaced)
        del el["id"]

    for a in body.find_all("a", href=True):
        a["href"] = rewrite_internal_href(
            a["href"], page, pages_by_path, anchor_map, unresolved
        )

    for img in body.find_all("img", src=True):
        img["src"] = absolutize_url(img["src"])


class StyleGuideConverter(MarkdownConverter):
    """DevSite-specific HTML → Markdown rules."""

    class Options(MarkdownConverter.Options):
        """markdownify settings this book is converted with."""

        heading_style = ATX
        bullets = "-"
        escape_asterisks = False
        escape_underscores = False

    def __init__(self, page_slug: str, aside_warnings: list[str], **options: Any) -> None:
        """Bind the converter to one page; `aside_warnings` collects warnings."""
        super().__init__(**options)
        self.page_slug = page_slug
        self.aside_warnings = aside_warnings

    def convert_aside(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        """Render an <aside> as a GitHub callout, defaulting to NOTE."""
        classes = el.get("class") or []
        kind = "NOTE"
        matched = False
        for cls, mapped in ASIDE_KIND.items():
            if cls in classes:
                kind = mapped
                matched = True
                break
        if not matched and classes:
            self.aside_warnings.append(f"unknown aside class {classes!r} on {self.page_slug}")
        lines = [line for line in text.strip().splitlines() if line.strip()]
        if not lines:
            return "\n\n"
        quoted = "\n> ".join(lines)
        return f"\n\n> [!{kind}]\n> {quoted}\n\n"

    def convert_a(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        """Convert a link, preserving the bare <a id="…"> anchors we injected.

        markdownify would otherwise drop an empty anchor that has an id and no
        href, taking every cross-reference target with it.
        """
        anchor_id = el.get("id")
        if anchor_id and not el.get("href") and not (text or "").strip():
            return f'<a id="{anchor_id}"></a>'
        return super().convert_a(el, text, parent_tags)

    def process_text(
        self, el: NavigableString, parent_tags: set[str] | None = None
    ) -> str:
        """Escape literal Markdown fences that appear in prose.

        DevSite documents mention ``` as prose; left alone those open a fence
        and swallow the content that follows.
        """
        text = super().process_text(el, parent_tags=parent_tags)
        if parent_tags is None or "pre" not in parent_tags:
            text = text.replace("```", r"\`\`\`")
        return text

    def convert_dt(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        """Render a definition term as a bold line.

        Markdown has no definition lists; bold term plus indented body keeps the
        structure readable and avoids Pandoc-only syntax.
        """
        text = re.sub(r"\s+", " ", (text or "").strip())
        if "_inline" in parent_tags:
            return f" {text} "
        if not text:
            return "\n"
        return f"\n\n**{text}**\n"

    def convert_dd(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        """Render a definition body as a four-space indented block."""
        text = (text or "").strip()
        if "_inline" in parent_tags:
            return f" {text} "
        if not text:
            return "\n"
        indented = "\n".join(
            f"    {line}" if line.strip() else "" for line in text.splitlines()
        )
        return f"\n{indented}\n"

    def convert_hN(self, n: int, el: Tag, text: str, parent_tags: set[str]) -> str:
        """Shift a body heading down two levels, clamped to h6.

        The document already spends # / ## / ### on title / section / page.
        """
        if "_inline" in parent_tags:
            return text
        n = max(1, min(6, n + 2))
        text = re.sub(r"\s+", " ", (text or "").strip())
        if not text:
            return "\n\n"
        return f"\n\n{'#' * n} {text}\n\n"

    def convert_img(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        """Render an image, degrading to its alt text when there is no source."""
        alt = el.get("alt") or ""
        src = el.get("src") or ""
        if not src:
            return alt
        return f"![{alt}]({src})"

    def convert_pre(self, el: Tag, text: str, parent_tags: set[str]) -> str:
        """Render a code block as an unlabelled fence, always newline-terminated."""
        code = el.get_text().removeprefix("\n")
        if not code.endswith("\n"):
            code = code + "\n"
        return f"\n\n```\n{code}```\n\n"


def convert_body(body: Tag, page_slug: str, aside_warnings: list[str]) -> str:
    """Convert one cleaned article body to Markdown."""
    converter = StyleGuideConverter(page_slug=page_slug, aside_warnings=aside_warnings)
    return converter.convert(str(body)).strip()


def build_toc(pages: list[Page]) -> str:
    """Render the table of contents, grouped by section in nav order."""
    lines = ["## Table of contents", ""]
    current_section = None
    for page in pages:
        if page.section != current_section:
            if current_section is not None:
                lines.append("")
            current_section = page.section
            lines.append(f"### {current_section}")
            lines.append("")
        lines.append(f"- [{page.title}](#{page.slug})")
    lines.append("")
    return "\n".join(lines)


def assemble(pages: list[Page], bodies: dict[str, str], timestamp: str) -> str:
    """Join frontmatter, table of contents, and every page body into one file."""
    parts: list[str] = [
        "---",
        "type: Website",
        'title: "Google. Google Developer Documentation Style Guide."',
        'description: "Style guide for Google developer documentation"',
        f"resource: {BOOK}",
        "tags: [guide, Google]",
        f"timestamp: {timestamp}",
        "---",
        "",
        "# Google Developer Documentation Style Guide",
        "",
        f"*Snapshot of [{BOOK}]({BOOK}) generated {timestamp[:10]}.*",
        "",
        build_toc(pages),
    ]

    current_section = None
    for page in pages:
        if page.section != current_section:
            current_section = page.section
            parts.append(f"## {current_section}")
            parts.append("")
        parts.append(f'<a id="{page.slug}"></a>')
        parts.append("")
        parts.append(f"### {page.title}")
        parts.append("")
        parts.append(f"*Source: <{page.url}>*")
        parts.append("")
        parts.append(bodies[page.slug])
        parts.append("")
        parts.append("---")
        parts.append("")

    # Drop trailing divider.
    while parts and parts[-1] in ("", "---"):
        parts.pop()
    parts.append("")
    return "\n".join(parts)


def markdown_without_fences(md: str) -> str:
    """Strip fenced code blocks so example HTML does not trip content checks."""
    return re.sub(r"```.*?```", "", md, flags=re.DOTALL)


def validate_output(md: str, pages: list[Page], bodies: dict[str, str]) -> None:
    """Check the assembled document before it is written.

    Every failure is collected and reported together, then raises SystemExit, so
    one run surfaces all the problems rather than only the first.
    """
    errors: list[str] = []

    if len(bodies) != len(pages):
        missing = [p.slug for p in pages if p.slug not in bodies]
        errors.append(f"pages written ({len(bodies)}) != discovered ({len(pages)}): {missing}")

    emitted_anchors = set(re.findall(r'<a id="([^"]+)"></a>', md))
    emitted_anchors.update(p.slug for p in pages)
    for match in re.finditer(r'id="([^"]+)"', md):
        emitted_anchors.add(match.group(1))

    broken: list[str] = []
    for label, target in _MD_LINK_RE.findall(md):
        anchor = target[1:]  # strip #
        if anchor not in emitted_anchors:
            broken.append(f"[{label}]({target})")
    if broken:
        sample = "; ".join(broken[:20])
        more = f" (+{len(broken) - 20} more)" if len(broken) > 20 else ""
        errors.append(f"{len(broken)} broken internal links: {sample}{more}")

    prose = markdown_without_fences(md)
    if _DEVSITE_RE.search(prose):
        errors.append("output still contains 'devsite-' or 'material-icons' outside code fences")
    if _PANDOC_DD_RE.search(md):
        errors.append("output still contains Pandoc-style definition list markers")

    deep = [m.group(0).strip() for m in _HEADING_RE.finditer(md) if len(m.group(1)) > 6]
    if deep:
        errors.append(f"headings deeper than h6 found: {deep[:5]}")

    size = len(md.encode("utf-8"))
    if not (SIZE_MIN <= size <= SIZE_MAX):
        errors.append(
            f"output size {size / 1024 / 1024:.2f} MB outside "
            f"{SIZE_MIN / 1024 / 1024:.1f}–{SIZE_MAX / 1024 / 1024:.1f} MB"
        )

    word_list = bodies.get("word-list", "")
    # Definition terms are emitted as <a id="word-list--…"></a> then **term**.
    term_count = len(
        re.findall(r'<a id="word-list--[^"]+"></a>\s*\*\*', word_list)
    )
    low = WORD_LIST_TERM_EXPECTED - WORD_LIST_TERM_TOLERANCE
    high = WORD_LIST_TERM_EXPECTED + WORD_LIST_TERM_TOLERANCE
    if not (low <= term_count <= high):
        errors.append(
            f"word-list term count {term_count} outside {low}–{high} "
            f"(expected ~{WORD_LIST_TERM_EXPECTED})"
        )

    if errors:
        for err in errors:
            print(f"VALIDATION ERROR: {err}", file=sys.stderr)
        raise SystemExit(1)

    print(
        f"Validation OK: {len(pages)} pages, {size / 1024 / 1024:.2f} MB, "
        f"{term_count} word-list terms, {len(emitted_anchors)} anchors.",
        file=sys.stderr,
    )


def run(*, refresh: bool, cache_dir: Path, output: Path) -> None:
    """Fetch, clean, convert, validate, and write the whole book.

    Nothing is written to `output` unless validation passes, so a failed run
    leaves the previous snapshot intact.
    """
    warnings.filterwarnings("ignore", category=UserWarning, module="bs4")
    cache_dir.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)

    with httpx.Client(
        headers={"User-Agent": UA},
        follow_redirects=True,
        timeout=60.0,
    ) as client:
        index_html = fetch_html(
            client, BOOK, cache_dir / "_index.html", refresh=refresh
        )
        pages = discover_pages(index_html)
        pages_by_path = {p.path: p for p in pages}

        cleaned: dict[str, Tag] = {}
        dropped_classes: set[str] = set()
        for i, page in enumerate(pages, start=1):
            print(f"[{i}/{len(pages)}] {page.url}", file=sys.stderr)
            html = fetch_html(
                client, page.url, cache_dir / f"{page.slug}.html", refresh=refresh
            )
            cleaned[page.slug] = clean_body(html, page, dropped_classes)

        if dropped_classes:
            print(
                "Dropped class values seen during cleaning: "
                + ", ".join(sorted(dropped_classes)),
                file=sys.stderr,
            )

        anchor_map: dict[tuple[str, str], str] = {}
        for page in pages:
            collect_ids(cleaned[page.slug], page.slug, anchor_map)

        unresolved: list[str] = []
        aside_warnings: list[str] = []
        bodies: dict[str, str] = {}
        for page in pages:
            body = cleaned[page.slug]
            apply_anchors_and_links(
                body, page, pages_by_path, anchor_map, unresolved
            )
            bodies[page.slug] = convert_body(body, page.slug, aside_warnings)

        if unresolved:
            print(
                f"{len(unresolved)} internal targets rewritten to absolute URLs "
                f"(missing from map). Sample: {unresolved[:10]}",
                file=sys.stderr,
            )
        for warning in aside_warnings:
            print(f"WARNING: {warning}", file=sys.stderr)

        md = assemble(
            pages,
            bodies,
            timestamp=datetime.now(tz=UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        validate_output(md, pages, bodies)
        output.write_text(md, encoding="utf-8")
        print(f"Wrote {output}", file=sys.stderr)


def main(argv: list[str] | None = None) -> None:
    """Parse the command line and run the scrape."""
    parser = argparse.ArgumentParser(
        description="Fetch developers.google.com/style into one Markdown file."
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        help="re-fetch pages even if a cache entry exists",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=DEFAULT_CACHE,
        help=f"HTML cache directory (default: {DEFAULT_CACHE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"output Markdown path (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args(argv)
    run(refresh=args.refresh, cache_dir=args.cache_dir, output=args.output)


if __name__ == "__main__":
    main()
