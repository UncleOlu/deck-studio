# Mode A: PowerPoint (.pptx)

New decks come from a pptxgenjs generator script (or the kit in
`templates/`). Existing decks are restructured with `scripts/deck_edit.py` and
checked with the QA scripts listed at the end of this file.

## Premium layer (do this first)

Before you write any slide code, declare the design system as constants at the
top of the generator script. Every slide references these constants. No raw
values in slide code.

```js
// tokens — declare once, reference everywhere
const C = {                      // palette: max 5, semantic roles
  bg:      "FFFFFF",             // background
  fg:      "1A1D23",             // foreground text
  brand:   "0F3D5C",             // dominant (60-70% of colored area)
  support: "D8E4EC",             // support tone
  accent:  "E8843C",             // accent — sparing, semantic use only
};
const F = { display: "Cambria", body: "Calibri" };   // one pairing, safe-list
const T = { title: 40, header: 22, body: 15, caption: 11, stat: 66 }; // pt
const S = { margin: 0.6, gap: 0.4 };                 // inches — one grid
```

Rules layered on the base pptx workflow:

- **No default Office look.** Never leave the default theme, default chart
  palette, or default text styling in place. Every visible element gets a
  token value.
- **Fonts the client already has**, each with a metric-compatible LibreOffice
  stand-in, or line breaks move between the QA render and the client's screen.
  Display: Cambria or Century Schoolbook (Bookman Old Style for warmth). Body:
  Calibri or Arial. Never Arial titles; never Aptos (no stand-in to check).
- **Soft shadows only**, e.g. `{ type: "outer", color: "000000", opacity: 0.18,
  blur: 14, offset: 3, angle: 90 }`, returned fresh from a function per shape:
  pptxgenjs writes into the options object, so a shared one leaks settings.
- **Spacing grid:** place every element on the `S` grid. Same title y-position
  on every content slide. Same margins deck-wide.
- **Charts native and quiet:** use `addChart()`, set `chartColors` from `C`,
  turn off the legend for single series, remove category gridlines, mute axis
  label colors, and label values directly (`showValue: true`).

**Never hand-edit OOXML to create a deck.** Build new decks with pptxgenjs or
the kit. If you use python-pptx, stay within its public API: no `_element`, no
lxml edits of chart or slide XML, and no swapped-in embedded workbooks. Decks
built that way in evals passed schema validation, but PowerPoint refused to
open them without repair. `pptx2pdf.py` fails when PowerPoint has to repair a
file, so render with PowerPoint before delivery whenever it is available.

## pptxgenjs mechanics (break these and the file corrupts or misrenders)

These and the font rule are *mechanics*: no design choice or DNA guardrail
overrides them (Precedence in `SKILL.md`). Each holds for pptxgenjs 3.12.

**Setup**
- pptxgenjs 3.12 is vendored: `require("<skill dir>/templates/lib/vendor/node_modules/pptxgenjs")`,
  no `npm install`. Use one `new pptxgen()` per output file.
- Set `pres.layout` before the first slide (`LAYOUT_16x9` 10 × 5.625 in,
  `LAYOUT_WIDE` 13.3 × 7.5 in); off-canvas coordinates ship unclamped.

**Colour and effects**
- Colours are six hex digits with no leading `#` (`"0F3D5C"`); a `#` or an
  alpha pair produces a file PowerPoint repairs. See-through fills and images
  take `transparency` (0–100); shadows take `opacity` (0–1).
- Shadow `offset` is never negative (aim with `angle`; 270 is up). No gradient
  fills: use a gradient image. `rectRadius` works on `ROUNDED_RECTANGLE` only.

**Text**
- Tracking is `charSpacing`; `letterSpacing` does nothing.
- Bulleted lists use the `bullet` option on each run, never a typed `•`. Every
  run except the last needs `breakLine: true`. Gap paragraphs with
  `paraSpaceAfter`; `lineSpacing` changes the line pitch, not the gap.
- Text boxes carry an inner inset; `margin: 0` lines text up with shapes.
- Text centres vertically by default, so sibling boxes with different line
  counts misalign: give each `valign: "top"`.
- Speaker notes go through `slide.addNotes()`; a text box is not a note.

**Charts**
- Stacked bar or column charts accept data labels at `ctr`, `inEnd`, or
  `inBase` only; `outEnd` makes the file unreadable.
- A series on `secondaryValAxis` needs two entries in both `valAxes` and
  `catAxes`, or PowerPoint drops the chart on open.
- Horizontal bars (`barDir: "bar"`) draw the first category at the bottom:
  sort ascending so the largest bar sits on top.

**Images and icons**
- Icons go in as PNG: rasterise the SVG at ≥ 256 px (e.g. `sharp`) and pass
  it to `addImage` as a base64 data URI; raw SVG renders unevenly in Office.

## Client-editable decks (`consulting` and `banking` registers — required)

Consulting and banking deliverables get edited after you hand them over, so
build them the way the client's team will expect.

- **One slide master with real placeholders.** Put the tracker, title, and
  source line in the master as placeholders. Put the page number in the
  master's `slideNumber`. Content slides use `pres.addSlide({ masterName })`
  and `addText(..., { placeholder: "title" })`. A tracker that is a loose
  text box drifts; a placeholder cannot.

```js
pres.defineSlideMaster({ title: "CONTENT", background: { color: C.bg }, objects: [
  { placeholder: { options: { name: "tracker", type: "body", x: S.margin, y: 0.22, w, h: 0.26, fontSize: 9, color: C.muted, margin: 0 }, text: "" } },
  { placeholder: { options: { name: "title", type: "title", x: S.margin, y: 0.5, w, h: 0.95, fontFace: F.display, fontSize: T.title, margin: 0, valign: "top" }, text: "" } },
  { placeholder: { options: { name: "source", type: "body", x: S.margin, y: 6.95, w: w - 0.8, h: 0.3, fontSize: T.caption, color: C.muted, margin: 0, valign: "bottom" }, text: "" } },
], slideNumber: { x: 12.33, y: 6.95, w: 0.5, h: 0.3, fontSize: T.caption, color: C.muted, align: "right" } });
```

- **Native charts and tables only.** Use `addChart` and `addTable`, or
  shapes for Marimekko and Harvey balls. Never use a screenshot of a chart.
  Recipes are in `finance-charts.md`.
- **Reading order.** Add objects in the order a screen reader should read
  them: title, then the unit line, body, and source. pptxgenjs writes the
  z-order in call order.
- **Alt text** on every image and chart: set `altText` to one sentence that
  states what the visual shows, i.e. the title's claim.
- **Speaker notes carry the trace.** Cite the fact ids for each number on the
  slide, plus a `calc:` line for each derived figure (`storyline.md` §9).
- **QA adds** `storyline-lint.py`, `trace-check.py`, `integrity-check.py`,
  and `layout-check.py --pdf`. The order is in `SKILL.md`.

## Editing existing decks / templates

Do all structural work first with `scripts/deck_edit.py` (`list`, `dup N
--after M`, `delete N…`, `move N --to M`); it copies charts with their
workbooks and saving drops orphaned parts. Then edit slide content, either
with python-pptx or in `ppt/slides/slideN.xml` (parse with
`defusedxml.minidom` only; zip from inside the directory). Delete whole unused
template groups, not just their text. Validate with `scripts/validate_pptx.py`
after every step. All scripts run on Python ≥ 3.9.

## QA (required, in this order)

```bash
python3 scripts/validate_pptx.py out.pptx --native-charts  # file integrity; fix in the generator
python3 scripts/copy-lint.py out.pptx                 # cliché/intensifier/sentence-length lint
python3 scripts/pptx2pdf.py out.pptx                  # render: soffice → PowerPoint → Keynote
python3 scripts/deck_thumbnails.py out.pdf            # contact sheets out-grid-NN.jpg (poppler or pypdfium2)
```

Look at every slide image, starting with overflow and collisions (the defect
the evals hit most), then work through the pre-flight checklist in
`quality-floor.md`. Every fix means rebuilding the .pptx and rendering a new
PDF; images made from the old PDF show the old deck. Ship the PDF with the
.pptx.

Text dump: `unzip -p out.pptx 'ppt/slides/*.xml' | grep -o '<a:t>[^<]*'`.
