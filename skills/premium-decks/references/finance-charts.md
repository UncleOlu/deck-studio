# Finance charts — waterfall, football field, Marimekko, Harvey balls, 2×2, tornado, sensitivity, comps

Recipes for the `consulting` and `banking` registers. In PPTX, every chart
here is a **native, editable** object: a pptxgenjs chart, a table, or plain
shapes. Never use an image. The client will edit these numbers. Tokens `C`
(palette), `F` (fonts), and `T` (sizes) are the deck's constants from
`pptx-mode.md`. HTML versions follow the same geometry with SVG or CSS grid and
`var()` tokens (`html-finance.md`). Each recipe was built with pptxgenjs
3.12, validated with `scripts/validate_pptx.py`, and rendered in PowerPoint.

## Waterfall (bridge)

Build it as a stacked column chart. Series 1 is an **invisible base** (the bar
colour equals the background). Then add series for total, increase, and
decrease. Compute the base from the running level so the arithmetic holds;
`integrity-check.py` reads the chart and fails a bar that does not start where
the last one ended.

```js
let level = 0; const base = [], tot = [], up = [], down = [];
for (const [, v, kind] of steps) {            // steps: [label, value, "total"|"step"]
  if (kind === "total") { base.push(0); tot.push(v); up.push(0); down.push(0); level = v; }
  else if (v >= 0) { base.push(level); up.push(v); down.push(0); tot.push(0); level += v; }
  else { level += v; base.push(level); down.push(-v); up.push(0); tot.push(0); }
}
s.addChart(pres.charts.BAR, [{ name: "base", labels, values: base }, { name: "total", labels, values: tot },
  { name: "increase", labels, values: up }, { name: "decrease", labels, values: down }],
  { barDir: "col", barGrouping: "stacked", barGapWidthPct: 40, chartColors: [C.bg, C.brand, C.accent, C.muted],
    showLegend: false, valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" } });
```

- Label every step with its value in a text box above the bar, or in a data
  table under the axis. Data labels on the stacked series also label the
  zeros.
- The title names the largest step. Give that step, and only that step, the
  accent colour.
- Keep it to 8 steps or fewer. Group the tail into "Other".

## Football field (valuation summary)

Build it as a horizontal stacked bar: an invisible `low` series plus a
`range` series. Add the offer (or current price) as a dashed line shape.
Place the line with the plot-area layout, as below. Fix `valAxisMinVal` and
`valAxisMaxVal` so the maths is exact.

```js
const layout = { x: 0.33, y: 0.02, w: 0.64, h: 0.86 };   // plot area inside the chart box
s.addChart(pres.charts.BAR, [{ name: "low", labels, values: low }, { name: "range", labels, values: span }],
  { x, y, w, h, barDir: "bar", barGrouping: "stacked", chartColors: [C.bg, C.support], layout,
    valAxisMinVal: min, valAxisMaxVal: max, valAxisLabelFormatCode: "$0", showLegend: false });
const offerX = x + layout.x * w + (offer - min) / (max - min) * layout.w * w;
s.addShape(pres.shapes.LINE, { x: offerX, y: y + 0.05, w: 0, h: h * layout.h, line: { color: C.accent, width: 2, dashType: "dash" } });
```

- Name the method **and its key assumptions** in each row label: "Trading
  comps (9.0x–10.5x NTM EBITDA)".
- Pass the rows in reverse order: `barDir: "bar"` draws the first category at
  the bottom.
- The title states where the offer falls against the ranges.

## Marimekko (market map)

pptxgenjs has no variable-width chart, so draw native rectangles. The column
width is proportional to segment size, and the heights are the shares within
each column. Write "Name NN%" inside each cell, and "Segment · €x.xB" under
each column. Colour the player that matters in `C.brand`, and the others in
support and neutral tones. Use 3–6 columns. When a cell is too small for its
label, put the label beside the cell with a leader line.

## Harvey balls (options × criteria)

Draw an outline circle (`OVAL`, no fill) plus a filled `PIE` with
`angleRange: [270, 270 + 90 * q]` for q = 1–3 quarters. Full is a filled oval.
Empty is the outline alone. Tint the recommended option's row with the accent
at 10–15%. Print the scale key in the footer:
"○ none · ◔ low · ◑ medium · ◕ high · ● full". (Avoid "very": copy-lint flags it.)

## 2×2 prioritisation

Use a native `BUBBLE` chart with both axes fixed from 0 to the maximum. Draw
the quadrant labels as text boxes in the corners of the plot area, not as
chart titles. Give the chosen quadrant's bubbles the accent colour, as a
separate series. Label both axes with what they score, e.g. "Ease of
delivery (1–5)".

## Tornado (sensitivity ranking)

Use a horizontal clustered bar with `barOverlapPct: 100`: a downside series
(negative values) and an upside series. Sort by total spread, largest at the
top (so pass the rows smallest first). Set `catAxisLabelPos: "low"` so the
labels clear the bars. Set `dataLabelFormatCode: "$0.0;($0.0)"` for
parenthesised negatives.

## Sensitivity heat-table

Build a native `addTable`, with rows for one variable and columns for the
other. Fill each cell from a **two-step scale only**: above the offer
(accent at 10–15%) and below it (neutral tint). Outline the base-case cell
with a no-fill 2pt accent rectangle drawn over the cell. Do not use a cell
border: neighbouring cells overwrite shared borders, and the outline renders
with only two sides. Right-align the values. Put the variable names in
the top-left cell ("WACC \ TGR").

## Trading comps / precedents table

Build a native table with no vertical rules and a 1pt rule under the header.
Right-align every numeric column. Use one precision per column: `x.x` for
multiples, thousands separators for EV. Put a **median** (and optionally a
mean) row under a 1pt rule, then the subject company's row, tinted with the
accent. Show negative values in parentheses. The footer gives the source and
an "as of" date, and defines any non-GAAP term (EV, EBITDA adjustments).

## Rules for every finance chart

1. The unit line under the title states the units: "($ in millions, except
   per-share values)".
2. The source line names the data provider and its "as of" date, and the
   model or management case used.
3. The accent marks only the datum in the title. Everything else stays
   brand, support, or neutral.
4. No 3-D, no shadows on bars, no gradients, no default Office palette.
5. After the build, run `integrity-check.py`, which checks waterfall
   continuity, that shares sum to 100%, and that table totals add up.
