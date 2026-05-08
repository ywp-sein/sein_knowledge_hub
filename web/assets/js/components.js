const pageGroups = [
  {
    en: "Main",
    de: "Hauptseite",
    pages: [
      { id: "index", en: "Main page", de: "Startseite" },
    ],
  },
  {
    en: "Some Hows",
    de: "Einige Wie-Fragen",
    pages: [
      { id: "how-to-change-society", en: "How to change society", de: "Wie man Gesellschaft verändert" },
      { id: "research-social-issues", en: "How to research a social issue", de: "Wie man ein soziales Thema recherchiert" },
    ],
  },
  {
    en: "Homelessness",
    de: "Wohnungslosigkeit",
    pages: [
      { id: "homelessness-berlin", en: "Overview in Berlin", de: "Überblick in Berlin" },
      { id: "homelessness-how-to-help", en: "How to help", de: "Wie man hilft" },
      { id: "homelessness-organizations-berlin", en: "Helping map and organizations", de: "Hilfekarte und Organisationen" },
      { id: "homelessness-policies-germany", en: "Policies in Germany", de: "Politik in Deutschland" },
    ],
  },
  {
    en: "Knowledge Hub development",
    de: "Entwicklung des Knowledge Hub",
    pages: [
      { id: "knowledge-hub-version-log", en: "Version log", de: "Versionsprotokoll" },
      { id: "knowledge-hub-next-steps", en: "Next steps", de: "Nächste Schritte" },
    ],
  },
  {
    en: "Legal",
    de: "Rechtliches",
    pages: [
      { id: "imprint", en: "Imprint", de: "Impressum" },
      { id: "privacy", en: "Privacy Policy", de: "Datenschutz" },
      { id: "license", en: "License", de: "Lizenz" },
    ],
  },
];

const pageRoutes = {
  index: { en: "index.html", de: "index.de.html" },
  "how-to-change-society": {
    en: "some-hows/how-to-change-society.html",
    de: "some-hows/how-to-change-society.de.html",
  },
  "research-social-issues": {
    en: "some-hows/research-social-issues.html",
    de: "some-hows/research-social-issues.de.html",
  },
  "homelessness-berlin": {
    en: "homelessness/homelessness-berlin.html",
    de: "homelessness/homelessness-berlin.de.html",
  },
  "homelessness-how-to-help": {
    en: "homelessness/homelessness-how-to-help.html",
    de: "homelessness/homelessness-how-to-help.de.html",
  },
  "homelessness-organizations-berlin": {
    en: "homelessness/homelessness-organizations-berlin.html",
    de: "homelessness/homelessness-organizations-berlin.de.html",
  },
  "homelessness-policies-germany": {
    en: "homelessness/homelessness-policies-germany.html",
    de: "homelessness/homelessness-policies-germany.de.html",
  },
  "knowledge-hub-version-log": {
    en: "development/knowledge-hub-version-log.html",
    de: "development/knowledge-hub-version-log.de.html",
  },
  "knowledge-hub-next-steps": {
    en: "development/knowledge-hub-next-steps.html",
    de: "development/knowledge-hub-next-steps.de.html",
  },
  imprint: { en: "legal/imprint.html", de: "legal/imprint.de.html" },
  privacy: { en: "legal/privacy.html", de: "legal/privacy.de.html" },
  license: { en: "legal/license.html", de: "legal/license.de.html" },
};

function currentLang() {
  return document.documentElement.lang === "de" ? "de" : "en";
}

function currentPathKey() {
  const parts = window.location.pathname.split("/").filter(Boolean);
  const last = parts.at(-1) || "index.html";
  const parent = parts.at(-2);
  return parent && ["some-hows", "homelessness", "development", "legal"].includes(parent)
    ? `${parent}/${last}`
    : last;
}

function currentPageId() {
  const path = currentPathKey();
  const found = Object.entries(pageRoutes).find(([, routes]) => routes.en === path || routes.de === path);
  return found ? found[0] : "index";
}

function currentDepthPrefix() {
  return currentPathKey().includes("/") ? "../" : "";
}

function relativeHref(path) {
  return `${currentDepthPrefix()}${path}`;
}

function pageHref(id, lang = currentLang()) {
  return relativeHref(pageRoutes[id][lang]);
}

function themeIcon() {
  return '<svg aria-hidden="true" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>';
}

function menuIcon() {
  return '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M4 7h16"></path><path d="M4 12h16"></path><path d="M4 17h16"></path></svg>';
}

class SeinHeader extends HTMLElement {
  connectedCallback() {
    const lang = currentLang();
    const page = currentPageId();
    const labels = {
      en: { home: "SEiN Knowledge Hub home", language: "language", menu: "Open pages menu", theme: "Theme" },
      de: { home: "SEiN Knowledge Hub Startseite", language: "Sprache", menu: "Seitenmenü öffnen", theme: "Darstellung" },
    }[lang];
    this.innerHTML = `
      <header class="site-header">
        <button class="sidebar-toggle" id="sidebarToggle" type="button" aria-label="${labels.menu}" aria-controls="siteSidebar" aria-expanded="false">${menuIcon()}</button>
        <a class="brand" href="${pageHref("index", lang)}" aria-label="${labels.home}">
          <img src="${relativeHref("assets/icons/icon.svg")}" alt="" />
          <span>SEiN Knowledge Hub</span>
        </a>
        <button class="theme-toggle" id="themeToggle" type="button" aria-label="${labels.theme}" aria-live="polite">${themeIcon()}<span>Auto</span></button>
        <nav class="language-switch" aria-label="${labels.language}">
          <a ${lang === "en" ? 'aria-current="page"' : ""} href="${pageHref(page, "en")}">EN</a>
          <a ${lang === "de" ? 'aria-current="page"' : ""} href="${pageHref(page, "de")}">DE</a>
        </nav>
      </header>
    `;
  }
}

class SeinSidebar extends HTMLElement {
  connectedCallback() {
    const lang = currentLang();
    const page = currentPageId();
    const labels = {
      en: {
        aria: "wiki pages",
        pages: "Pages",
        search: "Search the wiki",
        placeholder: "homelessness, policy...",
        improve: "Improve this hub",
        issueText: "Suggestions, corrections, and new source ideas can be shared through GitHub issues.",
        issueLink: "Open an issue",
      },
      de: {
        aria: "Wiki-Seiten",
        pages: "Seiten",
        search: "Wiki durchsuchen",
        placeholder: "Wohnungslosigkeit, Politik...",
        improve: "Dieses Hub verbessern",
        issueText: "Vorschläge, Korrekturen und neue Quellenideen können über GitHub Issues geteilt werden.",
        issueLink: "Issue öffnen",
      },
    }[lang];

    const nav = pageGroups
      .map((group) => {
        const isOpen = group.pages.some((item) => item.id === page);
        const items = group.pages
          .map((item) => {
            const current = item.id === page ? ' aria-current="page"' : "";
            const subpage = item.id === "index" || group.en === "Some Hows" ? "" : ' class="subpage-link"';
            return `          <li><a${subpage} href="${pageHref(item.id, lang)}"${current}>${item[lang]}</a></li>`;
          })
          .join("\n");
        return `          <details class="page-nav-group"${isOpen ? " open" : ""}>
            <summary>${group[lang]}</summary>
            <ul>
${items}
            </ul>
          </details>`;
      })
      .join("\n");

    this.innerHTML = `
      <aside class="contents" id="siteSidebar" aria-label="${labels.aria}">
        <button class="sidebar-close" id="sidebarClose" type="button" aria-label="${lang === "de" ? "Seitenmenü schließen" : "Close pages menu"}">×</button>
        <form class="sidebar-search" role="search">
          <label for="wikiSearch">${labels.search}</label>
          <input id="wikiSearch" type="search" autocomplete="off" placeholder="${labels.placeholder}" />
          <div id="wikiSearchResults" class="search-results" hidden></div>
        </form>
        <h2>${labels.pages}</h2>
        <nav class="page-nav" aria-label="${labels.pages}">
${nav}
        </nav>
        <div class="sidebar-note">
          <strong>${labels.improve}</strong>
          <p>${labels.issueText}</p>
          <a href="https://github.com/ywp-sein/sein_knowledge_hub/issues">${labels.issueLink}</a>
        </div>
      </aside>
    `;
  }
}

customElements.define("sein-header", SeinHeader);
customElements.define("sein-sidebar", SeinSidebar);
