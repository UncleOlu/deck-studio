# Quality Floor

Applies to both modes. Read it before you design any slide; run the pre-flight
checklist before you deliver. A deck with one banned item is not complete.
Nothing in the other references overrides this file (Precedence in `SKILL.md`).

Sources: `high-end-visual-design`, `impeccable/craft-floor`, and the gap audit
against designsystemchecklist.com (`docs/history/GAP-AUDIT-v1.3.md`). The register overrides
come from `research/corpus-findings.md`. Craft detail lives in `polish.md`.

## Banned defaults

Do not ship a deck that contains any of these:

**Typography**
- Inter, Roboto, Arial, Open Sans, or Helvetica as the headline font *reached
  for as a default*. These read as unstyled defaults. Exception: executing a
  named DNA from `design-dna.md` whose identity depends on such a face (e.g.
  Void Console's tight-tracked Inter) is a deliberate choice — HTML mode only;
  PPTX always uses that DNA's safe-font mapping. (PPTX mode: Arial permitted
  for body text when render fidelity requires a safe font — see pptx-mode.md.)
- Aptos, anywhere: without a metric-compatible stand-in, its line breaks cannot be
  checked before the client opens the file.
- More than two font families per deck.
- Headline and body at similar sizes. The title must be at least 2x the body size.

**Color and surface**
- Default Office themes and default chart palettes.
- Generic 1px solid gray borders as the only card treatment.
- Harsh dark drop shadows (high opacity, small blur). Use soft diffused shadows:
  large blur, low opacity, visible offset.
- Gradient text. Use weight or size for emphasis.
- More than ~5 colors. Each color must have a semantic role (see Required).
- A warm off-white ground nobody asked for (a DNA that chooses one is exempt).

**Layout**
- Symmetrical bootstrap-style 3-column grids with equal cards as the page
  structure. Vary card sizes or use a split layout.
- Bullet-wall slides: a title plus 5+ bullets and nothing else.
- Ornamental rules and stripes that carry no information: a rule under the
  title, a coloured band across the top or bottom, a strip down one edge of the
  slide or one side of a card. Separate with space or a surface change.
- Section numbers (01 / 02 / 03) unless the order itself carries information.
- Kicker/eyebrow labels above headings when the heading already states the point.
- Body text or lists set centred. They read ragged on both sides; align them left.

**Motion (HTML mode)**
- Linear or ease-in-out easing. Use a custom cubic-bezier or exponential ease-out,
  e.g. `cubic-bezier(0.32, 0.72, 0, 1)`.
- Instant state changes with no interpolation.
- The same entrance animation on every element. Author one clear moment.
- Animating `top`/`left`/`width`/`height`. Animate `transform` and `opacity`.

## Required

Every deck must have all of these:

1. **One idea per slide.** The slide title states the idea as a full assertion.
   The body proves it. If a slide has two ideas, split it.
2. **A palette of five roles, declared once**: background, foreground, a
   dominant colour that owns most of the coloured area, a support tone, and an
   accent. Slides reference the tokens; a raw hex typed twice is a defect.
3. **One type scale, declared once** (title, section header, body, caption,
   big number); no per-slide sizes. The kit's keynote scale: 40 / 22 / 15 / 11
   / 66 pt. Consulting and banking use the Register overrides table.
4. **Intentional type pairing.** One characterful display face for titles, one
   quiet complementary face for body. Pair them on purpose; state the pairing.
5. **One spacing unit and its multiples.** PPTX: the kit's grid is a 0.6 in
   margin and 0.4 in between blocks, deck-wide. HTML: steps of 8 px.
6. **Generous whitespace.** Leave deliberate empty space. Do not fill every
   region. More space above a heading than below it.
7. **Three elevation levels, declared once**, each paired with a surface
   colour: **flat** (no shadow; the background shift separates it), **raised**
   (cards: visible offset, large blur, low opacity), **floating** (at most one
   element per slide). On a dark ground, lift the surface colour instead of
   deepening the shadow. No fourth level. When a DNA guardrail forbids shadows,
   the guardrail wins: three surface/border levels and no shadow.
8. **Data-ink discipline on charts.** Every chart makes one point, stated in the
   slide title. Remove gridlines you do not need, legends for single series,
   and axis clutter. Label the data directly where possible. Use the deck
   palette, with the accent color only on the datum that carries the point.
9. **Contrast.** Body text ≥ 4.5:1 against its background; large text ≥ 3:1.
   Icons and text on colored surfaces must pass the same check.
10. **Something to look at on every content slide**: a chart, diagram, image,
    big number, or structured comparison. Title-plus-bullets alone fails.
11. **Executive copy rules** from `executive-writing.md`: takeaway first, ASD-STE100
    style, no clichés, no hyperbole. Run `scripts/copy-lint.py` on the output.
12. **A distinct look per deck.** List the palette, type pairing, and hero
    layout of `samples/` and this user's recent decks; change at least the
    palette and one hero layout. Never the same `design-dna.md` DNA two decks
    in a row, and never the sample formula (dark bookends + big-stat-left with
    three tinted cards + chart-left/text-right) as a package. Carry one motif
    (chart treatment, card geometry, or divider device) on every slide. A
    DNA's guardrails apply on top of this floor.
13. **Speaker notes on every content slide**: 2–4 sentences of talk track plus
    the source of each number on the slide. **A page number on every content
    slide**, in every register: blind judges marked down a keynote deck
    without them.
14. **One icon set.** One family, outline by default, filled only for the one
    active or completed state. Stroke 1.5px beside regular text, 2px beside
    semibold. One bounding box, sized on the spacing grid. Never two sources.

## Register overrides (exhaustive — every other item binds in every register)

| Item | keynote | consulting | banking |
|---|---|---|---|
| Headline font: Arial/Helvetica-class sans | banned as default | allowed (R9) | allowed (R9) |
| PPTX type scale (Required 3) | title 40pt, body 15pt (kit) | title 20–24pt (sentence titles), body 12–14pt, notes/source 8–9pt | title 18–22pt, body 10–12pt, notes 7–8pt |
| Bullet-wall ban; Required 10 | binds | a structured text page (bold lead-ins, ≤ 5 blocks) is allowed and counts as the visual (R10) | same as consulting |
| Section numbers (01/02/03) | banned | allowed in tracker and agenda dividers (R8) | allowed |
| Kicker/eyebrow above title | banned | tracker allowed (R8) | breadcrumb allowed |
| Action title on every content slide | yes, ≤ 25 words | yes, ≤ 20 words, ≤ 2 lines (R1–R2) | neutral label allowed, ≤ 12 words (R3) |
| Source line on chart/table slides | slide or notes | on the slide (R5) | on the slide (R5) |
| "Confidential" / "Preliminary draft" label | — | optional | expected on the cover |
| Required 12 (distinct look per deck) | binds | the register DNA is a house style: keep it, vary only the motif | same as consulting |

## Pre-flight checklist

Run this before you deliver. Render the deck (thumbnails, PDF pages, or
screenshots) and check the images, not the code.

- [ ] Every slide title is a full assertion (a finding, not a topic label).
      The cover is the one exemption: subject, audience, date.
- [ ] One idea per slide; supporting content proves the title.
- [ ] No banned item from the list above appears anywhere.
- [ ] Only the declared font pairing, palette (accent sparing and semantic),
      and spacing grid, on every slide.
- [ ] Nothing overflows, truncates, or collides. The evals caught this more
      than any other defect; in PPTX, look again after every edit.
- [ ] Elements aligned across slides: titles, margins, and repeated components
      sit at the same coordinates deck-wide.
- [ ] Charts: one point each, direct labels, palette colors, no default look.
- [ ] Copy passes executive-writing.md (short sentences, active voice, no
      clichés, numbers verified).
- [ ] Contrast passes on every text/background pair.
- [ ] Numbers: one precision per metric family, one unit style, numeric columns
      right-aligned and tabular (HTML: `font-variant-numeric: tabular-nums`).
- [ ] Icons: one family, one stroke weight, one bounding box deck-wide.
- [ ] HTML only: arrow keys plus Home/End step the deck, and every nav control
      shows a `:focus-visible` ring with a ≥44×44px hit area.
- [ ] Consulting/banking: `storyline-lint`, `trace-check`, `integrity-check`,
      and `layout-check --pdf` report 0 errors; the partner review has no
      open must-fix.
- [ ] Mode-specific validation passed (PPTX: `scripts/validate_pptx.py`;
      HTML: token validator + browser screenshot at 1280×720 and one small size).

If any item fails, fix it and re-render the affected slides. Do not report the
deck complete with a failing item.
