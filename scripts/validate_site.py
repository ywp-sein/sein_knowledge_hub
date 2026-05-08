#!/usr/bin/env python3
from __future__ import annotations

import html.parser
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"

REQUIRED_SHARED_ASSETS = {
    "./assets/css/styles.css",
    "./assets/js/components.js",
    "./assets/js/resources.js",
    "./assets/js/search-index.js",
    "./assets/js/app.js",
    "./manifest.webmanifest",
    "./assets/icons/icon.svg",
}


class HtmlChecker(html.parser.HTMLParser):
    def error(self, message: str) -> None:  # pragma: no cover - required by older API
        raise ValueError(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def html_files() -> list[Path]:
    return sorted(WEB.glob("*.html")) + sorted(path for path in WEB.glob("*/*.html"))


def web_path(path: Path) -> str:
    return path.relative_to(WEB).as_posix()


def parse_html(errors: list[str]) -> None:
    for path in html_files():
        try:
            HtmlChecker().feed(read(path))
        except Exception as exc:  # noqa: BLE001 - report parser context
            fail(errors, f"{path.relative_to(ROOT)} does not parse as HTML: {exc}")


def language_pairs(errors: list[str]) -> None:
    names = {web_path(path) for path in html_files()}
    english = sorted(name for name in names if not name.endswith(".de.html"))
    for name in english:
        base = name.removesuffix(".html")
        de_name = "index.de.html" if base == "index" else f"{base}.de.html"
        if de_name not in names:
            fail(errors, f"Missing German page for {name}: expected {de_name}")

    for name in sorted(name for name in names if name.endswith(".de.html")):
        en_name = "index.html" if name == "index.de.html" else name.replace(".de.html", ".html")
        if en_name not in names:
            fail(errors, f"Missing English page for {name}: expected {en_name}")


def component_page_ids() -> set[str]:
    text = read(WEB / "assets/js/components.js")
    return set(re.findall(r'id:\s*"([^"]+)"', text))


def page_filename(page_id: str, lang: str) -> str:
    routes = {
        "index": {"en": "index.html", "de": "index.de.html"},
        "how-to-change-society": {
            "en": "some-hows/how-to-change-society.html",
            "de": "some-hows/how-to-change-society.de.html",
        },
        "research-social-issues": {
            "en": "some-hows/research-social-issues.html",
            "de": "some-hows/research-social-issues.de.html",
        },
        "homelessness-berlin": {
            "en": "homelessness/homelessness-berlin.html",
            "de": "homelessness/homelessness-berlin.de.html",
        },
        "homelessness-how-to-help": {
            "en": "homelessness/homelessness-how-to-help.html",
            "de": "homelessness/homelessness-how-to-help.de.html",
        },
        "homelessness-organizations-berlin": {
            "en": "homelessness/homelessness-organizations-berlin.html",
            "de": "homelessness/homelessness-organizations-berlin.de.html",
        },
        "homelessness-map-berlin": {
            "en": "homelessness/homelessness-map-berlin.html",
            "de": "homelessness/homelessness-map-berlin.de.html",
        },
        "homelessness-policies-germany": {
            "en": "homelessness/homelessness-policies-germany.html",
            "de": "homelessness/homelessness-policies-germany.de.html",
        },
        "knowledge-hub-version-log": {
            "en": "development/knowledge-hub-version-log.html",
            "de": "development/knowledge-hub-version-log.de.html",
        },
        "knowledge-hub-next-steps": {
            "en": "development/knowledge-hub-next-steps.html",
            "de": "development/knowledge-hub-next-steps.de.html",
        },
        "imprint": {"en": "legal/imprint.html", "de": "legal/imprint.de.html"},
        "privacy": {"en": "legal/privacy.html", "de": "legal/privacy.de.html"},
        "license": {"en": "legal/license.html", "de": "legal/license.de.html"},
    }
    return routes[page_id][lang]


def sidebar_pages_exist(errors: list[str]) -> None:
    for page_id in sorted(component_page_ids()):
        for lang in ("en", "de"):
            name = page_filename(page_id, lang)
            if not (WEB / name).exists():
                fail(errors, f"Sidebar page id {page_id!r} points to missing {name}")


def search_urls() -> set[str]:
    text = read(WEB / "assets/js/search-index.js")
    return set(re.findall(r'url:\s*"([^"]+)"', text))


def search_index(errors: list[str]) -> None:
    urls = search_urls()
    for url in sorted(urls):
        if not (WEB / url).exists():
            fail(errors, f"Search index points to missing page: {url}")

    for page_id in sorted(component_page_ids()):
        for lang in ("en", "de"):
            name = page_filename(page_id, lang)
            if name not in urls:
                fail(errors, f"Sidebar page {name} is missing from search-index.js")


def service_worker_assets() -> set[str]:
    text = read(WEB / "service-worker.js")
    return set(re.findall(r'"(\./[^"]+)"', text))


def service_worker(errors: list[str]) -> None:
    assets = service_worker_assets()
    for required in sorted(REQUIRED_SHARED_ASSETS):
        if required not in assets:
            fail(errors, f"service-worker.js is missing required asset {required}")

    for path in html_files():
        asset = f"./{web_path(path)}"
        if asset not in assets:
            fail(errors, f"service-worker.js does not cache {asset}")

    for asset in sorted(assets):
        if asset == "./":
            continue
        if not (WEB / asset.removeprefix("./")).exists():
            fail(errors, f"service-worker.js caches missing asset {asset}")


def article_requirements(errors: list[str]) -> None:
    for path in html_files():
        text = read(path)
        if "<main" not in text:
            continue
        if 'class="revision-meta"' not in text:
            fail(errors, f"{path.name} is missing visible revision metadata")
        if 'class="infobox"' not in text:
            fail(errors, f"{path.name} is missing an infobox")


def main() -> int:
    errors: list[str] = []
    parse_html(errors)
    language_pairs(errors)
    sidebar_pages_exist(errors)
    search_index(errors)
    service_worker(errors)
    article_requirements(errors)

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Site validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
