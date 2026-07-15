# Playtest placeholders

These are **throwaway placeholder cards for playtesting** — not deck art.

Human- and community-made artwork takes time. So the deck can be printed, cut, and played *now*, this folder holds one simple, code-drawn placeholder per card: a plain "image pending" glyph, the card's image-cue text in words, and a `PLACEHOLDER · ART TO COME` marker. Nothing here is an illustration, and nothing here is final.

## How they're made

Generated from the card files in [`../../cards/`](../../cards/) by [`../../scripts/build-placeholders.py`](../../scripts/build-placeholders.py). From the repo root:

```
python3 scripts/build-placeholders.py
```

No dependencies. It reads each card's name, image cue, and prompt and writes `assets/playtest/<family>/<slug>.svg`. Interaction cards are skipped — they already have finished faces in [`../cards/interaction/`](../cards/interaction/).

A ready-to-print **print-and-play PDF** of all placeholders (nine cards per US-Letter page, with cut borders) can be assembled from these SVGs for quick table testing.

## When real art arrives

A placeholder is a temporary stand-in with a clean swap target. When an artist's piece is ready, drop it into the card template's `#art` window (see [`../templates/README.md`](../templates/README.md)), and the finished face graduates into [`../cards/`](../cards/). The matching file here can then be deleted.

These files are safe to regenerate or delete at any time. Do not treat them as the deck's artwork.
