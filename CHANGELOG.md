# Changelog

Notable changes to Cavendish Cards — both the **deck** (cards added or reworded) and the **site** (features and fixes at [cavendish.app](https://cavendish.app/)). Newest first; dates are when a change shipped. The site deploys continuously, so there are no version numbers — for the full detail, see the [commit history](https://github.com/Stimpunks/Cavendish-Cards/commits/main).

Each dated entry is split into **Deck** (changes to the cards themselves) and **Site** (changes to the web version). An entry only includes the sections that changed.

## 2026-07-18

### Site

- Added a **favicon and app icons** — the card-fan mark — across the site.
- Added **Open Graph and Twitter Card** metadata and a social share image, so shared links show a proper preview.
- The site is now an **offline-capable Progressive Web App**: it keeps working with no connection after the first visit, and can be installed to a home screen or dock.
- Added a **light/dark toggle** and automatic **dark mode** using the Solarized dark palette. It follows your device setting, and the toggle remembers your choice on your own device.
- Self-hosted the **Atkinson Hyperlegible** typeface, removing the third-party font request.
- Added a **Privacy & security page** and a strict set of security response headers, including a Content Security Policy.
- Added a **sitemap, robots.txt, and structured data**, plus web-app metadata, for better discoverability and installation.
- Added this **changelog**, kept in the repository and published as a page on the site.
