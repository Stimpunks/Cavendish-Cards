/* Cavendish Cards offline service worker.
   Generated into web/sw.js by scripts/build-site.py — do NOT edit web/sw.js by
   hand. Edit this template (scripts/sw-template.js) and rebuild. __VERSION__ and
   __PRECACHE__ are filled in per build so a new deploy evicts old caches. */

const VERSION = '__VERSION__';
const PRECACHE = 'cavendish-precache-' + VERSION;
const RUNTIME = 'cavendish-runtime-' + VERSION;
const FONTS = 'cavendish-fonts';
const PRECACHE_URLS = __PRECACHE__;

self.addEventListener('install', function (event) {
  event.waitUntil((async function () {
    const cache = await caches.open(PRECACHE);
    // Per-URL adds so one missing asset can't fail the whole install.
    await Promise.allSettled(PRECACHE_URLS.map(function (u) { return cache.add(u); }));
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', function (event) {
  event.waitUntil((async function () {
    const keep = [PRECACHE, RUNTIME, FONTS];
    const names = await caches.keys();
    await Promise.all(names.map(function (n) {
      if (n.indexOf('cavendish-') === 0 && keep.indexOf(n) === -1) {
        return caches.delete(n);
      }
      return undefined;
    }));
    await self.clients.claim();
  })());
});

function isFontRequest(url) {
  return url.origin === 'https://fonts.googleapis.com' ||
         url.origin === 'https://fonts.gstatic.com';
}

self.addEventListener('fetch', function (event) {
  const req = event.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);

  // Google Fonts: serve fast from cache, refresh in the background.
  if (isFontRequest(url)) {
    event.respondWith(staleWhileRevalidate(req, FONTS));
    return;
  }

  // Leave other cross-origin requests to the network untouched.
  if (url.origin !== self.location.origin) return;

  // Freshness where it matters: page navigations and the card data are
  // network-first, so a deploy is never more than one load stale.
  if (req.mode === 'navigate' || url.pathname === '/cards.json') {
    event.respondWith(networkFirst(req));
    return;
  }

  // Everything else same-origin (styles, script, faces, icons): cache-first.
  event.respondWith(cacheFirst(req));
});

async function networkFirst(req) {
  const cache = await caches.open(RUNTIME);
  try {
    const res = await fetch(req);
    if (res && res.ok) cache.put(req, res.clone()).catch(function () {});
    return res;
  } catch (err) {
    const cached = await caches.match(req);
    if (cached) return cached;
    if (req.mode === 'navigate') {
      const shell = (await caches.match('/')) || (await caches.match('/index.html'));
      if (shell) return shell;
    }
    throw err;
  }
}

async function cacheFirst(req) {
  const cached = await caches.match(req);
  if (cached) return cached;
  const cache = await caches.open(RUNTIME);
  const res = await fetch(req);
  if (res && res.ok) cache.put(req, res.clone()).catch(function () {});
  return res;
}

async function staleWhileRevalidate(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  const network = fetch(req).then(function (res) {
    if (res) cache.put(req, res.clone()).catch(function () {});
    return res;
  }).catch(function () { return null; });
  return cached || network || fetch(req);
}
