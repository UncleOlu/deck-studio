# Changelog

## 1.1.0 — 2026-09-23

Makes "verified" mean something precise, and makes incomplete QA impossible to
mistake for a pass. Prompted by an external review of 1.0.0.

### Changed

- **Numbers are verified, not just cited** (`trace-check.py`, new
  `calc_verify.py`). Each number is now *verified*, *assumption*, *cited*,
  *illustrative*, *untraced*, or *calc-error*:
  - a `calc:` line is recomputed (no `eval()`): `+ - x /`, `%`, `bps`, k/M/B,
    `SUM`, `AVERAGE`, `MEDIAN`, `MIN`, `MAX`, `COUNT`, fact ids and ranges
    (`F0001:F0005`), chains (`a = expr = b`), ranges (`$49–52M`), and
    accounting negatives. Wrong arithmetic fails; prose or unsourced inputs
    are "cited, not verified" (a warning);
  - the inputs of a calculation must be cited facts, other verified results,
    or figures declared on a new `assume:` line;
  - a direct match must also name the fact's metric (on the slide or in the
    note that cites it), not just equal a number the notes happen to cite.
  Before, `calc: $999M = 100 + 50 [F0001]` passed.
- **QA reports PASS / WARN / SKIP / FAIL** (`qa-deck.py`). Skipped checks are
  named, the summary says when the automated checks were incomplete, and it
  always states that the visual review is manual. A crashed checker fails even
  when its findings are advisory; `--strict` also fails on a skip (CI uses it).
  Collision checks now use only a PDF rendered in the same run; before, a PDF
  left from an earlier build could pass the current deck.
- `ingest.py` evaluates `AVERAGE`, `MEDIAN`, `MIN`, `MAX`, and `COUNT` in
  workbook formulas, not only `SUM`.
- Positioning: "editable executive decks with documented sources, checked
  calculations, and an explicit review report" replaces "would send without
  edits".
- Samples: their notes now use checkable calculations. Alder Vale verifies
  75/75 numbers; Halden 76 of 82 plus 2 declared assumptions; Corvane 84 of
  110 (its DCF grid and conditional counts stay "cited").

### Fixed

- `storyline.md`: margin = profit ÷ revenue (it said margin = price × volume −
  cost, which is profit). An audit of every analytical example also fixed: a
  table recipe that summed a rate column; the MECE test (items, not facts, must
  not sit in two branches); driver trees that divide as well as add; an
  example that credited a whole $19M gap to one lever; the EV-to-equity bridge
  and treasury-method share count; comps medians that must exclude the
  subject; 2×2 quadrant midpoints; waterfalls that cross zero.

## 1.0.0 — 2026-09-23

First public release. Internal pre-release history, including what was
rejected and why, is in `docs/history/CHANGELOG-prerelease.md`.

- **premium-decks skill** in three registers: keynote, consulting
  (answer-first storylines, action titles, SteerCo grammar), and banking
  (board books and strategic-alternatives books).
- **Folder to deck:** `ingest.py` reads xlsx, csv, docx, pdf, pptx, md, and
  txt into a fact base; every number on a slide cites a fact or a `calc:` line.
- **Client-editable .pptx** from a native kit (slide master, native charts,
  finance recipes: waterfall, football field, comps, sensitivity, Harvey
  balls), or a self-contained HTML deck with matching finance recipes.
- **QA gate:** storyline lint, number tracing, arithmetic integrity, layout
  collisions, copy lint, device-mix cap, and a render check (`qa-deck.py`).
- **Tools:** `deck_edit.py` (restructure existing decks), `doctor.py`
  (dependency check), slide search over the decision data.
- **Research:** rules from a coded study of 131 public consulting and banking
  decks plus 8 banker discussion books (`research/`).
- **Samples:** three decks built end to end from fictional inputs, plus
  keynote examples.
- **Quality:** pytest suite on Python 3.9 and 3.12, ruff, `mypy --strict`,
  Bandit, Semgrep, gitleaks, pip-audit, and trigger evals.
