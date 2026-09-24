# Polish

Small craft rules that decide whether a deck reads as designed or as generated.
Read this after `quality-floor.md`; it adds detail, it does not replace the
floor. Where a rule here elaborates a Required item, it says which one and adds
only what the checklist cannot test by eye.

Sources: https://ui-skills.com (Playbook; `jakubkrehel/better-ui`;
`rams/rams`) and the Vercel Web Interface Guidelines that
`antfu/web-design-guidelines` fetches
(https://raw.githubusercontent.com/vercel-labs/web-interface-guidelines/main/command.md).

This file sits near the bottom of the precedence chain in `SKILL.md`: a DNA
guardrail that forbids shadows or prescribes hairline borders overrides the
shadow and border rules below.

## Both modes

**Optical alignment beats geometric alignment.** A number inside a circle, a
triangular play or chevron glyph, and an icon beside a label all sit wrong when
centred by measurement. Nudge them by eye. On slides this shows on step
markers, timeline dots, and icon-plus-label rows repeated down a column.

**Concentric radius: outer = inner + padding.** A chart card inside a section
panel needs the outer radius raised by the gap between them. Mismatched nested
radii are the most common reason a slide "feels off" with no nameable defect.

**Shadows carry depth, borders carry structure.** If a border exists only to
lift a card off the page, delete it and use the shadow recipe. Keep borders
that separate two things: table rules, a divider between a chart and its
source note, the edge of an inverted band.

**Group with space before you draw a line.** Try 1.5x the gap unit first. Add
the rule only when space alone leaves the grouping ambiguous. Most divider
lines on a slide are covering for spacing that was never decided.

**Elevation** — Required 7 sets the scale. The craft part it cannot check: pick
the level from what the element *is*, not from how much you want it noticed. A
chart card and a stat card at the same depth read as one system; the same two
at different depths read as an accident.

**Icons** — Required 14 sets the rule (one family, one stroke weight, outline
by default). The craft part it cannot check: an icon beside a label almost
always needs an optical nudge, and one recoloured SVG per state beats two
assets, because `currentColor` keeps hover and disabled states in the palette.

**Never let colour alone carry meaning.** A red or green delta needs a sign, an
arrow glyph, or the word. Slides get projected through bad colour profiles and
read by colour-blind executives.

**One accent per slide, not per deck section** (Required 2 rations the palette;
Required 8 puts the accent on the datum that carries the point). Secondary
emphasis stays neutral: weight, size, or a support tone. Two accents on one
slide leave the audience without a place to look first.

**Muted text still has to pass** (Required 9). Caption and label tones drawn
from a palette's "muted" slot usually fail 4.5:1 on a *tinted* ground even when
they pass on white. Darken the tone for that surface; do not accept the miss.

**Images take a 1px neutral outline at ~10% opacity** — pure black in a light
deck, pure white in a dark one. Never a near-black grey or a tinted neutral: a
tinted edge picks up the surface under it and reads as dirt on the photo.

**Sentence case on labels, axis titles, and chips.** All caps costs legibility
at projection distance and reads as chrome.

**Typographic finish.** `…` not three periods, and curly quotes. Ranges and
units are in `executive-writing.md` under Numbers; these two are not.

## HTML mode

**Why the focus ring is not optional** (`html-mode.md` sets the requirement):
a presenter drives the deck from the keyboard in a dark room, and a control
they cannot locate is a control they will click past.

**Name the properties you transition.** `transition: opacity 160ms …, transform
160ms …`, never `transition: all` — on a slide, `all` also animates the colour
change when a theme or a `.active` class flips, and the reveal smears. Set
`transform-origin` explicitly; for SVG, transform the `<g>` wrapper with
`transform-box: fill-box`.

**CSS transitions for state, keyframes for the one reveal.** Transitions can be
interrupted mid-flight; a presenter who arrows forward twice quickly must not
watch a queued animation finish.

**Entrances ease-out; exits shorter, with a small `translateY`.** Match the
enter and exit curves so a slide feels like one surface. Start scale at 0.95,
never 0 — scale-from-zero reads as a pop-up, not a reveal.

**Stagger the title slide only, ~100ms per chunk.** Every later slide gets one
authored reveal. Never replay an entrance when the presenter arrows back to a
slide already seen.

**`scale(0.96)` on press for nav buttons.** The only motion on a
high-frequency control; anything below 0.95 reads as a bounce.

**No glow on the primary control, no blurred backdrop.** Contrast and spacing
carry the emphasis; a full-screen backdrop blur costs frames on the projector's
machine, not yours.

**Explicit `width`/`height` on every `<img>`** — the companion to the
`aspect-ratio` rule in `html-mode.md`, and the one it does not cover.

**`color-scheme: dark` on `<html>`** for dark decks, and a
`<meta name="theme-color">` matching the slide ground, so scrollbars and native
controls do not flash light.

**One token per job for thin lines.** `--hairline` for structure, `--chart-grid`
for gridlines, `--data-edge` for a shape that carries a value. The third is the
one people miss: an empty track or an unstarted bar at hairline weight is
invisible on a projector, so it needs 3:1, not 0.14 alpha.
