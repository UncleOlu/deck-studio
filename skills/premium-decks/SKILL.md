---
name: premium-decks
description: "Use when the user wants a deck, slides, a presentation, a pitch deck, a pitchbook, a board book, a consulting-style deck, a SteerCo update, or a premium presentation — for executives, clients, boards, or work — whether the output is a PowerPoint file or a web page, and especially when they supply a folder of analysis, spreadsheets, or notes to turn into a deck. Three registers: keynote (talks, all-hands, product), consulting (diagnostics, strategy, SteerCo; MBB/Big 4 grammar), banking (valuation board books, fairness-style books, sell-side pitches). Mode A builds .pptx; Mode B builds HTML decks. Trigger on any mention of \"deck\", \"slides\", \"presentation\", \".pptx\", \"pitch\", \"pitchbook\", \"board book\", or \"storyline\"."
---

# Premium Decks

Turn source files into editable executive decks with documented sources,
checked calculations, and an explicit review report. Every slide leads with
its conclusion, every number traces to a source and every derivation is
recomputed, and every element is a deliberate design choice. Tell the user
what the checks verified and what still needs their review; never present a
deck as finished on the automated gate alone.

## Routing

**Mode** (the file format):

| Signal | Mode |
|---|---|
| `.pptx`/`.potx`, "PowerPoint", a template file, a client or board deliverable | **A — PowerPoint** |
| "HTML deck", "web slides", browser presentation, frontend slide UI | **B — HTML** |
| Ambiguous | Ask: "PowerPoint file or web page?" Consulting and banking default to A |

**Register** (the grammar). Pick one in step 1 and say which in your first reply:

| Signal | Register | Read |
|---|---|---|
| Talk, all-hands, keynote, product launch, conference, investor story | **keynote** | `executive-writing.md` |
| Diagnostic, strategy, market entry, due diligence, SteerCo, transformation, "consulting-style", a board recommendation | **consulting** | `storyline.md`, `frameworks.md`, `consulting-grammar.md` |
| Valuation, fairness, special committee, board book, pitchbook, M&A, comps, precedents | **banking** | `storyline.md`, `banking-pitchbook.md`, `finance-charts.md` (HTML: `html-finance.md`) |

The register rules come from a study of 131 public consulting and banking decks
(`../../research/corpus-findings.md`). The quality floor's **Register
overrides** table lists everything that changes by register. Everything else
binds in every register.

## Workflow

Work in this order. Do not write slide code before step 3 is done.

0. **Ingest** (whenever the user supplies files or a folder):
   `python3 scripts/ingest.py <folder> --out brief`. It writes three files:
   - `brief/sources.md`: what each file holds;
   - `brief/facts.jsonl`: every figure, with its file and cell or line;
   - `brief/conflicts.md`: one metric with two values.

   Read all three. Resolve each conflict: prefer system extracts over notes,
   and filed figures over estimates. Record the choice in
   `brief/decisions.md`. Never build a slide from a file that is irrelevant to
   the question.
1. **Storyline.**
   - **Keynote:** follow `executive-writing.md`: audience, the one takeaway,
     and every title a full assertion.
   - **Consulting/banking:** follow `storyline.md`. Write the governing
     question, the issue tree, the synthesis ("so what"), and an answer-first
     structure. Then write the ghost deck, `brief/ghost-deck.md` (numbered
     titles, the framework for each slide, and the fact ids).
     - Red-team it with `partner-review.md` pass 1. When a subagent is
       available, give that pass to a fresh one.
     - **Checkpoint:** show the user the ghost deck and the resolved
       conflicts, and wait for approval. Skip the wait only if the user said
       to proceed without checkpoints.

   **Data contract:** every number on a slide cites a fact id in that slide's
   speaker notes (`[F0027]`), in a clause that names its metric. A derived
   figure gets a `calc:` line whose arithmetic the checker recomputes:
   `calc: $48M = 578 - 11.0% x 4820 [F0027, F0021, F0025]`. Write the
   arithmetic, never prose: inputs are cited facts, earlier results, or fact
   ids (`F0027`, `F0001:F0005`); `+ - x /`, `SUM`, `AVERAGE`, `MEDIAN`, `MIN`,
   `MAX`, `COUNT`, and `%` work (`calc: 9.4x = MEDIAN(10.0, 9.2, 9.4, 8.8, 9.9)`,
   not "middle of five values"). A figure you chose rather than found goes on
   an `assume:` line (`assume: $21.00, $23.00 (illustrative prices)`). If the
   user supplied no figures, put invented numbers in one `deck-data.json` with
   `"illustrative": true`. Label the deck illustrative in the slide-1 notes,
   and list the fields the user must replace.
2. **Design system.** Read `references/quality-floor.md`. Pick a DNA:
   - consulting: §8 Advisory Ink (`references/register-dna.md`);
   - banking: §9 Board Ledger (`references/register-dna.md`);
   - keynote: one of the seven product DNAs in `references/design-dna.md`, or
     a fresh system.

   Declare once: palette (≤ 5 colours with roles), type pairing and scale,
   spacing grid, elevation. There are no raw values in slide code.
3. **Layout plan.** Give each slide the archetype that answers its question.
   Search `python3 scripts/search-slides.py "<query>" -d archetype`, and see
   `data/slide-layouts.csv` for keynote.
4. **Build** per the mode section below.
5. **QA:** see the QA order below. Deliver the .pptx, the rendered PDF, and
   the `brief/` folder together. Do not deliver earlier. Data gaps and
   assumptions go in your hand-over message and the appendix, never in the
   main story (`storyline.md` §5).

## Mode A — PowerPoint (.pptx)

Read `references/pptx-mode.md` before writing generator code. It covers the
pptxgenjs footguns, safe fonts, and the client-editable rules: slide master
placeholders, native charts, alt text, and notes carrying the trace.

- **Consulting/banking: build with the kit. This is the default, not an
  option.** In Olu's calibration grades, both kit-built pages scored 4 of 5;
  eight hand-coded agent pages averaged 3.1 (`evals/judge/calibration.md`; a
  small sample). The kit also guarantees the master, native charts, and the
  builder refusals. Fill a deck JSON and run a builder:

```bash
node templates/build-consulting.js deck.json   # schema: templates/consulting-deck.schema.json
node templates/build-pitchbook.js deck.json    # schema: templates/pitchbook.schema.json
```

  Both builders share `templates/lib/deck-kit.js`. It provides:
  - the slide master (tracker, title, and source placeholders, plus a page
    number);
  - slide types: `cover`, `disclaimer`, `divider`, `exec-summary`, `text`,
    `chart`, `waterfall`, `football-field`, `table`, `sensitivity`,
    `options` (Harvey balls), `roadmap`, `marimekko`;
  - builder refusals: a deck without an early answer page, a data slide
    without a source, or a slide without notes.

  The worked examples are `templates/consulting-deck.sample.json` and
  `templates/pitchbook.sample.json`, generated by `samples/build_samples.py`
  from the inputs in `samples/source/`. Restyle through the JSON `theme` block.
  The kit needs only Node: pptxgenjs is vendored, so a missing npm package or
  no network is never a reason to fall back to python-pptx.
  When a slide needs a form the kit lacks, add a slide type to
  `lib/deck-kit.js` in the kit's own style (master, grammar zones, tokens),
  and then use it. Do not hand-code a whole deck beside the kit.
  - Chart choice: one message per chart. Prefer a sorted bar, a bridge, or a
    table with the datum highlighted. Avoid per-unit scatter and dot plots of
    100+ points on a client page; put them in the appendix (they graded 2 of 5).
- **Keynote accelerator:** `templates/build-deck.js` is an 8-slide decision
  deck driven by `templates/deck-data.sample.json`. Otherwise write a
  pptxgenjs script, with tokens as constants.
- **Edit an existing deck or template:**
  1. Unzip it, and do the structural work first.
  2. Edit the slide XML with `defusedxml`.
  3. Zip it again.
  4. Validate the result.
- Finance charts (waterfall, football field, Marimekko, Harvey balls, 2×2,
  tornado, sensitivity, comps): see `references/finance-charts.md`. All are
  native and editable.

## Mode B — HTML deck

Read `references/html-mode.md` before writing markup.

- One self-contained HTML file with three-layer CSS tokens; slides use
  `var()` only. Use `<section class="slide">` and `<aside class="notes">` for
  the trace, and `.tracker` for the section marker.
- Recipes: `references/html-components.md` (stepper, gantt, data table, KPI
  row, timeline); `references/html-finance.md` for consulting and banking
  (waterfall, football field, tornado, heat and comps tables, options, buyer
  universe; `integrity-check.py` reads its waterfall data). Other charts: the
  Chart.js recipe in `html-mode.md`. The decision
  data is in `data/*.csv` (`scripts/search-slides.py`).
- Keyboard navigation, progress bar, print stylesheet, reduced-motion guard.

## QA order (every deck)

One command runs the whole gate and prints one line per check:

```bash
python3 scripts/qa-deck.py out.pptx --register consulting --facts brief/facts.jsonl
```

Each check reports PASS, WARN, SKIP, or FAIL; fix and re-run until nothing
fails, and treat every SKIP as work still to do (`--strict` fails on it):
1. `validate_pptx.py`: package integrity.
2. `pptx2pdf.py`: render via LibreOffice, then PowerPoint, then Keynote.
3. `storyline-lint.py`: titles, exec summary position, sources, tracker.
4. `trace-check.py`: every number verified against a fact or a recomputed
   `calc:` line; "cited but not verified" numbers are warnings to resolve or
   to name in the hand-over note, and wrong arithmetic fails.
5. `integrity-check.py`: waterfalls, shares, totals, one value per metric.
6. `layout-check.py --pdf`: overflow, drift, collisions.
7. `copy-lint.py`: clichés, intensifiers, long sentences (advisory).
8. `deck_thumbnails.py`: a contact sheet for the visual review.

For Mode B (`.html`), the same command swaps the package check for
`slide-token-validator.py`. Take browser screenshots at two sizes.

The gate never says the deck is ready: the visual review is manual. Report
to the user what passed, what was skipped, and which numbers are cited but not
verified. Then run the pre-flight checklist in `references/quality-floor.md` **on the
rendered images**, and partner review pass 2. Give both to a fresh subagent
when one is available: after writing the generator you see what you expect,
not what rendered. The scripts cannot see a label drawn against the wrong
bar; a reviewer who looks at the image can.

If the Anthropic pptx skill is installed locally, its `office/validate.py`
adds XSD schema validation (Python ≥ 3.10). It is optional and never shipped
here: `validate_pptx.py` is the required integrity check.

## Quality floor and precedence

`references/quality-floor.md` is rank 1. It holds the banned defaults, the
Required items, the **Register overrides** table, and the pre-flight
checklist. `references/polish.md` carries craft detail that the checklist
cannot test by eye. When two references disagree, resolve them in this order
and say which rule you followed at the point of deviation:

1. `quality-floor.md`, including its Register overrides table.
2. Mode mechanics in `pptx-mode.md` and `html-mode.md`, wherever they govern
   whether the deck is valid, safe, editable, and presentable. This covers the
   pptxgenjs footguns, safe fonts, the slide master, native charts, a
   self-contained HTML file (one file, no build step; pinned CDN fonts and
   libraries allowed), print, keyboard, focus, and reduced motion. A design
   choice never overrides a mechanism.
3. Register grammar: `consulting-grammar.md` or `banking-pitchbook.md`.
4. The chosen DNA's guardrails (`design-dna.md` or `register-dna.md`).
5. Mode styling defaults: a suggested value, not a mechanism.
6. `polish.md`, then the recipes in `html-components.md`, `html-finance.md`,
   and `finance-charts.md`.

The prose rules in `executive-writing.md` and the method in `storyline.md`
sit outside this chain: copy rules and design rules do not compete.

## Dependencies

Run `python3 scripts/doctor.py` first on a new machine: it checks every row
below and prints the fix for anything missing.

| Dependency | Needed for | Check |
|---|---|---|
| Node ≥ 18 | Mode A create | `node --version`. pptxgenjs 3.12 ships vendored in `templates/lib/vendor/`: no install, no network |
| Python ≥ 3.9 + `python-pptx`, `lxml`, `defusedxml`, `Pillow`, `openpyxl`, `pypdf`, `pypdfium2` | ingest, QA scripts, thumbnails, collision check | `scripts/doctor.py`; with the user's OK, `scripts/doctor.py --install` installs the pinned set. The macOS system Python 3.9 works. |
| LibreOffice **or** PowerPoint **or** Keynote | render for visual QA | `scripts/pptx2pdf.py` tries each in order. On Windows and Linux, LibreOffice is the renderer; it is found on PATH or in its default install folder |

## Samples

`samples/` holds worked examples. Read them for structure; for keynote decks,
change the palette, DNA, and hero layout for the next deck (quality-floor rule
12):
- `alder-vale-margin-diagnostic.*`: consulting;
- `corvane-special-committee-book.*`: banking board book;
- `halden-strategic-alternatives.pptx`: banking strategic-alternatives book
  (kit `kind: "pitch"`, the sell-side skeleton in `banking-pitchbook.md`).

  All three are built through `ingest.py` from `samples/source/*/input` by
  `samples/build_samples.py`. The register DNAs are shared house styles, so
  rule 12's "change the palette" applies to keynote decks only.
- `northlane-pitch.*` and `ridgeline-card-cost.html`: keynote.

All companies and figures are fictional. No sample shares data with an eval
case.
