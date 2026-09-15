#!/usr/bin/env python3
"""Build the favicon set, the app icons, and the Open Graph card from one source.

Everything visual here is drawn as SVG in this file and rasterised with headless
Chrome, so the mark is defined exactly once. Editing a shape means editing it
here and re-running; there is no hand-maintained PNG to fall out of step.

    python3 scripts/build-icons.py

Writes into web/: favicon.svg, favicon-16/32/48/96.png, favicon.ico,
apple-touch-icon.png, icon-192.png, icon-512.png, og-image.png.

THE MARK. A sheltering arch with a hearth inside it, on the house cream tile.
It is the cave and the campfire in one shape — the two most iconic Cavendish
forms — with the tile reading as the habitat that holds them. It replaced a fan
of three cards when the site stopped being only a card deck.

WHY THREE VARIANTS. A browser tab draws the favicon as-is, so that one carries
its own rounded corners and border. Apple and Android mask app icons to their
own shape and crop the edges, so those are full-bleed with the mark inside the
safe centre — a rounded tile inside a mask gets its corners shaved twice and
looks dented.

WHY CHROME. No SVG rasteriser is installed on this machine (no rsvg-convert, no
cairosvg, no ImageMagick), and Pillow cannot read SVG. Chrome is already here
and renders the same engine the site is viewed in.
"""
from __future__ import annotations

import base64
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEB = ROOT / "web"

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CREAM = "#fdf6e3"
INK = "#002b36"
GREEN = "#0F6E56"
RUST = "#993C1D"
MUTED = "#586e75"

# The mark itself, in a 32x32 box. `tile` draws the rounded, bordered tile a
# browser tab needs; without it the caller supplies its own background.
def mark(tile: bool) -> str:
    bg = (f'<rect x="0.5" y="0.5" width="31" height="31" rx="7.5" '
          f'fill="{CREAM}" stroke="{INK}" stroke-width="1"/>') if tile else \
         f'<rect width="32" height="32" fill="{CREAM}"/>'
    return f"""{bg}
  <path d="M3.8 27.5 L3.8 16 a12.2 12.2 0 0 1 24.4 0 L28.2 27.5 Z" fill="{GREEN}"/>
  <path d="M10 27.5 L10 17.6 a6 6 0 0 1 12 0 L22 27.5 Z" fill="{CREAM}"/>
  <circle cx="16" cy="22" r="3.8" fill="{RUST}"/>"""


def svg_doc(tile: bool, scale: float = 1.0) -> str:
    """A standalone SVG. `scale` shrinks the mark inside the box to leave the
    safe margin a maskable icon needs."""
    if scale == 1.0:
        inner = mark(tile)
    else:
        off = 16 * (1 - scale)
        inner = (f'<rect width="32" height="32" fill="{CREAM}"/>'
                 f'<g transform="translate({off:.3f},{off:.3f}) scale({scale})">{mark(False)}</g>')
    return ('<svg viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg" role="img" '
            f'aria-label="Cavendish Space"><title>Cavendish Space</title>{inner}</svg>')


def shot(html: str, out: pathlib.Path, w: int, h: int) -> None:
    """Render an HTML string at an exact pixel size."""
    with tempfile.TemporaryDirectory() as td:
        page = pathlib.Path(td) / "p.html"
        page.write_text(html, encoding="utf-8")
        subprocess.run(
            [CHROME, "--headless", "--disable-gpu", "--hide-scrollbars",
             "--force-device-scale-factor=1", f"--window-size={w},{h}",
             "--default-background-color=00000000",
             f"--screenshot={out}", f"file://{page}"],
            check=True, capture_output=True)


def render_svg(svg: str, out: pathlib.Path, size: int) -> None:
    data = base64.b64encode(svg.encode()).decode()
    shot(f'<body style="margin:0;padding:0">'
         f'<img src="data:image/svg+xml;base64,{data}" width="{size}" height="{size}">'
         f'</body>', out, size, size)


def build_icons() -> None:
    (WEB / "favicon.svg").write_text(svg_doc(tile=True) + "\n", encoding="utf-8")
    print("  favicon.svg")

    for s in (16, 32, 48, 96):
        render_svg(svg_doc(tile=True), WEB / f"favicon-{s}x{s}.png", s)
        print(f"  favicon-{s}x{s}.png")

    # Apple rounds the corners itself, so this one is full-bleed.
    render_svg(svg_doc(tile=False), WEB / "apple-touch-icon.png", 180)
    print("  apple-touch-icon.png")

    # Declared `purpose: any maskable`, so the mark sits inside the safe centre
    # (~78%); a mask crops roughly the outer 10% on every side.
    for s in (192, 512):
        render_svg(svg_doc(tile=False, scale=0.78), WEB / f"icon-{s}.png", s)
        print(f"  icon-{s}.png")

    try:
        from PIL import Image
    except ImportError:
        print("  ! Pillow missing — favicon.ico not rebuilt", file=sys.stderr)
        return
    base = Image.open(WEB / "favicon-96x96.png").convert("RGBA")
    base.save(WEB / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
    print("  favicon.ico")


def build_og() -> None:
    """The 1200x630 share card. Self-hosted Atkinson Hyperlegible, embedded as a
    data URI so the render does not depend on a font being installed."""
    font = WEB / "fonts" / "AtkinsonHyperlegible-Bold.woff2"
    reg = WEB / "fonts" / "AtkinsonHyperlegible-Regular.woff2"
    faces = ""
    for path, weight in ((font, 700), (reg, 400)):
        if path.exists():
            b64 = base64.b64encode(path.read_bytes()).decode()
            faces += (f"@font-face{{font-family:AH;font-weight:{weight};"
                      f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")
    logo = base64.b64encode(svg_doc(tile=True).encode()).decode()
    html = f"""<body style="margin:0"><style>{faces}
 *{{box-sizing:border-box}}
 .c{{width:1200px;height:630px;background:{CREAM};font-family:AH,system-ui;
    padding:84px;display:flex;flex-direction:column;justify-content:center;gap:54px}}
 .t{{font-weight:700;font-size:92px;color:{INK};margin:0;line-height:1.05}}
 .s{{font-weight:400;font-size:38px;color:{INK};margin:22px 0 0;max-width:22ch;line-height:1.35}}
 .r{{display:flex;gap:18px;align-items:center}}
 .p{{font-weight:700;font-size:26px;color:{GREEN};border:3px solid {GREEN};
    border-radius:999px;padding:10px 26px}}
 .f{{font-weight:400;font-size:24px;color:{MUTED};margin:0}}
 .h{{display:flex;align-items:center;gap:28px}}
</style>
<div class="c">
  <div>
    <div class="h"><img src="data:image/svg+xml;base64,{logo}" width="104" height="104">
      <p class="t">Cavendish Space</p></div>
    <p class="s">Places built to fit bodyminds, not the other way round.</p>
  </div>
  <div>
    <div class="r"><span class="p">Show how you feel</span><span class="p">Set up a room</span></div>
    <p class="f" style="margin-top:26px">cavendish.space &middot; a project of Stimpunks Foundation</p>
  </div>
</div></body>"""
    shot(html, WEB / "og-image.png", 1200, 630)
    print("  og-image.png")


def main() -> int:
    if not pathlib.Path(CHROME).exists():
        print(f"Chrome not found at {CHROME}", file=sys.stderr)
        return 1
    if not shutil.which("python3"):
        return 1
    print("Building icons into web/ …")
    build_icons()
    build_og()
    print("Done. These are tracked files — commit them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
