# Card templates

Front templates for Cavendish Cards — one SVG per family, plus the two shared card backs. Each front is a print-scale frame that a human illustrator fills with artwork.

## Files

- `places.svg`, `weather.svg`, `what-helps.svg`, `lily-pad.svg`, `grower.svg`, `love-locution.svg`, `blank.svg` — one front template per family.
- `interaction.svg` — the interaction family. A special case: fixed color+shape designs (green circle, yellow triangle, red square, neutral diamond, orange star), not art-window frames — the badge is the art. Keep both color and shape for colorblind readers. The five finished faces live in [`assets/cards/interaction/`](../cards/interaction/).
- `back-standard.svg` — the shared back for the face-down realms (every family except Love Locutions and Interaction).
- `back-love-locution.svg` — the distinct Love Locution back, so an affirmation is never mistaken for a state or a need.
- `back-interaction.svg` — the distinct Interaction back; the badges are shown and worn, not laid face-down, so they don't share the standard back.

## Card size

`750 × 1050` units = 2.5 × 3.5 inches at 300 dpi (standard poker card). No bleed is included — add your printer's bleed if you need it.

## The art slot

Each front holds two relevant pieces:

- `#art` — a rect marking the exact bounds of the picture window. Drop artwork in and clip it to these bounds, or replace the rect with your artwork.
- `#art-placeholder` — the dashed frame, corner ticks, and "place art here" label. Delete this group once real art is in.

Art is human- and community-made. The frame holds the layout; it never supplies the picture. Don't paste AI-generated images.

## Anatomy

- **Family tag** (top-left) — the family name in its color. Matches the `Family` field and the `cards/<family>/` folder.
- **Art window** — `#art`.
- **Name** — the card's H1, in Atkinson Hyperlegible bold.
- **Prompt** — the gentle line. Love Locutions carry no prompt (given or claimed); the blank card's window is a draw-on space, not an illustrator's.

## Font

Type is set in [Atkinson Hyperlegible](https://www.brailleinstitute.org/freefont/), referenced by name rather than embedded. Install the font to see cards in-brand; without it, text falls back to a plain sans. Keeping it referenced keeps the files small and the text editable.

## Color

Solarized palette. Card front background is BASE2 `#eee8d5`; the art windows and card backs use BASE3 `#fdf6e3`. Each family carries its own accent — read it off the front file.

## Making a new card

1. Duplicate the matching family template.
2. Replace the art in `#art`, then delete `#art-placeholder`.
3. Set the name (H1) and prompt to match the card's `.md` file in `cards/<family>/`.

## License

Dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Free to use, print, adapt, and remix.
