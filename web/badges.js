/* Interaction badges — Cavendish Cards.
 *
 * Makes printable interaction badges at the standard conference badge sizes
 * from the deck's own Interaction realm, lays them out on a sheet, and hands
 * back SVG you can print at home or send to a print shop.
 *
 * Three rules this file exists to keep:
 *
 *   1. The badge is worn, so it is the one part of the deck that is meant to
 *      be seen. Everything else in the deck lies face-down until its person
 *      turns it up. That is why these have a maker and the other realms don't.
 *   2. Color is never alone. Every signal carries a shape and a word as well,
 *      because a badge read across a room, in bad light, by a colorblind
 *      person, still has to say the same thing.
 *   3. Nothing leaves the browser. A logo the user picks is read with
 *      FileReader and embedded in the SVG here; it is never uploaded, and
 *      there is nowhere for it to be uploaded to.
 *
 * Units: SVG user units are PostScript points (72 to the inch) throughout, and
 * every root <svg> carries a physical width/height in inches. So a badge that
 * says 3 x 4 in is 3 x 4 in on paper, provided the print dialog is set to 100%
 * rather than "fit to page".
 *
 * Geometry is proportional rather than hard-coded, because the four badge
 * sizes do not share an aspect ratio (3:4, 2:3, 74:105, 105:148). Everything
 * below scales from the badge's own width and height, with one deliberate
 * exception: the punch holes. A quarter-inch hole a third of an inch from the
 * top is a fact about hole punches, not about badges, so it stays fixed at
 * every size.
 */
(function () {
  "use strict";

  var STORE = "cavendish.badges.v2";
  var MM = 72 / 25.4;

  /* ---- the signals -------------------------------------------------------
   * Names and prompts are copied from cards/interaction/*.md and must stay
   * word-for-word identical to them: the badge and the card are the same
   * thing in two materials. `word` is the color name the convention is known
   * by, kept because people arrive already knowing "red badge" even when they
   * have never seen this deck.
   */
  var SIGNALS = [
    {
      id: "come-say-hi", name: "come say hi", word: "green",
      prompt: "i want to talk — you can start.",
      shape: "circle", color: "#1E8E3E"
    },
    {
      id: "people-i-know", name: "people i know", word: "yellow",
      prompt: "only say hi if we've met.",
      shape: "triangle", color: "#EAB308"
    },
    {
      id: "not-right-now", name: "not right now", word: "red",
      prompt: "please don't start talking to me.",
      shape: "square", color: "#D64541"
    },
    {
      id: "ive-got-this", name: "i've got this", word: "neutral",
      prompt: "i can do my own hellos.",
      shape: "diamond", color: "#FFFFFF", ink: "#2C2C2A", outline: true
    },
    {
      id: "ask-first", name: "ask first", word: "orange",
      prompt: "ask before you touch me.",
      shape: "star", color: "#E8730C"
    },
    {
      id: "your-own", name: "your own", word: "blank",
      prompt: "Your own signal.",
      shape: "blank", color: "#5F5E5A"
    }
  ];

  var DEFAULT_ON = ["come-say-hi", "people-i-know", "not-right-now"];

  /* Paper, in points. */
  var PAPER = {
    letter: { w: 612, h: 792, label: "US Letter", css: "8.5in 11in" },
    a4:     { w: 595.28, h: 841.89, label: "A4", css: "210mm 297mm" }
  };

  /* The four standard conference badge sizes, stored PORTRAIT (short side
   * first) and flipped for landscape. Each is a real off-the-shelf holder and
   * insert size, so a badge made here fits something you can buy. */
  var SIZES = [
    {
      id: "4x3", label: "4 × 3 in", w: 3 * 72, h: 4 * 72,
      metric: "76 × 102 mm",
      note: "The common one, and the one that stacks and flips best on rings. " +
            "Day events, meetups, quick check-in."
    },
    {
      id: "a7", label: "A7", w: 74 * MM, h: 105 * MM,
      metric: "74 × 105 mm · 2.9 × 4.1 in",
      note: "The smaller European size. Minimal, and it fits the narrow lanyard " +
            "holders common at UK and EU conferences."
    },
    {
      id: "a6", label: "A6", w: 105 * MM, h: 148 * MM,
      metric: "105 × 148 mm · 4.1 × 5.8 in",
      note: "The European classic conference pass. Roomy, and readable much " +
            "further across a hall."
    },
    {
      id: "4x6", label: "4 × 6 in", w: 4 * 72, h: 6 * 72,
      metric: "102 × 152 mm",
      note: "The big one, for multi-day conferences. A signal this size is " +
            "readable down a corridor, with room under it for a name."
    }
  ];

  var BLEED = 9;        /* 0.125 in — what a print shop trims off */
  var MIN_MARGIN = 18;  /* 0.25 in — under this, a desk printer clips */
  var HOLE_R = 9;       /* 0.25 in hole: a fact about punches, not badges */
  var HOLE_Y = 24;      /* 0.33 in down from the top edge */
  var PAPER_INK = "#fdf6e3";
  var INK = "#002b36";
  var MUTED = "#586e75";
  var RULE = "#d9d2bc";
  var CUT = "#b9b3a0";

  /* ---- small helpers ---------------------------------------------------- */

  function esc(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  function n(v) { return Math.round(v * 100) / 100; }

  function inches(pt) { return Math.round(pt / 72 * 100) / 100; }
  function mm(pt) { return Math.round(pt / MM); }

  /* Width estimate for Atkinson Hyperlegible. Good to a few percent, which is
   * all centered text needs. Used to shrink a long event name rather than let
   * it run off the badge. */
  function textWidth(s, size, bold) {
    return String(s).length * size * (bold ? 0.60 : 0.545);
  }

  function fitSize(s, maxWidth, desired, min, bold) {
    var size = desired;
    while (size > min && textWidth(s, size, bold) > maxWidth) size -= 0.5;
    return size;
  }

  function wrap(s, maxWidth, size) {
    var words = String(s).split(/\s+/), lines = [], line = "";
    for (var i = 0; i < words.length; i++) {
      var test = line ? line + " " + words[i] : words[i];
      if (line && textWidth(test, size) > maxWidth) { lines.push(line); line = words[i]; }
      else line = test;
    }
    if (line) lines.push(line);
    return lines;
  }

  function byId(id) { return document.getElementById(id); }

  function signal(id) {
    for (var i = 0; i < SIGNALS.length; i++) if (SIGNALS[i].id === id) return SIGNALS[i];
    return null;
  }

  function sizeDef(id) {
    for (var i = 0; i < SIZES.length; i++) if (SIZES[i].id === id) return SIZES[i];
    return SIZES[0];
  }

  /* Trim size in points for a size id and orientation. */
  function dims(id, orient) {
    var s = sizeDef(id);
    return orient === "landscape" ? { w: s.h, h: s.w } : { w: s.w, h: s.h };
  }

  function sizeLabel(id, orient) {
    return sizeDef(id).label + " " + orient;
  }

  /* ---- the shapes -------------------------------------------------------
   * White on the signal color, with the same geometry as the card faces in
   * assets/cards/interaction/. The shape is not decoration: it is the half of
   * the signal that survives being colorblind, or photocopied in gray.
   *
   * The scale factors even the shapes out by area. At equal circumradius a
   * triangle covers 1.3r2 against a circle's 3.14r2, so a set drawn without
   * them reads as a big circle beside a small triangle.
   */
  var SHAPE_SCALE = {
    circle: 1, square: 1.08, triangle: 1.22, diamond: 1.15, star: 1.14, blank: 1.06
  };

  function shape(kind, cx, cy, r, sig, k) {
    r = r * (SHAPE_SCALE[kind] || 1);
    var fill = "#ffffff";
    var stroke = sig.outline ? sig.ink : "#00000033";
    var sw = (sig.outline ? 3 : 1.5) * k;
    var pts, i, a;
    if (kind === "circle") {
      return '<circle cx="' + n(cx) + '" cy="' + n(cy) + '" r="' + n(r) +
        '" fill="' + fill + '" stroke="' + stroke + '" stroke-width="' + n(sw) + '"/>';
    }
    if (kind === "square") {
      var s = r * 1.6;
      return '<rect x="' + n(cx - s / 2) + '" y="' + n(cy - s / 2) + '" width="' + n(s) +
        '" height="' + n(s) + '" rx="' + n(s * 0.06) + '" fill="' + fill +
        '" stroke="' + stroke + '" stroke-width="' + n(sw) + '"/>';
    }
    if (kind === "triangle") {
      pts = [];
      for (i = 0; i < 3; i++) {
        a = -Math.PI / 2 + i * 2 * Math.PI / 3;
        pts.push(n(cx + r * Math.cos(a)) + "," + n(cy + r * 0.98 * Math.sin(a) + r * 0.08));
      }
      return '<polygon points="' + pts.join(" ") + '" fill="' + fill + '" stroke="' + stroke +
        '" stroke-width="' + n(sw) + '" stroke-linejoin="round"/>';
    }
    if (kind === "diamond") {
      pts = [[cx, cy - r], [cx + r, cy], [cx, cy + r], [cx - r, cy]]
        .map(function (p) { return n(p[0]) + "," + n(p[1]); });
      return '<polygon points="' + pts.join(" ") + '" fill="' + fill + '" stroke="' + stroke +
        '" stroke-width="' + n(sw) + '" stroke-linejoin="round"/>';
    }
    if (kind === "star") {
      pts = [];
      for (i = 0; i < 10; i++) {
        a = -Math.PI / 2 + i * Math.PI / 5;
        var rr = (i % 2 === 0) ? r : r * 0.45;
        pts.push(n(cx + rr * Math.cos(a)) + "," + n(cy + rr * Math.sin(a)));
      }
      return '<polygon points="' + pts.join(" ") + '" fill="' + fill + '" stroke="' + stroke +
        '" stroke-width="' + n(sw) + '" stroke-linejoin="round"/>';
    }
    /* blank: a panel to draw your own signal into, with a visible edge so the
     * wearer knows where the drawing goes. */
    var b = r * 1.8;
    return '<rect x="' + n(cx - b / 2) + '" y="' + n(cy - b / 2) + '" width="' + n(b) +
      '" height="' + n(b) + '" rx="' + n(8 * k) + '" fill="#fdf6e3" stroke="#ffffff" ' +
      'stroke-width="' + n(3 * k) + '" stroke-dasharray="' + n(9 * k) + " " + n(7 * k) + '"/>';
  }

  /* ---- where everything sits on a badge ---------------------------------
   * One function, so the eight size-and-orientation combinations cannot drift
   * apart. `k` is the typographic scale: width-driven in portrait, because the
   * width is what text has to fit across; height-driven in landscape, because
   * there the bands are what run out of room first.
   */
  function layout(W, H, landscape) {
    if (landscape) {
      var k = H / 216;
      var m = W * 0.042;
      var top = Math.max(46 * k, HOLE_Y + HOLE_R + 10);
      var panel = { x: m, y: top, w: W * 0.389, h: H - top - 12 * k };
      return {
        k: k, landscape: true, panel: panel,
        holes: [W / 3, 2 * W / 3],
        cx: panel.x + panel.w / 2, cy: panel.y + panel.h / 2,
        r: Math.min(panel.w, panel.h) * 0.41,
        colX: m + panel.w + 14 * k, colW: W - m - (m + panel.w + 14 * k),
        anchor: "start",
        wordY: top + 46 * k, nameY: top + 74 * k, promptY: top + 94 * k,
        ruleY: H - 44 * k, bandY: H - 38 * k
      };
    }
    var kp = W / 216;
    var mp = W * 0.056;
    var topP = Math.max(44 * kp, HOLE_Y + HOLE_R + 10);
    var lower = 96 * kp;            /* word, name, prompt, rule, band */
    var panelP = { x: mp, y: topP, w: W - 2 * mp, h: H - topP - lower };
    var base = panelP.y + panelP.h;
    return {
      k: kp, landscape: false, panel: panelP,
      holes: [W * 0.25, W * 0.75],
      cx: W / 2, cy: panelP.y + panelP.h / 2,
      r: Math.min(panelP.w, panelP.h) * 0.36,
      colX: W / 2, colW: W - 2 * mp, anchor: "middle",
      wordY: base + 14 * kp, nameY: base + 38 * kp, promptY: base + 54 * kp,
      ruleY: base + 62 * kp, bandY: base + 66 * kp
    };
  }

  /* ---- one badge --------------------------------------------------------
   * Returns a <g> translated to (x, y), drawn in the badge's own space.
   * Layout follows the card face: a colored panel carrying the shape, then
   * the name and prompt in dark ink on the deck's paper color, then a band
   * for whoever is running the event. Text is never white on color — at badge
   * sizes that is where contrast quietly fails.
   */
  function badge(sig, o, x, y) {
    var d = dims(o.size, o.orient), W = d.w, H = d.h;
    var L = layout(W, H, o.orient === "landscape"), k = L.k;
    var g = [];

    g.push('<rect x="0" y="0" width="' + n(W) + '" height="' + n(H) + '" fill="' +
      PAPER_INK + '"/>');

    if (o.holes) {
      for (var i = 0; i < L.holes.length; i++) {
        g.push('<circle cx="' + n(L.holes[i]) + '" cy="' + HOLE_Y + '" r="' + HOLE_R +
          '" fill="none" stroke="' + CUT + '" stroke-width="1" stroke-dasharray="3 3"/>');
        g.push('<circle cx="' + n(L.holes[i]) + '" cy="' + HOLE_Y + '" r="1" fill="' +
          CUT + '"/>');
      }
    }

    g.push('<rect x="' + n(L.panel.x) + '" y="' + n(L.panel.y) + '" width="' + n(L.panel.w) +
      '" height="' + n(L.panel.h) + '" rx="' + n(10 * k) + '" fill="' + sig.color + '"' +
      (sig.outline ? ' stroke="' + sig.ink + '" stroke-width="' + n(2 * k) + '"' : '') + '/>');
    g.push(shape(sig.shape, L.cx, L.cy, L.r, sig, k));

    g.push(txt(sig.word, L.colX, L.wordY, 10 * k, MUTED, L.anchor, false,
      'letter-spacing="' + n(2 * k) + '"'));
    g.push(txt(sig.name, L.colX, L.nameY, fitSize(sig.name, L.colW - 4 * k, 19 * k, 10 * k, true),
      INK, L.anchor, true));

    var promptSize = 9.5 * k;
    var lines = wrap(sig.prompt, L.colW - 4 * k, promptSize);
    for (var j = 0; j < lines.length && j < 3; j++) {
      g.push(txt(lines[j], L.colX, L.promptY + j * (promptSize + 3.5 * k), promptSize,
        MUTED, L.anchor));
    }

    /* the band: whoever is running the event, and the logo they supplied */
    if (o.logo || o.event || o.credit) {
      var bx = L.landscape ? L.colX : L.panel.x;
      var bw = L.landscape ? L.colW : L.panel.w;
      g.push('<line x1="' + n(bx) + '" y1="' + n(L.ruleY) + '" x2="' + n(bx + bw) +
        '" y2="' + n(L.ruleY) + '" stroke="' + RULE + '" stroke-width="' + n(k) + '"/>');
      var tx = bx;
      if (o.logo) {
        var lh = 18 * k, lw = Math.min(bw * 0.4, 52 * k);
        g.push('<image x="' + n(bx) + '" y="' + n(L.bandY) + '" width="' + n(lw) +
          '" height="' + n(lh) + '" preserveAspectRatio="xMinYMid meet" href="' +
          esc(o.logo) + '" xlink:href="' + esc(o.logo) + '"/>');
        tx = bx + lw + 8 * k;
      }
      if (o.event) {
        g.push(txt(o.event, tx, L.bandY + 13 * k,
          fitSize(o.event, bx + bw - tx, 9 * k, 5.5), INK, "start"));
      }
      /* The credit drops to its own row when an event name already owns the
       * first one; otherwise it sits on that row. Either way it stays clear of
       * the trim. */
      if (o.credit) {
        g.push(txt("cavendish.space", bx + bw, L.bandY + (o.event ? 25 : 13) * k,
          6.5 * k, MUTED, "end"));
      }
    }

    if (o.cutlines) {
      g.push('<rect x="0.25" y="0.25" width="' + n(W - 0.5) + '" height="' + n(H - 0.5) +
        '" fill="none" stroke="' + CUT + '" stroke-width="0.5"/>');
    }

    return '<g transform="translate(' + n(x) + ',' + n(y) + ')">' + g.join("") + '</g>';
  }

  function txt(s, x, y, size, fill, anchor, bold, extra) {
    return '<text x="' + n(x) + '" y="' + n(y) + '" font-family="Atkinson Hyperlegible, ' +
      'Verdana, sans-serif" font-size="' + n(size) + '" fill="' + fill + '"' +
      (anchor && anchor !== "start" ? ' text-anchor="' + anchor + '"' : '') +
      (bold ? ' font-weight="700"' : '') + (extra ? " " + extra : "") + ">" + esc(s) + "</text>";
  }

  /* ---- the sheet --------------------------------------------------------
   * One grid, used by both modes. The grid never gets a gutter: badges butt
   * against each other so a guillotine (or a pair of scissors along one line)
   * cuts two badges at once, and the shared edge is the same cut.
   */
  function grid(paper, size, orient, pro) {
    var p = PAPER[paper], s = dims(size, orient);
    /* A desk printer cannot print into its own unprintable edge, so a home
     * sheet keeps a quarter inch clear. A print shop runs oversize stock and
     * trims, so there the sheet is only a carrier and the margin can go to
     * nothing — which is the difference between one A6 badge on an A4 sheet
     * and four. */
    var m = pro ? 0 : MIN_MARGIN;
    var cols = Math.max(1, Math.floor((p.w - 2 * m) / s.w));
    var rows = Math.max(1, Math.floor((p.h - 2 * m) / s.h));
    var gw = cols * s.w, gh = rows * s.h;
    return {
      cols: cols, rows: rows, per: cols * rows,
      x: (p.w - gw) / 2, y: (p.h - gh) / 2, w: gw, h: gh,
      margin: Math.min((p.w - gw) / 2, (p.h - gh) / 2)
    };
  }

  function line(x1, y1, x2, y2) {
    return '<line x1="' + n(x1) + '" y1="' + n(y1) + '" x2="' + n(x2) + '" y2="' + n(y2) +
      '" stroke="#000000" stroke-width="0.5"/>';
  }

  function marks(g) {
    /* Crop marks in the margin, clear of the bleed. Drawn at every grid line,
     * not only the corners, because the interior lines are where a guillotine
     * operator sets the stops. */
    var out = [], i, v, a = BLEED + 1, b = BLEED + 8;
    for (i = 0; i <= g.cols; i++) {
      v = g.x + i * (g.w / g.cols);
      out.push(line(v, g.y - a, v, g.y - b));
      out.push(line(v, g.y + g.h + a, v, g.y + g.h + b));
    }
    for (i = 0; i <= g.rows; i++) {
      v = g.y + i * (g.h / g.rows);
      out.push(line(g.x - a, v, g.x - b, v));
      out.push(line(g.x + g.w + a, v, g.x + g.w + b, v));
    }
    return out.join("");
  }

  /* `fill` is an array of signal ids, one per slot; a null leaves the slot
   * empty. Returns a complete standalone SVG document as a string. */
  function sheetSVG(fill, o, fontCSS) {
    var p = PAPER[o.paper], s = dims(o.size, o.orient);
    var g = grid(o.paper, o.size, o.orient, o.pro);
    var body = [];

    body.push('<rect x="0" y="0" width="' + n(p.w) + '" height="' + n(p.h) + '" fill="#ffffff"/>');

    if (o.pro && g.margin >= BLEED) {
      /* Bleed: the badge background is a flat paper color, so extending it
       * past the trim is the whole of the bleed. Interior edges need none —
       * neighbours already cover them. */
      body.push('<rect x="' + n(g.x - BLEED) + '" y="' + n(g.y - BLEED) + '" width="' +
        n(g.w + 2 * BLEED) + '" height="' + n(g.h + 2 * BLEED) + '" fill="' + PAPER_INK + '"/>');
    }

    for (var i = 0; i < g.per; i++) {
      var id = fill[i];
      if (!id) continue;
      var sig = signal(id);
      if (!sig) continue;
      var col = i % g.cols, row = Math.floor(i / g.cols);
      body.push(badge(sig, o, g.x + col * s.w, g.y + row * s.h));
    }

    if (o.pro && g.margin >= MIN_MARGIN) body.push(marks(g));

    return '<?xml version="1.0" encoding="UTF-8"?>\n' +
      '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ' +
      'width="' + p.css.split(" ")[0] + '" height="' + p.css.split(" ")[1] + '" ' +
      'viewBox="0 0 ' + n(p.w) + ' ' + n(p.h) + '" role="img" ' +
      'aria-label="A sheet of Cavendish interaction badges, ready to cut.">' +
      (fontCSS ? "<defs><style>" + fontCSS + "</style></defs>" : "") +
      body.join("") + "</svg>";
  }

  /* ---- what goes on which sheet ----------------------------------------- */

  function sheets(o) {
    var g = grid(o.paper, o.size, o.orient, o.pro), out = [], i;
    if (o.layout === "bulk") {
      /* One signal per sheet. Print 25 copies of the green sheet, cut, and you
       * have 100 green badges — which is how a hundred-person event actually
       * gets badged. */
      for (i = 0; i < o.signals.length; i++) {
        var fill = [];
        for (var j = 0; j < g.per; j++) fill.push(o.signals[i]);
        out.push({ title: signal(o.signals[i]).name, slug: o.signals[i], fill: fill });
      }
    } else {
      /* One set. Trailing slots stay empty rather than repeating a signal —
       * cut this sheet up and you are holding exactly one person's stack. */
      var k = 0;
      while (k < o.signals.length) {
        var f = [];
        for (var m = 0; m < g.per; m++) f.push(o.signals[k + m] || null);
        out.push({ title: "one set", slug: "set" + (out.length + 1), fill: f });
        k += g.per;
      }
    }
    return out;
  }

  /* ---- fonts, for export ------------------------------------------------
   * A downloaded SVG opened on somebody else's machine has no access to this
   * site's fonts, and a print shop will not install one. So the export path
   * inlines the two weights as base64 and the file becomes self-contained.
   * The preview does not do this: the page already has the fonts, and a
   * <style> element inserted into this document would be refused by the CSP.
   */
  var fontCache = null;
  function loadFonts() {
    if (fontCache) return fontCache;
    var files = [
      ["/fonts/AtkinsonHyperlegible-Regular.woff2", 400],
      ["/fonts/AtkinsonHyperlegible-Bold.woff2", 700]
    ];
    fontCache = Promise.all(files.map(function (f) {
      return fetch(f[0]).then(function (r) { return r.arrayBuffer(); }).then(function (buf) {
        var bytes = new Uint8Array(buf), bin = "";
        for (var i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
        return "@font-face{font-family:'Atkinson Hyperlegible';font-style:normal;font-weight:" +
          f[1] + ";src:url(data:font/woff2;base64," + btoa(bin) + ") format('woff2');}";
      });
    })).then(function (css) { return css.join(""); }).catch(function () { return ""; });
    return fontCache;
  }

  /* ---- state ------------------------------------------------------------ */

  var state = {
    signals: DEFAULT_ON.slice(),
    size: "4x3",
    orient: "portrait",
    paper: "letter",
    layout: "bulk",
    mode: "home",
    holes: true,
    cutlines: true,
    credit: true,
    event: "",
    logo: null,
    people: 50
  };

  function opts() {
    return {
      signals: state.signals, size: state.size, orient: state.orient,
      paper: state.paper, layout: state.layout, pro: state.mode === "pro",
      holes: state.holes,
      cutlines: state.mode === "home" && state.cutlines,
      credit: state.credit, event: state.event.trim(), logo: state.logo
    };
  }

  function save() {
    try {
      /* The logo stays out of storage on purpose: it is somebody's file, it
       * can be megabytes, and a badge maker has no business keeping it. */
      localStorage.setItem(STORE, JSON.stringify({
        signals: state.signals, size: state.size, orient: state.orient,
        paper: state.paper, layout: state.layout, mode: state.mode,
        holes: state.holes, cutlines: state.cutlines, credit: state.credit,
        event: state.event, people: state.people
      }));
    } catch (e) { /* private mode, quota, or storage off — not worth a message */ }
  }

  function restore() {
    try {
      var raw = localStorage.getItem(STORE);
      if (!raw) return;
      var v = JSON.parse(raw);
      if (!v || typeof v !== "object") return;
      if (Array.isArray(v.signals) && v.signals.length) {
        state.signals = v.signals.filter(function (id) { return !!signal(id); });
      }
      for (var i = 0; i < SIZES.length; i++) if (SIZES[i].id === v.size) state.size = v.size;
      if (v.orient === "portrait" || v.orient === "landscape") state.orient = v.orient;
      if (PAPER[v.paper]) state.paper = v.paper;
      if (v.layout === "bulk" || v.layout === "set") state.layout = v.layout;
      if (v.mode === "home" || v.mode === "pro") state.mode = v.mode;
      state.holes = v.holes !== false;
      state.cutlines = v.cutlines !== false;
      state.credit = v.credit !== false;
      if (typeof v.event === "string") state.event = v.event.slice(0, 60);
      if (typeof v.people === "number" && v.people > 0) {
        state.people = Math.min(Math.round(v.people), 100000);
      }
    } catch (e) { /* ignore a corrupt value rather than break the page */ }
  }

  /* ---- render ----------------------------------------------------------- */

  var current = [];

  function render() {
    var o = opts(), g = grid(o.paper, o.size, o.orient, o.pro);
    var host = byId("badges-sheets");
    if (!host) return;

    setHoleSpec(o);

    if (!o.signals.length) {
      host.innerHTML = '<p class="muted">Choose at least one signal above and the sheets ' +
        "will appear here.</p>";
      current = [];
      setSummary(g, 0);
      return;
    }

    current = sheets(o);
    var html = "";
    for (var i = 0; i < current.length; i++) {
      html += '<figure class="badge-sheet">' +
        '<div class="badge-sheet-paper">' + sheetSVG(current[i].fill, o, null) + "</div>" +
        "<figcaption>" +
        '<span class="badge-sheet-title">' + esc(current[i].title) + "</span> " +
        '<span class="muted">' + g.per + " per sheet · " + PAPER[o.paper].label +
        " · " + esc(sizeLabel(o.size, o.orient)) + "</span> " +
        '<button type="button" class="btn ghost small" data-sheet="' + i +
        '">Download this sheet (SVG)</button>' +
        "</figcaption></figure>";
    }
    host.innerHTML = html;
    setSummary(g, current.length);
  }

  function setSummary(g, sheetCount) {
    var el = byId("badges-summary");
    if (!el) return;
    var o = opts(), d = dims(o.size, o.orient);
    if (!o.signals.length) { el.textContent = "No signals chosen yet."; return; }
    var lines = [];
    lines.push(g.cols + " × " + g.rows + " = " + g.per + " badge" +
      (g.per === 1 ? "" : "s") + " per " + PAPER[o.paper].label + " sheet. Each badge is " +
      inches(d.w) + " × " + inches(d.h) + " in (" + mm(d.w) + " × " + mm(d.h) +
      " mm) — the " + sizeDef(o.size).label + " size, " + o.orient + ".");
    if (o.layout === "bulk") {
      var people = Math.max(1, state.people);
      var copies = Math.ceil(people / g.per);
      lines.push(people + " " + (people === 1 ? "person" : "people") + " × " +
        o.signals.length + " " + (o.signals.length === 1 ? "signal" : "signals") + " = " +
        (people * o.signals.length) + " badges. Print " + copies + " " +
        (copies === 1 ? "copy" : "copies") + " of each of the " + sheetCount + " " +
        (sheetCount === 1 ? "sheet" : "sheets") + " below, cut, then collate one of each " +
        "into a stack per person.");
    } else {
      lines.push("One set per sheet: cut it up and you are holding one person's stack of " +
        o.signals.length + ". Set Copies in the print dialog to the number of people.");
    }
    if (state.mode === "home") {
      if (g.margin < MIN_MARGIN + 6) {
        lines.push("Margins are tight at this combination (" + inches(g.margin) +
          " in). If your printer clips the outer badges, switch paper or orientation.");
      }
      /* A6 on A4 is four-up with no margin at all and one-up with a safe one,
       * so a reader who never tries the other orientation quietly wastes most
       * of their card. Only the orientation is suggested: paper size is
       * whatever is in the drawer, not a choice. */
      var alt = grid(o.paper, o.size, o.orient === "portrait" ? "landscape" : "portrait", false);
      if (alt.per > g.per) {
        lines.push("Turned the other way, the same sheet would hold " + alt.per +
          " instead of " + g.per + ".");
      }
    } else {
      if (g.margin < BLEED) {
        lines.push("This badge tiles the sheet edge to edge, so there is no room for bleed " +
          "or crop marks on it. Send the single-badge files instead and let the shop " +
          "impose them on oversize stock — that is what they would rather have anyway.");
      } else if (g.margin < MIN_MARGIN) {
        lines.push("There is room for bleed but not for crop marks at this combination. " +
          "Trim to the outer edge of the bleed instead, or send the single-badge files.");
      }
    }
    el.textContent = lines.join(" ");
  }

  /* The hole positions a print shop needs are a fact about the chosen size, so
   * they are computed rather than written down once and left to go stale. */
  function setHoleSpec(o) {
    var el = byId("badges-holes-spec");
    if (!el) return;
    var d = dims(o.size, o.orient);
    var L = layout(d.w, d.h, o.orient === "landscape");
    var edge = L.holes[0];
    var apart = L.holes[1] - L.holes[0];
    el.textContent = "At " + sizeLabel(o.size, o.orient) + ": two holes " +
      inches(HOLE_R * 2) + " in (" + mm(HOLE_R * 2) + " mm) across, centers " +
      inches(edge) + " in (" + mm(edge) + " mm) in from each side edge — " +
      inches(apart) + " in (" + mm(apart) + " mm) apart — and " + inches(HOLE_Y) +
      " in (" + mm(HOLE_Y) + " mm) down from the top edge.";
  }

  /* ---- download --------------------------------------------------------- */

  function download(name, text, type) {
    var blob = new Blob([text], { type: type });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = name;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 4000);
  }

  function say(msg) {
    var el = byId("badges-status");
    if (el) el.textContent = msg;
  }

  function downloadSheet(i) {
    var o = opts();
    if (!current[i]) return;
    say("Embedding the fonts…");
    loadFonts().then(function (css) {
      download("cavendish-badges-" + current[i].slug + "-" + o.size + "-" + o.orient +
        "-" + o.paper + ".svg", sheetSVG(current[i].fill, o, css), "image/svg+xml");
      say("Downloaded. The fonts are inside the file, so it opens the same anywhere.");
    });
  }

  /* One badge at trim + bleed with crop marks: the file a print shop asks for
   * when it would rather impose the sheet itself. */
  function downloadSingles() {
    var o = opts();
    if (!o.signals.length) return;
    say("Embedding the fonts…");
    loadFonts().then(function (css) {
      var s = dims(o.size, o.orient);
      var W = s.w + 2 * BLEED, H = s.h + 2 * BLEED;
      o.signals.forEach(function (id, k) {
        var sig = signal(id);
        var single = Object.assign({}, o, { cutlines: false });
        var m = [];
        [0, s.w].forEach(function (v) {
          m.push(line(BLEED + v, BLEED - 1, BLEED + v, 0));
          m.push(line(BLEED + v, BLEED + s.h + 1, BLEED + v, H));
        });
        [0, s.h].forEach(function (v) {
          m.push(line(BLEED - 1, BLEED + v, 0, BLEED + v));
          m.push(line(BLEED + s.w + 1, BLEED + v, W, BLEED + v));
        });
        var svg = '<?xml version="1.0" encoding="UTF-8"?>\n' +
          '<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ' +
          'width="' + n(W / 72) + 'in" height="' + n(H / 72) + 'in" viewBox="0 0 ' + n(W) +
          " " + n(H) + '" role="img" aria-label="Cavendish interaction badge: ' + esc(sig.name) +
          ', at trim size plus bleed.">' +
          "<defs><style>" + css + "</style></defs>" +
          '<rect x="0" y="0" width="' + n(W) + '" height="' + n(H) + '" fill="' + PAPER_INK +
          '"/>' + badge(sig, single, BLEED, BLEED) + m.join("") + "</svg>";
        /* Staggered: browsers drop simultaneous downloads. */
        setTimeout(function () {
          download("cavendish-badge-" + id + "-" + o.size + "-" + o.orient + "-bleed.svg",
            svg, "image/svg+xml");
        }, k * 350);
      });
      say(o.signals.length + " " + (o.signals.length === 1 ? "file" : "files") +
        " downloading, one per signal, each at trim size plus an eighth-inch bleed " +
        "with crop marks.");
    });
  }

  /* ---- printing ---------------------------------------------------------
   * The sheets are already exact physical sizes, so all printing needs is a
   * page box that matches and no browser margin on top of it. @page cannot be
   * set from an inline <style> under this site's CSP, so it goes in through
   * the CSSOM, which CSP does not govern.
   */
  var pageRuleIndex = -1;
  function setPageSize(css) {
    try {
      var sheet = null, i;
      for (i = 0; i < document.styleSheets.length; i++) {
        var ss = document.styleSheets[i];
        if (ss.href && ss.href.indexOf("styles.css") !== -1) { sheet = ss; break; }
      }
      if (!sheet) return;
      if (pageRuleIndex >= 0) {
        try { sheet.deleteRule(pageRuleIndex); } catch (e) { /* already gone */ }
        pageRuleIndex = -1;
      }
      pageRuleIndex = sheet.insertRule("@page{size:" + css + ";margin:0}", sheet.cssRules.length);
    } catch (e) {
      /* Cross-origin or locked stylesheet. The printed sheet is still the right
       * size on paper as long as the dialog is set to 100% — which the
       * instructions on the page say to do anyway. */
    }
  }

  function printSheets() {
    setPageSize(PAPER[state.paper].css);
    document.body.classList.add("printing-badges");
    window.print();
  }

  /* ---- the logo ---------------------------------------------------------
   * Read locally, embedded as a data URL, never sent anywhere. An SVG logo is
   * embedded through <image>, which renders it in the secure static mode — no
   * scripts, no external fetches — so an arbitrary file can be accepted
   * without sanitising it.
   */
  var OK_TYPES = ["image/png", "image/jpeg", "image/svg+xml", "image/webp", "image/gif"];

  function takeLogo(file) {
    if (!file) return;
    if (OK_TYPES.indexOf(file.type) === -1) {
      say("That file is a " + (file.type || "unknown type") +
        ". Use a PNG, JPEG, SVG, WebP, or GIF.");
      return;
    }
    if (file.size > 3 * 1024 * 1024) {
      say("That logo is " + Math.round(file.size / 1024 / 1024 * 10) / 10 +
        " MB. Anything over about 3 MB makes the downloaded file unwieldy — " +
        "try a smaller one.");
      return;
    }
    var reader = new FileReader();
    reader.onload = function () {
      state.logo = String(reader.result);
      var l = byId("badges-logo-name");
      if (l) l.textContent = file.name;
      var clear = byId("badges-logo-clear");
      if (clear) clear.hidden = false;
      say("Logo added. It stays in this browser — it is written into the file you " +
        "download and is never uploaded.");
      render();
    };
    reader.onerror = function () { say("That file could not be read."); };
    reader.readAsDataURL(file);
  }

  /* ---- wiring ----------------------------------------------------------- */

  function init() {
    restore();

    var list = byId("badges-signals");
    if (list) {
      var html = "";
      SIGNALS.forEach(function (s) {
        html += '<label class="badge-pick"><input type="checkbox" name="sig" value="' + s.id +
          '"' + (state.signals.indexOf(s.id) !== -1 ? " checked" : "") + ">" +
          '<span class="badge-pick-swatch sig-' + s.id + '"></span>' +
          '<span class="badge-pick-text"><strong>' + esc(s.name) + "</strong> " +
          '<span class="muted">' + esc(s.word) + " · " + esc(s.prompt) +
          "</span></span></label>";
      });
      list.innerHTML = html;
      list.addEventListener("change", function () {
        var picked = [];
        SIGNALS.forEach(function (s) {
          var box = list.querySelector('input[value="' + s.id + '"]');
          if (box && box.checked) picked.push(s.id);
        });
        state.signals = picked;
        save(); render();
      });
    }

    var sizes = byId("badges-sizes");
    if (sizes) {
      var sh = "";
      SIZES.forEach(function (s) {
        sh += '<label><input type="radio" name="badge-size" value="' + s.id + '"' +
          (state.size === s.id ? " checked" : "") + "><span><strong>" + esc(s.label) +
          "</strong> — " + esc(s.metric) + ". " + esc(s.note) + "</span></label>";
      });
      sizes.innerHTML = sh;
    }

    function bindRadio(name, key) {
      var boxes = document.querySelectorAll('input[name="' + name + '"]');
      Array.prototype.forEach.call(boxes, function (b) {
        b.checked = (b.value === state[key]);
        b.addEventListener("change", function () {
          if (b.checked) { state[key] = b.value; save(); syncModeUI(); render(); }
        });
      });
    }
    bindRadio("badge-size", "size");
    bindRadio("badge-orient", "orient");
    bindRadio("badge-paper", "paper");
    bindRadio("badge-layout", "layout");
    bindRadio("badge-mode", "mode");

    function bindCheck(id, key) {
      var el = byId(id);
      if (!el) return;
      el.checked = !!state[key];
      el.addEventListener("change", function () { state[key] = el.checked; save(); render(); });
    }
    bindCheck("badges-holes", "holes");
    bindCheck("badges-cutlines", "cutlines");
    bindCheck("badges-credit", "credit");

    var ev = byId("badges-event");
    if (ev) {
      ev.value = state.event;
      ev.addEventListener("input", function () {
        state.event = ev.value.slice(0, 60); save(); render();
      });
    }

    var people = byId("badges-people");
    if (people) {
      people.value = state.people;
      people.addEventListener("input", function () {
        var v = parseInt(people.value, 10);
        state.people = (isNaN(v) || v < 1) ? 1 : Math.min(v, 100000);
        save(); render();
      });
    }

    var logo = byId("badges-logo");
    if (logo) {
      logo.addEventListener("change", function () { takeLogo(logo.files && logo.files[0]); });
    }
    var clear = byId("badges-logo-clear");
    if (clear) {
      clear.addEventListener("click", function () {
        state.logo = null;
        if (logo) logo.value = "";
        var l = byId("badges-logo-name");
        if (l) l.textContent = "";
        clear.hidden = true;
        say("Logo removed.");
        render();
      });
    }

    var host = byId("badges-sheets");
    if (host) {
      host.addEventListener("click", function (e) {
        var b = e.target.closest ? e.target.closest("[data-sheet]") : null;
        if (b) downloadSheet(parseInt(b.getAttribute("data-sheet"), 10));
      });
    }

    var p = byId("badges-print");
    if (p) p.addEventListener("click", printSheets);
    var d = byId("badges-singles");
    if (d) d.addEventListener("click", downloadSingles);

    window.addEventListener("afterprint", function () {
      document.body.classList.remove("printing-badges");
    });

    syncModeUI();
    render();
    var note = byId("badges-jsnote");
    if (note) note.hidden = true;
  }

  function syncModeUI() {
    var cut = byId("badges-cutlines-row");
    if (cut) cut.hidden = (state.mode === "pro");
    var people = byId("badges-people-row");
    if (people) people.hidden = (state.layout !== "bulk");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
