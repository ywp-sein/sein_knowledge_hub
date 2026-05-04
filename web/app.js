const resources = window.SEIN_RESOURCES || [];
const searchIndex = window.SEIN_SEARCH_INDEX || [];
const searchInput = document.querySelector("#wikiSearch");
const searchResults = document.querySelector("#wikiSearchResults");
const resourceRows = document.querySelector("#resourceRows");
const resultCount = document.querySelector("#resultCount");
const themeToggle = document.querySelector("#themeToggle");
const themeColorMetas = document.querySelectorAll('meta[name="theme-color"]');
const isGerman = document.documentElement.lang === "de";
const themeStorageKey = "sein-knowledge-hub-theme";
const themeOrder = ["auto", "light", "dark"];
const themeLabels = {
  en: { auto: "Auto", light: "Light", dark: "Dark" },
  de: { auto: "Auto", light: "Hell", dark: "Dunkel" },
};
const themeIcons = {
  auto: '<svg aria-hidden="true" viewBox="0 0 24 24"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line></svg>',
  light: '<svg aria-hidden="true" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"></circle><path d="M12 2v2"></path><path d="M12 20v2"></path><path d="m4.93 4.93 1.41 1.41"></path><path d="m17.66 17.66 1.41 1.41"></path><path d="M2 12h2"></path><path d="M20 12h2"></path><path d="m6.34 17.66-1.41 1.41"></path><path d="m19.07 4.93-1.41 1.41"></path></svg>',
  dark: '<svg aria-hidden="true" viewBox="0 0 24 24"><path d="M12 3a6 6 0 0 0 9 7.5A9 9 0 1 1 12 3Z"></path></svg>',
};

function applyTheme(value) {
  const theme = ["auto", "light", "dark"].includes(value) ? value : "auto";
  if (theme === "auto") {
    document.documentElement.removeAttribute("data-theme");
    themeColorMetas.forEach((meta) => {
      if (meta.dataset.originalMedia) meta.setAttribute("media", meta.dataset.originalMedia);
    });
  } else {
    document.documentElement.dataset.theme = theme;
    const color = theme === "dark" ? "#171c21" : "#f8f9fa";
    themeColorMetas.forEach((meta) => {
      if (!meta.dataset.originalMedia) meta.dataset.originalMedia = meta.getAttribute("media") || "";
      meta.removeAttribute("media");
      meta.setAttribute("content", color);
    });
  }
  if (themeToggle) {
    themeToggle.dataset.theme = theme;
    themeToggle.innerHTML = `${themeIcons[theme]}<span>${themeLabels[isGerman ? "de" : "en"][theme]}</span>`;
    themeToggle.setAttribute(
      "aria-label",
      isGerman
        ? `Darstellung: ${themeLabels.de[theme]}`
        : `Theme: ${themeLabels.en[theme]}`,
    );
  }
}

function setTheme(value) {
  const theme = ["auto", "light", "dark"].includes(value) ? value : "auto";
  try {
    if (theme === "auto") {
      localStorage.removeItem(themeStorageKey);
    } else {
      localStorage.setItem(themeStorageKey, theme);
    }
  } catch {
    // The selector should still work even when storage is blocked.
  }
  applyTheme(theme);
}

function storedTheme() {
  try {
    return localStorage.getItem(themeStorageKey) || "auto";
  } catch {
    return "auto";
  }
}

function nextTheme() {
  const current = ["auto", "light", "dark"].includes(document.documentElement.dataset.theme)
    ? document.documentElement.dataset.theme
    : storedTheme();
  const index = themeOrder.indexOf(current);
  return themeOrder[(index + 1) % themeOrder.length];
}

function renderSiteSearch() {
  if (!searchInput || !searchResults) return;
  const query = normalize(searchInput.value);
  if (!query) {
    searchResults.hidden = true;
    searchResults.innerHTML = "";
    return;
  }

  const visible = searchIndex
    .filter((entry) => entry.lang === document.documentElement.lang)
    .filter((entry) => searchablePage(entry).includes(query))
    .slice(0, 6);

  searchResults.hidden = false;
  searchResults.innerHTML = visible.length
    ? visible.map(renderSearchResult).join("")
    : `<p>${isGerman ? "Keine passende Wikiseite gefunden." : "No matching wiki page found."}</p>`;
}

function renderSearchResult(entry) {
  return `
    <a class="search-result" href="${entry.url}">
      <strong>${escapeHtml(entry.title)}</strong>
      <span>${escapeHtml(entry.category)}</span>
      <small>${escapeHtml(entry.summary)}</small>
    </a>
  `;
}

function renderResources() {
  if (!searchInput || !resourceRows || !resultCount) return;
  const query = normalize(searchInput.value);
  const visible = resources.filter((resource) => searchable(resource).includes(query));

  resultCount.textContent = isGerman
    ? `${visible.length} Eintr${visible.length === 1 ? "ag" : "äge"}`
    : `${visible.length} entr${visible.length === 1 ? "y" : "ies"}`;
  resourceRows.innerHTML = visible.length
    ? visible.map(renderResourceRow).join("")
    : `<tr class="empty-row"><td colspan="5">${
        isGerman
          ? "Kein Verzeichniseintrag passt zu dieser Suche."
          : "No directory entry matches this search."
      }</td></tr>`;
}

function renderResourceRow(resource) {
  return `
    <tr>
      <td>
        <strong>${escapeHtml(resource.title)}</strong><br />
        ${escapeHtml(resource.summary)}
      </td>
      <td>${escapeHtml(resource.type)}</td>
      <td>${renderAudience(resource)}</td>
      <td>${escapeHtml(resource.action)}</td>
      <td>
        ${resource.official ? `<span class="official-badge">${isGerman ? "Offiziell" : "Official"}</span><br />` : ""}
        <a href="${resource.source}">${escapeHtml(resource.sourceLabel)}</a>
      </td>
    </tr>
  `;
}

function renderAudience(resource) {
  const label = resource.audience === "want-help"
    ? (isGerman ? "Möchte helfen" : "Want to help")
    : (isGerman ? "Braucht Hilfe" : "Need help");
  return `<span class="audience-badge">${label}</span>`;
}

function searchable(resource) {
  return normalize(
    [
      resource.title,
      resource.audience,
      resource.type,
      resource.tags.join(" "),
      resource.summary,
      resource.action,
      resource.sourceLabel,
    ].join(" "),
  );
}

function searchablePage(entry) {
  return normalize([entry.title, entry.category, entry.summary, entry.keywords].join(" "));
}

function normalize(value) {
  return String(value || "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

if (searchInput) {
  searchInput.addEventListener("input", () => {
    renderSiteSearch();
    renderResources();
  });
}
applyTheme(storedTheme());
if (themeToggle) themeToggle.addEventListener("click", () => setTheme(nextTheme()));
renderSiteSearch();
renderResources();
