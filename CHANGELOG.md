# Changelog

Notable changes to Cavendish Cards — both the **deck** (cards added or reworded) and the **site** (features and fixes at [cavendish.space](https://cavendish.space/)). Newest first; dates are when a change shipped. The site deploys continuously, so there are no version numbers — for the full detail, see the [commit history](https://github.com/Stimpunks/Cavendish-Cards/commits/main).

Each dated entry is split into **Deck** (changes to the cards themselves) and **Site** (changes to the web version). An entry only includes the sections that changed.

## 2026-09-16

### Deck

- **Every card has a picture now.** For months the deck's 88 non-Interaction cards carried an empty dashed box where the illustration goes — a placeholder that said "image pending" and printed the picture description in words underneath. That defeated the premise. The whole idea is that a person shows how they feel by *pointing at a picture*, with no reading required, and there was no picture to point at; the one thing the deck asks of a card, it could not do.

- **So the art rule gets one narrow carve-out.** Deck art is still human- and community-made, and no AI-generated image is committed here — that has not changed and is not up for negotiation. What has changed is what a *placeholder* is allowed to be. The same carve-out already in force for the site's favicon, app icons, and card frames now covers card faces: **plain vector illustration, drawn in code**, one motif per card, written by hand as shapes with coordinates in a source file anyone can read, diff, and edit. No image generator was used, and none will be. Every card face says `PLACEHOLDER ART · HUMAN ART WANTED` under the picture, so a card never pretends to be finished.

- **[The call for art](https://github.com/Stimpunks/Cavendish-Cards/blob/main/CALL-FOR-ART.md) is still open and still the point.** These pictures exist so the deck can be printed, cut, and played now — not so it can stop waiting for artists. The moment a human piece arrives for a card, it goes into `assets/cards/` and the web and print builds prefer it automatically; the placeholder is deleted. A deck nobody can use is not a purer deck.

- **Image cues are no longer printed on the card.** They were, while the window was empty, because words were the only thing standing in for the picture. They are now what they were always meant to be: the brief the illustration was drawn from, kept in the card files and the starter deck for illustrators. The card itself asks nothing of a reader.

### Site

- **A new page for grouping a room's access needs**, at [/group-needs.html](https://cavendish.space/group-needs.html). At an event, people lay spreads; a coordinator cannot hold twenty of them in their head. The page is a method for turning the pile into one short brief for the room — and it doubles as a skill description you can hand to whatever AI you already use, so it does the sorting. Hand it the page, then the spreads.

- **The method is narrow on purpose, because of what goes wrong without it.** Left to itself, a general-purpose AI will invent its own categories for access needs, rank them by how many people asked, and hand back something that reads like a report on a group of people. So the page does not ask for analysis. It asks for translation into a vocabulary that already exists here: the seventeen room conditions behind [Zone a room](https://cavendish.space/rooms.html), plus three lists that are not the room at all — kit, permission, and pacing. A need that fits no box is listed in the person's own card rather than forced into one.

- **Three rules carry the stance, and they are the whole point.** No score, ever. The subject of every output sentence is the room, never a person or a group. And no counting — not how many spreads named a thing, not sorted by it, not marked common or rare. Access is not a vote: one person needing a way out is exactly as actionable as eight, because you build the way out once either way. Counts also re-identify, since in a small group "named once" points at somebody.

- **Consent gets a step of its own, before the method.** Turning a card face-up is consent given to the room, in the moment, to the people there — not to an AI company. So the page opens with what to do first: merge and strip names, tell people at the start that this is the plan, drop the note field, leave out a spread that would be recognizable, and know that whatever service you paste into has its own retention and it is not ours. Weather, Kind words, and Interaction cards are never aggregated at all.

- **Nothing about this touches the site's promise.** No form, no endpoint, no submission, no storage. The page is prose; the work happens in the coordinator's own tool. Cavendish still stores nothing, and still has no server-side code.

- **An independent session ran the spreads and found the method's real flaw.** It produced a correct room list, then reported that it had guessed at six cards. The method names which cards map to which condition, and never says which realm any card belongs to — so every card not in a mapping list left it choosing between "this is weather, it goes with the day", "this has no box, it goes to the remainder" and "this is a realm we never aggregate, drop it" by reading the card's tone. That is exactly the inference the page exists to forbid, and the page was requiring it. `not right now` is an Interaction card and `not yet` is a lily pad; `you don't have to talk` is a Kind word and carries no description at all, so a pasted spread gives nothing to identify it by.

- **The fix was already published and never pointed at.** The whole deck is at [/cards.json](https://cavendish.space/cards.json), every card under its realm. The method now says to fetch it first and sort the paste into realms before mapping anything, and to ask the coordinator rather than guess if it cannot.

- **"Something soft" was in the wrong place, and it was a mapping made from a card's name.** The card reads "a plush thing to hold" — a comfort object — and it had been mapped to the room condition "something soft to sit or lean on" because the words matched. It is kit. The condition stays, because a room does still need somewhere soft to sit, but no card in the deck asks for it: a person who wants it will say so in their own words, which is what the remainder is for.

- **The brief no longer summarizes the weather at all.** It used to be allowed one plain sentence about the day. "The weather ran the full range" sounds harmless and is still a claim about a group of people's moods, which two of the three rules forbid. The brief now says only that weather was laid and is not being summarized, and that anyone who wants to know how the day felt can ask the people who were there.

- **"Dropped unread" was a comforting phrase for something that did not happen.** You have to read a note to know it is a note. The brief now says a note field was present and is not used, which is true, and says plainly that the only step which can keep a note unread is the one before the paste.

- **Three smaller contradictions closed.** The self-check told coordinators to reject any brief containing a category outside the vocabulary — which is precisely what the two remainder lines carry, so a correct brief failed its own check. A zone somebody asked for had nowhere to go, since the link carries conditions only; the method now says zones are carried by hand and why. And the brief's own lists had no stated order, so any order could be read as a ranking; the room list now runs in the page's fixed order.

- **A second test run found the method reading the wrong lines.** A spread copied out of the deck carries the reflection question the app offered under each card, and several of those questions name *other cards* as examples — "is there a lily-pad card that fits right now — not yet, slowly, or i need a minute?" names three cards nobody laid. The method said nothing about those lines. A tool matching card names against the whole paste would have pulled a pacing need out of a spread where somebody laid nothing but weather, which is the exact failure the page exists to prevent. It now says to read only the card lines, and why.

- **The strip list was inconsistent with itself.** The method told coordinators to remove Interaction cards and the note field, then told the tool that a Kind word or a grower in the paste meant the strip step had failed — a step that had never asked for either. Everything that never aggregates is now named in one place and left out of the paste together, which also means less of it reaches a third party.

- **The zoner link is now written out, not inferred.** The method told a tool to put the ids "after `#asked=`" and never said what came before it — the address itself appeared only inside an example of finished output. That worked, because a capable tool reads the example and copies it, but it meant the one instruction the coordinator actually carries away was the one thing never stated outright. The section is now called how to build it rather than what it does not do, and gives the whole address, the separator, a worked example, and the rule that the link always starts `https://cavendish.space/` because it gets pasted into a message, not into that page.

- **The group-brief method got tested, and four things were wrong with it.** Twelve generated spreads went through it in a separate session, which is the only way to find out what a set of instructions actually does. The room list and the zoner link came back exactly right. What it caught was everything the method had no rule for.

- **Growers were not addressed at all.** Dandelion, tulip and orchid describe how a person grows and what conditions they need — self-description, and a pile of it summarized is the closest this deck comes to producing a profile. The method now names growers alongside Kind words and Interaction as never aggregated. It also says why they are the most tempting thing here to mine: "give me my conditions and I bloom" sounds like it names conditions, and does not name which.

- **Lily pads fell through a gap.** The mapping table gestured at "the lily pads about going slowly," which left `stuck` and `watch first` belonging to nothing. They now split three ways, named card by card rather than described: `coming back` maps, because it asks the room to hold a place; the four pace requests map; `ready now` and `all done` are passing states and are never aggregated; `stuck` and `watch first` go to the remainder with a question. Nothing is left to inference.

- **A brief must now say what it had to drop.** If an Interaction card, a Kind word, a grower or a note field is in the paste, the strip step did not happen, and the coordinator has to learn that before the next event — a silent drop teaches them the process worked when it did not. The report names the kind and nothing else: never the content, never how many. The note field matters most: it is the most identifying text in a pile, and often the most mappable, which is exactly why it is not the tool's to mine.

- **The remainder was doing two jobs.** "Somebody drew their own card" and "this page could not place a card that exists" are different problems and ask different questions — one is a gap in the deck, the other a gap in the instructions. They are two lines now, and neither is ever resolved by stretching a condition to fit.

- **And the brief can now arrive in the zoner.** [Zone a room](https://cavendish.space/rooms.html) reads a group brief from the end of its own URL — `rooms.html#asked=quiet,corner,way-out` — and shows what was asked for beside what the room has: asked for and already here, asked for and not there yet. Tick what is true and the rest is the to-do list.

- **It does not tick the boxes for you, on purpose.** A tick means the room has something; a brief means somebody asked for it. Pre-filling a brief would make the page announce zones the room cannot actually hold, which is the one thing that page exists to refuse. So the brief is a layer beside the form, not a shortcut into it, and "put the brief aside" clears it without touching your ticks. The page re-sorts the list into its own order, so a tool that ranked its output cannot pass the ranking along, and it still never counts anything.

- **The link is a fragment, which is the whole reason this needs no server.** Everything after the `#` stays in the browser and is never put in the request — that is how URLs work, not a promise being made. The list is not saved to your browser either, because it is a record of what people asked for: close the tab and it is gone, the same as a spread. Still no form, still no endpoint, still nothing stored.

- The print-and-play PDF is no longer rebuilt when nothing has changed. It renders differently every time it is built — same pages, a few bytes apart — so every full build left a 3.7MB file looking modified when it wasn't, which both hid real staleness and would have padded the repository with meaningless copies. It now checks a hash of what actually shapes it and does nothing if that hasn't moved.

- **The printed facilitator sheet had been saying the wrong thing since July.** The deck was rewritten for all ages in the summer — `child` became `person`, `adult` became `facilitator` — and the web version changed with it, but the PDF you actually print and hand to someone did not. It still said "the child controls sharing," still described "Build my day" as being for "a child and a support worker," and was missing the rewritten "Map the edges." Rebuilt from the current source, along with the print-and-play deck, which had been missing two pages of cards added since July.
- **And the reason it lagged is fixed, not just the lag.** The PDF builders need native libraries that Apple's system Python cannot load, so rebuilding them meant remembering an undocumented local setup — which is why two months passed. `build-all.py` now finds the right interpreter itself and runs the PDF steps with it, so one command rebuilds everything. Where that interpreter doesn't exist, it skips exactly as before and prints the three commands that would fix it.

- **The guidebook is now published as Markdown too**, at [`/guidebook.md`](https://cavendish.space/guidebook.md) — the whole deck, every card, in one file an agent or a reader can take whole. It was the one page held back from the Markdown endpoints, because its Markdown was built by a different script than its web page and could fall behind the deck without anyone noticing. The document builder moved into a function both scripts call, so the web guidebook, the Markdown guidebook, and the copy in the repository are now rendered from the cards in a single pass and cannot disagree. Checked by changing a card and watching all three move together.

- **HSTS now covers subdomains.** The site already told browsers to use HTTPS and nothing else; it now says the same for every subdomain of cavendish.space. Checked before shipping rather than after: `www` is the only subdomain, it serves valid HTTPS, and the certificate is a wildcard, so nothing was left behind by the change. No `preload` — the preload list's own operator advises against it now, and getting off the list takes months.

- **Added a security contact.** [`/.well-known/security.txt`](https://cavendish.space/.well-known/security.txt) (RFC 9116) tells anyone who finds a hole here where to send it, instead of leaving them to guess between an issue tracker, a contact form, and posting publicly. The privacy page gained the human-readable half: what to report, where, and that there is no bounty because this is a small nonprofit project. The file is generated rather than hand-written, because the RFC's required `Expires` field invalidates it once it lapses — every deploy pushes the date out again. It is served from the site root and rewritten to the canonical `/.well-known/` path, because Netlify quietly declines to publish dot-directories — which it does not warn about and which only shows up as a 404 on the live site.

- **The site is now readable by machines without scraping it.** Every prose page is published as its Markdown source alongside its HTML — `/why.html` is also `/why.md` — carrying frontmatter with the title, the canonical URL, the date the source last changed, and the CC0 licence. The Markdown is copied in the same build that renders the HTML, from the same file, so the two cannot drift. Nine pages; the guidebook is deliberately left out, because its Markdown is generated by a different script and would ship a snapshot that falls behind the deck.
- **Added [`/llms.txt`](https://cavendish.space/llms.txt)** — a short curated index rather than a restatement of the sitemap. It leads with the two things the deck is most often mistaken for: it is not a screening tool, and it is not an AAC board. If a model is going to summarize this project, those are the sentences it should have. Advertised with `rel="describedby"` in every page head and as a `Link:` header, which is the part llms.txt v2 added and the part sites usually skip.
- The homepage footer now says both are there, for anyone reading with a machine.

- **A real 404 page.** A broken link used to land on Netlify's stock "Page not found" — right status code, wrong everything else: no menu, no route back, and not a word in the deck's voice. `/404.html` is now generated from the same shell as every other prose page, so its menu comes from `SITE_NAV` and cannot drift. The copy holds the line the rest of the deck holds: a dead link is a broken system, not a visitor who did something wrong. It names four doors back in and says where to report the bug.
- **Dark mode was telling the browser it was light.** Every page shipped `<meta name="color-scheme" content="light">` while the stylesheet has shipped a full dark theme for months. Browsers took the meta tag at its word, so dark-mode visitors got light-rendered scrollbars and form controls, and the white flash the no-flash script exists to prevent. Now `light dark`.
- `theme-color` was a single cream value, which put light browser chrome above a dark page. It is now a light/dark pair keyed to `prefers-color-scheme`, using the same two `--bg` tokens as the stylesheet.
- **The web manifest was served as `application/octet-stream`.** Netlify has no mapping for the `.webmanifest` extension, and some browsers refuse a manifest at the wrong type — which would have broken add-to-home-screen silently, with nothing in any log. `netlify.toml` now pins `application/manifest+json`.
- The standalone page shell's one-line description is now overridable instead of hardcoded. It had to be: "you're on one of its pages" is false on the page that says a page isn't there.

## 2026-09-15

### Site

- **The five zones are now drawn, not just listed.** Between the doors and the footer, the threshold carries a landscape of the whole model: a cave in a hillside, a campfire ringed with stones, a watering hole, a library, and the ground that holds all four — with a dashed path of stepping stones running between them, because the edges and the lily pads are part of the model too. Hand-drawn SVG, every fill a theme token, and a caption that names each zone in plain text so the meaning is never trapped in the picture.
- The mark now appears on the front page too, locked up beside the wordmark the way it is on the share card. It is the same `favicon.svg` the browser already fetched for the tab rather than an inlined copy, so the logo on the page cannot drift from the icon when the generator rebuilds it.
- **New mark.** The favicon was a fan of three cards, which described the site when the site was a card deck. It is now **a sheltering arch with a hearth inside it** — the cave and the campfire in one shape, on the house cream tile that reads as the habitat holding them. Chosen by rendering the candidates at 16px and looking: a three-zone version was legible at 64px and mush at 16, which is the size that actually matters.
- Icons and the Open Graph card are now generated from one SVG source by `scripts/build-icons.py`, so the mark is defined once. Three variants, for a real reason: a browser tab draws the favicon as-is and keeps its rounded border, while Apple and Android mask app icons and crop the edges — a rounded tile inside a mask gets its corners shaved twice.
- **New share card** at 1200×630, set in Atkinson Hyperlegible like the site, carrying the mark, the line *places built to fit bodyminds, not the other way round*, and the two verbs. The old `og:image:alt` described a fan of cards on a cream background, which had not been true since the image changed; it now describes what is actually in the picture.
- Fixed a latent cache bug found while doing it: the service worker's version hash was computed from the HTML, CSS, JS and card faces but **not** the icons it precaches — so an icon-only change would never have reached a returning visitor. Everything precached now feeds the version.

- **The site moved to [cavendish.space](https://cavendish.space/).** The name now matches what the site is: Cavendish Space holding the deck, the room zoner, and the model, rather than a card deck that grew two more things. **cavendish.app keeps working** — it stays registered, stays an alias on the site, stays on the certificate, and 301s path-for-path, so every existing link lands on the same page it always did.
- Everything the site says about itself moved with it: canonical URLs, Open Graph and Twitter URLs, the JSON-LD graph, the sitemap, robots.txt, and the footer on the printable room signs, which had the old domain baked into the sheet you pin to a door.

- **The home page is now a threshold, not the deck.** `/` opens **Cavendish Space** — three doors, above the fold, no scrolling to reach a tool: *Show how you feel* (the deck), *Set up a room* (the zoner), and *Read the idea* (the model, at stimpunks.org). The deck keeps everything it had and now lives at **[/deck.html](https://cavendish.space/deck.html)**, first and largest among the doors because it is the one with an audience already pointed at it.
- **The threshold is deliberately thin on prose.** The deck's promise is that no reading is required to use it, so a landing page that has to be read would charge its own audience at the door. One line of framing, three doors, and a link to the rest. The full Cavendish Space model stays at [stimpunks.org](https://stimpunks.org/space/cavendish/) rather than being restated here — one canonical explainer, not two.
- An installed app still opens the deck: `start_url` in the web manifest now points at `/deck.html`, so anyone who added Cavendish to a home screen lands where they always did.
- Added **[What is a Cavendish Space?](https://cavendish.space/space.html)** — a condensed but detailed account of the model, so the third door on the threshold stays on site instead of sending a first-time reader straight off it. Who Cavendish was and why the name carries an argument about privilege; caves, campfires, and watering holes with their Thornburg lineage; the rhythm of intermittent collaboration that keeps them distinct; the eleven elements; dandelions, tulips, and orchids; and what the model refuses. It ends with the full set of stimpunks.org resources — the model, the project, the Why Sheet and broadside, and the glossary vocabulary.
- **stimpunks.org stays canonical, and the page says so twice** — once at the top and once in the footer: *where the two differ, that one is right.* A condensed copy that does not name its source is how you end up with two explainers and no way to tell which is current.
- The page carries **all five zones** — cave, campfire, watering hole, library, and habitat — each with what it looks like in practice and the design recipes behind it, condensed from [Designing Cavendish Space](https://stimpunks.org/cavendish/). Three come from Thornburg's primordial learning metaphors; the library and the habitat complete them.
- It also carries the two parts of the model that are easiest to leave out and most likely to be what actually breaks: **the edges**, where transitions between zones consume processing time and drive masking pressure — *design is tested at the edges* — and **lily pads**, the small landing places that stabilise those crossings. Lily pads are a realm in the deck; until now the site explained the cards without ever explaining the idea behind them.

- Added **[Zone a room](https://cavendish.space/rooms.html)** — the deck's environment-side companion. You tick what a room has got, and it says which Cavendish zones the room can hold today: cave, campfire, watering hole, library, habitat. The zones a room can't hold yet come back as a list of **changes to the room**, in the room's own words, never as a lack. Then it prints **signs for the door**, one zone per sheet, because a cave only works if people know not to talk in it — and that knowledge has to be in the room, not in a document.
- **No score, and the code says so.** No number out of five, no percentage, no grade, no pass, no certificate. Every question is about the room and what can be changed in it; no output sentence takes a person as its subject. The page says this out loud before the first question, next to the same commitment the [Livable worlds checklist](https://cavendish.space/livable-worlds.html) already makes.
- **The questions are the deck's vocabulary, not a new one.** The conditions are grouped by the same sense signposts the What helps realm uses — Being in charge, Sound, Light & looking, Touch/Pressure/Temperature, Movement, Space & enclosure, Telling & talking, People & time — so a need named on a card and a condition ticked on this page are the same need. Each zone's requirements are written from its own card's Notes; the wording on the page is the deck's.
- Works with JavaScript off: the five zones and what each one needs are in the page, so it can be worked out on paper. With it on, nothing leaves the browser — state is in `localStorage`, there is no account, and no request goes anywhere.
- Where it sits: a room is the **Environment** rung of [ARLES](https://cavendish.space/arles.html), and the rung below it is what a person actually needs. A spread is a design brief for the room; this is where the brief gets acted on.

## 2026-07-21

### Deck

- Added two cards from the [SLODF ARLES crosswalk](https://stimpunks.org/design/slodf/) (Dark, 2026), where a workplace-inclusion framework's design responses named needs the deck hadn't yet voiced — both chosen to serve everyday all-ages use, not just work: **one thing at a time** (What helps) for task sequencing, reframing the switching cost of a piled-up queue as monotropic focus rather than slowness; and **say it straight** (What helps) for plain, direct communication, holding the double empathy problem (Milton, 2012) in its Notes as lineage rather than as a label. *(For Helen's batch review: `say it straight` is the first card to name the need Double Empathy explains — it patterns to 30 Communication Bandwidth and keeps 28 Double Empathy as a behind-lens; whether a direct-communication card should finally turn Double Empathy into a nameable Pattern is flagged as an open question in the [Pattern crosswalk](https://github.com/Stimpunks/Cavendish-Cards/blob/main/cavendish-cards-pattern-crosswalk.md). Distinctness to watch in playtest: one thing at a time vs let me finish / fewer choices / pulled every way.)*
- Added three cards for playtesting, drawn from the Livable worlds checklist crosswalk where the deck had gaps: **fewer choices** (What helps) for decision overload, **keep it the same** (What helps) for a need for sameness — reframing the labeled "insistence on sameness" as a support need — and **running on empty** (Weather) for everyday depletion, from spoon theory.

### Site

- Added a workplace example spread — **[A new job, first weeks](https://cavendish.space/example-spreads.html)** (an adult, at work) — showing the deck read as a design brief across a workday, and featuring the two new cards. Reinforces adult self-use and the all-ages reframe.
- The **[ARLES page](https://cavendish.space/arles.html)** now situates the deck against the [System-Level Organisational Design Framework](https://stimpunks.org/design/slodf/) (SLODF): SLODF reads *across* four organisational domains but has no Lived Experience layer, and the deck's Weather realm is precisely the layer it lacks. Facilitator-layer framing only — no jargon on the cards.
- The ARLES page also adds a companion section on the [Ecosystemic Model of Distress](https://stimpunks.org/design/ecosystemic-model-of-distress/) (EMD; Gray-Hammond): distress read as a *current* through nested ecosystems, versus ARLES as a *ladder*. Reframes a spread as **feedback** — the bodymind reporting an unsustainable ecosystem — not a symptom list. No new cards: EMD's person layer is already covered by Weather, and its distinctive content is the Systems/power layer the deck deliberately doesn't card.

- Added a **[Livable worlds checklist](https://cavendish.space/livable-worlds.html)** page — a companion environmental audit that pairs with the deck, adapted from Stimpunks' [Livable Worlds Checklist](https://stimpunks.org/design/livable-worlds-checklist/) (after Rose & Lupton, 2026) and dedicated to the public domain under CC0. Eleven areas, from regulation to sustainability, run on the room, the routine, the kit, or the system — never on the person — with no score and no pass mark, plus a section-by-section crosswalk to the cards that voice each need.
- Deep-linked pages now orient newcomers: every guide page carries a sticky top bar with an **Open the deck** button and the Menu, plus a *Cavendish Cards* home link and a one-line description in the header — so landing on a page like the guidebook or the checklist makes clear what the site is and how to reach the playable deck.

## 2026-07-20

### Deck

- **Kind words reframe:** no longer framed as *a gift*. A Kind word is **given to someone, or claimed for yourself** — never earned. The card back now reads *a kind word* / *you don't have to earn it* (was *a gift* / *given, not earned*), the faces read *given or claimed*, and the guidebook and starter deck match. Self-use is first-class alongside giving.

### Site

- Card backs can now be opened in the lightbox — on the table, a face-down card gets the same enlarge button, showing just the back image (no card name or notes) so it can be seen larger without turning the card up. A visual-accessibility fix that keeps the turn-up-to-share gesture intact.
- Offline cache now updates on art-only and guidebook-only changes: the service worker versions by page and card-face **content**, not just filenames — so returning visitors always get the current deck.

## 2026-07-19

### Deck

- Added **let me unmask** (What helps) — permission, and a safe space, to drop the mask for anyone who masks to get by. It names the *need* to stop performing, not the act of masking itself. Lineage: masking / camouflaging; freedom of embodiment (Nick Walker).
- **All-ages reframe:** the whole deck now speaks to people of any age, not just children — *child* becomes *person* throughout, and *adult* becomes *facilitator* where it means the support role (age-neutral wording elsewhere). Self-use and peer-use are first-class: the deck is as much for an Autistic adult naming their own conditions as for a child. The child-safety commitments stay, and children are still named explicitly.
- Mapped the deck to the **[Stimpunks Pattern Library](https://stimpunks.org/patterns/library/)**: each card can carry an optional Pattern field, and the guidebook now shows the pattern(s) each card instantiates, linking the published ones. Facilitator-layer only — patterns never appear on the card itself, the starter deck, or the web card view.
- Added **big step** (Weather) — threshold anxiety: the dread at the edge of a change, like a doorway, a first day, or graduating. The moves for crossing it live in *Lily pads* and *What helps*.
- **Plain-language pass across the whole deck:** every card's guidebook entry rewritten to about a grade-6 reading level (down from ~7.8), one idea per sentence, following [ASAN's plain-language guidance](https://autisticadvocacy.org/resources/accessibility/easyread/). The metaphors, counter-deficit reframes, and lineage all stay — the sentences just got shorter and plainer.
- Added **no words right now** (situational mutism) and **too seen** (exposure anxiety) to Weather, and **no spotlight** to *What helps* — naming the voice going quiet and the discomfort of being seen, with lineage credited to Donna Williams.
- Added the kind word **you don't have to talk**, affirming that not speaking is not the same as not knowing (presume competence).
- Added **tender** (Weather) — the wound of rejection sensitivity, the "emotional sunburn," with lineage credited.

### Site

- Added an **[ARLES & the cards](https://cavendish.space/arles.html)** page — how the deck fits the Stimpunks Design Method (Attention → Relational → Lived Experience → Environment → Systems), with the design-method poster. Markdown pages can now include images.
- The site reflects the all-ages reframe (see Deck), and gained an example spread of **an adult using the deck for themselves** — no facilitator. The behind-the-scenes "adult layer" is now the **"facilitator layer"** across the guidebook and implementation pages.
- Added an **[Example spreads](https://cavendish.space/example-spreads.html)** page — worked gameplay examples that read a spread as a design brief for the environment, not a report on a person.
- The **guidebook** now links community vocabulary in each card's lineage to the Stimpunks glossary (monotropism, interoception, exposure anxiety, and more); the in-the-moment card view stays plain.
- **Copy for a journal** now includes the date and an optional note field (kept only in the copy, never saved).

## 2026-07-18

### Site

- Added a **favicon and app icons** — the card-fan mark — across the site.
- Added **Open Graph and Twitter Card** metadata and a social share image, so shared links show a proper preview.
- The site is now an **offline-capable Progressive Web App**: it keeps working with no connection after the first visit, and can be installed to a home screen or dock.
- Added a **light/dark toggle** and automatic **dark mode** using the Solarized dark palette. It follows your device setting, and the toggle remembers your choice on your own device.
- Self-hosted the **Atkinson Hyperlegible** typeface, removing the third-party font request.
- Added a **Privacy & security page** and a strict set of security response headers, including a Content Security Policy.
- Added a **sitemap, robots.txt, and structured data**, plus web-app metadata, for better discoverability and installation.
- Added this **changelog**, kept in the repository and published as a page on the site.
- Reworked the **I need a bodymind break** button into a calming full-screen break: a modal (with the deck paused behind it) holding the definition of *bodymind*, an affirmation invitation, a self-hosted looping ocean-waves recording by Adriel Jeremiah Wool, and a collapsible list of ways to affirm your bodymind.
- Fixed the **Copy for a journal** button failing silently in privacy-hardened Firefox browsers (such as Zen); it now uses a reliable fallback and shows a "Copied!" confirmation.

## 2026-07-17

### Site

- Fixed a card-identity bug: cards are now keyed by realm *and* slug, so each realm's "your own" card no longer collides with another's in selection, card backs, and faces.

## 2026-07-16

### Deck

- Added the monotropism weather cards — **in the zone**, **meerkat**, **round and round**, and **pulled every way** — with their lineage credited.
- Added **can't tell** (interoception) and **need more** (sensory seeking) to Weather, plus **happy flappy** (happy stimming).
- Added **let me stim**, **let me finish**, and **let me come and go**, along with more niche-construction cards, regrouping *What helps* into twelve sense signposts.
- Reframed *Love Locutions* as self-affirmation (shown as **Kind words** in the app), moved **parallel existence** into *What helps*, and kept penguin pebbling as a guidebook note rather than a card.
- Named the **"not an AAC board"** boundary, with an inclusion test in the card template, the README, and the guidebook.
- Curated the Weather order into a gentle range with no good/bad split, renamed families to **realms**, and made **lily pads** a browsable realm.

### Site

- Added native **Why**, **Origin**, and **Facilitator** pages, a generated **Implementation guidebook**, and a site-wide collapsed menu.
- Added **lightbox zoom** and a collapsible "what this card means" to card previews, and grouped the deck by realm with per-realm info.
- Made laid cards toggle back off the table, kept an added-state on tiles, and added a sticky jump-to-table button.
- Added the **build a niche** and **map your rhythm** play modes (seven ways to play), the Why Sheet, and a consent guardrail in the implementation guidebook.

## 2026-07-15

### Deck

- Added **guidebook Notes to every card** — the entry that says what each card means and how to hold it.
- Added **reflection questions**: per-realm pools plus per-card overrides, with the Reflection field documented in the card template.

### Site

- Added the **playable web deck** and its Netlify build, and linked it from the README.
- Ran four playtest rounds: intro and guidebook pages, a bodymind-break, an interaction-first guided order, sense grouping, a reflection summary, and per-realm draw-your-own.
- Added the **guidebook assembler**, the **print-and-play PDF** builder, and the playtest placeholder generator.
- Added the **call for art**, linked from the README and the site.

## 2026-07-14

### Deck

- **Initial deck** — 49 cards scaffolded across six families.
- Added the **interaction realm** — the Autistic community's color communication badges — with finished card faces.
- Stated the deck is **not a screening tool**, refusing the pathology, deficit, and behaviorism framings.

### Site

- Added print-scale **SVG card templates** for every family plus the blank, and the two card backs.
- Rebuilt the **facilitator sheet** (larger type, six-color rainbow, sharing models) and wrote the project README.
