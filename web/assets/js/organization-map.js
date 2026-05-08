(() => {
  const container = document.querySelector("#organizationMap");
  if (!container) return;

  const fallback = document.querySelector(".map-fallback");
  const lang = container.dataset.mapLang === "de" ? "de" : "en";
  const labels = {
    en: {
      source: "Source",
      approx: "Approximate service-area marker",
      loadError: "The map could not load. Use the organization list below.",
    },
    de: {
      source: "Quelle",
      approx: "Ungefährer Marker für ein Angebotsgebiet",
      loadError: "Die Karte konnte nicht geladen werden. Nutze die Organisationsliste darunter.",
    },
  }[lang];

  if (!window.L) {
    if (fallback) fallback.textContent = labels.loadError;
    return;
  }

  const dataUrl = new URL("../data/berlin-homelessness-organizations.json", document.currentScript.src);

  fetch(dataUrl)
    .then((response) => {
      if (!response.ok) throw new Error(`Map data request failed: ${response.status}`);
      return response.json();
    })
    .then((payload) => {
      const organizations = payload.organizations.filter((organization) => {
        const coordinates = organization.coordinates || {};
        return Number.isFinite(coordinates.latitude) && Number.isFinite(coordinates.longitude);
      });
      if (!organizations.length) throw new Error("No organization coordinates found");

      const map = L.map(container, {
        scrollWheelZoom: false,
      });

      L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      }).addTo(map);

      const bounds = [];
      organizations.forEach((organization) => {
        const coordinates = organization.coordinates;
        const marker = L.marker([coordinates.latitude, coordinates.longitude], {
          icon: L.divIcon({
            className: "organization-map-marker",
            html: `<span>${escapeHtml(organization.map_marker)}</span>`,
            iconSize: [30, 30],
            iconAnchor: [15, 15],
            popupAnchor: [0, -12],
          }),
          title: organization.name[lang],
        }).addTo(map);

        marker.bindPopup(popupContent(organization, labels, lang));
        bounds.push([coordinates.latitude, coordinates.longitude]);
      });

      map.fitBounds(bounds, { padding: [28, 28], maxZoom: 13 });
      if (fallback) fallback.hidden = true;
    })
    .catch(() => {
      if (fallback) fallback.textContent = labels.loadError;
    });
})();

function popupContent(organization, labels, lang) {
  const approximate = organization.coordinates.precision.includes("placeholder")
    ? `<small>${escapeHtml(labels.approx)}</small>`
    : "";
  return `
    <div class="organization-map-popup">
      <strong>${escapeHtml(organization.name[lang])}</strong>
      <span>${escapeHtml(organization.address.label)}</span>
      ${approximate}
      <a href="${escapeHtml(organization.source.url)}" target="_blank" rel="noopener">${escapeHtml(labels.source)}</a>
    </div>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}
