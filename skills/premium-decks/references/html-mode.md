# Mode B: HTML deck / frontend slides

One self-contained HTML file that presents as a deck: a `<section
class="slide">` per slide, keyboard navigation, a progress bar. Precedence in
`SKILL.md` separates mechanics here (never overridden) from token values (a
DNA guardrail may replace them).

**Markup that the QA scripts read** (a mechanic):
- the slide title goes in the section's first `<h1>`/`<h2>`;
- speaker notes go in `<aside class="notes">` (hidden with
  `aside.notes { display: none; }`) and carry the sources and fact ids;
- the consulting/banking section marker is an element with class
  `tracker`.

## Token architecture (primitive → semantic → component)

Declare all design decisions as CSS variables in three layers. Slides use only
`var()` — a raw hex, font name, or px size inside a slide is a defect.

```css
:root {
  /* primitive */
  --blue-900: #0F3D5C;  --orange-500: #E8843C;
  --gray-100: #F4F6F8;  --gray-900: #1A1D23;
  --font-display: "Fraunces", Georgia, serif;
  --font-body: "Instrument Sans", "Helvetica Neue", sans-serif;
  --size-title: clamp(2.2rem, 4.5vw, 3.4rem);
  --size-body: clamp(1rem, 1.4vw, 1.15rem);
  --size-stat: clamp(4rem, 9vw, 7rem);
  --space-1: 8px; --space-2: 16px; --space-3: 32px; --space-4: 64px;

  /* semantic */
  --color-bg: #FFFFFF;          --color-fg: var(--gray-900);
  --color-primary: var(--blue-900);
  --color-support: var(--gray-100);
  --color-accent: var(--orange-500);
  --color-muted: #6B7480;       /* captions and labels — check 4.5:1 per ground */

  /* component */
  --card-bg: var(--color-support);
  --card-radius: 16px;
  --card-shadow: 0 12px 40px rgba(15, 61, 92, 0.10);  /* soft, diffused */
  --hairline: rgba(26, 29, 35, 0.14);   /* structure: rules, dividers */
  --chart-grid: rgba(26, 29, 35, 0.08); /* chart gridlines only */
  --data-edge: rgba(26, 29, 35, 0.50);  /* shapes that carry a value — 3:1 min */
}
```

Fonts: 1–2 Google Fonts with real fallback stacks; a characterful display
face (no default Inter/Roboto/Arial/Open Sans/Helvetica unless a DNA's identity
needs it) and a quiet body face, pairing stated in a comment. Prefer adapting
a `design-dna.md` direction (palette, pairing, radii, motion) to inventing one.

## Layout patterns (adapted from ui-ux-pro-max, MIT — pick per slide goal)

| Goal | Layout | Notes |
|---|---|---|
| Opening | Title slide, centered | display face, one line, no clutter |
| Main conclusion | Big-number hero or split | stat in `--size-stat`, label below |
| Problem / situation | Two-column split (1fr 1fr, 48px gap) | text left, evidence right |
| Capabilities | Feature grid, 2–3 asymmetric cards | vary card sizes; never equal 3-up |
| KPIs | Metrics row (max 4) | number + label + comparison each |
| Progression | Timeline flow | only when order carries information |
| Options | Comparison table or columns | quantified trade-offs |
| Close | The ask | decision, owner, date |

Break the visual pattern once around 1/3 and 2/3 of the deck (e.g. one
full-bleed dark slide in a light deck) so attention resets. The CSV files in
`data/` hold the full decision system: `slide-strategies.csv` (deck
structures), `slide-layouts.csv` (25 layouts), `slide-copy.csv` (formulas),
`slide-charts.csv` (chart selection), `slide-typography.csv`,
`slide-color-logic.csv`. Search them:

```bash
python3 scripts/search-slides.py "board update" --context --position 2 --total 8
```

## Copy

`executive-writing.md` rules; `data/slide-copy.csv` informs order, never tone.

## Charts (Chart.js)

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"
        integrity="sha384-..." crossorigin="anonymous"></script>
```

Always pin the version and set Subresource Integrity. Compute the hash:
`curl -s <url> | openssl dgst -sha384 -binary | openssl base64 -A`.

- One chart per slide, one point per chart, point stated in the slide title.
- Colors from the token palette via `getComputedStyle`; accent color only on
  the datum that carries the point, support tone on the rest.
- `plugins.legend.display: false` for single series. Mute grid
  (`--chart-grid`), remove x-grid, label data directly where possible
  (datalabels or drawn text), `maintainAspectRatio: false` inside a sized
  container.
- Offline: inline the Chart.js source, or draw the chart as SVG — styling its
  marks with CSS classes, never `fill=`/`stroke=` attributes, which cannot
  resolve `var()`.

## Deck shell requirements

- Keyboard navigation (arrow keys **plus Home/End** to jump to the first and
  last slide), click/tap to advance, and a thin progress bar. The bar takes
  `--color-accent` — a styling default, so a DNA that rations that colour wins
  and the bar takes `--color-primary` instead.
- Every nav control carries a `:focus-visible` ring, an `aria-label`, and a hit
  area of at least 44×44px — pad the control, do not enlarge the glyph. Never
  `outline: none` without a replacement. Decorative SVG gets `aria-hidden`.
- Slides sized to the viewport (`100dvh`). Scale slide padding and gaps with
  viewport height (`clamp(28px, 6.5vh, 64px)`) and reserve a bottom band taller
  than the fixed nav controls — fixed padding collides with them on a short
  laptop screen. Verify at 1280×720 **and** 1024×576.
- Print stylesheet: `@media print` with one slide per page, backgrounds forced
  (`print-color-adjust: exact`) so the deck exports to PDF from the browser.
- Entrance motion: at most one authored reveal per slide, `transform`/`opacity`
  only, custom cubic-bezier (e.g. `cubic-bezier(0.32, 0.72, 0, 1)`), and a
  `prefers-reduced-motion` guard that disables it.

## Micro-rules (required in the shell CSS)

One declaration each, in the shell, not per slide (after the ui-skills.com
Playbook, MIT).

- `font-variant-numeric: tabular-nums` on every stat, numeric column, axis
  and data label, so digits keep their width and columns align.
- `text-wrap: balance` on titles (a 6–12-word assertion otherwise strands one
  word), `text-wrap: pretty` on body text.
- `aspect-ratio` on every chart, media, and image box, so nothing reflows in
  front of the room while fonts or Chart.js load.
- Body blocks capped at 60–75 characters — `ch` is the width of "0", so `68ch`
  renders ~90; `52ch` measured 68. Title line-height ~1.1, tracking tightened
  as display size grows.
- `min-width: 0` on flex children holding text, then `line-clamp` or a mask
  fade — a truncated legend beats an overflowing one.

`polish.md` carries the rest of the craft rules. `html-components.md` holds
five token-based recipes — process/stepper row, roadmap gantt bars, dense data
table, KPI row with attainment, milestone timeline — for the roadmap, process,
and dense-data slides; `html-finance.md` the finance charts and pitch pages.

## QA (required)

1. Step through every slide in a browser; screenshot at 1280×720 and a
   laptop size; check overflow, alignment, contrast, and charts.
3. Run the full pre-flight checklist in `quality-floor.md`.
4. Token compliance: `python3 scripts/slide-token-validator.py deck.html` —
   it also checks inline SVG, where `var()` cannot resolve.
