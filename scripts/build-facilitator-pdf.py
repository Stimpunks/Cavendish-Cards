#!/usr/bin/env python3
"""Build the facilitator-sheet PDF from its Markdown source.

Reads cavendish-cards-facilitator-sheet.md and writes
cavendish-cards-facilitator-sheet.pdf, so the print-ready sheet always matches
the screen-reader-friendly Markdown source and never drifts out of sync (the
failure mode this script exists to fix: the PDF was hand-built and lagged the
Markdown, still showing "Five ways to play" after the deck grew to seven).

Layout is a single styled HTML document rendered by WeasyPrint: the umbrella
Solarized palette, a teal left bar, teal section headings, teal-dot bullets,
teal numbered badges, and a CC0 footer — all set in Atkinson Hyperlegible, the
same accessible typeface the rest of the deck uses. The font is referenced by
family name, so it must be installed on the system (as it is for the card
faces); WeasyPrint embeds a subset into the PDF.

This needs one library beyond the standard build scripts:
    pip install weasyprint

WeasyPrint also needs system libraries (Pango, cairo, GDK-PixBuf); see
https://doc.courtbouillon.org/weasyprint/stable/first_steps.html

Usage, from the repo root:
    python3 scripts/build-facilitator-pdf.py [output.pdf]
"""

from html import escape
from pathlib import Path
import re
import sys

FONT = "'Atkinson Hyperlegible','Atkinson Hyperlegible Next',sans-serif"

CSS = """
  :root{
    --ink:#002b36;    /* headings, strong */
    --body:#073642;   /* body text */
    --teal:#2aa198;   /* accent: bar, bullets, badges */
    --muted:#93a1a1;  /* kicker, footer */
    --rule:#cfe0dc;   /* faint dividers */
  }
  @page{ size:Letter; margin:14mm 16mm 12mm 20mm; }
  html{ font-family:__FONT__; color:var(--body); font-size:10.5pt; line-height:1.42; }
  body{ margin:0; }
  .leftbar{ position:fixed; top:0; bottom:0; left:-14mm; width:6mm; background:var(--teal); }
  .title{ font-weight:700; font-size:25pt; color:var(--ink); letter-spacing:.2px; line-height:1.05; margin:0; }
  .kicker{ font-weight:700; font-size:10.5pt; color:var(--muted); letter-spacing:3px; text-transform:uppercase; margin:2px 0 0; }
  .lede{ margin:10px 0 2px; }
  .headrule{ border:0; border-top:1.5px solid var(--rule); margin:11px 0 14px; }
  h2{ font-weight:700; font-size:14.5pt; color:var(--ink); margin:17px 0 7px; }
  p{ margin:0 0 7px; }
  strong{ color:var(--ink); font-weight:700; }
  em{ color:var(--muted); }
  a{ color:inherit; }
  .lead{ font-weight:700; color:var(--ink); margin:15px 0 6px; }
  ul.dot{ list-style:none; margin:0 0 4px; padding:0; }
  ul.dot > li{ position:relative; padding-left:16px; margin:0 0 6px; break-inside:avoid; }
  ul.dot > li::before{ content:""; position:absolute; left:0; top:.52em; width:6px; height:6px; border-radius:50%; background:var(--teal); }
  .mode{ margin:0 0 8px; break-inside:avoid; }
  .mode .name{ font-weight:700; color:var(--ink); }
  .mode .who{ font-style:italic; color:var(--muted); }
  .mode .desc{ margin:1px 0 0; }
  ol.steps{ list-style:none; counter-reset:s; margin:0; padding:0; }
  ol.steps > li{ counter-increment:s; position:relative; padding-left:28px; margin:0 0 7px; break-inside:avoid; }
  ol.steps > li::before{ content:counter(s); position:absolute; left:0; top:0; width:18px; height:18px; border-radius:50%; background:var(--teal); color:#fff; font-weight:700; font-size:9.5pt; text-align:center; line-height:18px; }
  footer{ margin-top:16px; padding-top:9px; border-top:1.5px solid var(--rule); color:var(--muted); font-size:8.6pt; }
""".replace("__FONT__", FONT)

# Inline Markdown: links, then bold, then italic. Escape first.
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD = re.compile(r"\*\*(.+?)\*\*")
_ITAL = re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)")
_MODE = re.compile(r"^\*\*(.+?)\*\*\s+—\s+\*(.+?)\*\s*$")


def inline(text):
    out = escape(text.strip())
    # links: the delimiters survive escaping ([, ], (, ) are not escaped)
    out = _LINK.sub(lambda m: f'<a href="{escape(m.group(2), quote=True)}">{m.group(1)}</a>', out)
    out = _BOLD.sub(r"<strong>\1</strong>", out)
    out = _ITAL.sub(r"<em>\1</em>", out)
    return out


def parse(md):
    """Return (title, kicker, [html_block, ...]) from the facilitator Markdown."""
    title, kicker = "Cavendish Cards", "Facilitator Sheet"
    lines = md.splitlines()

    # Title from the first H1, split on an em-dash if present.
    for ln in lines:
        if ln.startswith("# ") and not ln.startswith("## "):
            head = ln[2:].strip()
            if "—" in head:
                title, kicker = (p.strip() for p in head.split("—", 1))
            else:
                title = head
            break

    # Blocks separated by blank lines; drop H1 and "----" separators.
    body = "\n".join(l for l in lines
                     if not (l.startswith("# ") and not l.startswith("## ")))
    raw_blocks = [b.strip() for b in re.split(r"\n\s*\n", body)]
    blocks = [b for b in raw_blocks if b and set(b.strip()) != {"-"}]

    html, section, first_para = [], "", True
    for block in blocks:
        blines = block.splitlines()

        if block.startswith("## "):
            section = block[3:].strip().lower()
            html.append(f"<h2>{inline(block[3:].strip())}</h2>")
            continue

        if all(l.lstrip().startswith("- ") for l in blines):
            items = "".join(f"<li>{inline(l.lstrip()[2:])}</li>" for l in blines)
            html.append(f'<ul class="dot">{items}</ul>')
            continue

        if all(re.match(r"^\d+\.\s", l.lstrip()) for l in blines):
            stripped = (re.sub(r"^\d+\.\s+", "", l.lstrip()) for l in blines)
            items = "".join(f"<li>{inline(s)}</li>" for s in stripped)
            html.append(f'<ol class="steps">{items}</ol>')
            continue

        if "ways to play" in section:
            m = _MODE.match(blines[0])
            if m:
                desc = inline(" ".join(l.strip() for l in blines[1:]))
                html.append(
                    f'<div class="mode"><span class="name">{escape(m.group(1))}</span> '
                    f'<span class="who">— {escape(m.group(2))}</span>'
                    f'<p class="desc">{desc}</p></div>')
                continue

        if block.startswith("Free to use"):
            html.append(f"<footer>{inline(block)}</footer>")
            continue

        # A whole-line bold paragraph is a lead/sub-head.
        if len(blines) == 1 and re.fullmatch(r"\*\*.+\*\*", block):
            html.append(f'<p class="lead">{inline(block)}</p>')
            continue

        para_cls = ' class="lede"' if first_para else ""
        html.append(f"<p{para_cls}>{inline(' '.join(l.strip() for l in blines))}</p>")
        first_para = False

    return title, kicker, html


def render_html(title, kicker, blocks):
    # Rule sits under the header block (after the lede paragraph).
    body = []
    placed = False
    for b in blocks:
        body.append(b)
        if not placed and 'class="lede"' in b:
            body.append('<hr class="headrule">')
            placed = True

    return (
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        f"<title>{escape(title)} — {escape(kicker)}</title>"
        f"<style>{CSS}</style></head><body>"
        '<div class="leftbar"></div>'
        f'<h1 class="title">{escape(title)}</h1>'
        f'<p class="kicker">{escape(kicker)}</p>'
        + "".join(body)
        + "</body></html>"
    )


def main():
    root = Path(__file__).resolve().parent.parent
    src = root / "cavendish-cards-facilitator-sheet.md"
    if not src.is_file():
        sys.exit(f"Source not found: {src}")

    out_path = (Path(sys.argv[1]).resolve() if len(sys.argv) > 1
                else root / "cavendish-cards-facilitator-sheet.pdf")

    try:
        from weasyprint import HTML
    except ImportError as exc:
        sys.exit(
            f"Missing dependency: {exc.name}.\n"
            "This script needs WeasyPrint:\n"
            "    pip install weasyprint\n"
            "WeasyPrint also needs system libraries (Pango, cairo, GDK-PixBuf); see\n"
            "https://doc.courtbouillon.org/weasyprint/stable/first_steps.html"
        )

    title, kicker, blocks = parse(src.read_text(encoding="utf-8"))
    HTML(string=render_html(title, kicker, blocks)).write_pdf(str(out_path))
    print(f"Wrote {out_path.name} from {src.name}")


if __name__ == "__main__":
    main()
