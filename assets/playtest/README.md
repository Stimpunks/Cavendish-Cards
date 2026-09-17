# Placeholder card faces

These are **placeholder cards** — a stand-in for the deck's real art, which is still to come.

## The carve-out

The deck's art is human- and community-made, and no AI-generated image is ever committed here. That has not changed.

What has changed is what a placeholder looks like. For months this folder held one dashed "image pending" box per card, on the reasoning that anything more would be passing a stand-in off as the deck's illustration. That was the wrong trade. Not one piece of human art has been submitted, and a deck of empty boxes is not a deck: the whole point is that a person of any age *points at a picture*, and there was no picture to point at. A deck nobody can use is not a purer deck.

So the project takes the same carve-out it already takes for its favicon, its app icons, and its card frames: **plain vector illustration, drawn in code, as an explicit placeholder.** Each motif is shapes with coordinates in [`../../scripts/card-art.py`](../../scripts/card-art.py) — readable, editable, and reviewable like any other source file, written by hand rather than generated from a prompt. Every card face carries `PLACEHOLDER ART · HUMAN ART WANTED` under the picture, so a card never claims to be finished.

**The call for art is still open, and it is still the goal.** See [`../../CALL-FOR-ART.md`](../../CALL-FOR-ART.md). These pictures exist so the deck can be printed, cut, and played *now* — not so it can stop waiting for artists.

## How they're made

Generated from the card files in [`../../cards/`](../../cards/) by [`../../scripts/build-placeholders.py`](../../scripts/build-placeholders.py), which draws each illustration with [`../../scripts/card-art.py`](../../scripts/card-art.py). From the repo root:

```
python3 scripts/build-placeholders.py
```

No dependencies. It reads each card's name, image cue, and prompt and writes `assets/playtest/<family>/<slug>.svg`: family tag, illustration, name, prompt. The image cue is the brief each illustration was drawn from; it is not printed on the card, because a person points at the picture and never has to read anything.

Interaction cards are skipped — they already have finished faces in [`../cards/interaction/`](../cards/interaction/).

Adding a card without adding a motif for it is reported on stderr, so a new card cannot quietly ship with an empty picture window. To see the whole set at once, `python3 scripts/card-art.py` writes a contact sheet of every motif to `/tmp`.

## Print-and-play PDF

For a ready-to-print sheet — nine cards per US-Letter page, with cut borders — run [`../../scripts/build-playtest-pdf.py`](../../scripts/build-playtest-pdf.py) from the repo root:

```
python3 scripts/build-playtest-pdf.py
```

It reuses the placeholder generator, so the PDF always matches these cards, and writes `cavendish-cards-playtest.pdf` beside them. Unlike the SVG generator, it needs two libraries: `pip install cairosvg weasyprint` (WeasyPrint also needs system libraries — Pango, cairo, GDK-PixBuf — see its [install notes](https://doc.courtbouillon.org/weasyprint/stable/first_steps.html)).

## When real art arrives

A placeholder is a temporary stand-in with a clean swap target. When an artist's piece is ready, drop it into the card template's `#art` window (see [`../templates/README.md`](../templates/README.md)), and the finished face graduates into [`../cards/`](../cards/) — where the web and print builds prefer it automatically. The matching file here, and its motif in `card-art.py`, can then be deleted.

These files are safe to regenerate or delete at any time. Do not treat them as the deck's artwork.
