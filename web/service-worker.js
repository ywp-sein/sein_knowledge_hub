const CACHE_NAME = "sein-knowledge-hub-v17";
const ASSETS = [
  "./",
  "./index.html",
  "./index.de.html",
  "./research-social-issues.html",
  "./research-social-issues.de.html",
  "./homelessness-berlin.html",
  "./homelessness-berlin.de.html",
  "./homelessness-how-to-help.html",
  "./homelessness-how-to-help.de.html",
  "./homelessness-organizations-berlin.html",
  "./homelessness-organizations-berlin.de.html",
  "./homelessness-policies-germany.html",
  "./homelessness-policies-germany.de.html",
  "./knowledge-hub-version-log.html",
  "./knowledge-hub-version-log.de.html",
  "./knowledge-hub-next-steps.html",
  "./knowledge-hub-next-steps.de.html",
  "./styles.css",
  "./resources.js",
  "./search-index.js",
  "./app.js",
  "./manifest.webmanifest",
  "./icon.svg",
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
