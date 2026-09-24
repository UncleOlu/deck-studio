# Blind judge — baseline-v1.3.3__vs__v1.4.2

## Rubric means (1–5) by dimension

| Dimension | baseline-v1.3.3 | v1.4.2 |
|---|---|---|
| storyline | 4.29 | 4.29 |
| synthesis | 4.14 | 4.00 |
| framework_fit | 4.00 | 4.00 |
| page_grammar | 3.57 | 4.00 |
| data_integrity | 4.29 | 4.57 |
| visual_quality | 3.86 | 3.43 |
| decision_readiness | 4.00 | 3.86 |
| **overall** | **4.02** | **4.02** |

## Per case (mean over dimensions)

| Case | A | A score | B | B score | Preferred |
|---|---|---|---|---|---|
| grocer-costout | baseline-v1.3.3 | 4.00 | v1.4.2 | 4.00 | baseline-v1.3.3 |
| keynote-allhands | baseline-v1.3.3 | 3.57 | v1.4.2 | 3.86 | v1.4.2 |
| keynote-conference | baseline-v1.3.3 | 4.14 | v1.4.2 | 3.86 | baseline-v1.3.3 |
| market-entry | v1.4.2 | 4.57 | baseline-v1.3.3 | 3.86 | v1.4.2 |
| sell-side-pitch | v1.4.2 | 3.86 | baseline-v1.3.3 | 4.43 | baseline-v1.3.3 |
| steerco-update | baseline-v1.3.3 | 3.71 | v1.4.2 | 4.29 | v1.4.2 |
| take-private-valuation | v1.4.2 | 3.71 | baseline-v1.3.3 | 4.43 | baseline-v1.3.3 |

Preferences: baseline-v1.3.3 4, v1.4.2 3

## Discrimination (generated vs real)

- Judge 1: accuracy 40/40 = 100%
  - tell: Waterfall has a full-sentence numeric title, an italic unit subtitle and a side panel of bold lead-ins, the tool's usual layout
  - tell: Action/owner/by table with a peach-highlighted first row and a sentence title naming the first action, a stock generated layout
  - tell: Decision table with a peach highlighted row, a 'Value at stake' column and a board-action sentence title
  - tell: Peer table with a highlighted focal row, a gap row and a right-hand panel whose bold lead-ins restate the title
- Judge 2: accuracy 40/40 = 100%
  - tell: Full-sentence action title with a computed % of ceiling, a clean template waterfall, and bold-lead callouts on the right; no source line
  - tell: Uniform action/owner/by table with one peach-highlighted row and a title that counts its own rows ('Six actions')
  - tell: Same templated decision table with a peach first row and a value-at-stake column; the title reads as a board-ask sentence
  - tell: Peer table with a highlighted company row, a computed gap row, and a two-point bold-lead sidebar
- Judge 3: accuracy 40/40 = 100%
  - tell: Full-sentence action title with a computed % of ceiling, one highlighted waterfall bar, and a bold-lead-in sidebar; the same template recurs across the set
  - tell: Rule-only action/owner/by table with a peach first row highlighted, plus a sentence title stating the priority
  - tell: Same peach-highlighted decision/owner/when/value table, with a sentence title that ends in 'now'
  - tell: Clean benchmark table with a highlighted subject row, a gap row, and a two-point bold-lead-in sidebar that restates the maths
- **Mean accuracy 100%** (target ≤ 65%; 50% = chance)
