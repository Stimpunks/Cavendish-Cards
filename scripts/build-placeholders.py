#!/usr/bin/env python3
"""Generate placeholder card faces for playtesting.

Reads the card files in cards/ and writes one simple, obviously-provisional
SVG per card into assets/playtest/<family>/<slug>.svg. Interaction cards are
skipped — they already have finished faces in assets/cards/interaction/.

These are NOT art. They are code-drawn placeholders (a plain "image pending"
glyph plus the card's image-cue text) so the deck can be printed and
playtested while human- and community-made artwork is in progress. When real
art arrives, drop it into the template's `#art` window and the card graduates
into assets/cards/; the playtest file can then be deleted.

No dependencies. Usage, from the repo root:
    python3 scripts/build-placeholders.py
"""

from pathlib import Path
import html
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


def build_svg(family, name, cue, prompt):
    acc, dark, word = FAM[family]

    cue_svg = "".join(
        f'<text x="375" y="{500 + i * 36}" text-anchor="middle" '
        f'font-family="{FONT}" font-size="27" fill="{dark}" '
        f'opacity="0.75">{esc(line)}</text>'
        for i, line in enumerate(wrap(cue, 26))
    )

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
            f'font-style="italic" fill="{acc}">given, not read</text>'
        )
    else:
        prompt_svg = "".join(
            f'<text x="60" y="{py + i * 34}" font-family="{FONT}" '
            f'font-size="29" fill="#586e75">{esc(line)}</text>'
            for i, line in enumerate(wrap(prompt, 38))
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050" width="750" height="1050">
<rect x="0" y="0" width="750" height="1050" rx="48" fill="#eee8d5"/>
<rect x="60" y="60" width="34" height="34" rx="9" fill="{acc}"/>
<text x="108" y="87" font-family="{FONT}" font-size="30" font-weight="500" fill="{dark}">{esc(word)}</text>
<rect id="art" x="60" y="150" width="630" height="600" rx="24" fill="#fdf6e3" stroke="{acc}" stroke-width="3" stroke-dasharray="11 9"/>
<g id="art-placeholder" opacity="0.6">
<rect x="300" y="292" width="150" height="118" rx="12" fill="none" stroke="{acc}" stroke-width="4"/>
<circle cx="334" cy="328" r="12" fill="{acc}"/>
<polygon points="315,404 360,350 390,382 424,338 449,404" fill="{acc}"/>
</g>
{cue_svg}
<text x="375" y="712" text-anchor="middle" font-family="{FONT}" font-size="17" fill="#93a1a1" letter-spacing="2">PLACEHOLDER · ART TO COME</text>
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


if __name__ == "__main__":
    main()
