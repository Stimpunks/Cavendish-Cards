# Changelog

Notable changes to Cavendish Cards — both the **deck** (cards added or reworded) and the **site** (features and fixes at [cavendish.app](https://cavendish.app/)). Newest first; dates are when a change shipped. The site deploys continuously, so there are no version numbers — for the full detail, see the [commit history](https://github.com/Stimpunks/Cavendish-Cards/commits/main).

Each dated entry is split into **Deck** (changes to the cards themselves) and **Site** (changes to the web version). An entry only includes the sections that changed.

## 2026-07-21

### Deck

- Added two cards from the [SLODF ARLES crosswalk](https://stimpunks.org/design/slodf/) (Dark, 2026), where a workplace-inclusion framework's design responses named needs the deck hadn't yet voiced — both chosen to serve everyday all-ages use, not just work: **one thing at a time** (What helps) for task sequencing, reframing the switching cost of a piled-up queue as monotropic focus rather than slowness; and **say it straight** (What helps) for plain, direct communication, holding the double empathy problem (Milton, 2012) in its Notes as lineage rather than as a label. *(For Helen's batch review: `say it straight` is the first card to name the need Double Empathy explains — it patterns to 30 Communication Bandwidth and keeps 28 Double Empathy as a behind-lens; whether a direct-communication card should finally turn Double Empathy into a nameable Pattern is flagged as an open question in the [Pattern crosswalk](https://github.com/Stimpunks/Cavendish-Cards/blob/main/cavendish-cards-pattern-crosswalk.md). Distinctness to watch in playtest: one thing at a time vs let me finish / fewer choices / pulled every way.)*
- Added three cards for playtesting, drawn from the Livable worlds checklist crosswalk where the deck had gaps: **fewer choices** (What helps) for decision overload, **keep it the same** (What helps) for a need for sameness — reframing the labeled "insistence on sameness" as a support need — and **running on empty** (Weather) for everyday depletion, from spoon theory.

### Site

- Added a workplace example spread — **[A new job, first weeks](https://cavendish.app/example-spreads.html)** (an adult, at work) — showing the deck read as a design brief across a workday, and featuring the two new cards. Reinforces adult self-use and the all-ages reframe.
- The **[ARLES page](https://cavendish.app/arles.html)** now situates the deck against the [System-Level Organisational Design Framework](https://stimpunks.org/design/slodf/) (SLODF): SLODF reads *across* four organisational domains but has no Lived Experience layer, and the deck's Weather realm is precisely the layer it lacks. Facilitator-layer framing only — no jargon on the cards.
- The ARLES page also adds a companion section on the [Ecosystemic Model of Distress](https://stimpunks.org/design/ecosystemic-model-of-distress/) (EMD; Gray-Hammond): distress read as a *current* through nested ecosystems, versus ARLES as a *ladder*. Reframes a spread as **feedback** — the bodymind reporting an unsustainable ecosystem — not a symptom list. No new cards: EMD's person layer is already covered by Weather, and its distinctive content is the Systems/power layer the deck deliberately doesn't card.

- Added a **[Livable worlds checklist](https://cavendish.app/livable-worlds.html)** page — a companion environmental audit that pairs with the deck, adapted from Stimpunks' [Livable Worlds Checklist](https://stimpunks.org/design/livable-worlds-checklist/) (after Rose & Lupton, 2026) and dedicated to the public domain under CC0. Eleven areas, from regulation to sustainability, run on the room, the routine, the kit, or the system — never on the person — with no score and no pass mark, plus a section-by-section crosswalk to the cards that voice each need.
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

- Added an **[ARLES & the cards](https://cavendish.app/arles.html)** page — how the deck fits the Stimpunks Design Method (Attention → Relational → Lived Experience → Environment → Systems), with the design-method poster. Markdown pages can now include images.
- The site reflects the all-ages reframe (see Deck), and gained an example spread of **an adult using the deck for themselves** — no facilitator. The behind-the-scenes "adult layer" is now the **"facilitator layer"** across the guidebook and implementation pages.
- Added an **[Example spreads](https://cavendish.app/example-spreads.html)** page — worked gameplay examples that read a spread as a design brief for the environment, not a report on a person.
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
