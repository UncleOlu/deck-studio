# Finance charts and pitch pages (HTML mode)

HTML versions of the `finance-charts.md` recipes and the sell-side pages in
`banking-pitchbook.md`. The geometry, labelling, and accent rules are the same
as in PPTX; read those files for *what* to show. Here: CSS grid, `var()`
tokens only, and **numbers declared once as inline custom properties**
(`style="--from:36.8;--to:39.2"`). The CSS draws from them and
`integrity-check.py` reads them, so the drawing and the check cannot disagree.
The token validator allows custom properties inline.

## Waterfall (bridge)

The container sets the axis (`--min`, `--max`). Each bar declares where it
starts and ends; a total starts at 0. `integrity-check.py` fails a bar that
does not start where the previous one ended.

```css
.wf{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;column-gap:var(--space-2);
  height:clamp(220px,42vh,380px);border-bottom:1px solid var(--hairline);margin-bottom:2.4em}
.wf-bar{position:relative;font-variant-numeric:tabular-nums}
.wf-bar>i{position:absolute;inset-inline:14%;background:var(--color-support);border:1px solid var(--data-edge);
  bottom:calc((min(var(--from),var(--to)) - var(--min)) / (var(--max) - var(--min)) * 100%);
  height:calc(max(var(--to) - var(--from),var(--from) - var(--to)) / (var(--max) - var(--min)) * 100%)}
.wf-bar.is-total>i{background:var(--color-primary);border-color:transparent}
.wf-bar.is-point>i{background:var(--color-accent)}
.wf-bar>b{position:absolute;inset-inline:0;text-align:center;
  bottom:calc((max(var(--from),var(--to)) - var(--min)) / (var(--max) - var(--min)) * 100% + 4px)}
.wf-bar>span{position:absolute;inset-inline:0;top:100%;padding-top:var(--space-1);text-align:center;
  color:var(--color-muted)}
```

```html
<div class="wf" role="img" aria-label="EBITDA rises from $36.8M to $41.8M" style="--min:0;--max:45">
  <div class="wf-bar is-total" data-label="FY25" style="--from:0;--to:36.8"><i></i><b>$36.8M</b><span>FY25</span></div>
  <div class="wf-bar" data-label="Housekeeping" style="--from:36.8;--to:39.2"><i></i><b>+2.4</b><span>Housekeeping</span></div>
  <div class="wf-bar is-point" data-label="Energy" style="--from:39.2;--to:41.8"><i></i><b>+2.6</b><span>Energy</span></div>
  <div class="wf-bar is-total" data-label="At median" style="--from:0;--to:41.8"><i></i><b>$41.8M</b><span>At median</span></div>
</div>
```

- A decrease runs downward: `--from` above `--to`. Keep 8 bars or fewer.
- The accent (`is-point`) goes on the step the title names, and only there.

## Football field (valuation summary)

```css
.ff{--ff-label:26ch;position:relative;display:grid;grid-template-columns:var(--ff-label) 1fr;
  row-gap:var(--space-2);align-items:center;font-variant-numeric:tabular-nums}
.ff-track{position:relative;height:22px}
.ff-track>i{position:absolute;top:0;bottom:0;background:var(--color-support);border:1px solid var(--data-edge);
  left:calc((var(--lo) - var(--min)) / (var(--max) - var(--min)) * 100%);
  width:calc((var(--hi) - var(--lo)) / (var(--max) - var(--min)) * 100%)}
.ff::after{content:"";position:absolute;top:0;bottom:0;border-left:2px dashed var(--color-accent);
  left:calc(var(--ff-label) + (100% - var(--ff-label)) * (var(--offer) - var(--min)) / (var(--max) - var(--min)))}
```

```html
<div class="ff" role="img" aria-label="The $24.00 offer sits above four of five ranges"
     style="--min:14;--max:30;--offer:24">
  <span>Trading comps (9.0x–10.5x NTM EBITDA)</span><div class="ff-track" style="--lo:17.2;--hi:21.9"><i></i></div>
  <span>DCF (WACC 8.5–9.5%)</span><div class="ff-track" style="--lo:19.8;--hi:25.6"><i></i></div>
</div>
```

- Rows read top to bottom in the book's method order (HTML draws in source
  order, unlike `barDir: "bar"`). Print the low and high values at the bar
  ends and label the offer line once, at the top.

## Tornado

One row per driver, sorted by spread, largest first. Each half of the track is
a grid column; the base case is the line between them. `--dn` is the
downside (negative), `--up` the upside, `--span` the largest absolute value.

```css
.tor{display:grid;grid-template-columns:22ch 1fr 1fr;row-gap:var(--space-1);align-items:center;
  font-variant-numeric:tabular-nums}
.tor-dn,.tor-up{display:flex;height:20px}
.tor-dn{justify-content:flex-end;border-right:1px solid var(--color-fg)}
.tor-dn>i{width:calc(-1 * var(--dn) / var(--span) * 100%);background:var(--color-support);
  border:1px solid var(--data-edge)}
.tor-up>i{width:calc(var(--up) / var(--span) * 100%);background:var(--color-primary)}
```

```html
<div class="tor" style="--span:4.2">
  <span>WACC ±50 bp</span><div class="tor-dn" style="--dn:-4.2"><i></i></div><div class="tor-up" style="--up:3.9"><i></i></div>
</div>
```

## Sensitivity heat-table and comps table

Use real `<table>` markup (the QA scripts read it) with the dense-table
recipe in `html-components.md`, plus:

```css
td.is-above{background:color-mix(in srgb,var(--color-accent) 14%,var(--color-bg))}
td.is-base{outline:2px solid var(--color-accent);outline-offset:-2px}
tr.is-median td{border-top:1px solid var(--color-fg)}
tr.is-subject td{background:color-mix(in srgb,var(--color-accent) 12%,var(--color-bg))}
```

Two-step heat only (above / below the offer), right-aligned tabular numbers,
negatives in parentheses, and the variable pair in the corner cell
("WACC \ TGR"). `outline` draws all four sides, so HTML needs no overlay.

## Pitch pages

**Alternatives side by side.** One column per option, identical rows, so the
eye compares across:

```css
.opts{display:grid;grid-template-columns:repeat(var(--n),1fr);column-gap:var(--space-3)}
.opt>h3{padding-bottom:var(--space-1);border-bottom:2px solid var(--color-primary)}
.opt.is-recommended>h3{border-color:var(--color-accent)}
.opt dl{display:grid;grid-template-rows:subgrid;grid-row:span 3}
```

Rows: what it is, merits, considerations. Mark a recommended column only on
the recommendation page, after the analysis; before it, every column is equal.

**Buyer universe.** A `<table>` grouped by tier: a full-width group row
(`<tr class="tier"><th colspan="4">Tier 1 · strategics</th></tr>`), then one
row per buyer with capacity (market cap or fund size), rationale, and a
fit mark. Strategics and sponsors never share a tier. Code names are fine.

**Process timeline.** The gantt recipe in `html-components.md`, one row per
phase (preparation, first round, second round, signing), weeks across the
top, and the board's decision points as `is-point` rows.

**Recommendation and next steps.** A text page: the recommendation in one
sentence in the bank's voice, three reasons tied to earlier pages, then a
next-steps table (action, owner, date).
