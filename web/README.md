# The web deck

A calm, no-scoring web version of Cavendish Cards. Browse the deck, filter by family, and lay cards on a table — where they arrive **face-down** and you **turn them up** when you want to share them. That turn is the whole point: it puts the deck's sharing-is-consent rule into the interaction itself.

Nothing is scored. There are no accounts, no timers, and no analytics, and nothing you do is ever sent anywhere — a spread lives only in the page while it is open. The only things kept are on your own device (an optional light/dark preference and an offline copy of the site); see the [Privacy & security page](https://cavendish.app/privacy.html).

## How it's built

A static site with no framework and no build tooling to install — just Python's standard library. The files fall into three groups.

**Hand-authored** (edit these directly):

- `index.html` — the deck page shell.
- `styles.css` — all styling, including the light and dark palettes.
- `app.js` — the deck itself: rendering, filtering, laying and turning cards, the lightbox.
- `sw-register.js` — registers the service worker on every page.
- `theme-toggle.js` — the on-page light/dark toggle.

**Committed static assets** (in the repo, not generated):

- `fonts/` — Atkinson Hyperlegible (Regular, Bold, Italic), self-hosted as woff2.
- `favicon.svg`, `favicon.ico`, `favicon-*.png`, `apple-touch-icon.png`, `icon-192.png`, `icon-512.png` — the card-fan favicon and app icons.
- `og-image.png` — the social share image.
- `site.webmanifest` — the web-app manifest (name, icons, theme colour, standalone display).

**Generated** by [`../scripts/build-site.py`](../scripts/build-site.py) — don't hand-edit; they're gitignored and Netlify rebuilds them on every deploy:

- `cards.json` and `faces/` — the deck data and card faces, from the card files.
- `guidebook.html`, `implementation.html`, `why.html`, `origin.html`, `facilitator.html`, `privacy.html` — the standalone pages.
- `sw.js` — the offline service worker, generated from [`../scripts/sw-template.js`](../scripts/sw-template.js) and version-stamped each build.
- `sitemap.xml`, `robots.txt`.

The generator reads every card in [`../cards/`](../cards/), uses the finished face from [`../assets/cards/`](../assets/cards/) when one exists and a placeholder otherwise, copies the two card backs, and renders the prose pages from their Markdown sources in the repo root. So the site always matches the deck and its sources — no site edits needed when a card or a sheet changes.

## Run it locally

From the repo root:

```
python3 scripts/build-site.py           # writes cards.json, faces/, the pages, sw.js, sitemap.xml, robots.txt
python3 -m http.server --directory web  # then open http://localhost:8000
```

Serve it over http rather than opening `index.html` directly: browsers block `fetch('cards.json')` from `file://`, and the service worker only runs in a secure context (http on `localhost` counts). The security headers and CSP are applied by Netlify from [`../netlify.toml`](../netlify.toml), so they are not present when serving locally — that's expected.

## Deploy on Netlify

1. In Netlify, **Add new site → Import an existing project**, and connect the `Stimpunks/Cavendish-Cards` GitHub repo.
2. The build settings come from [`../netlify.toml`](../netlify.toml): build command `python3 scripts/build-site.py`, publish directory `web`. Leave Netlify's defaults; it reads the file. The same file also sets the site's response headers (see Security & privacy below).
3. Deploy. Every push rebuilds and republishes, so editing a card and pushing updates the live site.

## Offline & install

The site is a Progressive Web App. `sw-register.js` registers `sw.js` on every page; on first visit the worker precaches the shell, all card faces, the fonts, and every page, so the deck keeps working with no connection. In most browsers people can also install it ("Install" / "Add to Home Screen") to open it in its own window from a home screen or dock.

`sw.js` is generated from `../scripts/sw-template.js` and stamped with a version hash derived from the site's files, so each deploy gets a fresh cache and old caches are evicted when the new worker activates. Navigations and `cards.json` are network-first (a deploy is never more than one load stale); other same-origin assets are cache-first. Returning visitors pick up a new version on their next reload.

## Theming (light & dark)

Light is the default. Dark is the Solarized dark pairing of the palette, defined with CSS custom properties in `styles.css`:

- **Automatic.** `@media (prefers-color-scheme: dark)` applies dark for anyone whose device is set to dark — no JavaScript needed.
- **Manual.** `theme-toggle.js` adds an on-page toggle (next to the Menu) that flips light/dark and remembers the choice in `localStorage`. Until someone uses it, the site follows the device setting.
- **No flash.** A tiny inline script in each page's `<head>` applies a saved choice before first paint. Because the CSP forbids inline scripts, that one script is whitelisted by its SHA-256 hash in `netlify.toml`. If you change it (it lives as `_THEME_INLINE` in `build-site.py`, mirrored in `index.html`), recompute the hash.

Both palettes meet WCAG AA contrast. Card faces keep their own light backgrounds, so in dark mode they read as light cards on a dark table.

## Security & privacy

Response headers are set in [`../netlify.toml`](../netlify.toml):

- A strict **Content Security Policy**: everything loads from the site's own origin only (`default-src 'self'`) — no third-party scripts, styles, fonts, or images, and no inline scripts except the single hashed theme script. `object-src`, `base-uri`, and `form-action` are locked down, and `frame-ancestors` allows embedding only from Stimpunks.
- `X-Content-Type-Options: nosniff`, a `Referrer-Policy`, and a `Permissions-Policy` that denies camera, microphone, geolocation, and topics.
- Long-lived immutable caching for `/fonts/*`.

Nothing about a user is stored or transmitted. The only local storage is the theme preference and the service-worker cache, both on-device and clearable. The full, plain-language statement is [`../cavendish-cards-privacy.md`](../cavendish-cards-privacy.md), published as the [Privacy & security page](https://cavendish.app/privacy.html).

## Notes

- **Fonts.** Atkinson Hyperlegible is self-hosted from `fonts/` (woff2), declared with `@font-face` in `styles.css` and preloaded in each page `<head>` — no external font request.
- **Accessibility.** Full keyboard operation, visible focus, screen-reader announcements for laying and turning cards, `prefers-reduced-motion` respected, and both palettes at WCAG AA contrast. Keep these if you extend it.
- **License.** CC0 1.0, like the rest of the deck.
