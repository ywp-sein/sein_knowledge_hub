#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data/berlin-homelessness-organizations.json"
PUBLIC_DATA_FILE = ROOT / "web/assets/data/berlin-homelessness-organizations.json"
SERVICE_WORKER_FILE = ROOT / "web/service-worker.js"
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
                    f'                    <td><strong>{name}</strong><br /><span class="org-address">{address}</span></td>',
                    f"                    <td>{focus}</td>",
                    f"                    <td>{how_it_helps}</td>",
                    f"                    <td>{source}</td>",
                    "                  </tr>",
                ],
            ),
        )
    return "\n".join(rows)


def public_map_data(payload: dict) -> dict:
    return {
        "schema_version": payload["schema_version"],
        "topic": payload["topic"],
        "location": payload["location"],
        "last_reviewed": payload["last_reviewed"],
        "organizations": [
            {
                "id": organization["id"],
                "map_marker": organization["map_marker"],
                "name": organization["name"],
                "address": {"label": organization["address"]["label"]},
                "coordinates": organization["coordinates"],
                "focus": organization["focus"],
                "source": organization["sources"][0],
            }
            for organization in payload["organizations"]
        ],
    }


def write_public_data(payload: dict, *, check: bool) -> bool:
    PUBLIC_DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(public_map_data(payload), ensure_ascii=False, indent=2) + "\n"
    previous = PUBLIC_DATA_FILE.read_text(encoding="utf-8") if PUBLIC_DATA_FILE.exists() else ""
    if previous == content:
        return False
    if check:
        return True
    PUBLIC_DATA_FILE.write_text(content, encoding="utf-8")
    return True


def cache_name_for(content: str) -> str:
    digest = hashlib.sha256(content.encode("utf-8")).hexdigest()[:10]
    return f'sein-knowledge-hub-v41-data-{digest}'


def update_service_worker_cache_name(public_data_content: str, *, check: bool) -> bool:
    service_worker = SERVICE_WORKER_FILE.read_text(encoding="utf-8")
    cache_name = cache_name_for(public_data_content)
    updated = re.sub(
        r'const CACHE_NAME = "sein-knowledge-hub-v41(?:-data-[a-f0-9]{10})?";',
        f'const CACHE_NAME = "{cache_name}";',
        service_worker,
        count=1,
    )
    if updated == service_worker:
        if cache_name in service_worker:
            return False
        raise ValueError("service-worker.js cache name did not match the expected pattern")
    if check:
        return True
    SERVICE_WORKER_FILE.write_text(updated, encoding="utf-8")
    return True


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

    payload = load_data()
    organizations = payload["organizations"]
    stale_pages: list[str] = []
    public_payload = public_map_data(payload)
    public_data_content = json.dumps(public_payload, ensure_ascii=False, indent=2) + "\n"
    public_data_changed = write_public_data(payload, check=args.check)
    service_worker_changed = update_service_worker_cache_name(public_data_content, check=args.check)
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

    if args.check and public_data_changed:
        print(f"Generated public data is stale: {PUBLIC_DATA_FILE.relative_to(ROOT)}", file=sys.stderr)
        print("Run: python3 scripts/build_organization_tables.py", file=sys.stderr)
        return 1

    if args.check and service_worker_changed:
        print(f"Service worker cache name is stale: {SERVICE_WORKER_FILE.relative_to(ROOT)}", file=sys.stderr)
        print("Run: python3 scripts/build_organization_tables.py", file=sys.stderr)
        return 1

    if args.check:
        print("Generated organization tables are up to date.")
    else:
        print("Generated organization tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
