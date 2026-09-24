# Blind judge — baseline-v1.3.3__vs__v1.4

## Rubric means (1–5) by dimension

| Dimension | baseline-v1.3.3 | v1.4 |
|---|---|---|
| storyline | 4.33 | 4.17 |
| synthesis | 4.50 | 3.50 |
| framework_fit | 4.00 | 3.83 |
| page_grammar | 3.50 | 4.17 |
| data_integrity | 4.33 | 4.67 |
| visual_quality | 4.00 | 3.67 |
| decision_readiness | 4.33 | 3.83 |
| **overall** | **4.14** | **3.98** |

## Per case (mean over dimensions)

| Case | A | A score | B | B score | Preferred |
|---|---|---|---|---|---|
| steerco-update | baseline-v1.3.3 | 4.00 | v1.4 | 4.57 | v1.4 |
| keynote-allhands | baseline-v1.3.3 | 3.86 | v1.4 | 3.00 | baseline-v1.3.3 |
| market-entry | v1.4 | 4.57 | baseline-v1.3.3 | 3.86 | v1.4 |
| take-private-valuation | v1.4 | 3.43 | baseline-v1.3.3 | 4.43 | baseline-v1.3.3 |
| sell-side-pitch | v1.4 | 4.43 | baseline-v1.3.3 | 4.57 | baseline-v1.3.3 |
| grocer-costout | baseline-v1.3.3 | 4.14 | v1.4 | 3.86 | baseline-v1.3.3 |

Preferences: baseline-v1.3.3 4, v1.4 2

## Discrimination (generated vs real)

- Judge 1: accuracy 40/40 = 100%
  - tell: Terse numeric title, a sparse sensitivity grid over a large empty lower half, and bolded lead-in sidebar bullets
  - tell: Same sparse template, a bottom takeaway box, and a self-referential footnote ('taken from the acquirer names in the file')
  - tell: Clean football field with an 'owner ask' reference line, and a note disclosing data that was not provided
  - tell: Full-sentence 'so' action title, a redundant chart subtitle 'Price', and a KPI side panel in a uniform template
- Judge 2: accuracy 40/40 = 100%
  - tell: Terse numeric action title, template sensitivity grid, bold-lead side bullets that restate the numbers, lots of empty space
  - tell: Clean template table with a highlighted 'at the offer' row, takeaway box, and a footnote that talks about 'names in the file'
  - tell: Floating-bar chart against the ask line, sentence title, a note owning up to data that was not provided
  - tell: Long action title, redundant 'Price' chart heading, a KPI side panel that re-derives the gaps, generic disclaimer footnote
- Judge 3: accuracy 40/40 = 100%
  - tell: Numeric action title, clean sensitivity grid with shaded and outlined cells, bold-lead side bullets, 'Note:' footer; templated whitespace
  - tell: Minimal comps table, 'Target One/Sponsor A' rows, highlighted offer row, full-sentence takeaway box and self-referential footnote
  - tell: Football-field with dashed ask line, sentence action title, italic unit line, long 'Note:' footer in the house template
  - tell: Full-sentence numeric title, simple sorted bar chart with a redundant 'Price' chart title, KPI side panel of percentages
- **Mean accuracy 100%** (target ≤ 65%; 50% = chance)
