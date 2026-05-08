const CACHE_NAME = "sein-knowledge-hub-v40";
const ASSETS = [
  "./",
  "./index.html",
  "./index.de.html",
  "./some-hows/research-social-issues.html",
  "./some-hows/research-social-issues.de.html",
  "./some-hows/how-to-change-society.html",
  "./some-hows/how-to-change-society.de.html",
  "./homelessness/homelessness-berlin.html",
  "./homelessness/homelessness-berlin.de.html",
  "./homelessness/homelessness-how-to-help.html",
  "./homelessness/homelessness-how-to-help.de.html",
  "./homelessness/homelessness-organizations-berlin.html",
  "./homelessness/homelessness-organizations-berlin.de.html",
  "./homelessness/homelessness-policies-germany.html",
  "./homelessness/homelessness-policies-germany.de.html",
  "./development/knowledge-hub-version-log.html",
  "./development/knowledge-hub-version-log.de.html",
  "./development/knowledge-hub-next-steps.html",
  "./development/knowledge-hub-next-steps.de.html",
  "./legal/imprint.html",
  "./legal/imprint.de.html",
  "./legal/privacy.html",
  "./legal/privacy.de.html",
  "./legal/license.html",
  "./legal/license.de.html",
  "./assets/css/styles.css",
  "./assets/js/components.js",
  "./assets/js/resources.js",
  "./assets/js/search-index.js",
  "./assets/js/app.js",
  "./manifest.webmanifest",
  "./assets/icons/icon.svg",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  if (event.request.mode === "navigate" || event.request.destination === "document") {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
          return response;
        })
        .catch(() => caches.match(event.request)),
    );
    return;
  }
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request);
    }),
  );
});
