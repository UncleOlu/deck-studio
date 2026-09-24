# Slide components (HTML mode)

Five recipes for slide shapes the layout tables do not cover: process, roadmap,
dense table, KPI attainment, milestone timeline. Plain CSS and HTML only — no
Tailwind, no React. Every value comes from the three-layer tokens in
`html-mode.md`; a raw hex or px in a slide is still a defect.

Two tokens beyond the standard set: `--hairline` for structure (rules, dividers)
and **`--data-edge` for the outline of any shape that carries a value** — an
empty track, an unstarted bar, a future step dot. A pale fill on a pale ground
vanishes through a projector, so `--data-edge` must clear 3:1, not 0.14 alpha.
Pattern ideas from reui.io (MIT: Stepper, Gantt, Timeline, Table); the meter
layout idea from coss.com/ui. The CSS here is our own; no code was copied.

## Process / stepper row

```css
.steps{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;align-items:start}
.step{display:grid;justify-items:center;gap:var(--space-1);position:relative;
  padding-inline:var(--space-2);text-align:center}
.step::before{content:"";position:absolute;top:15px;left:-50%;right:50%;height:2px;
  background:var(--hairline)}
.step:first-child::before{display:none}
/* a connector is complete when the step BEFORE it is */
.step.is-done::before,.step.is-now::before{background:var(--color-primary)}
.step-dot{width:32px;height:32px;border-radius:50%;display:grid;place-items:center;
  background:var(--color-support);border:1px solid var(--data-edge);
  font-variant-numeric:tabular-nums;position:relative}
.step.is-done .step-dot{background:var(--color-primary);color:var(--color-bg);border-color:transparent}
.step.is-now  .step-dot{background:var(--color-accent); color:var(--color-fg)}  /* keeps
  --data-edge: a pale accent on a pale ground is invisible on a projector */
```

```html
<div class="steps">
  <div class="step is-done"><span class="step-dot">1</span><b>Scope</b>Signed 12 Feb</div>
  <div class="step is-now"><span class="step-dot">2</span><b>Pilot</b>Two sites live</div>
</div>
```

- Four steps maximum on one row; past five, use the timeline recipe.
- The accent marks the current step only; steps ahead stay support-toned.
- Each step carries one line of evidence, and every count gets a reference
  point ("41 of 60"), never a bare number.

## Roadmap gantt bars

```css
.gantt{display:grid;grid-template-columns:22ch repeat(6,1fr) 6ch;row-gap:var(--space-3);
  align-items:center;font-variant-numeric:tabular-nums}
.gantt-head{grid-column:2/8;display:grid;grid-template-columns:subgrid;color:var(--color-muted);
  border-bottom:1px solid var(--hairline);padding-bottom:var(--space-1)}
.gantt-head span{border-left:1px solid var(--hairline);padding-left:6px}  /* period ticks */
.gantt-row{grid-column:1/-1;display:grid;grid-template-columns:subgrid}
.gantt-bar{height:20px;border-radius:10px;background:var(--color-support);
  border:1px solid var(--data-edge);position:relative;overflow:hidden}
.gantt-bar>i{position:absolute;inset:0 auto 0 0;display:block;background:var(--color-primary)}
.gantt-row.is-point .gantt-bar>i{background:var(--color-accent)}
.gantt-pct{grid-column:8/9;text-align:right;color:var(--color-muted)}
```

```html
<div class="gantt">
  <div class="gantt-head"><span>Q1</span><span>Q2</span><!-- … --></div>
  <div class="gantt-row is-point"><span>Billing migration</span>
    <div class="gantt-bar" style="grid-column:3/6"><i style="width:60%"></i></div>
    <span class="gantt-pct">60%</span></div>
</div>
```

- Bar start/end come from `grid-column`, the inner `<i>` width is percent
  complete. Both are data — put them in `deck-data.json`, not the markup.
- Six rows maximum; a roadmap that needs study is a table.
- The fill encodes a quantity, so print it: `.gantt-pct` labels every row, and
  the header ticks let a reader find a bar's start and end.

## Dense data table

```css
.dtable{width:100%;border-collapse:collapse;font-variant-numeric:tabular-nums}
.dtable th,.dtable td{padding:var(--space-1) var(--space-2);text-align:left;
  border-bottom:1px solid var(--hairline)}
/* outer cells lose their padding so the table sits on the slide margin */
.dtable th:first-child,.dtable td:first-child{padding-left:0;font-weight:600}
.dtable th:last-child,.dtable td:last-child{padding-right:var(--space-1)}
.dtable th{font-weight:500;color:var(--color-muted)}
.dtable .num{text-align:right}
.dtable td.is-point{background:var(--color-accent);font-weight:600}  /* tint the CELL:
  a padded span would break the column's right alignment or bleed past the margin */
.dtable tfoot td{border-bottom:none;border-top:2px solid var(--color-fg);font-weight:600}
```

```html
<table class="dtable"><thead><tr><th>Lane</th><th class="num">Cost / unit</th></tr></thead>
  <tbody><tr><td>Midwest</td><td class="num is-point">$4.20</td></tr></tbody>
  <tfoot><tr><td>Total</td><td class="num">$18.60</td></tr></tfoot></table>
```

- Horizontal hairlines only: no vertical rules, zebra striping, or cell borders.
- Every numeric cell takes `.num` and `tabular-nums`, one precision per column.
  Eight rows and four columns maximum on a slide; beyond that, chart it.

## KPI row with attainment

```css
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:var(--space-3)}
.kpi{display:grid;gap:var(--space-1)}
.kpi-top{display:flex;justify-content:space-between;align-items:baseline;color:var(--color-muted)}
.kpi-val{font-size:var(--size-stat);line-height:.95;font-variant-numeric:tabular-nums}
.kpi-track{height:6px;border-radius:3px;background:var(--color-support);
  border:1px solid var(--data-edge);overflow:hidden}   /* 3:1, not a hairline */
.kpi-fill{height:100%;background:var(--color-primary)}
.kpi.is-point .kpi-fill{background:var(--color-accent)}
```

```html
<div class="kpi is-point"><div class="kpi-top"><span>On-time delivery</span><span>94%</span></div>
  <div class="kpi-val">91.4%</div>
  <div class="kpi-track"><div class="kpi-fill" style="width:97%"></div></div>
  <small>Target 94%. Q3 actual, ops ledger, 30 Sep.</small></div>
```

- The track is attainment against target, not decoration. Put the target in
  `.kpi-top` on the right, so the reference point sits beside the value.
- Four metrics maximum. One carries `.is-point` — the slide's title in numbers.

## Milestone timeline

```css
.tl{display:grid;grid-template-columns:max-content 12px 1fr;column-gap:var(--space-2)}
.tl-item{display:grid;grid-template-columns:subgrid;grid-column:1/-1}
.tl-when{text-align:right;color:var(--color-muted);font-variant-numeric:tabular-nums}
.tl-rail{justify-self:center;width:1px;background:var(--hairline);position:relative}
.tl-rail::before{content:"";position:absolute;top:4px;left:50%;translate:-50% 0;width:9px;
  height:9px;border-radius:50%;background:var(--color-bg);box-shadow:0 0 0 2px var(--data-edge)}
.tl-item.is-done .tl-rail::before{box-shadow:0 0 0 2px var(--color-primary)}
.tl-item.is-point .tl-rail::before{background:var(--color-accent);
  box-shadow:0 0 0 2px var(--color-accent)}
.tl-body{padding-bottom:var(--space-3)}
```

```html
<div class="tl"><div class="tl-item is-done"><span class="tl-when">Feb 2026</span>
  <span class="tl-rail"></span>
  <div class="tl-body"><b>Pilot closed</b><br>Two sites, 11% unit-cost fall.</div></div></div>
```

- Dates sit in a right-aligned gutter so the rail stays straight. Use this only
  when the order carries information; a list of dates is not a timeline.
- Filled dot for done, hollow for planned, accent for the one under decision.
