#!/usr/bin/env python3
"""Build cavendish-cards-starter-deck.md from the card files.

One readable table per realm (name, image cue, prompt) plus deck-balance
counts, regenerated from cards/ so the list never drifts. The editorial prose
(realm blurbs, card backs, ways to play) lives here as text. No dependencies.

Draw-your-own cards (each realm's `your own`, and the standalone blank) are
templates, so they are not enumerated per realm — they are counted together as
"Draw your own" in the balance, matching how the deck treats blanks.

Usage, from the repo root:
    python3 scripts/build-starter-deck.py
"""

from pathlib import Path
import importlib.util
import sys


def _load_placeholders():
    path = Path(__file__).resolve().parent / "build-placeholders.py"
    if not path.exists():
        sys.exit(f"Could not find {path}")
    spec = importlib.util.spec_from_file_location("build_placeholders", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Realms in canonical print order (Places first), each with the blurb that
# heads its section.
REALMS = [
    ("places", "Places",
     "The five Cavendish zones. Fixed. Everything else sits in one of these."),
    ("weather", "Weather",
     "Inner weather, not clinical states. Covers the whole range: too much, too "
     "little, and settled — good and hard alike."),
    ("what-helps", "What helps",
     "The niche-construction pieces — the ways we change the environment so it "
     "fits. The workhorse realm, and where the staff game finds its conflicts."),
    ("lily-pad", "Lily pads",
     "The in-between. Transitions are where environments break, so the edges get "
     "their own cards. Every one is a landing place, not a failure. \"Stuck\" is "
     "information."),
    ("grower", "Growers",
     "Who am I today. Optional. A non-deficit way to hold that different people "
     "bloom in different conditions — and none is broken. Draw from the dandelion "
     "/ tulip / orchid resilience metaphor."),
    ("love-locution", "Love Locutions",
     "Affirmations. Given between people, never earned, never a reward for "
     "behaving. Distinct card back so it reads as a gift. If it's a prize, it's "
     "scoring — keep it a gift."),
    ("interaction", "Interaction",
     "How open I am to talking, right now. The Autistic community's color "
     "communication badges — Autism Network International, the first Autreat, Jim "
     "Sinclair, 1996 — brought into the deck. Color and shape are redundant, so "
     "the cards work for colorblind readers: keep both. These are the deck's one "
     "exception to the face-down default: their whole job is to be shown, and "
     "they can be worn and flipped as status changes. See "
     "https://stimpunks.org/access/interaction/."),
]

# Curated order per realm; any card not listed falls in alphabetically after
# the listed ones. "your own" is handled separately (not enumerated).
ORDER = {
    "places": ["the-cave", "the-campfire", "the-watering-hole", "the-library",
               "the-habitat"],
    "weather": ["bright", "buzzy", "prickly", "full", "foggy", "heavy",
                "far-away", "fizzy", "stormy", "warm"],
    "what-helps": ["headphones", "dim-the-light", "something-soft",
                   "a-big-squeeze", "room-to-move", "busy-hands",
                   "a-steady-sound", "just-one-person", "a-way-out",
                   "my-own-spot", "something-to-chew", "less-talking",
                   "tell-me-first", "no-rush"],
    "lily-pad": ["i-need-a-minute", "watch-first", "coming-back", "not-yet",
                 "stuck", "ready-now", "all-done", "slowly"],
    "grower": ["dandelion", "tulip", "orchid"],
    "love-locution": ["you-belong-here", "youre-not-broken",
                      "its-okay-to-need-what-you-need", "im-glad-youre-here",
                      "you-can-rest", "your-way-is-a-real-way", "nothing-to-fix",
                      "i-see-you"],
    "interaction": ["come-say-hi", "people-i-know", "not-right-now",
                    "ive-got-this", "ask-first"],
}

HEADER = """# Cavendish Cards — Starter Deck

A pictorial deck for naming sensory and niche-construction needs. Point at a card, or lay a few. No reading required to play. No points, no matching, no right answer, no winning.

The starter deck is **{total} cards** across seven realms, plus blanks. It is usable by early years out of the box and deep enough to run staff training. It grows in the open: one card, one file, community-authored, CC0.

Broken systems, not broken people. A child laying *cave, buzzy, headphones* has handed you a design brief, not a behavior report.

---- 

## How to read this list

Each card is one small spec:

- **Name** — the words under the picture. For the adults. A child never needs to read them.
- **Image cue** — a motif for the illustrator. All deck art is human- and community-made; these are starting points, not finished art.
- **Prompt** — an optional line an adult can voice, or an older child can read. Gentle, never a demand.

Sentence case throughout. Always capitalize Autistic and Disabled."""

DRAW_YOUR_OWN = """## Draw your own

Every realm carries a **draw-your-own** card, and the deck ships with spare blanks besides — a blank front with the realm colors down one edge so it can join any realm. A child or a staff member draws the need the deck doesn't have yet. This is the sketch-based play from the brief, and it is how the community authors the deck: use it, find the gap, draw the card, send it in.

| Name          | Image cue                 | Prompt                                   |
| ------------- | ------------------------- | ---------------------------------------- |
| draw your own | a blank card and a pencil | The deck isn't finished. What's missing? |"""

BACKS = """## Two card backs

- **Standard back** — the umbrella logo, Solarized palette, a six-color rainbow accent, and the line *how i feel, what i need*, set in Atkinson Hyperlegible. One shared back for Places, Weather, What helps, Lily pads, Growers, Interaction, and Blanks.
- **Love Locution back** — visibly different, so a gift is never mistaken for a state or a need. It should read, at a glance, as *someone gave me this.*

The distinct back also does the sharing work: a spread laid face-down stays private until the child turns it up. The gesture of turning a card over *is* consent. Interaction cards are the deliberate exception: their job is to be shown, so they sit face-up, and the child changes them by flipping or swapping — still the child's choice, just worn openly."""

PLAY = """## Playing across the age range

The same {total} cards, seven ways:

- **Early years — show me.** One card. The adult mirrors it back.
- **Child and staff — build my day.** A place, a weather, a couple of what-helps. A sentence in pictures.
- **A class — class weather.** Everyone lays a weather card face-up. No one named, nothing scored.
- **Older kids — map the edges.** Walk lily pads across a timetable to find the hard transitions.
- **Staff training — play as the environment.** Deal conflicting what-helps cards; build one habitat that holds them all. Feel neurological pluralism instead of hearing about it.
- **Moving between — map your rhythm.** Lay places, interaction moods, and lily pads left to right to show how you move between alone and together across a day: the cave, then ready now, then the campfire, then a minute alone, then back. Move a card when the rhythm shifts. This is intermittent collaboration — nobody stays in one place all day.
- **Build a niche — design a space that fits.** Lay the what-helps that would make a space yours — the den, less to look at, the right temperature — with *the habitat* card at the center. A design brief for the room, not a snapshot of the day. Then build it on any budget: see [Creating Cavendish Space on a Budget](https://stimpunks.org/2024/03/14/creating-cavendish-space-on-a-budget/)."""

LICENSE = """## License

This starter deck is free to use, print, translate, adapt, and remix.

Version: 0.1 (starter draft)
License: This work is dedicated to the public domain under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). Home: https://stimpunks.org/projects/cavendish-space-project/
Repository: `github.com/Stimpunks/Cavendish-Cards`"""

SEP = "\n\n---- \n\n"


def ordered_slugs(slug, present):
    order = ORDER.get(slug, [])
    listed = [s for s in order if s in present]
    rest = sorted(s for s in present if s not in order and s != "your-own")
    return listed + rest


def table(rows):
    headers = ["Name", "Image cue", "Prompt"]
    widths = [len(h) for h in headers]
    for r in rows:
        for i, c in enumerate(r):
            widths[i] = max(widths[i], len(c))

    def line(cells):
        return "| " + " | ".join(c.ljust(widths[i]) for i, c in enumerate(cells)) + " |"

    out = [line(headers), "| " + " | ".join("-" * widths[i] for i in range(3)) + " |"]
    for r in rows:
        out.append(line(r))
    return "\n".join(out)


def main():
    bp = _load_placeholders()
    root = Path(__file__).resolve().parent.parent
    cards_dir = root / "cards"
    if not cards_dir.is_dir():
        sys.exit(f"cards/ not found at {cards_dir}")

    sections = []
    counts = []
    total = 0
    draw_your_own = 0

    for slug, display, blurb in REALMS:
        fam_dir = cards_dir / slug
        if not fam_dir.is_dir():
            continue
        cards = {}
        for f in fam_dir.glob("*.md"):
            name, sec = bp.parse_card(f)
            if not name:
                continue
            cards[f.stem] = (name,
                             sec.get("Image cue", "").strip(),
                             sec.get("Prompt", "").strip() or "—")
        if "your-own" in cards:
            draw_your_own += 1
        rows = [cards[s] for s in ordered_slugs(slug, list(cards))]
        if not rows:
            continue
        n = len(rows)
        total += n
        counts.append((display, n))
        sections.append(f"## {display} ({n})\n\n{blurb}\n\n{table(rows)}")

    blank_dir = cards_dir / "blank"
    if blank_dir.is_dir():
        draw_your_own += len(list(blank_dir.glob("*.md")))
    total += draw_your_own

    bal = ["| Realm | Cards |", "| ----- | ----- |"]
    for display, n in counts:
        bal.append(f"| {display} | {n} |")
    bal.append(f"| Draw your own | {draw_your_own} |")
    bal.append(f"| **Total** | **{total}** |")
    balance = ("## Deck balance\n\n" + "\n".join(bal) +
               "\n\nRoughly a card deck's spread — familiar to hold, easy to lay "
               "out. \"What helps\" is deliberately the largest: it carries the "
               "niche-construction work and gives the staff game enough conflicting "
               "needs to build around (room to move against less talking; just one "
               "person against a full group).")

    doc = (
        "<!-- Generated by scripts/build-starter-deck.py from the card files. Do not hand-edit. -->\n\n"
        + HEADER.format(total=total)
        + SEP + SEP.join(sections)
        + SEP + DRAW_YOUR_OWN
        + SEP + balance
        + SEP + BACKS
        + SEP + PLAY.format(total=total)
        + SEP + LICENSE
        + "\n"
    )

    out = root / "cavendish-cards-starter-deck.md"
    out.write_text(doc, encoding="utf-8")
    print(f"Wrote {out.name}: {total} cards")
    for display, n in counts:
        print(f"  {display}: {n}")
    print(f"  Draw your own: {draw_your_own}")


if __name__ == "__main__":
    main()
