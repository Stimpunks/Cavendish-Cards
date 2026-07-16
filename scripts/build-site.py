#!/usr/bin/env python3
"""Build the static web deck into web/ from the card files.

Writes:
  web/cards.json        card data for the player (index.html / app.js)
  web/faces/            card faces (finished art if present, else placeholder)
                        plus the two card backs
  web/guidebook.html    a readable, in-site guidebook generated from the cards

Reuses scripts/build-placeholders.py, so placeholder faces match the deck.
No third-party dependencies.

Usage, from the repo root:
    python3 scripts/build-site.py
"""

from pathlib import Path
import html
import importlib.util
import json
import shutil
import sys


def _load_placeholders():
    path = Path(__file__).resolve().parent / "build-placeholders.py"
    if not path.exists():
        sys.exit(f"Could not find {path}")
    spec = importlib.util.spec_from_file_location("build_placeholders", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Family display order on the web (interaction first, per playtest feedback),
# with display name and a short player-facing intro.
FAMILIES = [
    ("interaction", "Interaction",
     "How open you are to talking right now — from “come say hi” to "
     "“not right now.” Made to be shown or worn."),
    ("places", "Places",
     "The kind of space that fits right now — a quiet cave, a small campfire, "
     "an easy watering hole, a library, or the whole habitat around them."),
    ("weather", "Weather",
     "How it feels inside right now — your inner weather, from bright to stormy. "
     "Not good or bad, just what's true this moment."),
    ("what-helps", "What helps",
     "Small changes to the space that make things easier — quiet, softer light, "
     "room to move, a way out."),
    ("lily-pad", "Lily pads",
     "Moments you can drop onto the table anytime — a pause, a not-yet, a "
     "ready-now. Each is a place to land, not a failure."),
    ("grower", "Growers",
     "How you're growing today, and what you need to do well. Some people are "
     "dandelions and grow almost anywhere; some are tulips and do well with the "
     "right basics; some are orchids and thrive with specific care. None is "
     "better — they just need different things."),
    ("love-locution", "Kind words",
     "Things that are true about you — you belong, you can rest, you're not "
     "broken. Turning one up claims it out loud: I need this said, and heard."),
    ("blank", "Blank",
     "The card that isn't here yet. Draw or write your own."),
]

# Families rendered as an always-available "moments" strip rather than a
# browsable filter (item 8/17 from playtesting).
MOMENTS = {"lily-pad"}

# App-only subtitles surfaced under a realm's name (community / alternate terms).
SUBTITLES = {
    "love-locution": "Also called Love Locutions or Love Languages.",
}

# Headings kept in the guidebook even when the app shows a plainer label.
GB_NAMES = {
    "love-locution": "Love Locutions",
}

# Curated display order within a realm (web deck). Cards not listed fall in
# alphabetically after the listed ones; a realm's "your own" card is always last.
# No headings, no good/bad split — just a gentle range.
ORDER = {
    "weather": [
        "warm", "bright", "fizzy", "happy-flappy", "in-the-zone",
        "buzzy", "prickly", "full", "pulled-every-way", "meerkat",
        "round-and-round", "stormy", "heavy", "foggy", "far-away",
    ],
}


def order_files(slug, fam_dir):
    order = ORDER.get(slug)
    files = list(fam_dir.glob("*.md"))
    if not order:
        return sorted(files)
    idx = {s: i for i, s in enumerate(order)}
    def key(p):
        s = p.stem
        if s == "your-own":
            return (2, 0, s)
        if s in idx:
            return (0, idx[s], "")
        return (1, 0, s)
    return sorted(files, key=key)

# Sense-signpost grouping for the What helps family (display only).
GROUPS = {
    "what-helps": [
        ("Being in charge", ["let-me-control-it"]),
        ("Sound", ["headphones", "a-steady-sound"]),
        ("Light & looking", ["dim-the-light", "less-to-look-at"]),
        ("Touch", ["something-soft"]),
        ("Pressure", ["a-big-squeeze"]),
        ("Temperature", ["the-right-temperature"]),
        ("Movement", ["room-to-move", "busy-hands", "sit-my-way", "let-me-stim"]),
        ("Mouth & nose", ["something-to-chew", "a-snack-or-a-drink", "a-smell-that-helps"]),
        ("Space & enclosure", ["a-corner", "a-den", "my-own-spot", "a-way-out"]),
        ("Telling & talking", ["less-talking", "tell-me-first", "another-way-to-talk"]),
        ("People & time", ["just-one-person", "parallel-existence", "no-rush", "let-me-finish"]),
        ("Make your own", ["your-own"]),
    ],
}

# Reflection question pools (hybrid). A card uses its own ## Reflection section
# if present; otherwise the authoring pool (blank / your-own cards) or its
# family pool. Card- and environment-facing, invitational, never diagnostic.
REFLECTIONS = {
    "weather": [
        "Where do you feel this in your body right now?",
        "A little, or a lot?",
        "Is this the same as earlier, or has it changed?",
        "Is there a what-helps card you'd reach for?",
    ],
    "places": [
        "What's one thing that would make this place feel right?",
        "Is there one thing nearby you'd change?",
        "Who would you want here with you — anyone, or no one?",
        "Is there a what-helps card that goes with this place?",
    ],
    "what-helps": [
        "Could you have this right now, or is something in the way?",
        "Who could help make it happen?",
        "Would you want someone to know you need this?",
        "Is there another what-helps card you'd add?",
    ],
    "lily-pad": [
        "What would help you feel ready — or is staying right for now?",
        "Are you just settling here, or ready to move on?",
        "Would a little more time help?",
        "Is there a what-helps card that would make this easier?",
    ],
    "grower": [
        "What helps you bloom on a day like today?",
        "What are your good conditions right now?",
        "Is today this kind of day, or a different one?",
        "Is there a what-helps card that fits your conditions?",
    ],
    "love-locution": [
        "Is this one you needed to hear today?",
        "What would help you believe it?",
        "Who could help you hold onto it?",
        "Would you want someone to know this is true for you?",
    ],
    "interaction": [
        "Who around you should see this card?",
        "Is this true just for now, or for a while?",
        "Would you wear it, or show it once?",
        "Is there a different signal you'd rather give?",
    ],
}

AUTHORING = [
    "What's missing that you'd want a card for?",
    "What would the picture be?",
    "What would it help someone understand?",
]

INTRO = (
    "Cavendish Cards come from the Cavendish Space model — a way of shaping the "
    "space around real needs instead of asking people to mask them. The deck "
    "gives a person pictures and words for how they feel and what helps, so they "
    "can show someone rather than explain in words they may not have. This "
    "guidebook says what each card means and how to hold it. It describes the "
    "card, never the child."
)

SCREENING = (
    "These cards help a person say what they need, on their own terms. They are "
    "not a way to assess, score, sort, or diagnose anyone. A card names a need, "
    "never a symptom or a target. Used to rank or flag people, the deck becomes "
    "the opposite of what it is for. Broken systems, not broken people."
)

GUIDEBOOK_NOTES = {
    "love-locution":
        "<p><strong>Penguin pebbling.</strong> Giving someone a Love Locution is "
        "<em>penguin pebbling</em> — penguins bring each other pebbles, and these "
        "cards are pebbles you can hand to a person. On paper, the cards are made "
        "to be given this way. In the web app they work the other way round, too: "
        "truths a person claims and turns up for themselves.</p>",
}


def e(s):
    return html.escape(s, quote=False)


def guidebook_html(out_families):
    sections = []
    for fam in out_families:
        entries = []
        for c in fam["cards"]:
            if c["prompt"]:
                meta = f'<em>{e(c["cue"])}</em> &middot; &ldquo;{e(c["prompt"])}&rdquo;'
            elif c["given_not_read"]:
                meta = f'<em>{e(c["cue"])}</em> &middot; given, not read'
            else:
                meta = f'<em>{e(c["cue"])}</em>'
            note = f'<p>{e(c["notes"])}</p>' if c["notes"] else ''
            entries.append(
                f'<article class="gb-entry"><h3>{e(c["name"])}</h3>'
                f'<p class="gb-meta">{meta}</p>{note}</article>'
            )
        realm_note = GUIDEBOOK_NOTES.get(fam["slug"], "")
        gb_name = GB_NAMES.get(fam["slug"], fam["name"])
        sections.append(
            f'<section class="gb-family"><h2>{e(gb_name)}</h2>'
            f'<p class="muted">{e(fam["intro"])}</p>{realm_note}{"".join(entries)}</section>'
        )
    body = "\n".join(sections)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Cavendish Cards — Guidebook</title>
  <meta name="description" content="What each Cavendish card means and how to hold it. It describes the card, never the child.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css">
</head>
<body>
  <a class="skip" href="#gb">Skip to the guidebook</a>
  <header class="site-header">
    <div class="wrap">
      <p class="backlink"><a href="index.html">&larr; Back to the deck</a></p>
      <h1>Guidebook</h1>
      <p class="intro">{e(INTRO)}</p>
      <div class="rules" role="note" aria-label="Not a screening tool">
        <p><strong>Not a screening tool.</strong> {e(SCREENING)}</p>
      </div>
    </div>
  </header>
  <main id="gb" class="wrap gb">
{body}
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <p>Free to use, print, and adapt under <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>. Part of the <a href="https://stimpunks.org/projects/cavendish-space-project/">Cavendish Space Project</a>. <a href="https://github.com/Stimpunks/Cavendish-Cards">Source on GitHub</a>. <a href="https://github.com/Stimpunks/Cavendish-Cards/blob/main/CALL-FOR-ART.md">Contribute art</a>.</p>
    </div>
  </footer>
</body>
</html>
'''


def main():
    bp = _load_placeholders()
    root = Path(__file__).resolve().parent.parent
    cards_dir = root / "cards"
    web = root / "web"
    faces = web / "faces"
    if not cards_dir.is_dir():
        sys.exit(f"cards/ not found at {cards_dir}")
    faces.mkdir(parents=True, exist_ok=True)

    for back in ("back-standard.svg", "back-love-locution.svg"):
        src = root / "assets" / "templates" / back
        if src.exists():
            shutil.copyfile(src, faces / back)
        else:
            print(f"  ! missing back {src}", file=sys.stderr)

    out_families = []
    total = 0
    for slug, display, intro in FAMILIES:
        fam_dir = cards_dir / slug
        if not fam_dir.is_dir():
            continue
        cards = []
        group_map = {}
        group_order = []
        used_more = False
        for glabel, gslugs in GROUPS.get(slug, []):
            group_order.append(glabel)
            for gs in gslugs:
                group_map[gs] = glabel
        for f in order_files(slug, fam_dir):
            name, sec = bp.parse_card(f)
            if not name:
                continue
            cue = sec.get("Image cue", "").strip()
            prompt = sec.get("Prompt", "").strip()
            notes = sec.get("Notes", "").strip()
            cslug = f.stem

            finished = root / "assets" / "cards" / slug / f"{cslug}.svg"
            if finished.exists():
                face_svg = finished.read_text(encoding="utf-8")
            elif slug in bp.FAM:
                face_svg = bp.build_svg(slug, name, cue, prompt)
            else:
                print(f"  ! no face for {slug}/{cslug}", file=sys.stderr)
                continue
            (faces / f"{cslug}.svg").write_text(face_svg, encoding="utf-8")

            grp = group_map.get(cslug)
            if group_order and grp is None:
                grp = "More"
                used_more = True
            refl_override = sec.get("Reflection", "").strip()
            if refl_override:
                reflections = [ln.lstrip("-* ").strip()
                               for ln in refl_override.splitlines() if ln.strip()]
            elif slug == "blank" or cslug == "your-own":
                reflections = list(AUTHORING)
            else:
                reflections = list(REFLECTIONS.get(slug, []))
            has_prompt = bool(prompt) and prompt != "—"
            back = ("back-love-locution.svg" if slug == "love-locution"
                    else "back-standard.svg")
            cards.append({
                "slug": cslug,
                "name": name,
                "cue": cue,
                "prompt": prompt if has_prompt else "",
                "given_not_read": slug == "love-locution",
                "notes": notes,
                "face": f"faces/{cslug}.svg",
                "back": f"faces/{back}",
                "group": grp,
                "reflections": reflections,
            })
            total += 1
        if cards:
            order = group_order + (["More"] if used_more else [])
            fam_obj = {"slug": slug, "name": display, "intro": intro,
                       "mode": "moments" if slug in MOMENTS else "browse",
                       "cards": cards}
            if slug in SUBTITLES:
                fam_obj["subtitle"] = SUBTITLES[slug]
            if order:
                fam_obj["groupOrder"] = order
            out_families.append(fam_obj)

    (web / "cards.json").write_text(
        json.dumps({"families": out_families}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    (web / "guidebook.html").write_text(guidebook_html(out_families), encoding="utf-8")

    print(f"Wrote web/cards.json, web/guidebook.html, and {total} faces into web/faces/")
    for fam in out_families:
        print(f"  {fam['name']}: {len(fam['cards'])}")


if __name__ == "__main__":
    main()
