#!/usr/bin/env python3
"""Generate placeholder card faces — one complete, printable card per card file.

Reads the card files in cards/ and writes one SVG per card into
assets/playtest/<family>/<slug>.svg: the family tag, a vector illustration of
the card's image cue, the card's name, and its prompt. Interaction cards are
skipped — they already have finished faces in assets/cards/interaction/.

The illustrations are **placeholder vector art, drawn in code** by
scripts/card-art.py, and every face says so in small type. The deck's art is
still meant to be human- and community-made — no human submissions have
arrived yet, and a deck of empty dashed boxes is not a deck anyone can hand to
a person and ask them to point at. So the project takes the same carve-out it
already takes for its icons and card frames: plain vector shapes, written as
source, never a generative-AI image.

When human art arrives for a card, drop the finished face into
assets/cards/<family>/<slug>.svg — build-site.py prefers it automatically — and
this placeholder can be deleted.

No dependencies. Usage, from the repo root:
    python3 scripts/build-placeholders.py
"""

from pathlib import Path
import html
import importlib.util
import sys
import textwrap

FONT = "'Atkinson Hyperlegible','Atkinson Hyperlegible Next',sans-serif"

# family slug -> (accent, dark accent), display word. Interaction is omitted
# on purpose: it has real faces already.
FAM = {
    "places":        ("#534AB7", "#26215C", "places"),
    "weather":       ("#BA7517", "#412402", "weather"),
    "what-helps":    ("#0F6E56", "#04342C", "what helps"),
    "lily-pad":      ("#3B6D11", "#173404", "lily pad"),
    "grower":        ("#993556", "#4B1528", "grower"),
    "love-locution": ("#993C1D", "#4A1B0C", "love locution"),
    "blank":         ("#5F5E5A", "#2C2C2A", "blank"),
}
ORDER = ["places", "weather", "what-helps", "lily-pad", "grower",
         "love-locution", "blank"]

# The art window, in card units. card-art.py draws into the top card_art.H of
# this box; ART_DROP nudges the picture down so it sits centred in the space
# above the marker line rather than riding high against the window's top edge.
ART = (60, 150, 630, 600)
ART_DROP = 28

# Small type under the picture. The art is a stand-in, and the card says so
# rather than passing code-drawn shapes off as the deck's illustration.
MARK = "PLACEHOLDER ART · HUMAN ART WANTED"


def _load_card_art():
    """Load the sibling card-art.py module (hyphenated filename)."""
    path = Path(__file__).resolve().parent / "card-art.py"
    if not path.exists():
        sys.exit(f"Could not find {path}")
    spec = importlib.util.spec_from_file_location("card_art", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ART_LIB = _load_card_art()


def parse_card(path):
    """Return {section: text} for a card file, plus the H1 name."""
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
        if line.strip() == "----":
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


def esc(s):
    return html.escape(s, quote=False)


def wrap(s, n):
    return textwrap.wrap(s, width=n) or [s]


def build_svg(family, slug, name, cue, prompt):
    """One complete card face: family tag, illustration, name, prompt.

    `cue` is the card's image cue. It is the brief the illustration was drawn
    from, and it is not printed on the face — a person points at the picture,
    and never has to read anything.
    """
    acc, dark, word = FAM[family]
    ax, ay, aw, ah = ART

    art = ART_LIB.draw(family, slug, acc, dark)
    if art is None:
        # A card with no motif yet. Say so on the face rather than shipping a
        # blank picture window; main() also reports it on stderr.
        art = (f'<text x="{aw / 2:.0f}" y="{ah / 2:.0f}" text-anchor="middle" '
               f'font-family="{FONT}" font-size="26" fill="{acc}">'
               f'no illustration yet</text>')

    name_lines = wrap(name, 20)
    ny0, nlh = 852, 60
    name_svg = "".join(
        f'<text x="60" y="{ny0 + i * nlh}" font-family="{FONT}" '
        f'font-size="58" font-weight="700" fill="#002b36">{esc(line)}</text>'
        for i, line in enumerate(name_lines)
    )

    py = ny0 + len(name_lines) * nlh + 4
    if prompt == "—" or not prompt:
        prompt_svg = (
            f'<text x="60" y="{py}" font-family="{FONT}" font-size="29" '
            f'font-style="italic" fill="{acc}">given or claimed</text>'
        )
    else:
        prompt_svg = "".join(
            f'<text x="60" y="{py + i * 34}" font-family="{FONT}" '
            f'font-size="29" fill="#586e75">{esc(line)}</text>'
            for i, line in enumerate(wrap(prompt, 38))
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050" width="750" height="1050">
<defs><clipPath id="art-window"><rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="24"/></clipPath></defs>
<rect x="0" y="0" width="750" height="1050" rx="48" fill="#eee8d5"/>
<rect x="60" y="60" width="34" height="34" rx="9" fill="{acc}"/>
<text x="108" y="87" font-family="{FONT}" font-size="30" font-weight="500" fill="{dark}">{esc(word)}</text>
<!-- The clip lives on an untransformed group: a clip-path resolves in the
     element's own user space, so putting both on one <g> would clip against
     the moved coordinates and shear the top off every picture. -->
<rect id="art" x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="24" fill="#fdf6e3"/>
<g id="art-illustration" clip-path="url(#art-window)"><g transform="translate({ax} {ay + ART_DROP})">{art}</g></g>
<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" rx="24" fill="none" stroke="{acc}" stroke-width="3"/>
<text x="375" y="{ay + ah - 24}" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#93a1a1" letter-spacing="2">{MARK}</text>
{name_svg}
{prompt_svg}
</svg>
'''


def main():
    root = Path(__file__).resolve().parent.parent
    cards_dir = root / "cards"
    out_root = root / "assets" / "playtest"
    if not cards_dir.is_dir():
        sys.exit(f"cards/ not found at {cards_dir}")

    # Fail loudly on a card added without a motif, rather than quietly
    # shipping a card with an empty picture.
    gaps = ART_LIB.missing({fam: [p.stem for p in (cards_dir / fam).glob("*.md")]
                            for fam in ORDER if (cards_dir / fam).is_dir()})

    total = 0
    summary = []
    for family in ORDER:
        files = sorted((cards_dir / family).glob("*.md"))
        if not files:
            continue
        (out_root / family).mkdir(parents=True, exist_ok=True)
        count = 0
        for f in files:
            name, sections = parse_card(f)
            if not name:
                print(f"  ! skipped {f} (no card name)", file=sys.stderr)
                continue
            svg = build_svg(
                family,
                f.stem,
                name,
                sections.get("Image cue", "").strip(),
                sections.get("Prompt", "").strip(),
            )
            (out_root / family / f"{f.stem}.svg").write_text(svg, encoding="utf-8")
            count += 1
            total += 1
        summary.append((family, count))

    print(f"Wrote {total} placeholder cards to assets/playtest/")
    for family, count in summary:
        print(f"  {family}: {count}")
    print("\nInteraction cards are skipped — they already have finished faces "
          "in assets/cards/interaction/.")
    if gaps:
        print(f"\n  ! {len(gaps)} card(s) have no illustration in "
              f"scripts/card-art.py — add a motif and register it:",
              file=sys.stderr)
        for family, slug in gaps:
            print(f"      {family}/{slug}", file=sys.stderr)


if __name__ == "__main__":
    main()
