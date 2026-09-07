from __future__ import annotations

import json
from html import escape
from pathlib import Path
from string import Template
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://re-accept.com"
PLAY_STORE_URL = "https://play.google.com/store/apps/details?id=com.dotaremoteaccept"
LOCALE_DIRS = {
    "de": "de",
    "es": "es",
    "id": "id",
    "pl": "pl",
    "pt-BR": "pt-br",
    "ru": "ru",
    "tr": "tr",
    "uk": "uk",
    "vi": "vi",
}
ALL_LANGUAGES = ("en", *LOCALE_DIRS)
LANGUAGE_NAMES = {
    "en": "English",
    "de": "Deutsch",
    "es": "Español",
    "id": "Bahasa Indonesia",
    "pl": "Polski",
    "pt-BR": "Português (Brasil)",
    "ru": "Русский",
    "tr": "Türkçe",
    "uk": "Українська",
    "vi": "Tiếng Việt",
}
LAST_MODIFIED = "2026-08-27"


def absolute_url(language: str, page: str) -> str:
    if language == "en":
        suffix = "/" if page == "home" else "/accept-dota-2-match-from-phone/"
    else:
        prefix = LOCALE_DIRS[language]
        suffix = f"/{prefix}/" if page == "home" else f"/{prefix}/accept-dota-2-match-from-phone/"
    return f"{BASE_URL}{suffix}"


def hreflang_links(page: str) -> str:
    links = [
        f'  <link rel="alternate" hreflang="{language}" href="{absolute_url(language, page)}">'
        for language in ALL_LANGUAGES
    ]
    links.append(
        f'  <link rel="alternate" hreflang="x-default" href="{absolute_url("en", page)}">'
    )
    return "\n".join(links)


def language_switcher(current: str, page: str) -> str:
    links = []
    for language in ALL_LANGUAGES:
        current_attr = ' aria-current="page"' if language == current else ""
        links.append(
            f'<a lang="{escape(language)}" href="{absolute_url(language, page)}"{current_attr}>'
            f'{escape(LANGUAGE_NAMES[language])}</a>'
        )
    return (
        '<details class="language-switcher">'
        f'<summary>{escape(LANGUAGE_NAMES[current])}</summary>'
        f'<div class="language-menu">{"".join(links)}</div>'
        "</details>"
    )


def render_steps(items: list[dict[str, str]], image_prefix: str, images: list[str]) -> str:
    result = []
    for index, item in enumerate(items, start=1):
        image = ""
        if index <= len(images):
            image = (
                f'<img class="step-shot" src="{image_prefix}{images[index - 1]}?rev=20260820-1" '
                f'alt="{escape(item["alt"])}" loading="lazy">'
            )
        result.append(
            f'<li><span class="step-num">{index}</span><div><h3>{escape(item["title"])}</h3>'
            f'<p>{escape(item["text"])}</p>{image}</div></li>'
        )
    return "\n".join(result)


def render_features(items: list[dict[str, str]]) -> str:
    return "\n".join(
        f'<div class="feature"><h3>{escape(item["title"])}</h3><p>{escape(item["text"])}</p></div>'
        for item in items
    )


def render_background(items: list[dict[str, str]], image_prefix: str) -> str:
    images = ("app-settings.png", "app-info.png", "app-allow-bg-activity.png")
    return "\n".join(
        f'<figure><img src="{image_prefix}{image}?rev=20260820-1" '
        f'alt="{escape(item["alt"])}" loading="lazy">'
        f'<figcaption>{index}. {escape(item["caption"])}</figcaption></figure>'
        for index, (item, image) in enumerate(zip(items, images, strict=True), start=1)
    )


def render_faq(items: list[dict[str, str]]) -> str:
    return "\n".join(
        f'<details><summary>{escape(item["question"])}</summary><p>{escape(item["answer"])}</p></details>'
        for item in items
    )


def render_home(language: str, catalog: dict[str, Any], template: Template) -> str:
    common = catalog["common"]
    page = catalog["home"]
    locale_dir = LOCALE_DIRS[language]
    canonical = absolute_url(language, "home")
    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": "ReAccept",
            "applicationCategory": "UtilitiesApplication",
            "operatingSystem": "Windows, Android",
            "url": canonical,
            "inLanguage": language,
            "description": page["description"],
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "USD",
                "description": page["offer_description"],
            },
        },
        ensure_ascii=False,
        indent=2,
    )
    values = {
        **{key: escape(str(value)) for key, value in common.items()},
        **{key: escape(str(value)) for key, value in page.items() if isinstance(value, str)},
        "lang": language,
        "canonical": canonical,
        "hreflang": hreflang_links("home"),
        "language_switcher": language_switcher(language, "home"),
        "guide_url": absolute_url(language, "guide"),
        "play_store_url": PLAY_STORE_URL,
        "assets": "../assets/",
        "styles": "../styles.css?rev=20260907-1",
        "privacy_url": f"{BASE_URL}/privacy.html",
        "terms_url": f"{BASE_URL}/terms.html",
        "disclaimer_url": f"{BASE_URL}/disclaimer.html",
        "steps": render_steps(
            page["steps"],
            "../assets/screenshots/en/",
            ["desk-main.png", "desk-qr.png", "app-notification.png", "app-match-found.png"],
        ),
        "features": render_features(page["features"]),
        "background_steps": render_background(page["background_steps"], "../assets/screenshots/en/"),
        "faq": render_faq(page["faq"]),
        "json_ld": json_ld,
    }
    output = template.safe_substitute(values)
    destination = ROOT / locale_dir / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output, encoding="utf-8", newline="\n")
    return output


def render_guide(language: str, catalog: dict[str, Any], template: Template) -> str:
    common = catalog["common"]
    page = catalog["guide"]
    locale_dir = LOCALE_DIRS[language]
    canonical = absolute_url(language, "guide")
    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": page["h1"],
            "description": page["description"],
            "image": f"{BASE_URL}/assets/screenshots/en/og-cover.png",
            "datePublished": "2026-08-24",
            "dateModified": LAST_MODIFIED,
            "inLanguage": language,
            "url": canonical,
            "author": {"@type": "Organization", "name": "REACCEPT"},
            "publisher": {"@type": "Organization", "name": "REACCEPT"},
            "mainEntityOfPage": canonical,
        },
        ensure_ascii=False,
        indent=2,
    )
    values = {
        **{key: escape(str(value)) for key, value in common.items()},
        **{key: escape(str(value)) for key, value in page.items() if isinstance(value, str)},
        "lang": language,
        "canonical": canonical,
        "hreflang": hreflang_links("guide"),
        "language_switcher": language_switcher(language, "guide"),
        "home_url": absolute_url(language, "home"),
        "play_store_url": PLAY_STORE_URL,
        "assets": "../../assets/",
        "styles": "../../styles.css?rev=20260907-1",
        "privacy_url": f"{BASE_URL}/privacy.html",
        "terms_url": f"{BASE_URL}/terms.html",
        "disclaimer_url": f"{BASE_URL}/disclaimer.html",
        "steps": render_steps(page["steps"], "", []),
        "json_ld": json_ld,
    }
    output = template.safe_substitute(values)
    destination = ROOT / locale_dir / "accept-dota-2-match-from-phone" / "index.html"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(output, encoding="utf-8", newline="\n")
    return output


def build_sitemap() -> None:
    groups = ("home", "guide")
    entries: list[str] = []
    for page in groups:
        alternates = "\n".join(
            f'    <xhtml:link rel="alternate" hreflang="{language}" href="{absolute_url(language, page)}" />'
            for language in ALL_LANGUAGES
        )
        alternates += (
            "\n"
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{absolute_url("en", page)}" />'
        )
        for language in ALL_LANGUAGES:
            entries.append(
                "  <url>\n"
                f"    <loc>{absolute_url(language, page)}</loc>\n"
                f"{alternates}\n"
                f"    <lastmod>{LAST_MODIFIED}</lastmod>\n"
                "  </url>"
            )
    for legal in ("privacy.html", "terms.html", "disclaimer.html"):
        entries.append(
            f"  <url><loc>{BASE_URL}/{legal}</loc><lastmod>2026-08-24</lastmod></url>"
        )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )
    (ROOT / "sitemap.xml").write_text(sitemap, encoding="utf-8", newline="\n")


def main() -> None:
    catalogs = json.loads((ROOT / "locales" / "pages.json").read_text(encoding="utf-8"))
    home_template = Template((ROOT / "templates" / "home.html").read_text(encoding="utf-8"))
    guide_template = Template((ROOT / "templates" / "accept-page.html").read_text(encoding="utf-8"))
    missing = set(LOCALE_DIRS) - set(catalogs)
    if missing:
        raise SystemExit(f"Missing locale catalogs: {', '.join(sorted(missing))}")
    for language in LOCALE_DIRS:
        render_home(language, catalogs[language], home_template)
        render_guide(language, catalogs[language], guide_template)
    build_sitemap()


if __name__ == "__main__":
    main()
