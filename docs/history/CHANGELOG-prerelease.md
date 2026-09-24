# Pre-release changelog

Internal builds before the first public release, 1.0.0. Their version numbers
(1.x–2.0.x) were never published; eval reports and notes still use them as labels.
Each entry keeps what was added, what was rejected and why.

## 2.0.2 — 2026-09-23

### Fixed

- `search-slides.py --context`: `should_break_pattern` now fires only when the
  current slide's emotion contrasts with the previous one (frustration → hope,
  fear → relief, …). Before, any frustration, hope, or fear on the previous
  slide triggered a break, so the contrast table was never used.

### Changed

- The repository passes `mypy --strict`; mypy resolves the scripts' own
  imports through `[tool.mypy] mypy_path`. No behaviour change.

## 2.0.1 — 2026-09-23

Security fixes from the new Security & Quality Gate (Bandit and Semgrep now
pass). No change to deck output.

### Changed

- `pptx2pdf.convert()` and `deck_thumbnails.make_grids()` are importable;
  `validate_pptx.py --render` and the judge's `prepare_pairs.py` call them in
  process instead of launching a Python subprocess.
- `pptx2pdf.py` also looks for LibreOffice in the usual Linux install folders.
- `tools/corpus/edgar_fetch.py` uses `requests` with an HTTPS + sec.gov
  allowlist that is re-checked on every redirect (dev-only dependency).
- `evals/harvest.py` opens and deletes only its own `e-*` run folders inside a
  sticky temp folder, never through a symlink, and unseals them read-only.
- GitHub Actions are pinned to commit hashes; Dependabot keeps them current
  with a 7-day cooldown.
- Security workflow: pre-commit hooks, CI scanning (gitleaks, Semgrep, Bandit,
  pip-audit, ruff/mypy/pytest), and a secrets baseline.

### Known gaps

- The gate's `mypy --strict` job still fails on existing code; typing it is a
  separate task.

## 2.0.0 — 2026-09-23

First public-ready release: MIT licence, no proprietary material in the tree,
portable install, and the deferred 1.4.x and Milestone 2 work. The planned
1.4.1 and 1.5.0 releases were folded in here because the work touched the same
files; the sections below keep the three groups apart.

### Fixes planned for 1.4.1

- `storyline-lint.py`: a gap page titled "Open items" or "to be confirmed" is
  flagged when its body says data is missing ("not yet received", "awaiting",
  "TBC"); a SteerCo decision list under the same title still passes.
- `storyline-lint.py` and the kit: any "<noun> file / spreadsheet / workbook"
  as a source ("budget tracker file") is flagged; "master file" is exempt.
- `integrity-check.py`: inline "(1)"–"(9)" note markers are checked for order
  and a matching note line on slides that carry numbered notes (PPTX and
  HTML); labels like "Phase (2)" elsewhere and values like "(12)" are not.
- Trigger evals: six cases (`--tag trigger`), 18/18 runs pass
  (`evals/reports/trigger-v2.0.md`).
- Every reference file is 150 lines or fewer.

### Milestone 2: banking depth and HTML parity

- **Pitch-book study:** 8 banker discussion books from 7 banks (SEC EX-99.(c)),
  coded in `research/pitchbook-findings.md`. The sell-side recipe in
  `banking-pitchbook.md` now follows them: neutral titles, key considerations
  up front, valuation, alternatives side by side, a tiered buyer universe, a
  process timeline, then the recommendation and next steps.
- **HTML finance recipes** (`references/html-finance.md`): waterfall, football
  field, tornado, heat and comps tables, options, and buyer universe. Numbers
  are inline custom properties, and `integrity-check.py` now checks HTML
  waterfalls.
- **New sample:** `halden-strategic-alternatives` (banking, kind `pitch`), built
  through the ingest path; trace, integrity, layout, storyline, and copy
  checks pass.
- **Device mix:** the kit refuses a deck that uses side panels, takeaway
  callouts, or tinted table rows (consulting) on more than about a third of
  content slides. Blind judges told generated slides from real ones 40/40,
  citing repeated templates (side panels restating the title, tinted rows,
  computed sentence titles); the corpus uses bold lead-ins on 20% and
  highlight boxes on 22%. The cap addresses the device part only and has not
  been re-judged.

### Milestone 3: public release

- Anthropic pptx-skill scripts removed; they are not distributed. New own tools: `deck_edit.py` (list,
  duplicate, delete, move slides; charts copied with their workbooks) and
  `doctor.py` (dependency check with fixes).
- Rewritten in new wording: the pptxgenjs mechanics, font, and QA passages in
  `pptx-mode.md`; the Anthropic-derived items in `quality-floor.md`; all of
  `design-dna.md`.
- `LICENSE` (MIT), `NOTICE`, `licenses/`, a corrected `PROVENANCE.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, `.claude-plugin/marketplace.json`, a
  public README with a before/after gallery, and GitHub Actions (lint and
  tests on Python 3.9 and 3.12, sample rebuild and QA, manual smoke eval).
- Personal paths removed; raw eval output (absolute paths, transcripts) is no
  longer tracked; plans and audits moved to `docs/history/`.
- `pptx2pdf.py` finds LibreOffice in its default install folder on macOS and
  Windows; `requirements.txt` pins tested versions.

### Rejected

- **Answer-first storylines for pitch books:** 0 of 8 banker books put the
  answer first, so the recipe no longer borrows the consulting order.
- **"Why us" and credentials as standard front matter:** 1 of 8; kept only for
  books that compete for a mandate.
- **Publishing the development history:** the public repository starts from a
  fresh history that never contained the removed material.

### Known gaps

- Only one of the 8 pitch books competes for a mandate, so "why us" pages rest
  on thin evidence.
- The Halden sample's PDF render could not be produced on the release machine
  (PowerPoint and Keynote automation failed); CI renders it with LibreOffice.

## 1.4.0 — 2026-09-23

Adds the consulting and banking registers, a folder-to-deck pipeline with
traced numbers, and a QA gate that can fail. The rules come from a study of
131 public decks: 95 coded, 28 held out for the blind test, and 8 collected
but not coded (`research/corpus-findings.md`).

### Added

- **Registers:** `keynote`, `consulting`, `banking`, selected at step 1. Density
  and typography differences enter only through the countable Register
  overrides table in `quality-floor.md`; every other floor item still binds.
- **Step 0, Ingest** (`scripts/ingest.py`): reads xlsx (values and formulas),
  csv, docx, pdf, pptx, md, and txt into `brief/facts.jsonl`, with a locator,
  unit, and scale for every number. Conflicting values for the same metric are
  flagged before any storyline work. Paths are canonicalised, symlink escapes
  refused, file count and size capped, and Office XML parsed with defusedxml.
- **Storyline engine** (`references/storyline.md`, `frameworks.md`,
  `partner-review.md`): governing question, issue tree, synthesis ladder,
  answer-first structure, a ghost deck the user approves before any build, and
  a partner red-team pass.
- **Page grammar** for client decks (`consulting-grammar.md`) and board books
  and pitches (`banking-pitchbook.md`), plus native finance recipes
  (`finance-charts.md`).
- **Deck kit** (`templates/lib/deck-kit.js`, `build-consulting.js`,
  `build-pitchbook.js`): a slide master with tracker, title, and source
  placeholders; native charts and tables; waterfall, football field, comps,
  sensitivity, Harvey balls, roadmap, and Marimekko. It refuses a deck JSON
  with a data slide that has no source, a slide with no notes, an over-long
  waterfall, or slide text about the builder's inputs. pptxgenjs 3.12.0 and
  jszip 3.10.2 are vendored (MIT), so it runs offline.
- **QA scripts:** `storyline-lint.py`, `trace-check.py`, `integrity-check.py`,
  `layout-check.py`, `validate_pptx.py` (clean-room), `deck_thumbnails.py`,
  and the `qa-deck.py` runner. `pptx2pdf.py` now reports a deck that PowerPoint
  had to repair (exit 3).
- **Samples** built through the ingest path from new fictional inputs: Alder &
  Vale Hotels (consulting diagnostic) and Corvane Instruments (special
  committee book).
- **Research:** corpus sources, codebook v3, coder agreement (κ 0.91 archetype,
  0.96 chart type, 1.00 assertion titles), findings, and a rule ledger R1–R16.
- **Evals:** 7 fictional cases with planted conflicts and noise
  (`evals/cases/`), `claude plugin eval` graders, an objective scorer, blind
  A/B rubric judging calibrated on Olu's grades of 10 slides, and a
  generated-versus-real discrimination test.

### What each source contributed

- **SEC EDGAR EX-99(c) board books** (65 decks, 12 advisors): the banking
  register — neutral titles, unit lines, numbered notes, confidentiality
  labels, and the fixed analysis sequence.
- **Public-sector client deliverables** (26) and **consulting client decks**
  (19): the consulting register — action titles ≤ 20 words, answer-first
  exec summary, trackers, source lines, structured dense pages.
- **Firm-published decks** (21): contrast only; marketing decks do not set
  client-page rules.
- **Slideworks, Analyst Academy, 10X EBITDA:** free public samples, coded
  with the consulting set.
- **SlideScience** (blocked, HTTP 403), **Slidebook.io and Alexander Jarvis**
  (files gated): notes only, no coded decks.

### Rejected

- R13 "so-what box on every slide": the action title carries the so-what.
- R14 4:3 page size: kept 16:9; 4:3 on request.
- R15 firm-specific palettes: the register DNAs use a generic navy/ink system.
- R7 unit line for consulting: units are labelled in the chart.

### Evaluation (honest result)

- **Objective**, v1.3.3 → v1.4.2 on the same 7 cases, scored with the
  release's scripts (`evals/reports/objective-*.md`):
  - numbers traced to a source: 0 of 873 → 1,010 of 1,010 (market-entry's
    cost assumptions trace to its illustrative data file, per the data
    contract);
  - layout errors: 7 → 0; storyline errors 14 → 0; integrity errors 1 → 0;
  - eval graders: 1.00 on all 7 cases. v1.3.3: 1.00 on 6 cases and 0.67 on
    grocer. Those baseline figures come from `evals/reports/rerun/`: the
    first baseline run (`baseline-v1.3.3.json`, overall 0.52) lost 4 cases to
    an account session limit before any deck was built, and those 4 were
    rerun;
  - every v1.4.2 deck opened in PowerPoint without repair; the v1.3.3
    sell-side deck needed repair (`evals/reports/iter2/prepare_pairs.log`).
- **Plan pass bar: NOT met on any of its three conditions.**
- **Blind rubric** (7 cases, 1–5): a tie, 4.02 against 4.02, so "beats
  v1.3.3 on every consulting/banking dimension" is not met. v1.4.2 is better
  on page grammar (4.00 vs 3.57) and data integrity (4.57 vs 4.29), and worse
  on visual quality (3.43 vs 3.86), synthesis (4.00 vs 4.14), and decision
  readiness (3.86 vs 4.00). Judges preferred v1.3.3 in 4 cases and v1.4.2 in
  3; take-private and sell-side went to v1.3.3. Keynote did not hold steady
  case by case: all-hands rose (3.57 → 3.86) and conference fell (4.14 →
  3.86); the keynote mean is unchanged at 3.86.
- **Discrimination:** each of 3 judges told generated slides from real ones
  40 of 40 times (120 of 120). The plan's bar (≤ 65%) is not met. The tells are now the kit's
  uniform look: tinted highlight rows, bold lead-in side panels, and the
  italic unit subtitle. This is the first target for 1.4.1.
- One iteration ran between the first judging and this release: data-gap
  pages and talk about the inputs now fail `storyline-lint`, tables and grids
  fill the page, banking titles state the factual finding, and the kit was
  vendored after eval agents were found to lack pptxgenjs (0 of 7 decks had
  used it).

### Fixed

- The skill's own scripts run on the stock macOS Python 3.9
  (`requires-python >= 3.9`). The optional Anthropic helpers
  (`office/validate.py`, `add_slide.py`, `clean.py`, `thumbnail.py`) still
  need 3.10; the required QA now uses `validate_pptx.py`.
- `pptx2pdf.py` passes file paths to AppleScript as arguments, so a quote in a
  path can no longer inject AppleScript.
- `ingest.py` caps each Office XML part at 64 MB decompressed (zip-bomb
  guard) and each file at 256 MB, and a malformed PDF, xlsx, or docx lands in
  "Not read" instead of
  stopping the run.
- `storyline-lint.py`: no false positives on "the data room" or SteerCo
  titles with "pending"; a unit line may end with a note marker "(1)"; source
  lines such as "precedents file" are caught.
- `trace-check.py` skips section-strip labels ("1 Baseline · 2 Labour") but
  still checks data lines in the same shape ("Pilot Stores 240 · Control
  Stores 238").
- The Corvane sample names business sources, and its note markers run in
  reading order.
- `qa-deck.py` reports the renderer that produced the PDF, not an earlier
  renderer's stderr.

### Deviations from the plan

- **Trigger evals were not built**: no non-deck case and no
  register-selection grader. Planned for 1.4.1.
- **Reference size**: `quality-floor.md` (161 lines), `html-mode.md` (159),
  and `design-dna.md` (179) exceed the ~150-line guide.
- **Context load per register** (measured, characters / 4, PPTX mode):
  keynote ~11.2k tokens, consulting ~12.8k (1.15×), banking ~13.4k (1.19×).
  Within the 1.5× limit.
- `integrity-check.py` checks footnote order from superscript markers only;
  the kit writes inline "(n)" markers, which it does not check yet.

### Known gaps

- No public banker pitch books were available; the sell-side recipe combines
  board-book grammar with the consulting storyline.
- The Anthropic pptx helper scripts still ship in this private build; they
  are replaced before any public release (Milestone 3).

## 1.3.3 — 2026-08-26

Fixes the two HIGH findings from the second chief-of-staff audit, plus the
regressions it traced to them.

### Fixed

- **`scripts/slide-token-validator.py` documented a check it never
  implemented.** The docstring promised that an inline `style=` may only carry
  layout data, but the code tested for hex, colour functions, and the literal
  string `font-family` only — so a literal `font-size` in a style attribute
  passed. `samples/northlane-pitch.html:152` carried exactly that
  (`style="font-size: clamp(2.6rem, 6vw, 4.2rem)"`, an invented per-slide size)
  and the validator called the file clean. The inline branch now flags any
  declaration whose property is not layout data and whose value is not a
  `var()`; the size moved into `:root` as `--size-cover`.
- **Three further validator defects found in the same pass:**
  - A CSS comment mentioning `:root` made the block matcher swallow the *next*
    real rule, silently skipping every check in it. Comments are now stripped
    first, and the matcher is anchored.
  - A hash selector made only of hex letters (`#faded`, `#beef`) was reported
    as a raw hex colour. Scanning is now scoped to declarations inside rule
    bodies, so selectors are never read as values.
  - SMIL's non-paint `fill="freeze"` / `fill="remove"` were flagged as colour
    defects. Both are now allowed.
- **Named CSS colours are now caught** (`color: white`, `border: 1px solid
  rebeccapurple`). They were a hard-coded value the tool never looked for.
- **`references/design-dna.md`, Meadow Ledger: the operative clause was not in
  the file.** 1.3.1 wrote "one datum per slide" and relied on a qualifier that
  existed only in this changelog, the memory file, and a CSS comment — so the
  plugin's own sample complied under a reading a reader of `design-dna.md`
  could not reach. Rather than write an exception that licenses the sample, the
  rule is now countable: **at most one lime mark per slide**, and
  `samples/ridgeline-card-cost.html` slide 3 drops to one (the current-step
  dot stays lime; the KPI fill becomes forest). The 1.3.1 entry above is
  corrected to quote the file.
- The current-step dot kept `border-color: transparent`, discarding its
  `--data-edge` — lime on white is 1.5:1, so the one mark the guardrail is
  about was the one that vanished on a projector. Fixed in the sample and in
  the `html-components.md` stepper recipe.
- **`references/polish.md`** restated Required 7 almost verbatim while claiming
  it never repeats a Required item. The elevation paragraph now names Required
  7 and adds only what the checklist cannot test; "One accent per slide" and
  "Muted text still has to pass" now name Required 2/8 and Required 9.
- **Slide 4 of the sample alternated "ceiling" and "target"** for the same
  0.94% figure (ASD-STE100 rule 5), described a per-lane ceiling while
  computing a gap for the blended row, and said "cross-border alone does not"
  clear it — which reads as *the only* breaching lane when domestic credit is
  also above. Copy rewritten: one term, both breaching lanes named, and the
  caption explains what the All-lanes row is.

### Clarified (gaps the audit surfaced in the 1.3.2 precedence chain)

- **"Self-contained" is now defined** in `SKILL.md`: one HTML file, no build
  step, no local asset dependencies — pinned CDN fonts and libraries expected.
  It was ranked non-overridable while `html-mode.md` instructs loading Google
  Fonts, so both samples read as breaching a rank-2 mechanic.
- **The mechanics list is explicitly not closed**, and now names the
  `prefers-reduced-motion` guard and `aspect-ratio`. Both previously fell
  through to rank 4, where a styling guardrail would have outranked them —
  wrong for a reduced-motion guard.
- **`executive-writing.md`'s exclusion from the chain is narrowed** to its
  prose sections. Its Numbers section carries typographic rules that also live
  in `quality-floor.md` and `html-mode.md`; those enter at rank 1.

## 1.3.2 — 2026-08-26

### Fixed

- **Precedence gap.** `polish.md` defined a three-file chain (quality-floor →
  DNA guardrails → polish) that left `html-mode.md` and `pptx-mode.md` outside
  it entirely, so a mode reference meeting a DNA guardrail had no rule. The
  live case: html-mode.md requires the progress bar in `--color-accent`, Meadow
  Ledger rations lime to one plane, and nothing said which won.

  The canonical chain now lives in `SKILL.md` (the file that routes between
  references; `polish.md` sat near the bottom of the chain it was defining) and
  **splits the mode references by rule type**, which a flat ordering could not:

  1. `quality-floor.md` — nothing overrides it.
  2. **Mode mechanics** — the pptxgenjs footguns, the safe-font mapping, a
     self-contained HTML file, pinned Chart.js with SRI, the print stylesheet,
     viewport sizing, keyboard and focus. A design choice never overrides a
     mechanism.
  3. **The chosen DNA's guardrails.**
  4. **Mode styling defaults** — which token a component takes, the example
     radius and shadow values. A DNA guardrail beats these.
  5. `polish.md`, then the `html-components.md` recipes.

  `quality-floor.md`, `polish.md`, `html-mode.md`, and `pptx-mode.md` each
  point at it. `executive-writing.md` is explicitly outside the chain — copy
  rules and design rules do not compete.

- `references/html-mode.md`: the measure micro-rule said `max-width: 68ch` for
  a 60–75 character line. Wrong — `ch` is the width of "0", so 68ch measured
  ~90 characters in the v1.3.0 QA pass. Now states the trap and the measured
  value (`52ch` → 68 characters), matching what the sample already uses.
- `references/html-mode.md`: the offline-charts bullet now says to style SVG
  marks with CSS classes rather than `fill=`/`stroke=` attributes, which is the
  defect the v1.3.0 validator work uncovered in `northlane-pitch.html`.
- `references/html-mode.md`: the QA step dropped its stale "or grep the
  `<section>` styles for `#`" fallback — the token validator now does that job
  properly, including inside inline SVG.

## 1.3.1 — 2026-08-26

### Fixed

- `references/design-dna.md`, Meadow Ledger: the Character line and the
  Guardrails line contradicted each other. Character said "everything else is
  white with forest/lime as punctuation"; Guardrails said "lime never bleeds
  past its one slide". Read strictly, the guardrail left every slide after the
  title with no accent at all, which breaks quality-floor Required 2. The 1.3.0
  release resolved this by interpretation in the changelog only, because plan
  constraint 5 forbade editing the file.

  The guardrail now states the limit in terms the eye can check:
  **one lime plane per deck**, and elsewhere **at most one lime mark per
  slide**. It also names the contrast trap the old wording never mentioned:
  lime is a ground, never a text colour on white (`9FE870` on white is 1.5:1;
  ink on lime is 13:1, lime on the forest band is 9.4:1).

  (The first wording of this fix said "one datum per slide" and leaned on a
  clause that lived only in this changelog, not in `design-dna.md`. Corrected
  in 1.3.3 — see below.)

## 1.3.0 — 2026-08-26

Upgraded `premium-decks` from four external UI resources. Every rule taken had
to name a deck application; everything else was rejected on the record below.

### Added

- `references/polish.md` (new) — craft rules the pre-flight checklist cannot
  test by eye, split into "both modes" and "HTML mode".
- `references/html-components.md` (new) — five token-based slide-component
  recipes in plain CSS: process/stepper row, roadmap gantt bars, dense data
  table, KPI row with attainment, milestone timeline. Closes the gap where
  roadmap and process slides had only the pptx timeline pattern.
- `references/html-mode.md` — new "Micro-rules" section required in the deck
  shell, plus keyboard/focus requirements in the shell section.
- `references/quality-floor.md` — Required 7 became a three-level elevation
  scale; new Required 14 (icon set discipline); three new pre-flight lines
  (numeric formatting, icon consistency, HTML keyboard/focus path).
- `references/executive-writing.md` — Numbers section gained deck-wide
  formatting consistency rules.
- `README.md` (new, plugin root) — structure plus a Maintenance section:
  versioning, changelog discipline, when to bump, and the reinstall trap.
- `GAP-AUDIT-v1.3.md` (new, plugin root) — the written audit of
  designsystemchecklist.com against the quality floor.
- `samples/ridgeline-card-cost.html` (new) — 4-slide sample exercising the
  stepper, gantt, and data-table recipes, built on the **Meadow Ledger** DNA
  (first use; the last two decks used custom espresso/amber and burgundy/gold).

### Fixed

- `scripts/slide-token-validator.py` was a dead wrapper that shelled out to
  `html-token-validator.py`, a file this plugin never shipped — every run
  failed with "can't open file". Replaced with a working self-contained
  validator. Outside `:root` and `@media print` it flags: raw hex and
  `rgb()`/`hsl()`/`oklch()`/`lab()` literals; `font-family` without a `var()`;
  `font-size` with any literal length; non-token inline `style=`; and SVG
  presentation attributes (`fill`, `stroke`, `stop-color`, `font-family`,
  `font-size`), which cannot resolve `var()` at all.
- Running that validator surfaced 17 pre-existing token defects in
  `samples/northlane-pitch.html` — 15 raw hex `fill`/`stroke` values and 2 raw
  `font-family`/`font-size` attributes inside its two inline SVG charts, plus
  two invented `rem` sizes in CSS. The chart marks now take their colours from
  CSS classes (`.svg-ink`, `.svg-mark`, `.svg-line`, `.svg-axis`,
  `.svg-muted`) and the sizes are declared in the scale. Both samples pass.

### Sources — what each contributed, and what was rejected

**https://ui-skills.com** (highest value)

- *Contributed (Playbook):* `tabular-nums` on all deck numerics;
  `text-wrap: balance` on titles and `pretty` on body; `aspect-ratio` on media
  and chart boxes; ≥44×44px nav hit areas; `:focus-visible`; one accent per
  view; 60–75 character measure; ~1.1 heading line-height with tighter display
  tracking; never colour alone for status; `min-width: 0` plus `line-clamp` or
  a mask fade for long labels.
- *Contributed (`jakubkrehel/better-ui`):* concentric border radius
  (outer = inner + padding); optical over geometric alignment; shadows for
  elevation and borders for structure; interruptible CSS transitions with
  keyframes reserved for the one staged reveal; ~100ms staggered entrance on
  first load only; short exits with a small `translateY`; `scale(0.96)` press
  feedback; 1px pure-black/pure-white image outline at ~10% (never tinted);
  icon stroke matched to text weight; outline default, fill for active;
  name the transitioned properties.
- *Contributed (`antfu/web-design-guidelines` → the Vercel Web Interface
  Guidelines it fetches):* explicit `transform-origin` and SVG
  `transform-box: fill-box`; typographic finish (`…`, curly quotes, en dash
  for ranges, non-breaking space before units); `Intl.NumberFormat` /
  `Intl.DateTimeFormat`; `color-scheme` and `<meta name="theme-color">`;
  `aria-label` on icon-only controls and `aria-hidden` on decorative SVG;
  explicit `<img>` dimensions; no full-screen backdrop blur.
- *Contributed (`rams/rams`):* muted-text contrast floor on tinted grounds.
- *Rejected:* the installable-skill catalog itself — nothing was installed;
  deck-studio stays one skill. Form rules (labels, `autocomplete`, paste
  blocking, inline error placement), URL/navigation state, hydration safety,
  list virtualization, touch gestures and drag, empty states, modal backdrops,
  loading skeletons and spinners: app chrome with no slide equivalent.
  Vercel's "Title Case for headings/buttons (Chicago style)" was rejected
  outright — see Conflicts.

**https://designsystemchecklist.com**

- *Contributed:* an explicit elevation scale with a surface colour per level
  (Foundations `df-elevation-shadows` + `df-elevation-background`); icon set
  consistency (`df-iconography-style`, `df-iconography-grid`); number and date
  formatting consistency; the progress-bar rule that a track never appears
  without a label (`c-progress-label`), applied to the KPI recipe; the
  Maintenance section, distilled into `README.md`.
- *Rejected:* dark-mode palette variants (a deck commits to one ground, and
  `design-dna.md` already carries both dark and light profiles); breakpoints
  and per-device grids (decks are fixed 16:9); a z-index system (slides are
  single-layer); icon naming, keywords, and reserved-icon registries;
  internationalisation; and 162 of the 166 core-component items — only table,
  tooltip, progress, and badge map to anything on a slide. Full item-by-item
  verdicts in `GAP-AUDIT-v1.3.md`.

**https://reui.io/components**

- *Contributed:* the structure of five composed patterns — Stepper (numbered
  markers on a rule, completed segment coloured, one current marker), Gantt
  (fixed label column, period header row, bars positioned on a time grid with
  a percent-complete fill), Timeline (right-aligned date gutter, dot on a
  rail, filled versus hollow states), Table (hairline horizontal rules only,
  right-aligned numerics, a ruled total row). All four were rewritten from
  scratch as plain token-based CSS in `references/html-components.md`.
- *Rejected:* the entire delivery model — no npm, no shadcn CLI, no Tailwind,
  no React, and no source copied. Kanban, Filters, Event Calendar, File
  Upload, Sortable, and the Data Grid's interactive layer (virtualization,
  column resizing, drag-to-reschedule, inline CRUD) are irrelevant to a static
  slide.

**https://coss.com/ui** (lowest value — hard timeboxed)

- *Contributed:* exactly one pattern, the Meter — a label on the left and its
  value on the right, sharing one baseline row above a full-width track. That
  is the header row of the KPI attainment recipe.
- *Rejected:* everything else. Base UI is a React component API; empty states,
  toolbar spacing, and `kbd` styling have no slide equivalent. Closed early
  rather than forcing content in.

### Conflicts resolved (in favour of the existing floor)

1. `polish.md` says shadows carry depth and borders carry structure. Several
   DNA guardrails forbid shadows entirely (Product Whiteout, Meadow Ledger).
   **Guardrail wins.** A precedence note was added to `polish.md`, and
   Required 7 now states that the scale collapses to three surface/border
   levels when a DNA forbids shadows.
2. The Vercel guidelines require Title Case for headings and buttons.
   `executive-writing.md` requires titles that read as plain assertions, and
   `polish.md` requires sentence case on labels. **Existing floor wins**; the
   Title Case rule was not adopted.
3. The Playbook's "thin neutral outline around images" appears to brush the
   floor's ban on "generic 1px solid gray borders as the only card treatment".
   Not a conflict: the ban is about cards, and the outline is pure black or
   pure white at ~10% on images only — never a grey or tinted ring.
4. Meadow Ledger's guardrail says "lime never bleeds past its one slide" while
   its Character line says "everything else is white with forest/lime as
   punctuation". Reading adopted: **the lime *plane* is limited to one slide;
   lime as small punctuation (one bar fill, one table cell) is permitted.**
   The strict reading would leave three of four slides with no accent at all,
   which breaks floor Required 2. `design-dna.md` was left untouched at the
   time (plan constraint 5); **the file itself was corrected in 1.3.1.**

### What the fresh-eyes QA pass caught (and what it changed)

A subagent reviewed the rendered slides against the updated checklist. Ten
findings were real and are fixed in the sample; five of them were defects in
the new reference material itself and are fixed there too:

- **Contrast, non-text (3:1).** Pale tracks, unstarted bars, and future step
  dots sat at 1.1–1.4:1 against white and would vanish through a projector.
  `html-components.md` now requires a separate `--data-edge` token for any
  shape that carries a value, distinct from `--hairline`, verified at 3:1.
- **Contrast, text.** The muted tone measured 3.59:1 on the lime plane. The
  case `polish.md` already names; the sample now overrides it there.
- **Type scale.** `clamp()` on title and body independently let the ratio fall
  to 1.82x at 1024px — a banned default. Clamp floors must be chosen so the
  2x rule holds across the whole range, not just at the design size.
- **Table margins.** Uniform cell padding pushed the first column 16px past
  the slide margin. The recipe now zeroes the outer cells' outer padding.
- **Highlight chip.** A padded `<span>` either broke the numeric column's
  right alignment or bled past the margin. The recipe now tints the `<td>`.
- **Unlabelled encoding.** The gantt encoded percent-complete in bar fill and
  never printed it. The recipe gained a `.gantt-pct` column and header ticks.
- Also fixed in the sample: display line-height 0.92 collided descenders at
  the title scale; `68ch` yielded ~90 characters, not 68 (52ch gives 68 in
  Inter); the pager sat 5px below the nav buttons; content start varied with
  title line count; the entrance replayed when arrowing backwards.

## 1.2.0 — 2026-08-23

- Added `references/design-dna.md`: seven real product design systems (Linear,
  Apple, Anthropic, Railway, Cursor, Wise, Framer) extracted from
  superdesign.dev/design-systems and translated to deck tokens, each with
  guardrails and a PPTX safe-font mapping.
- Quality-floor rule 12 now forbids reusing the same DNA on two decks in a row.

## 1.1.0 — 2026-08-23

- Folded the short-lived `board-deck` skill back into `premium-decks` as the
  optional `templates/build-deck.js` generator. deck-studio ships one skill.
