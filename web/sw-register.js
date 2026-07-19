/* Register the offline service worker (scope: the whole site).
   Loaded on every page so the deck works offline regardless of entry point. */
if ('serviceWorker' in navigator) {
  window.addEventListener('load', function () {
    navigator.serviceWorker.register('/sw.js').catch(function () {});
  });
}
