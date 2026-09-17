/* Zone a room — Cavendish Cards.
 *
 * Takes a room's conditions and says which Cavendish zones it can hold, then
 * renders printable signs for them.
 *
 * Two rules this file exists to keep, and they are the reason for several
 * choices that would otherwise look long-winded:
 *
 *   1. No score. Never a number out of five, never a percentage, never a
 *      grade, never a pass. An unmet zone renders as a list of changes to the
 *      room, in the room's own vocabulary, and nothing else.
 *   2. The subject is always the room. No output sentence takes a person as
 *      its subject. A room that holds nothing yet is a room with a to-do list,
 *      not a room that failed.
 *
 * State lives in localStorage and nowhere else. No network, no account.
 */
(function () {
  "use strict";

  var STORE = "cavendish.rooms.v1";

  /* Condition labels, phrased as the CHANGE rather than the lack. These are
   * what a reader sees when a zone is not held yet, so each one has to read as
   * something you could go and do this afternoon. */
  var COND = {
    "control": "let people in the room change things in it",
    "own-spot": "a spot that can stay someone's for the session",
    "quiet": "somewhere it can be made quiet",
    "steady-sound": "steady background sound or headphones allowed",
    "dim": "light that can come down or a corner out of the brightest light",
    "less-to-look-at": "somewhere with less to look at",
    "soft": "something soft to sit or lean on",
    "temperature": "a temperature people can change or dress for",
    "room-to-move": "room to move without being in anyone's way",
    "sit-my-way": "permission to sit however you like",
    "corner": "a corner, nook, or den out of the main flow",
    "way-out": "a way out that doesn't cross in front of everyone",
    "written": "what happens here written down or posted",
    "another-way": "a way to take part other than speaking aloud",
    "come-and-go": "leaving and coming back without explaining",
    "no-rush": "things not all at one pace",
    "small-group": "somewhere a small group can meet without the room listening in"
  };

  /* The five zones. `needs` mirrors the "Needs:" line under each zone in
   * rooms.html — if you change one, change both. `sign` is what gets printed
   * and put on the wall: the deck's own prompt, then one line telling a person
   * walking up what this place asks of them.
   *
   * `prompt` is the matching card's own ## Prompt in cards/places/ — a third
   * copy, so change it there, here, and in rooms.html together.
   *
   * `art` is that card's illustration without the card around it, written by
   * build-site.py from card-art.py's motif (ART_ONLY). It is named per zone
   * rather than built from the id, so renaming an id cannot quietly point a
   * sign at a file that is not there. */
  var ZONES = [
    {
      id: "cave",
      art: "faces/places--the-cave--art.svg",
      name: "The cave",
      prompt: "Somewhere quiet, just for you.",
      needs: ["quiet", "dim", "corner", "come-and-go"],
      sign: "Quiet. One person at a time. You don't have to say why you came in, or why you're leaving."
    },
    {
      id: "campfire",
      art: "faces/places--the-campfire--art.svg",
      name: "The campfire",
      prompt: "A small group, sharing.",
      needs: ["small-group", "soft", "sit-my-way", "another-way"],
      sign: "A few people, talking. Sit however you like. Listening is taking part, and nobody here has to perform."
    },
    {
      id: "watering-hole",
      art: "faces/places--the-watering-hole--art.svg",
      name: "The watering hole",
      prompt: "Where we learn from each other.",
      needs: ["room-to-move", "way-out", "come-and-go", "less-to-look-at"],
      sign: "Be near people without joining in. Hover at the edge, drift off, come back. No task, no script."
    },
    {
      id: "library",
      art: "faces/places--the-library--art.svg",
      name: "The library",
      prompt: "Where we keep what we've figured out.",
      needs: ["written", "no-rush", "another-way", "own-spot"],
      sign: "What we've worked out, kept where you can reach it. Find your own way in, at your own pace."
    },
    {
      id: "habitat",
      art: "faces/places--the-habitat--art.svg",
      name: "The habitat",
      prompt: "The world around it all — steady, sensory-safe.",
      needs: ["control", "temperature", "quiet", "dim", "steady-sound"],
      sign: "This whole room is meant to fit you, not the other way round. If something here doesn't fit, it can be changed — say so."
    }
  ];

  var form = document.getElementById("rooms-form");
  var resultBox = document.getElementById("rooms-result");
  var signsBox = document.getElementById("rooms-signs");
  var savedNote = document.getElementById("rooms-saved");
  var jsNote = document.getElementById("rooms-jsnote");
  var askedSection = document.getElementById("rooms-asked-section");
  var askedBox = document.getElementById("rooms-asked");
  if (!form || !resultBox) return;

  /* A group brief arrives in the URL fragment: rooms.html#asked=quiet,corner
   *
   * It does NOT tick boxes, and that distinction is the reason this is a
   * separate layer rather than a shortcut into the form. A tick means "the
   * room has this." A brief means "somebody asked for this." Pre-ticking a
   * brief would make the page announce zones the room cannot actually hold,
   * which is the one thing it must never do.
   *
   * Read from the fragment and never stored. Everything after "#" stays in the
   * browser -- no browser puts it in the request -- and this is a list of
   * access needs somebody named, so it does not go in localStorage either.
   * Close the tab and it is gone, the same as a spread.
   *
   * Rendered in COND order, never the link's order, so a tool that emitted a
   * ranked list cannot smuggle a ranking through. Nothing here is counted. */
  var CONDORDER = Object.keys(COND);
  var asked = [];
  var askedUnknown = [];

  function readAsked() {
    asked = [];
    askedUnknown = [];
    var m = /(?:^|[#&])asked=([^&]*)/.exec(String(location.hash || ""));
    if (!m) return;
    var raw;
    try { raw = decodeURIComponent(m[1].replace(/\+/g, " ")); } catch (e) { raw = m[1]; }
    raw.split(/[,\s]+/).forEach(function (t) {
      var k = t.trim().toLowerCase();
      if (!k) return;
      if (COND[k]) {
        if (asked.indexOf(k) < 0) asked.push(k);
      } else if (askedUnknown.indexOf(k) < 0 && askedUnknown.length < 12) {
        askedUnknown.push(k);
      }
    });
    asked.sort(function (a, b) { return CONDORDER.indexOf(a) - CONDORDER.indexOf(b); });
  }

  /* Mark the boxes the brief named, in text as well as color -- a coordinator
   * scanning the form should not have to hold the list in their head, and a
   * tint alone says nothing to a screen reader. */
  function flagAskedBoxes() {
    boxes().forEach(function (b) {
      var lab = b.closest ? b.closest("label") : b.parentNode;
      if (!lab) return;
      var on = asked.indexOf(b.value) >= 0;
      var tag = lab.querySelector(".rooms-asked-tag");
      if (on) {
        lab.classList.add("is-asked");
        // Right after the checkbox, not at the end: appended, it lands past a
        // two-line label and reads as a stray word.
        if (!tag) lab.insertBefore(el("span", "rooms-asked-tag", "asked for"), b.nextSibling);
      } else {
        lab.classList.remove("is-asked");
        if (tag) tag.parentNode.removeChild(tag);
      }
    });
  }

  function renderAsked(state) {
    if (!askedSection || !askedBox) return;
    if (!asked.length && !askedUnknown.length) {
      askedSection.hidden = true;
      return;
    }
    askedSection.hidden = false;
    askedBox.textContent = "";

    var here = asked.filter(function (k) { return state[k]; });
    var gap = asked.filter(function (k) { return !state[k]; });

    var lead = el("p", "rooms-lead");
    lead.textContent = gap.length
      ? "Tick below what the room already has. What stays unticked is what there is still to do."
      : "Everything the brief named is ticked below. Nothing from it is outstanding.";
    askedBox.appendChild(lead);

    if (gap.length) {
      askedBox.appendChild(el("h3", "rooms-open-head", "Asked for, not there yet"));
      var gl = el("ul", "rooms-asked-gap");
      gap.forEach(function (k) { gl.appendChild(el("li", null, COND[k])); });
      askedBox.appendChild(gl);
    }
    if (here.length) {
      askedBox.appendChild(el("h3", "rooms-open-head", "Asked for, already here"));
      var hl = el("ul", "rooms-asked-have");
      here.forEach(function (k) { hl.appendChild(el("li", null, COND[k])); });
      askedBox.appendChild(hl);
    }
    if (askedUnknown.length) {
      var u = el("p", "muted");
      u.textContent = "The link also named " +
        joinList(askedUnknown.map(function (k) { return "\u201c" + k + "\u201d"; })) +
        ", which this page has no condition for. Carry " +
        (askedUnknown.length === 1 ? "that one" : "those") +
        " yourself \u2014 a need this page cannot hold is still a need.";
      askedBox.appendChild(u);
    }
    var note = el("p", "muted");
    note.textContent = "This list came from the link and is not kept in this browser. " +
      "It says what was asked for. It does not say how many asked, and it is in no order of importance.";
    askedBox.appendChild(note);
  }

  function boxes() {
    return Array.prototype.slice.call(form.querySelectorAll('input[name="c"]'));
  }

  function selected() {
    var out = {};
    boxes().forEach(function (b) { if (b.checked) out[b.value] = true; });
    return out;
  }

  function load() {
    var raw;
    try { raw = localStorage.getItem(STORE); } catch (e) { return; }
    if (!raw) return;
    var saved;
    try { saved = JSON.parse(raw); } catch (e) { return; }
    if (!saved || typeof saved !== "object") return;
    boxes().forEach(function (b) { b.checked = saved[b.value] === true; });
  }

  function save(state) {
    try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) { /* private window; fine */ }
  }

  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }

  function evaluate(state) {
    return ZONES.map(function (z) {
      var missing = z.needs.filter(function (k) { return !state[k]; });
      return { zone: z, missing: missing, held: missing.length === 0 };
    });
  }

  function joinList(items) {
    if (items.length === 1) return items[0];
    if (items.length === 2) return items[0] + " and " + items[1];
    return items.slice(0, -1).join(", ") + ", and " + items[items.length - 1];
  }

  function render(state) {
    var rows = evaluate(state);
    var held = rows.filter(function (r) { return r.held; });
    var open = rows.filter(function (r) { return !r.held; });

    resultBox.textContent = "";

    var lead = el("p", "rooms-lead");
    if (held.length === 0) {
      lead.textContent = "Nothing is ticked yet, so this page is not assuming anything about the room. " +
        "Tick what is true above, or read the five zones below and work it out on paper.";
      var anyTicked = Object.keys(state).length > 0;
      if (anyTicked) {
        lead.textContent = "No zone is fully held yet. Every zone below lists what would change that — " +
          "and each line is a change to the room, not a verdict on it.";
      }
    } else {
      lead.textContent = "This room can hold " +
        joinList(held.map(function (r) { return r.zone.name.toLowerCase(); })) + " today.";
    }
    resultBox.appendChild(lead);

    if (held.length) {
      var heldList = el("ul", "rooms-held");
      held.forEach(function (r) {
        var li = el("li");
        li.appendChild(el("strong", null, r.zone.name));
        li.appendChild(document.createTextNode(" — " + r.zone.prompt));
        heldList.appendChild(li);
      });
      resultBox.appendChild(heldList);
      var sgn = el("p", "muted");
      sgn.textContent = "Print a sign for each of these so the room says so itself.";
      resultBox.appendChild(sgn);
    }

    if (open.length) {
      var h = el("h3", "rooms-open-head", "What the other zones would need");
      resultBox.appendChild(h);
      var openList = el("ul", "rooms-open");
      open.forEach(function (r) {
        var li = el("li");
        li.appendChild(el("strong", null, r.zone.name));
        li.appendChild(document.createTextNode(": "));
        li.appendChild(document.createTextNode(
          joinList(r.missing.map(function (k) { return COND[k] || k; })) + "."));
        openList.appendChild(li);
      });
      resultBox.appendChild(openList);
      var note = el("p", "muted");
      note.textContent = "Some of these are an afternoon's work. Some are somebody else's decision. " +
        "Both are worth writing down, because a room nobody can change is itself a finding.";
      resultBox.appendChild(note);
    }

    renderSigns(held.map(function (r) { return r.zone; }));
    renderAsked(state);
  }

  function signCard(z) {
    var fig = el("figure", "rooms-sign");
    if (z.art) {
      // Decorative: the zone's name is the heading immediately below, so alt
      // text would make a screen reader say it twice.
      var img = document.createElement("img");
      img.className = "rooms-sign-art";
      img.src = z.art;
      img.alt = "";
      img.width = 630;
      img.height = 530;
      fig.appendChild(img);
    }
    fig.appendChild(el("p", "rooms-sign-kicker", "This is"));
    fig.appendChild(el("h3", "rooms-sign-name", z.name.toLowerCase()));
    fig.appendChild(el("p", "rooms-sign-prompt", z.prompt));
    fig.appendChild(el("p", "rooms-sign-body", z.sign));
    var cap = el("figcaption", "rooms-sign-foot");
    cap.textContent = "Cavendish Space · cavendish.space";
    fig.appendChild(cap);
    return fig;
  }

  function renderSigns(zones) {
    if (!signsBox) return;
    signsBox.textContent = "";
    if (!zones.length) {
      var p = el("p", "muted");
      p.textContent = "Signs appear here for each zone the room can hold. " +
        "Use “Print all five” if you would rather have the whole set to hand.";
      signsBox.appendChild(p);
      return;
    }
    zones.forEach(function (z) { signsBox.appendChild(signCard(z)); });
  }

  function update() {
    var state = selected();
    save(state);
    render(state);
    if (savedNote) {
      savedNote.textContent = "Saved in this browser only.";
    }
  }

  form.addEventListener("change", function (e) {
    if (e.target && e.target.name === "c") update();
  });

  var clearBtn = document.getElementById("rooms-clear");
  if (clearBtn) {
    clearBtn.addEventListener("click", function () {
      boxes().forEach(function (b) { b.checked = false; });
      try { localStorage.removeItem(STORE); } catch (e) { /* fine */ }
      render({});
      if (savedNote) savedNote.textContent = "Cleared.";
    });
  }

  var askedClear = document.getElementById("rooms-asked-clear");
  if (askedClear) {
    askedClear.addEventListener("click", function () {
      // Drop the fragment without a navigation, so the ticks and the scroll stay put.
      if (history.replaceState) {
        history.replaceState(null, "", location.pathname + location.search);
      } else {
        location.hash = "";
      }
      readAsked();
      flagAskedBoxes();
      render(selected());
    });
  }

  window.addEventListener("hashchange", function () {
    readAsked();
    flagAskedBoxes();
    render(selected());
  });

  var printBtn = document.getElementById("rooms-print");
  if (printBtn) {
    printBtn.addEventListener("click", function () {
      document.body.classList.add("printing-signs");
      window.print();
    });
  }

  var printAllBtn = document.getElementById("rooms-print-all");
  if (printAllBtn) {
    printAllBtn.addEventListener("click", function () {
      renderSigns(ZONES);
      document.body.classList.add("printing-signs");
      window.print();
    });
  }

  window.addEventListener("afterprint", function () {
    document.body.classList.remove("printing-signs");
    render(selected());
  });

  if (jsNote) {
    jsNote.textContent = "Ticking a box updates this straight away. Your choices stay in this browser.";
  }

  readAsked();
  load();
  flagAskedBoxes();
  render(selected());
})();
