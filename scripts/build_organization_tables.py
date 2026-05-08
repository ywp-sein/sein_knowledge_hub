#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data/berlin-homelessness-organizations.json"
PAGES = {
    "en": ROOT / "web/homelessness/homelessness-organizations-berlin.html",
    "de": ROOT / "web/homelessness/homelessness-organizations-berlin.de.html",
}
MARKER_NAME = "berlin-homelessness-organizations"


def load_data() -> dict:
    return json.loads(DATA_FILE.read_text(encoding="utf-8"))


def text(value: object) -> str:
    return html.escape(str(value), quote=True)


def field(organization: dict, key: str, lang: str) -> str:
    value = organization[key]
    if isinstance(value, dict):
        return text(value[lang])
    return text(value)


def source_link(organization: dict, lang: str) -> str:
    source = organization["sources"][0]
    label = source["label"]
    if lang == "en" and organization["id"] == "teen-challenge-berliner-help-stiftung":
        label = "Hilfelotse Berlin entry"
    if lang == "en" and organization["id"] == "heilsarmee-cafe-treffpunkt":
        label = "Heilsarmee Germany"
    if lang == "de" and organization["id"] == "heilsarmee-cafe-treffpunkt":
        label = "Heilsarmee Deutschland"
    return f'<a href="{text(source["url"])}">{text(label)}</a>'


def render_rows(lang: str, organizations: list[dict]) -> str:
    rows: list[str] = []
    for organization in organizations:
        marker = text(organization["map_marker"])
        name = field(organization, "name", lang)
        address = text(organization["address"]["label"])
        focus = field(organization, "focus", lang)
        how_it_helps = field(organization, "how_it_helps", lang)
        source = source_link(organization, lang)
        rows.append(
            "\n".join(
                [
                    "                  <tr>",
                    f"                    <td>{marker}</td>",
                    f'                    <td><strong>{name}</strong><span class="org-address">{address}</span></td>',
                    f"                    <td>{focus}</td>",
                    f"                    <td>{how_it_helps}</td>",
                    f"                    <td>{source}</td>",
                    "                  </tr>",
                ],
            ),
        )
    return "\n".join(rows)


def replace_generated_block(page: Path, lang: str, rows: str) -> tuple[str, str]:
    original = page.read_text(encoding="utf-8")
    start = f"                  <!-- BEGIN generated:{MARKER_NAME}:{lang} -->"
    end = f"                  <!-- END generated:{MARKER_NAME}:{lang} -->"
    if start not in original or end not in original:
        raise ValueError(f"{page.relative_to(ROOT)} is missing generated table markers for {lang}")
    before, rest = original.split(start, 1)
    _old, after = rest.split(end, 1)
    generated = f"{start}\n{rows}\n{end}"
    return original, f"{before}{generated}{after}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate organization tables from JSON data.")
    parser.add_argument("--check", action="store_true", help="Fail if generated HTML is stale.")
    args = parser.parse_args()

    organizations = load_data()["organizations"]
    stale_pages: list[str] = []
    for lang, page in PAGES.items():
        original, updated = replace_generated_block(page, lang, render_rows(lang, organizations))
        if args.check:
            if original != updated:
                stale_pages.append(str(page.relative_to(ROOT)))
        else:
            page.write_text(updated, encoding="utf-8")

    if stale_pages:
        print("Generated organization tables are stale:", file=sys.stderr)
        for page in stale_pages:
            print(f"  {page}", file=sys.stderr)
        print("Run: python3 scripts/build_organization_tables.py", file=sys.stderr)
        return 1

    if args.check:
        print("Generated organization tables are up to date.")
    else:
        print("Generated organization tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
