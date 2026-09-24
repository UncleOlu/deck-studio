# Gap audit — designsystemchecklist.com vs. `references/quality-floor.md`

Run for deck-studio v1.3.0 (2026-08-26). Source:
https://designsystemchecklist.com — content read from
`src/translations/en/{designLanguage,designFoundations,maintenance,components}.js`
in https://github.com/ardakaracizmeli/design-system-checklist (branch `master`).

Verdicts: **covered** — the floor already enforces it. **N/A** — the item is a
design-system-maintenance or app-chrome concern that a one-off deck cannot
have. **GAP** — worth closing.

## Design language (10 items)

| Item | Verdict |
|---|---|
| Brand · vision, design principles, brand assets | N/A — the deck adopts the subject's brand; `design-dna.md` + floor rule 12 pick a direction per deck |
| Brand · tone of voice | covered — `executive-writing.md` |
| Brand · terminology | covered — ASD-STE100 rule 5 (one term for one thing) |
| Guidelines · accessibility | covered — floor Required 9 (contrast) |
| Guidelines · writing guidelines, microcopy | covered — `executive-writing.md` + `copy-lint.py` |
| Guidelines · terminology | covered — as above |
| Guidelines · internationalisation | N/A — single-language decks |

## Foundations (26 items)

| Item | Verdict |
|---|---|
| Color · accessibility (AA pairings) | covered — Required 9 |
| Color · semantic colors | covered — Required 2 (≤5 colors, each with a role) |
| Color · dark mode | N/A — a deck commits to one ground; `design-dna.md` carries dark and light profiles |
| Color · guidelines (how *not* to use) | covered — banned defaults + per-DNA guardrails |
| Layout · units, grid, spacing | covered — Required 5 |
| Layout · breakpoints | N/A — fixed 16:9; QA already renders at two sizes |
| Typography · responsiveness | covered — `clamp()` type scale in `html-mode.md` |
| Typography · readability (tracking, leading, measure) | **GAP** — the floor sets sizes but not line-height, tracking, or line length |
| Typography · performance (fallbacks) | covered — `html-mode.md` requires real fallback stacks |
| Typography · grid relation (icon bounding boxes) | **GAP** — folded into the icon rule below |
| Typography · guidelines | covered — Required 4 (state the pairing) |
| Elevation · shadows (3–4 levels) | **GAP** — the floor requires *soft* shadows but defines no scale |
| Elevation · background colors linked per level | **GAP** — same |
| Elevation · z-index | N/A — slides are single-layer |
| Motion · easing, duration | covered — banned easings + `design-dna.md` motion values |
| Motion · accessibility (reduced motion) | covered — `html-mode.md` requires the guard |
| Iconography · style (one family, one variant) | **GAP** — the floor never mentions icons |
| Iconography · accessibility (accessible name) | **GAP** — closed in `html-mode.md` (`aria-label` on nav controls) |
| Iconography · naming, keywords, reserved icons, guidelines | N/A — library-maintenance concerns |

## Core components (skim — deck-shaped only)

- **Table** — not in the checklist. Recipe added in `html-components.md`.
- **Tooltip** — positioning/timeout/keyboard are N/A on a static slide. The
  useful residue (annotate the datum directly) is already floor Required 8.
- **Progress bar** — `c-progress-label` ("always provide a visible label")
  applied to the KPI attainment recipe: the track never appears without a
  label and a target value.
- **Badge** — `c-badge-colors` (one predefined colour per role) is Required 2.
- All other components are app chrome. Ignored.

## Maintenance (28 items)

Distilled into the plugin-root `README.md` **Maintenance** section: release
cycle, changelog discipline, when to bump, and the reinstall sequence.

## Changes applied (3 checklist items, the cap)

1. Required 7 extended into a **three-level elevation scale**, each level
   pairing one shadow recipe with one surface colour.
2. New Required 14: **icon set discipline** — one family, one stroke weight
   matched to text weight, outline default, bounding box on the spacing grid.
3. `executive-writing.md` **Numbers** section extended with formatting
   consistency (one precision per metric family, one unit style, tabular
   alignment, en dash for ranges).

Pre-flight checklist gained exactly three lines: numeric formatting, icon
consistency, and the HTML keyboard/focus path. Readability (line-height,
tracking, measure) went into `html-mode.md` micro-rules and `polish.md` rather
than the checklist, to keep the checklist runnable against rendered images.
