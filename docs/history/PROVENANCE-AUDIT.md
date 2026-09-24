# Provenance audit: premium-decks (preparing the MIT release)

Audited 2026-09-23. This was a read-only audit: no existing file was changed.
Scope: every file under `skills/premium-decks/{data,references,templates,scripts}`.
Excluded as already known to be Anthropic-licensed: `scripts/office/`,
`add_slide.py`, `clean.py`, `thumbnail.py`, `LICENSE-pptx-scripts.txt`.

## Method

- **Upstreams compared against local installed copies:**
  - the locally installed design-skills-pack plugin: `design-system`, `slides`, `ui-ux-pro-max`, `impeccable`, `high-end-visual-design`, `design-taste-frontend`, plus its `licenses/` folder.
  - the locally installed Anthropic pptx skill: the Anthropic pptx skill (SKILL.md, scripts, LICENSE.txt).
  - the locally installed frontend-slides skill.
  - the official frontend-design plugin.
- **Upstreams fetched from the web:**
  - `ibelick/ui-skills` (`src/data/playbook.ts`, `baseline-ui`).
  - `vercel-labs/web-interface-guidelines/command.md`.
  - `zarazhangrui/frontend-slides/SKILL.md`.
- **Overlap tests:**
  1. Exact normalised-line matching (≥40 chars) against every installed upstream file.
  2. 7-word shingle matching. Shingles found in more than 6 upstream files were dropped as boilerplate.
  3. 6-word shingles against the design skills.
  4. Manual side-by-side reading where the tests found hits.
- **Licences:**
  - Where a licence file was installed locally, it was read.
  - Otherwise the licence came from the GitHub API (`/repos/{r}/license`).

## Upstream licences

| Upstream | Licence | Class |
|---|---|---|
| nextlevelbuilder/ui-ux-pro-max-skill (`design-system`, `slides`, `ui-ux-pro-max` skills), commit bc826e2 | MIT, © 2024 Next Level Builder | Compatible: keep + attribute |
| pbakaus/impeccable | Apache-2.0, © 2025 Paul Bakaus. Its NOTICE.md covers only `ios.md`/`android.md`, which we did not use | Compatible: attribute |
| leonxlnx/taste-skill (`high-end-visual-design`) | MIT, © 2026 Leonxlnx | Compatible: attribute |
| zarazhangrui/frontend-slides | MIT | Compatible (no overlap found) |
| ibelick/ui-skills (ui-skills.com Playbook) | MIT | Compatible |
| vercel-labs/web-interface-guidelines | MIT | Compatible |
| antfu/skills (web-design-guidelines) | MIT | Compatible |
| keenthemes/reui (reui.io) | MIT | Compatible |
| cosscom/coss (coss.com/ui) | **AGPL-3.0** | Restrictive. Ideas only; no code was taken (see html-components.md) |
| jakubkrehel/better-ui, rams/rams (cited in polish.md) | **Unknown**: repos not found via API | Unknown. Ideas only, no text overlap found |
| superdesign.dev/design-systems (cited in design-dna.md) | **Unknown** for the site's design.md pages. The superdesigndev/superdesign repo is AGPL-3.0, with some files under a commercial licence | Unknown/restrictive |
| Anthropic `pptx` skill | **Anthropic proprietary**: "may not … Create derivative works … Distribute" | Restrictive: remove or rewrite |
| pptxgenjs 3.12.0 (vendored) | MIT, © 2015-2022 Brent Ely | Compatible: attribute |
| jszip 3.10.2 (vendored) | MIT or GPL-3.0; used under MIT, © 2009-2016 Stuart Knightley, David Duponchel, Franz Buchinger, António Afonso | Compatible: attribute |

## Per-file findings

| File | Origin | Upstream licence | Evidence | Action |
|---|---|---|---|---|
| data/slide-backgrounds.csv | ui-ux-pro-max `design-system/data/slide-backgrounds.csv` | MIT | 11/11 rows byte-identical | KEEP+ATTRIBUTE |
| data/slide-color-logic.csv | same skill, same file name | MIT | 14/14 rows identical | KEEP+ATTRIBUTE |
| data/slide-copy.csv | same | MIT | 26/26 rows identical | KEEP+ATTRIBUTE |
| data/slide-layout-logic.csv | same | MIT | 16/16 rows identical | KEEP+ATTRIBUTE |
| data/slide-layouts.csv | same | MIT | 26/26 rows identical | KEEP+ATTRIBUTE |
| data/slide-typography.csv | same | MIT | 15/15 rows identical | KEEP+ATTRIBUTE |
| data/slide-strategies.csv | same, plus own rows | MIT + own | 16 of 22 rows identical; 6 rows are new (v1.4) | KEEP+ATTRIBUTE |
| data/slide-charts.csv | same, plus own rows | MIT + own | 26 of 31 rows identical; 5 rows are new (v1.4) | KEEP+ATTRIBUTE |
| data/slide-archetypes.csv | Original (corpus study) | n/a | No match in any upstream | KEEP |
| scripts/slide_search_core.py | ui-ux-pro-max `design-system/scripts/slide_search_core.py`, whose BM25 class comes from `ui-ux-pro-max/scripts/core.py` | MIT | 1,527 of 1,616 7-grams shared; 96 exact lines, including the docstring "Slide Search Core - BM25 search engine…" and the `BM25` class | KEEP+ATTRIBUTE |
| scripts/search-slides.py | same skill, `search-slides.py` | MIT | 858 of 989 7-grams shared; 84 exact lines, including the docstring "Slide Search CLI - …" | KEEP+ATTRIBUTE |
| scripts/slide-token-validator.py | Rewritten from the same skill's 35-line validator | MIT (upstream) | 0 shared lines ≥25 chars; only the name and purpose carry over | KEEP+ATTRIBUTE (courtesy) |
| scripts/validate_pptx.py | Original code. Some checks encode facts documented in the Anthropic skill (hex without '#', stacked `outEnd`) | n/a (facts) | No shared lines; function set differs completely from `office/validate.py` | KEEP |
| scripts/deck_thumbnails.py, pptx2pdf.py, deck_edit.py, doctor.py | Original | n/a | Only generic 1–3 shingle hits (`import argparse …`, `tempfile.TemporaryDirectory`) | KEEP |
| scripts/deck_model.py, ingest.py, integrity-check.py, layout-check.py, qa-deck.py, copy-lint.py, storyline-lint.py, trace-check.py | Original | n/a | Only generic hits (import lines, OOXML namespace URIs) | KEEP |
| scripts/__init__.py | Empty file (0 bytes) | n/a | No content | KEEP (it has no copyrightable content), or recreate it empty |
| references/pptx-mode.md | Mixed: own premium layer plus material from the **Anthropic pptx skill** | **Anthropic proprietary** | § "pptxgenjs footguns (from the source skill …)" L52–85 follows Anthropic SKILL.md L31–53 item by item, in the same order, with near-verbatim wording. 21 7-gram hits. See the evidence notes below the table | **REWRITE**: L3–5, L30–38, L52–85, L136–141 |
| references/quality-floor.md | Own synthesis from impeccable `craft-floor`, taste-skill `high-end-visual-design`, and **the Anthropic pptx "Design Ideas / Avoid" list** | Apache-2.0 / MIT / **Anthropic proprietary** | No 7-gram hits, but some items are close paraphrases of Anthropic SKILL.md L90–167, in the same selection and order. 6 short hits against impeccable, e.g. "Section numbers (01 / 02 / 03) unless …" and "more space above a heading than below it". See the evidence notes below the table | **REWRITE** the Anthropic-derived items (listed below). KEEP+ATTRIBUTE the rest (impeccable, taste-skill) |
| references/html-mode.md | Own, with the layout table condensed from the ui-ux-pro-max `slides` skill (`layout-patterns.md`), micro-rules from the ui-skills Playbook, and Chart.js CDN snippet | MIT | Layout table is an adaptation: same pattern names ("Two-column split (1fr 1fr, 48px gap)", "Big-number hero", "Metrics row"). The only 7-gram hits are the Chart.js CDN URL. 0 hits against playbook.ts or vercel command.md | KEEP+ATTRIBUTE |
| references/polish.md | Rules distilled from the ui-skills Playbook, better-ui, rams, and Vercel WIG | MIT / unknown (better-ui, rams) | 0 7-gram hits against playbook.ts, baseline-ui, vercel command.md. better-ui and rams text could not be retrieved; no overlap test possible for them | KEEP. Keep the in-file citations as credit; NOTICE credit for the MIT sources |
| references/html-components.md | Own plain-CSS recipes inspired by reui.io (React/Tailwind) and the coss.com/ui Meter | reui MIT; **coss AGPL-3.0** | Recipes are plain CSS on our tokens; no shared code (2 generic hits: `grid-template-columns: repeat(3, 1fr)`). The Meter "pattern" is only a label/value/track layout idea | KEEP. Change L12–13 wording from "Adapted from" to "Pattern ideas from", so it is clear no AGPL code was copied |
| references/design-dna.md | Adapted from superdesign.dev "design.md" pages (L3: "extracted from superdesign.dev/design-systems") | **Unknown** (site pages; repo AGPL-3.0 + commercial) | The pages are JS-rendered and could not be fetched, so overlap is **unverified**. The file says the content was "extracted" | **REWRITE the prose** (Character / Guardrails / Deck-fit bullets, ~110 lines) unless a manual side-by-side with each page shows own wording. Hex values, font names and motion timings are facts and can stay. Drop "extracted" wording at L3 and L173 |
| references/storyline.md, consulting-grammar.md, banking-pitchbook.md, finance-charts.md, register-dna.md, partner-review.md | Original (own corpus study, `research/`) | n/a | 0 hits | KEEP |
| references/executive-writing.md | Original. Cites designsystemchecklist.com, ASD-STE100, and Vercel WIG `Intl.*` rules as sources of ideas | MIT (WIG); ideas only | 0 hits | KEEP |
| references/frameworks.md | Original summary of standard consulting frameworks (general knowledge) | n/a | 0 hits | KEEP |
| templates/lib/deck-kit.js, build-deck.js, build-consulting.js, build-pitchbook.js | Original | n/a | 0 hits against pptx, slides, frontend-slides | KEEP |
| templates/*.schema.json, deck-kit.schema.json, *.sample.json | Original (fictional sample data) | n/a | 0 hits | KEEP |
| templates/lib/vendor/README.md | Original | n/a | n/a | KEEP |
| templates/lib/vendor/node_modules/pptxgenjs/** | pptxgenjs 3.12.0 dist, unmodified | MIT | LICENSE ships beside it | KEEP+ATTRIBUTE |
| templates/lib/vendor/node_modules/jszip/** | jszip 3.10.2 dist, unmodified | MIT (dual MIT/GPL-3.0) | LICENSE.markdown ships beside it | KEEP+ATTRIBUTE |

### Evidence notes for the two REWRITE rows

The quoted overlaps are omitted here so that this file does not reproduce the
upstream text. In summary: `pptx-mode.md` L3–5, L31–38, L52–85, and L136–141
followed the Anthropic pptx skill's SKILL.md (its pptxgenjs pitfalls, safe
fonts, and QA sections) item by item, with 21 exact 7-word matches.
`quality-floor.md` L23, L34, L40–42, L47, L63–72, L90–91, and L136–137 followed
its design "avoid" list and type/spacing table in the same selection and
order. All of these passages were rewritten before the 1.0.0 release.

## Draft NOTICE file body

```
deck-studio
Copyright (c) 2026 Olu O

This product is licensed under the MIT License (see LICENSE). It includes or
adapts the third-party material listed below. Each item keeps its original
licence; the full licence texts are in the licenses/ directory.

------------------------------------------------------------------------------
1. UI UX Pro Max skill (design-system and slides skills)
   https://github.com/nextlevelbuilder/ui-ux-pro-max-skill  (commit bc826e2)
   Copyright (c) 2024 Next Level Builder
   Licence: MIT (licenses/ui-ux-pro-max-skill-MIT.txt)

   Included, with modifications:
     skills/premium-decks/data/slide-backgrounds.csv, slide-color-logic.csv,
       slide-copy.csv, slide-layout-logic.csv, slide-layouts.csv,
       slide-typography.csv (unmodified)
     skills/premium-decks/data/slide-strategies.csv, slide-charts.csv
       (upstream rows unmodified; rows added by deck-studio)
     skills/premium-decks/scripts/slide_search_core.py,
       skills/premium-decks/scripts/search-slides.py (modified: archetype
       domain, lint fixes)
     skills/premium-decks/scripts/slide-token-validator.py (rewritten from the
       upstream validator of the same name)
   Adapted: the layout-pattern table in
     skills/premium-decks/references/html-mode.md

------------------------------------------------------------------------------
2. Impeccable
   https://github.com/pbakaus/impeccable
   Copyright 2025 Paul Bakaus
   Licence: Apache License 2.0 (licenses/impeccable-Apache-2.0.txt)
   Design rules in skills/premium-decks/references/quality-floor.md are
   informed by Impeccable's reference/craft-floor.md, restated in
   deck-studio's own words.

------------------------------------------------------------------------------
3. taste-skill (high-end-visual-design)
   https://github.com/leonxlnx/taste-skill
   Copyright (c) 2026 Leonxlnx
   Licence: MIT (licenses/taste-skill-MIT.txt)
   Design rules in skills/premium-decks/references/quality-floor.md are
   informed by this skill, restated in deck-studio's own words.

------------------------------------------------------------------------------
4. PptxGenJS 3.12.0 (vendored, unmodified)
   skills/premium-decks/templates/lib/vendor/node_modules/pptxgenjs/
   Copyright (c) 2015-2022 Brent Ely
   Licence: MIT (pptxgenjs/LICENSE)

5. JSZip 3.10.2 (vendored, unmodified)
   skills/premium-decks/templates/lib/vendor/node_modules/jszip/
   Copyright (c) 2009-2016 Stuart Knightley, David Duponchel,
   Franz Buchinger, António Afonso
   Licence: dual MIT / GPL-3.0-or-later; used and redistributed under MIT
   (jszip/LICENSE.markdown)

------------------------------------------------------------------------------
Acknowledgements (ideas and guidelines only; no text or code copied)
   - UI Skills Playbook, https://github.com/ibelick/ui-skills (MIT)
   - Vercel Web Interface Guidelines,
     https://github.com/vercel-labs/web-interface-guidelines (MIT),
     via antfu/skills web-design-guidelines (MIT)
   - ReUI component patterns, https://reui.io (MIT)
   - Design System Checklist, https://designsystemchecklist.com
   Product names (Linear, Apple, Anthropic, Railway, Cursor, Wise, Framer) in
   references/design-dna.md are used descriptively. No logos, brand assets,
   or fonts from those companies ship with this product.
```

Ship with the NOTICE: a top-level `LICENSE` (MIT) and a `licenses/` folder
holding the MIT text of ui-ux-pro-max-skill and taste-skill, and the Apache-2.0
text for impeccable. The pptxgenjs and jszip licence texts already ship beside
their dist files. Neither `LICENSE`, `NOTICE`, nor `licenses/` exists in the
repository today.

## REWRITE work items

| # | File | Lines to rewrite | Size | What to do |
|---|---|---|---|---|
| 1 | references/pptx-mode.md | L52–85, the pptxgenjs footguns | ~34 lines | Re-derive every rule from the pptxgenjs docs and issues, or from own eval failures. Write new wording, grouped by our own taxonomy (colour, text, charts, shapes, output); do not follow Anthropic's order. Drop "(from the source skill …)" from the heading. Cite pptxgenjs docs or issues, never the Anthropic skill. Keep the rules that come from our own evals (valign, `barDir` ordering, the vendored require path) |
| 2 | references/pptx-mode.md | L3–5 | 3 lines | Replace "helper scripts … come unchanged from the Anthropic pptx skill" with a description of our own scripts |
| 3 | references/pptx-mode.md | L30–38, the safe-font and shadow bullets | ~9 lines | Rebuild the safe-font list from our own render tests (LibreOffice metric-compatible faces), in new wording. Restate the "fresh object per call" point in our own words |
| 4 | references/pptx-mode.md | L136–141, the QA prose | ~6 lines | Rewrite the "check overflow first / regenerate the PDF" wording |
| 5 | references/quality-floor.md | L23, L34, L40–42, L47 (banned list) | ~7 lines | Rewrite the Aptos, cream, accent-line, edge-stripe and centred-body items in new wording. Where possible, justify them from `research/corpus-findings.md` or eval findings |
| 6 | references/quality-floor.md | L63–72, Required 2/3/5 (60–70% dominance, 36–44/20–24/14–16/10–12/60–72pt scale, 0.5"/0.3–0.5" spacing) | ~10 lines | Replace the Anthropic table with our own scale, derived from the corpus study (the register table at L117 already does this for consulting and banking). Restate spacing as our own grid rule |
| 7 | references/quality-floor.md | L90–91 (Required 10), L99–101 (motif), L136–137 (overflow check item) | ~7 lines | Reword |
| 8 | references/design-dna.md | Prose in all 7 DNA sections (Character, Guardrails, Deck fit), plus L3–4 and L173–175 | ~110 lines (0 if the side-by-side check passes) | First open each superdesign.dev page in a browser and compare. If any sentence matches, rewrite it in our own words from public observation of each product. Keep hex values, font names, and timings (these are facts). Remove "extracted" and the instruction to fetch the pages |
| 9 | references/html-components.md | L12–13 | 2 lines | Change the wording to "pattern ideas from reui.io (MIT); meter layout idea from coss.com/ui". Do not import coss (AGPL-3.0) code in future |

Total: about 78 lines of certain rewrite (items 1–7 and 9), plus up to about 110
lines in design-dna.md depending on the verification in item 8.

## Inconsistencies in PROVENANCE.md (fix before release)

- It states the project licence is **Apache-2.0**. The release is planned as **MIT**. The licence must be chosen once and stated the same way in PROVENANCE, README, pyproject and LICENSE.
- It says `NOTICE` and `licenses/` exist. Neither exists, and there is no top-level `LICENSE` either.
- It says the `pptx-mode.md` footguns were "rewritten in our own words for the public branch". On `main` they have not been,.
- It says `quality-floor.md` is distilled only from impeccable and taste-skill. It also carries items from the Anthropic pptx skill's Design Ideas / Avoid list (see items 5–7).
- It does not mention the unknown or restrictive sources: superdesign.dev (design-dna), coss.com (AGPL), better-ui, and rams.
- `scripts/doctor.py` and `scripts/deck_edit.py` are not listed. Both are original (KEEP).
