# Changelog

Notable changes to Cavendish Cards — both the **deck** (cards added or reworded) and the **site** (features and fixes at [cavendish.app](https://cavendish.app/)). Newest first; dates are when a change shipped. The site deploys continuously, so there are no version numbers — for the full detail, see the [commit history](https://github.com/Stimpunks/Cavendish-Cards/commits/main).

Each dated entry is split into **Deck** (changes to the cards themselves) and **Site** (changes to the web version). An entry only includes the sections that changed.

## 2026-07-19

### Site

- **Copy for a journal** now includes the date and an optional note field (kept only in the copy, never saved).

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
- Reworked the **I need a bodymind break** button into a calming full-screen break: a modal (with the deck paused behind it) holding the definition of *bodymind*, an affirmation invitation, a self-hosted looping ocean-waves recording by Adriel Jeremiah Wool, and a collapsible list of ways to affirm your bodymind.
- Fixed the **Copy for a journal** button failing silently in privacy-hardened Firefox browsers (such as Zen); it now uses a reliable fallback and shows a "Copied!" confirmation.

## 2026-07-17

### Site

- Fixed a card-identity bug: cards are now keyed by realm *and* slug, so each realm's "your own" card no longer collides with another's in selection, card backs, and faces.

## 2026-07-16

### Deck

- Added the monotropism weather cards — **in the zone**, **meerkat**, **round and round**, and **pulled every way** — with their lineage credited.
- Added **can't tell** (interoception) and **need more** (sensory seeking) to Weather, plus **happy flappy** (happy stimming).
- Added **let me stim**, **let me finish**, and **let me come and go**, along with more niche-construction cards, regrouping *What helps* into twelve sense signposts.
- Reframed *Love Locutions* as self-affirmation (shown as **Kind words** in the app), moved **parallel existence** into *What helps*, and kept penguin pebbling as a guidebook note rather than a card.
- Named the **"not an AAC board"** boundary, with an inclusion test in the card template, the README, and the guidebook.
- Curated the Weather order into a gentle range with no good/bad split, renamed families to **realms**, and made **lily pads** a browsable realm.

### Site

- Added native **Why**, **Origin**, and **Facilitator** pages, a generated **Implementation guidebook**, and a site-wide collapsed menu.
- Added **lightbox zoom** and a collapsible "what this card means" to card previews, and grouped the deck by realm with per-realm info.
- Made laid cards toggle back off the table, kept an added-state on tiles, and added a sticky jump-to-table button.
- Added the **build a niche** and **map your rhythm** play modes (seven ways to play), the Why Sheet, and a consent guardrail in the implementation guidebook.

## 2026-07-15

### Deck

- Added **guidebook Notes to every card** — the entry that says what each card means and how to hold it.
- Added **reflection questions**: per-realm pools plus per-card overrides, with the Reflection field documented in the card template.

### Site

- Added the **playable web deck** and its Netlify build, and linked it from the README.
- Ran four playtest rounds: intro and guidebook pages, a bodymind-break, an interaction-first guided order, sense grouping, a reflection summary, and per-realm draw-your-own.
- Added the **guidebook assembler**, the **print-and-play PDF** builder, and the playtest placeholder generator.
- Added the **call for art**, linked from the README and the site.

## 2026-07-14

### Deck

- **Initial deck** — 49 cards scaffolded across six families.
- Added the **interaction realm** — the Autistic community's color communication badges — with finished card faces.
- Stated the deck is **not a screening tool**, refusing the pathology, deficit, and behaviorism framings.

### Site

- Added print-scale **SVG card templates** for every family plus the blank, and the two card backs.
- Rebuilt the **facilitator sheet** (larger type, six-color rainbow, sharing models) and wrote the project README.
