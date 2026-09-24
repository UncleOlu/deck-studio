# Consulting grammar — how a client deck page is built

Use this for the `consulting` register. The values come from 31 coded client
deliverables (14 of them McKinsey/BCG/Bain) in `research/corpus-findings.md`.
Rule numbers R1–R15 point to that file's ledger. Read `storyline.md` first:
the grammar serves the argument.

## Page anatomy (top to bottom)

| Zone | Content | Rule |
|---|---|---|
| Tracker | Current section name, or the section strip with the current one bold. Top left, small, muted | R8. Use it for decks with 3 or more sections. It is a master placeholder |
| Action title | A full sentence stating the finding and its implication. Median 14 words; **at most 20 words and 2 lines** | R1, R2 |
| Body | One framework (see `frameworks.md`), 1–5 content blocks, on a 2-column grid by default | Finding 10 |
| Emphasis | Accent on the one datum in the title; optional bold lead-ins, circled numbers, highlight box | R11, R13 |
| Notes | Numbered notes (1, 2, 3…) in reading order, above the source line | R6 |
| Source | "Source: …" on every chart or table slide: provider, dataset, date | R5 |
| Page number | Bottom right, from the master | — |

Units go **inside the chart**, in the axis title or data labels. Consulting
pages seldom use a unit line under the title (R7).

## Deck skeleton

1. **Cover:** subject, client, date, "Draft for discussion" where true.
2. **Executive summary, slide 2** (at the latest slide 3): R4. Use the dot-dash
   form. Put the governing answer in bold on top. Under it, 3–5 supporting
   arguments, each one sentence with its key number. Under each argument, 1–3
   dashes of evidence. The titles of the sections that follow repeat these
   arguments in the same order.
3. **Agenda:** only for 3 or more sections. Repeat it as the divider before
   each section, with the current section highlighted. This is the commonest
   MBB divider (8 of 14 decks).
4. **Sections:** each opens with the argument it proves and runs 2–6 slides.
   Every title is a sentence.
5. **Recommendation and next steps:** each action has an owner, a date, and
   the value at stake. Put decisions the reader must take in bold.
6. **Appendix:** after an "Appendix" divider. Back-up analyses keep full
   grammar, but their titles may be descriptive. Keep it to about a quarter
   of the deck or less.

## Density (register override of the bullet-wall ban)

Client pages are denser than keynote pages: 43% of MBB-client content slides
carry more than 120 words. A dense page is allowed **only when it is
structured** (R10):

- a bold lead-in phrase on each point, or a 2-column label/explanation grid;
- 5 content blocks or fewer;
- the title still states the point.

Five plain bullets under a topic title stay banned.

**Vary the callout device** (applies to banking too). Blind judges told
generated slides from real ones 40 times out of 40; the tells they named were
repeated templates: a bold-lead-in side panel restating the title, a tinted
table row, a computed sentence title. Real decks use bold lead-ins on 20% and highlight boxes on 22% of content
slides, mixed with chart annotations, arrows, and circled numbers. Use each
kit device (`side`, `takeaway`, a tinted `subject` row) on about a third of
content slides at most; the kit refuses more. A side panel must add something
the chart does not show, never restate the title.

## Typography and colour (register overrides)

- **Sans titles are allowed** (R9). every MBB-client deck and 45 of 48 board books set titles in a
  sans. A sober sans (Arial Bold, Calibri Bold) is a legitimate choice here.
  Keep the ≥ 2× title-to-body ratio. Title 20–24pt, body 12–14pt, notes and
  source 8–9pt.
- **Palette:** 3–4 meaningful hues. Navy or ink as the primary, one support
  tone, one accent for the datum that matters. Never imitate a firm's brand
  colour (R15).
- 16:9 by default (R14).

## What blind judges marked down (v1.4 evals)

In a blind test, judges told generated pages from real ones every time.
These were the tells. Avoid all of them:

- **Half-empty pages.** A short table or a small grid in the top half of the
  page. Fill the body: the kit sizes tables and grids to the page, and a side
  panel carries the "so what".
- **Redundant chart titles** ("Price", "Revenue") under an action title. The
  axis title or unit line carries the measure.
- **Notes about the build**: "the file", "inputs", "data not provided". Name
  the business source.
- **A bold lead-in on every point** in every side panel, and a takeaway box
  on every page. Use a takeaway box only where the page has no side panel
  and the title cannot carry the whole point.
- **Dense per-unit plots** (one bar or dot for each of 30+ stores). Show the
  distribution in bands or the top and bottom 5, and put the full list in the
  appendix.
- **Broken bridges**: a waterfall with missing category labels, clipped
  value labels, or no subtotal. Keep each label short (the kit enforces it)
  and show a subtotal at every section boundary.

## What separates the best client pages (the MBB-client benchmark)

- The title is the synthesis ("…so fixing Express markdowns first is worth
  $19M"), not the fact ("Express shrink is 3.4%").
- One chart per idea, with the datum in the title highlighted and everything
  else muted.
- The source line and notes are present on every analytical page.
- The exec summary could be sent alone, and it would still make the case.
