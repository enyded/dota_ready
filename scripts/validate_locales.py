from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

from build_locales import ALL_LANGUAGES, BASE_URL, LOCALE_DIRS, absolute_url


ROOT = Path(__file__).resolve().parents[1]
XHTML = "{http://www.w3.org/1999/xhtml}"
SITEMAP = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang: str | None = None
        self.canonical: str | None = None
        self.alternates: dict[str, str] = {}
        self.description: str | None = None
        self.og_url: str | None = None
        self.h1_count = 0
        self.title_parts: list[str] = []
        self.in_title = False
        self.links: list[str] = []
        self.assets: list[str] = []
        self.json_ld_parts: list[str] = []
        self.in_json_ld = False

    def handle_starttag(self, tag: str, attrs_list: list[tuple[str, str | None]]) -> None:
        attrs = dict(attrs_list)
        if tag == "html":
            self.lang = attrs.get("lang")
        elif tag == "title":
            self.in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "link":
            rel = attrs.get("rel")
            href = attrs.get("href")
            if rel == "canonical":
                self.canonical = href
            elif rel == "alternate" and href and attrs.get("hreflang"):
                self.alternates[attrs["hreflang"] or ""] = href
            if href:
                self.assets.append(href)
        elif tag == "meta":
            if attrs.get("name") == "description":
                self.description = attrs.get("content")
            elif attrs.get("property") == "og:url":
                self.og_url = attrs.get("content")
        elif tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"] or "")
        elif tag in {"img", "script"} and attrs.get("src"):
            self.assets.append(attrs["src"] or "")
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_json_ld = True

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self.in_title = False
        elif tag == "script":
            self.in_json_ld = False

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_json_ld:
            self.json_ld_parts.append(data)


def page_path(language: str, page: str) -> Path:
    if language == "en":
        return ROOT / ("index.html" if page == "home" else "accept-dota-2-match-from-phone/index.html")
    base = ROOT / LOCALE_DIRS[language]
    return base / ("index.html" if page == "home" else "accept-dota-2-match-from-phone/index.html")


def local_path_from_url(url: str, current_page: Path) -> Path | None:
    parsed = urlparse(url)
    if parsed.scheme in {"http", "https"} and f"{parsed.scheme}://{parsed.netloc}" != BASE_URL:
        return None
    if parsed.scheme in {"http", "https"} or parsed.path.startswith("/"):
        candidate = ROOT / parsed.path.lstrip("/")
    else:
        candidate = (current_page.parent / parsed.path).resolve()
    if not parsed.path or parsed.path.endswith("/") or candidate.is_dir():
        candidate /= "index.html"
    return candidate


def validate_page(language: str, page: str, failures: list[str]) -> None:
    path = page_path(language, page)
    if not path.is_file():
        failures.append(f"missing page: {path.relative_to(ROOT)}")
        return
    source = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(source)
    expected_url = absolute_url(language, page)
    expected_alternates = {lang: absolute_url(lang, page) for lang in ALL_LANGUAGES}
    expected_alternates["x-default"] = absolute_url("en", page)
    title = "".join(parser.title_parts).strip()

    checks = {
        "html lang": parser.lang == language,
        "title": bool(title),
        "description": bool(parser.description),
        "one h1": parser.h1_count == 1,
        "self canonical": parser.canonical == expected_url,
        "matching og:url": parser.og_url == expected_url,
        "complete hreflang": parser.alternates == expected_alternates,
        "no template placeholders": "$" not in source,
        "indexable": "noindex" not in source.lower(),
    }
    for name, valid in checks.items():
        if not valid:
            failures.append(f"{path.relative_to(ROOT)}: {name}")

    try:
        structured = json.loads("".join(parser.json_ld_parts))
        if structured.get("inLanguage") != language or structured.get("url", expected_url) != expected_url:
            failures.append(f"{path.relative_to(ROOT)}: JSON-LD locale/url mismatch")
    except json.JSONDecodeError:
        failures.append(f"{path.relative_to(ROOT)}: invalid JSON-LD")

    for href in parser.links:
        if href.startswith(("#", "mailto:", "https://github.com/")):
            continue
        target = local_path_from_url(href, path)
        if target is None:
            continue
        if not target.is_file():
            failures.append(f"{path.relative_to(ROOT)}: broken link {href}")

    for asset in parser.assets:
        if asset.startswith(("http://", "https://")):
            continue
        target = (path.parent / urlparse(asset).path).resolve()
        if not target.is_file():
            failures.append(f"{path.relative_to(ROOT)}: missing asset {asset}")


def validate_sitemap(failures: list[str]) -> None:
    tree = ET.parse(ROOT / "sitemap.xml")
    urls = tree.getroot().findall(f"{SITEMAP}url")
    locations = {
        node.findtext(f"{SITEMAP}loc", default="")
        for node in urls
    }
    expected = {
        absolute_url(language, page)
        for language in ALL_LANGUAGES
        for page in ("home", "guide")
    } | {f"{BASE_URL}/{name}" for name in ("privacy.html", "terms.html", "disclaimer.html")}
    if locations != expected:
        failures.append("sitemap URL set does not match generated pages and legal pages")

    for node in urls:
        location = node.findtext(f"{SITEMAP}loc", default="")
        page = "guide" if "/accept-dota-2-match-from-phone/" in location else "home"
        if location.endswith(("privacy.html", "terms.html", "disclaimer.html")):
            continue
        alternates = {
            link.attrib["hreflang"]: link.attrib["href"]
            for link in node.findall(f"{XHTML}link")
        }
        expected_alternates = {lang: absolute_url(lang, page) for lang in ALL_LANGUAGES}
        expected_alternates["x-default"] = absolute_url("en", page)
        if alternates != expected_alternates:
            failures.append(f"sitemap incomplete alternates: {location}")


def main() -> int:
    failures: list[str] = []
    for language in ALL_LANGUAGES:
        for page in ("home", "guide"):
            validate_page(language, page, failures)
    validate_sitemap(failures)
    if failures:
        print("Localization validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"Validated {len(ALL_LANGUAGES) * 2} localized pages and sitemap.xml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
