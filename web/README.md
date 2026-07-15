# The web deck

A calm, no-scoring web version of Cavendish Cards. Browse the deck, filter by family, and lay cards on a table — where they arrive **face-down** and you **turn them up** when you want to share them. That turn is the whole point: it puts the deck's sharing-is-consent rule into the interaction itself.

Nothing is scored. Nothing is stored. There are no accounts, no timers, and no analytics — a spread lives only in the current browser session.

## How it's built

This is a static site with no framework and no build tooling to install. Two hand-authored files and one generated data file:

- `index.html`, `styles.css`, `app.js` — the site shell (edited by hand).
- `cards.json` and `faces/` — **generated** from the card files by [`../scripts/build-site.py`](../scripts/build-site.py). Don't hand-edit them.

The generator reads every card in [`../cards/`](../cards/), uses the finished face from [`../assets/cards/`](../assets/cards/) when one exists and a placeholder otherwise, copies the two card backs, and writes `cards.json`. So the site always matches the deck, and when real artwork lands in `assets/cards/` it shows up on the site on the next build — no site edits needed.

## Run it locally

From the repo root:

```
python3 scripts/build-site.py          # writes web/cards.json and web/faces/
python3 -m http.server --directory web  # then open http://localhost:8000
```

Serve it over http rather than opening `index.html` directly — browsers block `fetch('cards.json')` from `file://` URLs.

## Deploy on Netlify

1. In Netlify, **Add new site → Import an existing project**, and connect the `Stimpunks/Cavendish-Cards` GitHub repo.
2. The build settings come from [`../netlify.toml`](../netlify.toml): build command `python3 scripts/build-site.py`, publish directory `web`. Leave Netlify's defaults; it reads the file.
3. Deploy. Every push to the repo rebuilds and republishes, so editing a card and pushing updates the live site.

If a deploy ever fails on the Python step, you can instead run `python3 scripts/build-site.py` locally, commit `web/cards.json` and `web/faces/`, and set the Netlify build command to empty with publish directory `web`.

## Notes

- **Fonts.** The site loads Atkinson Hyperlegible from Google Fonts, with a system-font fallback. To avoid the external request, self-host the font files and swap the `<link>` in `index.html` for an `@font-face` rule.
- **Accessibility.** Full keyboard operation, visible focus, screen-reader announcements for laying and turning cards, and `prefers-reduced-motion` respected. Keep these if you extend it.
- **License.** CC0 1.0, like the rest of the deck.
