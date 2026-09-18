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
import hashlib
import html
import importlib.util
import json
import re
import shutil
import sys


# Realms that also get an art-only SVG beside each card face, for somewhere
# that wants the picture without the card. Only Places so far: the five room
# signs in rooms.js. Kept to what is used -- generating 94 of these to serve
# five would just be more to cache and more to precache.
ART_ONLY = {"places"}


def _load_placeholders():
    path = Path(__file__).resolve().parent / "build-placeholders.py"
    if not path.exists():
        sys.exit(f"Could not find {path}")
    spec = importlib.util.spec_from_file_location("build_placeholders", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_guidebook():
    # Reuse the Pattern crosswalk registry + renderers so the web guidebook and
    # the Markdown guidebook can't drift. Single source of truth in build-guidebook.py.
    path = Path(__file__).resolve().parent / "build-guidebook.py"
    if not path.exists():
        sys.exit(f"Could not find {path}")
    spec = importlib.util.spec_from_file_location("build_guidebook", path)
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
     "Stepping stones for the crossings between one thing and the next — drop "
     "one onto the table anytime. A pause, a not-yet, a ready-now. Each is a "
     "place to land and push off from, never a failure."),
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
# browsable filter. Retired: lily pads are now a normal browsable realm, like
# every other family. Left as an empty hook — add a slug here (and restore the
# strip markup + renderer) to bring the mechanic back.
MOMENTS = set()

# App-only subtitles surfaced under a realm's name (community / alternate terms).
SUBTITLES = {
    "love-locution": "Also called Love Locutions or Love Languages.",
    "lily-pad": "Also called Moments.",
}

# Headings kept in the guidebook even when the app shows a plainer label.
GB_NAMES = {
    "love-locution": "Love Locutions",
}

# Realm -> implementation guide. Only realms with a genuine environment-build
# layer get a "how to build this" link; it deep-links to that realm's section in
# the on-site Implementation Guidebook. Weather, Growers, Love Locutions, Blank
# have nothing to build — no link. Anchors are emitted by implementation_html().
BUILD_LINKS = {
    "places":     {"href": "implementation.html#build-places",    "label": "Building the space"},
    "what-helps": {"href": "implementation.html#build-what-helps", "label": "Building the niche"},
    "lily-pad":   {"href": "implementation.html#build-lily-pad",   "label": "Building the crossings"},
}

# Curated display order within a realm (web deck). Cards not listed fall in
# alphabetically after the listed ones; a realm's "your own" card is always last.
# No headings, no good/bad split — just a gentle range.
ORDER = {
    "weather": [
        "warm", "bright", "fizzy", "happy-flappy", "in-the-zone", "need-more",
        "buzzy", "prickly", "full", "pulled-every-way", "meerkat", "too-seen",
        "big-step", "round-and-round", "stormy", "tender", "running-on-empty", "heavy", "foggy", "cant-tell", "far-away",
        "no-words-right-now",
    ],
    "lily-pad": [
        "i-need-a-minute", "not-yet", "slowly", "watch-first", "coming-back",
        "ready-now", "i-want-to-stay-a-while", "all-done", "stuck",
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

# Signpost grouping for the What helps family (display only). Mostly sensory
# channels, plus two that are not a sense at all -- Choosing and Same & new.
# A signpost is a CHANNEL WITH TWO DIRECTIONS, not a single need: Sound holds
# both turning it down and adding a steady hum, and Same & new holds both
# keeping it and changing it. Name a signpost for the channel, never for the
# design principle behind it -- "Predictability" would drag `tell me first`
# out of Telling & talking, where it belongs, because it is about warning.
GROUPS = {
    "what-helps": [
        ("Being in charge", ["let-me-control-it"]),
        ("Choosing", ["fewer-choices"]),
        ("Sound", ["headphones", "a-steady-sound"]),
        ("Light & looking", ["dim-the-light", "less-to-look-at"]),
        ("Touch", ["something-soft"]),
        ("Pressure", ["a-big-squeeze"]),
        ("Temperature", ["the-right-temperature"]),
        ("Movement", ["room-to-move", "busy-hands", "sit-my-way", "let-me-stim"]),
        ("Mouth & nose", ["something-to-chew", "a-snack-or-a-drink", "a-smell-that-helps"]),
        ("Space & enclosure", ["a-corner", "a-den", "my-own-spot", "a-way-out"]),
        ("Telling & talking", ["less-talking", "say-it-straight", "tell-me-first", "another-way-to-talk"]),
        ("People & time", ["just-one-person", "parallel-existence", "no-spotlight", "let-me-unmask", "no-rush", "one-thing-at-a-time", "let-me-finish", "let-me-come-and-go"]),
        ("Same & new", ["keep-it-the-same", "something-different"]),
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
    "card, never the person."
)

SCREENING = (
    "These cards help a person say what they need, on their own terms. They are "
    "not a way to assess, score, sort, or diagnose anyone. A card names a need, "
    "never a symptom or a target. Used to rank or flag people, the deck becomes "
    "the opposite of what it is for. Broken systems, not broken people."
)

# The four refused frameworks, kept word-for-word in sync with README and with
# build-guidebook.py (FRAMEWORKS_LEAD / FRAMEWORKS there).
FRAMEWORKS_LEAD = (
    "It carries none of the frameworks that turn human difference into a problem "
    "to be managed:"
)

FRAMEWORKS = [
    ("No pathology paradigm",
     "A card names a need, not a symptom. \"Buzzy\" describes an environment "
     "that is too much — not a disorder inside the person."),
    ("No deficit ideology",
     "The deck records what helps, never what a person lacks. If it isn't working, "
     "the environment is what hasn't fit yet."),
    ("No behaviorism",
     "No card is a target, a reward, or a compliance check. Turning a card up is "
     "communication, not performance — never something to shape a person toward "
     "\"better\" behavior."),
    ("No emotional sorting",
     "A card names where a person can be and what helps. It never places them on "
     "a scale of how regulated they are, and there is no state anyone is supposed "
     "to get back to. The five places describe a room, not the person standing "
     "in it."),
]

NOT_AAC = (
    "The deck is a lens, not a language. It makes one hard-to-voice thing — "
    "sensory, regulatory, and emotional weather, and the conditions that help — "
    "sayable, and it stops there. It is not a communication system and does not "
    "try to be comprehensive the way AAC must be. Most of all, it sits alongside "
    "a person's real communication tools, never in place of them: if a person needs "
    "a way to communicate, they need AAC, and \"they have the cards\" is never a "
    "reason to under-provide it."
)

GUIDEBOOK_NOTES = {
    "places":
        "<p><strong>Moving between the zones.</strong> Cave, campfire, and watering "
        "hole are also a sociality gradient — the cave inward and solo, the campfire "
        "a small safe group, the watering hole open and social. They line up with "
        "the interaction moods: the cave with red (not right now), the campfire with "
        "yellow (people I know), the watering hole with green (come say hi). Moving "
        "between them on your own terms — alone, then together, then alone again — is "
        "<em>intermittent collaboration</em>: everyone needs all three, but not at "
        "once, and not in the same measure. Lay places, interaction moods, and lily "
        "pads in a row to map that rhythm.</p>",
    "what-helps":
        "<p><strong>Building the niche.</strong> These cards name what would help — "
        "the <em>need</em>, not the thing that meets it. The materials are up to you "
        "and your budget: a den can be a pop-up tent or a blanket over a table; less "
        "to look at can be a screen, a corner, or a turned-around desk. For practical, "
        "low-cost ways to build these, see "
        "<a href=\"https://stimpunks.org/2024/03/14/creating-cavendish-space-on-a-budget/\">Creating Cavendish Space on a Budget</a> "
        "and <a href=\"https://stimpunks.org/glossary/nesting/\">Nesting</a>. The card "
        "names the need; niche construction fills it, with whatever you have.</p>",
    "love-locution":
        "<p><strong>Penguin pebbling.</strong> Giving someone a Love Locution is "
        "<em>penguin pebbling</em> — penguins bring each other pebbles, and these "
        "cards are pebbles you can hand to a person. On paper, the cards are made "
        "to be given this way. In the web app they work the other way round, too: "
        "truths a person claims and turns up for themselves.</p>",
}


def e(s):
    return html.escape(s, quote=False)


# ---------------------------------------------------------------------------
# SPACE-TIME (Helen Edgar, Autistic Realms) -- the one source for the page's
# infographic, its table, and the Cavendish mapping beside it.
#
# All three renderings come from this list on purpose. The article publishes an
# infographic and a table that say the same thing in two shapes, and keeping
# two copies here would let them drift the first time a line was reworded. The
# figure prints `letter`/`name`/`tile`; the table prints `space`/`dims`/`flow`;
# the "what it asks of a room" section prints `asks`/`zones`/`cards`/`conds`.
#
# Provenance, per field:
#   space, dims  -- the NAMES of elements in other people's frameworks
#                   (Doherty et al. 2023; McGreevy et al. 2024 after Todres et
#                   al. 2009). Cited, never absorbed.
#   flow         -- Helen's own column, carried with her agreement under the
#                   dual-licensing this page documents. Reproduced as written
#                   except for house US spelling (honouring -> honoring,
#                   centres -> centers); reword nothing else without asking.
#   tile, asks,
#   zones, cards,
#   conds        -- this project's, and the only part that knows the deck
#                   exists. `conds` are COND ids in web/rooms.js, checked at
#                   build time by _check_space_time_conds().
SPACE_TIME = [
    {
        "letter": "S", "name": "Sensory attunement", "part": "SPACE",
        "tile": "The channels a bodymind takes the world in through — turned "
                "down or turned up, by the person they belong to.",
        "space": "Sensory",
        "dims": "Embodiment, Insiderness",
        "flow": "Monotropic focus impacts our sensory experiences; attunement "
                "validates embodied inner worlds and helps regulation and wellbeing.",
        "asks": "Options in both directions, reachable without asking. A "
                "channel runs two ways: one person needs the sound down and "
                "the next needs some added, so a room that only ever subtracts "
                "has answered half of this.",
        "zones": ["the cave"],
        "cards": [("What helps", ["headphones", "a steady sound", "dim the light",
                                  "less to look at", "the right temperature",
                                  "a smell that helps", "something to chew",
                                  "a big squeeze"])],
        "conds": ["quiet", "steady-sound", "dim", "less-to-look-at",
                  "temperature", "soft"],
    },
    {
        "letter": "P", "name": "Predictability and place", "part": "SPACE",
        "tile": "Knowing what happens next, and having somewhere to be while "
                "it does.",
        "space": "Predictability",
        "dims": "Sense of place, Personal journey",
        "flow": "Predictability and flexible time reduces attentional "
                "fragmentation, allowing grounding, deep focus and continuity "
                "and flow in safe environments.",
        "asks": "Warning before a change, a pace that isn't one pace, and a "
                "spot that stays yours between visits. For monotropic "
                "attention this is not a comfort — it is the difference "
                "between flow and fragmentation.",
        "zones": ["the habitat"],
        "cards": [("What helps", ["tell me first", "keep it the same", "no rush",
                                  "let me finish", "my own spot",
                                  "one thing at a time"]),
                  ("Lily pads", ["not yet", "slowly", "coming back"])],
        "conds": ["written", "no-rush", "own-spot"],
    },
    {
        "letter": "A", "name": "Acceptance and agency", "part": "SPACE",
        "tile": "Following your own attention without being redirected. "
                "Holding the dial yourself.",
        "space": "Acceptance",
        "dims": "Agency, Uniqueness",
        "flow": "Embracing monotropism enables agency; people can follow "
                "interests without constant redirection which causes dysregulation.",
        "asks": "Permission that does not have to be asked for each time. This "
                "is the element the deck's own mechanics answer before any "
                "card does: cards lie face-down, and turning one up is the "
                "consent. Nobody reads a spread that was not offered.",
        "zones": [],
        "cards": [("What helps", ["let me control it", "let me stim",
                                  "let me unmask", "sit my way",
                                  "let me come and go", "fewer choices"])],
        "conds": ["control", "sit-my-way", "come-and-go", "way-out"],
    },
    {
        "letter": "C", "name": "Communication and connection", "part": "SPACE",
        "tile": "Every way of saying it counts. Speaking is one of them, not "
                "the price of entry.",
        "space": "Communication",
        "dims": "Togetherness, Sense-making",
        "flow": "Monotropic attention shapes communication through detail, "
                "flow, and passion, creating authentic connections and "
                "different ways of communicating.",
        "asks": "A way to take part that isn't talking, and a way to say how "
                "open you are without a conversation about it. This is the "
                "layer most rooms have done least about, because silence gets "
                "read as nothing happening.",
        "zones": ["the campfire", "the watering hole"],
        "cards": [("Interaction", ["come say hi", "ask first", "people i know",
                                   "not right now"]),
                  ("What helps", ["another way to talk", "less talking",
                                  "say it straight", "no spotlight"])],
        "conds": ["another-way", "written", "small-group"],
    },
    {
        "letter": "E", "name": "Empathy", "part": "SPACE",
        "tile": "Meeting the bodymind that is actually here — the stimming and "
                "the interests included.",
        "space": "Empathy",
        "dims": "Embodiment, Insiderness",
        "flow": "Monotropic flow is expressed through our bodies and minds by "
                "stimming and engagement in interests; empathy requires "
                "honoring and helps build trust.",
        "asks": "Nothing to install. This one is a practice, and it is what "
                "somebody does with a spread once it is in front of them: "
                "mirror it back, reach for the environment rather than the "
                "person, and leave the sharing where it started.",
        "zones": [],
        "cards": [("Weather", ["can't tell", "foggy", "tender", "too seen"]),
                  ("Kind words", ["i see you", "nothing to fix",
                                  "your way is a real way"])],
        "conds": [],
    },
    {
        "letter": "T", "name": "Togetherness", "part": "TIME",
        "tile": "Shared attention. Being alongside people, at the depth you "
                "choose and no deeper.",
        "space": "(implicit in SPACE)",
        "dims": "Togetherness, Sense of place, Sense-making",
        "flow": "Shared monotropic focus and joint flow (e.g., special "
                "interests) builds deep relational bonds and helps foster "
                "relationships and community.",
        "asks": "Company that costs nothing to join and nothing to leave. Two "
                "different rooms, not one: a few people sharing something, and "
                "somewhere you can be near people without joining in.",
        "zones": ["the campfire", "the watering hole"],
        "cards": [("What helps", ["parallel existence", "just one person",
                                  "room to move", "a way out"])],
        "conds": ["small-group", "room-to-move", "way-out", "come-and-go"],
    },
    {
        "letter": "I", "name": "Insiderness and personal journey", "part": "TIME",
        "tile": "The inside view is the account of record, and it keeps going "
                "across the day.",
        "space": "(implicit in SPACE)",
        "dims": "Insiderness, Embodiment, Uniqueness, Personal journey",
        "flow": "Monotropism centers our unique internal perspectives; "
                "validating our inner experiences and stories validates "
                "Autistic knowledge and ways of being.",
        "asks": "Somebody's own account, held as the account — not checked "
                "against an observation of them. Every rule against counting "
                "in this project protects this element: no score, no tally, "
                "nothing kept.",
        "zones": [],
        "cards": [("Growers", ["dandelion", "tulip", "orchid"]),
                  ("Kind words", ["you belong here", "you're not broken",
                                  "it's okay to need what you need"])],
        "conds": ["own-spot"],
    },
    {
        "letter": "M", "name": "Meaning-making and sense of place", "part": "TIME",
        "tile": "Coherence, and somewhere that is yours to be in.",
        "space": "(implicit in SPACE)",
        "dims": "Sense-making, Sense of place, Personal journey",
        "flow": "Monotropic attention drives coherence and narrative, making "
                "meaning and having a shared understanding with others is "
                "central to our wellbeing.",
        "asks": "Somewhere to put what you have made and find it again, and "
                "the room visibly changing after somebody said what they "
                "needed. Nothing makes a place mean less than asking and then "
                "building nothing.",
        "zones": ["the library", "the habitat"],
        "cards": [("Weather", ["in the zone"]),
                  ("Lily pads", ["i want to stay a while"])],
        "conds": ["own-spot", "written"],
    },
    {
        "letter": "E", "name": "Embodiment and uniqueness", "part": "TIME",
        "tile": "Attention is lived through a body. No two of them the same.",
        "space": "(implicit in SPACE)",
        "dims": "Embodiment, Insiderness, Uniqueness",
        "flow": "Flow and attention are lived through our bodyminds — "
                "being monotropic is an embodied way of being which impacts "
                "every aspect of life.",
        "asks": "Room for a body to do what it does, in public, without it "
                "being a problem someone solves. And the your-own card in "
                "every realm, because a deck of ninety-odd fixed pictures is "
                "still a set of somebody else's words.",
        "zones": [],
        "cards": [("What helps", ["let me stim", "busy hands", "room to move",
                                  "sit my way", "something soft"]),
                  ("Weather", ["heavy", "full", "running on empty", "fizzy"])],
        "conds": ["room-to-move", "sit-my-way", "soft"],
    },
]

# The infographic's own closing statement, from the article. Rendered as the
# figure's caption so the picture carries the words it carries there.
SPACE_TIME_STATEMENT = [
    "Monotropism shapes Autistic experiences through deep, embodied attention tunnels.",
    "Being monotropic shapes how Autistic people sense, focus, and connect.",
    "With Sensory attunement, Predictability, Acceptance, Communication, and "
    "Empathy, Autistic people find grounding and flow.",
    "Through Togetherness, Insiderness, Meaning-Making, and Embodiment, we can "
    "thrive, belong, and share our unique ways of being.",
    "SPACE–TIME helps us reimagine care and create environments where "
    "Autistic people can thrive.",
]



# ---------------------------------------------------------------------------
# Site navigation, a tiny Markdown renderer, and a shared page shell.
# Used by the standalone pages (Guidebook, Implementation, Why, Origin) and
# mirrored by the hand-authored index.html. No JS: a native <details> menu.
# ---------------------------------------------------------------------------

# Order of the collapsed site menu: (label, href, key, group).
#
# The group is the heading the entry sits under, and group ORDER is the order
# the groups first appear here -- so there is no second list to keep in step
# with this one. `None` means ungrouped, rendered above the first heading.
#
# This is also the ONE taxonomy: llms.txt builds its sections from these same
# groups (see _LLMS_DESCRIPTIONS), so the menu a person reads and the index a
# model reads cannot drift into two different shapes of the same site.
SITE_NAV = [
    ("Cavendish Space", "index.html", "home", None),

    ("The deck", "deck.html", "deck", "Use it"),
    ("Zone a room", "rooms.html", "rooms", "Use it"),
    ("Interaction badges", "badges.html", "badges", "Use it"),
    ("Print the deck", "print.html", "print", "Use it"),

    ("Guidebook", "guidebook.html", "guidebook", "The deck in use"),
    ("Implementation guidebook", "implementation.html", "implementation", "The deck in use"),
    ("Facilitator sheet", "facilitator.html", "facilitator", "The deck in use"),
    ("Example spreads", "example-spreads.html", "example-spreads", "The deck in use"),
    ("Place Explorers (for children)", "place-explorers.html", "place-explorers", "The deck in use"),
    ("Group access needs", "group-needs.html", "group-needs", "The deck in use"),
    ("Livable worlds checklist", "livable-worlds.html", "livable-worlds", "The deck in use"),

    ("What is a Cavendish Space?", "space.html", "space", "The model"),
    ("Why this exists", "why.html", "why", "The model"),
    ("Not an AAC board", "not-aac.html", "not-aac", "The model"),
    ("Origin & lineage", "origin.html", "origin", "The model"),
    ("ARLES & the cards", "arles.html", "arles", "The model"),
    ("SPACE-TIME", "space-time.html", "space-time", "The model"),
    ("Building inclusive environments", "inclusive-environment.html", "inclusive-environment", "The model"),

    ("Privacy & security", "privacy.html", "privacy", "About this site"),
    ("Changelog", "changelog.html", "changelog", "About this site"),
]


def nav_groups():
    """[(group or None, [(label, href, key), ...])] in SITE_NAV order."""
    out = []
    for label, href, key, group in SITE_NAV:
        if not out or out[-1][0] != group:
            out.append((group, []))
        out[-1][1].append((label, href, key))
    return out


# Pages whose HTML this script renders from a Markdown source, keyed by their
# SITE_NAV key. The source is published at web/<key>.md in the SAME build that
# renders the HTML, so the two representations cannot drift. A value of None
# means the Markdown is generated in-build rather than read from the repo root.
#
# The guidebook used to be excluded here: guidebook.html is generated from
# cards/**, but cavendish-cards-guidebook.md was written only by
# build-guidebook.py, so publishing it would have shipped whatever snapshot
# happened to be committed. That is fixed -- build-site.py now calls
# build-guidebook.build_markdown() itself, so both representations come from
# cards/** in the same build and cannot disagree.
MD_ENDPOINTS = {
    "why": "cavendish-cards-why-sheet.md",
    "not-aac": "cavendish-cards-not-aac.md",
    "origin": "cavendish-cards-origin.md",
    "arles": "cavendish-cards-arles.md",
    "inclusive-environment": "cavendish-cards-inclusive-environment.md",
    "example-spreads": "cavendish-cards-example-spreads.md",
    "group-needs": "cavendish-cards-group-needs.md",
    "livable-worlds": "cavendish-cards-livable-worlds.md",
    "privacy": "cavendish-cards-privacy.md",
    "facilitator": "cavendish-cards-facilitator-sheet.md",
    "changelog": "CHANGELOG.md",
    "guidebook": None,
    "implementation": None,
    "place-explorers": None,
    "space-time": None,
}

# llms.txt v2 wants the file advertised by link relation rather than guessed at
# the root. Emitted in every page head; netlify.toml sends the matching
# `Link: </llms.txt>; rel="describedby"` header for agents that never parse HTML.
_LLMS_LINK = '<link rel="describedby" type="text/markdown" href="/llms.txt">'


def nav_entry(key):
    """(label, href) for a SITE_NAV key."""
    for label, href, k, _group in SITE_NAV:
        if k == key:
            return label, href
    raise KeyError(f"no SITE_NAV entry for {key!r}")


def md_path(key):
    """Published .md path for a nav key, or None if that page has no source."""
    return f"/{key}.md" if key in MD_ENDPOINTS else None


def _md_head_links(key, label):
    """The describedby + alternate link pair for a page head."""
    out = "  " + _LLMS_LINK
    rel = md_path(key)
    if rel:
        out += ('\n  <link rel="alternate" type="text/markdown" '
                f'href="{rel}" title="{e(label)} \u2014 Markdown source">')
    return out



def site_nav(current):
    """A no-JS collapsed menu (native <details>), consistent across pages.

    Grouped, because nineteen flat entries is a wall rather than a list. The
    headings are <p aria-hidden>, with the same words as each <ul>'s aria-label:
    a screen reader hears "list, Use it, 4 items" and does not hear the heading
    twice. aria-label rather than aria-labelledby on purpose -- ids would have
    to be unique per page, and some pages carry this menu twice.

    The panel is a <div> holding several <ul>s rather than one <ul>, so the
    grouping is real structure and not labels faked with list items."""
    parts = []
    for group, entries in nav_groups():
        items = []
        for label, href, key in entries:
            cur = ' aria-current="page"' if key == current else ""
            items.append(f'<li><a href="{href}"{cur}>{e(label)}</a></li>')
        if group:
            parts.append(f'<p class="navgroup" aria-hidden="true">{e(group)}</p>')
            parts.append(f'<ul aria-label="{e(group)}">{"".join(items)}</ul>')
        else:
            parts.append(f'<ul>{"".join(items)}</ul>')
    return ('<details class="disclose sitenav">'
            '<summary>Menu</summary>'
            f'<div class="sitenav-panel">{"".join(parts)}</div>'
            '</details>')


# The five hand-authored pages that carry generated blocks, and the SITE_NAV
# key each one is currently on. Everything outside the markers in those files
# is hand-authored and untouched.
#
# It used to be six copies of the menu kept in step by hand, which is a rule
# that works until the day it doesn't: the check for it compared hrefs, so it
# could tell you the links matched and nothing about whether the groups did.
# Now there is one copy of each block, here, and those are renderings of it.
#
# They are tracked files, so a change leaves them dirty in `git status` after a
# build -- that is the reminder to commit them, the same as the tracked
# generated Markdown. Netlify runs this script on deploy, so even an
# uncommitted one is correct in production; the commit is for the repo's sake.
HAND_AUTHORED_NAV = {
    "index.html": "home",
    "deck.html": "deck",
    "rooms.html": "rooms",
    "badges.html": "badges",
    "space.html": "space",
}


def site_nav_pretty(current, indent):
    """site_nav() broken across lines at `indent`, for the hand-authored files.

    Those are read and reviewed as diffs by people, so the block they carry is
    formatted rather than the single line the generated pages get."""
    label, href = nav_entry("home")
    hcur = ' aria-current="page"' if current == "home" else ""
    out = [f'{indent}<a class="homelink" href="{href}"{hcur}>'
           '<span class="homelink-icon" aria-hidden="true">\u2302</span>'
           '<span>Home</span></a>',
           f'{indent}<details class="disclose sitenav">',
           f'{indent}  <summary>Menu</summary>',
           f'{indent}  <div class="sitenav-panel">']
    for group, entries in nav_groups():
        if group:
            out.append(f'{indent}    <p class="navgroup" aria-hidden="true">'
                       f'{e(group)}</p>')
            out.append(f'{indent}    <ul aria-label="{e(group)}">')
        else:
            out.append(f'{indent}    <ul>')
        for label, href, key in entries:
            cur = ' aria-current="page"' if key == current else ""
            out.append(f'{indent}      <li><a href="{href}"{cur}>{e(label)}</a></li>')
        out.append(f'{indent}    </ul>')
    out += [f'{indent}  </div>', f'{indent}</details>']
    return "\n".join(out)


def deck_cta():
    """The route into the deck, on the right of the bar.

    Two labels, one of which the stylesheet paints: the bar carries four
    controls and cannot fit "Open the deck" on one phone row -- it measured
    13px over. Both spans are aria-hidden and the link carries the full wording
    as its accessible name, so what a screen reader hears does not change with
    the viewport, and the short label is a subset of it (WCAG 2.5.3)."""
    return ('<a class="btn deck-cta" href="deck.html" aria-label="Open the deck">'
            '<span class="deck-cta-full" aria-hidden="true">Open the deck</span>'
            '<span class="deck-cta-brief" aria-hidden="true">The deck</span></a>')


def _deck_cta_pretty(current, indent):
    return indent + deck_cta()


# name -> (renderer(current, indent), required?). A required block missing its
# markers stops the build; an optional one is simply not on that page -- only
# four of the five carry the deck button, since the deck page is the deck.
GENERATED_BLOCKS = {
    "nav": (site_nav_pretty, True),
    "cta": (_deck_cta_pretty, False),
}


def _markers(name):
    return (f'<!-- {name}:start \u2014 generated by scripts/build-site.py; '
            'do not edit by hand -->', f'<!-- {name}:end -->')


def _write_hand_authored_navs(web):
    """Rewrite each marked block in the hand-authored pages from its one source.

    A missing REQUIRED marker is fatal, unlike every other check here. Every
    other one is non-fatal because a wrong word still ships a working site;
    this is different -- a lost marker means the file silently keeps whatever
    it had, which is exactly the stale-copy failure this function exists to
    end. Better a build that stops and says so."""
    written = []
    for name, key in HAND_AUTHORED_NAV.items():
        path = web / name
        text = path.read_text(encoding="utf-8")
        changed = False
        for block, (render, required) in GENERATED_BLOCKS.items():
            start_m, end_m = _markers(block)
            m = re.search(r"([ \t]*)" + re.escape(start_m) + r".*?"
                          + re.escape(end_m), text, re.S)
            if not m:
                if required:
                    sys.exit(f"{name}: no {block}:start/{block}:end block. What "
                             f"is there is hand-written and will go stale -- "
                             f"restore the markers around it.")
                continue
            indent = m.group(1)
            fresh = (f"{indent}{start_m}\n" + render(key, indent)
                     + f"\n{indent}{end_m}")
            if fresh != m.group(0):
                text = text[:m.start()] + fresh + text[m.end():]
                changed = True
        if changed:
            path.write_text(text, encoding="utf-8")
            written.append(name)
    return written


def home_link(current):
    """The Home control in the breakbar.

    A named Home link, not just the site name and not only the menu's first
    item: people arrive wired to look top-left for the word, and the one route
    home being an entry inside a collapsed menu means it is not there until you
    open something. The glyph matches the theme toggle's ☀/☾ pattern (plain
    text, no emoji, so it takes the current colour) and is aria-hidden, because
    the word beside it is the accessible name."""
    _label, href = nav_entry("home")
    cur = ' aria-current="page"' if current == "home" else ""
    return (f'<a class="homelink" href="{href}"{cur}>'
            '<span class="homelink-icon" aria-hidden="true">\u2302</span>'
            '<span>Home</span></a>')


def nav_cluster(current):
    """Home + the collapsed menu: everything the generated nav block holds.

    One function so the generated pages and the five hand-authored ones cannot
    end up with different controls in the bar. The theme toggle inserts itself
    after .sitenav at runtime, so the rendered order is Home, Menu, theme."""
    return home_link(current) + site_nav(current)


def site_topbar(current):
    """Sticky top bar for every generated page: the collapsed Menu on the left,
    and a clear route into the deck on the right. Mirrors index.html's breakbar
    so a visitor who lands on a deep-linked page can find the playable deck. The
    header below it carries a Cavendish Cards home link and a one-line description
    so they also know what site they're on."""
    return ('<div class="breakbar"><div class="wrap">'
            '<div class="breakbar-left">'
            + nav_cluster(current) +
            '</div>'
            + deck_cta() +
            '</div></div>')


_MD_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_MD_BOLD = re.compile(r'\*\*([^*]+)\*\*')
_MD_CODE = re.compile(r'`([^`]+)`')
_MD_EM = re.compile(r'\*([^*\n]+?)\*')
_MD_IMG = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$')
_MD_OL = re.compile(r'^\d+\.\s+(.*)$')


def _md_inline(s):
    """Inline Markdown -> HTML. Escape first, then links, code, bold, em."""
    s = e(s)
    s = _MD_LINK.sub(lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', s)
    s = _MD_CODE.sub(lambda m: f'<code>{m.group(1)}</code>', s)
    s = _MD_BOLD.sub(lambda m: f'<strong>{m.group(1)}</strong>', s)
    s = _MD_EM.sub(lambda m: f'<em>{m.group(1)}</em>', s)
    return s


def _strip_md_links(s):
    """Turn [text](url) into plain text — for the calm in-app card view."""
    return _MD_LINK.sub(lambda m: m.group(1), s)


def md_to_html(text):
    """Render the small Markdown subset used by the Why sheet and Origin page.

    Handles ## / ### headings, "- " bullet lists, "1. " numbered lists, "> "
    blockquotes, ">> " pull quotes, all-dash rules, blank-line paragraphs, and
    inline links/bold/code/em. Drops a leading "# " title so the page shell owns
    the single <h1>.

    Numbered lists were added on 2026-09-18, late. Three sources had been
    writing them since long before, and with no rule to match them every "1. "
    line fell through to the paragraph branch and got JOINED to its neighbours:
    the three steps for reading a spread shipped on /example-spreads.html as one
    run-on paragraph with the numerals still in the middle of it. Nothing
    failed, which is why it lasted -- a renderer that silently does something
    plausible with input it does not understand is worse than one that stops.

    A pull quote is a line the page is built around, promoted out of the body
    text rather than duplicated beside it — so the sentence appears once, in the
    source and on the page. ">> " was picked because a plain Markdown reader
    renders it as a nested blockquote: still a quote, just set in deeper, which
    is close enough to the intent that the .md endpoint reads correctly with no
    renderer support. It emits a <p>, not a <blockquote>: these are the page's
    own words, and <blockquote> would claim they came from somewhere else.
    """
    out, para, items, steps, quote, pull = [], [], [], [], [], []

    def flush_para():
        if para:
            out.append("<p>" + _md_inline(" ".join(para).strip()) + "</p>")
            para.clear()

    def flush_list():
        if items:
            out.append("<ul>" + "".join("<li>" + _md_inline(i) + "</li>"
                                        for i in items) + "</ul>")
            items.clear()

    def flush_steps():
        if steps:
            out.append("<ol>" + "".join("<li>" + _md_inline(i) + "</li>"
                                        for i in steps) + "</ol>")
            steps.clear()

    def flush_quote():
        if quote:
            out.append("<blockquote><p>"
                       + _md_inline(" ".join(quote).strip()) + "</p></blockquote>")
            quote.clear()

    def flush_pull():
        if pull:
            out.append('<p class="pull">'
                       + _md_inline(" ".join(pull).strip()) + "</p>")
            pull.clear()

    def flush_all():
        flush_para(); flush_list(); flush_steps(); flush_quote(); flush_pull()

    for raw in text.replace("\r\n", "\n").split("\n"):
        s = raw.strip()
        if not s:
            flush_all(); continue
        if s.startswith("# "):                       # drop title; shell owns <h1>
            flush_all(); continue
        m = _MD_IMG.match(s)
        if m:
            flush_all()
            _alt = html.escape(m.group(1), quote=True)
            _src = html.escape(m.group(2), quote=True)
            out.append(f'<figure class="fig"><img src="{_src}" alt="{_alt}" loading="lazy"></figure>')
            continue
        if len(s) >= 3 and set(s) == {"-"}:           # --- horizontal rule
            flush_all(); continue
        if s.startswith("### "):
            flush_all(); out.append("<h3>" + _md_inline(s[4:]) + "</h3>"); continue
        if s.startswith("## "):
            flush_all(); out.append("<h2>" + _md_inline(s[3:]) + "</h2>"); continue
        if s.startswith("- "):
            flush_para(); flush_steps(); flush_quote(); flush_pull()
            items.append(s[2:]); continue
        m = _MD_OL.match(s)
        if m:
            flush_para(); flush_list(); flush_quote(); flush_pull()
            steps.append(m.group(1)); continue
        if s.startswith(">> "):                       # pull quote, before "> "
            flush_para(); flush_list(); flush_steps(); flush_quote()
            pull.append(s[3:]); continue
        if s.startswith("> "):
            flush_para(); flush_list(); flush_steps(); flush_pull()
            quote.append(s[2:]); continue
        flush_list(); flush_steps(); flush_quote(); flush_pull(); para.append(s)

    flush_all()
    return "\n".join(out)


def _standalone_page(title, description, skip_id, skip_label, h1, current, body,
                     tagline, script=None):
    """Full HTML doc for a standalone prose page, matching the site shell.

    `tagline` is the line under the h1 and it is REQUIRED -- there is no default
    on purpose. It used to fall back to one generic sentence about the deck,
    which meant twelve pages in a row greeted a visitor with the same words and
    told them nothing about where they had landed. A default is what let that
    happen quietly, so the parameter has none: a new page cannot be added
    without someone writing a line for it.

    It is not the meta description. The description is written for a search
    result or a link preview and talks about the page in the third person; the
    tagline is addressed to the person already on it, and says what this page
    is for and what they can do with it. Keep it to a sentence or two of the
    deck's voice. The hand-authored pages carry theirs inline in the same
    `<p class="tagline">`, and the guidebook and implementation pages open with
    a `<p class="intro">` instead, which does the same job at more length."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {_THEME_INLINE}
  <script src="/theme-toggle.js" defer></script>
  {f'<script src="/{script}" defer></script>' if script else ''}
  <title>Cavendish Cards — {e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="preload" href="/fonts/AtkinsonHyperlegible-Regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/AtkinsonHyperlegible-Bold.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="styles.css">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
{_md_head_links(current, h1)}
  <meta name="theme-color" content="#fdf6e3" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#002b36" media="(prefers-color-scheme: dark)">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Cavendish Cards">
  <meta name="color-scheme" content="light dark">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="Cavendish">
  <meta name="application-name" content="Cavendish Cards">
  <meta property="og:locale" content="en_US">
  <link rel="license" href="https://creativecommons.org/publicdomain/zero/1.0/">
  {_JSONLD}
  <meta property="og:title" content="Cavendish Space — {e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="https://cavendish.space/{current}.html">
  <link rel="canonical" href="https://cavendish.space/{current}.html">
  <meta property="og:image" content="https://cavendish.space/og-image.png?v=2">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Cavendish Space — a sheltering arch with a hearth inside it, beside the words &quot;Cavendish Space: places built to fit bodyminds, not the other way round.&quot;">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Cavendish Space — {e(title)}">
  <meta name="twitter:description" content="{e(description)}">
  <meta name="twitter:image" content="https://cavendish.space/og-image.png?v=2">
</head>
<body>
  <a class="skip" href="#{skip_id}">{e(skip_label)}</a>
  <script src="/sw-register.js" defer></script>
  {site_topbar(current)}
  <header class="site-header">
    <div class="wrap">
      <p class="backlink"><a href="index.html">Cavendish Space</a></p>
      <h1>{e(h1)}</h1>
      <p class="tagline">{tagline}</p>
    </div>
  </header>
  <main id="{skip_id}" class="wrap">
    <div class="prose">
{body}
    </div>
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <p>Free to use, print, and adapt under <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>. Part of the <a href="https://stimpunks.org/projects/cavendish-space-project/">Cavendish Space Project</a>. <a href="https://github.com/Stimpunks/Cavendish-Cards">Source on GitHub</a>. <a href="https://github.com/Stimpunks/Cavendish-Cards/blob/main/CALL-FOR-ART.md">Contribute art</a>.</p>
    </div>
  </footer>
</body>
</html>
'''


def why_html(root):
    src = (root / "cavendish-cards-why-sheet.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Why this exists",
        "Why Cavendish Cards exist: what the deck is, why, and how it serves learners.",
        "why", "Skip to the Why sheet", "Why this exists", "why",
        md_to_html(src),
        tagline="What the deck is for, who it serves, and what it refuses to "
                "be. Start here if you want the argument before the cards.")


def not_aac_html(root):
    src = (root / "cavendish-cards-not-aac.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Cavendish Cards are not AAC",
        "Why a deck of pictures a person points at is not a communication system \u2014 "
        "what AAC is for, what the deck is for, and what a person is still owed once "
        "the cards are on the table.",
        "not-aac", "Skip to the argument", "Cavendish Cards are not AAC", "not-aac",
        md_to_html(src),
        tagline="The boundary, at length. These cards sit alongside a person's "
                "real communication tools and never in place of them — here is "
                "why the line falls where it does.")


def origin_html(root):
    src = (root / "cavendish-cards-origin.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Origin & lineage",
        "Where the Cavendish Space model behind the deck comes from, and its lineage.",
        "origin", "Skip to the origin", "Origin & lineage", "origin",
        md_to_html(src),
        tagline="Where the model came from: Henry Cavendish's own conditions, "
                "Thornburg's learning spaces, and the Autistic community work "
                "all of it rests on. Credit where it is owed.")


def arles_html(root):
    src = (root / "cavendish-cards-arles.md").read_text(encoding="utf-8")
    return _standalone_page(
        "ARLES & the cards",
        "How the deck fits the Stimpunks Design Method (ARLES): Attention, Relational, Lived Experience, Environment, Systems — and why it stops short of Systems as cards.",
        "arles", "Skip to the ARLES page", "ARLES & the cards", "arles",
        md_to_html(src),
        tagline="How the deck maps onto the Stimpunks Design Method — and why "
                "it stops at Environment rather than asking a person to card "
                "the system that is failing them.")


def example_spreads_html(root):
    src = (root / "cavendish-cards-example-spreads.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Example spreads",
        "Worked examples of the deck in use: a moment, a spread someone laid, and how to read it as a design brief for the environment.",
        "example-spreads", "Skip to the examples", "Example spreads", "example-spreads",
        md_to_html(src),
        tagline="Spreads somebody laid, read the way they are meant to be read: "
                "as a list of things to change in the room, never as a report "
                "on a person.")


# The children's page. Its prose lives in cavendish-cards-place-explorers.md;
# the five place cards are generated from here, because the picture on each one
# is the deck's own Places face and the name beside it is the card's own name.
# Only the child-height line and the classroom example are new, so only those
# two are written here -- a rewording of `the cave` in cards/places/ cannot
# leave this page quoting a card that no longer says that.
#
# There is no picker. The draft this page came from ended with one: choose a
# place, be told to "go find your Cave". That hands a child responsibility for
# an accommodation the room may not have, which is the deck's argument run
# backwards, so the page turns toward the room instead. And the
# point-at-a-picture job it was imitating is already done, properly and
# face-down, by the Places cards this page links to.
#
# (slug in cards/places/, the line a child reads, the classroom example)
PLACES = [
    ("the-cave",
     "Your own quiet spot. Nobody else is in it. Just you.",
     "a reading corner, a tent, or headphones at your desk."),
    ("the-campfire",
     "A small circle with a few friends. Quiet enough to talk in.",
     "three friends sharing one table for a project."),
    ("the-watering-hole",
     "Lots of people, showing each other what they know. "
     "You can join in, or just listen.",
     "everyone showing the class something they made."),
    ("the-library",
     "Where we keep what we have worked out, so anyone can find it again. "
     "Look things up, and add what you know.",
     "the word wall, or the box of instructions everyone adds to."),
    # The habitat holds the other four, so it spans the grid rather than
    # sitting in it as a fifth equal tile.
    ("the-habitat",
     "The whole space that holds the other four inside it. "
     "Your classroom. Your home.",
     "look around the room you are in. Where would a cave go? "
     "Where is the campfire?"),
]

_PLACES_HEADING = "## The five places"


def _place_names(out_families):
    """{slug: name} for the Places realm, from the built deck."""
    for fam in out_families:
        if fam["slug"] == "places":
            return {c["slug"]: c["name"] for c in fam["cards"]}
    return {}


def _place_cards_html(out_families):
    """The five place cards as a grid, each showing its real card face.

    The face is the same SVG the deck and the print sheets use, so a child sees
    on this page exactly the card they would be handed. It is decorative here:
    the card's name is the <h3> right beside it, and alt text repeating that
    name would make a screen reader say everything twice."""
    names = _place_names(out_families)
    cards = []
    for slug, line, try_it in PLACES:
        name = names.get(slug)
        if not name:
            print(f"  ! place-explorers: no places/{slug} card", file=sys.stderr)
            continue
        wide = " wide" if slug == "the-habitat" else ""
        cards.append(
            f'<article class="placecard{wide} place-{slug}">'
            f'<img class="placecard-face" src="faces/places--{slug}.svg" alt="" '
            f'width="750" height="1050" loading="lazy" decoding="async">'
            f'<div class="placecard-text">'
            f'<h3>{e(name)}</h3>'
            f'<p>{e(line)}</p>'
            f'<p class="tryit"><strong>Try it:</strong> {e(try_it)}</p>'
            f'</div></article>')
    return '<div class="places-grid">' + "".join(cards) + "</div>"


def _place_cards_md(out_families):
    """The same five cards as Markdown, for the .md endpoint."""
    names = _place_names(out_families)
    out = []
    for slug, line, try_it in PLACES:
        name = names.get(slug)
        if not name:
            continue
        out += [f"### {name}", "",
                f"![{name}](faces/places--{slug}.svg)", "",
                line, "", f"**Try it:** {try_it}", ""]
    return "\n".join(out)


def _place_explorers_parts(root):
    """The prose source, split either side of the generated card grid."""
    src = (root / "cavendish-cards-place-explorers.md").read_text(encoding="utf-8")
    if _PLACES_HEADING not in src:
        sys.exit(f"place-explorers: source is missing {_PLACES_HEADING!r}")
    before, after = src.split(_PLACES_HEADING, 1)
    return before, after


def place_explorers_md(root, out_families):
    """The full page as Markdown: prose source + generated cards spliced in."""
    before, after = _place_explorers_parts(root)
    return (before + _PLACES_HEADING + "\n\n"
            + _place_cards_md(out_families) + "\n" + after.lstrip("\n"))


def place_explorers_html(root, out_families):
    """The five places in children's words, with the deck's own card faces."""
    before, after = _place_explorers_parts(root)
    body = "\n".join([
        md_to_html(before),
        "<h2>The five places</h2>",
        _place_cards_html(out_families),
        md_to_html(after),
    ])
    return _standalone_page(
        "Place Explorers",
        "The five Cavendish places in children's words, for ages about 7 to 11 — "
        "cave, campfire, watering hole, library, and habitat, with classroom "
        "examples and what to do when the place you need isn't there.",
        "place-explorers", "Skip to the places", "Place Explorers", "place-explorers",
        body,
        tagline="Every room should have a spot for how you feel. "
                "Here are the five, in children's words.")


# ---------------------------------------------------------------------------
# SPACE-TIME page: three renderings of SPACE_TIME, plus the prose around them.
# ---------------------------------------------------------------------------

_ST_HEADINGS = ["## The framework at a glance",
                "## SPACE-TIME and monotropism",
                "## What each element asks of a room"]


def _split_on_headings(src, headings, what):
    """Split a prose source into the chunks around a list of headings.

    Returns [before_first, after_1, after_2, ...] -- one more piece than there
    are headings -- so a caller can interleave generated blocks. The headings
    themselves are dropped; the caller re-emits them, which keeps the heading
    text in the prose source where an author will find it.

    A missing heading is fatal. The alternative is a page that silently ships
    without its table, and a generated block is exactly the kind of thing
    nobody notices is absent."""
    out = []
    rest = src
    for h in headings:
        if h not in rest:
            sys.exit(f"{what}: source is missing the heading {h!r}")
        before, rest = rest.split(h, 1)
        out.append(before)
    out.append(rest)
    return out


def _cond_map(web):
    """The zone builder's conditions, id -> text, in rooms.js order.

    One parser, three callers: the COND parity check, the SPACE-TIME page's
    room conditions, and the SPACE-TIME id check. The page prints the zoner's
    own words rather than a paraphrase, so a reworded condition reaches the
    page on the next build instead of quietly disagreeing with it."""
    js = (web / "rooms.js").read_text(encoding="utf-8")
    block = re.search(r"var COND = \{(.*?)\n  \};", js, re.S)
    if not block:
        return {}
    return dict(re.findall(r'"([a-z-]+)": "([^"]*)"', block.group(1)))


def _check_space_time_cards(out_families):
    """Warn when SPACE-TIME cites a card that isn't in the realm it claims.

    Same failure as _check_card_citations, one layer in: the mapping is written
    by realm, by hand, from memory of the deck, and `i want to stay a while`
    was filed under Weather here before this check existed -- it is a lily pad.
    Non-fatal, like the rest; watch the build output."""
    where = {}
    display = {}
    for fam in out_families:
        display[fam["slug"]] = fam["name"]
        for c in fam["cards"]:
            where.setdefault(c["name"], set()).add(fam["name"])
    for row in SPACE_TIME:
        for realm, names in row["cards"]:
            for n in names:
                if n not in where:
                    print(f"  ! SPACE-TIME {row['letter']} cites {n!r}, "
                          f"which is no card in the deck", file=sys.stderr)
                elif realm not in where[n]:
                    print(f"  ! SPACE-TIME {row['letter']} files {n!r} under "
                          f"{realm}; it is {'/'.join(sorted(where[n]))}",
                          file=sys.stderr)


def _check_space_time_conds(web):
    """Warn when SPACE-TIME points at a zone-builder condition that is gone.

    The ids are a published contract already (see _check_cond_parity); this
    page is now a fourth place that spells them."""
    conds = _cond_map(web)
    if not conds:
        print("  ! could not check SPACE-TIME conditions (rooms.js moved)",
              file=sys.stderr)
        return
    for row in SPACE_TIME:
        for cid in row["conds"]:
            if cid not in conds:
                print(f"  ! SPACE-TIME {row['letter']} names condition "
                      f"{cid!r}, which rooms.js has no condition for",
                      file=sys.stderr)


def _space_time_figure_html():
    """The article's infographic, rebuilt as HTML.

    A picture of a framework is a picture: unselectable, unsearchable,
    unreadable at a screen reader and unreadable at 200% zoom on a phone. So it
    is laid out rather than drawn -- two panels of letter tiles and the
    statement underneath, from the same list the table comes from. The letters
    are aria-hidden: each one is the first letter of the name right beside it,
    and a screen reader announcing "S, Sensory attunement" reads the spelling
    aloud as content."""
    panels = []
    for part, lead in (("SPACE", "The foundations. What has to hold before "
                                 "anything else is possible."),
                       ("TIME", "What belonging takes, once the foundations "
                                "hold.")):
        rows = [r for r in SPACE_TIME if r["part"] == part]
        word = "".join(r["letter"] for r in rows)
        tiles = "".join(
            f'<li class="st-tile">'
            f'<span class="st-letter" aria-hidden="true">{e(r["letter"])}</span>'
            f'<span class="st-tile-text">'
            f'<strong>{e(r["name"])}</strong>'
            f'<span class="st-tile-line">{e(r["tile"])}</span>'
            f'</span></li>'
            for r in rows)
        panels.append(
            f'<section class="st-panel st-panel-{part.lower()}" '
            f'aria-label="{e(word)}">'
            f'<h3 class="st-word">{e(word)}</h3>'
            f'<p class="st-lead">{e(lead)}</p>'
            f'<ul class="st-tiles">{tiles}</ul>'
            f'</section>')
    statement = "".join(f"<p>{e(line)}</p>" for line in SPACE_TIME_STATEMENT)
    return ('<figure class="st-figure">'
            '<div class="st-panels">' + "".join(panels) + '</div>'
            '<figcaption class="st-statement">' + statement +
            '<p class="st-credit">SPACE-TIME, by Helen Edgar '
            '(<a href="https://autisticrealms.com/space-time-a-monotropism-informed-framework-for-autistic-people/">Autistic Realms</a>). '
            'Laid out here rather than pictured, so it can be read at any size '
            'and by anything.</p>'
            '</figcaption></figure>')


def _space_time_table_html():
    """Helen's table, reproduced. Four columns, hers, in her order.

    The Cavendish mapping is deliberately NOT a fifth column here: it is our
    writing, it belongs to us, and folding it in would make one table that
    reads as though one person wrote all of it. It gets its own section below.

    Wrapped in a labelled, focusable region so the horizontal overflow a narrow
    screen forces is reachable from a keyboard as well as a finger."""
    head = ("<thead><tr>"
            "<th scope=\"col\">SPACE-TIME element</th>"
            "<th scope=\"col\">From Autistic SPACE</th>"
            "<th scope=\"col\">From the 8 dimensions of care</th>"
            "<th scope=\"col\">Monotropism and Autistic flow</th>"
            "</tr></thead>")
    rows = "".join(
        '<tr><th scope="row">'
        f'<span class="st-rowletter" aria-hidden="true">{e(r["letter"])}</span> '
        f'{e(r["name"])}</th>'
        f'<td>{e(r["space"])}</td><td>{e(r["dims"])}</td>'
        f'<td>{e(r["flow"])}</td></tr>'
        for r in SPACE_TIME)
    return ('<div class="table-scroll" tabindex="0" role="region" '
            'aria-label="SPACE-TIME and monotropism, a table of nine elements">'
            '<table class="st-table">'
            '<caption>Each element, the framework it comes from, and what '
            'monotropism has to do with it. Columns two and three name other '
            "people's frameworks; column four is Helen Edgar's.</caption>"
            + head + "<tbody>" + rows + "</tbody></table></div>")


def _space_time_build_html(conds):
    """What each element asks of a room — the deck's own column, as blocks.

    Blocks rather than a table: this is prose with two short lists under it,
    and a fifth column of paragraphs would have pushed the table past what any
    phone can show."""
    out = []
    for r in SPACE_TIME:
        bits = [f'<h3 class="st-ask-head">'
                f'<span class="st-rowletter" aria-hidden="true">{e(r["letter"])}</span> '
                f'{e(r["name"])}</h3>',
                f'<p>{e(r["asks"])}</p>']
        if r["zones"]:
            zones = ", ".join(e(z) for z in r["zones"])
            bits.append(f'<p class="st-where"><strong>Places:</strong> {zones}.</p>')
        for realm, names in r["cards"]:
            listed = ", ".join(f"<em>{e(n)}</em>" for n in names)
            bits.append(f'<p class="st-where"><strong>{e(realm)}:</strong> {listed}.</p>')
        live = [c for c in r["conds"] if c in conds]
        if live:
            listed = "".join(f"<li><code>{e(c)}</code> — {e(conds[c])}</li>"
                             for c in live)
            bits.append('<p class="st-where"><strong>In the zone builder:</strong></p>'
                        f'<ul class="st-conds">{listed}</ul>')
        else:
            bits.append('<p class="st-where"><strong>In the zone builder:</strong> '
                        'nothing to tick. This one is not a property of the room.</p>')
        out.append('<section class="st-ask">' + "".join(bits) + '</section>')
    return '<div class="st-asks">' + "".join(out) + "</div>"


def _space_time_figure_md():
    """The infographic as Markdown, for the .md endpoint."""
    L = []
    for part in ("SPACE", "TIME"):
        L += [f"### {part}", ""]
        for r in SPACE_TIME:
            if r["part"] == part:
                L.append(f"- **{r['letter']} — {r['name']}.** {r['tile']}")
        L.append("")
    L += SPACE_TIME_STATEMENT + [""]
    L.append("SPACE-TIME, by Helen Edgar (Autistic Realms).")
    return "\n".join(L)


def _space_time_table_md():
    """Helen's table as a Markdown pipe table."""
    L = ["| SPACE-TIME element | From Autistic SPACE | "
         "From the 8 dimensions of care | Monotropism and Autistic flow |",
         "| --- | --- | --- | --- |"]
    for r in SPACE_TIME:
        L.append(f"| **{r['letter']} — {r['name']}** | {r['space']} | "
                 f"{r['dims']} | {r['flow']} |")
    return "\n".join(L)


def _space_time_build_md(conds):
    """The Cavendish mapping as Markdown."""
    L = []
    for r in SPACE_TIME:
        L += [f"### {r['letter']} — {r['name']}", "", r["asks"], ""]
        if r["zones"]:
            L.append(f"- **Places:** {', '.join(r['zones'])}.")
        for realm, names in r["cards"]:
            L.append(f"- **{realm}:** {', '.join('*' + n + '*' for n in names)}.")
        live = [c for c in r["conds"] if c in conds]
        if live:
            L.append("- **In the zone builder:** "
                     + "; ".join(f"`{c}` ({conds[c]})" for c in live) + ".")
        else:
            L.append("- **In the zone builder:** nothing to tick. This one is "
                     "not a property of the room.")
        L.append("")
    return "\n".join(L)


def space_time_html(root, web):
    conds = _cond_map(web)
    src = (root / "cavendish-cards-space-time.md").read_text(encoding="utf-8")
    a, b, c, d = _split_on_headings(src, _ST_HEADINGS, "space-time")
    body = "\n".join([
        md_to_html(a),
        "<h2>The framework at a glance</h2>", _space_time_figure_html(),
        "<h2>SPACE-TIME and monotropism</h2>", _space_time_table_html(),
        "<h2>What each element asks of a room</h2>", _space_time_build_html(conds),
        md_to_html(d),
    ])
    return _standalone_page(
        "SPACE-TIME",
        "Helen Edgar's monotropism-informed framework for Autistic people — "
        "nine elements an environment has to hold, the table behind them, and "
        "which cards and room conditions answer each one.",
        "space-time", "Skip to the framework", "SPACE-TIME", "space-time",
        body,
        tagline="What a place has to hold if an Autistic person is going to do "
                "more there than endure it — and which cards and zones "
                "answer each part.")


def space_time_md(root, web):
    """The full page as Markdown: prose source with the generated blocks in."""
    conds = _cond_map(web)
    src = (root / "cavendish-cards-space-time.md").read_text(encoding="utf-8")
    a, b, c, d = _split_on_headings(src, _ST_HEADINGS, "space-time")
    blocks = [_space_time_figure_md(), _space_time_table_md(),
              _space_time_build_md(conds)]
    # A generated block has to end in a BLANK line, not just a newline: the
    # pipe table ran straight into the next "## " heading otherwise, which a
    # Markdown reader renders as one more table row.
    return "".join([a] + [h + "\n\n" + b.rstrip("\n") + "\n\n"
                          for h, b in zip(_ST_HEADINGS, blocks)]
                   + [d.lstrip("\n")])


def inclusive_environment_html(root):
    src = (root / "cavendish-cards-inclusive-environment.md").read_text(
        encoding="utf-8")
    return _standalone_page(
        "Building inclusive environments",
        "The seven layers an environment is built in — nervous system, "
        "sensory, communication, predictability, instruction, repair, power "
        "— what each one asks for, and which cards and zones reach it.",
        "inclusive-environment", "Skip to the layers",
        "Building inclusive environments", "inclusive-environment",
        md_to_html(src),
        tagline="Inclusion is architecture, not goodwill. The seven layers a "
                "place is built in, and where the deck reaches — plus the "
                "two it deliberately doesn't.")


def group_needs_html(root):
    src = (root / "cavendish-cards-group-needs.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Group access needs",
        "A method for turning a pile of spreads into one brief for the room \u2014 and a "
        "skill description to hand an AI, with the rules that keep it a design brief "
        "and not a report on people.",
        "group-needs", "Skip to the method", "Group access needs", "group-needs",
        md_to_html(src),
        tagline="Many spreads, one room, and no counting. How to turn what a "
                "group asked for into a brief the room can act on, without it "
                "becoming a report on anybody.")


def livable_worlds_html(root):
    src = (root / "cavendish-cards-livable-worlds.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Livable worlds checklist",
        "A companion audit for the deck: run it on the room, the routine, the kit, or the system \u2014 never on the person \u2014 to find what to change.",
        "livable-worlds", "Skip to the checklist", "Livable worlds checklist", "livable-worlds",
        md_to_html(src),
        tagline="Run it on the room, the routine, the kit, or the system. Never "
                "on the person. Every box that comes up short is a design "
                "brief.")


def privacy_html(root):
    src = (root / "cavendish-cards-privacy.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Privacy & security",
        "What Cavendish Cards keeps (almost nothing), how it stays on your device, and the security measures behind the site.",
        "privacy", "Skip to the privacy details", "Privacy & security", "privacy",
        md_to_html(src),
        tagline="Nothing leaves your device, because there is nowhere for it to "
                "go: no server, no database, no analytics, no third parties. "
                "Also how to tell us if you find a hole.")


def not_found_html():
    """The 404 page. Netlify serves /404.html with a 404 status for any unmatched
    path, so this is what a broken link lands on. It reuses the standalone shell,
    which means the menu comes from SITE_NAV and stays correct for free. The copy
    holds the line: a dead link is a broken system, not a visitor who did
    something wrong."""
    body = """<p>This page isn't here. A link pointed somewhere that doesn't exist
&mdash; that's the link, not you. Nothing you did broke anything, and nothing is lost.</p>
<p>Here are the doors back in:</p>
<ul>
<li><a href="deck.html">The deck</a> &mdash; show how you feel and what you need.</li>
<li><a href="rooms.html">Zone a room</a> &mdash; set up a space with the five zones.</li>
<li><a href="space.html">What is a Cavendish Space?</a> &mdash; the model behind all of it.</li>
<li><a href="guidebook.html">The guidebook</a> &mdash; every card, and how to hold it.</li>
</ul>
<p>The full menu is at the top of this page. If a link on this site sent you here,
that's a bug worth telling us about &mdash;
<a href="https://github.com/Stimpunks/Cavendish-Cards/issues">open an issue</a>
or email <a href="mailto:stimpunks@stimpunks.org">stimpunks@stimpunks.org</a>.</p>"""
    return _standalone_page(
        "Page not found",
        "That page isn't here. The deck, the zone builder, and the guidebook are.",
        "not-found", "Skip to the ways back", "This page isn't here", "404",
        body,
        tagline="Every other page on this site still works. "
                "These are the main ones.")


def changelog_html(root):
    src = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Changelog",
        "A running summary of notable changes to the Cavendish Cards deck and website.",
        "changelog", "Skip to the changelog", "Changelog", "changelog",
        md_to_html(src),
        tagline="What changed in the deck and on the site, newest first — cards "
                "added and reworded under Deck, everything else under Site.")


def _load_facilitator():
    """Load build-facilitator-pdf.py for its Markdown parser only.

    Importing the module runs stdlib-level code only; weasyprint is imported
    lazily inside that script's main(), so this stays PDF-dependency-free and
    runs anywhere build-site.py runs (local dev without weasyprint, Netlify).
    """
    path = Path(__file__).resolve().parent / "build-facilitator-pdf.py"
    if not path.exists():
        sys.exit(f"Could not find {path}")
    spec = importlib.util.spec_from_file_location("build_facilitator_pdf", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


FACILITATOR_PDF_URL = ("https://github.com/Stimpunks/Cavendish-Cards/blob/main/"
                       "cavendish-cards-facilitator-sheet.pdf")


def facilitator_html(root):
    # Reuse the facilitator PDF's own parser so the on-site sheet and the print
    # PDF render from one source and cannot drift in content or structure.
    fac = _load_facilitator()
    src = (root / "cavendish-cards-facilitator-sheet.md").read_text(encoding="utf-8")
    _title, _kicker, blocks = fac.parse(src)
    # Drop the sheet's own CC0 footer; the site shell already carries one.
    blocks = [b for b in blocks if not b.startswith("<footer>")]
    pdf_note = (f'<p class="facilitator-pdf"><a href="{FACILITATOR_PDF_URL}">'
                'Download the print sheet (PDF)</a> \u2014 the same content, '
                'laid out for handing round.</p>')
    body = pdf_note + "\n" + "\n".join(blocks)
    return _standalone_page(
        "Facilitator Sheet",
        "A short guide for support staff: the seven ways to play, the sharing model, what to do with a pile of spreads, and how to respond to one.",
        "facilitator", "Skip to the facilitator sheet", "Facilitator Sheet",
        "facilitator", body,
        tagline="For whoever is holding the space. The ways to play, how "
                "sharing works, and what to do when somebody lays a spread in "
                "front of you.")


def guidebook_html(out_families):
    sections = []
    for fam in out_families:
        entries = []
        for c in fam["cards"]:
            if c["prompt"]:
                meta = f'<em>{e(c["cue"])}</em> &middot; &ldquo;{e(c["prompt"])}&rdquo;'
            elif c["given_not_read"]:
                meta = f'<em>{e(c["cue"])}</em> &middot; given or claimed'
            else:
                meta = f'<em>{e(c["cue"])}</em>'
            note = f'<p>{_md_inline(c["notes"])}</p>' if c["notes"] else ''
            pattern = c.get("_pattern", "")
            entries.append(
                f'<article class="gb-entry"><h3>{e(c["name"])}</h3>'
                f'<p class="gb-meta">{meta}</p>{note}{pattern}</article>'
            )
        realm_note = GUIDEBOOK_NOTES.get(fam["slug"], "")
        gb_name = GB_NAMES.get(fam["slug"], fam["name"])
        sections.append(
            f'<section class="gb-family" id="gb-{fam["slug"]}"><h2>{e(gb_name)}</h2>'
            f'<p class="muted">{e(fam["intro"])}</p>{realm_note}{"".join(entries)}</section>'
        )
    body = "\n".join(sections)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {_THEME_INLINE}
  <script src="/theme-toggle.js" defer></script>
  <title>Cavendish Cards — Guidebook</title>
  <meta name="description" content="What each Cavendish card means and how to hold it. It describes the card, never the person.">
  <link rel="preload" href="/fonts/AtkinsonHyperlegible-Regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/AtkinsonHyperlegible-Bold.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="styles.css">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="describedby" type="text/markdown" href="/llms.txt">
  <link rel="alternate" type="text/markdown" href="/guidebook.md" title="Guidebook &mdash; Markdown source">
  <meta name="theme-color" content="#fdf6e3" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#002b36" media="(prefers-color-scheme: dark)">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Cavendish Cards">
  <meta name="color-scheme" content="light dark">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="Cavendish">
  <meta name="application-name" content="Cavendish Cards">
  <meta property="og:locale" content="en_US">
  <link rel="license" href="https://creativecommons.org/publicdomain/zero/1.0/">
  {_JSONLD}
  <meta property="og:title" content="Cavendish Space — Guidebook">
  <meta property="og:description" content="What each Cavendish card means and how to hold it. It describes the card, never the person.">
  <meta property="og:url" content="https://cavendish.space/guidebook.html">
  <link rel="canonical" href="https://cavendish.space/guidebook.html">
  <meta property="og:image" content="https://cavendish.space/og-image.png?v=2">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Cavendish Space — a sheltering arch with a hearth inside it, beside the words &quot;Cavendish Space: places built to fit bodyminds, not the other way round.&quot;">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Cavendish Space — Guidebook">
  <meta name="twitter:description" content="What each Cavendish card means and how to hold it. It describes the card, never the person.">
  <meta name="twitter:image" content="https://cavendish.space/og-image.png?v=2">
</head>
<body>
  <a class="skip" href="#gb">Skip to the guidebook</a>
  <script src="/sw-register.js" defer></script>
  {site_topbar("guidebook")}
  <header class="site-header">
    <div class="wrap">
      <p class="backlink"><a href="index.html">Cavendish Space</a></p>
      <h1>Guidebook</h1>
      <p class="intro">{e(INTRO)}</p>
      <div class="rules stack" role="note" aria-label="Not a screening tool">
        <p><strong>Not a screening tool.</strong> {e(SCREENING)}</p>
        <p class="rules-lead">{e(FRAMEWORKS_LEAD)}</p>
        <ul class="rules-list">
{"".join(f"          <li><strong>{e(t)}.</strong> {e(b)}</li>{chr(10)}" for t, b in FRAMEWORKS)}        </ul>
      </div>
      <div class="rules" role="note" aria-label="Not an AAC board">
        <p><strong>Not an AAC board.</strong> {e(NOT_AAC)}</p>
        <p>The long version, and why the line is where it is: <a href="not-aac.html">Cavendish Cards are not AAC</a>.</p>
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


# ---------------------------------------------------------------------------
# Implementation Guidebook — the companion "how to build the room" book.
# Renders to web/implementation.html and cavendish-cards-implementation-layer.md.
# Card names come from the deck (so they never drift); the build prose lives here
# for hand-iteration. Facilitator layer: materials stay here, never on a card. Sourced
# from early-years / PMLD practice (Helen Edgar); meant to be iterated in-app.
# ---------------------------------------------------------------------------

IMPL_ORDER = ["places", "what-helps", "lily-pad"]
IMPL_LABELS = {
    "places": "Building the space",
    "what-helps": "Building the niche",
    "lily-pad": "Building the crossings",
}

IMPL_INTRO = (
    "The card guidebook says what each card means. This one says how to build the "
    "room the cards ask for. A person laying cave, i need a minute, coming back has "
    "handed you a design brief for the space between one place and the next \u2014 and "
    "this is how you answer it, in cushions, light, sightlines, and floor plan. It is "
    "the facilitator layer: the materials live here, never on a card. The card names the "
    "need; you fill it with what you have."
)

IMPL_PRINCIPLE = (
    "Design the space between the zones \u2014 not just the zones. Most rooms build the "
    "destinations and leave the crossings to chance, so a person still has to leap. The "
    "principle is the same for every person: gentle, continuous, warned, consented "
    "crossings, never on the room's clock. How you build the crossing changes with how "
    "a person moves, senses, and communicates \u2014 and the room is built with the person, "
    "not around them."
)

IMPL_GUARDRAILS = [
    ("The turn is theirs",
     "A spread laid face-down stays private; turning a card up is the person sharing "
     "it, and that turn is the consent \u2014 you don't turn their cards over for them. "
     "Build the room from what they've shown, never from the cards they've kept; a "
     "spread is self-advocacy in their hands, not a reading you take."),
    ("Build with, never to",
     "A padded crossing or a made niche is designed with the person and offered as a "
     "gentle nudge \u2014 never sprung as a demand, never done to them. Presume competence."),
    ("The room is the work, not the person",
     "You are shaping the environment, not fixing the person. A hard transition, or a "
     "space that doesn't fit, is information about the room \u2014 never a verdict on whoever "
     "is in it."),
    ("Not a compliance system",
     "Smoother days are a by-product, never the goal, and a sensory space is never "
     "containment or seclusion. Don't let \u201cwe built them a nook\u201d become a reason to "
     "under-provide real rest, real support, or a person's actual communication tools."),
]

IMPL_REALM_NOTES = {
    "places":
        "The five zones are the cave (solitude), the campfire (a small, known group), "
        "the watering hole (open, ambient company), the library (reference and depth), "
        "and the habitat (the whole surround that holds the other four). Cave, campfire, "
        "and watering hole also run along a sociality gradient \u2014 solo, small group, open "
        "\u2014 lining up with the interaction moods (red, yellow, green). Build the zones so "
        "a person can move along that gradient on their own terms, and keep each reachable "
        "without a leap.",
    "what-helps":
        "These are the pieces you change so the space fits. Each card names a need, not a "
        "product \u2014 a den can be a pop-up tent or a blanket over a table; less to look at "
        "can be a screen, a corner, or a turned-around desk. Build for the sense the person "
        "is asking about, with whatever you have. When nobody has laid a card, walk the room "
        "and ask it yourself, one channel at a time: what does a person see here, hear, "
        "smell? What meets them when they touch something? How can they move? Ask it "
        "standing in the room rather than at a desk, and put the answers in the signposts "
        "below. Two things a sense-walk will never show you, so ask them on their own: who "
        "holds the controls, and how much a person has to say \u2014 or how fast they have to "
        "be \u2014 to get what they need. Organised here the way the deck groups it \u2014 mostly "
        "by sense, plus the two that are not a channel of the body at all.",
    "lily-pad":
        "A transition is a crossing, and for a mind in deep focus a hard crossing is "
        "jarring and costly \u2014 attention yanked across with nowhere to land. Lily pads are "
        "the stepping stones that make it gentle: a pause, a heads-up, a held place, a "
        "graded step. Build the space between the zones so each crossing has somewhere to "
        "land, and keep the pace the person's \u2014 read from their signals when they can't set "
        "it with their feet.",
}

# Per-card build notes (Places zones + Lily-pad crossings). Keyed by card slug;
# the display name is pulled live from the deck. Cards without a note (each realm's
# your-own) are simply skipped.
IMPL_PAIRINGS = {
    "the-cave": "Two walls and a low roof of your making \u2014 a blanket over a table, a "
                "corner with a shelf pulled across, a hood pulled up. Low light, sound "
                "down, the world kept out. A retreat, never a time-out.",
    "the-campfire": "A small, soft circle \u2014 a rug, a few cushions, room for a known "
                    "handful rather than a crowd. Close enough to feel the warmth; never "
                    "a stage.",
    "the-watering-hole": "An open, in-between spot near others \u2014 a bench at the edge of "
                         "the room, somewhere to hover and drift, among people without a "
                         "task or a script.",
    "the-library": "Somewhere the group's figured-out things are kept and reachable \u2014 a "
                   "shelf, a box, a screen \u2014 a place to go deep at your own pace.",
    "the-habitat": "The whole surround: the light, sound, texture, and rhythm the other "
                   "zones sit inside. Make the habitat steady and sensory-safe first, and "
                   "the other places become reachable.",
    "i-need-a-minute": "A pause-place at the seam \u2014 a beanbag, a windowsill, a cushion "
                       "where two zones meet \u2014 so leaving one lands somewhere before "
                       "arriving at the next.",
    "slowly": "A graded strip between a loud zone and a quiet one, where the light dims "
              "and the sound drops before arrival. Grade the crossing instead of forcing "
              "a single leap.",
    "not-yet": "Let the crossing wait on the person's signal \u2014 check back rather than "
               "push \u2014 never on the room's clock.",
    "ready-now": "Go when they go: follow their timing, and build routes that let them "
                 "move the moment they're ready.",
    "coming-back": "Keep the spot, the task, and the welcome ready, and let a carried "
                   "object travel the crossing as a thread of continuity between the two "
                   "banks.",
    "stuck": "A landing spot in the gap \u2014 somewhere to be between pads without being "
             "pushed across. Offer a what-helps, and let them choose; never shove.",
    "watch-first": "A place at the rim of a group, in view of it, where watching counts "
                   "as being in. Keep joining optional.",
    "all-done": "Let a called ending be an ending \u2014 no one-more-thing, no negotiation "
                "over whether it really is.",
    "i-want-to-stay-a-while": "Let staying stand \u2014 a spot that isn't hurried on just "
                              "because the schedule wants it.",
}

# What helps — build guidance, one entry per signpost. Keep in step with GROUPS.
IMPL_WHATHELPS = [
    ("Being in charge",
     "Hand over the dial. The same input is fine when the person controls it and too "
     "much when someone else does \u2014 so give them the switch, the volume, the timing, "
     "not a fixed setting."),
    ("Choosing",
     "Cut the field down. Too many options is a real cost, not fussiness \u2014 offer two or "
     "three instead of ten, settle the small things in advance, or hand over a first step "
     "to start from. Narrowing a choice is not taking the choice away."),
    ("Sound",
     "Turn the world down, or fill it kindly \u2014 headphones, a quieter corner, or a "
     "steady hum to cover the jagged, unpredictable sounds. The sound was the problem; "
     "lowering it is the answer, not avoidance."),
    ("Light & looking",
     "Soften what reaches the eyes. Dim or diffuse harsh light, and clear busy "
     "sight-lines \u2014 a plainer wall, fewer displays, a calmer view. Clearing clutter "
     "is free."),
    ("Touch",
     "A soft thing to hold \u2014 a plush, a texture, something to squeeze or keep close. "
     "A tactile anchor is a real regulation strategy, not babyish; let it stay."),
    ("Pressure",
     "Deep, even pressure \u2014 a weighted wrap, a firm tuck \u2014 but only ever the pressure "
     "the person asks for, on their terms."),
    ("Temperature",
     "A layer, a fan, an open window, a warm drink. Too warm or too cold fills a body "
     "up like noise does; change the air around the person rather than telling them "
     "they're fine."),
    ("Movement",
     "Room to move, and things to move with \u2014 floor to pace or spin, a fidget for the "
     "hands, options to sit, stand, or wobble, freedom to stim. Bodies that move to "
     "focus are doing exactly what they should."),
    ("Mouth & nose",
     "Safe oral and scent input \u2014 something to chew or crunch, a snack or a drink, a "
     "calming smell brought close or an overwhelming one taken away. Ordinary needs, "
     "met without a negotiation."),
    ("Space & enclosure",
     "Cover and edges \u2014 a den to tuck under, a corner with sides, a claimed spot that "
     "stays theirs, and a visible, usable way out. Knowing the door is there is often "
     "what makes staying possible."),
    ("Telling & talking",
     "Ease the language load \u2014 fewer words, a heads-up before a change, and another "
     "channel to point, write, sign, or show a card when speech is hard. A different "
     "way to communicate is not less communication."),
    ("People & time",
     "Thin the social field and slow the clock \u2014 one steady person instead of a crowd, "
     "quiet company alongside, more processing time, a stopping point before a switch, "
     "permission to come and go. Speed is not understanding."),
    ("Same & new",
     "Two directions on one dial. Hold the routine steady where it does not need to move "
     "\u2014 same order, same setup, same cup \u2014 and change what is inside it when it has gone "
     "flat. A person can want both at once, and usually does: a steady container with "
     "moving contents is the shape that works, not a contradiction."),
    ("Make your own",
     "The gap the deck doesn't hold yet \u2014 draw or build the missing help together."),
]

IMPL_BUDGET = (
    "None of this is a purchase order. A blanket over a table is a cave. A rug zones a "
    "watering hole. A turned-around shelf makes a corner. A dimmable lamp makes a "
    "decompression seam. A cushion at the join of two zones is a pause pad. The "
    "materials are yours to choose; the card names the need, and you fill it with what "
    "you have."
)
BUDGET_URL = "https://stimpunks.org/2024/03/14/creating-cavendish-space-on-a-budget/"
NESTING_URL = "https://stimpunks.org/glossary/nesting/"
PMLD_URL = ("https://stimpunks.org/2024/10/28/spaces-for-multi-sensory-learners-and-those-with-profound-and-multiple-learning-disabilities/")
PMLD_TITLE = ("Cavendish Spaces for Multi-Sensory Learners and Those with Profound and Multiple Learning Disabilities")

IMPL_EXAMPLES_HEAD = "Worked examples: multi-sensory and PMLD settings"

IMPL_EXAMPLES_INTRO = (
    "Some people will never point at a card. The zones get built with them anyway, read "
    "from a different channel \u2014 what a person reaches for, turns toward, settles into, "
    "or pushes away. These are worked examples from early-years and specialist settings, "
    "where much of this practice was built with children with Profound and Multiple "
    "Learning Disabilities, at the level of umbrellas, projectors, and things within "
    "arm's length. Written here in the deck's own words; the source has them at length."
)

IMPL_EXAMPLES_RULES_LEAD = "Three things carry more weight here than anywhere else in this book:"

IMPL_EXAMPLES_RULES = [
    ("A den someone cannot leave is not a den",
     "A cave works because the person chose it and can end it. When leaving needs "
     "somebody else's hands, the way out is not a doorway \u2014 it is a person who checks, "
     "on the person's signal rather than the room's schedule. Without that, a sensory "
     "space is seclusion with nicer lighting."),
    ("Whatever a person talks with comes into the space",
     "A switch, a book, a talker, a signing partner, a card \u2014 it goes into the cave with "
     "them, stays in reach, and stays charged. A space that separates a person from "
     "their voice is the wrong space, however soft it is."),
    ("Reading is not scoring",
     "You build from what a person reaches for and what they turn away from. That "
     "reading is a design brief for the room, exactly like a spread. It is not a record "
     "of the person, it does not go in a file, and there is no state anyone is supposed "
     "to reach."),
]

IMPL_EXAMPLES_LEAD = "Then, zone by zone:"

IMPL_EXAMPLES = [
    ("the cave",
     "Enclosure, at whatever height the person already is. Over a bed: a frame carrying "
     "lights, soft materials, and things to reach for without moving. On the floor: a "
     "tent big enough that a wheelchair, a standing frame, or a physio wedge comes "
     "inside \u2014 the equipment goes in the cave, never parked outside it. At floor level: "
     "a large umbrella, which is the portable version, opened where the person already "
     "is, with things hung from the spokes. Overhead: a hoop or a curtain track, with a "
     "curtain that changes with the theme and takes a projection."),
    ("the campfire",
     "A small known group around one shared thing, with somebody telling it. A basket of "
     "natural objects to pass and explore. Multisensory stories, told the same way each "
     "time so the next part can be anticipated \u2014 rhyming versions when the rhythm is "
     "what carries it. Story Massage and Dance Massage, where the story arrives through "
     "touch and movement instead of words: offered, paused when a person signals, never "
     "done to somebody. Messy play graded by temperature and texture rather than by "
     "activity \u2014 dry, wet, warm, cool \u2014 and by scent. A theme to go into together: moon "
     "sand, percussion, switch-activated toys placed within reach of the person using them."),
    ("the watering hole",
     "The same materials, shared, with nobody leading. Trays or mats of paint big enough "
     "for more than one person, explored with hands, feet, or whatever part a person "
     "explores with. A hanging rail or a basket of instruments and sensory toys, at a "
     "height people can take from themselves. A projected scene with a scent to match "
     "\u2014 a woodland, a seaside, a winter \u2014 held long enough that people can come into "
     "it, be near each other in it, and leave without the scene ending. What passes "
     "between people here is what they show each other by doing it alongside: a splash, "
     "a sound, a handful of paint somebody then tries."),
]

IMPL_EXAMPLES_GAP = (
    "The source works three zones \u2014 cave, campfire, and watering hole, which are "
    "Thornburg's three. The library and the habitat are Cavendish's own additions, and "
    "it does not work them, so neither does this. That is a gap in the examples, not a "
    "sign the zones don't apply: the habitat in a room like this is the whole sensory "
    "surround the other three sit inside, and it is still the first thing to get steady."
)

IMPL_PLAYMODES = (
    "Two play modes map the rhythm; this book builds the room that lets it happen. Run "
    "Map the edges with the person to find where the crossings bite \u2014 focus to talking, "
    "rest to joining in, home to out the door. Run Moving between to see the shape of a "
    "day, alone to together and back. Then build the padding where the map shows it's "
    "needed. The person maps; you build it with them; the room changes, not the person."
)

# (bold lead, rest, optional url, optional link text -- None prints the bare URL)
IMPL_LINEAGE = [
    ("Physical niche construction in the early years",
     "Helen Edgar. Much of the budget and building practice here comes from twenty "
     "years teaching children with Profound and Multiple Learning Disabilities, where "
     "children and adults shaped the space together. (Credit wording to confirm with Helen.) "
     "Written up with Ryan Boren in",
     PMLD_URL, PMLD_TITLE),
    ("Nesting as the physical architecture of lily padding", "David Gray-Hammond.", None, None),
    ("Lily padding, and transitional trauma for monotropic minds", "Tanya Adkin.", None, None),
    ("Caves, campfires, and watering holes",
     "David Thornburg's learning-space metaphors; the case for cave spaces in schools, "
     "Prakash Nair, The Language of School Design.", None, None),
    ("Cavendish Space, intermittent collaboration, niche construction",
     "Stimpunks Foundation.", "https://stimpunks.org/glossary/lily-pad/", None),
]


def implementation_html(out_families):
    fam_by_slug = {f["slug"]: f for f in out_families}
    sections = []
    for slug in IMPL_ORDER:
        fam = fam_by_slug.get(slug)
        if not fam:
            continue
        note = IMPL_REALM_NOTES.get(slug, "")
        items = []
        if slug == "what-helps":
            for signpost, txt in IMPL_WHATHELPS:
                items.append(
                    f'<article class="gb-entry"><h3>{e(signpost)}</h3><p>{e(txt)}</p></article>')
        else:
            for c in fam["cards"]:
                pair = IMPL_PAIRINGS.get(c["slug"])
                if pair:
                    items.append(
                        f'<article class="gb-entry"><h3>{e(c["name"])}</h3><p>{e(pair)}</p></article>')
        sections.append(
            f'<section class="gb-family" id="build-{slug}"><h2>{e(IMPL_LABELS[slug])}</h2>'
            f'<p class="muted">{e(note)}</p>{"".join(items)}</section>')

    budget_html = (
        f'<section class="gb-family" id="build-budget"><h2>On any budget</h2>'
        f'<p class="muted">{e(IMPL_BUDGET)} For the full material-level how-to, see '
        f'<a href="{BUDGET_URL}">Creating Cavendish Space on a Budget</a> and '
        f'<a href="{NESTING_URL}">Nesting</a>.</p></section>')
    ex_rules = "".join(
        f'<li><strong>{e(t)}.</strong> {e(b)}</li>' for t, b in IMPL_EXAMPLES_RULES)
    ex_items = "".join(
        f'<article class="gb-entry"><h3>{e(name)}</h3><p>{e(txt)}</p></article>'
        for name, txt in IMPL_EXAMPLES)
    examples_html = (
        f'<section class="gb-family" id="build-examples"><h2>{e(IMPL_EXAMPLES_HEAD)}</h2>'
        f'<p class="muted">{e(IMPL_EXAMPLES_INTRO)} See '
        f'<a href="{PMLD_URL}">{e(PMLD_TITLE)}</a>.</p>'
        f'<div class="rules stack" role="note" aria-label="{e(IMPL_EXAMPLES_HEAD)}">'
        f'<p class="rules-lead">{e(IMPL_EXAMPLES_RULES_LEAD)}</p>'
        f'<ul class="rules-list">{ex_rules}</ul></div>'
        f'<p class="muted">{e(IMPL_EXAMPLES_LEAD)}</p>{ex_items}'
        f'<p class="muted">{e(IMPL_EXAMPLES_GAP)}</p></section>')
    play_html = (
        f'<section class="gb-family" id="build-play"><h2>How it pairs with the play modes</h2>'
        f'<p class="muted">{e(IMPL_PLAYMODES)}</p></section>')
    lineage_items = "".join(
        f'<li><strong>{e(lead)}</strong> \u2014 {e(rest)}'
        + (f' <a href="{url}">{e(label)}</a>.' if label
           else f' <a href="{url}">{e(url)}</a>' if url else '')
        + '</li>'
        for lead, rest, url, label in IMPL_LINEAGE)
    lineage_html = (
        f'<section class="gb-family" id="build-lineage"><h2>Lineage</h2>'
        f'<ul class="gb-lineage">{lineage_items}</ul></section>')

    guardrail_boxes = "\n".join(
        f'<div class="rules" role="note" aria-label="{e(t)}"><p><strong>{e(t)}.</strong> {e(b)}</p></div>'
        for t, b in IMPL_GUARDRAILS)

    body = "\n".join(sections + [budget_html, examples_html, play_html, lineage_html])
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {_THEME_INLINE}
  <script src="/theme-toggle.js" defer></script>
  <title>Cavendish Cards — Implementation Guidebook</title>
  <meta name="description" content="How to build the room the cards ask for. The facilitator layer: materials live here, never on a card.">
  <link rel="preload" href="/fonts/AtkinsonHyperlegible-Regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/AtkinsonHyperlegible-Bold.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="styles.css">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <link rel="describedby" type="text/markdown" href="/llms.txt">
  <link rel="alternate" type="text/markdown" href="/implementation.md" title="Implementation guidebook &mdash; Markdown source">
  <meta name="theme-color" content="#fdf6e3" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#002b36" media="(prefers-color-scheme: dark)">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Cavendish Cards">
  <meta name="color-scheme" content="light dark">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="Cavendish">
  <meta name="application-name" content="Cavendish Cards">
  <meta property="og:locale" content="en_US">
  <link rel="license" href="https://creativecommons.org/publicdomain/zero/1.0/">
  {_JSONLD}
  <meta property="og:title" content="Cavendish Space — Implementation Guidebook">
  <meta property="og:description" content="How to build the room the cards ask for. The facilitator layer: materials live here, never on a card.">
  <meta property="og:url" content="https://cavendish.space/implementation.html">
  <link rel="canonical" href="https://cavendish.space/implementation.html">
  <meta property="og:image" content="https://cavendish.space/og-image.png?v=2">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Cavendish Space — a sheltering arch with a hearth inside it, beside the words &quot;Cavendish Space: places built to fit bodyminds, not the other way round.&quot;">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Cavendish Space — Implementation Guidebook">
  <meta name="twitter:description" content="How to build the room the cards ask for. The facilitator layer: materials live here, never on a card.">
  <meta name="twitter:image" content="https://cavendish.space/og-image.png?v=2">
</head>
<body>
  <a class="skip" href="#impl">Skip to the guide</a>
  <script src="/sw-register.js" defer></script>
  {site_topbar("implementation")}
  <header class="site-header">
    <div class="wrap">
      <p class="backlink"><a href="index.html">Cavendish Space</a></p>
      <h1>Implementation Guidebook</h1>
      <p class="intro">{e(IMPL_INTRO)}</p>
      <div class="rules" role="note" aria-label="The one principle">
        <p><strong>The one principle.</strong> {e(IMPL_PRINCIPLE)}</p>
      </div>
      {guardrail_boxes}
    </div>
  </header>
  <main id="impl" class="wrap gb">
{body}
  </main>
  <footer class="site-footer">
    <div class="wrap">
      <p>Free to use, print, and adapt under <a href="https://creativecommons.org/publicdomain/zero/1.0/">CC0 1.0</a>. Part of the <a href="https://stimpunks.org/projects/cavendish-space-project/">Cavendish Space Project</a>. <a href="https://github.com/Stimpunks/Cavendish-Cards">Source on GitHub</a>.</p>
    </div>
  </footer>
</body>
</html>
'''


def implementation_md(out_families):
    fam_by_slug = {f["slug"]: f for f in out_families}
    L = ["# Cavendish Cards — Implementation Guidebook", ""]
    L.append("*How to build the room the cards ask for. Generated from the card files by "
             "`scripts/build-site.py` — do not edit this file by hand; edit the constants "
             "in the script and regenerate.*")
    L += ["", IMPL_INTRO, "", "Facilitator layer. Nothing here goes on a card.", "", "---- ", ""]
    L += ["## The one principle", "", IMPL_PRINCIPLE, ""]
    L += ["## Guardrails", ""]
    L += [f"- **{t}.** {b}" for t, b in IMPL_GUARDRAILS]
    L.append("")
    for slug in IMPL_ORDER:
        fam = fam_by_slug.get(slug)
        if not fam:
            continue
        L += ["---- ", "", f"## {IMPL_LABELS[slug]}", "", IMPL_REALM_NOTES.get(slug, ""), ""]
        if slug == "what-helps":
            L += [f"- **{signpost}** — {txt}" for signpost, txt in IMPL_WHATHELPS]
        else:
            for c in fam["cards"]:
                pair = IMPL_PAIRINGS.get(c["slug"])
                if pair:
                    L.append(f"- **{c['name']}** — {pair}")
        L.append("")
    L += ["---- ", "", "## On any budget", ""]
    L.append(f"{IMPL_BUDGET} For the full material-level how-to, see "
             f"[Creating Cavendish Space on a Budget]({BUDGET_URL}) and [Nesting]({NESTING_URL}).")
    L += ["", f"## {IMPL_EXAMPLES_HEAD}", "",
          f"{IMPL_EXAMPLES_INTRO} See [{PMLD_TITLE}]({PMLD_URL}).", "",
          IMPL_EXAMPLES_RULES_LEAD, ""]
    L += [f"- **{t}.** {b}" for t, b in IMPL_EXAMPLES_RULES]
    L += ["", IMPL_EXAMPLES_LEAD, ""]
    L += [f"- **{name}** \u2014 {txt}" for name, txt in IMPL_EXAMPLES]
    L += ["", IMPL_EXAMPLES_GAP, ""]
    L += ["## How it pairs with the play modes", "", IMPL_PLAYMODES, ""]
    L += ["## Lineage", ""]
    for lead, rest, url, label in IMPL_LINEAGE:
        link = f" [{label}]({url})." if label else (f" {url}" if url else "")
        L.append(f"- **{lead}** — {rest}{link}")
    L += ["", "---- ", ""]
    L.append("Dedicated to the public domain under [CC0 1.0]"
             "(https://creativecommons.org/publicdomain/zero/1.0/). "
             "Home: https://stimpunks.org/projects/cavendish-space-project/")
    L.append("")
    return "\n".join(L)


_SITE_URL = "https://cavendish.space"
_SITE_PAGES = ["/", "/deck.html", "/rooms.html", "/badges.html", "/print.html", "/space.html", "/guidebook.html", "/implementation.html",
               "/why.html", "/not-aac.html", "/origin.html", "/arles.html",
               "/space-time.html", "/inclusive-environment.html", "/facilitator.html",
               "/example-spreads.html", "/place-explorers.html", "/group-needs.html", "/livable-worlds.html",
               "/privacy.html", "/changelog.html"]

# Pre-paint inline script (no flash): applies a saved light/dark choice before
# first paint. Kept byte-identical to the copy in web/index.html and to the CSP
# hash in netlify.toml — if you change it, update both.
_THEME_INLINE = "<script>(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>"


_JSONLD = ('<script type="application/ld+json">\n'
           '{"@context":"https://schema.org","@graph":['
           '{"@type":"WebSite","@id":"https://cavendish.space/#website",'
           '"name":"Cavendish Cards","url":"https://cavendish.space/",'
           '"description":"A calm, no-scoring deck for naming sensory and '
           'interaction needs.","inLanguage":"en",'
           '"license":"https://creativecommons.org/publicdomain/zero/1.0/",'
           '"publisher":{"@id":"https://stimpunks.org/#organization"}},'
           '{"@type":"Organization","@id":"https://stimpunks.org/#organization",'
           '"name":"Stimpunks Foundation","url":"https://stimpunks.org/",'
           '"sameAs":["https://github.com/Stimpunks/Cavendish-Cards"]}]}\n'
           '</script>')


def _check_signpost_parity():
    """Warn when GROUPS and IMPL_WHATHELPS disagree about the signposts.

    They are two hand-kept lists of the same taxonomy: GROUPS decides which
    signpost a card appears under in the deck's What helps view, IMPL_WHATHELPS
    carries the build guidance for that signpost in the implementation
    guidebook. Nothing joins them, because IMPL_WHATHELPS holds prose rather
    than card slugs -- so a signpost added to one and not the other is silently
    wrong in a way no rebuild surfaces: the deck grows a heading with no
    guidance behind it, or the guidebook keeps explaining a signpost the deck
    no longer has. Order is compared too, since the two lists render
    independently and are meant to read in the same sequence.

    Non-fatal, like the COND check: a mismatch should not stop a deploy, but it
    should be impossible to miss in the build output.
    """
    in_groups = [name for name, _ in GROUPS.get("what-helps", [])]
    in_impl = [name for name, _ in IMPL_WHATHELPS]
    missing = [n for n in in_groups if n not in in_impl]
    extra = [n for n in in_impl if n not in in_groups]
    for n in missing:
        print(f"  ! signpost {n!r} is in GROUPS but has no IMPL_WHATHELPS entry "
              f"(the implementation guidebook will not mention it)", file=sys.stderr)
    for n in extra:
        print(f"  ! IMPL_WHATHELPS explains {n!r}, which is not a signpost in GROUPS",
              file=sys.stderr)
    if not missing and not extra and in_groups != in_impl:
        print(f"  ! the signposts match but are in a different order: GROUPS has "
              f"{in_groups}, IMPL_WHATHELPS has {in_impl}", file=sys.stderr)
    return len(in_groups), len(in_impl)


def _check_cond_parity(root, web):
    """Warn when the group-brief page and rooms.js disagree about the conditions.

    The 17 COND ids in web/rooms.js stopped being private the moment
    cavendish-cards-group-needs.md started telling coordinators (and their AI)
    to map needs into them, and rooms.html#asked=<ids> started carrying them in
    a link. Rename one in the JS and the doc silently teaches an id that no
    longer resolves, which surfaces as a need quietly dropped from somebody's
    brief -- exactly the failure the page is written to prevent.

    Non-fatal, like the missing-face warning: a stale doc should not stop a
    deploy, but it should be impossible to miss in the build output.
    """
    conds = _cond_map(web)
    doc_path = root / "cavendish-cards-group-needs.md"
    if not conds or not doc_path.exists():
        print("  ! could not check COND parity (rooms.js or the group-brief doc moved)",
              file=sys.stderr)
        return
    in_js = set(conds)
    in_doc = set(re.findall(r"^- `([a-z-]+)`", doc_path.read_text(encoding="utf-8"), re.M))
    for k in sorted(in_js - in_doc):
        print(f"  ! condition {k!r} is in rooms.js but not in the group-brief doc",
              file=sys.stderr)
    for k in sorted(in_doc - in_js):
        print(f"  ! the group-brief doc lists {k!r}, which rooms.js has no condition for",
              file=sys.stderr)
    return len(in_js), len(in_doc)


def _check_group_example(root):
    """Warn when the group-brief page's worked example breaks its own rules.

    Twice now the example has contradicted the prose above it: once listing the
    room conditions in arrival order, which the ordering rule forbids, and once
    opening a line with a person as its subject, which rule two forbids. Prose
    examples are the part of a page nobody proofreads against the page, and the
    example is the part a reader copies. Non-fatal, like the other warnings.
    """
    doc = (root / "cavendish-cards-group-needs.md").read_text(encoding="utf-8")
    order, label = [], {}
    for cid, text, _src in re.findall(
            r"^- `([a-z-]+)` \u2014 ([^.]+)\. From: ([^.]+)\.", doc, re.M):
        order.append(cid)
        label[text.strip()] = cid
    m = re.search(r"^- \*\*The room needs\*\* \u2014 (.+)$", doc, re.M)
    if not m or not order:
        print("  ! could not check the group-brief example", file=sys.stderr)
        return
    ids = [label.get(x.strip()) for x in m.group(1).split(" \u00b7 ")]
    if None in ids:
        print("  ! the group-brief example names a condition that is not in its own "
              "table", file=sys.stderr)
    else:
        pos = [order.index(i) for i in ids]
        if pos != sorted(pos):
            print("  ! the group-brief example lists conditions out of the page's own "
                  "order, which the ordering rule forbids", file=sys.stderr)
        link = re.search(r"\*\*A link to the zoner\*\* \u2014 \S+#asked=([a-z,-]+)", doc)
        if link and link.group(1).split(",") != ids:
            print("  ! the group-brief example's link does not match its own room list",
                  file=sys.stderr)
    # Rule two: no output line takes a person as its subject.
    for line in re.findall(r"^- \*\*[^*]+\*\* \u2014 (.+)$", doc, re.M):
        first = line.strip().split()[0].lower().strip('"')
        if first in ("someone", "somebody", "people", "they", "he", "she", "a person"):
            print(f"  ! a group-brief example line takes a person as its subject: "
                  f"{line[:60]!r}", file=sys.stderr)


# robots.txt, written deliberately rather than left to a blanket rule. The
# values call behind it (2026-09-17, Ryan's, logged for Helen's batch review):
# the deck is CC0, and llms.txt already steers models rather than shutting them
# out, so blocking AI crawlers would contradict a file this same generator
# writes. Naming each agent is what makes the openness legible as a choice.
#
# The vendor docs are the source of truth for these names and they change --
# re-check them rather than trusting this list's age. See
# https://specification.website/spec/agent-readiness/robots-for-ai-crawlers/
AI_CRAWLERS = [
    ("GPTBot", "OpenAI, training."),
    ("OAI-SearchBot", "OpenAI, retrieval for ChatGPT browsing."),
    ("ChatGPT-User", "OpenAI, on-demand fetch when someone asks ChatGPT for a URL."),
    ("ClaudeBot", "Anthropic, training and retrieval."),
    ("anthropic-ai", "Anthropic, legacy name, still seen."),
    ("Google-Extended", "Google. Covers Gemini and Vertex training only, not Search."),
    ("Applebot-Extended",
     "Apple. Covers Apple Intelligence training only, not Siri or Spotlight."),
    ("PerplexityBot", "Perplexity, retrieval."),
    ("Bytespider", "ByteDance."),
    ("CCBot", "Common Crawl, the dataset behind many open models."),
]

_ROBOTS_PREAMBLE = """\
# cavendish.space -- Cavendish Space, by Stimpunks Foundation.
#
# Everything here is CC0: dedicated to the public domain. So every crawler is
# allowed, AI crawlers included, and each one is named below rather than left to
# a blanket rule -- the openness here is chosen, not defaulted into.
#
# The reasoning, plainly: if a model is going to say something about Autistic and
# Disabled people, we would rather it had read this deck than not. A spread of
# cards is a design brief for the environment, not a report on a person. Cards
# describe the card, never the person. Broken systems, not broken people.
#
# /llms.txt is a curated index written for that purpose, and every prose page is
# also served as Markdown -- swap .html for .md.
#
# Nothing here is a security boundary, and none of it is a deletion request:
# what is already in a training set stays there. It is a statement of welcome.
"""


# Prose documents that cite cards as examples. The guidebook is deliberately not
# here: its card names come from cards/** beside the card they describe, so a
# name in a Notes field is authored next to its own source and cannot drift.
_CARD_CITING_DOCS = [
    "cavendish-cards-facilitator-sheet.md",
    "cavendish-cards-starter-deck.md",
    "cavendish-cards-example-spreads.md",
    "cavendish-cards-place-explorers.md",
    "cavendish-cards-livable-worlds.md",
    "cavendish-cards-group-needs.md",
    "cavendish-cards-why-sheet.md",
    "cavendish-cards-not-aac.md",
    "cavendish-cards-inclusive-environment.md",
    "cavendish-cards-space-time.md",
]

# Words that claim a realm, mapped to the family they claim. Used to check that a
# list introduced as "lay a lily pad -- x, y, z" holds only lily pads.
_REALM_WORDS = {
    "lily pad": "lily-pad", "lily-pad": "lily-pad",
    "what-helps": "what-helps", "what helps": "what-helps",
    "weather card": "weather", "weather": "weather",
    "interaction card": "interaction",
    "kind word": "love-locution", "love locution": "love-locution",
    "grower": "grower",
    "place card": "places",
}


def _check_card_citations(root, out_families):
    """Warn when a prose document cites a card that does not exist, or puts a
    real card in the wrong realm.

    Every one of these errors reached print: "map the edges" told a facilitator
    to lay a lily pad and listed `tell me first`, which is What helps; another
    mode listed `a minute alone`, which is no card at all. They survived because
    prose gets read against itself and never against the deck.

    Three checks, all high-precision on purpose -- a noisy warning is one nobody
    reads:

      A. An italic list where some items are cards and some are not. Mixed lists
         are card citations, so the odd one out is a mistake rather than prose.
      B. An italic list introduced by a word claiming a realm, holding a card
         from a different realm.
      C. A near-miss differing from a real card only by its leading article
         (`cave` for `the cave`, `the den` for `a den`).

    What it cannot catch: an invented phrase in plain prose, with no italics and
    no realm word near it. `a minute alone` was found by reading. Non-fatal,
    like the other warnings here.
    """
    realms = {}
    for fam in out_families:
        for c in fam["cards"]:
            realms.setdefault(c["name"], set()).add(fam["slug"])
    articles = ("the ", "a ", "an ")

    def variants(name):
        bare = name
        for a in articles:
            if name.startswith(a):
                bare = name[len(a):]
        return {bare} | {a + bare for a in articles}

    near = {}
    for name in realms:
        for v in variants(name):
            if v not in realms:
                near.setdefault(v, set()).add(name)

    for rel in _CARD_CITING_DOCS:
        path = root / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for m in re.finditer(r"\*([^*\n]+)\*", text):
            items = [i.strip().strip(".").strip() for i in m.group(1).split(",")]
            items = [i for i in items
                     if i and i == i.lower() and len(i) < 30
                     and "\u2014" not in i and "\u2013" not in i]
            if len(items) < 2:
                continue
            hits = [i for i in items if i in realms]
            if not hits:
                continue
            for i in items:
                if i in realms:
                    continue
                if i in near:
                    print(f"  ! {rel}: cites {i!r}; the card is "
                          f"{' or '.join(repr(n) for n in sorted(near[i]))}",
                          file=sys.stderr)
                else:
                    print(f"  ! {rel}: {i!r} is listed beside real cards but is "
                          f"not a card", file=sys.stderr)
            # B: a realm word just before the list constrains every item in it.
            lead = text[max(0, m.start() - 40):m.start()].lower()
            claimed = None
            for word, fam in _REALM_WORDS.items():
                tail = lead.rsplit(word, 1)
                if len(tail) == 2 and re.fullmatch(r"[\s\u2014\u2013:\-]{0,4}", tail[1]):
                    claimed = fam
            if claimed:
                for i in hits:
                    if claimed not in realms[i]:
                        print(f"  ! {rel}: {i!r} is listed as a {claimed!r} card "
                              f"but belongs to {'/'.join(sorted(realms[i]))}",
                              file=sys.stderr)


# ---------------------------------------------------------------------------
# Print-and-play sheets (print.html)
#
# The deck at its real size, imposed for cutting. Everything here is fixed:
# there is nothing to choose, because a deck is a deck. The only number that
# matters is the card, and it is the standard playing-card size the deck has
# always been drawn at -- 2.5 x 3.5 in, which is what the 750 x 1050 face
# viewBox is at 300dpi.
#
# The sheet is exactly the 3x3 grid and no more: 7.5 x 10.5 in. That is the one
# geometry that fits BOTH US Letter and A4 inside a quarter-inch margin, so
# there is no paper-size control and no second set of files. Letter is the
# tight one -- 11in less two quarter-inch margins is 10.5in exactly, with
# nothing to spare -- which the page says out loud, because a printer that
# cannot reach 0.25in of the short edge will shave the bottom row.
#
# Sheets never mix realms. It costs four sheets across the deck and buys the
# thing a control would otherwise have to buy: printing one realm is choosing
# its pages in the print dialog.
PRINT_CARD_W, PRINT_CARD_H = 180, 252          # 2.5 x 3.5 in, in points
PRINT_COLS, PRINT_ROWS = 3, 3
PRINT_SHEET_W = PRINT_CARD_W * PRINT_COLS      # 540pt = 7.5in
PRINT_SHEET_H = PRINT_CARD_H * PRINT_ROWS      # 756pt = 10.5in
PRINT_PER_SHEET = PRINT_COLS * PRINT_ROWS
PRINT_CUT = "#c9c2ad"


def _nest_svg(svg_text, x, y, w, h, uid):
    """Drop one card's SVG into a sheet at (x, y), scaled to w x h.

    Two things have to happen. The root <svg> gets position and size while
    keeping its own viewBox, which is what makes a 750x1050 face render at
    180x252pt. And every id is namespaced, because nine cards on a sheet means
    nine copies of `art-window` in one document and `url(#art-window)` resolves
    to whichever came first -- harmless today, since every card's clip is the
    same rectangle, and a trap the moment one card's differs.
    """
    body = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg_text)
    body = re.sub(r'\sid="([^"]+)"', lambda m: f' id="{uid}-{m.group(1)}"', body)
    body = re.sub(r"url\(#([^)]+)\)", lambda m: f"url(#{uid}-{m.group(1)})", body)
    body = re.sub(
        r"<svg\b[^>]*>",
        f'<svg x="{x}" y="{y}" width="{w}" height="{h}" viewBox="0 0 750 1050" '
        f'preserveAspectRatio="xMidYMid meet">',
        body, count=1)
    return body


def _card_bg(svg_text):
    """The card's own paper color, read off its full-bleed base rect.

    Cards butt against each other on a sheet, so a straight cut runs through
    the rounded corners a face draws. Without something behind them each cut
    card comes away with four white notches. Painting the card's own color into
    the slot first fills them, and the rounding stops mattering -- square-cut or
    corner-rounded, the card is solid to its edge either way. Read rather than
    assumed: two backs and one card use a different paper.
    """
    m = re.search(r'<rect[^>]*width="750"[^>]*height="1050"[^>]*fill="([^"]+)"',
                  svg_text)
    return m.group(1) if m else "#eee8d5"


def _cut_grid():
    """Hairlines on every card boundary, so a ruler has something to follow.

    Drawn as full-length lines rather than a box per card: the cuts that matter
    run the whole way across, and a shared edge should be one line rather than
    two that can disagree by a hair.
    """
    out = []
    for c in range(PRINT_COLS + 1):
        x = c * PRINT_CARD_W
        out.append(f'<line x1="{x}" y1="0" x2="{x}" y2="{PRINT_SHEET_H}" '
                   f'stroke="{PRINT_CUT}" stroke-width="0.5"/>')
    for r in range(PRINT_ROWS + 1):
        y = r * PRINT_CARD_H
        out.append(f'<line x1="0" y1="{y}" x2="{PRINT_SHEET_W}" y2="{y}" '
                   f'stroke="{PRINT_CUT}" stroke-width="0.5"/>')
    return "".join(out)


def _sheet_open(label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="7.5in" height="10.5in" '
            f'viewBox="0 0 {PRINT_SHEET_W} {PRINT_SHEET_H}" role="img" '
            f'aria-label="{e(label)}">'
            f'<rect x="0" y="0" width="{PRINT_SHEET_W}" height="{PRINT_SHEET_H}" '
            f'fill="#ffffff"/>')


def _slot_bg(x, y, fill):
    return (f'<rect x="{x}" y="{y}" width="{PRINT_CARD_W}" height="{PRINT_CARD_H}" '
            f'fill="{fill}"/>')


def _slot_xy(i):
    return ((i % PRINT_COLS) * PRINT_CARD_W, (i // PRINT_COLS) * PRINT_CARD_H)


def print_sheets(out_families, faces):
    """Impose the whole deck, one realm at a time, nine cards to a sheet.

    Returns a list of dicts: realm label, the face sheet, the matching back
    sheet, and the card names on it. A realm's cards all share one back, so a
    back sheet is the same image nine times and needs no mirroring for duplex
    -- whichever way the paper turns over, every slot is already right.
    """
    sheets = []
    for fam in out_families:
        cards = fam["cards"]
        for start in range(0, len(cards), PRINT_PER_SHEET):
            chunk = cards[start:start + PRINT_PER_SHEET]
            n = len(sheets) + 1
            label = (f"{fam['name']} — sheet {start // PRINT_PER_SHEET + 1}"
                     if len(cards) > PRINT_PER_SHEET else fam["name"])

            faces_svg = [_sheet_open(f"Cavendish Cards, {label}: nine card faces "
                                     f"laid out for cutting.")]
            backs_svg = [_sheet_open(f"Cavendish Cards, {label}: the matching "
                                     f"card backs.")]
            back_file = chunk[0]["back"].split("/")[-1]
            back_svg = (faces / back_file).read_text(encoding="utf-8")
            for i, card in enumerate(chunk):
                x, y = _slot_xy(i)
                face = (faces / card["face"].split("/")[-1]).read_text(encoding="utf-8")
                faces_svg.append(_slot_bg(x, y, _card_bg(face)))
                faces_svg.append(_nest_svg(face, x, y, PRINT_CARD_W, PRINT_CARD_H,
                                           f"s{n}c{i}"))
                backs_svg.append(_slot_bg(x, y, _card_bg(back_svg)))
                backs_svg.append(_nest_svg(back_svg, x, y, PRINT_CARD_W, PRINT_CARD_H,
                                           f"b{n}c{i}"))
            grid = _cut_grid()
            sheets.append({
                "n": n,
                "label": label,
                "realm": fam["name"],
                "slug": f"{n:02d}-{fam['slug']}",
                "count": len(chunk),
                "names": [c["name"] for c in chunk],
                "faces": "".join(faces_svg) + grid + "</svg>",
                "backs": "".join(backs_svg) + grid + "</svg>",
            })
    return sheets


def _write_print_sheets(web, sheets):
    """Write each sheet as a standalone SVG under web/print/.

    The page already carries every sheet inline, so these exist for one reason:
    handing a file to somebody, or to a print shop, without asking them to
    print a web page.
    """
    out = web / "print"
    if out.is_dir():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    for s in sheets:
        (out / f"faces-{s['slug']}.svg").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n' + s["faces"], encoding="utf-8")
        (out / f"backs-{s['slug']}.svg").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n' + s["backs"], encoding="utf-8")


def print_html(sheets, total_cards):
    """The print-and-play page: the whole deck, imposed, with nothing to set."""
    pages = len(sheets)
    realms = []
    for s in sheets:
        if not realms or realms[-1][0] != s["realm"]:
            realms.append([s["realm"], [s["n"]]])
        else:
            realms[-1][1].append(s["n"])
    realm_rows = "".join(
        "<li><strong>{}</strong> &mdash; {}</li>".format(
            e(name),
            "sheet " + str(ns[0]) if len(ns) == 1
            else f"sheets {ns[0]}&ndash;{ns[-1]}")
        for name, ns in realms)

    face_blocks = "".join(
        f'<figure class="print-sheet" id="sheet-{s["n"]}">'
        f'<div class="print-paper">{s["faces"]}</div>'
        f'<figcaption><span class="print-sheet-title">Sheet {s["n"]} &middot; '
        f'{e(s["label"])}</span> <span class="muted">{s["count"]} '
        f'{"card" if s["count"] == 1 else "cards"}</span> '
        f'<a class="btn ghost small" href="print/faces-{s["slug"]}.svg" download>'
        f'Download</a></figcaption></figure>'
        for s in sheets)

    back_blocks = "".join(
        f'<figure class="print-sheet print-back">'
        f'<div class="print-paper">{s["backs"]}</div>'
        f'<figcaption><span class="print-sheet-title">Backs for sheet {s["n"]}'
        f'</span> <span class="muted">{e(s["realm"])}</span> '
        f'<a class="btn ghost small" href="print/backs-{s["slug"]}.svg" download>'
        f'Download</a></figcaption></figure>'
        for s in sheets)

    body = f'''
      <section class="rooms-intro">
        <h2>The whole deck, at the size it is drawn</h2>
        <p class="intro">{total_cards} cards on {pages} sheets, nine to a page, at
          <strong>2.5 &times; 3.5 in</strong> (63.5 &times; 88.9 mm) &mdash; standard
          playing-card size. They fit a normal card sleeve, a normal card box, and a
          normal hand.</p>
        <p class="intro">There is nothing to choose on this page. A deck is a deck:
          same cards, same size, same order every time. Print it, cut it, use it.</p>
        <div class="rules stack">
          <p class="rules-lead"><strong>Before you print.</strong></p>
          <ul class="rules-list">
            <li><strong>Set the scale to 100%,</strong> not &ldquo;fit to page.&rdquo;
              This is the one that goes wrong. Browsers shrink by default, and a deck
              printed at 94% no longer fits a sleeve or a box.</li>
            <li><strong>Set margins to Minimum or None.</strong> A sheet is 7.5 &times;
              10.5 in, which fits US Letter and A4 alike inside a quarter-inch margin
              &mdash; the same file for both, no setting to pick.</li>
            <li><strong>US Letter is the tight one.</strong> Eleven inches less two
              quarter-inch margins is 10.5 exactly, with nothing spare. If your printer
              cannot reach within a quarter inch of the short edge it will shave the
              bottom row. A4 has three-quarters of an inch to spare; use it if you have
              it, or print the bottom row's sheet again on a printer that can.</li>
            <li><strong>Use card, not paper.</strong> 250&ndash;300 gsm (about
              90&ndash;110 lb cover) handles like a card and survives being laid out and
              swept up a hundred times. Plain paper curls by the second session.</li>
          </ul>
        </div>
        <div class="rooms-actions">
          <button type="button" class="btn" id="print-faces">Print the {pages} sheets</button>
          <button type="button" class="btn ghost" id="print-both">Print faces and backs</button>
        </div>
        <p class="muted rooms-note" id="print-note">No JavaScript? These buttons only
          set the page size for you. Print the page from your browser&rsquo;s own menu
          instead, with margins at 0.25 in (6 mm) and scale at 100%.</p>
      </section>

      <section class="rooms-step">
        <h2 id="whats-here">What is on which sheet</h2>
        <p class="intro">A sheet never mixes realms. That costs a few part-full pages
          across the deck and buys the thing this page would otherwise need a control
          for: <strong>to print one realm, print its pages.</strong></p>
        <ul class="print-contents">{realm_rows}</ul>
      </section>

      <section class="rooms-step print-sheets-section">
        <h2 id="sheets">The sheets</h2>
        <div class="print-sheets">{face_blocks}</div>
      </section>

      <section class="rooms-step">
        <h2 id="cutting">Cutting</h2>
        <ul class="badges-list">
          <li>The hairlines are the cuts. They run the full width and height of the
            sheet, so every cut is one straight line through three cards at once.</li>
          <li><strong>Cut the rows first, then the columns.</strong> Three long cuts
            each way turns a sheet into nine cards, and the cards stay square. Cutting
            one card out at a time is how a deck ends up with nine different sizes.</li>
          <li>A guillotine or a rotary trimmer beats scissors, and a metal ruler with a
            craft knife beats both for a single sheet.</li>
          <li><strong>Optional:</strong> a corner rounder, 3 mm radius. It is the
            difference between cards that look homemade and cards that look made, and it
            stops the corners going furry.</li>
        </ul>
      </section>

      <section class="rooms-step print-backs-section">
        <h2 id="backs">The backs, if you want them</h2>
        <p class="intro">You do not need these. <strong>The deck's privacy rule is that
          face-down cards are indistinguishable</strong> &mdash; a spread must not leak
          before its person turns a card up &mdash; and blank card stock does that
          perfectly well. Print backs only if you want the finished object.</p>
        <p class="intro">If you do: every card in a realm shares one back, so a back
          sheet is the same image nine times. That means <strong>alignment cannot go
          wrong</strong> &mdash; it does not matter which way the paper turns over.
          Print the faces, feed the stack back in, print the matching back sheet, and
          check one card against the light before you run the rest.</p>
        <p class="intro">Two realms carry their own back on purpose, and both are realms
          that are never laid face-down: <strong>Kind words</strong>, which is given or
          claimed, and <strong>Interaction</strong>, which is worn and shown. Everything
          else shares the standard back. That is why a distinct back is safe for those
          two and nowhere else.</p>
        <details class="disclose" id="print-backs-details">
          <summary>Show the {pages} back sheets</summary>
          <div class="print-sheets">{back_blocks}</div>
        </details>
      </section>

      <section class="rooms-step">
        <h2 id="next">Then what</h2>
        <ul class="rooms-next">
          <li><a href="guidebook.html">The guidebook</a> &mdash; every card, what it
            names, and how to hold it. Print it or keep it open beside the deck.</li>
          <li><a href="facilitator.html">The facilitator sheet</a> &mdash; for whoever
            is holding the space, with the play modes on it.</li>
          <li><a href="badges.html">Interaction badges</a> &mdash; the one realm meant
            to be worn rather than laid down, at conference badge size.</li>
          <li><a href="deck.html">The web deck</a> &mdash; the same cards, if you would
            rather not print anything at all.</li>
        </ul>
      </section>
'''
    return _standalone_page(
        "Print the deck",
        f"Print the whole Cavendish Cards deck at standard playing-card size "
        f"— {total_cards} cards on {pages} sheets, nine to a page, ready to cut. "
        f"Nothing to set up, no account, free and CC0.",
        "sheets", "Skip to the sheets", "Print the deck", "print", body,
        tagline="The whole deck at playing-card size, nine to a sheet, ready to "
                "cut. Nothing to choose, because a deck is a deck.",
        script="print.js")


def _write_sitemap_robots(web):
    """Write web/sitemap.xml and web/robots.txt from the known page list."""
    import datetime
    today = datetime.date.today().isoformat()
    urls = "\n".join(
        f"  <url><loc>{_SITE_URL}{p}</loc><lastmod>{today}</lastmod></url>"
        for p in _SITE_PAGES)
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
               + urls + "\n</urlset>\n")
    (web / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    groups = "".join(f"# {note}\nUser-agent: {agent}\nAllow: /\n\n"
                     for agent, note in AI_CRAWLERS)
    robots = (_ROBOTS_PREAMBLE + "\n"
              + groups
              + "# Everything else.\n"
              "User-agent: *\n"
              "Allow: /\n\n"
              f"Sitemap: {_SITE_URL}/sitemap.xml\n")
    (web / "robots.txt").write_text(robots, encoding="utf-8")


def _git_date(root, filename):
    """Last commit date (YYYY-MM-DD) for a repo file, or None if git can't say.
    Used for the `updated` field in .md frontmatter -- the build date would be a
    lie on every deploy that didn't touch the file."""
    import subprocess
    try:
        r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", filename],
                           cwd=str(root), capture_output=True, text=True, timeout=15)
        return r.stdout.strip() or None
    except Exception:
        return None


# What dates a generated page: the cards it is built from, plus the generator
# that renders it (a constant edited there changes the output too). ISO dates
# sort lexicographically, so max() is the newest. Erring newer is the safe
# direction -- it tells a caller to re-fetch, where erring older would tell it
# nothing changed when something did.
GENERATED_FROM = {
    "guidebook": ["cards", "scripts/build-guidebook.py"],
    "implementation": ["cards", "scripts/build-site.py"],
    "place-explorers": ["cards", "cavendish-cards-place-explorers.md",
                        "scripts/build-site.py"],
    # Not built from cards/**: the figure, the table and the room-condition
    # mapping come from SPACE_TIME in the generator, and the conditions'
    # wording comes from rooms.js.
    "space-time": ["cavendish-cards-space-time.md", "web/rooms.js",
                   "scripts/build-site.py"],
}


def _write_md_endpoints(root, web, generated):
    """Publish each Markdown-sourced page at web/<key>.md with frontmatter.

    Same build, same source as the HTML, so the two representations cannot
    drift. Frontmatter carries only what an agent can use: title, the canonical
    HTML URL, the last-changed date, and the licence.

    `generated` maps the keys whose MD_ENDPOINTS value is None to their
    already-built Markdown, for pages with no file in the repo root to copy."""
    import datetime
    written = []
    for key, source in sorted(MD_ENDPOINTS.items()):
        label, href = nav_entry(key)
        if source is None:
            body = generated[key]
            dates = [d for d in (_git_date(root, path)
                                 for path in GENERATED_FROM[key]) if d]
            updated = max(dates) if dates else datetime.date.today().isoformat()
        else:
            body = (root / source).read_text(encoding="utf-8")
            updated = _git_date(root, source) or datetime.date.today().isoformat()
        fm = [
            "---",
            f'title: "{label}"',
            f"url: {_SITE_URL}/{href}",
            f"updated: {updated}",
            "license: CC0-1.0",
            "license_url: https://creativecommons.org/publicdomain/zero/1.0/",
            "---",
            "",
        ]
        (web / f"{key}.md").write_text("\n".join(fm) + body, encoding="utf-8")
        written.append(f"{key}.md")
    return written


# llms.txt descriptions, keyed by SITE_NAV key. The GROUPING and the ORDER
# both come from SITE_NAV -- this is only the one-line gloss per page, which is
# the part llms.txt needs and the menu does not. One taxonomy, so the site
# cannot present itself to a person in one shape and to a model in another.
#
# A key with no entry here is left out of llms.txt: `home` is the only one, and
# it is the page every other link already leads back to. Keep the descriptions
# plain; models quote them.
_LLMS_DESCRIPTIONS = {
    "deck": "The card player. Lay a spread face-down; turning a card up is the consent.",
    "rooms": "Zone a room into cave, campfire, watering hole, library, and habitat.",
    "badges": "Make, print, and assemble interaction badges at conference badge size — the green/yellow/red communication badges from Autistic space, plus bulk print and assembly instructions.",
    "print": "Print the whole deck at standard playing-card size: every card, nine to a sheet, ready to cut. Nothing to configure.",
    "guidebook": "Every card in the deck: the metaphor, what it names, and how to hold it. The whole deck in one document.",
    "implementation": "Turning a spread into changes to the room, on any budget.",
    "facilitator": "The sheet for whoever is holding the space. Also a print PDF.",
    "example-spreads": "Worked examples: a spread someone laid, and how to read it as a design brief.",
    "place-explorers": "The five places in children's words, ages about 7 to 11: cave, campfire, watering hole, library, habitat, each shown as its real card face, with a classroom example — plus what to do when the place a child needs isn't in the room. A place is somewhere a person can be, never a state a child is sorted into.",
    "group-needs": "Many spreads at once: how to turn a group's access needs into one brief for the room, including the rules an AI must follow to do it without profiling anyone.",
    "livable-worlds": "A checklist for building spaces that fit bodyminds.",
    "space": "What a Cavendish Space is: the five zones, the eleven elements, what the model refuses.",
    "why": "Why the deck exists, who it serves, and the stance behind it.",
    "not-aac": "Why the deck is not AAC and must never be offered in place of it: what each one is for, the inclusion test that keeps them apart, and how they work together.",
    "origin": "The Cavendish Space model, its lineage, and who Cavendish was.",
    "arles": "How the deck fits the Stimpunks Design Method, and why it stops short of Systems as cards.",
    "space-time": "SPACE-TIME, Helen Edgar's monotropism-informed framework: nine things a place has to hold — Sensory attunement, Predictability and place, Acceptance and agency, Communication and connection, Empathy, then Togetherness, Insiderness, Meaning-making, Embodiment — with the framework table, and which cards and room conditions answer each one. It is a brief for building a place, never a scale to score a person on.",
    "inclusive-environment": "The seven layers an environment is built in, from nervous system out to policy and power, what each asks for, and where the deck reaches. Inclusion as architecture rather than accommodation, and the two layers the deck deliberately stops short of.",
    "privacy": "What the site keeps, which is almost nothing.",
    "changelog": "What changed in the deck and the site, newest first.",
}

_LLMS_SUMMARY = (
    "Free, CC0, neuroaffirming prompt cards and room-zoning tools from Stimpunks "
    "Foundation. A person of any age shows how they feel and what they need by "
    "pointing at or laying pictures — no reading required, no scoring, no "
    "matching, no right answer, no winning."
)

_LLMS_BODY = [
    "Cavendish Space holds three things: a pictorial card deck, a tool for zoning a "
    "room into the five Cavendish zones, and the model behind both. Everything here "
    "is dedicated to the public domain under CC0 1.0. The deck's art is to be human- "
    "and community-made — no AI-generated images, ever. Most of it has yet to be "
    "drawn, so until a human piece arrives a card carries a placeholder illustration "
    "hand-written as vector shapes in the project's own code, replaced automatically "
    "the moment real art lands. The call for art is open.",

    "Two things it is not, because it gets mistaken for both. It is **not a "
    "screening or assessment tool**: nothing is scored, normed, or recorded. It is "
    "**not an AAC board**: a card earns its place by naming a hard-to-voice inner "
    "state or a needed change to the environment *and* carrying a reframe, so "
    "\"can't tell\" belongs and \"hungry\" does not. The deck sits alongside real AAC "
    "and never replaces it.",

    "The framing that matters for anything you generate from this: a spread of "
    "cards is a design brief for the environment, not a report on a person. Cards "
    "describe the card, never the person. Broken systems, not broken people.",
]


def _write_llms_txt(web):
    """Write web/llms.txt per the llms.txt v2 convention."""
    L = ["# Cavendish Space", "", f"> {_LLMS_SUMMARY}", ""]
    for para in _LLMS_BODY:
        L += [para, ""]
    L += ["Every prose page listed below is also served as Markdown: swap `.html` for "
          "`.md` on its URL, or use the `.md` links here. The full card data is at "
          f"{_SITE_URL}/cards.json, and the source lives at "
          "https://github.com/Stimpunks/Cavendish-Cards.", ""]
    # A grouped page with no description silently vanishes from llms.txt, which
    # is the failure the one-taxonomy change exists to prevent -- so say so.
    # Non-fatal, like the other warnings here; watch the build output.
    for _l, _h, key, group in SITE_NAV:
        if group and key not in _LLMS_DESCRIPTIONS:
            print(f"  ! llms.txt: no description for {key!r}; it will be left out",
                  file=sys.stderr)
    for heading, entries in nav_groups():
        listed = [(lbl, hrf, k) for lbl, hrf, k in entries
                  if k in _LLMS_DESCRIPTIONS]
        if not heading or not listed:
            continue
        L += [f"## {heading}", ""]
        for label, href, key in listed:
            rel = md_path(key) or f"/{href}"
            L.append(f"- [{label}]({_SITE_URL}{rel}): {_LLMS_DESCRIPTIONS[key]}")
        L.append("")
    (web / "llms.txt").write_text("\n".join(L), encoding="utf-8")


def _write_security_txt(web):
    """Write web/.well-known/security.txt (RFC 9116).

    Expires is required, and a lapsed one makes the file invalid -- so it is
    computed at build time rather than hard-coded, and every deploy pushes it
    out again. RFC 9116 asks for less than a year, so this uses 330 days: under
    the limit, with the most lapse headroom that leaves. The remaining risk is
    ~11 months with no deploy at all; if that becomes likely, add a scheduled
    Netlify build or a calendar reminder.

    Contact is the Foundation's published address, which is a monitored mailbox.
    Deliberately NOT listing the GitHub advisory URL: private vulnerability
    reporting is disabled on the repo, so that link would dead-end a reporter.
    """
    import datetime
    expires = (datetime.datetime.now(datetime.timezone.utc)
               + datetime.timedelta(days=330)).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        "# Security contact for cavendish.space, per RFC 9116.",
        "# Generated by scripts/build-site.py -- Expires refreshes on every deploy.",
        "",
        "Contact: mailto:stimpunks@stimpunks.org",
        f"Expires: {expires}",
        "Preferred-Languages: en",
        f"Canonical: {_SITE_URL}/.well-known/security.txt",
        f"Policy: {_SITE_URL}/privacy.html",
        "",
    ]
    # Written to the site root, NOT web/.well-known/: Netlify's deploy does not
    # publish dot-directories from the publish dir (verified against the live
    # site -- /.well-known/security.txt 404'd while every sibling file served).
    # web/_redirects rewrites the canonical well-known path here with a 200, so
    # the RFC 9116 location is what actually answers.
    (web / "security.txt").write_text("\n".join(lines), encoding="utf-8")


def _write_service_worker(root, web, faces):
    """Generate web/sw.js from scripts/sw-template.js, version-stamped from the
    shell files + face inventory so a new deploy evicts old caches. No deps."""
    template = (Path(__file__).resolve().parent / "sw-template.js").read_text(
        encoding="utf-8")
    face_names = sorted(p.name for p in faces.glob("*.svg"))
    font_names = sorted(p.name for p in (web / "fonts").glob("*.woff2"))
    h = hashlib.sha1()
    for name in ("index.html", "deck.html", "styles.css", "app.js", "cards.json",
                 "theme-toggle.js", "rooms.html", "rooms.js", "badges.html",
                 "badges.js", "print.html", "space.html",
                 "guidebook.html", "implementation.html", "why.html", "origin.html",
                 "arles.html", "facilitator.html", "example-spreads.html",
                 "place-explorers.html", "group-needs.html",
                 "livable-worlds.html", "not-aac.html", "privacy.html",
                 "space-time.html", "inclusive-environment.html",
                 "changelog.html"):
        p = web / name
        if p.exists():
            h.update(p.read_bytes())
    # Icons and the share card are precached, so they must feed the version hash
    # too. Without this an icon-only change never reaches a returning visitor:
    # the service worker keeps serving the old one from a cache it has no reason
    # to evict. Everything precached should influence the version.
    for name in ("favicon.svg", "favicon.ico", "apple-touch-icon.png",
                 "icon-192.png", "icon-512.png", "og-image.png",
                 "site.webmanifest"):
        p_ = web / name
        if p_.exists():
            h.update(p_.read_bytes())
    for name in face_names:
        h.update(name.encode("utf-8"))
        h.update((faces / name).read_bytes())
    for name in font_names:
        h.update(name.encode("utf-8"))
    _audio = web / "audio" / "ocean-waves.mp3"
    if _audio.exists():
        h.update(_audio.read_bytes())
    version = h.hexdigest()[:8]
    precache = [
        "/", "/index.html", "/deck.html", "/styles.css", "/app.js", "/cards.json",
        "/rooms.html", "/rooms.js", "/badges.html", "/badges.js", "/space.html",
        "/sw-register.js", "/theme-toggle.js", "/site.webmanifest",
        "/favicon.svg", "/favicon.ico", "/apple-touch-icon.png",
        "/icon-192.png", "/icon-512.png", "/og-image.png", "/audio/ocean-waves.mp3",
        "/guidebook.html", "/implementation.html", "/why.html",
        "/origin.html", "/arles.html", "/facilitator.html", "/example-spreads.html",
        "/place-explorers.html",
        "/group-needs.html", "/livable-worlds.html", "/not-aac.html",
        "/space-time.html", "/inclusive-environment.html",
        "/privacy.html", "/changelog.html",
    ] + [f"/fonts/{n}" for n in font_names] + [f"/faces/{n}" for n in face_names]
    js = (template.replace("__VERSION__", version)
                  .replace("__PRECACHE__", json.dumps(precache, ensure_ascii=False)))
    (web / "sw.js").write_text(js, encoding="utf-8")
    return version, len(precache)


def main():
    bp = _load_placeholders()
    gb = _load_guidebook()
    root = Path(__file__).resolve().parent.parent
    cards_dir = root / "cards"
    web = root / "web"
    faces = web / "faces"
    if not cards_dir.is_dir():
        sys.exit(f"cards/ not found at {cards_dir}")
    # Wipe rather than overwrite. Netlify builds from a clean checkout so it
    # never noticed, but a long-lived local clone accumulates every face the
    # deck has ever had: renaming the files to <family>--<slug>.svg left 77
    # orphans behind, each one still precached by the service worker and each
    # one still carrying markings the deck had since dropped. A generated
    # directory should hold exactly what this build generated.
    if faces.is_dir():
        shutil.rmtree(faces)
    faces.mkdir(parents=True, exist_ok=True)

    for back in ("back-standard.svg", "back-love-locution.svg", "back-interaction.svg"):
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
            # Facilitator-layer only. Underscore keys are stripped before cards.json,
            # so the Pattern crosswalk reaches the web guidebook but never the
            # card view — same one-way wall as the Markdown guidebook.
            pattern_html = gb.render_pattern_html(
                gb.parse_pattern_field(sec.get("Pattern", "").strip()))
            cslug = f.stem

            finished = root / "assets" / "cards" / slug / f"{cslug}.svg"
            if finished.exists():
                face_svg = finished.read_text(encoding="utf-8")
            elif slug in bp.FAM:
                face_svg = bp.build_svg(slug, cslug, name, cue, prompt)
            else:
                print(f"  ! no face for {slug}/{cslug}", file=sys.stderr)
                continue
            # Face filenames are namespaced by family: slugs are only unique
            # within a realm (every realm ships a `your-own`), so a bare
            # {cslug}.svg would let realms overwrite each other's faces.
            face_file = f"{slug}--{cslug}.svg"
            (faces / face_file).write_text(face_svg, encoding="utf-8")

            # Art-only copy for the room signs, which print the picture beside
            # the zone's own words -- see ART_ONLY. It comes from card-art.py's
            # motif, so a card with FINISHED art has none: if real Places art
            # ever lands, this needs revisiting rather than silently dropping
            # the picture off the signs. The build says so.
            if slug in ART_ONLY:
                art_svg = bp.build_art_svg(slug, cslug)
                if art_svg:
                    (faces / f"{slug}--{cslug}--art.svg").write_text(
                        art_svg, encoding="utf-8")
                elif finished.exists():
                    print(f"  ! {slug}/{cslug} has finished art, so no art-only "
                          f"copy for the room signs", file=sys.stderr)

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
                    else "back-interaction.svg" if slug == "interaction"
                    else "back-standard.svg")
            card = {
                "slug": cslug,
                "name": name,
                "cue": cue,
                "prompt": prompt if has_prompt else "",
                "given_not_read": slug == "love-locution",
                "notes": notes,
                "face": f"faces/{face_file}",
                "back": f"faces/{back}",
                "group": grp,
                "reflections": reflections,
                "_pattern": pattern_html,
            }
            if slug in BUILD_LINKS:
                card["buildLink"] = BUILD_LINKS[slug]
            cards.append(card)
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

    # Underscore-prefixed keys are facilitator-layer build state (e.g. _pattern) and
    # must never reach the web deck's card view. Strip them here.
    json_families = [
        {**fam, "cards": [
            {**{k: v for k, v in c.items() if not k.startswith("_")},
             "notes": _strip_md_links(c["notes"])}
            for c in fam["cards"]]}
        for fam in out_families
    ]
    (web / "cards.json").write_text(
        json.dumps({"families": json_families}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    (web / "guidebook.html").write_text(guidebook_html(out_families), encoding="utf-8")
    (web / "implementation.html").write_text(implementation_html(out_families), encoding="utf-8")
    (web / "why.html").write_text(why_html(root), encoding="utf-8")
    (web / "not-aac.html").write_text(not_aac_html(root), encoding="utf-8")
    (web / "origin.html").write_text(origin_html(root), encoding="utf-8")
    (web / "arles.html").write_text(arles_html(root), encoding="utf-8")
    (web / "space-time.html").write_text(space_time_html(root, web), encoding="utf-8")
    (web / "inclusive-environment.html").write_text(
        inclusive_environment_html(root), encoding="utf-8")
    (web / "facilitator.html").write_text(facilitator_html(root), encoding="utf-8")
    (web / "example-spreads.html").write_text(example_spreads_html(root), encoding="utf-8")
    (web / "place-explorers.html").write_text(
        place_explorers_html(root, out_families), encoding="utf-8")
    (web / "group-needs.html").write_text(group_needs_html(root), encoding="utf-8")
    (web / "livable-worlds.html").write_text(livable_worlds_html(root), encoding="utf-8")
    (web / "privacy.html").write_text(privacy_html(root), encoding="utf-8")
    (web / "changelog.html").write_text(changelog_html(root), encoding="utf-8")
    _print = print_sheets(out_families, faces)
    _write_print_sheets(web, _print)
    (web / "print.html").write_text(print_html(_print, total), encoding="utf-8")
    (web / "404.html").write_text(not_found_html(), encoding="utf-8")
    _sw_version, _sw_count = _write_service_worker(root, web, faces)
    _write_sitemap_robots(web)
    _check_signpost_parity()
    _check_cond_parity(root, web)
    _check_space_time_cards(out_families)
    _check_space_time_conds(web)
    _check_group_example(root)
    _check_card_citations(root, out_families)
    _impl_md = implementation_md(out_families)
    (root / "cavendish-cards-implementation-layer.md").write_text(
        _impl_md, encoding="utf-8")
    # Same call build-guidebook.py makes, so the published guidebook.md, the
    # rendered guidebook.html and the tracked root copy all agree by
    # construction. Writing the tracked file here (as we already do for the
    # implementation layer) means a deck change shows up in `git status` after
    # any build-site.py run, instead of waiting for someone to remember
    # build-all.py.
    _gb_md, _, _ = gb.build_markdown(cards_dir)
    (root / "cavendish-cards-guidebook.md").write_text(_gb_md, encoding="utf-8")
    _md_written = _write_md_endpoints(
        root, web, {"implementation": _impl_md, "guidebook": _gb_md,
                    "place-explorers": place_explorers_md(root, out_families),
                    "space-time": space_time_md(root, web)})
    _write_llms_txt(web)
    _write_security_txt(web)
    _navs = _write_hand_authored_navs(web)

    print(f"Wrote web/cards.json, web/guidebook.html, web/implementation.html, "
          f"web/why.html, web/origin.html, web/facilitator.html, web/example-spreads.html, "
          f"web/print.html ({len(_print)} sheets), "
          f"web/sw.js (v{_sw_version}, {_sw_count} precached), "
          f"web/llms.txt, web/security.txt, "
          f"{len(_md_written)} .md endpoints, "
          f"cavendish-cards-implementation-layer.md, and {total} faces into web/faces/")
    if _navs:
        print(f"  menu rewritten in {len(_navs)} hand-authored pages: "
              f"{', '.join(sorted(_navs))} — commit them")
    for fam in out_families:
        print(f"  {fam['name']}: {len(fam['cards'])}")


if __name__ == "__main__":
    main()
