# Group access needs

At an event, people lay spreads. A coordinator cannot hold twenty spreads in their head, and should not try. This page is a method for turning a pile of spreads into one short brief for the room — and a skill description you can hand to whatever AI you already use, so it does the sorting without inventing anything.

The method exists because of what goes wrong without it. Left alone, a general-purpose AI will cluster access needs into categories it made up, rank them by how many people asked, and hand back something that reads like a report on a group of people. All three of those are failures. What follows is narrow on purpose.

## What it does

It maps a pile of spreads into a fixed vocabulary that already exists in this project — the seventeen room conditions behind [Zone a room](rooms.html), plus three buckets that are not the room at all. Then it says what the room, the kit, the permissions, and the pacing need to be.

The AI's job is translation, not analysis. It is not looking for patterns. It is putting each named need into one of a set of boxes a human already built, in language a human already wrote. Anything that does not fit a box is listed as-is, under the card's own name, rather than forced into one.

That is the tree the idea started with. The branches are just authored rather than discovered.

---- 

## Before you paste anything

Turning a card face-up is the consent. That consent was given to the room, in the moment, to the people there. It was not given to an AI company.

So there is a step before the method, and it is not optional.

- **Merge first, strip names.** Combine every spread into one list with no names, no initials, no ordering that tracks who sat where. You are pasting a pile, not a stack of labeled sheets.
- **Say what you are doing, before people lay cards.** "I'll type these up and use an AI to turn them into a list of changes" is a sentence people can decline. Ask at the start, not after.
- **Know that a small group is identifying.** In a group of eight, one unusual card is a pointer at a person even with the name gone. If a spread would be recognizable, leave it out of the paste and carry it yourself.
- **The AI is a third party.** Whatever service you use has its own retention and its own training policy, and neither is ours. Cavendish stores nothing at any point in this — but the moment you paste, that stops being the whole story.
- **Drop the note field.** The deck's copy button includes anything a person typed into the note box. That is the most personal part of a spread and the least necessary for this. Delete it before you paste.
- **Do not paste a headcount, and strip the dates.** "Twelve people, one pile" hands over a number before the brief starts, and a date plus a small group narrows who was there. Neither helps and both travel.
- **Leave out the realms that never aggregate.** Interaction cards, Kind words and growers do not belong in a room brief (the reasons are below), and the simplest way to keep them out of one is to keep them out of the paste. Less goes to a third party that way, too.

If any of that cannot be honored, do the sorting by hand. The vocabulary below works fine with paper.

If something that should have been stripped goes in anyway, the brief will say so — which is a safety net, not a plan. It reports that a note field was there; it cannot un-send it.

## Three rules

These are the rules the tools already follow, written so an AI can follow them too.

**No score.** Never a number out of five, never a percentage, never a grade, never a pass, never a readiness level. A room that holds nothing yet is a room with a to-do list, not a room that failed.

**The subject is always the room.** No output sentence takes a person or a group as its subject. Not "attendees struggle with noise" — "this room needs somewhere it can be made quiet." A spread is a design brief for the environment. It is never a report on who was there.

**No counting.** Do not say how many spreads named a thing, do not sort by it, do not mark anything as common or rare or an outlier. Access is not a vote. One person needing a way out is exactly as actionable as eight, because you build the way out once either way. Counts also re-identify: in a small group, "named once" points at somebody. The brief names what the room needs and stops there.

---- 

## First, the card roster

Before any of this, fetch **https://cavendish.space/cards.json**. It is the whole deck as data: every card, under the realm it belongs to. You need it, because which realm a card came from decides everything below, and a card's name does not tell you. `not right now` is an Interaction card; `not yet` is a lily pad. `you don't have to talk` is a Kind word and carries no description at all, so there is nothing in a pasted spread to identify it by.

Use the roster to put every line of the paste in its realm first. Then map.

**If you cannot fetch it, ask the coordinator which realm each unfamiliar card came from.** Do not infer a realm from how a card sounds. Guessing a realm is how a mood becomes a room change and how a worn badge ends up in a summary — and you will not know you got it wrong.

## The room conditions

Seventeen conditions, each phrased as the change rather than the lack. These are the same ids [Zone a room](rooms.html) uses, so a brief written in them can be ticked straight into the zoner. After each one: the cards that map to it.

- `quiet` — somewhere it can be made quiet. From: headphones, less talking, a den.
- `steady-sound` — steady background sound or headphones allowed. From: a steady sound, headphones.
- `dim` — light that can come down or a corner out of the brightest light. From: dim the light, a den.
- `less-to-look-at` — somewhere with less to look at. From: less to look at.
- `soft` — something soft to sit or lean on. From: none yet.
- `temperature` — a temperature people can change or dress for. From: the right temperature.
- `room-to-move` — room to move without being in anyone's way. From: room to move, parallel existence.
- `sit-my-way` — permission to sit however you like. From: sit my way.
- `corner` — a corner or nook out of the main flow. From: a corner, a den.
- `own-spot` — a spot that can stay someone's for the session. From: my own spot, coming back.
- `way-out` — a way out that doesn't cross in front of everyone. From: a way out, no spotlight.
- `come-and-go` — leaving and coming back without explaining. From: let me come and go, a way out, coming back.
- `control` — let people in the room change things in it. From: let me control it, let me unmask.
- `written` — what happens here written down or posted. From: tell me first, another way to talk.
- `another-way` — a way to take part other than speaking aloud. From: another way to talk, no spotlight.
- `no-rush` — things not all at one pace. From: no rush, one thing at a time, let me finish, i need a minute, not yet, slowly, i want to stay a while.
- `small-group` — somewhere a small group can meet without the room listening in. From: just one person, parallel existence.

## The three buckets that are not the room

Plenty of what a spread names is not a fixture. Forcing it into a room condition loses it. These go in their own lists.

**Kit** — things the space stocks or a person brings. A big squeeze, something soft, busy hands, something to chew, a snack or a drink, a smell that helps. Mostly an afternoon and a budget. The [implementation guidebook](implementation.html) covers doing this on no money.

**Permission** — things that cost nothing and are a rule, not a purchase. Let me stim, let me unmask, sit my way, say it straight, no spotlight. These belong on the signs, in the opening announcement, and in what the staff are told. A permission that is not said out loud has not been given.

**Pacing** — how the session runs. Keep it the same, fewer choices, tell me first, one thing at a time, let me finish, no rush, and the four lily pads that map to `no-rush`. Those land in both: the room has to allow more than one pace, and the agenda has to actually use it. This is the agenda, not the furniture.

`soft` has no card yet. Nothing in the deck asks for soft seating: `something soft` sounds like it does and does not — it is "a plush thing to hold," a comfort object, so it is kit. The condition stays in the list because the zoner uses it and a room still needs somewhere soft to sit; it just will not arrive from a card. A reader who wants it will say so in their own words, which is the remainder's job.

A card can land in two lists. Let me unmask is a room condition and a permission; do both. Sit my way is a permission the room has to physically allow. Overlap is not a mistake to resolve.

## What never gets mapped

**The `reflect:` lines are not answers.** A spread copied from the deck carries the reflection question the app offered under each card. Those questions are the app talking, not the person, and several of them *name other cards as examples* — "is there a lily-pad card that fits right now — not yet, slowly, or i need a minute?" names three cards nobody laid. Read only the card lines. A tool that matches card names against the whole paste will find needs that were never asked for, and the spread that suffers most is the one where somebody laid nothing but weather. Ignore every `reflect:` line, or delete them before pasting.

**Weather cards are not needs.** Stormy, foggy, running on empty, too seen — these say how a day felt. They do not convert into a room change, and an AI that infers one ("several people were stormy, so add quiet") is guessing at people from their moods. Weather is not summarized at all — not as a list, and not as a sentence about how the day went. "The weather ran the full range" sounds harmless and is still a claim about a group of people's moods, which rules two and three both forbid. Say only that weather was laid and is not being summarized, and that anyone who wants to know how the day felt can ask the people who were there. They are right there, and they are better at it than you.

**Kind words are never aggregated.** They are given to someone or claimed for yourself. They are not a need and not data.

**Interaction cards are never aggregated.** The red, yellow, and green badges are worn, live, for a moment, and meant to be changed the second they stop being true. A summary of who was red today is a behavior report wearing a badge's clothes. Leave them out of the paste entirely.

**Growers are never aggregated.** Dandelion, tulip, orchid describe how a person grows and what conditions they need to bloom. That is self-description, and turning a pile of it into a summary is the closest this deck comes to producing a profile. It is also the most tempting thing here to mine, because "give me my conditions and I bloom" sounds like it names conditions. It does not name which. Leave growers out.

**Places go to the zones, not the conditions.** If people laid the cave, the room needs a cave. That is a direct request for a zone and should be read as one.

**Lily pads split three ways, and the mapping table already says which.** `coming back` asks the room to hold a place, so it maps. `i need a minute`, `not yet`, `slowly` and `i want to stay a while` are pace requests, so they map. `ready now` and `all done` are passing states like weather — a person announcing where they are in a moment — so they are never aggregated. `stuck` and `watch first` are neither: they name a moment the vocabulary above has no box for, so they go to the remainder with a question attached. Do not stretch a condition to cover them.

---- 

## What the output looks like

Four lists, a zone read, and two kinds of honesty at the end. No preamble, no summary of the group, no recommendations about people.

- **The room needs** — somewhere it can be made quiet · a corner or nook out of the main flow · a way out that doesn't cross in front of everyone · light that can come down · a temperature people can change or dress for
- **Kit** — something soft to sit or lean on · something to chew · a snack and water within reach
- **Permission, say it out loud** — stim freely · sit however you like · leave and come back without explaining
- **Pacing** — post the plan before the session · one thing at a time · nothing on a single clock
- **Zones asked for** — the cave, the watering hole
- **The deck had no card for this** — someone drew their own. Ask what they drew; it may be a card this deck still owes people.
- **The method had no box for this** — "stuck", "watch first". Ask whether the room owes them a change of pace or just somewhere to land.
- **Should not have been in the paste** — an Interaction card, and a note field. Neither is used in this brief. The strip step did not happen; do it before the next one.
- **Weather** — laid, and not summarized. If you want to know how the day felt, ask the people who were there.
- **A link to the zoner** — https://cavendish.space/rooms.html#asked=quiet,corner,way-out,dim,temperature

**The two remainders are different questions, so they are two lines.** "The deck had no card for this" is a gap in the deck — somebody needed something that does not exist yet, and the answer might be a new card. "The method had no box for this" is a gap in *these instructions* — the card exists and this page could not place it. Never merge them, and never resolve either by stretching a condition to fit.

**Put the room list in this page's order**, not the order the cards arrived in and not longest-first. Any order can be read as priority, so use one that obviously is not: the conditions run down this page in a fixed order, so use that. The other lists can run in any order that is not frequency.

**And say what you had to drop.** If an Interaction card, a Kind word, a grower, or a note field is in the paste, the strip step above did not happen, and the coordinator needs to know that before the next event — a silent drop teaches them the process works when it did not. Name the *kind*, never the content, and never how many: "a note field was present; it is not used in this brief" and nothing more. Do not write "dropped unread" — you had to read it to know what it was, and a phrase that reassures the coordinator about something that did not happen is worse than saying nothing. The only step that can actually keep a note unread is the one before the paste. A note is the most identifying text in a pile and often the most mappable, which is exactly why it is not yours to mine.

## The link, and how to build it

The last line of the brief is the room list again, as ids, in a link to the zoner. Build it exactly like this, in full, every time:

> `https://cavendish.space/rooms.html#asked=` followed by the ids, comma-separated, with no spaces.

So a brief naming quiet, a corner, a way out, dimmable light and a temperature people can change ends with:

> [https://cavendish.space/rooms.html#asked=quiet,corner,way-out,dim,temperature](https://cavendish.space/rooms.html#asked=quiet,corner,way-out,dim,temperature)

A zone somebody asked for does not go in the link — the zoner works out which zones a room can hold from what is ticked, so there is nothing for a zone to set. Carry it by hand: say it in the brief, and once the conditions are ticked the zoner will list what that zone still needs.

Three rules for what goes in it. **Only ids from the list above** — the seventeen, spelled exactly as they appear, not the sentence next to them. **Nothing else** — no names, no notes, no weather, no zones, no counts. **Always the whole address**, starting `https://cavendish.space/`, because the coordinator will paste it into a message or a document, not into this page.

A word that is not one of the seventeen is not silently dropped: the zoner names it back to whoever opens the link and says it has no condition for it. A typo is visible rather than lost, which is the same principle as the remainder.

Open it and [Zone a room](rooms.html) shows the brief beside the room: asked for and already here, asked for and not there yet. Then tick what is true, and it says which of the five zones the room can hold today and what each of the rest still needs. Print the signs. The room says it itself, and nobody has to ask.

Three things the link deliberately does not do.

- **It does not tick anything.** A tick means the room has something. The brief means somebody asked for it. Pre-ticking a brief would make the page claim zones the room cannot hold, which is the one thing that page refuses to do.
- **It does not carry an order.** The zoner re-sorts the ids into its own order on arrival, so a ranked list cannot sneak a ranking through.
- **It does not reach a server.** Everything after the `#` stays in the browser and is never put in the request — that is how URLs work, not a promise we are making. The zoner does not save it either. Close the tab and it is gone, the same as a spread.

A link is still a list of what a group of people asked for. Share it the way you would share the brief itself.

## Handing it to your AI

Give it this page and then the spreads. Most tools will fetch a URL:

> Follow the method at https://cavendish.space/group-needs.md exactly. Here are the merged spreads:

If yours cannot fetch, paste this page's text above the spreads. Either way, the method is the whole page — there is no shorter version that keeps the rules, because the rules are the point.

Check what comes back against the three rules before you act on it or show it to anyone. If there is a number in it, a person as the subject of a sentence, or a *category* it invented rather than one from this page, the tool did not follow the method. The two remainder lines are the exception and are meant to carry card names that are not in the vocabulary — that is them working, not failing. Say so and ask again.

## What this is not

It is not a screening tool, and running it over a group does not make one. Nothing here is scored, normed, stored, or compared to a baseline.

It is not a profile. The output describes a room. If you can read a person out of it, something has gone wrong upstream — go back to the merge step.

It is not a substitute for asking. The brief tells you what to change. It does not tell you that you got it right, and the only people who can tell you that are in the room.

---- 

## License

CC0 1.0 Universal. Public domain dedication.
