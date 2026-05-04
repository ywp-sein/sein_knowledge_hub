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

The wiki starts with a general main page and two subpage types:

- Method pages, beginning with how to research a social issue.
- Issue pages, beginning with homelessness in Berlin.

The structure is intentionally expandable so later issue categories can be added without returning to an mdBook layout.

## Revision timestamps

When wiki content is revised, update the visible `Last revised` timestamp in `web/index.html`.
Use the local Berlin time zone format already shown on the page.

## Automated version log

The development version log pages are generated from git history:

```bash
python3 scripts/build_version_log.py
```

GitHub Pages runs this script during deployment, so each pushed update appears with a commit version, timestamp, message, and changed files. Use clear commit messages because they become the public update summary.

## Local preview

Open `web/index.html` directly in a browser, or serve the `web/` folder with any static file server.

The older markdown files under `src/` remain as source notes, but the published site no longer uses mdBook.
