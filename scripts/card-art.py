#!/usr/bin/env python3
"""Placeholder vector illustrations — one motif per card, drawn in code.

WHY THIS EXISTS. The deck's art is meant to be human- and community-made, and
that is still what we want. But no human art has been submitted, and a deck of
dashed "image pending" boxes is not a deck anyone can actually hand to a person
and ask them to point at. So the project takes the same carve-out it already
takes for its icons and card frames: **plain vector illustration, drawn in code
in this file, as an explicit placeholder.** Every card face says so. No
generative-AI image tool is used, and no AI-generated image is ever committed —
these are shapes with coordinates, readable and editable like any other source.

When human art arrives for a card, drop the finished face into
assets/cards/<family>/<slug>.svg and the pipeline prefers it automatically; the
motif here can then be deleted.

HOW A MOTIF IS DRAWN. Each function takes the family's accent and dark accent
and returns SVG for the art window's local coordinate space: 630 wide, and the
top 530 tall (the strip below that carries the placeholder marker). Origin is
the window's top-left. The caller wraps the result in a translate + clip, so a
motif never has to know where the window sits on the card.

HOUSE STYLE. Flat shapes, rounded ends, one family color in two or three
weights plus the paper underneath. No text inside the picture (a person never
has to read a card), no faces beyond eyes, no gradients, no clutter. Stroke
weights: MAIN for the thing the card is about, THIN for detail.

No dependencies. Imported by build-placeholders.py; not usually run directly,
but `python3 scripts/card-art.py` writes a contact sheet to /tmp for review.
"""

from __future__ import annotations

# The drawable box inside the art window.
W, H = 630, 530
CX = W / 2

PAPER = "#fdf6e3"
INK = "#002b36"

MAIN = 11   # the line weight of the subject
THIN = 6    # detail, texture, motion


# ---------------------------------------------------------------- svg helpers

def _attrs(kw):
    out = []
    for k, v in kw.items():
        if v is None:
            continue
        out.append(f'{k.rstrip("_").replace("_", "-")}="{v}"')
    return (" " + " ".join(out)) if out else ""


def path(d, **kw):
    return f'<path d="{d}"{_attrs(kw)}/>'


def circle(cx, cy, r, **kw):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}"{_attrs(kw)}/>'


def ellipse(cx, cy, rx, ry, **kw):
    return (f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" '
            f'ry="{ry:.1f}"{_attrs(kw)}/>')


def rect(x, y, w, h, rx=0, **kw):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'rx="{rx:.1f}"{_attrs(kw)}/>')


def line(x1, y1, x2, y2, **kw):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" '
            f'y2="{y2:.1f}"{_attrs(kw)}/>')


def poly(points, **kw):
    pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polyline points="{pts}"{_attrs(kw)}/>'


def group(body, **kw):
    return f'<g{_attrs(kw)}>{body}</g>'


def stroke(color, w=MAIN, **kw):
    """Shorthand attrs for an unfilled stroked shape."""
    kw.update(fill="none", stroke=color, stroke_width=w)
    return kw


def wash(color, o=0.16, **kw):
    """Shorthand attrs for a soft tinted fill."""
    kw.update(fill=color, fill_opacity=o)
    return kw


# -------------------------------------------------------------- shape vocabulary

def person(cx, base, s=1.0, color=INK, o=1.0, head=True):
    """A simple figure: bell body on the ground line at `base`, head above."""
    w, bh, hr, gap = 42 * s, 112 * s, 31 * s, 13 * s
    body = path(
        f"M{cx - w:.1f} {base:.1f} Q{cx - w:.1f} {base - bh:.1f} "
        f"{cx:.1f} {base - bh:.1f} Q{cx + w:.1f} {base - bh:.1f} "
        f"{cx + w:.1f} {base:.1f} Z", fill=color, fill_opacity=o)
    if not head:
        return body
    return body + circle(cx, base - bh - gap - hr, hr, fill=color, fill_opacity=o)


def person_top(cx, base, s=1.0):
    """Y of the top of a person's head, for hanging things above one."""
    return base - 112 * s - 13 * s - 62 * s


def arm(cx, base, s, dx, dy, color=INK, w=None):
    """A single arm springing from the shoulder, ending at (dx, dy) offset."""
    sy = base - 92 * s
    sx = cx + (34 * s if dx > 0 else -34 * s)
    return path(f"M{sx:.1f} {sy:.1f} Q{sx + dx * 0.55:.1f} {sy + dy * 0.3:.1f} "
                f"{sx + dx:.1f} {sy + dy:.1f}",
                **stroke(color, w or 13 * s))


def eyes(cx, cy, gap=26, r=8, color=INK):
    return (circle(cx - gap, cy, r, fill=color) +
            circle(cx + gap, cy, r, fill=color))


def sparkle(x, y, r, color, w=THIN):
    return (line(x - r, y, x + r, y, **stroke(color, w)) +
            line(x, y - r, x, y + r, **stroke(color, w)))


def star4(x, y, r, color):
    k = r * 0.3
    return path(f"M{x} {y - r} Q{x + k} {y - k} {x + r} {y} "
                f"Q{x + k} {y + k} {x} {y + r} Q{x - k} {y + k} {x - r} {y} "
                f"Q{x - k} {y - k} {x} {y - r} Z", fill=color)


def cloud(cx, cy, s, color, o=1.0):
    return group(
        ellipse(cx - 62 * s, cy + 8 * s, 58 * s, 42 * s, fill=color) +
        ellipse(cx + 8 * s, cy - 18 * s, 76 * s, 58 * s, fill=color) +
        ellipse(cx + 76 * s, cy + 10 * s, 56 * s, 40 * s, fill=color) +
        rect(cx - 62 * s, cy + 6 * s, 140 * s, 46 * s, 23 * s, fill=color),
        fill_opacity=o)


def ground(y, a, o=0.13):
    """A soft floor line, so a figure has somewhere to stand."""
    return (rect(40, y, W - 80, 14, 7, **wash(a, o)) +
            line(40, y + 7, W - 40, y + 7, **stroke(a, 3, stroke_opacity=0.45)))


def lilypad(cx, cy, rx, a, o=0.9):
    """A lily pad seen from a low angle: a disc with a wedge cut out."""
    ry = rx * 0.42
    return (ellipse(cx, cy, rx, ry, fill=a, fill_opacity=o) +
            path(f"M{cx:.1f} {cy:.1f} L{cx + rx * 0.72:.1f} {cy - ry * 0.7:.1f} "
                 f"L{cx + rx * 0.96:.1f} {cy + ry * 0.12:.1f} Z", fill=PAPER))


def ripples(cx, cy, a, n=3, rx=70, step=34):
    return "".join(
        ellipse(cx, cy, rx + i * step, (rx + i * step) * 0.34,
                **stroke(a, THIN - 1, stroke_opacity=0.5 - i * 0.12))
        for i in range(n))


def door(x, y, w, h, a, d, open_=True):
    frame = rect(x, y, w, h, 10, **stroke(d, MAIN))
    if not open_:
        return frame + circle(x + w - 22, y + h / 2, 7, fill=d)
    leaf = path(f"M{x + w:.1f} {y:.1f} L{x + w + 74:.1f} {y - 26:.1f} "
                f"L{x + w + 74:.1f} {y + h + 26:.1f} L{x + w:.1f} {y + h:.1f} Z",
                **wash(a, 0.22))
    return (rect(x, y, w, h, 10, fill=a, fill_opacity=0.5) + frame + leaf +
            circle(x + w + 56, y + h / 2, 7, fill=d))


def arrow(x1, y1, x2, y2, color, w=MAIN, head=17):
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    a1 = ang + 2.6
    a2 = ang - 2.6
    return (line(x1, y1, x2, y2, **stroke(color, w)) +
            poly([(x2 + head * math.cos(a1), y2 + head * math.sin(a1)),
                  (x2, y2),
                  (x2 + head * math.cos(a2), y2 + head * math.sin(a2))],
                 **stroke(color, w)))


def motion(cx, cy, a, n=3, r=34, side=1, spread=17):
    """Short arcs beside a thing, to say it is moving."""
    return "".join(
        path(f"M{cx + side * (r + i * spread):.1f} {cy - 26 - i * 5:.1f} "
             f"Q{cx + side * (r + i * spread + 13):.1f} {cy:.1f} "
             f"{cx + side * (r + i * spread):.1f} {cy + 26 + i * 5:.1f}",
             **stroke(a, THIN - 1, stroke_opacity=0.75 - i * 0.16))
        for i in range(n))


def open_palm(x, y, s=1.0, a=INK, d=INK, rot=0):
    """A flat open hand, fingers up. Used for `not yet` and `you belong here`."""
    dd = ("M-96 134 q-14 -108 6 -160 q10 -26 30 -20 q16 4 16 34 l0 46 l0 -132 "
        "q0 -30 26 -30 q26 0 26 30 l0 126 l0 -146 q0 -30 26 -30 "
        "q26 0 26 30 l0 146 l0 -112 q0 -30 26 -30 q26 0 26 30 l0 208 "
        "q0 90 -92 90 q-84 0 -116 -80 Z")
    return group(path(dd, fill=a, fill_opacity=0.6) + path(dd, **stroke(d, MAIN)),
                 transform=f"translate({x:.1f} {y:.1f}) rotate({rot}) "
                           f"scale({s:.3f})")


def hand(x, y, s=1.0, a=INK, d=INK, rot=0, point=False):
    """A hand: palm, four fingers, a thumb. Points with the index when asked.

    Hands carry a lot of these cards (pointing at a card, sliding choices
    aside, resting on a dial), so they get a real shape rather than a blob.
    """
    fingers = ""
    for i in range(4):
        fh = (96 if point and i == 3 else
              (74, 86, 80, 68)[i]) if not point else (30, 34, 30, 96)[i]
        fw = 21
        fx = -46 + i * 24
        fingers += rect(fx, -fh, fw, fh + 34, fw / 2,
                        fill=a, fill_opacity=0.8)
        fingers += rect(fx, -fh, fw, fh + 34, fw / 2, **stroke(d, 5))
    palm = (rect(-50, -14, 106, 96, 34, fill=a, fill_opacity=0.8) +
            rect(-50, -14, 106, 96, 34, **stroke(d, 6)))
    thumb = (group(rect(-16, -22, 32, 84, 16, fill=a, fill_opacity=0.8) +
                   rect(-16, -22, 32, 84, 16, **stroke(d, 6)),
                   transform="translate(64 34) rotate(42)"))
    return group(fingers + palm + thumb,
                 transform=f"translate({x:.1f} {y:.1f}) rotate({rot}) "
                           f"scale({s:.3f})")


def blank_card_and_pencil(a, d):
    """Shared motif for every realm's `your own` card, and the blank card."""
    card = rect(CX - 214, 104, 232, 320, 22,
                fill=PAPER, stroke=d, stroke_width=MAIN,
                stroke_dasharray="16 14")
    corner = path(f"M{CX - 184:.1f} 144 L{CX - 184:.1f} 394 "
                  f"L{CX - 48:.1f} 394", **stroke(a, THIN, stroke_opacity=0.4))
    px, py = CX + 200, 124
    pencil = group(
        path(f"M{px:.1f} {py:.1f} L{px + 46:.1f} {py + 30:.1f} "
             f"L{px - 78:.1f} {py + 242:.1f} L{px - 122:.1f} {py + 212:.1f} Z",
             fill=a) +
        path(f"M{px - 78:.1f} {py + 242:.1f} L{px - 122:.1f} {py + 212:.1f} "
             f"L{px - 134:.1f} {py + 276:.1f} Z", fill=d) +
        line(px - 4, py + 38, px - 118, py + 232, **stroke(PAPER, 5,
                                                           stroke_opacity=0.5)))
    return card + corner + pencil + ground(452, a)


# ------------------------------------------------------------------- places

def m_places_campfire(a, d):
    fire = (path(f"M{CX:.1f} 118 Q{CX + 86:.1f} 214 {CX + 52:.1f} 292 "
                 f"Q{CX + 30:.1f} 340 {CX:.1f} 340 Q{CX - 30:.1f} 340 "
                 f"{CX - 52:.1f} 292 Q{CX - 86:.1f} 214 {CX:.1f} 118 Z",
                 fill=a) +
            path(f"M{CX:.1f} 196 Q{CX + 40:.1f} 250 {CX + 24:.1f} 296 "
                 f"Q{CX + 12:.1f} 322 {CX:.1f} 322 Q{CX - 12:.1f} 322 "
                 f"{CX - 24:.1f} 296 Q{CX - 40:.1f} 250 {CX:.1f} 196 Z",
                 fill=PAPER, fill_opacity=0.85))
    logs = (line(CX - 92, 372, CX + 92, 348, **stroke(d, 18)) +
            line(CX - 92, 348, CX + 92, 372, **stroke(d, 18)))
    glow = circle(CX, 300, 168, **wash(a, 0.10))
    folk = (person(CX - 196, 402, 0.62, d) + person(CX + 196, 402, 0.62, d) +
            person(CX, 462, 0.7, d))
    return glow + folk + logs + fire


def m_places_cave(a, d):
    mouth = path(f"M{CX - 186:.1f} 430 L{CX - 186:.1f} 276 "
                 f"Q{CX:.1f} 96 {CX + 186:.1f} 276 L{CX + 186:.1f} 430 Z",
                 fill=d)
    inner = path(f"M{CX - 128:.1f} 430 L{CX - 128:.1f} 292 "
                 f"Q{CX:.1f} 162 {CX + 128:.1f} 292 L{CX + 128:.1f} 430 Z",
                 fill=a, fill_opacity=0.35)
    tucked = person(CX, 428, 0.72, PAPER)
    lamp = circle(CX + 84, 356, 15, fill=PAPER, fill_opacity=0.8)
    return mouth + inner + tucked + lamp + ground(430, a)


def m_places_habitat(a, d):
    sky = "".join(path(f"M{74 + i * 16} {300 - i * 34} Q{CX:.1f} {110 - i * 40} "
                       f"{556 - i * 16} {300 - i * 34}",
                       **stroke(a, 5, stroke_opacity=0.5 - i * 0.14))
                  for i in range(3))
    land = (path("M40 328 Q170 244 316 322 Q452 396 590 300 L590 478 L40 478 Z",
                 **wash(a, 0.2)) +
            path("M40 404 Q200 350 372 404 Q486 442 590 400 L590 478 L40 478 Z",
                 **wash(d, 0.22)))
    # the four other places, small, sitting in the one landscape
    cave = (path("M112 400 L112 362 Q152 312 192 362 L192 400 Z", fill=d) +
            circle(152, 380, 11, fill=PAPER))
    fire = (path("M298 400 Q268 366 288 330 Q292 356 306 348 "
                 "Q296 322 318 306 Q312 348 330 360 Q344 376 330 400 Z",
                 fill=d) +
            line(262, 408, 340, 408, **stroke(d, 9)) +
            line(268, 416, 334, 400, **stroke(d, 7)))
    pool = (ellipse(406, 392, 56, 22, fill=d, fill_opacity=0.75) +
            ellipse(406, 392, 30, 12, **stroke(PAPER, 4)))
    book = (path("M488 402 L530 388 L572 402 L572 366 L530 352 L488 366 Z",
                 fill=d) +
            line(530, 352, 530, 388, **stroke(PAPER, 4)))
    hold = path("M62 470 Q60 232 316 218 Q572 232 570 470",
                **stroke(a, 8, stroke_dasharray="20 16", stroke_opacity=0.7))
    return sky + land + hold + cave + fire + pool + book


def m_places_library(a, d):
    shelf = ""
    for i, y in enumerate((150, 246)):
        shelf += rect(96, y + 66, 438, 12, 6, fill=d)
        x = 112
        for j, (bw, bh) in enumerate(((30, 66), (22, 54), (34, 72), (26, 60),
                                      (30, 50), (24, 68), (32, 58), (26, 64),
                                      (30, 70), (22, 52))):
            shelf += rect(x, y + 66 - bh, bw, bh, 4,
                          **wash(a, 0.4 + 0.12 * ((i + j) % 3)))
            x += bw + 8
            if x > 500:
                break
    bk = path(f"M{CX:.1f} 388 L{CX - 158:.1f} 356 Q{CX - 80:.1f} 336 "
              f"{CX:.1f} 358 Q{CX + 80:.1f} 336 {CX + 158:.1f} 356 "
              f"L{CX:.1f} 388 Z", fill=a)
    spine = line(CX, 358, CX, 388, **stroke(d, THIN))
    pages = path(f"M{CX - 158:.1f} 356 L{CX - 150:.1f} 428 "
                 f"Q{CX - 74:.1f} 406 {CX:.1f} 428 Q{CX + 74:.1f} 406 "
                 f"{CX + 150:.1f} 428 L{CX + 158:.1f} 356 "
                 f"Q{CX + 80:.1f} 336 {CX:.1f} 358 Q{CX - 80:.1f} 336 "
                 f"{CX - 158:.1f} 356 Z", fill=PAPER, stroke=d,
                 stroke_width=THIN)
    return shelf + bk + pages + spine


def m_places_watering_hole(a, d):
    pool = ellipse(CX, 372, 224, 88, fill=a, fill_opacity=0.32)
    rim = ellipse(CX, 372, 224, 88, **stroke(a, THIN, stroke_opacity=0.6))
    rip = (ellipse(CX, 372, 138, 54, **stroke(PAPER, 5, stroke_opacity=0.8)) +
           ellipse(CX, 372, 74, 29, **stroke(PAPER, 5, stroke_opacity=0.6)))
    folk = (person(CX - 196, 320, 0.66, d) + person(CX - 92, 292, 0.58, d) +
            person(CX + 150, 318, 0.7, d) + person(CX + 50, 288, 0.56, d))
    return pool + rim + rip + folk


def m_places_your_own(a, d):
    return blank_card_and_pencil(a, d)


# ------------------------------------------------------------------ weather

def m_weather_big_step(a, d):
    riser = rect(CX - 40, 96, 290, 334, 12, fill=a, fill_opacity=0.45)
    lip = rect(CX - 56, 96, 306, 26, 13, fill=d)
    tiny = person(CX - 150, 430, 0.5, d)
    look = arrow(CX - 150, 300, CX - 84, 158, d, THIN, 14)
    return ground(430, a) + riser + lip + tiny + look


def m_weather_bright(a, d):
    import math
    rays = "".join(
        line(CX + 118 * math.cos(math.radians(k)),
             236 + 118 * math.sin(math.radians(k)),
             CX + 182 * math.cos(math.radians(k)),
             236 + 182 * math.sin(math.radians(k)), **stroke(a, MAIN))
        for k in range(0, 360, 30))
    sun = circle(CX, 236, 92, fill=a)
    horizon = line(70, 420, 560, 420, **stroke(a, THIN, stroke_opacity=0.5))
    return rays + sun + horizon


def m_weather_buzzy(a, d):
    import math
    out = circle(CX, 262, 54, **wash(a, 0.3))
    for i, k in enumerate(range(6, 360, 29)):
        r0 = 74 + (i % 3) * 20
        r1 = r0 + 46 + (i % 4) * 14
        x0 = CX + r0 * math.cos(math.radians(k))
        y0 = 262 + r0 * math.sin(math.radians(k))
        x1 = CX + r1 * math.cos(math.radians(k))
        y1 = 262 + r1 * math.sin(math.radians(k))
        xm = (x0 + x1) / 2 + (18 if i % 2 else -18)
        ym = (y0 + y1) / 2 + (-14 if i % 2 else 14)
        out += poly([(x0, y0), (xm, ym), (x1, y1)],
                    **stroke(d if i % 2 else a, THIN))
    return out


def m_weather_cant_tell(a, d):
    haze = (circle(CX, 296, 138, **wash(a, 0.22)) +
            circle(CX, 296, 186, **wash(a, 0.1)))
    body = person(CX, 470, 1.15, d)
    q = path(f"M{CX - 34:.1f} 268 q0 -48 36 -48 q38 0 38 40 "
             f"q0 32 -36 46 l0 18", **stroke(PAPER, 17))
    dot = circle(CX + 2, 358, 11, fill=PAPER)
    fuzz = (circle(CX + 2, 292, 104, **stroke(a, 5, stroke_dasharray="10 16",
                                              stroke_opacity=0.55)))
    return ground(470, a) + haze + body + fuzz + q + dot


def m_weather_far_away(a, d):
    # A long view: floor lines running to a vanishing point, the person small
    # and pale at the far end of it, a near figure solid in the foreground.
    horizon = line(60, 258, 570, 258, **stroke(a, 5, stroke_opacity=0.4))
    floor = "".join(
        line(60 + i * 128, 500, CX - 40 + i * 20, 262,
             **stroke(a, 4, stroke_opacity=0.3)) for i in range(5))
    rungs = "".join(
        path(f"M{CX - (230 - i * 44):.1f} {480 - i * 54} "
             f"L{CX + (230 - i * 44):.1f} {480 - i * 54}",
             **stroke(a, 4, stroke_opacity=0.3 - i * 0.04)) for i in range(4))
    far = person(CX - 34, 258, 0.2, d, o=0.55)
    haze = circle(CX - 34, 240, 62, **wash(a, 0.16))
    near = person(CX + 4, 512, 0.9, d)
    return floor + rungs + horizon + haze + far + near


def m_weather_fizzy(a, d):
    glass = path(f"M{CX - 92:.1f} 172 L{CX - 70:.1f} 424 "
                 f"Q{CX:.1f} 444 {CX + 70:.1f} 424 L{CX + 92:.1f} 172 Z",
                 **stroke(d, MAIN))
    drink = path(f"M{CX - 82:.1f} 252 L{CX - 70:.1f} 424 "
                 f"Q{CX:.1f} 444 {CX + 70:.1f} 424 L{CX + 82:.1f} 252 Z",
                 **wash(a, 0.4))
    bub = ""
    for x, y, r in ((-46, 386, 13), (-12, 340, 9), (24, 368, 15), (52, 306, 10),
                    (-34, 292, 12), (8, 262, 8), (40, 222, 12), (-20, 196, 9),
                    (14, 150, 13), (-48, 128, 8), (44, 108, 10)):
        bub += circle(CX + x, y, r, **stroke(a if y > 250 else d, 5))
    return glass + drink + bub


def m_weather_foggy(a, d):
    shape = person(CX, 420, 1.0, d, o=0.3)
    bands = "".join(
        rect(46 + (i % 2) * 54, 190 + i * 52, 490 - (i % 2) * 90, 32, 16,
             **wash(a, 0.26 if i % 2 else 0.18))
        for i in range(6))
    return shape + bands


def m_weather_full(a, d):
    jar = path(f"M{CX - 112:.1f} 178 L{CX - 112:.1f} 402 "
               f"Q{CX - 112:.1f} 442 {CX - 72:.1f} 442 L{CX + 72:.1f} 442 "
               f"Q{CX + 112:.1f} 442 {CX + 112:.1f} 402 L{CX + 112:.1f} 178",
               **stroke(d, MAIN))
    lip = line(CX - 128, 178, CX + 128, 178, **stroke(d, MAIN))
    fill_ = path(f"M{CX - 101:.1f} 186 L{CX - 101:.1f} 402 "
                 f"Q{CX - 101:.1f} 431 {CX - 72:.1f} 431 L{CX + 72:.1f} 431 "
                 f"Q{CX + 101:.1f} 431 {CX + 101:.1f} 402 L{CX + 101:.1f} 186 "
                 f"Q{CX:.1f} 162 {CX - 101:.1f} 186 Z", fill=a,
                 fill_opacity=0.55)
    meniscus = path(f"M{CX - 101:.1f} 186 Q{CX:.1f} 156 {CX + 101:.1f} 186",
                    **stroke(a, THIN))
    drop = circle(CX + 128, 214, 11, fill=a, fill_opacity=0.6)
    return fill_ + jar + lip + meniscus + drop


def m_weather_happy_flappy(a, d):
    body = person(CX, 446, 1.0, d)
    flaps = (arm(CX, 446, 1.0, 92, -78, d) + arm(CX, 446, 1.0, -92, -78, d))
    blur = (motion(CX + 78, 300, a, 3, 26, 1, 16) +
            motion(CX - 78, 300, a, 3, 26, -1, 16))
    joy = (star4(CX - 150, 200, 22, a) + star4(CX + 156, 172, 17, a) +
           star4(CX + 54, 130, 14, a) + star4(CX - 62, 152, 11, a))
    return ground(446, a) + joy + blur + flaps + body


def m_weather_heavy(a, d):
    lid = (rect(56, 118, 518, 76, 30, fill=a, fill_opacity=0.55) +
           rect(56, 118, 518, 76, 30, **stroke(d, THIN, stroke_opacity=0.4)))
    press = "".join(arrow(120 + i * 78, 214, 120 + i * 78, 286, d, THIN, 14)
                    for i in range(6))
    small = person(CX, 470, 0.78, d)
    return lid + press + ground(470, a) + small


def m_weather_in_the_zone(a, d):
    glow = "".join(circle(CX, 296, 210 - i * 44, **wash(a, 0.08 + i * 0.05))
                   for i in range(4))
    body = person(CX, 452, 1.0, d)
    held = rect(CX - 62, 300, 124, 86, 12, fill=PAPER, stroke=d,
                stroke_width=THIN)
    hands = arm(CX, 452, 1.0, 44, -30, d) + arm(CX, 452, 1.0, -44, -30, d)
    return glow + body + hands + held


def m_weather_meerkat(a, d):
    body = path(f"M{CX:.1f} 178 Q{CX + 54:.1f} 196 {CX + 52:.1f} 292 "
                f"Q{CX + 48:.1f} 398 {CX + 26:.1f} 428 L{CX - 30:.1f} 428 "
                f"Q{CX - 50:.1f} 386 {CX - 46:.1f} 292 "
                f"Q{CX - 46:.1f} 198 {CX:.1f} 178 Z", fill=d)
    belly = path(f"M{CX + 2:.1f} 236 Q{CX + 30:.1f} 276 {CX + 26:.1f} 348 "
                 f"Q{CX + 22:.1f} 396 {CX + 4:.1f} 412 "
                 f"Q{CX - 16:.1f} 372 {CX - 14:.1f} 310 "
                 f"Q{CX - 12:.1f} 262 {CX + 2:.1f} 236 Z", **wash(a, 0.55))
    head = ellipse(CX + 2, 156, 46, 42, fill=d)
    ears = (circle(CX - 34, 130, 17, fill=d) + circle(CX + 40, 128, 17, fill=d))
    face = (eyes(CX + 2, 150, 20, 7, PAPER) +
            ellipse(CX + 2, 174, 9, 7, fill=PAPER))
    tail = path(f"M{CX + 46:.1f} 412 Q{CX + 122:.1f} 400 {CX + 120:.1f} 300",
                **stroke(d, 15))
    scan = (path(f"M{CX + 74:.1f} 110 Q{CX + 124:.1f} 136 {CX + 128:.1f} 186",
                 **stroke(a, 5, stroke_opacity=0.5)) +
            path(f"M{CX - 70:.1f} 110 Q{CX - 120:.1f} 136 {CX - 124:.1f} 186",
                 **stroke(a, 5, stroke_opacity=0.5)))
    return ground(428, a) + scan + tail + body + belly + ears + head + face


def m_weather_need_more(a, d):
    empty = (circle(CX + 96, 252, 176, **wash(a, 0.08)) +
             circle(CX + 96, 252, 176, **stroke(a, 4,
                                                stroke_dasharray="14 18",
                                                stroke_opacity=0.4)))
    body = person(CX - 140, 460, 0.94, d)
    reach = path(f"M{CX - 108:.1f} 368 Q{CX - 30:.1f} 330 {CX + 36:.1f} 292",
                 **stroke(d, 14))
    grasp = hand(CX + 70, 274, 0.48, a, d, rot=52)
    pull = "".join(
        path(f"M{CX + 132 + i * 34:.1f} {236 - i * 22:.1f} q36 -16 66 -6",
             **stroke(a, 5, stroke_opacity=0.6 - i * 0.16))
        for i in range(3))
    return ground(460, a) + empty + pull + reach + body + grasp


def m_weather_no_words_right_now(a, d):
    head = circle(CX, 244, 126, fill=d)
    ey = (circle(CX - 46, 220, 21, fill=PAPER) +
          circle(CX + 46, 220, 21, fill=PAPER) +
          circle(CX - 46, 220, 10, fill=d) + circle(CX + 46, 220, 10, fill=d) +
          circle(CX - 53, 212, 5, fill=PAPER) +
          circle(CX + 39, 212, 5, fill=PAPER))
    mouth = line(CX - 42, 306, CX + 42, 306, **stroke(PAPER, 10))
    # the voice, curled up quiet: a spiral inside a soft speech bubble that
    # stays closed rather than a word coming out.
    bubble = (path(f"M{CX - 118:.1f} 396 l236 0 q30 0 30 30 l0 62 "
                   f"q0 30 -30 30 l-236 0 q-30 0 -30 -30 l0 -62 "
                   f"q0 -30 30 -30 Z", **wash(a, 0.2)) +
              path(f"M{CX - 118:.1f} 396 l236 0 q30 0 30 30 l0 62 "
                   f"q0 30 -30 30 l-236 0 q-30 0 -30 -30 l0 -62 "
                   f"q0 -30 30 -30 Z", **stroke(a, THIN,
                                                stroke_dasharray="16 14")))
    import math
    pts = [(CX + (46 - i * 0.55) * math.cos(math.radians(i * 9)),
            457 + (46 - i * 0.55) * math.sin(math.radians(i * 9)))
           for i in range(0, 70)]
    curl = poly(pts, **stroke(d, THIN))
    return head + ey + mouth + bubble + curl


def m_weather_prickly(a, d):
    # Deliberately not a sun: a lumpy body with hard triangular thorns, and
    # small scratch marks around it. `bright` owns the radiating lines.
    import math
    blob = path(f"M{CX - 118:.1f} 272 q-14 -76 62 -102 q72 -26 128 18 "
                f"q58 46 34 116 q-24 68 -104 76 q-84 8 -114 -46 "
                f"q-18 -32 -6 -62 Z", fill=a, fill_opacity=0.55)
    edge = path(f"M{CX - 118:.1f} 272 q-14 -76 62 -102 q72 -26 128 18 "
                f"q58 46 34 116 q-24 68 -104 76 q-84 8 -114 -46 "
                f"q-18 -32 -6 -62 Z", **stroke(d, THIN))
    thorns = ""
    for i, k in enumerate(range(0, 360, 24)):
        t = math.radians(k)
        r0 = 108 + (i % 3) * 8
        r1 = r0 + 54 + (i % 2) * 16
        bx, by = CX + 6, 280
        tip = (bx + r1 * math.cos(t), by + r1 * math.sin(t))
        l = (bx + r0 * math.cos(t - 0.16), by + r0 * math.sin(t - 0.16))
        r = (bx + r0 * math.cos(t + 0.16), by + r0 * math.sin(t + 0.16))
        thorns += path(f"M{l[0]:.1f} {l[1]:.1f} L{tip[0]:.1f} {tip[1]:.1f} "
                       f"L{r[0]:.1f} {r[1]:.1f} Z", fill=d)
    scratch = "".join(line(96 + i * 150, 452 + (i % 2) * 22,
                           142 + i * 150, 486 + (i % 2) * 22,
                           **stroke(d, 5, stroke_opacity=0.4))
                      for i in range(3))
    return thorns + blob + edge + scratch


def m_weather_pulled_every_way(a, d):
    import math
    body = person(CX, 320, 0.62, d)
    pulls = ""
    for k in range(0, 360, 45):
        x0 = CX + 92 * math.cos(math.radians(k))
        y0 = 268 + 92 * math.sin(math.radians(k))
        x1 = CX + 204 * math.cos(math.radians(k))
        y1 = 268 + 204 * math.sin(math.radians(k))
        pulls += arrow(x0, y0, x1, y1, a, 8, 16)
    return pulls + body


def m_weather_round_and_round(a, d):
    import math
    pts = []
    for i in range(0, 1080, 6):
        t = math.radians(i)
        r = 196 - i * 0.165
        pts.append((CX + r * math.cos(t), 276 + r * math.sin(t)))
    return (poly(pts, **stroke(a, MAIN)) +
            circle(pts[-1][0], pts[-1][1], 10, fill=d))


def m_weather_running_on_empty(a, d):
    def spoon(x, y, rot, color, o=1.0):
        return group(ellipse(0, 0, 25, 34, fill=color, fill_opacity=o) +
                     rect(-7, 26, 14, 118, 7, fill=color, fill_opacity=o),
                     transform=f"translate({x:.1f} {y:.1f}) rotate({rot})")
    gone = "".join(spoon(112 + i * 62, 158, -12 + i * 6, a, 0.16)
                   for i in range(5))
    left = spoon(CX - 26, 212, -10, d) + spoon(CX + 40, 206, 9, d)
    wrist = path(f"M{CX + 6:.1f} 506 q-4 -44 0 -72", **stroke(a, 42,
                                                              stroke_opacity=0.7))
    return gone + left + wrist + hand(CX + 6, 388, 0.82, a, d)


def m_weather_stormy(a, d):
    cl = cloud(CX - 10, 200, 1.2, a, 0.75)
    bolt = path(f"M{CX + 12:.1f} 274 L{CX - 42:.1f} 366 L{CX - 2:.1f} 366 "
                f"L{CX - 34:.1f} 452 L{CX + 56:.1f} 344 L{CX + 12:.1f} 344 "
                f"L{CX + 52:.1f} 274 Z", fill=d)
    rain = "".join(line(120 + i * 58, 292 + (i % 3) * 18,
                        104 + i * 58, 348 + (i % 3) * 18,
                        **stroke(a, THIN, stroke_opacity=0.65))
                   for i in range(8) if i not in (3, 4))
    return cl + rain + bolt


def m_weather_tender(a, d):
    body = person(CX - 34, 448, 0.92, d)
    glow = (person(CX - 34, 452, 1.02, a, o=0.3) +
            person(CX - 34, 456, 1.1, a, o=0.14))
    pebble = circle(CX + 168, 216, 17, fill=d)
    fall = path(f"M{CX + 196:.1f} 140 Q{CX + 186:.1f} 178 {CX + 172:.1f} 198",
                **stroke(a, 5, stroke_opacity=0.6))
    land = ripples(CX + 150, 330, a, 3, 40, 26)
    return ground(452, a) + glow + body + land + fall + pebble


def m_weather_too_seen(a, d):
    import math
    small = person(CX, 344, 0.62, d)
    gazes = ""
    for k in range(0, 360, 60):
        x = CX + 208 * math.cos(math.radians(k))
        y = 282 + 190 * math.sin(math.radians(k))
        gazes += (ellipse(x, y, 34, 21, fill=a, fill_opacity=0.45) +
                  circle(x, y, 11, fill=d))
        gazes += line(x - 42 * math.cos(math.radians(k)),
                      y - 38 * math.sin(math.radians(k)),
                      CX + 76 * math.cos(math.radians(k) + math.pi),
                      282 + 70 * math.sin(math.radians(k) + math.pi),
                      **stroke(a, 4, stroke_opacity=0.35))
    fold = (path(f"M{CX - 54:.1f} 300 q22 26 0 48", **stroke(a, 5,
                                                             stroke_opacity=0.6)) +
            path(f"M{CX + 54:.1f} 300 q-22 26 0 48", **stroke(a, 5,
                                                              stroke_opacity=0.6)))
    return gazes + small + fold


def m_weather_warm(a, d):
    glow = "".join(circle(CX, 300, 214 - i * 46, **wash(a, 0.08 + i * 0.06))
                   for i in range(4))
    body = person(CX, 428, 0.84, d)
    blanket = path(f"M{CX - 118:.1f} 252 Q{CX:.1f} 206 {CX + 118:.1f} 252 "
                   f"L{CX + 138:.1f} 432 L{CX - 138:.1f} 432 Z",
                   fill=a, fill_opacity=0.7)
    hem = path(f"M{CX - 138:.1f} 424 q34 18 68 0 q34 -18 68 0 q34 18 68 0",
               **stroke(d, THIN, stroke_opacity=0.5))
    return glow + body + blanket + hem


def m_weather_your_own(a, d):
    return blank_card_and_pencil(a, d)


# --------------------------------------------------------------- what helps

def m_wh_a_big_squeeze(a, d):
    body = person(CX, 440, 1.0, d)
    wrap = path(f"M{CX - 108:.1f} 292 Q{CX:.1f} 266 {CX + 108:.1f} 292 "
                f"L{CX + 118:.1f} 398 Q{CX:.1f} 424 {CX - 118:.1f} 398 Z",
                fill=a, fill_opacity=0.65)
    seams = "".join(line(CX - 118 + i * 59, 300 - abs(i - 2) * 5,
                         CX - 118 + i * 59, 408 - abs(i - 2) * 6,
                         **stroke(d, 4, stroke_opacity=0.35))
                    for i in range(5))
    hugs = (arrow(CX - 214, 344, CX - 140, 344, d, 9, 16) +
            arrow(CX + 214, 344, CX + 140, 344, d, 9, 16))
    return ground(440, a) + hugs + body + wrap + seams


def m_wh_a_corner(a, d):
    back = path("M150 118 L150 396 L500 396 L500 118", **wash(a, 0.22))
    walls = (line(150, 118, 150, 400, **stroke(d, MAIN)) +
             line(150, 400, 500, 400, **stroke(d, MAIN)))
    floor = path("M150 400 L500 400 L560 470 L90 470 Z", **wash(a, 0.12))
    body = person(216, 396, 0.76, d)
    return back + floor + walls + body


def m_wh_a_den(a, d):
    roof = path(f"M{CX - 206:.1f} 268 Q{CX:.1f} 108 {CX + 206:.1f} 268 "
                f"Q{CX + 104:.1f} 240 {CX:.1f} 254 Q{CX - 104:.1f} 240 "
                f"{CX - 206:.1f} 268 Z", fill=a, fill_opacity=0.75)
    pole = line(CX, 254, CX, 296, **stroke(d, 8))
    under = circle(CX, 340, 130, **wash(a, 0.14))
    body = person(CX, 438, 0.76, d)
    return under + ground(438, a) + body + roof + pole


def m_wh_a_smell_that_helps(a, d):
    pot = path(f"M{CX - 84:.1f} 348 L{CX - 68:.1f} 436 "
               f"Q{CX - 20:.1f} 450 {CX + 28:.1f} 436 L{CX + 44:.1f} 348 Z",
               fill=a, fill_opacity=0.55)
    rim = line(CX - 96, 348, CX + 56, 348, **stroke(d, MAIN))
    sprig = (line(CX - 20, 348, CX - 20, 268, **stroke(d, 8)) +
             path(f"M{CX - 20:.1f} 306 q-36 -10 -48 -44", **stroke(d, 8)) +
             path(f"M{CX - 20:.1f} 290 q36 -12 48 -46", **stroke(d, 8)))
    curls = "".join(
        path(f"M{CX - 72 + i * 52:.1f} 234 q24 -32 0 -62 q-24 -30 0 -58",
             **stroke(a, THIN, stroke_opacity=0.7 - i * 0.14))
        for i in range(3))
    wrist = path(f"M{CX + 208:.1f} 452 q22 -44 4 -76", **stroke(a, 30,
                                                                  stroke_opacity=0.7))
    return (curls + sprig + pot + rim + wrist +
            hand(CX + 150, 344, 0.78, a, d, rot=-38))


def m_wh_a_snack_or_a_drink(a, d):
    cup = path(f"M{CX - 152:.1f} 262 L{CX - 130:.1f} 420 "
               f"Q{CX - 74:.1f} 440 {CX - 18:.1f} 420 L{CX + 4:.1f} 262 Z",
               fill=a, fill_opacity=0.5)
    cup_l = path(f"M{CX - 152:.1f} 262 L{CX - 130:.1f} 420 "
                 f"Q{CX - 74:.1f} 440 {CX - 18:.1f} 420 L{CX + 4:.1f} 262 Z",
                 **stroke(d, MAIN))
    lip = line(CX - 164, 262, CX + 16, 262, **stroke(d, MAIN))
    steam = "".join(path(f"M{CX - 118 + i * 48:.1f} 226 q18 -26 0 -50",
                         **stroke(a, 5, stroke_opacity=0.6))
                    for i in range(3))
    snack = (circle(CX + 126, 376, 62, fill=a, fill_opacity=0.55) +
             circle(CX + 126, 376, 62, **stroke(d, MAIN)) +
             circle(CX + 104, 356, 9, fill=d) +
             circle(CX + 150, 372, 9, fill=d) +
             circle(CX + 116, 404, 9, fill=d))
    return steam + cup + cup_l + lip + snack


def m_wh_a_steady_sound(a, d):
    import math
    pts = [(70 + i * 3, 276 + 86 * math.sin(math.radians(i * 3)))
           for i in range(164)]
    ghost = [(70 + i * 3, 276 + 86 * math.sin(math.radians(i * 3)))
             for i in range(164)]
    return (poly(ghost, **stroke(a, 24, stroke_opacity=0.18)) +
            poly(pts, **stroke(d, MAIN)) +
            line(70, 276, 562, 276, **stroke(a, 3, stroke_opacity=0.35)))


def m_wh_a_way_out(a, d):
    beam = path(f"M{CX - 34:.1f} 140 L{CX + 130:.1f} 140 L{CX + 262:.1f} 470 "
                f"L{CX - 186:.1f} 470 Z", **wash(a, 0.16))
    return beam + door(CX - 140, 140, 174, 304, a, d, True) + ground(444, a)


def m_wh_another_way_to_talk(a, d):
    board = (rect(298, 142, 262, 196, 14, fill=PAPER, stroke=d,
                  stroke_width=MAIN) +
             "".join(line(326, 190 + i * 42, 532 - (i % 2) * 66, 190 + i * 42,
                          **stroke(a, 8, stroke_opacity=0.55))
                     for i in range(3)))
    card = (rect(84, 150, 162, 204, 14, fill=a, fill_opacity=0.5) +
            rect(84, 150, 162, 204, 14, **stroke(d, MAIN)) +
            circle(165, 226, 36, fill=PAPER) +
            rect(112, 294, 106, 16, 8, **wash(d, 0.4)))
    return board + card + hand(212, 420, 0.78, a, d, rot=-30, point=True)


def m_wh_busy_hands(a, d):
    spin = group(
        "".join(group(rect(-26, -96, 52, 76, 22, fill=a, fill_opacity=0.7) +
                      rect(-26, -96, 52, 76, 22, **stroke(d, THIN)),
                      transform=f"rotate({k})")
                for k in (0, 120, 240)) +
        circle(0, 0, 26, fill=d),
        transform=f"translate({CX + 46:.1f} 232)")
    spins = (motion(CX + 46, 232, a, 3, 132, 1, 18) +
             motion(CX + 46, 232, a, 3, 132, -1, 18))
    wrist = path(f"M{CX - 172:.1f} 496 q22 -46 44 -70", **stroke(a, 32,
                                                                stroke_opacity=0.7))
    return spins + spin + wrist + hand(CX - 118, 400, 0.66, a, d, rot=-26)


def m_wh_dim_the_light(a, d):
    shade = path(f"M{CX - 130:.1f} 260 L{CX - 62:.1f} 140 L{CX + 62:.1f} 140 "
                 f"L{CX + 130:.1f} 260 Z", fill=a, fill_opacity=0.6)
    bulb = circle(CX, 282, 24, fill=a, fill_opacity=0.5)
    cord = line(CX, 140, CX, 96, **stroke(d, 6))
    dial = (path(f"M{CX - 118:.1f} 430 a118 118 0 0 1 236 0",
                 **stroke(a, 16, stroke_opacity=0.3)) +
            path(f"M{CX - 118:.1f} 430 a118 118 0 0 1 72 -109",
                 **stroke(d, 16)))
    knob = (circle(CX, 430, 30, fill=PAPER, stroke=d, stroke_width=THIN) +
            line(CX, 430, CX - 42, 356, **stroke(d, 9)))
    down = arrow(CX + 154, 340, CX + 154, 424, d, THIN, 14)
    return shade + cord + bulb + dial + knob + down


def m_wh_fewer_choices(a, d):
    many = "".join(rect(76 + i * 62, 180, 48, 188, 8,
                        fill=a, fill_opacity=0.16,
                        stroke=a, stroke_width=4, stroke_opacity=0.32)
                   for i in range(4))
    two = "".join(rect(384 + i * 94, 160, 76, 224, 10,
                       fill=a, fill_opacity=0.55, stroke=d, stroke_width=MAIN)
                  for i in range(2))
    knobs = "".join(circle(384 + i * 94 + 60, 272, 7, fill=d) for i in range(2))
    sweep = arrow(336, 248, 176, 248, d, 8, 16)
    return many + sweep + two + knobs + hand(342, 316, 0.6, a, d, rot=-14) + \
        ground(400, a)


def m_wh_headphones(a, d):
    band = path(f"M{CX - 148:.1f} 316 L{CX - 148:.1f} 254 "
                f"a148 148 0 0 1 296 0 L{CX + 148:.1f} 316",
                **stroke(d, 18))
    cups = (rect(CX - 186, 306, 78, 128, 32, fill=a, fill_opacity=0.7) +
            rect(CX - 186, 306, 78, 128, 32, **stroke(d, THIN)) +
            rect(CX + 108, 306, 78, 128, 32, fill=a, fill_opacity=0.7) +
            rect(CX + 108, 306, 78, 128, 32, **stroke(d, THIN)))
    quiet = "".join(
        path(f"M{CX - 218 - i * 30:.1f} {350 + i * 6:.1f} "
             f"q-16 22 0 44", **stroke(a, 5, stroke_opacity=0.45 - i * 0.14))
        for i in range(3))
    quiet += "".join(
        path(f"M{CX + 218 + i * 30:.1f} {350 + i * 6:.1f} "
             f"q16 22 0 44", **stroke(a, 5, stroke_opacity=0.45 - i * 0.14))
        for i in range(3))
    return quiet + band + cups


def m_wh_just_one_person(a, d):
    # Side by side, nothing drawn between the heads: two dots above a curve
    # reads as a face, and the curve reads as a frown.
    two = person(CX - 86, 440, 0.92, d) + person(CX + 86, 440, 0.92, a, o=0.8)
    near = path(f"M{CX - 30:.1f} 452 q30 14 60 0", **stroke(a, 8,
                                                            stroke_opacity=0.45))
    return ground(440, a) + two + near


def m_wh_keep_it_the_same(a, d):
    shelf = rect(84, 356, 462, 12, 6, fill=d)
    row = ""
    for i in range(3):
        x = 140 + i * 152
        row += (path(f"M{x - 34:.1f} 250 L{x - 26:.1f} 350 "
                     f"Q{x:.1f} 362 {x + 26:.1f} 350 L{x + 34:.1f} 250 Z",
                     fill=a, fill_opacity=0.5) +
                line(x - 42, 250, x + 42, 250, **stroke(d, THIN)) +
                path(f"M{x + 34:.1f} 276 q30 4 30 26 q0 22 -30 24",
                     **stroke(d, THIN)))
    pathline = path("M108 432 q104 -28 208 0 q104 28 208 0",
                    **stroke(a, 18, stroke_opacity=0.3))
    dots = "".join(circle(126 + i * 62, 432 - (0 if i % 2 else 8), 6,
                          fill=a, fill_opacity=0.6) for i in range(8))
    return row + shelf + pathline + dots


def m_wh_less_talking(a, d):
    big = path(f"M{CX - 178:.1f} 152 L{CX + 30:.1f} 152 q36 0 36 36 l0 104 "
               f"q0 36 -36 36 l-126 0 l-58 52 l6 -52 l-22 0 q-36 0 -36 -36 "
               f"l0 -104 q0 -36 36 -36 Z", **wash(a, 0.18))
    small = path(f"M{CX + 66:.1f} 300 l84 0 q30 0 30 30 l0 54 q0 30 -30 30 "
                 f"l-40 0 l-36 34 l4 -34 q-30 0 -30 -30 l0 -54 q0 -30 30 -30 Z",
                 fill=a, fill_opacity=0.65)
    small += path(f"M{CX + 66:.1f} 300 l84 0 q30 0 30 30 l0 54 q0 30 -30 30 "
                  f"l-40 0 l-36 34 l4 -34 q-30 0 -30 -30 l0 -54 q0 -30 30 -30 Z",
                  **stroke(d, THIN))
    face = (circle(CX - 74, 224, 76, fill=d) +
            eyes(CX - 74, 208, 28, 8, PAPER) +
            path(f"M{CX - 104:.1f} 262 q30 14 60 0", **stroke(PAPER, 8)))
    return big + face + small


def m_wh_less_to_look_at(a, d):
    busy = rect(70, 146, 228, 300, 12, fill=PAPER, stroke=d, stroke_width=THIN)
    import math
    for i in range(26):
        x = 88 + (i * 47) % 192
        y = 166 + (i * 71) % 262
        r = 8 + (i % 4) * 5
        if i % 3 == 0:
            busy += rect(x, y, r * 2, r * 1.6, 3, **wash(a, 0.75))
        elif i % 3 == 1:
            busy += circle(x + r, y + r, r, **wash(d, 0.5))
        else:
            busy += line(x, y, x + r * 2.4, y + r, **stroke(a, 5,
                                                            stroke_opacity=0.8))
    calm = (rect(332, 146, 228, 300, 12, fill=PAPER, stroke=d,
                 stroke_width=THIN) +
            rect(332, 146, 228, 300, 12, **wash(a, 0.1)) +
            circle(446, 296, 26, **wash(a, 0.4)))
    return busy + calm


def m_wh_let_me_come_and_go(a, d):
    dr = door(CX - 64, 150, 150, 286, a, d, True)
    loop = path(f"M{CX + 46:.1f} 400 q160 30 160 -80 q0 -96 -150 -60",
                **stroke(a, 9, stroke_dasharray="18 14"))
    out = person(CX + 172, 464, 0.5, d)
    back = arrow(CX + 96, 260, CX + 30, 260, d, 8, 15)
    return ground(444, a) + dr + loop + out + back


def m_wh_let_me_control_it(a, d):
    ticks = "".join(line(118 + i * 58, 210, 118 + i * 58, 230,
                         **stroke(a, 4, stroke_opacity=0.45)) for i in range(8))
    track = rect(96, 270, 438, 26, 13, **wash(a, 0.3))
    fill_ = rect(96, 270, 196, 26, 13, fill=a, fill_opacity=0.8)
    knob = (rect(256, 232, 70, 102, 20, fill=PAPER, stroke=d,
                 stroke_width=MAIN) +
            "".join(line(276 + i * 15, 254, 276 + i * 15, 312,
                         **stroke(a, 5, stroke_opacity=0.6)) for i in range(3)))
    wrist = path("M292 470 q-4 -46 0 -78", **stroke(a, 34,
                                                     stroke_opacity=0.7))
    return ticks + track + fill_ + knob + wrist + hand(292, 330, 0.72, a, d)


def m_wh_let_me_finish(a, d):
    book = (path(f"M{CX - 190:.1f} 168 L{CX - 190:.1f} 420 "
                 f"Q{CX - 96:.1f} 398 {CX:.1f} 420 Q{CX + 96:.1f} 398 "
                 f"{CX + 190:.1f} 420 L{CX + 190:.1f} 168 "
                 f"Q{CX + 96:.1f} 146 {CX:.1f} 168 Q{CX - 96:.1f} 146 "
                 f"{CX - 190:.1f} 168 Z", fill=PAPER, stroke=d,
                 stroke_width=MAIN) +
            line(CX, 168, CX, 420, **stroke(d, THIN)))
    text = "".join(line(CX - 160 + (0 if i < 4 else 186), 208 + (i % 4) * 34,
                        CX - 40 + (0 if i < 4 else 186), 208 + (i % 4) * 34,
                        **stroke(a, 6, stroke_opacity=0.45)) for i in range(8))
    mark = path(f"M{CX + 58:.1f} 140 L{CX + 116:.1f} 140 L{CX + 116:.1f} 336 "
                f"L{CX + 87:.1f} 306 L{CX + 58:.1f} 336 Z", fill=a)
    down = arrow(CX + 87, 96, CX + 87, 128, d, THIN, 13)
    return book + text + mark + down


def m_wh_let_me_stim(a, d):
    body = person(CX, 452, 1.0, d)
    swing = (motion(CX, 330, a, 3, 92, 1, 22) + motion(CX, 330, a, 3, 92, -1, 22))
    arms = arm(CX, 452, 1.0, 66, 26, d) + arm(CX, 452, 1.0, -66, 26, d)
    rock = path(f"M{CX - 96:.1f} 470 q96 34 192 0", **stroke(a, 9,
                                                             stroke_opacity=0.5))
    return swing + arms + body + rock


def m_wh_let_me_unmask(a, d):
    real = (circle(CX - 20, 246, 104, fill=d) +
            eyes(CX - 20, 228, 36, 11, PAPER) +
            path(f"M{CX - 52:.1f} 286 q32 20 64 0", **stroke(PAPER, 8)))
    ease = (path(f"M{CX - 152:.1f} 396 q66 -34 132 -6", **stroke(a, 9,
                                                                 stroke_opacity=0.5)))
    mask = group(
        ellipse(0, 0, 86, 106, fill=PAPER, stroke=d, stroke_width=THIN) +
        ellipse(0, 0, 86, 106, **wash(a, 0.28)) +
        path("M-40 -22 q18 -16 36 0", **stroke(d, 7)) +
        path("M12 -26 q18 -16 36 0", **stroke(d, 7)) +
        path("M-40 34 q38 34 76 -6", **stroke(d, 7)) +
        rect(-6, 100, 12, 118, 6, fill=d),
        transform=f"translate({CX + 150:.1f} 306) rotate(16)")
    return real + ease + mask


def m_wh_my_own_spot(a, d):
    mat = path(f"M{CX:.1f} 260 L{CX + 212:.1f} 356 L{CX:.1f} 452 "
               f"L{CX - 212:.1f} 356 Z", fill=a, fill_opacity=0.45)
    edge = path(f"M{CX:.1f} 260 L{CX + 212:.1f} 356 L{CX:.1f} 452 "
                f"L{CX - 212:.1f} 356 Z", **stroke(d, MAIN))
    inner = path(f"M{CX:.1f} 294 L{CX + 146:.1f} 356 L{CX:.1f} 418 "
                 f"L{CX - 146:.1f} 356 Z", **stroke(PAPER, THIN))
    flag = (line(CX, 356, CX, 168, **stroke(d, 9)) +
            path(f"M{CX:.1f} 176 L{CX + 104:.1f} 206 L{CX:.1f} 236 Z", fill=a))
    return mat + edge + inner + flag


def m_wh_no_rush(a, d):
    face = (circle(CX, 282, 152, fill=PAPER, stroke=d, stroke_width=MAIN) +
            circle(CX, 282, 152, **wash(a, 0.12)))
    ticks = "".join(line(CX, 282, CX, 282, **stroke(a, 1)) for _ in range(0))
    import math
    for k in range(0, 360, 30):
        x0 = CX + 122 * math.cos(math.radians(k))
        y0 = 282 + 122 * math.sin(math.radians(k))
        x1 = CX + 136 * math.cos(math.radians(k))
        y1 = 282 + 136 * math.sin(math.radians(k))
        ticks += line(x0, y0, x1, y1, **stroke(a, 5, stroke_opacity=0.5))
    hands = (line(CX, 282, CX, 196, **stroke(d, 11)) +
             line(CX, 282, CX + 66, 316, **stroke(d, 11)) +
             circle(CX, 282, 12, fill=d))
    slow = (path(f"M{CX + 168:.1f} 210 a168 168 0 0 1 44 106",
                 **stroke(a, 8, stroke_opacity=0.6)) +
            path(f"M{CX - 168:.1f} 210 a168 168 0 0 0 -44 106",
                 **stroke(a, 8, stroke_opacity=0.6)))
    return face + ticks + hands + slow


def m_wh_no_spotlight(a, d):
    beam = path(f"M{CX + 38:.1f} 130 L{CX + 98:.1f} 130 L{CX + 236:.1f} 430 "
                f"L{CX + 20:.1f} 430 Z", fill=a, fill_opacity=0.28)
    lamp = rect(CX + 34, 106, 68, 34, 10, fill=d)
    pool = ellipse(CX + 128, 430, 108, 26, fill=a, fill_opacity=0.35)
    body = person(CX - 176, 448, 0.8, d)
    calm = path(f"M{CX - 238:.1f} 466 q62 20 124 0", **stroke(a, 8,
                                                              stroke_opacity=0.45))
    return ground(448, a) + beam + lamp + pool + body + calm


def m_wh_one_thing_at_a_time(a, d):
    table = (rect(70, 356, 492, 18, 9, fill=d) +
             line(132, 374, 116, 462, **stroke(d, 12)) +
             line(500, 374, 516, 462, **stroke(d, 12)))
    thing = (rect(CX - 62, 252, 124, 104, 16, fill=a, fill_opacity=0.65) +
             rect(CX - 62, 252, 124, 104, 16, **stroke(d, MAIN)))
    clear = (line(150, 330, 250, 330, **stroke(a, 5, stroke_opacity=0.25)) +
             line(382, 330, 482, 330, **stroke(a, 5, stroke_opacity=0.25)))
    return clear + thing + table


def m_wh_parallel_existence(a, d):
    two = person(CX - 108, 452, 0.9, d) + person(CX + 108, 452, 0.9, d)
    b1 = (ellipse(CX - 132, 214, 72, 52, **wash(a, 0.4)) +
          circle(CX - 96, 266, 13, **wash(a, 0.4)))
    b2 = (ellipse(CX + 132, 200, 72, 52, **wash(a, 0.4)) +
          circle(CX + 96, 252, 13, **wash(a, 0.4)))
    inner = (circle(CX - 132, 214, 22, fill=d, fill_opacity=0.5) +
             rect(CX + 110, 182, 44, 36, 8, fill=d, fill_opacity=0.5))
    return ground(452, a) + two + b1 + b2 + inner


def m_wh_room_to_move(a, d):
    floor = (path("M76 448 L244 216 L460 216 L580 448 Z", **wash(a, 0.16)) +
             path("M76 448 L244 216 L460 216 L580 448 Z",
                  **stroke(a, 5, stroke_opacity=0.45)))
    loop = path("M196 410 q-52 -118 104 -140 q166 -24 184 78 q14 66 -84 82 "
                "q-100 16 -116 -40", **stroke(a, 13, stroke_dasharray="22 18"))
    body = person(336, 372, 0.66, d)
    swish = (motion(336, 306, a, 2, 50, 1, 20) +
             motion(336, 306, a, 2, 50, -1, 20))
    return floor + loop + swish + body


def m_wh_say_it_straight(a, d):
    curvy = path("M96 380 q70 -70 140 -10 q70 60 140 -20 q70 -80 140 10",
                 **stroke(a, 9, stroke_opacity=0.28,
                          stroke_dasharray="16 14"))
    straight = arrow(96, 240, 534, 240, d, 14, 24)
    return curvy + straight


def m_wh_sit_my_way(a, d):
    cushion = (ellipse(150, 396, 84, 46, fill=a, fill_opacity=0.6) +
               ellipse(150, 384, 84, 44, fill=a, fill_opacity=0.85) +
               ellipse(150, 384, 84, 44, **stroke(d, THIN)))
    stool = (ellipse(CX + 6, 322, 66, 24, fill=a, fill_opacity=0.8) +
             ellipse(CX + 6, 322, 66, 24, **stroke(d, THIN)) +
             path(f"M{CX - 26:.1f} 336 q32 62 64 0", **stroke(d, MAIN)) +
             ellipse(CX + 6, 420, 44, 16, **wash(a, 0.3)))
    stand = person(506, 428, 0.72, d)
    return ground(438, a) + cushion + stool + stand


def m_wh_something_different(a, d):
    # The familiar way: a path worn smooth, with the same things still on it.
    floor = line(54, 420, 340, 420, **stroke(d, THIN, stroke_opacity=0.32))
    # The worn path carries on past the fork: the familiar way is not closed.
    worn = path("M60 420 q116 -26 232 -2 q92 9 186 -2",
                **stroke(a, 20, stroke_opacity=0.24))
    same = ""
    for i in range(3):
        x = 116 + i * 96
        same += (rect(x - 27, 322, 54, 96, 13, fill=a, fill_opacity=0.34) +
                 line(x - 34, 322, x + 34, 322, **stroke(d, THIN)))
    # The new way: a branch off the same path, drawn at full weight.
    branch = path("M352 420 C452 418 500 350 506 268 C509 232 508 214 506 198",
                  **stroke(a, 15))
    tip = star4(506, 150, 62, a) + star4(506, 150, 26, PAPER)
    spark = (sparkle(404, 232, 23, a) + sparkle(590, 266, 17, a) +
             sparkle(428, 322, 13, a, w=5))
    return floor + worn + same + branch + tip + spark


def m_wh_something_soft(a, d):
    plush = (path(f"M{CX:.1f} 176 q112 0 112 112 q0 78 -52 112 "
                  f"q-60 38 -120 0 q-52 -34 -52 -112 q0 -112 112 -112 Z",
                  fill=a, fill_opacity=0.65) +
             circle(CX - 96, 214, 42, fill=a, fill_opacity=0.65) +
             circle(CX + 96, 214, 42, fill=a, fill_opacity=0.65))
    face = (eyes(CX, 278, 40, 11, d) +
            path(f"M{CX - 22:.1f} 322 q22 16 44 0", **stroke(d, 7)))
    hands = (path(f"M{CX - 150:.1f} 428 q0 -38 38 -38 l50 0 q38 0 38 38 "
                  f"q0 44 -44 44 l-42 0 q-44 0 -44 -44 Z", **wash(a, 0.45)) +
             path(f"M{CX + 24:.1f} 428 q0 -38 38 -38 l50 0 q38 0 38 38 "
                  f"q0 44 -44 44 l-42 0 q-44 0 -44 -44 Z", **wash(a, 0.45)))
    return plush + face + hands


def m_wh_something_to_chew(a, d):
    cord = (path(f"M{CX - 160:.1f} 132 q54 122 118 168", **stroke(d, 8)) +
            path(f"M{CX + 160:.1f} 132 q-54 122 -118 168", **stroke(d, 8)))
    bead = (circle(CX - 150, 132, 15, fill=a, fill_opacity=0.7) +
            circle(CX + 150, 132, 15, fill=a, fill_opacity=0.7))
    tube = group(rect(-48, -112, 96, 224, 48, fill=a, fill_opacity=0.8) +
                 rect(-48, -112, 96, 224, 48, **stroke(d, MAIN)) +
                 "".join(line(-30, -56 + i * 56, 30, -56 + i * 56,
                              **stroke(d, 6, stroke_opacity=0.4))
                         for i in range(3)),
                 transform=f"translate({CX:.1f} 380) rotate(-10)")
    return cord + bead + tube


def m_wh_tell_me_first(a, d):
    post = rect(CX - 9, 300, 18, 156, 9, fill=d)
    sign = (rect(CX - 156, 152, 312, 158, 20, fill=a, fill_opacity=0.55) +
            rect(CX - 156, 152, 312, 158, 20, **stroke(d, MAIN)))
    bang = (rect(CX - 13, 190, 26, 62, 13, fill=d) +
            circle(CX, 274, 15, fill=d))
    return ground(456, a) + post + sign + bang


def m_wh_the_right_temperature(a, d):
    blanket = (path("M84 212 q84 -26 168 0 l0 208 q-84 26 -168 0 Z",
                    fill=a, fill_opacity=0.6) +
               path("M84 212 q84 -26 168 0 l0 208 q-84 26 -168 0 Z",
                    **stroke(d, THIN)) +
               "".join(line(84, 254 + i * 44, 252, 228 + i * 44,
                            **stroke(d, 4, stroke_opacity=0.3))
                       for i in range(4)))
    fan = group("".join(group(path("M0 -16 q64 -46 92 -8 q22 30 -16 34 "
                                   "q-40 4 -76 -26 Z", fill=a,
                                   fill_opacity=0.7),
                              transform=f"rotate({k})")
                        for k in (0, 120, 240)) +
                circle(0, 0, 20, fill=d) +
                circle(0, 0, 120, **stroke(d, THIN)),
                transform="translate(452 276)")
    stand = (rect(444, 396, 16, 62, 8, fill=d) +
             rect(406, 452, 92, 16, 8, fill=d))
    return blanket + fan + stand


def m_wh_your_own(a, d):
    return blank_card_and_pencil(a, d)


# ---------------------------------------------------------------- lily pads

def water(y, a, o=0.16):
    return (rect(40, y, W - 80, 530 - y, 24, **wash(a, o)) +
            "".join(path(f"M{80 + (i % 2) * 40:.1f} {y + 40 + i * 30:.1f} "
                         f"q30 -14 60 0 q30 14 60 0",
                         **stroke(a, 4, stroke_opacity=0.4))
                    for i in range(3)))


def m_lp_all_done(a, d):
    ring = circle(CX, 282, 152, **stroke(a, 26, stroke_opacity=0.35))
    knot = path(f"M{CX - 152:.1f} 282 a152 152 0 1 1 152 152",
                **stroke(d, MAIN))
    tie = path(f"M{CX:.1f} 434 q-38 -34 0 -62 q38 28 0 62 Z", fill=d)
    tick = poly([(CX - 58, 282), (CX - 14, 326), (CX + 68, 234)],
                **stroke(d, MAIN))
    return ring + knot + tie + tick


def m_lp_coming_back(a, d):
    spot = (ellipse(168, 416, 84, 34, **wash(a, 0.4)) +
            ellipse(168, 416, 84, 34, **stroke(d, THIN,
                                               stroke_dasharray="14 12")))

    def foot(x, y, rot, color, o=1.0):
        return group(ellipse(0, 0, 30, 46, fill=color, fill_opacity=o) +
                     "".join(circle(-17 + i * 11, -52, 8, fill=color,
                                    fill_opacity=o) for i in range(4)),
                     transform=f"translate({x} {y}) rotate({rot})")

    away = (foot(300, 356, 20, a, 0.3) + foot(392, 306, 20, a, 0.22) +
            foot(482, 258, 20, a, 0.16))
    back = path("M520 212 q66 -84 -26 -128 q-96 -46 -186 30 q-86 68 -140 156",
                **stroke(a, 9, stroke_dasharray="18 14"))
    tip = arrow(196, 314, 172, 362, d, 8, 15)
    here = foot(168, 406, -6, d)
    return away + back + tip + spot + here


def m_lp_i_need_a_minute(a, d):
    pad = lilypad(CX, 396, 186, a, 0.75)
    lie = (circle(CX - 132, 322, 33, fill=d) +
           path(f"M{CX - 106:.1f} 352 q56 -22 112 -8 q44 12 52 -20 "
                f"q6 -24 30 -18 q22 6 16 30 q-16 56 -78 54 "
                f"q-70 -2 -132 6 q-26 2 -26 -20 q0 -20 26 -24 Z", fill=d))
    z = "".join(path(f"M{CX + 44 + i * 40:.1f} {268 - i * 52:.1f} "
                     f"l{34 - i * 6:.1f} 0 l{-34 + i * 6:.1f} {30 - i * 5:.1f} "
                     f"l{34 - i * 6:.1f} 0", **stroke(a, THIN - i))
                for i in range(3))
    return water(360, a) + pad + lie + z


def m_lp_i_want_to_stay_a_while(a, d):
    pad = lilypad(CX, 412, 200, a, 0.8)
    body = person(CX, 404, 0.86, d)
    cosy = (circle(CX, 330, 152, **wash(a, 0.14)) +
            path(f"M{CX - 96:.1f} 372 q96 -34 192 0", **stroke(a, 8,
                                                               stroke_opacity=0.5)))
    return water(376, a) + cosy + pad + body


def m_lp_not_yet(a, d):
    hush = "".join(path(f"M{CX - 166 - i * 34:.1f} {250 + i * 8:.1f} q-16 26 0 52",
                        **stroke(a, 5, stroke_opacity=0.45 - i * 0.12))
                   for i in range(3))
    return hush + open_palm(CX, 300, 1.0, a, d)


def m_lp_ready_now(a, d):
    here = lilypad(190, 424, 128, a, 0.55)
    there = lilypad(452, 372, 128, a, 0.85)
    foot = group(ellipse(0, 0, 34, 54, fill=d) +
                 "".join(circle(-20 + i * 13, -60, 9, fill=d) for i in range(4)),
                 transform="translate(400 330) rotate(14)")
    step = arrow(232, 330, 348, 296, d, 9, 17)
    return water(346, a) + here + there + step + foot


def m_lp_slowly(a, d):
    here = lilypad(150, 408, 118, a, 0.7)
    there = lilypad(490, 408, 118, a, 0.7)
    bridge = (path("M150 388 q170 -110 340 0", **stroke(a, 22,
                                                        stroke_opacity=0.35)) +
              path("M150 388 q170 -110 340 0", **stroke(d, THIN,
                                                        stroke_dasharray="4 24")))
    slow = "".join(circle(196 + i * 62, 352 - (0 if i in (0, 4) else 22) -
                          (10 if i in (1, 3) else 0), 9,
                          fill=d, fill_opacity=0.8) for i in range(5))
    return water(380, a) + here + there + bridge + slow


def m_lp_stuck(a, d):
    here = lilypad(146, 424, 118, a, 0.6)
    there = lilypad(494, 424, 118, a, 0.6)
    body = person(CX, 408, 0.8, d)
    # arms held out for balance, not raised in joy -- and a foot hovering
    # over water it has not committed to.
    arms = (path(f"M{CX - 26:.1f} 322 q-62 6 -84 34", **stroke(d, 12)) +
            path(f"M{CX + 26:.1f} 322 q62 6 84 34", **stroke(d, 12)))
    gap = "".join(line(238 + i * 40, 462, 262 + i * 40, 462,
                       **stroke(a, 6, stroke_opacity=0.55)) for i in range(4))
    sway = (path(f"M{CX - 118:.1f} 296 q16 -22 34 -6", **stroke(a, 5,
                                                                stroke_opacity=0.5)) +
            path(f"M{CX + 118:.1f} 296 q-16 -22 -34 -6", **stroke(a, 5,
                                                                  stroke_opacity=0.5)))
    return water(394, a) + here + there + gap + sway + arms + body


def m_lp_watch_first(a, d):
    crowd = ("".join(person(300 + i * 74, 396 + (i % 2) * 14, 0.66, a, o=0.5)
                     for i in range(4)))
    edge = person(150, 410, 0.74, d)
    look = (ellipse(150, 296, 40, 26, fill=PAPER, stroke=d, stroke_width=THIN) +
            circle(158, 296, 13, fill=d))
    sight = path("M198 296 q76 8 118 46", **stroke(a, 5,
                                                   stroke_dasharray="12 10"))
    return ground(424, a) + crowd + edge + look + sight


def m_lp_your_own(a, d):
    return blank_card_and_pencil(a, d)


# ------------------------------------------------------------------ growers

def m_gr_dandelion(a, d):
    import math
    slab = (rect(60, 400, 230, 76, 8, **wash(d, 0.28)) +
            rect(340, 400, 230, 76, 8, **wash(d, 0.28)))
    crack = path("M290 400 q14 34 0 76 M340 400 q-14 34 0 76",
                 **stroke(d, THIN, stroke_opacity=0.5))
    stem = path(f"M{CX:.1f} 404 q-14 -80 0 -132", **stroke(d, 9))
    leaves = (path(f"M{CX:.1f} 380 q-58 -6 -76 -44 q52 -10 76 44 Z", fill=d) +
              path(f"M{CX:.1f} 348 q58 -8 78 -46 q-54 -8 -78 46 Z", fill=d))
    head = circle(CX, 250, 24, fill=d)
    seeds = ""
    for k in range(0, 360, 20):
        x1 = CX + 84 * math.cos(math.radians(k))
        y1 = 250 + 84 * math.sin(math.radians(k))
        seeds += (line(CX + 24 * math.cos(math.radians(k)),
                       250 + 24 * math.sin(math.radians(k)), x1, y1,
                       **stroke(a, 4)) +
                  circle(x1, y1, 9, fill=a, fill_opacity=0.8))
    drift = "".join(circle(CX + 130 + i * 44, 200 - i * 34, 8 - i,
                           fill=a, fill_opacity=0.6 - i * 0.14)
                    for i in range(3))
    return slab + crack + stem + leaves + seeds + head + drift


def m_gr_orchid(a, d):
    pot = (path(f"M{CX - 86:.1f} 378 L{CX - 70:.1f} 468 "
                f"Q{CX:.1f} 482 {CX + 70:.1f} 468 L{CX + 86:.1f} 378 Z",
                fill=d) +
           rect(CX - 98, 358, 196, 26, 8, fill=d))
    stem = path(f"M{CX + 30:.1f} 358 q-40 -90 -10 -150", **stroke(d, 9))
    bloom = group(
        "".join(group(ellipse(0, -54, 34, 56, fill=a, fill_opacity=0.7),
                      transform=f"rotate({k})")
                for k in (0, 72, 144, 216, 288)) +
        circle(0, 0, 26, fill=d) + circle(0, 0, 11, fill=PAPER),
        transform=f"translate({CX + 20:.1f} 196)")
    bud = (circle(CX - 40, 268, 20, fill=a, fill_opacity=0.5) +
           circle(CX - 62, 314, 15, fill=a, fill_opacity=0.4))
    care = (rect(88, 132, 454, 366, 28, **stroke(a, THIN,
                                                 stroke_dasharray="16 16",
                                                 stroke_opacity=0.55)))
    return care + stem + bud + pot + bloom


def m_gr_tulip(a, d):
    bed = (rect(60, 412, 510, 66, 16, **wash(d, 0.22)) +
           "".join(line(96 + i * 68, 424, 96 + i * 68, 466,
                        **stroke(d, 4, stroke_opacity=0.3)) for i in range(8)))
    stem = line(CX, 412, CX, 274, **stroke(d, 11))
    leaves = (path(f"M{CX:.1f} 396 q-74 -22 -90 -102 q70 22 90 102 Z", fill=d) +
              path(f"M{CX:.1f} 360 q74 -24 92 -106 q-72 24 -92 106 Z", fill=d))
    cup = path(f"M{CX - 74:.1f} 258 q0 106 74 106 q74 0 74 -106 "
               f"q-26 34 -34 -6 q-16 44 -40 0 q-24 44 -40 0 q-8 40 -34 6 Z",
               fill=a, fill_opacity=0.85)
    outline = path(f"M{CX - 74:.1f} 258 q0 106 74 106 q74 0 74 -106 "
                   f"q-26 34 -34 -6 q-16 44 -40 0 q-24 44 -40 0 "
                   f"q-8 40 -34 6 Z", **stroke(d, THIN))
    return bed + stem + leaves + cup + outline


def m_gr_your_own(a, d):
    return blank_card_and_pencil(a, d)


# ---------------------------------------------------------------- kind words

def eye_shape(cx, cy, w, h, a, d, pupil=True):
    e = (path(f"M{cx - w:.1f} {cy:.1f} Q{cx:.1f} {cy - h:.1f} "
              f"{cx + w:.1f} {cy:.1f} Q{cx:.1f} {cy + h:.1f} "
              f"{cx - w:.1f} {cy:.1f} Z", fill=PAPER, stroke=d,
              stroke_width=MAIN))
    if pupil:
        e += (circle(cx, cy, h * 0.52, fill=a, fill_opacity=0.8) +
              circle(cx, cy, h * 0.24, fill=d))
    return e


def m_ll_i_see_you(a, d):
    left = eye_shape(CX - 132, 238, 108, 62, a, d)
    right = eye_shape(CX + 132, 238, 108, 62, a, d)
    # The line of sight runs between the eyes, at eye level. Under them it
    # would read as a mouth, and the pair would become a face.
    meet = line(CX - 40, 238, CX + 40, 238,
                **stroke(a, THIN, stroke_dasharray="14 12"))
    warm = (star4(CX, 400, 24, a) + star4(CX - 186, 384, 14, a) +
            star4(CX + 186, 384, 14, a))
    return left + right + meet + warm


def m_ll_im_glad_youre_here(a, d):
    glow = "".join(circle(CX, 316, 200 - i * 44, **wash(a, 0.08 + i * 0.05))
                   for i in range(4))
    # Two figures of different heights, overlapping, one arm reaching round
    # the back of the other. Deliberately NOT two same-size heads side by
    # side over a horizontal line -- that reads as a face, and the line reads
    # as a frown. Different sizes and head heights break the pattern.
    arm_behind = path(f"M{CX - 40:.1f} 396 Q{CX + 56:.1f} 368 "
                      f"{CX + 132:.1f} 402", **stroke(a, 15,
                                                      stroke_opacity=0.9))
    tall = person(CX - 66, 486, 1.06, d)
    short = person(CX + 74, 486, 0.72, d)
    spark = (star4(CX - 18, 160, 26, a) + star4(CX - 190, 214, 15, a) +
             star4(CX + 176, 196, 15, a))
    return glow + spark + arm_behind + tall + short


def m_ll_its_okay_to_need_what_you_need(a, d):
    bowl = path(f"M{CX - 200:.1f} 262 q0 176 200 176 q200 0 200 -176",
                **stroke(d, MAIN))
    space = path(f"M{CX - 200:.1f} 262 q0 176 200 176 q200 0 200 -176 Z",
                 **wash(a, 0.14))
    hands = (path(f"M{CX - 206:.1f} 272 q-46 -30 -76 6", **stroke(a, 13)) +
             path(f"M{CX + 206:.1f} 272 q46 -30 76 6", **stroke(a, 13)))
    # Varied shapes at varied heights -- three even dots over a wide curve
    # would read as a face, which this card is not.
    room = (circle(CX - 96, 322, 15, **wash(a, 0.45)) +
            rect(CX - 24, 350, 42, 32, 9, **wash(a, 0.4)) +
            path(f"M{CX + 96:.1f} 300 l30 26 l-30 26 l-30 -26 Z",
                 **wash(a, 0.5)))
    return space + bowl + hands + room


def m_ll_nothing_to_fix(a, d):
    whole = (circle(CX, 282, 150, fill=a, fill_opacity=0.5) +
             circle(CX, 282, 150, **stroke(d, MAIN)))
    calm = circle(CX, 282, 92, **stroke(PAPER, THIN))
    tool = group(rect(-13, -84, 26, 118, 13, fill=d, fill_opacity=0.28) +
                 circle(0, -96, 28, fill=d, fill_opacity=0.28) +
                 circle(0, -96, 13, fill=PAPER),
                 transform="translate(96 470) rotate(-74)")
    down = line(60, 486, 240, 486, **stroke(a, 5, stroke_opacity=0.4))
    return whole + calm + tool + down


def m_ll_you_belong_here(a, d):
    # An open palm held out flat, fingers toward the person, not a fist.
    body = person(468, 464, 0.92, d)
    arm_in = path("M40 346 q28 2 50 4", **stroke(a, 26, stroke_opacity=0.7))
    offer = open_palm(190, 354, 0.58, a, d, rot=92)
    toward = arrow(292, 354, 352, 354, a, 8, 16)
    warm = star4(252, 214, 17, a) + star4(166, 178, 12, a)
    return ground(464, a) + warm + arm_in + offer + toward + body


def m_ll_you_can_rest(a, d):
    mat = (rect(76, 320, 478, 118, 42, fill=a, fill_opacity=0.55) +
           rect(76, 320, 478, 118, 42, **stroke(d, THIN)))
    pillow = (rect(108, 268, 154, 82, 34, fill=PAPER, stroke=d,
                   stroke_width=THIN) +
              rect(108, 268, 154, 82, 34, **wash(a, 0.2)))
    fold = path("M300 356 q64 -22 128 0 q64 22 118 0", **stroke(d, THIN,
                                                                stroke_opacity=0.4))
    soft = "".join(path(f"M{206 + i * 108:.1f} 224 q18 -26 0 -50",
                        **stroke(a, 5, stroke_opacity=0.45)) for i in range(3))
    return soft + pillow + mat + fold


def m_ll_you_dont_have_to_talk(a, d):
    bubble = path(f"M{CX - 200:.1f} 190 l400 0 q40 0 40 40 l0 156 "
                  f"q0 40 -40 40 l-150 0 l-64 60 l8 -60 l-194 0 "
                  f"q-40 0 -40 -40 l0 -156 q0 -40 40 -40 Z",
                  **stroke(a, MAIN, stroke_dasharray="20 16"))
    inside = path(f"M{CX - 200:.1f} 190 l400 0 q40 0 40 40 l0 156 "
                  f"q0 40 -40 40 l-150 0 l-64 60 l8 -60 l-194 0 "
                  f"q-40 0 -40 -40 l0 -156 q0 -40 40 -40 Z", **wash(a, 0.08))
    calm = path(f"M{CX - 120:.1f} 308 q120 -40 240 0", **stroke(a, THIN,
                                                                stroke_opacity=0.45))
    return inside + bubble + calm


def m_ll_your_way_is_a_real_way(a, d):
    goal = circle(CX, 152, 32, fill=d)
    halo = circle(CX, 152, 62, **wash(a, 0.3))
    paths = ""
    for i, sx in enumerate((84, 196, 314, 434, 552)):
        paths += path(f"M{sx:.1f} 468 Q{sx + (CX - sx) * 0.35:.1f} 300 "
                      f"{CX:.1f} 214", **stroke(a, 9,
                                                stroke_opacity=0.45 + (i % 2) * 0.3))
    ticks = "".join(circle(sx, 468, 11, fill=d) for sx in (84, 196, 314, 434, 552))
    return paths + ticks + halo + goal


def m_ll_youre_not_broken(a, d):
    ring = circle(CX, 282, 158, **stroke(d, 30))
    inner = circle(CX, 282, 158, **stroke(a, 14, stroke_opacity=0.65))
    glow = circle(CX, 282, 158, **wash(a, 0.12))
    return glow + ring + inner


def m_ll_your_own(a, d):
    return blank_card_and_pencil(a, d)


# -------------------------------------------------------------------- blank

def m_blank_draw_your_own(a, d):
    return blank_card_and_pencil(a, d)


# ------------------------------------------------------------------ registry

MOTIFS = {
    ("places", "the-campfire"): m_places_campfire,
    ("places", "the-cave"): m_places_cave,
    ("places", "the-habitat"): m_places_habitat,
    ("places", "the-library"): m_places_library,
    ("places", "the-watering-hole"): m_places_watering_hole,
    ("places", "your-own"): m_places_your_own,

    ("weather", "big-step"): m_weather_big_step,
    ("weather", "bright"): m_weather_bright,
    ("weather", "buzzy"): m_weather_buzzy,
    ("weather", "cant-tell"): m_weather_cant_tell,
    ("weather", "far-away"): m_weather_far_away,
    ("weather", "fizzy"): m_weather_fizzy,
    ("weather", "foggy"): m_weather_foggy,
    ("weather", "full"): m_weather_full,
    ("weather", "happy-flappy"): m_weather_happy_flappy,
    ("weather", "heavy"): m_weather_heavy,
    ("weather", "in-the-zone"): m_weather_in_the_zone,
    ("weather", "meerkat"): m_weather_meerkat,
    ("weather", "need-more"): m_weather_need_more,
    ("weather", "no-words-right-now"): m_weather_no_words_right_now,
    ("weather", "prickly"): m_weather_prickly,
    ("weather", "pulled-every-way"): m_weather_pulled_every_way,
    ("weather", "round-and-round"): m_weather_round_and_round,
    ("weather", "running-on-empty"): m_weather_running_on_empty,
    ("weather", "stormy"): m_weather_stormy,
    ("weather", "tender"): m_weather_tender,
    ("weather", "too-seen"): m_weather_too_seen,
    ("weather", "warm"): m_weather_warm,
    ("weather", "your-own"): m_weather_your_own,

    ("what-helps", "a-big-squeeze"): m_wh_a_big_squeeze,
    ("what-helps", "a-corner"): m_wh_a_corner,
    ("what-helps", "a-den"): m_wh_a_den,
    ("what-helps", "a-smell-that-helps"): m_wh_a_smell_that_helps,
    ("what-helps", "a-snack-or-a-drink"): m_wh_a_snack_or_a_drink,
    ("what-helps", "a-steady-sound"): m_wh_a_steady_sound,
    ("what-helps", "a-way-out"): m_wh_a_way_out,
    ("what-helps", "another-way-to-talk"): m_wh_another_way_to_talk,
    ("what-helps", "busy-hands"): m_wh_busy_hands,
    ("what-helps", "dim-the-light"): m_wh_dim_the_light,
    ("what-helps", "fewer-choices"): m_wh_fewer_choices,
    ("what-helps", "headphones"): m_wh_headphones,
    ("what-helps", "just-one-person"): m_wh_just_one_person,
    ("what-helps", "keep-it-the-same"): m_wh_keep_it_the_same,
    ("what-helps", "less-talking"): m_wh_less_talking,
    ("what-helps", "less-to-look-at"): m_wh_less_to_look_at,
    ("what-helps", "let-me-come-and-go"): m_wh_let_me_come_and_go,
    ("what-helps", "let-me-control-it"): m_wh_let_me_control_it,
    ("what-helps", "let-me-finish"): m_wh_let_me_finish,
    ("what-helps", "let-me-stim"): m_wh_let_me_stim,
    ("what-helps", "let-me-unmask"): m_wh_let_me_unmask,
    ("what-helps", "my-own-spot"): m_wh_my_own_spot,
    ("what-helps", "no-rush"): m_wh_no_rush,
    ("what-helps", "no-spotlight"): m_wh_no_spotlight,
    ("what-helps", "one-thing-at-a-time"): m_wh_one_thing_at_a_time,
    ("what-helps", "parallel-existence"): m_wh_parallel_existence,
    ("what-helps", "room-to-move"): m_wh_room_to_move,
    ("what-helps", "say-it-straight"): m_wh_say_it_straight,
    ("what-helps", "sit-my-way"): m_wh_sit_my_way,
    ("what-helps", "something-different"): m_wh_something_different,
    ("what-helps", "something-soft"): m_wh_something_soft,
    ("what-helps", "something-to-chew"): m_wh_something_to_chew,
    ("what-helps", "tell-me-first"): m_wh_tell_me_first,
    ("what-helps", "the-right-temperature"): m_wh_the_right_temperature,
    ("what-helps", "your-own"): m_wh_your_own,

    ("lily-pad", "all-done"): m_lp_all_done,
    ("lily-pad", "coming-back"): m_lp_coming_back,
    ("lily-pad", "i-need-a-minute"): m_lp_i_need_a_minute,
    ("lily-pad", "i-want-to-stay-a-while"): m_lp_i_want_to_stay_a_while,
    ("lily-pad", "not-yet"): m_lp_not_yet,
    ("lily-pad", "ready-now"): m_lp_ready_now,
    ("lily-pad", "slowly"): m_lp_slowly,
    ("lily-pad", "stuck"): m_lp_stuck,
    ("lily-pad", "watch-first"): m_lp_watch_first,
    ("lily-pad", "your-own"): m_lp_your_own,

    ("grower", "dandelion"): m_gr_dandelion,
    ("grower", "orchid"): m_gr_orchid,
    ("grower", "tulip"): m_gr_tulip,
    ("grower", "your-own"): m_gr_your_own,

    ("love-locution", "i-see-you"): m_ll_i_see_you,
    ("love-locution", "im-glad-youre-here"): m_ll_im_glad_youre_here,
    ("love-locution", "its-okay-to-need-what-you-need"):
        m_ll_its_okay_to_need_what_you_need,
    ("love-locution", "nothing-to-fix"): m_ll_nothing_to_fix,
    ("love-locution", "you-belong-here"): m_ll_you_belong_here,
    ("love-locution", "you-can-rest"): m_ll_you_can_rest,
    ("love-locution", "you-dont-have-to-talk"): m_ll_you_dont_have_to_talk,
    ("love-locution", "your-way-is-a-real-way"): m_ll_your_way_is_a_real_way,
    ("love-locution", "youre-not-broken"): m_ll_youre_not_broken,
    ("love-locution", "your-own"): m_ll_your_own,

    ("blank", "draw-your-own"): m_blank_draw_your_own,
}


def missing(families):
    """(family, slug) pairs in `families` that have no motif yet.

    families: {family_slug: [card_slug, ...]}. Used by build-placeholders.py to
    fail loudly when a card is added without art, rather than shipping a blank.
    """
    return [(f, c) for f, cards in families.items() for c in cards
            if (f, c) not in MOTIFS]


def draw(family, slug, accent, dark):
    """SVG for one card's art window, in the window's local coordinates.

    Returns None when there is no motif for this card, so the caller can decide
    what to do about it.
    """
    fn = MOTIFS.get((family, slug))
    if fn is None:
        return None
    return group(fn(accent, dark), stroke_linecap="round",
                 stroke_linejoin="round")


if __name__ == "__main__":
    # Contact sheet: every motif on one page, for eyeballing the set at once.
    import pathlib
    cols, cell = 8, 230
    fams = {"places": ("#534AB7", "#26215C"), "weather": ("#BA7517", "#412402"),
            "what-helps": ("#0F6E56", "#04342C"), "lily-pad": ("#3B6D11", "#173404"),
            "grower": ("#993556", "#4B1528"),
            "love-locution": ("#993C1D", "#4A1B0C"), "blank": ("#5F5E5A", "#2C2C2A")}
    items = list(MOTIFS.items())
    rows = (len(items) + cols - 1) // cols
    body = []
    for i, ((fam, slug), fn) in enumerate(items):
        acc, dk = fams[fam]
        x, y = (i % cols) * cell, (i // cols) * (cell + 26)
        s = (cell - 16) / W
        body.append(
            f'<g transform="translate({x + 8} {y + 8}) scale({s:.4f})">'
            f'<rect x="0" y="0" width="{W}" height="{H}" fill="{PAPER}" '
            f'stroke="{acc}" stroke-width="4"/>'
            f'{draw(fam, slug, acc, dk)}</g>'
            f'<text x="{x + 8}" y="{y + 8 + (H * s) + 16}" font-size="11" '
            f'font-family="sans-serif" fill="#555">{slug}</text>')
    out = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{cols * cell}" '
           f'height="{rows * (cell + 26)}" viewBox="0 0 {cols * cell} '
           f'{rows * (cell + 26)}"><rect width="100%" height="100%" '
           f'fill="#ffffff"/>{"".join(body)}</svg>')
    dest = pathlib.Path("/tmp/cavendish-contact-sheet.svg")
    dest.write_text(out, encoding="utf-8")
    print(f"{len(items)} motifs -> {dest}")
