#!/usr/bin/env python3
"""Build the Knowledge Hub version log pages from git history."""

from __future__ import annotations

import html
import os
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"
BERLIN = ZoneInfo("Europe/Berlin")
MAX_COMMITS = 50


@dataclass
class VersionRecord:
    version: str
    timestamp: datetime
    subject: str
    files: list[str]
    dirty: bool = False


def run_git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).rstrip("\n")


def git_records() -> list[VersionRecord]:
    try:
        raw = run_git([
            "log",
            f"--max-count={MAX_COMMITS}",
            "--pretty=format:%H%x1f%cI%x1f%s",
        ])
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

    entries: list[tuple[str, str, str, list[str]]] = []
    for line in raw.splitlines():
        if not line:
            continue
        full_sha, committed_at, subject = line.split("\x1f", 2)
        files = run_git(["show", "--name-only", "--format=", "--no-renames", full_sha]).splitlines()
        entries.append((full_sha, committed_at, subject, [file for file in files if file]))

    total = len(entries)
    records: list[VersionRecord] = []
    for index, (_full_sha, committed_at, subject, files) in enumerate(entries):
        records.append(
            VersionRecord(
                version=semantic_version(total - index),
                timestamp=datetime.fromisoformat(committed_at).astimezone(BERLIN),
                subject=subject,
                files=files,
            ),
        )
    return records


def semantic_version(number: int) -> str:
    major = number // 100
    minor = (number % 100) // 10
    patch = number % 10
    return f"{major}.{minor}.{patch}"


def dirty_record() -> VersionRecord | None:
    if os.environ.get("VERSION_LOG_INCLUDE_DIRTY") == "0":
        return None
    try:
        raw = run_git(["status", "--porcelain"])
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    files = [line[3:] for line in raw.splitlines() if len(line) > 3]
    if not files:
        return None
    return VersionRecord(
        version="0.0.0",
        timestamp=datetime.now(BERLIN),
        subject="Uncommitted Knowledge Hub update",
        files=files,
        dirty=True,
    )


def classify(files: list[str], lang: str) -> str:
    joined = " ".join(files)
    labels = {
        "development": "Knowledge Hub development" if lang == "en" else "Entwicklung des Knowledge Hub",
        "homelessness": "Homelessness" if lang == "en" else "Wohnungslosigkeit",
        "research": "Research method" if lang == "en" else "Recherchemethode",
        "main": "Main page" if lang == "en" else "Startseite",
        "deploy": "Deployment" if lang == "en" else "Deployment",
        "sources": "Source notes" if lang == "en" else "Quellennotizen",
        "website": "Website" if lang == "en" else "Website",
    }
    if "homelessness" in joined:
        return labels["homelessness"]
    if "knowledge-hub-" in joined or "build_version_log.py" in joined:
        return labels["development"]
    if "research-social-issues" in joined:
        return labels["research"]
    if ".github/workflows" in joined or "service-worker" in joined:
        return labels["deploy"]
    if "web/index" in joined:
        return labels["main"]
    if "src/" in joined:
        return labels["sources"]
    return labels["website"]


def format_date(dt: datetime, lang: str) -> str:
    if lang == "de":
      months = {
          1: "Januar",
          2: "Februar",
          3: "März",
          4: "April",
          5: "Mai",
          6: "Juni",
          7: "Juli",
          8: "August",
          9: "September",
          10: "Oktober",
          11: "November",
          12: "Dezember",
      }
      return f"{dt.day}. {months[dt.month]} {dt.year}, {dt:%H:%M} CEST"
    months = {
        1: "January",
        2: "February",
        3: "March",
        4: "April",
        5: "May",
        6: "June",
        7: "July",
        8: "August",
        9: "September",
        10: "October",
        11: "November",
        12: "December",
    }
    return f"{dt.day} {months[dt.month]} {dt.year}, {dt:%H:%M} CEST"


def rows(records: list[VersionRecord], lang: str) -> str:
    if not records:
        empty = "No revision history found." if lang == "en" else "Keine Revisionshistorie gefunden."
        return f"<tr><td colspan=\"4\">{empty}</td></tr>"
    rendered = []
    for record in records:
        content = updated_content(record, lang)
        rendered.append(
            "\n".join(
                [
                    "                  <tr>",
                    f"                    <td><code>{html.escape(record.version)}</code></td>",
                    f"                    <td>{html.escape(format_date(record.timestamp, lang))}</td>",
                    f"                    <td>{html.escape(classify(record.files, lang))}</td>",
                    f"                    <td>{html.escape(content)}</td>",
                    "                  </tr>",
                ],
            ),
        )
    return "\n".join(rendered)


def updated_content(record: VersionRecord, lang: str) -> str:
    if not record.dirty:
        return record.subject
    joined = " ".join(record.files)
    if "homelessness-organizations-berlin" in joined and (
        "map-marker" in joined or "scripts/build_organization_tables.py" in joined
    ):
        return (
            "Organization addresses forced onto a new line and fixed map overlay labels removed"
            if lang == "en"
            else "Organisationsadressen in eigene Zeile gesetzt und feste Karten-Overlays entfernt"
        )
    if "homelessness-organizations-berlin" in joined and (
        "scripts/build_organization_tables.py" in joined
        or "build_organization_tables" in joined
    ):
        return (
            "Organization table generation automated from JSON data"
            if lang == "en"
            else "Organisationstabelle wird automatisch aus JSON-Daten erzeugt"
        )
    if "homelessness-organizations-berlin" in joined and (
        "homelessness-map-berlin" in joined
        or "data/berlin-homelessness-organizations.json" in joined
        or "data/" in joined
    ):
        return (
            "Helping map directory table simplified and organization JSON database added"
            if lang == "en"
            else "Hilfekarten-Tabelle vereinfacht und Organisationsdatenbank als JSON ergänzt"
        )
    if "homelessness-map-berlin" in joined:
        return (
            "Berlin homelessness support map added with organization coordinates"
            if lang == "en"
            else "Karte der Berliner Wohnungslosenhilfe mit Organisationskoordinaten ergänzt"
        )
    if (
        "web/some-hows/" in joined
        or "web/homelessness/" in joined
        or "web/development/" in joined
        or "web/legal/" in joined
    ) and "service-worker.js" in joined:
        return (
            "Published pages reorganized into category directories"
            if lang == "en"
            else "Veröffentlichte Seiten in Kategorieverzeichnisse umorganisiert"
        )
    if "assets/" in joined and "service-worker.js" in joined:
        return (
            "Published web assets reorganized under assets directories"
            if lang == "en"
            else "Veröffentlichte Web-Assets in assets-Verzeichnisse umorganisiert"
        )
    if "scripts/validate_site.py" in joined or "docs/content" in joined or "docs/technical" in joined:
        return (
            "Repository structure, content guidelines, and site validation added"
            if lang == "en"
            else "Repository-Struktur, Inhaltsrichtlinien und Site-Validierung ergänzt"
        )
    if "how-to-change-society" in joined or "how-to-have-hope-to-help" in joined:
        return (
            "How to change society page revised with responsibility for words and deeds"
            if lang == "en"
            else "Wie man Gesellschaft verändert um Verantwortung für Worte und Taten ergänzt"
        )
    if "components.js" in joined and "service-worker.js" in joined:
        return (
            "Some Hows sidebar order and indentation adjusted"
            if lang == "en"
            else "Reihenfolge und Einrückung der Sidebar-Kategorie Einige Wie-Fragen angepasst"
        )
    if "homelessness-organizations-berlin" in joined:
        return (
            "Teen Challenge and Salvation Army sources added to Berlin organization list"
            if lang == "en"
            else "Teen Challenge und Heilsarmee mit Quellen zur Berliner Organisationsliste ergänzt"
        )
    if ("privacy" in joined or "license" in joined) and "components.js" in joined and "styles.css" in joined:
        return (
            "Legal/privacy source-use guidance tightened and sidebar categories made foldable"
            if lang == "en"
            else "Rechts-, Datenschutz- und Quellenhinweise geschärft und Sidebar-Kategorien einklappbar gemacht"
        )
    if "components.js" in joined and "app.js" in joined and "styles.css" in joined:
        return (
            "Phone layout separated from desktop with a slide-out wiki sidebar"
            if lang == "en"
            else "Smartphone-Layout vom Desktop getrennt und Wiki-Sidebar als Slide-out ergänzt"
        )
    if "styles.css" in joined and "components.js" not in joined:
        return (
            "Phone browser layout improved for header, sidebar, infoboxes, and tables"
            if lang == "en"
            else "Layout für Smartphone-Browser bei Header, Sidebar, Infoboxen und Tabellen verbessert"
        )
    if "license" in joined and "privacy" in joined:
        return (
            "Privacy transparency expanded and source-use guidance added to license page"
            if lang == "en"
            else "Datenschutzhinweise erweitert und Quellenhinweise zur Lizenzseite ergänzt"
        )
    if "components.js" in joined and "styles.css" in joined:
        return (
            "Sidebar categories made foldable and duplicate infobox revision rows removed"
            if lang == "en"
            else "Sidebar-Kategorien einklappbar gemacht und doppelte Revisionszeilen aus Infoboxen entfernt"
        )
    if "components.js" in joined:
        return (
            "Shared header and sidebar components added across pages"
            if lang == "en"
            else "Gemeinsame Header- und Sidebar-Komponenten für alle Seiten ergänzt"
        )
    if "imprint" in joined or "privacy" in joined:
        return (
            "Legal contact details added to imprint and privacy pages"
            if lang == "en"
            else "Rechtliche Kontaktdaten in Impressum und Datenschutz ergänzt"
        )
    if ("imprint" in joined or "privacy" in joined or "license" in joined) and "research-social-issues" in joined:
        return (
            "Legal pages added and research method references embedded"
            if lang == "en"
            else "Rechtsseiten ergänzt und Referenzen in die Methodenseite eingebettet"
        )
    if "imprint" in joined or "privacy" in joined or "license" in joined:
        return (
            "Legal pages added for imprint, privacy, and license"
            if lang == "en"
            else "Rechtsseiten für Impressum, Datenschutz und Lizenz ergänzt"
        )
    if "research-social-issues" in joined:
        return (
            "Research social issue method page expanded with methods and references"
            if lang == "en"
            else "Methodenseite zur Recherche sozialer Themen um Methoden und Referenzen erweitert"
        )
    if "themeIcons" in joined or "themeToggle" in joined or ("web/assets/css/styles.css" in joined and "web/assets/js/app.js" in joined):
        return (
            "Theme toggle uses open-source-style icons before language switch"
            if lang == "en"
            else "Darstellungsschalter nutzt Open-Source-Icons vor der Sprachauswahl"
        )
    if "knowledge-hub-next-steps" in joined:
        return (
            "Issue label set simplified to avoid content and source overlap"
            if lang == "en"
            else "Issue-Labelset vereinfacht, um Überschneidungen zwischen Inhalt und Quellen zu vermeiden"
        )
    if "search-index.js" in joined or "wikiSearch" in joined or "app.js" in joined:
        return (
            "Global sidebar search and GitHub issue feedback link"
            if lang == "en"
            else "Globale Suche in der Seitenleiste und Feedback-Link zu GitHub Issues"
        )
    if "knowledge-hub-version-log" in joined:
        return (
            "Version log generated for the latest Knowledge Hub update"
            if lang == "en"
            else "Versionsprotokoll für die neueste Aktualisierung des Knowledge Hub erzeugt"
        )
    return (
        "Draft update to Knowledge Hub content and layout"
        if lang == "en"
        else "Entwurfsaktualisierung von Inhalt und Layout des Knowledge Hub"
    )


def page(lang: str, records: list[VersionRecord]) -> str:
    is_de = lang == "de"
    revised = records[0].timestamp if records else datetime.now(BERLIN)
    revised_label = format_date(revised, lang)
    revised_iso = revised.isoformat(timespec="minutes")
    if is_de:
        title = "Versionsprotokoll · SEiN Knowledge Hub"
        home = "index.de.html"
        switch = '<a href="knowledge-hub-version-log.html">EN</a><a aria-current="page" href="knowledge-hub-version-log.de.html">DE</a>'
        nav = """          <li><a href="index.de.html">Startseite</a></li>
          <li><a href="research-social-issues.de.html">Wie man ein soziales Thema recherchiert</a></li>
          <li class="page-nav-group">Wohnungslosigkeit</li>
          <li><a class="subpage-link" href="homelessness-berlin.de.html">Überblick in Berlin</a></li>
          <li><a class="subpage-link" href="homelessness-how-to-help.de.html">Wie man hilft</a></li>
          <li><a class="subpage-link" href="homelessness-organizations-berlin.de.html">Hilfekarte und Organisationen</a></li>
          <li><a class="subpage-link" href="homelessness-policies-germany.de.html">Politik in Deutschland</a></li>
          <li class="page-nav-group">Entwicklung des Knowledge Hub</li>
          <li><a class="subpage-link" href="knowledge-hub-version-log.de.html" aria-current="page">Versionsprotokoll</a></li>
          <li><a class="subpage-link" href="knowledge-hub-next-steps.de.html">Nächste Schritte</a></li>
          <li class="page-nav-group">Rechtliches</li>
          <li><a class="subpage-link" href="imprint.de.html">Impressum</a></li>
          <li><a class="subpage-link" href="privacy.de.html">Datenschutz</a></li>
          <li><a class="subpage-link" href="license.de.html">Lizenz</a></li>"""
        labels = {
            "pages": "Seiten",
            "search_label": "Wiki durchsuchen",
            "search_placeholder": "Wohnungslosigkeit, Politik...",
            "theme_label": "Darstellung",
            "issue_title": "Dieses Hub verbessern",
            "issue_text": "Vorschläge, Korrekturen und neue Quellenideen können über GitHub Issues geteilt werden.",
            "issue_link": "Issue öffnen",
            "namespace": "Entwicklungsseite",
            "h1": "Versionsprotokoll des Knowledge Hub",
            "subtitle": "Ein automatisch erzeugtes Protokoll der Website-Revisionen und Inhaltsaktualisierungen.",
            "revised": "Zuletzt überarbeitet",
            "box": "Versionsprotokoll",
            "type": "Seitentyp",
            "type_value": "Automatisches Entwicklungsprotokoll",
            "purpose": "Zweck",
            "purpose_value": "Jede öffentliche Aktualisierung und ihre Inhalte festhalten",
            "rule": "Automatisierung",
            "rule_value": "Diese Seite wird beim Deployment aus der Revisionshistorie erzeugt",
            "how": "Nutzung dieser Seite",
            "how_text": "Diese Seite dokumentiert die Entwicklung des Knowledge Hub selbst. Jede Inhaltsänderung, Strukturänderung, Quellenprüfung, Übersetzung oder neue Kategorie erscheint hier als Versionseintrag.",
            "records": "Versionsaufzeichnungen",
            "th_time": "Revisionszeit",
            "th_version": "Version",
            "th_area": "Bereich",
            "th_content": "Aktualisierter Inhalt",
            "brand": "SEiN Knowledge Hub Startseite",
        }
    else:
        title = "Knowledge Hub version log · SEiN Knowledge Hub"
        home = "index.html"
        switch = '<a aria-current="page" href="knowledge-hub-version-log.html">EN</a><a href="knowledge-hub-version-log.de.html">DE</a>'
        nav = """          <li><a href="index.html">Main page</a></li>
          <li><a href="research-social-issues.html">How to research a social issue</a></li>
          <li class="page-nav-group">Homelessness</li>
          <li><a class="subpage-link" href="homelessness-berlin.html">Overview in Berlin</a></li>
          <li><a class="subpage-link" href="homelessness-how-to-help.html">How to help</a></li>
          <li><a class="subpage-link" href="homelessness-organizations-berlin.html">Helping map and organizations</a></li>
          <li><a class="subpage-link" href="homelessness-policies-germany.html">Policies in Germany</a></li>
          <li class="page-nav-group">Knowledge Hub development</li>
          <li><a class="subpage-link" href="knowledge-hub-version-log.html" aria-current="page">Version log</a></li>
          <li><a class="subpage-link" href="knowledge-hub-next-steps.html">Next steps</a></li>
          <li class="page-nav-group">Legal</li>
          <li><a class="subpage-link" href="imprint.html">Imprint</a></li>
          <li><a class="subpage-link" href="privacy.html">Privacy Policy</a></li>
          <li><a class="subpage-link" href="license.html">License</a></li>"""
        labels = {
            "pages": "Pages",
            "search_label": "Search the wiki",
            "search_placeholder": "homelessness, policy...",
            "theme_label": "Theme",
            "issue_title": "Improve this hub",
            "issue_text": "Suggestions, corrections, and new source ideas can be shared through GitHub issues.",
            "issue_link": "Open an issue",
            "namespace": "Development page",
            "h1": "Knowledge Hub version log",
            "subtitle": "An automatically generated record of website revisions and content updates.",
            "revised": "Last revised",
            "box": "Version log",
            "type": "Page type",
            "type_value": "Automated development record",
            "purpose": "Purpose",
            "purpose_value": "Record every public update and its changed content",
            "rule": "Automation",
            "rule_value": "This page is generated from revision history during deployment",
            "how": "How to use this page",
            "how_text": "This page records the development of the Knowledge Hub itself. Every content update, structural change, source refresh, translation update, or new category appears here as a version entry.",
            "records": "Version records",
            "th_time": "Revision time",
            "th_version": "Version",
            "th_area": "Area",
            "th_content": "Updated content",
            "brand": "SEiN Knowledge Hub home",
        }
    return f"""<!doctype html>
<html lang="{lang}">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
    <meta name="theme-color" content="#f8f9fa" media="(prefers-color-scheme: light)" />
    <meta name="theme-color" content="#171c21" media="(prefers-color-scheme: dark)" />
    <title>{html.escape(title)}</title>
    <link rel="manifest" href="../manifest.webmanifest" />
    <link rel="icon" href="../assets/icons/icon.svg" type="image/svg+xml" />
    <link rel="stylesheet" href="../assets/css/styles.css" />
  </head>
  <body>
    <sein-header></sein-header>

    <div class="page">
      <sein-sidebar></sein-sidebar>

      <main class="article">
        <article>
          <header class="article-header">
            <p class="namespace">{labels["namespace"]}</p>
            <h1>{labels["h1"]}</h1>
            <p class="subtitle">{labels["subtitle"]}</p>
            <p class="revision-meta">
              {labels["revised"]}: <time datetime="{revised_iso}">{html.escape(revised_label)}</time>
            </p>
          </header>

          <aside class="infobox" aria-label="article summary">
            <h2>{labels["box"]}</h2>
            <dl>
              <div><dt>{labels["type"]}</dt><dd>{labels["type_value"]}</dd></div>
              <div><dt>{labels["purpose"]}</dt><dd>{labels["purpose_value"]}</dd></div>
              <div><dt>{labels["rule"]}</dt><dd>{labels["rule_value"]}</dd></div>
            </dl>
          </aside>

          <section>
            <h2>{labels["how"]}</h2>
            <p>{labels["how_text"]}</p>
          </section>

          <section>
            <h2>{labels["records"]}</h2>
            <div class="table-wrap">
              <table class="directory-table">
                <thead>
                  <tr>
                    <th>{labels["th_version"]}</th>
                    <th>{labels["th_time"]}</th>
                    <th>{labels["th_area"]}</th>
                    <th>{labels["th_content"]}</th>
                  </tr>
                </thead>
                <tbody id="versionLogRows">
{rows(records, lang)}
                </tbody>
              </table>
            </div>
          </section>
        </article>
      </main>
    </div>
    <script src="../assets/js/components.js"></script>
    <script src="../assets/js/resources.js"></script>
    <script src="../assets/js/search-index.js"></script>
    <script src="../assets/js/app.js"></script>
  </body>
</html>
"""


def main() -> None:
    records = git_records()
    dirty = dirty_record()
    if dirty:
        dirty.version = semantic_version(len(records) + 1)
        records.insert(0, dirty)
    (WEB / "development/knowledge-hub-version-log.html").write_text(page("en", records), encoding="utf-8")
    (WEB / "development/knowledge-hub-version-log.de.html").write_text(page("de", records), encoding="utf-8")


if __name__ == "__main__":
    main()
