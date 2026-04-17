const CACHE_NAME = 'tech4today-pulse-v1';
const ASSETS_TO_CACHE = [
  '/',
  '/static/css/style.css',
  '/static/icon-512.png',
  'https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&family=Outfit:wght@900&display=swap'
];

// Install Event
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('SW: Pre-caching static assets');
      return cache.addAll(ASSETS_TO_CACHE);
    })
  );
  self.skipWaiting();
});

// Activate Event
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      );
    })
  );
  self.clients.claim();
});

// Fetch Event (Network First, then Cache)
self.addEventListener('fetch', (event) => {
  // Only cache GET requests
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Clone the response to store in cache
        const resClone = response.clone();
        caches.open(CACHE_NAME).then((cache) => {
          // Do not cache API responses or dynamic content for too long
          if (!event.request.url.includes('/api/')) {
             cache.put(event.request, resClone);
          }
        });
        return response;
      })
      .catch(() => caches.match(event.request).then((res) => res))
  );
});
