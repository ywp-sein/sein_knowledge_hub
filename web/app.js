const resources = window.SEIN_RESOURCES || [];
const searchIndex = window.SEIN_SEARCH_INDEX || [];
const searchInput = document.querySelector("#wikiSearch");
const searchResults = document.querySelector("#wikiSearchResults");
const resourceRows = document.querySelector("#resourceRows");
const resultCount = document.querySelector("#resultCount");
const isGerman = document.documentElement.lang === "de";

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
renderSiteSearch();
renderResources();
