#!/usr/bin/env python3
"""Generate test spreads for the group-brief method, plus an answer key.

A development tool. It writes nothing the site or the deck uses, nothing is
tracked from its output, and build-all.py does not call it. It exists so that
testing cavendish-cards-group-needs.md does not mean hand-typing spreads, or
inventing card names that are not in the deck.

Fidelity is the whole point. Every card name, prompt and reflection question
comes from web/cards.json, and the reflection a card gets is chosen the way
app.js chooses it -- lay() sets the index to the number of already-laid cards
sharing that pool, mod the pool length -- so a generated spread is shaped like
one a person would actually paste out of the deck.

The twelve profiles are deliberate rather than uniform-random, because a test
set wants the awkward cases: a spread with no mappable need in it at all, one
carrying an Interaction card that must never be aggregated, one with a note
attached, one naming a card the method has no condition for.

The answer key at the end is derived by parsing the mapping table out of
cavendish-cards-group-needs.md rather than restated here, so it cannot drift
from the method it is checking.

    python3 scripts/make-test-spreads.py [seed] > /tmp/spreads.md

Needs web/cards.json, which is generated and gitignored -- run build-site.py
first in a fresh clone.
"""
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CARDS_JSON = ROOT / "web" / "cards.json"
METHOD_MD = ROOT / "cavendish-cards-group-needs.md"
DATE = "September 16, 2026"   # fixed, so two runs differ only by their cards

if not CARDS_JSON.exists():
    sys.exit(f"{CARDS_JSON} not found -- run: python3 scripts/build-site.py")

data = json.loads(CARDS_JSON.read_text(encoding="utf-8"))
fam = {f["slug"]: f for f in data["families"]}


def pool(slug, exclude_your_own=True):
    # Tag the realm here: every realm ships a `your own`, so a card cannot be
    # traced back to its realm by name afterwards.
    return [dict(c, _family=slug) for c in fam[slug]["cards"]
            if not (exclude_your_own and c["slug"] == "your-own")]


def pick(slug, n, rng, **kw):
    return rng.sample(pool(slug, **kw), n)


def reflection_for(card, already):
    """Mirror app.js lay(): index = laid cards sharing this pool, mod pool size."""
    refs = card.get("reflections") or []
    if not refs:
        return None
    if len(refs) == 1:
        return refs[0]
    same = sum(1 for c in already if (c.get("reflections") or [None])[0] == refs[0])
    return refs[same % len(refs)]


MANIFEST = []
UNSTRIPPED = set()   # kinds the method says to strip, planted here on purpose
REFLECT_LINES = []   # the app's questions, which name cards nobody laid


def render(cards, date, note=None):
    """One spread, byte-shaped like the deck's copy button (app.js summaryText)."""
    # Record what was laid, with its realm, so the answer key never has to
    # re-derive a realm from a card name.
    MANIFEST.extend((c["_family"], c["name"]) for c in cards)
    if note:
        UNSTRIPPED.add("a note field")
    for c in cards:
        if c["_family"] == "interaction":
            UNSTRIPPED.add("an Interaction card")
        elif c["_family"] == "love-locution":
            UNSTRIPPED.add("a Kind word")
        elif c["_family"] == "grower":
            UNSTRIPPED.add("a grower")
    out = ["My Cavendish spread", date, ""]
    laid = []
    for c in cards:
        out.append("- " + c["name"] + (" — " + c["prompt"] if c["prompt"] else ""))
        q = reflection_for(c, laid)
        if q:
            out.append("  reflect: " + q)
            REFLECT_LINES.append(q)
        laid.append(c)
    if note:
        out += ["", "Note:", note]
    return "\n".join(out)


def build(rng):
    spreads = []

    def add(label, cards, note=None):
        spreads.append((label, render(cards, DATE, note)))

    # Weather only. Nothing here maps to a room condition -- the method must say
    # so rather than inferring needs from moods.
    add("weather only (nothing should map)", pick("weather", 3, rng))

    add("the ordinary one", pick("weather", 2, rng) + pick("what-helps", 3, rng))

    # A place card is a direct request for a zone.
    add("place-led (a zone is being asked for)",
        pick("places", 1, rng) + pick("what-helps", 2, rng))

    # Lily pads are about pacing, not furniture.
    add("transition", pick("lily-pad", 2, rng) + pick("what-helps", 2, rng))

    # Interaction is worn live and must be dropped at the merge, never summarized.
    add("carries an Interaction card (must not be aggregated)",
        pick("interaction", 1, rng) + pick("weather", 1, rng) + pick("what-helps", 2, rng))

    add("carries a Kind word (not a need)",
        pick("love-locution", 1, rng) + pick("what-helps", 2, rng))

    # The method says delete the note before pasting. This is the thing to delete.
    add("has a note attached (should be stripped)",
        pick("weather", 1, rng) + pick("what-helps", 3, rng),
        note="the strip lights in the main hall are the worst part, and nobody "
             "believes me about the humming. last time i left after ten minutes "
             "and had to explain myself at the door.")

    # Named, unmappable, and it has to survive as a remainder rather than be
    # forced into the nearest condition.
    add("draw-your-own (an unmappable remainder)",
        [dict(c, _family="what-helps") for c in fam["what-helps"]["cards"]
         if c["slug"] == "your-own"]
        + pick("what-helps", 2, rng))

    add("building a niche", pick("what-helps", 6, rng))

    add("grower", pick("grower", 1, rng) + pick("weather", 1, rng)
        + pick("what-helps", 2, rng))

    # Two spreads that overlap heavily: the method must not start counting once
    # the same condition turns up twice.
    shared = pick("what-helps", 3, rng)
    add("overlapping A (no counting, even here)", pick("weather", 1, rng) + shared)
    add("overlapping B (same needs as A)",
        pick("weather", 1, rng) + shared[:2] + pick("what-helps", 1, rng))
    return spreads


def mapping_from_method():
    """card name -> [condition ids], and condition id -> its change phrasing.

    Parsed out of the method document, so the key checks the doc that ships
    rather than a second copy of it kept here.
    """
    doc = METHOD_MD.read_text(encoding="utf-8")
    cond_text, card_to_cond = {}, {}
    rows = re.findall(r"^- `([a-z-]+)` — ([^.]+)\. From: ([^.]+)\.", doc, re.M)
    if not rows:
        sys.exit(f"could not parse the mapping table in {METHOD_MD.name}")
    for cid, label, froms in rows:
        cond_text[cid] = label.strip()
        for name in froms.split(","):
            name = name.strip()
            if name and not name.startswith("and the lily pads"):
                card_to_cond.setdefault(name, []).append(cid)
    buckets = {}
    for name, cards in re.findall(
            r"^\*\*(Kit|Permission|Pacing)\*\* \u2014 [^.]+\. ([^.]+)\.", doc, re.M):
        for c in cards.split(","):
            c = c.strip()
            c = (c[0].lower() + c[1:]) if c else c   # the doc sentence-cases them
            if c:
                buckets.setdefault(c, []).append(name.lower())
    if not buckets:
        sys.exit(f"could not parse the kit/permission/pacing lists in {METHOD_MD.name}")
    return cond_text, card_to_cond, buckets


# Realms the method never aggregates. Growers belong here for the same reason
# Kind words do: a grower is self-description, and a pile of self-description
# summarized is a profile. Leaving them out of this set was how the first
# version of this key let `dandelion` vanish without anyone noticing.
NEVER = {"weather", "love-locution", "interaction", "grower"}

# Lily pads that announce where a person is in a moment rather than asking the
# room for anything. The method treats these like weather.
LILY_STATES = {"ready now", "all done"}


def answer_key(cond_text, card_to_cond, buckets):
    conds, zones, unmapped, dropped, deckgap = set(), set(), set(), set(), set()
    bucketed = {}
    for f, name in MANIFEST:
        # Every realm ships one, and it means the same thing everywhere: the
        # deck had no card for what was needed. That is a different question
        # from a card the method could not place, so a different bucket.
        if name in ("your own", "draw your own"):
            deckgap.add(f)
        elif f in NEVER or name in LILY_STATES:
            dropped.add(name)
        elif f == "places":
            zones.add(name)
        elif f in ("what-helps", "lily-pad"):
            hit = card_to_cond.get(name)
            if hit:
                conds.update(hit)
            if name in buckets:
                for b in buckets[name]:
                    bucketed.setdefault(b, set()).add(name)
            elif not hit:
                # No room condition and no bucket either: a genuine hole in the
                # method, which is a different finding from "not a fixture".
                unmapped.add(name)
    # Cards named in a reflection question but never actually laid. Mapping one
    # is the clearest sign a tool read the whole paste instead of the card lines.
    laid_names = {n for _f, n in MANIFEST}
    decoys = {c for c in card_to_cond
              if c not in laid_names
              and any(re.search(r"\b" + re.escape(c) + r"\b", q) for q in REFLECT_LINES)}
    order = [c for c in cond_text if c in conds]
    L = ["", "", "=" * 70, "## Answer key", "=" * 70, "",
         "What a brief over all of these should come back with, worked out from the",
         "mapping table in the method itself. No counts, in the page's own order.", "",
         "**The room needs** — " + " · ".join(cond_text[c] for c in order), "",
         "**As ids, for the link** — `" + ",".join(order) + "`", "",
         "    https://cavendish.space/rooms.html#asked=" + ",".join(order), "",
         "**Zones asked for** — " + (", ".join(sorted(zones)) or "none"), "",
         "**Not a room condition, but it has a bucket** — " + " \u00b7 ".join(
             f"{b}: " + ", ".join(sorted(v)) for b, v in sorted(bucketed.items())), "",
         "**The method had no box for this** — " + (", ".join(sorted(unmapped)) or "none"),
         "  (a real hole — an honest remainder with a question, never a stretched condition)", "",
         "**The deck had no card for this** — " + (
             ", ".join(f"a `your own` from {r}" for r in sorted(deckgap)) or "none"), "",
         "**Never aggregated, should not appear at all** — " + ", ".join(sorted(dropped)), "",
         "**Should be reported as unstripped** — " + ", ".join(sorted(UNSTRIPPED)), "",
         "**Decoys — named only in reflect: lines, laid by nobody** — " + (
             ", ".join(f"{c} (would add `{','.join(card_to_cond[c])}`)"
                       for c in sorted(decoys)) or "none"), "",
         "  (the reflection questions are the app talking, not the person. A brief",
         "  carrying a condition sourced only from one of these read the wrong lines.)", "",
         "  (named as kinds, never quoted, never counted — a silent drop teaches the",
         "  coordinator the strip step worked when it did not)", "",
         "If what comes back has a number in it, a person as the subject of a sentence,",
         "or a category that is not in the method's vocabulary, the tool did not follow it."]
    return "\n".join(L)


def main():
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 20260916
    spreads = build(random.Random(seed))
    out = ["# Test spreads for the group-brief method", "",
           f"Generated from web/cards.json in the deck's copy-button format (seed {seed}).",
           f"{len(spreads)} spreads, as if from one event. Merge them, strip what the method",
           "says to strip, then paste. Labels are for you — they are not part of a real paste.",
           ""]
    for i, (label, text) in enumerate(spreads, 1):
        out += ["", "=" * 70, f"## Spread {i} — {label}", "=" * 70, "", text]
    out.append(answer_key(*mapping_from_method()))
    print("\n".join(out))


if __name__ == "__main__":
    main()
