#!/usr/bin/env python3
"""Build the static web deck into web/ from the card files.

Reads cards/**, resolves each card's face (finished art from assets/cards/ if
present, otherwise a generated placeholder), copies faces and the two card
backs into web/faces/, and writes web/cards.json. The hand-authored site shell
(web/index.html, web/styles.css, web/app.js) reads cards.json at runtime.

Reuses scripts/build-placeholders.py, so placeholder faces match the deck.
No third-party dependencies.

Usage, from the repo root:
    python3 scripts/build-site.py
"""

from pathlib import Path
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


# All families, in deck order, with display name and short intro.
FAMILIES = [
    ("places", "Places",
     "The five Cavendish zones. Everything else sits in one of these."),
    ("weather", "Weather",
     "Inner weather, not clinical states — the whole range, good and hard alike."),
    ("what-helps", "What helps",
     "The ways we change the environment so it fits."),
    ("lily-pad", "Lily pads",
     "The in-between. Every card is a landing place, not a failure."),
    ("grower", "Growers",
     "Who am I today. Different people bloom in different conditions."),
    ("love-locution", "Love Locutions",
     "Affirmations. Given between people, never earned."),
    ("interaction", "Interaction",
     "How open I am to talking, right now."),
    ("blank", "Blank",
     "The card the deck doesn't have yet. Draw it."),
]


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
        for f in sorted(fam_dir.glob("*.md")):
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
            })
            total += 1
        if cards:
            out_families.append({"slug": slug, "name": display,
                                 "intro": intro, "cards": cards})

    (web / "cards.json").write_text(
        json.dumps({"families": out_families}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"Wrote web/cards.json and {total} faces into web/faces/")
    for fam in out_families:
        print(f"  {fam['name']}: {len(fam['cards'])}")


if __name__ == "__main__":
    main()
