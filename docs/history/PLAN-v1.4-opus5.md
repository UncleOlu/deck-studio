# deck-studio → consulting & banking grade (plan for Opus 5.5)

## Context

`premium-decks` (v1.3.3, `~/claude-plugins/deck-studio/`) builds polished
executive decks, but its rules come from product and keynote design. It has
no model of how MBB/Big 4 consultants and investment bankers **think**
(hypothesis → synthesis → storyline) or how they **lay out a page** (action
title, tracker, unit line, "so-what" box, source footer).

Olu's goals:

1. Train the skill on real decks from the approved sources: SEC EDGAR
   EX-99(c) board books, and the free samples on Slideworks, SlideScience,
   Analyst Academy, Slidebook.io, 10X EBITDA, and Alexander Jarvis.
2. Produce consulting-quality decks on demand from an injected folder of
   analysis and context.
3. Publish the result as a top-tier public GitHub skill.

On approval, the first execution step copies this file to
`docs/history/PLAN-v1.4-opus5.md` so an Opus 5.5 session can
run it.

### What makes this world-class rather than "more references"

An expert review of the first draft found eight weaknesses. Each fix is
built into the phases below.

1. **Sample bias.** EDGAR gives *fairness/board* books, not pitches.
   Firm-published "insights" PDFs are marketing, not client work.
   → Add **public-sector client deliverables**: the decks that agencies,
   cities, and universities publish from engagements. They are real client
   work in real client grammar. Tag every document by genre and weight rules
   by genre.
2. **Codebook before scale.** → Pilot the codebook on 6 decks, revise it,
   then scale. Measure agreement with Cohen's κ ≥ 0.7. Stop collecting at
   *saturation* (10 new decks add no new archetype), not at a fixed count.
3. **Overfitting.** → Hold out 20% of the corpus. No rule is derived from it;
   it is used only for eval.
4. **Thinking, not just formatting.** The hard part of consulting quality is
   synthesis: insight vs. summary, the "so what" ladder, and a day-one
   answer. → The storyline engine includes a synthesis step, and an
   adversarial **partner-review agent** red-teams the ghost deck.
5. **Deliverables clients can use.** Consultants hand over editable
   PowerPoint. → Mode A requires a real **slide master** with placeholders
   (tracker, title, source, page number), **native editable charts and
   tables** (never images), a correct reading order, and alt text.
6. **Density makes overflow and misalignment likely.** → Add automated
   checks from the rendered deck: text overflow, coordinate drift across
   slides, and footnote-numbering order. Add **arithmetic integrity**:
   waterfalls sum, percentages total 100, and a metric keeps the same value
   on every slide.
7. **A quality claim needs a test that can fail.** → Blind **discrimination
   test**: a judge sees generated slides mixed with held-out real slides.
   The target is that the judge cannot tell them apart on grammar and
   storyline. Olu grades a calibration set so the LLM judge is anchored to a
   human expert.
8. **Big-bang release risk.** → Ship in three releasable milestones. Each one
   is useful on its own.

## Hard constraints

1. **IP: extract patterns, never content.**
   - The corpus lives in `~/deck-corpus/`, outside the repo and never
     committed.
   - Nothing ships from it: no slide images, verbatim text, logos,
     firm-branded templates, or DNA names.
   - References cite URLs and describe conventions in our own words.
   - All samples and fixtures are fictional.
2. **Access: free and public only.**
   - Do not bypass paywalls, logins, or robots rules.
   - Use the browser where WebFetch is blocked.
   - For EDGAR, read the `User-Agent` from env var `SEC_USER_AGENT` (never
     hard-coded), stay at ≤5 requests/s, and cache locally.
3. **Size limits.** SKILL.md stays under 300 lines, and each reference at or
   under ~150 lines. The register references load only when their register
   is selected. Measure the context tokens each register loads, and keep
   consulting ≤ 1.5× keynote.
4. **Nothing gets weaker.** The quality floor, the PPTX safe fonts,
   ASD-STE100, and the precedence chain stay binding. The density changes
   enter only through the countable **register overrides** table.
5. **Security** (CLAUDE.md): no eval/exec/shell=True. Ingest canonicalises
   paths, refuses symlink escapes, caps file count and size, and parses
   Office XML only with `defusedxml`.
6. Every phase has a gate. Olu approves before `/init-security`, before the
   repo is created, and before any public push.
7. **Authorship: Olu is the sole author.** No Claude attribution anywhere:
   - no `Co-Authored-By: Claude…` trailer in any commit;
   - no "Generated with Claude Code" line in any PR, README, CHANGELOG, or
     file header;
   - Olu is the only author in `plugin.json`, the `LICENSE` copyright line,
     the README, and the package metadata.

   Olu's instruction overrides the harness's default attribution reminder.
   Mentioning Claude Code as the *platform* the skill runs on is fine.
   Crediting it as an author is not. A scan on 2026-09-22 found no existing
   attribution lines; `plugin.json` already lists Olu.
8. **Workflow opt-in.** Olu explicitly authorises this plan's Workflow runs
   (Phase 2 coding, Phase 5 evals), each capped at ≤10 agents per run.

---

## Milestone 1 (v1.4) — research corpus + storyline engine + ingest

### Phase 0 — baseline
- `git init` the plugin and commit v1.3.3 as-is.
- Create `~/deck-corpus/{edgar,consulting,public-sector,banking}/` and
  `manifest.jsonl`. Each row holds: url, publisher, firm, date, genre, deck
  type, industry, license note, sha256, and a `holdout` flag.
- **Baseline eval first.** Run v1.3.3 on the 5 fixtures (Phase 5 builds them;
  build the fixtures now) and store the scores. Every later claim is measured
  against this baseline.

### Phase 1 — corpus (stratified, until saturation)

- **EDGAR.** Write `tools/corpus/edgar_fetch.py` (dev tool, not part of the
  skill). It pulls EX-99.(c) exhibits from SC 13E-3 and DEFM14A/PREM14A
  filings. Stratify:
  - Advisors: bulge bracket and elite boutique.
  - Years: 2015–2026.
  - Deal types: take-private, special committee, strategic sale.

  The finviz `get_edgar_*` tools can seed CIKs. Include a `--dry-run` flag.
- **Aggregators.** Slideworks, SlideScience, Analyst Academy, Slidebook.io,
  10X EBITDA, and Alexander Jarvis: free samples only.
  - Download originals only where they are publicly hosted.
  - Where a site offers only a deconstruction article, save notes, not files.
- **Public-sector client decks** (a source added beyond Olu's list, so ask
  Olu once before collecting). Search for engagement deliverables that
  agencies, cities, and universities publish, across MBB and Big 4.
- **Stratify** consulting decks by firm × deck type:
  - diagnostic
  - strategy
  - transformation/SteerCo
  - market study
  - due diligence
- Gate:
  - Every genre cell has at least 8 decks.
  - Saturation is reached.
  - A 20% hold-out is flagged.
  - `research/corpus-sources.md` (ships) lists the sources, the method, and
    the counts. It includes no files.

### Phase 2 — deconstruct (codebook-driven)

1. Render the pages (`pdftoppm -r 100`) and extract the text
   (`pdftotext -layout`).
2. Write `research/coding-schema.json`.
   - **Deck level:** storyline type, where the exec summary sits and its
     form, tracker/divider system, appendix ratio, page count, and footnote
     system.
   - **Slide level:** archetype, whether the title is an assertion, title
     words and lines, unit line, chart type, so-what box, source/notes
     footer, element count, colours, grid, callout devices, and text density
     (words/slide).
3. **Pilot** on 6 decks with two independent coders, then revise the
   codebook.
4. **Scale** with a Workflow (≤10 agents per run, in batches). Double-code
   15%; κ ≥ 0.7 on archetype, chart type, and whether the title is an
   assertion. Disagreements go to an adjudicator agent.
5. Write `research/corpus-findings.md` (ships). Every claim carries n, the
   median/IQR, and the genre split. Keep a **rule ledger** of proposed rule →
   supporting statistic → decision (adopt/reject/why).
- Gate: κ is met, every proposed rule has a ledger row, and none is sourced
  from the hold-out.

### Phase 3 — distil (registers + storyline engine)

**Register mechanism.** Add `register: keynote | consulting | banking` at
workflow step 1. `quality-floor.md` gains a **Register overrides** table,
countable and exhaustive. Examples:
- Consulting allows a dot-dash exec summary, a tracker, and numbered sections.
- Banking allows dense comps tables, footnote blocks, and a "Preliminary
  draft / Confidential" label.

All other floor items stay binding.
*Trade-off:* this adds one lookup level. In return, the skill can express
genuine genre density without deleting the keynote rules. Accepted.

| File | Contents |
|---|---|
| `references/storyline.md` | Governing question → issue/hypothesis tree (MECE check) → **synthesis ladder** (fact → "so what" → implication → action; reject any title that restates a fact) → Minto pyramid / SCR → **ghost deck** → horizontal-logic test (the titles alone tell the story) and vertical-logic test (the body proves the title). |
| `references/frameworks.md` | A framework library indexed by *the question it answers*: driver tree, 2×2, value chain, profit pool, waterfall bridge, options × criteria (Harvey balls), prioritisation matrix, phased roadmap, sensitivity. Each has its preconditions and misuse cases. |
| `references/consulting-grammar.md` | Page anatomy with corpus-derived values: title length, tracker, unit line, so-what box, source/notes footer, exec-summary forms, dividers, appendix discipline, density limits per archetype. |
| `references/banking-pitchbook.md` | Book anatomy: situation overview, valuation summary (football field), trading comps, precedent transactions, DCF and sensitivity, premia, LBO, process timeline. Conventions: `($ in millions)`, parenthesised negatives, `x.x` multiples, "as of" dates, ordered footnotes. |
| `references/finance-charts.md` | Recipes for both modes: waterfall, football field, Marimekko, Harvey balls, 2×2 bubble, tornado, sensitivity heat-table, comps table. PPTX versions use **native** pptxgenjs charts and tables so the client can edit them. |
| `references/partner-review.md` | The red-team rubric for the partner-review agent: the ~15 questions a partner asks of a ghost deck and of a rendered deck. |
| `references/pptx-mode.md` (extend) | `defineSlideMaster` with placeholders for tracker, title, source, and page number. Rules for native charts and tables. Reading order and alt text. |
| `data/slide-archetypes.csv` (new) + `slide_search_core.py` | Archetypes with corpus frequency, register, required elements, and when to use each. |
| `data/slide-strategies.csv`, `slide-charts.csv` | Add the consulting and banking deck types and the finance chart types. |
| `references/design-dna.md` | Two **unbranded** register DNAs whose tokens come from the corpus colour and typography stats. |
| `templates/build-consulting.js`, `build-pitchbook.js` | Data-JSON driven and master-based, each with a JSON schema. |

### Phase 4 — "inject a folder" pipeline

- **Step 0: Ingest.** `scripts/ingest.py <folder>` reads pdf, docx, xlsx
  (values *and* formulas, sheet!cell), csv, md, txt, and pptx. It normalises
  units and scale (k/M/B, %, currency, period) and writes two files:
  - `brief/sources.md`
  - `brief/facts.jsonl`: `{id, value, unit, scale, period, text, file,
    locator}`

  It then flags conflicting values for the same metric *before* any
  storyline work.
- **Step 1: Storyline.** Governing question, issue tree, synthesis, ghost
  deck. The **partner-review agent** red-teams the ghost deck. Then comes the
  **user checkpoint**: Olu approves the ghost deck, and nothing is built
  before that.
- **Steps 2–4:** design, layout, and build (unchanged), using the register
  references.
- **Step 5: QA.** Run the existing checks plus these new scripts:
  - `trace-check.py`: every number on a slide maps to a fact id, or to
    `deck-data.json` marked illustrative.
  - `integrity-check.py`: waterfalls sum, shares total 100, one value per
    metric deck-wide, and footnote markers appear in order and resolve.
  - `storyline-lint.py`: action titles, exec summary at or before slide 3, a
    source on every chart slide, tracker consistency. It also prints the
    title sequence for the horizontal-logic review.
  - `layout-check.py`: from the rendered deck plus the shape geometry, it
    finds text overflow, drift of title/margin/footer coordinates across
    slides, and off-grid elements.
  - The partner-review agent reviews the rendered images.

### Phase 5 — prove it

- **Fixtures** (`evals/fixtures/`, fictional, deliberately messy: mixed
  units, one conflicting figure, and irrelevant files):
  - a grocer cost-out diagnostic;
  - a market-entry study;
  - a SteerCo update;
  - a take-private board valuation;
  - a sell-side pitch;
  - 2 keynote fixtures for regression.
- **Evals** (`claude plugin eval`; confirm the format with the
  claude-code-guide agent):
  - all scripts pass;
  - the rubric judge, calibrated on Olu's grades of 10 slides, scores
    storyline, synthesis, framework fit, page grammar, traceability,
    editability, and visual quality;
  - the **blind discrimination test** against held-out real slides;
  - **trigger evals**: the skill description fires on deck requests, picks
    the correct register, and does not fire on non-deck requests.
- **Pass bar:**
  - v1.4 beats the v1.3.3 baseline on every consulting/banking dimension;
  - the keynote scores do not regress;
  - judge accuracy on the discrimination test is ≤ 65% for grammar.
- **Samples:** 2 new fictional samples built *through the ingest path*: a
  12-slide consulting deck and an 8-slide banking book, each as pptx + pdf.
  The existing samples must still validate.
- **Release:** bump to 1.4.0, write the CHANGELOG (the contribution and the
  rejections of each source), reinstall, update memory, and run the
  chief-of-staff audit.

## Milestone 2 (v1.5) — banking depth + HTML parity

- Bring the finance-chart and pitchbook recipes to HTML mode.
- Add a fully worked banking sample.
- Tune the density limits from the eval failure analysis.
- Gate: the same eval suite, with no regressions.

## Milestone 3 (v2.0) — public release

1. **License blocker.** `scripts/LICENSE-pptx-scripts.txt` (Anthropic)
   forbids redistribution. `thumbnail.py`, `add_slide.py`, `clean.py`, and
   `office/*` (including the XSDs) therefore cannot be published. Replace
   them with clean-room tools:
   - `validate_pptx.py`: zip/rels/content-types integrity, a python-pptx
     round-trip, and a render check;
   - `thumbnail.py` rebuilt on pdftoppm + Pillow.

   Delegate to the Anthropic pptx skill only when it is installed locally.
   Keep the originals on a private branch.
2. **Provenance audit** of `data/*.csv` and all references: some content was
   distilled from ui-ux-pro-max, impeccable, and other skills. Keep content
   only under a compatible licence and attribute it in `NOTICE`. Rewrite the
   rest.
3. **Scrub personal paths but keep Olu as the author.**
   - Remove home-directory paths, memory paths, and the local-only marketplace
     install instructions (replace them with the public marketplace install).
   - Keep Olu as the named author (constraint 7).
   - Do not publish Olu's email unless Olu asks.
4. **Portability:**
   - Conform to the open Agent Skills spec (frontmatter, relative paths).
   - Support macOS, Linux, and Windows (for Windows, document the
     LibreOffice path).
   - Keep dependencies minimal and pinned; a `doctor.py` checks them.
5. **Repo:**
   - `LICENSE` (MIT or Apache-2.0: Olu picks), `NOTICE`, `CONTRIBUTING`,
     `SECURITY.md`, and a `.gitignore` that excludes the corpus, renders,
     `.venv`, and `.DS_Store`.
   - `README` with install, a 60-second demo, a before/after gallery of the
     fictional samples, the methodology, and a link to the corpus findings.
   - `pyproject.toml` (ruff, pytest), and `tests/` for every own script,
     including path-safety cases for ingest.
   - GitHub Actions: lint, tests, sample validation, and a smoke eval.
   - Tagged releases, and a changelog for each release.
6. Olu approves `/init-security`, repo creation, and the first push.

## Verification (end to end)

- `python3 tools/corpus/edgar_fetch.py --dry-run`: lists the candidate
  exhibits by stratum
- `pytest -q` passes; `ruff check .` is clean
- `python3 scripts/ingest.py evals/fixtures/grocer-costout`: `facts.jsonl`
  has locators, and the planted conflict is flagged
- Run `storyline-lint.py`, `copy-lint.py`, `trace-check.py`,
  `integrity-check.py`, and `layout-check.py` on the new samples: 0 errors.
  Each script must also catch its **planted defect** in a deliberately broken
  copy.
- Run `validate_pptx.py` on all pptx samples (plus: the charts are native,
  the master placeholders are used) and `slide-token-validator.py` on the HTML
- `claude plugin eval`: the pass bar in Phase 5 is met, and the report is
  saved to `evals/reports/`
- Public branch checks:
  - `git grep for home-directory paths, memory paths, and the local marketplace name` finds nothing.
  - No Anthropic-licensed file remains.
  - `git log --format=%B | grep -iE "co-authored|generated with|noreply@anthropic"`
    and `git grep -iE "co-authored|generated with claude"` find nothing.
  - `git log --format='%an %ae' | sort -u` shows only Olu.
- chief-of-staff audit: every must-fix item resolved
