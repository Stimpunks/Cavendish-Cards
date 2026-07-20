<!-- Project knowledge for the Cavendish Cards Project. Tracked in the repo as cavendish-cards-project-brief.md; paste the current version into Claude Project knowledge (or attach it) when it changes. Durable context only — live counts and status live in the repo. -->

# Cavendish Cards — Project Brief

## What this is

Cavendish Cards is a free, open (CC0), neuroaffirming pictorial prompt-card deck by Stimpunks Foundation. A person of any age SHOWS how they feel and what they need by pointing at or laying pictures — **no reading required, no scoring, no matching, no right answer, no winning.** The person controls sharing: cards lie face-down by default, and turning one up *is* the act of consent. It grows in the open, one card = one Markdown file, community-authored. It comes from the Cavendish Space model.

It is **not** a screening/assessment tool and **not** an AAC board (see Boundaries). A spread is a *design brief for the environment*, not a behavior report.

## Values (non-negotiable)

- **Broken systems, not broken people.** Counter-deficit throughout. A card names a need, a state, or a change to the environment — never the person as the problem.
- **Neurodiversity paradigm**, not pathology. Identity-first language; always **capitalize Autistic and Disabled**.
- **Human/community-made art only — no AI art.** Glossary/Notes are human-authored.
- Nothing about us without us. Helen Edgar (Autistic Realms) owns the values-heavy and Autistic-community calls (see Collaborators for the current, looser review pattern).

## The realms (as of this handoff — the generators compute exact counts)

- **Places** (~6): the cave, the campfire, the watering hole, the library, the habitat (+ your own). The five Cavendish zones. Fixed.
- **Weather** (~18): inner weather, the whole range good and hard. Has a **curated display order** (gentle range, no headings, no good/bad split).
- **What helps** (~28): the niche-construction realm; the largest on purpose. Grouped into ~12 sense **signposts** in its single-realm view (Being in charge, Sound, Light & looking, Touch, Pressure, Temperature, Movement, Mouth & nose, Space & enclosure, Telling & talking, People & time, Make your own).
- **Lily pads** (~10): transitions/moments, rendered as an always-available "moments" strip.
- **Growers** (~4): dandelion/tulip/orchid resilience metaphor. Optional.
- **Kind words** (~9): affirmations. Display label is **"Kind words"** in the app (subtitle "Also called Love Locutions or Love Languages"); the **guidebook keeps "Love Locutions."** Reframed as **self-affirmation / self-advocacy** (claim it and show it), not gift-giving, on the web. Folder/slug stays `love-locution`.
- **Interaction** (~6): the Autistic community's red/yellow/green communication badges (ANI/Autreat/Sinclair 1996). The one exception to face-down default — meant to be shown.
- **Blank** (1): draw your own. Every realm also carries a `your-own` card.

## Repository & deployment

- Public repo: **github.com/Stimpunks/Cavendish-Cards** (CC0, branch `main`).
- Ryan's local clone (Claude edits here via Filesystem MCP): **/Users/ryan/Documents/GitHub/Cavendish-Cards/**
- Deployed web app: **https://cavendish.app/** (Netlify; builds `web/` via `scripts/build-site.py`). All in-repo links point to cavendish.app.
- Card art submissions → **stimpunks@stimpunks.org** (see CALL-FOR-ART.md). CC0, no AI.

## How Claude and Ryan collaborate (workflow)

- **Claude writes files into Ryan's clone; Ryan commits/pushes and runs scripts himself.** Claude cannot run code on Ryan's machine and has no delete tool (file deletion = Ryan runs `git rm`; `Filesystem:move_file` exists for moves/renames, load it via tool_search).
- **Claude validates on its own container**, not Ryan's machine: `git clone` the public repo to `/home/claude/cc`, sync changed files in (Ryan-repo → `copy_file_user_to_claude` → `/mnt/user-data/uploads` → `cp` into the clone), then run generators / `node --check` (JS) / `py_compile` (Python). The container has cairosvg + weasyprint + node + Atkinson fonts. (Note: a given container may lack weasyprint — that's fine, it mirrors Ryan's own weasyprint-less setup; see the facilitator flag below.)
- **Rebuild rule:**
  - Deck-content or generator change → `python3 scripts/build-all.py`, then `git add -A && commit && push`.
  - Hand-authored web file (`web/index.html`, `web/styles.css`, `web/app.js`) → **no rebuild**; Netlify serves as-is. Just commit those files.
  - `web/cards.json`, `web/guidebook.html`, `web/implementation.html`, `web/why.html`, `web/origin.html`, `web/facilitator.html`, `web/example-spreads.html`, and `web/faces/` are **gitignored** (generated; Netlify rebuilds).
- After edits, Claude hands Ryan the exact `git add/commit/push` commands. **Claude cannot see whether a commit actually landed — always confirm.**
- **Always mirror a validated container edit back into Ryan's repo** (the failure mode this session: patching the container copy but forgetting the `Filesystem:edit_file` to the repo → git sees nothing).

## Card schema & conventions

- `cards/<realm>/<slug>.md`: `# name` (lowercase, deck-facing), `## Family` (folder-matching key), `## Image cue` (motif for illustrator), `## Prompt` (gentle optional line; `—` for Kind words), optional `## Reflection` (bulleted per-card override), `## Notes` (guidebook entry — metaphor / what it names / how to hold; "When this card is out…"; describe the card, never the person), optional `## Pattern` (facilitator-layer Stimpunks Pattern map; never card-facing), `----`, `## License` (CC0).
- **Notes carry a reframe, not just a label** — this is the anti-AAC feature. Lineage credited in Notes where relevant (e.g., Adkin & Gray-Hammond for monotropism terms; Nick Walker/NQLS for embodiment; Erin/@EisforErin for tendril theory; ANI/Sinclair 1996 for Interaction; Cavendish Space for intermittent collaboration).
- Voice: short declarative sentences, stakes first, no hedging, no marketing register, em-dashes and fragments for weight. US spelling. Deck-facing copy lowercase.
- Generators live in `scripts/` and read `cards/**` by folder. `build-all.py` runs them all. Reflection pools + display labels + signpost groups + curated order + subtitles + guidebook realm-notes are constants at the top of `build-site.py`; the starter deck's curated order + play modes are in `build-starter-deck.py`; the markdown guidebook's realm-notes are in `build-guidebook.py`.
- Reflection questions: hybrid (per-realm pool in `build-site.py` + optional per-card `## Reflection` override). On the table/summary, a spread **distributes** questions across the pool so they don't repeat.
- **Standalone web pages** are generated by `build-site.py` into `web/` (all gitignored; Netlify rebuilds): `guidebook.html` and `implementation.html` from the cards; `why.html` and `origin.html` from `cavendish-cards-why-sheet.md` / `cavendish-cards-origin.md` via a small no-dependency `md_to_html` in `build-site.py`; and `facilitator.html` by **reusing `build-facilitator-pdf.py`'s `parse()`** (loaded like `build-placeholders.py`) so the on-site sheet and the print PDF render from one source. **Do not** hoist the `weasyprint` import to module level in `build-facilitator-pdf.py`, and don't change `parse()`'s `(title, kicker, blocks)` return shape — either breaks the site build on Netlify and on weasyprint-less machines.
- A no-JS `<details>` **site nav** links all pages: `SITE_NAV` in `build-site.py` (for the generated pages) mirrored in hand-authored `web/index.html` (in the floating breakbar). Keep the two in sync when adding a page.
- The spread summary in `web/index.html` carries a "What a spread is for" note (design-brief framing; "Regulation before instruction. Environment is curriculum.") linking the Why page — values wording, so route through Helen per the batch-review pattern.

## Decision log (settled — don't relitigate without reason)

- **All ages, not just children** (per Helen's request). The deck's framing was broadened from child-specific to all ages: `child` → `person`, `adult` → `facilitator` where it means the support role, or age-neutral phrasing otherwise; the "adult layer" term of art is now the **"facilitator layer."** Self-use and peer-use are first-class (Kind words are self-affirmation on the web; example spread 8 is an adult using the deck for themselves, no facilitator). Child-safety commitments are retained and children are still named explicitly (e.g. the AAC-alongside line). Origin's historical "children with PMLD" / "adult professionals" wording is left as-is. **Resolved (was an open item):** added `let me unmask` (What helps) — a niche-construction *need* (permission and a safe space to unmask), which passes the inclusion test as a request to the environment, not a "you are masking" behavior-label. The deck still never asks anyone to name masking as a meta-observation; `let me unmask` and `no-spotlight` address the masking *pressure*, not the mask itself. Logged for Helen's batch review.

- **Not an AAC board.** Inclusion test (in `CARD.md`): a card earns its place if it names a hard-to-voice inner state or a niche-construction need AND carries a reframe — not if it's a want/object/action a person could request. "can't tell" (experience) belongs; "hungry" (request) does not. The deck sits **alongside** real AAC, never replacing it (child-safety line, in README + guidebook).
- **Not a screening tool** (in README + guidebook).
- **Materials stay in the facilitator layer.** The deck names the *need*; specific materials/techniques (tents, projectors, budget hacks) live in the guidebook + linked posts (Cavendish Space on a Budget, Nesting), not as cards.
- **Kind words reframe:** self-affirmation on the web; "given, not read" kept only in print/guidebook; distinct card back retained (flagged for possible reconsideration).
- **penguin pebbling** is the giving *verb*, not a card → guidebook note. **parallel existence** = body doubling → What helps.
- **Monotropic-spiral clinical depth** (burnout→psychosis) stays OUT of the person cards; "round and round" names only the everyday looping-thought feeling.
- **Seven play modes is the ceiling:** Show me · Build my day · Class weather · Map the edges · Play as the environment · Moving between (map your rhythm) · Build a niche. Listed in web app, starter deck, and facilitator sheet.
- **Weather grouping:** flat with a curated order, NOT signpost headings (feelings don't sort cleanly, and a good/bad split would betray the ethos).
- **Pattern crosswalk (facilitator layer).** Each card may carry an optional `## Pattern` field mapping it to Stimpunks Pattern(s); renders in the Markdown + web guidebook only, never on the card face / starter deck / web card view (stripped from cards.json). Registry of slugs lives in `build-guidebook.py`; `build-site.py` imports it. Full map in `cavendish-cards-pattern-crosswalk.md`. Anxiety-cluster Patterns 52–54 drafted for the Library, pending Helen review before publish/wire.

## Collaborators

- **Ryan** — Co-Creative Director / Board Chair, Stimpunks. Drives the build; commits/pushes. Approves values-heavy / counter-deficit / Autistic-community / lineage wording, including in Helen's stead.
- **Helen Edgar** — Autistic Realms; co-creator of Cavendish Space. Owns the values-heavy and Autistic-community calls (monotropism framing, self-affirmation reframe, "not AAC" wording, sensory/interoception language) — but trusts Ryan to make these in her stead and reviews in batch later. Different timezones, so approval shouldn't block iteration: ship with Ryan's sign-off and **log the change for Helen's batch review** rather than waiting on her.

## Open flags at handoff

- Confirm outstanding commits actually pushed (reflection-distribution `web/app.js`; build-a-niche; "Not AAC" docs).
- **Facilitator sheet renders from one source; the print PDF lags.** `cavendish-cards-facilitator-sheet.md` is the single source for the web page (`web/facilitator.html`, generated by `build-site.py`, gitignored, Netlify rebuilds), the print PDF (`cavendish-cards-facilitator-sheet.pdf`, via `build-facilitator-pdf.py`), and the md itself. Content can't drift — same parser — but they rebuild on different schedules: the web page auto-updates every deploy; the PDF only when Ryan runs `python3 scripts/build-facilitator-pdf.py` locally with the macOS weasyprint/DYLD workaround (below). **After editing the sheet, rebuild and commit the PDF** or it trails the live web version.
- Distinctness to watch in playtest: pulled every way vs full · meerkat vs buzzy/prickly · round and round vs stormy · let me finish vs tell me first / no rush · let me come and go vs not right now · can't tell vs foggy / far-away.
- macOS PDF build needs native libs (`brew install cairo pango gdk-pixbuf libffi`) + a Homebrew-Python venv with `DYLD_FALLBACK_LIBRARY_PATH` (Apple system Python strips `DYLD_*` under SIP).

## Starting a new Project chat

A Project holds this knowledge, but **not** the live tooling. Each new chat still needs the Filesystem connection to Ryan's clone and network enabled; Claude re-clones the public repo to its container for validation. Open with: *"Continue Cavendish Cards"* + point at the repo path.
