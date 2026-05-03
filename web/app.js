const resources = window.SEIN_RESOURCES || [];
const searchInput = document.querySelector("#resourceSearch");
const resourceRows = document.querySelector("#resourceRows");
const resultCount = document.querySelector("#resultCount");

function renderResources() {
  if (!searchInput || !resourceRows || !resultCount) return;
  const query = normalize(searchInput.value);
  const visible = resources.filter((resource) => searchable(resource).includes(query));

  resultCount.textContent = `${visible.length} entr${visible.length === 1 ? "y" : "ies"}`;
  resourceRows.innerHTML = visible.length
    ? visible.map(renderResourceRow).join("")
    : `<tr class="empty-row"><td colspan="5">No directory entry matches this search.</td></tr>`;
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
        ${resource.official ? '<span class="official-badge">Official</span><br />' : ""}
        <a href="${resource.source}">${escapeHtml(resource.sourceLabel)}</a>
      </td>
    </tr>
  `;
}

function renderAudience(resource) {
  const label = resource.audience === "want-help" ? "Want to help" : "Need help";
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

if (searchInput) searchInput.addEventListener("input", renderResources);
renderResources();
