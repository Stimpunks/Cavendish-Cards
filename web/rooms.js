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
    "corner": "a corner or nook out of the main flow",
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
   * walking up what this place asks of them. */
  var ZONES = [
    {
      id: "cave",
      name: "The cave",
      prompt: "Somewhere quiet, just for you.",
      needs: ["quiet", "dim", "corner", "come-and-go"],
      sign: "Quiet. One person at a time. You don't have to say why you came in, or why you're leaving."
    },
    {
      id: "campfire",
      name: "The campfire",
      prompt: "A small group, sharing.",
      needs: ["small-group", "soft", "sit-my-way", "another-way"],
      sign: "A few people, talking. Sit however you like. Listening is taking part, and nobody here has to perform."
    },
    {
      id: "watering-hole",
      name: "The watering hole",
      prompt: "A soft place to pause and be near people.",
      needs: ["room-to-move", "way-out", "come-and-go", "less-to-look-at"],
      sign: "Be near people without joining in. Hover at the edge, drift off, come back. No task, no script."
    },
    {
      id: "library",
      name: "The library",
      prompt: "Where we keep what we've figured out.",
      needs: ["written", "no-rush", "another-way", "own-spot"],
      sign: "What we've worked out, kept where you can reach it. Find your own way in, at your own pace."
    },
    {
      id: "habitat",
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
  if (!form || !resultBox) return;

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
  }

  function signCard(z) {
    var fig = el("figure", "rooms-sign");
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

  load();
  render(selected());
})();
