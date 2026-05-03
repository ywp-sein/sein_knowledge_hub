const CACHE_NAME = "sein-knowledge-hub-v8";
const ASSETS = [
  "./",
  "./index.html",
  "./research-social-issues.html",
  "./homelessness-berlin.html",
  "./homelessness-how-to-help.html",
  "./homelessness-organizations-berlin.html",
  "./homelessness-policies-germany.html",
  "./styles.css",
  "./resources.js",
  "./app.js",
  "./manifest.webmanifest",
  "./icon.svg",
];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(ASSETS)));
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key)))),
  );
});

self.addEventListener("fetch", (event) => {
  if (event.request.method !== "GET") return;
  event.respondWith(
    caches.match(event.request).then((cached) => {
      return cached || fetch(event.request);
    }),
  );
});
