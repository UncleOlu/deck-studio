# Banking pitchbook and board book grammar

Use this for the `banking` register. Board-book values come from 48 coded
banker books in `research/corpus-findings.md`; the sell-side and
strategic-alternatives pattern comes from 8 coded banker discussion books from
7 banks in `research/pitchbook-findings.md` (SEC EDGAR EX-99.(c) exhibits).
Counts below are "k of 48" or "k/8".

## Two book types

| | Board book (valuation / fairness, special committee) | Sell-side pitch (to an owner) |
|---|---|---|
| Purpose | Present the analysis neutrally so the board can decide | Lay out value, alternatives, buyers, and a process, then recommend one |
| Titles | **Neutral, not empty** (R3): a label plus the factual finding, e.g. "Trading comps: the offer is 12.7x LTM EBITDA against a 10.7x median" (≤ 20 words). State what the page shows, never a judgment ("attractive", "fair"). A bare label ("Selected Precedent Transactions", median 5 words in the corpus) is allowed, but blind judges scored those books lower on synthesis | The same neutral label, ~5 words (62 of 64 sampled pages); a one-line finding under it is the stronger form (2/8). Not consulting action titles |
| Storyline | The fixed analysis sequence (40 of 48 books) | Situation → valuation → alternatives → buyers → process → recommendation → next steps. **Not answer-first** (0/8): the recommendation follows the analysis |
| Emphasis | Highlight boxes (43% of content slides), notes | Fewer highlight boxes (25% of pages); a section tracker on most pages (56%) |

## Board book skeleton

1. **Cover:** project code name, "Discussion Materials", date,
   "Confidential" (23 of 48 books; 39 of 48 carry a confidentiality or draft label). Use "Preliminary draft" only while it is a
   draft.
2. **Disclaimer page.** Write your own wording: say that the materials are
   for the board's use, are based on public information and management
   projections, and are not advice to any shareholder. Never copy a bank's
   legal text. Pitch books put it at the back more often (5/8) than the front.
3. **Situation overview:** the proposal (price, form, premium), the
   timeline, and the process to date.
4. **Valuation summary (football field):** the answer page. It sits by
   slide 3 after the disclaimer (R4). Show every method as a range, with the
   offer marked.
5. **Analyses**, one per section, each with a title-only divider (34 of 48
   books):
   - share price performance (line, with the offer and the 52-week range);
   - analyst price targets;
   - trading comps (table);
   - precedent transactions (table);
   - DCF (summary plus a sensitivity grid);
   - premiums paid (bar or table);
   - an LBO where a sponsor is involved.
6. **Appendix:** WACC build, management projections, and the definitions of
   non-GAAP terms.

## Sell-side / strategic-alternatives skeleton

1. **Cover** and, early, a **key considerations** page: the questions the
   board must answer, as short bold-led blocks (5/8). It is the book's
   summary page (kit slide type `exec-summary`; the lint accepts the title).
2. **Situation:** the company, the approach or trigger, and market context.
3. **Valuation**, marked "Illustrative" or "Preliminary" (7/8): share-price
   history first (6/8), then an analysis-at-various-prices table (5/8),
   premiums (5/8), and a football field (4/8).
4. **Alternatives side by side** (4/8): one column per option (status quo,
   sale, spin, recap…) with its merits and considerations.
5. **Buyer universe** (6/8), tiered, strategics apart from sponsors, each
   with capacity or rationale. Names may be codes.
6. **Process timeline** (7/8): phases against weeks or dates, as a Gantt.
7. **Recommendation** in the bank's own voice (3/8; always after the
   analysis), then **next steps** (5/8).
8. **"Why us" and credentials** only when the book competes for the mandate
   (1/8): team page, tombstones, "Why <bank>".

## Page grammar

| Element | Convention | Rule |
|---|---|---|
| Unit line | "($ in millions, except per-share values)" directly under the title on every numeric page | R7 (45% of banking chart pages; the lint warns) |
| Source | "Source: Company filings, FactSet as of DD Mon YYYY" on every chart or table page. Found on 87% of banking chart pages | R5 |
| Notes | Numbered notes (1), (2)… above the source line, in reading order. 44 of 48 coded books use this system | R6 |
| Numbers | Multiples as `x.x` (e.g. `10.7x`); negatives in parentheses `(12.4)`; per-share values to 2 decimals; percentages to 1 decimal; one precision per column | — |
| Dates | Every market figure carries an "as of" date. Projections name their case: "Management Case", "Street Case" | — |
| Colour | Navy primary (30 of 48 books; blue in 13 more), one support tone, the accent for the offer line and the subject company's row | R15 |
| Page size | 16:9 by default; 4:3 or Letter is common in older books (45 of 48), on request | R14 |

## Page recipes

All are in `finance-charts.md`:

- football field;
- sensitivity heat-table;
- comps and precedent tables (median row, subject row tinted);
- tornado;
- waterfall (for an EBITDA or value bridge).

Share-price history is a native line chart. Annotate the key dates on the
line (announcement, unaffected date) with short labels, and mark the offer
as a dashed reference line.

## Integrity rules (checked by the scripts)

- **Shares count:** one diluted share count and one net-debt figure through
  the whole book. `integrity-check.py` flags a metric with two values.
- **Implied values:** every implied per-share value states its multiple
  range and the metric it multiplies. Add a `calc:` line in the notes (for
  `trace-check.py`).
- **Premiums:** premiums are calculated against a named unaffected date.
  State it on the page.
