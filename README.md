# Cavendish Cards

Cavendish Cards is an open deck for naming sensory and interaction needs — you point at a card, or lay a few, and no reading is required to play.

Cavendish Cards come out of the [Cavendish Space Project](https://stimpunks.org/projects/cavendish-space-project/) — an open experiment in designing environments that work for real neurodivergent and Disabled bodies and minds. The deck lets a person of any age shape the space around them, and lets the people beside them read what that person needs — without anyone having to explain in words they may not have.

Inspired by oracle decks, but these are not oracle cards. They are pictorial prompt cards.

**Broken systems, not broken people.** A person laying *cave, buzzy, headphones* has handed you a design brief, not a behavior report.

**[Play it on the web](https://cavendish.app/)** — browse the deck and lay a spread. No scoring, no accounts, nothing stored.

**[Artists: we need art](./CALL-FOR-ART.md)** — the deck's pictures are still placeholders. Any style, warm and human-made, CC0. You draw; we place it.

## Two rules hold the whole thing up

- **No scoring.** No points, no matching, no right answer, no winning. There is no wrong card and no wrong hand. Just a gentler way for a person to be understood.
- **The person controls sharing.** A spread laid face-down stays private. Turning a card up is the person sharing it. The turn is the consent — you don't turn their cards over for them.

## Not a screening tool

The deck augments a person's legibility to the people around them — on the person's own terms. It does not screen a person's inner world for institutional convenience. It makes needs sayable; it does not make people assessable. A spread is self-advocacy in the person's hands, never data gathered about them.

It carries none of the frameworks that turn human difference into a problem to be managed:

- **No pathology paradigm.** A card names a need, not a symptom. "Buzzy" describes an environment that is too much — not a disorder inside the person.
- **No deficit ideology.** The deck records what helps, never what a person lacks. If it isn't working, the environment is what hasn't fit yet.
- **No behaviorism.** No card is a target, a reward, or a compliance check. Turning a card up is communication, not performance — never something to shape a person toward "better" behavior.

Used to sort, score, rank, or flag people, the deck becomes the opposite of what it is for.

## Not an AAC board

The deck is a lens, not a language. It makes one hard-to-voice thing — sensory, regulatory, and emotional weather, and the conditions that help — sayable and shareable. It is not a communication system, and it does not try to be comprehensive the way augmentative and alternative communication (AAC) must be. Its vocabulary is small and opinionated on purpose.

- **Curated, not comprehensive.** AAC aims to let a person say anything. This deck names a specific, hard-to-voice inner world and stops there. Completeness is not the goal; chasing it is how the deck drifts.
- **A reframe, not a referent.** An AAC symbol is a neutral pointer ("juice" means the drink). Every card here carries a worldview in its Notes — how to hold it, why it is not misbehavior. A card that is only a label does not belong.
- **A design brief, not a request.** A spread changes the facilitator and the room, not just the message. AAC is a person's expressive channel; this deck is a relational object that reshapes the environment.

Most of all: **this deck sits alongside a person's real communication tools — never in place of them.** If a person needs a way to communicate, they need AAC — this holds at any age, and especially for children. Don't let "they have the cards" become a reason to under-provide it.

## Privacy & security

Cavendish Cards keeps nothing about you or a person. No accounts, no analytics, no tracking, no cookies; no spread, card choice, or reflection is ever recorded or sent anywhere. The only things saved live on your own device, for your own benefit — an optional light/dark preference and an offline copy of the site — and you can clear them at any time. The site loads only its own files, fonts included, with no third parties; it is served over HTTPS and ships a strict Content Security Policy and related protections.

Plain-language details are on the [Privacy & security page](https://cavendish.app/privacy.html); the exact response headers and policy live in [`netlify.toml`](./netlify.toml).

## The seven realms

Every card is pictorial first. The words are for the people alongside; no one ever has to read to play.

- **Places** — the five Cavendish zones: cave, campfire, watering hole, library, habitat.
- **Weather** — inner weather, not clinical states: bright, buzzy, foggy, heavy, warm.
- **What helps** — the niche-construction pieces: headphones, dim light, room to move, a way out.
- **Lily pads** — the in-between: i need a minute, watch first, coming back, stuck.
- **Growers** — who am I today: dandelion, tulip, orchid.
- **Love Locutions** — affirmations, given never earned: you belong here, you're not broken.
- **Interaction** — how open I am to talking, right now: come say hi, people i know, not right now. The Autistic community's color communication badges, brought into the deck.

Plus a **blank card** — the deck isn't finished. A person or a facilitator draws the need that's missing, and if it's good, it becomes a card. The community authors the deck by using it.

## What's in this repo

- [`cards/`](./cards/) — the deck itself: one card per file, sorted into the seven realms. This is the source of truth.
- [`cavendish-cards-starter-deck.md`](./cavendish-cards-starter-deck.md) — every card as a single readable list, with image cues and prompts. Generated by the script below — don't hand-edit.
- [`cavendish-cards-guidebook.md`](./cavendish-cards-guidebook.md) — the guidebook: an entry for every card, assembled from the cards. Generated by the script below — don't hand-edit.
- [`CARD.md`](./CARD.md) — the template for adding a new card. Copy it, fill it in, open a pull request.
- [`CALL-FOR-ART.md`](./CALL-FOR-ART.md) — the call for art: what we need from illustrators, and how to submit.
- [`assets/templates/`](./assets/templates/) — print-scale SVG card frames, one per realm plus the two card backs, each with an art slot for human-made artwork. See its [README](./assets/templates/README.md) for the workflow.
- [`assets/cards/`](./assets/cards/) — finished, print-ready card faces. So far the interaction realm, whose fixed color+shape designs need no illustrator.
- [`assets/playtest/`](./assets/playtest/) — temporary placeholder card faces for playtesting while human art is in progress. Not deck art. See its [README](./assets/playtest/README.md).
- [`cavendish-cards-facilitator-sheet.md`](./cavendish-cards-facilitator-sheet.md) — one page on the seven ways to play, for support staff. Screen-reader-friendly source.
- [`cavendish-cards-facilitator-sheet.pdf`](./cavendish-cards-facilitator-sheet.pdf) — the print-ready version of the same sheet.
- [`cavendish-cards-example-spreads.md`](./cavendish-cards-example-spreads.md) — worked gameplay examples: a moment, a spread someone laid, and how to read it as a design brief for the environment, never a report on a person. Also rendered as a page on the site.
- [`cavendish-cards-why-sheet.md`](./cavendish-cards-why-sheet.md) — a [Why Sheet](https://stimpunks.org/why/) making the case for the deck and connecting it to the [Cavendish Space](https://stimpunks.org/space/) learning-space principles.
- [`cavendish-cards-privacy.md`](./cavendish-cards-privacy.md) — the source for the site's Privacy & security page: what's kept (almost nothing) and the security measures behind the site.
- [`CHANGELOG.md`](./CHANGELOG.md) — notable changes to the deck and the site, newest first; also published as the [Changelog page](https://cavendish.app/changelog.html).
- [`scripts/build-all.py`](./scripts/build-all.py) — runs all the build scripts below in one command.
- [`scripts/build-guidebook.py`](./scripts/build-guidebook.py) — regenerates the guidebook from the card files.
- [`scripts/build-starter-deck.py`](./scripts/build-starter-deck.py) — regenerates the starter-deck list from the card files.
- [`scripts/build-placeholders.py`](./scripts/build-placeholders.py) — generates the playtest placeholder cards from the card files.
- [`scripts/build-playtest-pdf.py`](./scripts/build-playtest-pdf.py) — lays the placeholders out as a print-and-play PDF.
- [`scripts/build-facilitator-pdf.py`](./scripts/build-facilitator-pdf.py) — regenerates the facilitator-sheet PDF from its Markdown source.
- [`web/`](./web/) — the playable web version, live at [cavendish.app](https://cavendish.app/). A static site generated from the cards; see its [README](./web/README.md).
- [`scripts/build-site.py`](./scripts/build-site.py) — builds the web deck from the card files and page sources: card data, faces, the standalone pages, the offline service worker, sitemap, and robots.txt.
- [`netlify.toml`](./netlify.toml) — Netlify build configuration, plus the site's security response headers and Content Security Policy.

## Guidebook

Like an oracle deck, Cavendish Cards has a guidebook — [`cavendish-cards-guidebook.md`](./cavendish-cards-guidebook.md) — with an entry for every card: what the image means, what it names, and how to hold it, plus the lineage behind the metaphors. It describes the card, never the person.

The guidebook is generated from the cards themselves — each card's `Notes` field is its entry — so it never drifts out of sync. After adding or editing a card, regenerate it from the repo root:

```
python3 scripts/build-guidebook.py
```

No dependencies; it writes `cavendish-cards-guidebook.md` and prints a per-family count.

## Seven ways to play

One deck, across the age range: **show me** (early years), **build my day** (a person and a support worker), **class weather** (a whole group), **map the edges** (older learners), **play as the environment** (staff training), **moving between** (anyone, across a day), and **build a niche** (a learner or a group). The [facilitator sheet](./cavendish-cards-facilitator-sheet.md) has the details.

## Play it on the web

The deck is playable online at **[cavendish.app](https://cavendish.app/)** — browse and filter the cards, then lay a spread where each card starts face-down and you turn it up to share it. No scoring, no accounts, nothing stored. It's a static site generated from the card files and deployed from this repo by Netlify, so it stays in sync with the deck. See [`web/README.md`](./web/README.md).

It works offline and installs like an app. After the first visit the deck keeps working with no connection, and most browsers offer "Install" or "Add to Home Screen" to open it in its own window from a home screen or dock. It follows your device's light or dark setting, with an on-page toggle to switch. The offline copy and your theme choice are the only things kept, and they stay on your device — see [Privacy & security](https://cavendish.app/privacy.html).

## Playtesting before the art exists

Human- and community-made artwork takes time, so the deck can be printed and played now with temporary placeholders — plain, code-drawn stand-ins (an "image pending" glyph plus each card's image-cue text), never illustrations. From the repo root:

```
python3 scripts/build-placeholders.py     # writes assets/playtest/<family>/<slug>.svg
python3 scripts/build-playtest-pdf.py     # writes assets/playtest/cavendish-cards-playtest.pdf, nine cards a page with cut lines
```

The placeholder generator has no dependencies; the PDF builder needs `cairosvg` and `weasyprint` plus their native libraries (on macOS: `brew install cairo pango gdk-pixbuf libffi`). Both read the card files, so the output always matches the deck. When real art arrives it drops into the template's art slot and the finished face moves into [`assets/cards/`](./assets/cards/). See [`assets/playtest/README.md`](./assets/playtest/README.md).

## Contributing

The deck grows in the open. To add a card, copy [`CARD.md`](./CARD.md), fill it in, and open a pull request. After adding or editing cards, run `python3 scripts/build-all.py` from the repo root to regenerate the starter deck, guidebook, placeholders, web deck, and print-and-play PDF. The guidance inside the template carries the only rules: sentence case, human- and community-made art, no scoring language, counter-deficit framing — nothing that reads a card as a symptom, a target, or a reward. Always capitalize Autistic and Disabled. Illustrators: see the [call for art](./CALL-FOR-ART.md) for the style and specs, then email work to stimpunks@stimpunks.org — we handle placement. (The card frames live in [`assets/templates/`](./assets/templates/) if you'd rather drop artwork into the slot yourself.)

## License

Dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Free to use, print, translate, adapt, and remix — no permission needed, no attribution required. Default to open.
