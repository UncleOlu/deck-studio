# Changelog

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
