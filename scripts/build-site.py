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
        "big-step", "round-and-round", "stormy", "tender", "heavy", "foggy", "cant-tell", "far-away",
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
        ("People & time", ["just-one-person", "parallel-existence", "no-spotlight", "let-me-unmask", "no-rush", "let-me-finish", "let-me-come-and-go"]),
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
# Site navigation, a tiny Markdown renderer, and a shared page shell.
# Used by the standalone pages (Guidebook, Implementation, Why, Origin) and
# mirrored by the hand-authored index.html. No JS: a native <details> menu.
# ---------------------------------------------------------------------------

# Order of the collapsed site menu. (label, href, key)
SITE_NAV = [
    ("The deck", "index.html", "deck"),
    ("Guidebook", "guidebook.html", "guidebook"),
    ("Implementation guidebook", "implementation.html", "implementation"),
    ("Facilitator sheet", "facilitator.html", "facilitator"),
    ("Example spreads", "example-spreads.html", "example-spreads"),
    ("Why this exists", "why.html", "why"),
    ("Origin & lineage", "origin.html", "origin"),
    ("ARLES & the cards", "arles.html", "arles"),
    ("Privacy & security", "privacy.html", "privacy"),
    ("Changelog", "changelog.html", "changelog"),
]


def site_nav(current):
    """A no-JS collapsed menu (native <details>), consistent across pages."""
    items = []
    for label, href, key in SITE_NAV:
        cur = ' aria-current="page"' if key == current else ""
        items.append(f'<li><a href="{href}"{cur}>{e(label)}</a></li>')
    return ('<details class="disclose sitenav">'
            '<summary>Menu</summary>'
            f'<ul>{"".join(items)}</ul>'
            '</details>')


_MD_LINK = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
_MD_BOLD = re.compile(r'\*\*([^*]+)\*\*')
_MD_CODE = re.compile(r'`([^`]+)`')
_MD_EM = re.compile(r'\*([^*\n]+?)\*')
_MD_IMG = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$')


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

    Handles ## / ### headings, "- " bullet lists, "> " blockquotes, all-dash
    rules, blank-line paragraphs, and inline links/bold/code/em. Drops a leading
    "# " title so the page shell owns the single <h1>.
    """
    out, para, items, quote = [], [], [], []

    def flush_para():
        if para:
            out.append("<p>" + _md_inline(" ".join(para).strip()) + "</p>")
            para.clear()

    def flush_list():
        if items:
            out.append("<ul>" + "".join("<li>" + _md_inline(i) + "</li>"
                                        for i in items) + "</ul>")
            items.clear()

    def flush_quote():
        if quote:
            out.append("<blockquote><p>"
                       + _md_inline(" ".join(quote).strip()) + "</p></blockquote>")
            quote.clear()

    def flush_all():
        flush_para(); flush_list(); flush_quote()

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
            flush_para(); flush_quote(); items.append(s[2:]); continue
        if s.startswith("> "):
            flush_para(); flush_list(); quote.append(s[2:]); continue
        flush_list(); flush_quote(); para.append(s)

    flush_all()
    return "\n".join(out)


def _standalone_page(title, description, skip_id, skip_label, h1, current, body):
    """Full HTML doc for a standalone prose page, matching the site shell."""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {_THEME_INLINE}
  <script src="/theme-toggle.js" defer></script>
  <title>Cavendish Cards — {e(title)}</title>
  <meta name="description" content="{e(description)}">
  <link rel="preload" href="/fonts/AtkinsonHyperlegible-Regular.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/fonts/AtkinsonHyperlegible-Bold.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="styles.css">
  <link rel="icon" href="/favicon.ico" sizes="any">
  <link rel="icon" href="/favicon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/apple-touch-icon.png">
  <link rel="manifest" href="/site.webmanifest">
  <meta name="theme-color" content="#fdf6e3">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Cavendish Cards">
  <meta name="color-scheme" content="light">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="Cavendish">
  <meta name="application-name" content="Cavendish Cards">
  <meta property="og:locale" content="en_US">
  <link rel="license" href="https://creativecommons.org/publicdomain/zero/1.0/">
  {_JSONLD}
  <meta property="og:title" content="Cavendish Cards — {e(title)}">
  <meta property="og:description" content="{e(description)}">
  <meta property="og:url" content="https://cavendish.app/{current}.html">
  <link rel="canonical" href="https://cavendish.app/{current}.html">
  <meta property="og:image" content="https://cavendish.app/og-image.png">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Cavendish Cards — a fan of colorful cards on a warm cream background.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Cavendish Cards — {e(title)}">
  <meta name="twitter:description" content="{e(description)}">
  <meta name="twitter:image" content="https://cavendish.app/og-image.png">
</head>
<body>
  <a class="skip" href="#{skip_id}">{e(skip_label)}</a>
  <script src="/sw-register.js" defer></script>
  <header class="site-header">
    <div class="wrap">
      {site_nav(current)}
      <h1>{e(h1)}</h1>
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
        md_to_html(src))


def origin_html(root):
    src = (root / "cavendish-cards-origin.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Origin & lineage",
        "Where the Cavendish Space model behind the deck comes from, and its lineage.",
        "origin", "Skip to the origin", "Origin & lineage", "origin",
        md_to_html(src))


def arles_html(root):
    src = (root / "cavendish-cards-arles.md").read_text(encoding="utf-8")
    return _standalone_page(
        "ARLES & the cards",
        "How the deck fits the Stimpunks Design Method (ARLES): Attention, Relational, Lived Experience, Environment, Systems — and why it stops short of Systems as cards.",
        "arles", "Skip to the ARLES page", "ARLES & the cards", "arles",
        md_to_html(src))


def example_spreads_html(root):
    src = (root / "cavendish-cards-example-spreads.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Example spreads",
        "Worked examples of the deck in use: a moment, a spread someone laid, and how to read it as a design brief for the environment.",
        "example-spreads", "Skip to the examples", "Example spreads", "example-spreads",
        md_to_html(src))


def privacy_html(root):
    src = (root / "cavendish-cards-privacy.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Privacy & security",
        "What Cavendish Cards keeps (almost nothing), how it stays on your device, and the security measures behind the site.",
        "privacy", "Skip to the privacy details", "Privacy & security", "privacy",
        md_to_html(src))


def changelog_html(root):
    src = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    return _standalone_page(
        "Changelog",
        "A running summary of notable changes to the Cavendish Cards deck and website.",
        "changelog", "Skip to the changelog", "Changelog", "changelog",
        md_to_html(src))


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
                'Download the one-page print sheet (PDF)</a> \u2014 the same content, '
                'laid out for handing round.</p>')
    body = pdf_note + "\n" + "\n".join(blocks)
    return _standalone_page(
        "Facilitator Sheet",
        "A one-page guide for support staff: the seven ways to play, the sharing model, and how to respond to a spread.",
        "facilitator", "Skip to the facilitator sheet", "Facilitator Sheet",
        "facilitator", body)


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
  <meta name="theme-color" content="#fdf6e3">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Cavendish Cards">
  <meta name="color-scheme" content="light">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="Cavendish">
  <meta name="application-name" content="Cavendish Cards">
  <meta property="og:locale" content="en_US">
  <link rel="license" href="https://creativecommons.org/publicdomain/zero/1.0/">
  {_JSONLD}
  <meta property="og:title" content="Cavendish Cards — Guidebook">
  <meta property="og:description" content="What each Cavendish card means and how to hold it. It describes the card, never the person.">
  <meta property="og:url" content="https://cavendish.app/guidebook.html">
  <link rel="canonical" href="https://cavendish.app/guidebook.html">
  <meta property="og:image" content="https://cavendish.app/og-image.png">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Cavendish Cards — a fan of colorful cards on a warm cream background.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Cavendish Cards — Guidebook">
  <meta name="twitter:description" content="What each Cavendish card means and how to hold it. It describes the card, never the person.">
  <meta name="twitter:image" content="https://cavendish.app/og-image.png">
</head>
<body>
  <a class="skip" href="#gb">Skip to the guidebook</a>
  <script src="/sw-register.js" defer></script>
  <header class="site-header">
    <div class="wrap">
      {site_nav("guidebook")}
      <h1>Guidebook</h1>
      <p class="intro">{e(INTRO)}</p>
      <div class="rules" role="note" aria-label="Not a screening tool">
        <p><strong>Not a screening tool.</strong> {e(SCREENING)}</p>
      </div>
      <div class="rules" role="note" aria-label="Not an AAC board">
        <p><strong>Not an AAC board.</strong> {e(NOT_AAC)}</p>
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
        "is asking about, with whatever you have. Organised here by sense, the way the deck "
        "groups it.",
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

# What helps — build guidance organised by the deck's sense signposts.
IMPL_WHATHELPS = [
    ("Being in charge",
     "Hand over the dial. The same input is fine when the person controls it and too "
     "much when someone else does \u2014 so give them the switch, the volume, the timing, "
     "not a fixed setting."),
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

IMPL_PLAYMODES = (
    "Two play modes map the rhythm; this book builds the room that lets it happen. Run "
    "Map the edges with the person to find where the crossings bite \u2014 focus to talking, "
    "rest to joining in, home to out the door. Run Moving between to see the shape of a "
    "day, alone to together and back. Then build the padding where the map shows it's "
    "needed. The person maps; you build it with them; the room changes, not the person."
)

# (bold lead, rest, optional url)
IMPL_LINEAGE = [
    ("Physical niche construction in the early years",
     "Helen Edgar. Much of the budget and building practice here comes from twenty "
     "years teaching children with Profound and Multiple Disabilities, where children "
     "and adults shaped the space together. (Credit wording to confirm with Helen.)",
     None),
    ("Nesting as the physical architecture of lily padding", "David Gray-Hammond.", None),
    ("Lily padding, and transitional trauma for monotropic minds", "Tanya Adkin.", None),
    ("Caves, campfires, and watering holes",
     "David Thornburg's learning-space metaphors; the case for cave spaces in schools, "
     "Prakash Nair, The Language of School Design.", None),
    ("Cavendish Space, intermittent collaboration, niche construction",
     "Stimpunks Foundation.", "https://stimpunks.org/glossary/lily-pad/"),
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
    play_html = (
        f'<section class="gb-family" id="build-play"><h2>How it pairs with the play modes</h2>'
        f'<p class="muted">{e(IMPL_PLAYMODES)}</p></section>')
    lineage_items = "".join(
        f'<li><strong>{e(lead)}</strong> \u2014 {e(rest)}'
        + (f' <a href="{url}">{e(url)}</a>' if url else '')
        + '</li>'
        for lead, rest, url in IMPL_LINEAGE)
    lineage_html = (
        f'<section class="gb-family" id="build-lineage"><h2>Lineage</h2>'
        f'<ul class="gb-lineage">{lineage_items}</ul></section>')

    guardrail_boxes = "\n".join(
        f'<div class="rules" role="note" aria-label="{e(t)}"><p><strong>{e(t)}.</strong> {e(b)}</p></div>'
        for t, b in IMPL_GUARDRAILS)

    body = "\n".join(sections + [budget_html, play_html, lineage_html])
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
  <meta name="theme-color" content="#fdf6e3">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Cavendish Cards">
  <meta name="color-scheme" content="light">
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="default">
  <meta name="apple-mobile-web-app-title" content="Cavendish">
  <meta name="application-name" content="Cavendish Cards">
  <meta property="og:locale" content="en_US">
  <link rel="license" href="https://creativecommons.org/publicdomain/zero/1.0/">
  {_JSONLD}
  <meta property="og:title" content="Cavendish Cards — Implementation Guidebook">
  <meta property="og:description" content="How to build the room the cards ask for. The facilitator layer: materials live here, never on a card.">
  <meta property="og:url" content="https://cavendish.app/implementation.html">
  <link rel="canonical" href="https://cavendish.app/implementation.html">
  <meta property="og:image" content="https://cavendish.app/og-image.png">
  <meta property="og:image:type" content="image/png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Cavendish Cards — a fan of colorful cards on a warm cream background.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="Cavendish Cards — Implementation Guidebook">
  <meta name="twitter:description" content="How to build the room the cards ask for. The facilitator layer: materials live here, never on a card.">
  <meta name="twitter:image" content="https://cavendish.app/og-image.png">
</head>
<body>
  <a class="skip" href="#impl">Skip to the guide</a>
  <script src="/sw-register.js" defer></script>
  <header class="site-header">
    <div class="wrap">
      {site_nav("implementation")}
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
    L += ["", "## How it pairs with the play modes", "", IMPL_PLAYMODES, ""]
    L += ["## Lineage", ""]
    for lead, rest, url in IMPL_LINEAGE:
        L.append(f"- **{lead}** — {rest}" + (f" {url}" if url else ""))
    L += ["", "---- ", ""]
    L.append("Dedicated to the public domain under [CC0 1.0]"
             "(https://creativecommons.org/publicdomain/zero/1.0/). "
             "Home: https://stimpunks.org/projects/cavendish-space-project/")
    L.append("")
    return "\n".join(L)


_SITE_URL = "https://cavendish.app"
_SITE_PAGES = ["/", "/guidebook.html", "/implementation.html",
               "/why.html", "/origin.html", "/arles.html", "/facilitator.html",
               "/example-spreads.html", "/privacy.html", "/changelog.html"]

# Pre-paint inline script (no flash): applies a saved light/dark choice before
# first paint. Kept byte-identical to the copy in web/index.html and to the CSP
# hash in netlify.toml — if you change it, update both.
_THEME_INLINE = "<script>(function(){try{var t=localStorage.getItem('theme');if(t==='dark'||t==='light')document.documentElement.setAttribute('data-theme',t);}catch(e){}})();</script>"


_JSONLD = ('<script type="application/ld+json">\n'
           '{"@context":"https://schema.org","@graph":['
           '{"@type":"WebSite","@id":"https://cavendish.app/#website",'
           '"name":"Cavendish Cards","url":"https://cavendish.app/",'
           '"description":"A calm, no-scoring deck for naming sensory and '
           'interaction needs.","inLanguage":"en",'
           '"license":"https://creativecommons.org/publicdomain/zero/1.0/",'
           '"publisher":{"@id":"https://stimpunks.org/#organization"}},'
           '{"@type":"Organization","@id":"https://stimpunks.org/#organization",'
           '"name":"Stimpunks Foundation","url":"https://stimpunks.org/",'
           '"sameAs":["https://github.com/Stimpunks/Cavendish-Cards"]}]}\n'
           '</script>')


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
    robots = ("User-agent: *\n"
              "Allow: /\n\n"
              f"Sitemap: {_SITE_URL}/sitemap.xml\n")
    (web / "robots.txt").write_text(robots, encoding="utf-8")


def _write_service_worker(root, web, faces):
    """Generate web/sw.js from scripts/sw-template.js, version-stamped from the
    shell files + face inventory so a new deploy evicts old caches. No deps."""
    template = (Path(__file__).resolve().parent / "sw-template.js").read_text(
        encoding="utf-8")
    face_names = sorted(p.name for p in faces.glob("*.svg"))
    font_names = sorted(p.name for p in (web / "fonts").glob("*.woff2"))
    h = hashlib.sha1()
    for name in ("index.html", "styles.css", "app.js", "cards.json", "theme-toggle.js",
                 "guidebook.html", "implementation.html", "why.html", "origin.html",
                 "arles.html", "facilitator.html", "example-spreads.html",
                 "privacy.html", "changelog.html"):
        p = web / name
        if p.exists():
            h.update(p.read_bytes())
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
        "/", "/index.html", "/styles.css", "/app.js", "/cards.json",
        "/sw-register.js", "/theme-toggle.js", "/site.webmanifest",
        "/favicon.svg", "/favicon.ico", "/apple-touch-icon.png",
        "/icon-192.png", "/icon-512.png", "/og-image.png", "/audio/ocean-waves.mp3",
        "/guidebook.html", "/implementation.html", "/why.html",
        "/origin.html", "/arles.html", "/facilitator.html", "/example-spreads.html",
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
                face_svg = bp.build_svg(slug, name, cue, prompt)
            else:
                print(f"  ! no face for {slug}/{cslug}", file=sys.stderr)
                continue
            # Face filenames are namespaced by family: slugs are only unique
            # within a realm (every realm ships a `your-own`), so a bare
            # {cslug}.svg would let realms overwrite each other's faces.
            face_file = f"{slug}--{cslug}.svg"
            (faces / face_file).write_text(face_svg, encoding="utf-8")

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
    (web / "origin.html").write_text(origin_html(root), encoding="utf-8")
    (web / "arles.html").write_text(arles_html(root), encoding="utf-8")
    (web / "facilitator.html").write_text(facilitator_html(root), encoding="utf-8")
    (web / "example-spreads.html").write_text(example_spreads_html(root), encoding="utf-8")
    (web / "privacy.html").write_text(privacy_html(root), encoding="utf-8")
    (web / "changelog.html").write_text(changelog_html(root), encoding="utf-8")
    _sw_version, _sw_count = _write_service_worker(root, web, faces)
    _write_sitemap_robots(web)
    (root / "cavendish-cards-implementation-layer.md").write_text(
        implementation_md(out_families), encoding="utf-8")

    print(f"Wrote web/cards.json, web/guidebook.html, web/implementation.html, "
          f"web/why.html, web/origin.html, web/facilitator.html, web/example-spreads.html, "
          f"web/sw.js (v{_sw_version}, {_sw_count} precached), "
          f"cavendish-cards-implementation-layer.md, and {total} faces into web/faces/")
    for fam in out_families:
        print(f"  {fam['name']}: {len(fam['cards'])}")


if __name__ == "__main__":
    main()
