#!/usr/bin/env python3
"""Audit the reading level and sentence length of every card's Notes.

A diagnostic, not a generator: it writes nothing and gates nothing. It reads
cards/**/*.md and reports, per realm and overall, an approximate Flesch-Kincaid
grade level and average sentence length for each card's ## Notes (the guidebook
entry), then lists the hardest cards to work on first.

This exists to support a plain-language / Easy Read audit against ASAN's
"One Idea Per Line" standard (https://autisticadvocacy.org/resources/accessibility/easyread/).
Two caveats, both from that guide:
  - Reading-level formulas are only one lens and disagree with each other;
    sentence length (words per sentence) is the clearer, more actionable signal.
    ASAN aims for ~10-15 words per sentence, one idea per sentence.
  - No script can certify Easy Read. That needs a focus group of people with
    intellectual and developmental disabilities: "nothing about us, without us."

Lineage credits and glossary links are stripped before scoring, since proper
nouns and defined terms inflate the grade without being the thing to fix (ASAN
pulls such terms out before checking a score). Prompts and image cues are not
scored — they are short by design.

No third-party dependencies.

Usage, from the repo root:
    python3 scripts/check-readability.py            # audit the whole deck
    python3 scripts/check-readability.py cards/weather/tender.md   # one or more cards
    python3 scripts/check-readability.py --top 12   # show more of the hardest cards
"""

from pathlib import Path
import argparse
import re
import statistics
import sys

REALM_ORDER = ["places", "weather", "what-helps", "lily-pad", "grower",
               "love-locution", "interaction", "blank"]

_LINK = re.compile(r'\[([^\]]+)\]\([^)]+\)')          # [text](url) -> text
_WORD = re.compile(r"[A-Za-z']+")
_SENT = re.compile(r'(?<=[.!?])\s+')


def syllables(word):
    w = re.sub(r'[^a-z]', '', word.lower())
    if not w:
        return 0
    groups = re.findall(r'[aeiouy]+', w)
    n = len(groups)
    if w.endswith('e') and n > 1:
        n -= 1
    return max(1, n)


def sentences(text):
    return [s.strip() for s in _SENT.split(text.strip()) if s.strip()]


def notes_of(path):
    """Return a card's Notes text, minus glossary links and the Lineage clause."""
    body = path.read_text(encoding="utf-8")
    m = re.search(r'## Notes\n\n(.*?)\n\n----', body, re.S)
    if not m:
        return None
    text = _LINK.sub(r'\1', m.group(1))
    text = re.sub(r'\s*Lineage:.*$', '', text.strip(), flags=re.S)
    return text.strip()


def measure(text):
    ss = sentences(text)
    words = _WORD.findall(text)
    if not ss or not words:
        return None
    W, S = len(words), len(ss)
    Sy = sum(syllables(w) for w in words)
    grade = 0.39 * (W / S) + 11.8 * (Sy / W) - 15.59
    per_sentence = [len(_WORD.findall(s)) for s in ss]
    return {
        "words": W, "sentences": S, "wps": W / S, "grade": grade,
        "longest": max(per_sentence),
        "long_sentences": sum(1 for n in per_sentence if n > 15),
    }


def collect(paths):
    rows = []
    for p in paths:
        text = notes_of(p)
        if not text:
            continue
        m = measure(text)
        if m:
            rows.append((p.parent.name, p.stem, m))
    return rows


def main():
    ap = argparse.ArgumentParser(description="Readability audit of card Notes.")
    ap.add_argument("paths", nargs="*", help="specific card files (default: all)")
    ap.add_argument("--top", type=int, default=8, help="how many hardest cards to list")
    args = ap.parse_args()

    root = Path(__file__).resolve().parent.parent
    if args.paths:
        paths = [Path(p) for p in args.paths]
    else:
        cards = root / "cards"
        if not cards.is_dir():
            sys.exit(f"cards/ not found at {cards}")
        paths = sorted(cards.glob("*/*.md"))

    rows = collect(paths)
    if not rows:
        sys.exit("No card Notes found to measure.")

    by_realm = {}
    for realm, slug, m in rows:
        by_realm.setdefault(realm, []).append(m)

    print(f"{'realm':14}{'cards':>6}{'mean grade':>12}{'mean words/sentence':>22}")
    ordered = [r for r in REALM_ORDER if r in by_realm]
    ordered += [r for r in sorted(by_realm) if r not in REALM_ORDER]
    for realm in ordered:
        ms = by_realm[realm]
        g = statistics.mean(m["grade"] for m in ms)
        w = statistics.mean(m["wps"] for m in ms)
        print(f"{realm:14}{len(ms):>6}{g:>12.1f}{w:>22.1f}")

    allg = [m["grade"] for _, _, m in rows]
    allw = [m["wps"] for _, _, m in rows]
    long_cards = sum(1 for _, _, m in rows if m["long_sentences"])
    print(f"\nOVERALL: {len(rows)} cards | mean grade {statistics.mean(allg):.1f} "
          f"| mean words/sentence {statistics.mean(allw):.1f}")
    print("Targets (ASAN): Easy Read grade 3-5, Plain Language grade 6-8; "
          "~10-15 words per sentence.")
    print(f"Cards with a sentence over 15 words: {long_cards} / {len(rows)}")

    hardest = sorted(rows, key=lambda x: -x[2]["grade"])[:args.top]
    print(f"\nHardest {len(hardest)} to work on first (by Notes grade level):")
    for realm, slug, m in hardest:
        print(f"  grade {m['grade']:5.1f}  {realm}/{slug}  "
              f"(longest sentence {m['longest']} words)")


if __name__ == "__main__":
    main()
