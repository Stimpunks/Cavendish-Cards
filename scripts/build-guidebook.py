#!/usr/bin/env python3
"""Assemble the Cavendish Cards guidebook from the card files.

Walks cards/<family>/*.md, reads each card's name, image cue, prompt, and
Notes, and writes cavendish-cards-guidebook.md, grouped by family in deck
order (cards alphabetical within each family).

The guidebook is generated. Do not edit it by hand — edit the cards in
cards/ and run this script again.

Usage:
    python3 scripts/build-guidebook.py
"""

from pathlib import Path
import sys

# Family order (deck order) with display name and one-line intro.
FAMILIES = [
    ("places", "Places",
     "The five Cavendish zones. Everything else sits in one of these."),
    ("weather", "Weather",
     "Inner weather, not clinical states — the whole range, good and hard alike."),
    ("what-helps", "What helps",
     "The niche-construction pieces: the ways we change the environment so it fits."),
    ("lily-pad", "Lily pads",
     "The in-between. Stepping stones for the crossings — every card is a place "
     "to land and push off from, never a failure."),
    ("grower", "Growers",
     "Who am I today. A non-deficit way to hold that different people bloom in "
     "different conditions."),
    ("love-locution", "Love Locutions",
     "Affirmations. Given between people, never earned — a gift, never a reward."),
    ("interaction", "Interaction",
     "How open I am to talking, right now. The Autistic community's color "
     "communication badges."),
    ("blank", "Blank",
     "The card the deck doesn't have yet. Find the gap, draw it, send it in."),
]

REALM_NOTES = {
    "places":
        "**Moving between the zones.** Cave, campfire, and watering hole are also a "
        "sociality gradient — the cave inward and solo, the campfire a small safe "
        "group, the watering hole open and social. They line up with the interaction "
        "moods: the cave with red (not right now), the campfire with yellow (people I "
        "know), the watering hole with green (come say hi). Moving between them on "
        "your own terms — alone, then together, then alone again — is *intermittent "
        "collaboration*: everyone needs all three, but not at once, and not in the "
        "same measure. Lay places, interaction moods, and lily pads in a row to map "
        "that rhythm.",
    "lily-pad":
        "**Lily padding.** A lily pad is a springboard and a landing place both — "
        "somewhere to rest, and somewhere to push off from. For a mind in deep focus, "
        "a hard crossing between one thing and the next is jarring and costly: "
        "attention gets yanked across with nowhere to land. Lily pads are the stepping "
        "stones that make the crossing gentle — a pause, a heads-up, a held place, a "
        "graded step — designed *with* the person and never sprung *at* them. Each card "
        "names not a failure to move but a way to land and launch again: *i need a "
        "minute*, *slowly*, *coming back*, *stuck*. The work is never to hurry the "
        "crossing; it's to pad it. Rendered in the web app as an always-available "
        "*Moments* strip, because a moment can land on the table at any point in play. "
        "Lineage: lily padding, from Cavendish Space; the transitional-trauma framing "
        "from Tanya Adkin — https://stimpunks.org/glossary/lily-pad/.",
    "what-helps":
        "**Building the niche.** These cards name what would help — the *need*, not "
        "the thing that meets it. The materials are up to you and your budget: a den "
        "can be a pop-up tent or a blanket over a table; less to look at can be a "
        "screen, a corner, or a turned-around desk. For practical, low-cost ways to "
        "build these, see [Creating Cavendish Space on a Budget]"
        "(https://stimpunks.org/2024/03/14/creating-cavendish-space-on-a-budget/) and "
        "[Nesting](https://stimpunks.org/glossary/nesting/). The card names the need; "
        "niche construction fills it, with whatever you have.",
    "love-locution":
        "**Penguin pebbling.** Giving someone a Love Locution is *penguin "
        "pebbling* — penguins bring each other pebbles, and these cards are "
        "pebbles you can hand to a person. On paper, the cards are made to be "
        "given this way. In the web app they work the other way round, too: "
        "truths a person claims and turns up for themselves.",
}

# Child-safety framing, kept word-for-word in sync with the web guidebook
# (SCREENING / NOT_AAC in build-site.py). The deck sits alongside AAC, never
# in place of it, and is never an assessment tool.
SCREENING = (
    "These cards help a person say what they need, on their own terms. They are "
    "not a way to assess, score, sort, or diagnose anyone. A card names a need, "
    "never a symptom or a target. Used to rank or flag people, the deck becomes "
    "the opposite of what it is for. Broken systems, not broken people."
)

NOT_AAC = (
    "The deck is a lens, not a language. It makes one hard-to-voice thing — "
    "sensory, regulatory, and emotional weather, and the conditions that help — "
    "sayable, and it stops there. It is not a communication system and does not "
    "try to be comprehensive the way AAC must be. Most of all, it sits alongside "
    "a child's real communication tools, never in place of them: if a child needs "
    "a way to communicate, they need AAC, and \"they have the cards\" is never a "
    "reason to under-provide it."
)


def parse_card(path):
    """Return (name, {section_heading: text}) for a card file, excluding License."""
    name = None
    sections = {}
    current = None
    buf = []

    def flush():
        if current is not None:
            sections[current] = "\n".join(buf).strip()

    for line in path.read_text(encoding="utf-8").splitlines():
        if name is None and line.startswith("# ") and not line.startswith("## "):
            name = line[2:].strip()
            continue
        if line.strip() == "----":       # separator before License — stop here
            flush()
            current = None
            buf = []
            break
        if line.startswith("## "):
            flush()
            current = line[3:].strip()
            buf = []
            continue
        if current is not None:
            buf.append(line)
    flush()
    return name, sections


def render_card(name, cue, prompt, notes):
    meta = f"*{cue}*" if cue else ""
    if prompt and prompt != "—":
        meta += f' · "{prompt}"' if meta else f'"{prompt}"'
    elif prompt == "—":
        meta += " · given, not read" if meta else "given, not read"
    parts = [f"### {name}"]
    if meta:
        parts.append(meta)
    parts.append("")
    parts.append(notes if notes else "_No guidebook entry yet._")
    return "\n".join(parts)


def main():
    root = Path(__file__).resolve().parent.parent
    cards_dir = root / "cards"
    out_path = root / "cavendish-cards-guidebook.md"
    if not cards_dir.is_dir():
        sys.exit(f"cards/ not found at {cards_dir}")

    doc = [
        "# Cavendish Cards — Guidebook",
        "",
        "A companion to the deck: what each card means, how to hold it, and where "
        "its metaphor comes from. Like an oracle deck's guidebook — but it "
        "describes the card, never the child.",
        "",
        "_Generated from the card files in `cards/` by "
        "`scripts/build-guidebook.py`. Do not edit this file by hand — edit the "
        "cards and regenerate._",
        "",
        f"**Not a screening tool.** {SCREENING}",
        "",
        f"**Not an AAC board.** {NOT_AAC}",
        "",
    ]

    total = 0
    summary = []
    for slug, display, intro in FAMILIES:
        files = sorted((cards_dir / slug).glob("*.md"))
        if not files:
            continue
        doc += ["----", "", f"## {display}", "", f"_{intro}_", ""]
        if slug in REALM_NOTES:
            doc += [REALM_NOTES[slug], ""]
        count = 0
        for f in files:
            name, sections = parse_card(f)
            if not name:
                print(f"  ! skipped {f} (no card name)", file=sys.stderr)
                continue
            doc.append(render_card(
                name,
                sections.get("Image cue", "").strip(),
                sections.get("Prompt", "").strip(),
                sections.get("Notes", "").strip(),
            ))
            doc.append("")
            count += 1
            total += 1
        summary.append((display, count))

    doc += [
        "----",
        "",
        "Dedicated to the public domain under "
        "[CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). "
        "Home: https://stimpunks.org/projects/cavendish-space-project/",
        "",
    ]

    out_path.write_text("\n".join(doc), encoding="utf-8")
    print(f"Wrote {out_path.name} — {total} cards across {len(summary)} families")
    for display, count in summary:
        print(f"  {display}: {count}")


if __name__ == "__main__":
    main()
