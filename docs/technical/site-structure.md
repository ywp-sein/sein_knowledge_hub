# Site Structure

The Knowledge Hub publishes the `web/` directory directly to GitHub Pages.

The published article pages in `web/` are grouped by public wiki category. Shared assets live under
`web/assets/`. Root-level files are reserved for the landing pages, app metadata, and service worker.

## Repository Directories

```text
.
├── .github/workflows/       GitHub Pages deployment workflow
├── docs/
│   ├── compliance/          Legal and compliance check records
│   ├── content/             Editorial guidance and content rules
│   └── technical/           Site structure and maintenance notes
├── scripts/                 Build and validation scripts
├── src/                     Older notes and project material, not published directly
└── web/                     Published static website
    ├── assets/
    │   ├── css/             Shared stylesheets
    │   ├── icons/           Site icons
    │   └── js/              Shared JavaScript modules
    ├── development/         Version log and maintainer-facing public pages
    ├── homelessness/        Homelessness issue pages
    ├── legal/               Imprint, privacy, and license pages
    └── some-hows/           General how-to pages
```

## Published Website Files

The main published files live in `web/`:

- `index.html` and `index.de.html`: main pages.
- `some-hows/`: general how-to pages.
- `homelessness/`: homelessness issue category pages.
- `development/`: version log and development pages.
- `legal/`: legal pages.
- `*.de.html`: German language pairs.
- `assets/css/styles.css`: shared layout and theme styling.
- `assets/js/components.js`: shared header and sidebar.
- `assets/js/search-index.js`: global wiki search metadata.
- `assets/js/resources.js`: structured resource table data.
- `assets/js/app.js`: search, theme, and mobile sidebar behavior.
- `assets/icons/icon.svg`: site icon.
- `service-worker.js`: offline/cache asset list.
- `manifest.webmanifest`: installable app metadata.

## Navigation Sources

When adding a published page, update:

- `web/assets/js/components.js` if the page should appear in the sidebar.
- `web/assets/js/search-index.js` so the page appears in search.
- `web/service-worker.js` so the page is cached.
- The English and German HTML files.
- The visible revision timestamp for changed content.

Then run:

```bash
python3 scripts/validate_site.py
python3 scripts/build_version_log.py
```

## Path Rules

Root pages use asset paths such as `assets/js/components.js`.

Category pages are one directory deep and use asset paths such as `../assets/js/components.js`.

The shared component router stores page routes as root-relative web paths, then renders links
relative to the current page depth. Keep category pages one level below `web/` unless the router and
validator are updated together.

If the hub grows much larger, the next structural step can be a static build script that generates
`web/` from structured content source files.
