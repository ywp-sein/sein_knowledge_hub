# SEiN Knowledge Hub

This is a static information hub for collecting practical support pathways and verified source links.
It now deploys from `web/` as a GitHub Pages app, following the deployment style used in `berlin_re_sim`.

Public entry point:

- GitHub Pages action publishes the `web/` folder.
- `index.html` at the repository root redirects to `web/index.html` as a fallback if Pages is configured to serve the branch root.

> *Information is not equal to knowledge,* <br>
> *Knowledge is not equal to wisdom,* <br>
> *We need people to make wise decisions and act with integrity.*

## Current focus

The wiki starts with a general main page and a few page families:

- Some Hows, beginning with how to change society and how to research a social issue.
- Issue pages, beginning with homelessness in Berlin.
- Development pages for the version log and next steps.
- Legal pages for imprint, privacy, and license information.

The structure is intentionally expandable so later issue categories can be added without returning to an mdBook layout.

## Repository structure

Published website files stay in `web/` so GitHub Pages can deploy a simple static folder. Maintainer documentation is organized under `docs/`:

- `docs/content/`: writing rules, source practice, translation practice, and page requirements.
- `docs/compliance/`: legal and compliance check records.
- `docs/technical/`: site structure and maintenance notes.
- `scripts/`: build and validation scripts.
- `src/`: older source notes, not published directly.

For details, see:

- `docs/content/content-guidelines.md`
- `docs/technical/site-structure.md`

## Revision timestamps

When wiki content is revised, update the visible `Last revised` timestamp on the changed page.
Use the local Berlin time zone format already shown across the site.
Structural-only changes are recorded in the automated version log and do not require changing every article timestamp.

## Automated version log

The development version log pages are generated from git history:

```bash
python3 scripts/build_version_log.py
```

GitHub Pages runs this script during deployment, so each pushed update appears with a numbered version, timestamp, area, and updated content summary. Use clear commit messages because they become the public update summary.

## Validation

Run the structural validator before publishing larger changes:

```bash
python3 scripts/validate_site.py
```

The validator checks HTML parsing, English/German page pairs, sidebar pages, search index entries, service-worker assets, visible revision timestamps, and infobox presence.
The GitHub Pages workflow runs this check before building the version log and deploying.

## Local preview

Open `web/index.html` directly in a browser, or serve the `web/` folder with any static file server.

The older markdown files under `src/` remain as source notes, but the published site no longer uses mdBook.
