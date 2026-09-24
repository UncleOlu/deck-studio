# Provenance

Every file in this repository, with where it came from and the licence that
covers it. The project is MIT-licensed (`LICENSE`); third-party material keeps
its own licence, attributed in `NOTICE`, with full texts in `licenses/`. The
file-by-file evidence is in `docs/history/PROVENANCE-AUDIT.md`.

| Path | Origin | Licence | Decision |
|---|---|---|---|
| `skills/premium-decks/data/*.csv` except `slide-archetypes.csv` | nextlevelbuilder/ui-ux-pro-max-skill (commit bc826e2). deck-studio added rows to `slide-strategies.csv` and `slide-charts.csv` | MIT, © 2024 Next Level Builder, plus own rows | Keep; attributed |
| `data/slide-archetypes.csv` | Generated from the own corpus study | MIT (own) | Keep |
| `scripts/slide_search_core.py`, `scripts/search-slides.py` | Same upstream; deck-studio added the archetype domain and lint fixes | MIT, © 2024 Next Level Builder | Keep; attributed |
| `scripts/slide-token-validator.py` | Own rewrite of the upstream validator of the same name (no shared lines) | MIT | Keep; attributed as a courtesy |
| Anthropic pptx-skill scripts (`office/**`, `add_slide.py`, `clean.py`, `thumbnail.py`) | Anthropic `pptx` skill | Proprietary: no redistribution or derivatives | **Not included** (removed before 1.0.0). Replaced by own `deck_edit.py`, `validate_pptx.py`, `deck_thumbnails.py` |
| `references/pptx-mode.md` (pptxgenjs mechanics, fonts, QA prose) and `references/quality-floor.md` (banned list, Required 2/3/5/10) | Passages that followed the Anthropic pptx skill's wording and order | — | **Rewritten before 1.0.0** in new wording and grouping; values replaced with the kit's own scale and grid |
| `references/quality-floor.md` (rest) | Ideas from impeccable (Apache-2.0) and taste-skill `high-end-visual-design` (MIT), own wording | Apache-2.0 / MIT ideas | Keep; attributed |
| `references/design-dna.md` | Directions modelled on public product sites; prose rewritten before 1.0.0 in own words (the earlier text cited superdesign.dev, licence unknown) | MIT (own wording); colour values and font names are facts | Keep; product names used descriptively |
| `references/html-mode.md` layout table | Adapted from the ui-ux-pro-max `slides` skill | MIT | Keep; attributed |
| `references/polish.md`, `html-mode.md` micro-rules | Ideas from the ui-skills Playbook and Vercel Web Interface Guidelines (both MIT); no text overlap found | Own wording | Keep; acknowledged |
| `references/html-components.md` | Pattern ideas from reui.io (MIT); meter idea from coss.com/ui (AGPL-3.0: idea only, no code) | Own CSS | Keep; do not import coss code |
| `templates/lib/vendor/node_modules/{pptxgenjs,jszip}` | Unmodified npm dist: pptxgenjs 3.12.0, jszip 3.10.2 | MIT (jszip dual MIT/GPL-3.0, used under MIT); licence files ship beside them | Keep; attributed |
| `research/*`, `evals/cases/*` fixtures, `samples/*` | Own study and fictional data | MIT (own) | Keep. The corpus itself never ships |
| Everything else | Own work | MIT | Keep |

## The research corpus

The decks studied for `research/corpus-findings.md` and
`research/pitchbook-findings.md` are public documents other people wrote: SEC
EDGAR exhibits, public-sector publications, and firms' own public PDFs. They
are stored outside the repository and are never committed or redistributed.
The repository holds only aggregate statistics, source URLs, and conventions
described in our own words.
