# deck-studio v1.3 improvement plan (for Claude Opus 5)

Execute this plan in a Claude Code session. It upgrades the deck-studio
plugin (skill: premium-decks) using four external resources. Work top to
bottom. Every phase has a verification gate — do not skip gates.

## Context (read first)

- Plugin source of truth: `~/claude-plugins/deck-studio/` (skills/premium-decks/).
  Edit HERE. The install cache and the `~/.agents/skills/premium-decks` symlink
  derive from it.
- Current version: 1.2.0. This plan produces 1.3.0.
- Read before editing: `skills/premium-decks/SKILL.md`, all files in
  `references/`, and memory file
  the maintainer's local memory notes.
- The skill builds executive .pptx (Mode A) and HTML decks (Mode B).
  The four resources below are web-UI-centric. Your job is to TRANSLATE
  what applies to slides and REJECT what does not. Every rule you add must
  name its deck application. "Nothing worth taking" is an acceptable,
  documented outcome for any resource.

## Hard constraints

1. Do not resurrect board-deck as a separate skill (Olu rejected it; it lives
   on only as `templates/build-deck.js` inside premium-decks).
2. SKILL.md stays under 300 lines; put detail in `references/`. Each new or
   extended reference stays under ~150 lines.
3. Do not modify `scripts/` copied from the Anthropic pptx skill
   (thumbnail, add_slide, clean, office/*). Own scripts (copy-lint, pptx2pdf)
   may be extended if a phase needs it.
4. Do not weaken the PPTX safe-font system or the executive-writing rules.
   Write all new guidance in the same ASD-STE100 style the skill enforces.
5. `references/design-dna.md` (v1.2 work) is done — extend only if a resource
   supplies concrete new token data, never rewrite it.
6. External sites are read-only sources. Cite each source URL in the file
   that uses its material.

## Phase 1 — extract from the four resources

### 1a. ui-skills.com (highest value)

A catalog of installable UI agent-skills plus a "Playbook" of concrete
micro-rules. WebFetch returns 403 on it — use the browser pane
(`preview_start {url}` → `get_page_text`).

- Read the full Playbook (https://ui-skills.com → "See playbook"). Already
  confirmed present: `aspect-ratio` to prevent layout shift, `text-balance`
  for headings / `text-pretty` for body, `tabular-nums` for data alignment,
  44px touch targets. Collect the rest.
- Fold the deck-applicable rules into `references/html-mode.md` (deck shell
  requirements): at minimum `tabular-nums` on all chart/data numbers,
  `text-wrap: balance` on slide titles, `aspect-ratio` on media boxes,
  ≥44px hit area for deck nav controls. Judge the rest.
- From the catalog, read (do not install wholesale) these skill pages:
  `better-ui` (jakubkrehel), `web-design-guidelines` (antfu), `rams`.
  Distill deck-relevant polish rules — optical alignment, border/shadow
  interplay, focus states, spacing rhythm — into a NEW
  `references/polish.md` (<120 lines), split into "HTML mode" and
  "both modes" sections. Skip anything already covered by quality-floor.md.

### 1b. designsystemchecklist.com

Open-source checklist: Design language (10 items), Foundations (26),
Core components (166), Maintenance (28). The site is JS-rendered — use the
browser, or read the source data from the project's GitHub (linked via
"Contribute").

- Walk Design language + Foundations item by item against
  `references/quality-floor.md`. Produce a written gap list first; then apply
  only gaps that matter for decks. Expected gaps worth closing: focus-visible
  and keyboard coverage for HTML decks beyond arrow keys, an explicit
  elevation/shadow scale (one recipe per level), icon consistency
  (single family, single stroke weight), number/date formatting consistency
  (feeds `executive-writing.md` Numbers section — tabular alignment,
  one precision per metric family).
- Core components: skim only for the handful that map to deck elements
  (table, tooltip-as-annotation, progress). Ignore app chrome (forms,
  dialogs, navigation).
- Maintenance section: distill into a short "Maintenance" section in the
  plugin root `README.md` (create it): versioning, changelog discipline,
  when to bump, how to reinstall. Include the known trap: plain
  `claude plugin update deck-studio` fails for this local plugin — the
  working sequence is
  `claude plugin marketplace update <marketplace>` →
  `claude plugin uninstall deck-studio@<marketplace>` →
  `claude plugin install deck-studio@<marketplace>`.

### 1c. reui.io/components

1100+ open-source shadcn/React/Tailwind components; 19 custom ones include
Timeline, Stepper, Gantt, Data Grid, Event Calendar, Charts (recharts).

- Target the deck-shaped ones only: Timeline, Stepper, Gantt, Data Grid,
  chart styling. Read each component's rendered look and structure.
- Produce `references/html-components.md` (<150 lines): 4–6 copy-adaptable
  slide-component recipes in plain CSS using the skill's three-layer tokens
  (NO Tailwind, no React — self-contained HTML/CSS): process/stepper row,
  roadmap gantt bars, dense data table (hairline rules, tabular-nums,
  right-aligned numerics), annotated metric/KPI row, timeline. Each recipe
  ≤25 lines of CSS+HTML sketch plus 2–3 usage rules.
- These fill a real gap: roadmap and process slides currently have only the
  pptx timeline pattern.

### 1d. coss.com/ui (lowest value — timebox hard)

Base-UI component library ("for developers and AI"). Skim for visual
conventions the deck shell could borrow (empty states, toolbar spacing,
kbd styling for shortcut hints). If nothing translates to slides, write one
line in the changelog saying so and move on. Do not force content in.

## Phase 2 — integrate

- Wire new/extended references into `SKILL.md`: one line each in the Mode B
  section (html-components.md) and the QA/quality-floor section (polish.md).
  Keep the routing table and workflow structure unchanged.
- Update `references/quality-floor.md` pre-flight checklist with any new
  REQUIRED items (focus-visible, tabular-nums, icon consistency) — add at
  most 3 checklist lines; the checklist must stay runnable, not aspirational.
- Cross-check: no rule added in Phase 1 contradicts design-dna.md guardrails
  or the banned-defaults list. Resolve conflicts in favor of the existing
  floor and note the decision in the changelog.

## Phase 3 — verify (gate)

1. Build ONE sample HTML deck slide-set exercising the new recipes: a 4-slide
   mini deck (title, roadmap gantt slide, process stepper slide, dense data
   table slide) using one design-dna profile not used by the last deck
   (last used: custom espresso/amber; before that burgundy/gold). Screenshot
   each slide in the browser at 1280×720; run
   `scripts/copy-lint.py` on the HTML; run the quality-floor pre-flight
   including the NEW checklist items.
2. Re-validate existing artifacts still pass:
   `scripts/office/validate.py` on `samples/northlane-pitch.pptx`
   (needs Python ≥3.10: `/opt/homebrew/bin/python3.12` venv — see SKILL.md
   dependency table).
3. Dispatch a fresh subagent to review the new sample screenshots against the
   updated checklist. Fix findings, re-render, and only then proceed.
4. Save the mini deck into `samples/` (replace nothing; add alongside).

## Phase 4 — release

1. Bump `.claude-plugin/plugin.json` to 1.3.0; append a `CHANGELOG.md` entry
   in the plugin root listing: what each resource contributed, what was
   rejected and why (one line each).
2. Reinstall using the working sequence from 1b; delete the stale
   `~/.claude/plugins/cache/<marketplace>/deck-studio/1.2.0` directory after the
   new install verifies; confirm
   `~/.claude/plugins/cache/<marketplace>/deck-studio/1.3.0/skills/premium-decks/references/`
   contains the new files.
3. Confirm `~/.agents/skills/premium-decks/references/` shows them too
   (symlink to source — no action expected, just verify).
4. Update memory: the maintainer's local memory notes
   (version, new references, which DNA the new sample used) and the
   deck-skills line in `MEMORY.md`.
5. Run the `chief-of-staff` audit agent (available in the Agent tool) over
   the completed work as the final gate. Address must-fix findings before
   reporting done.

## Acceptance criteria

- [ ] Playbook micro-rules present in html-mode.md with deck applications named
- [ ] `references/polish.md` exists, <120 lines, no overlap with quality-floor
- [ ] `references/html-components.md` exists with 4–6 token-based recipes
- [ ] Quality-floor gap audit written down; ≤3 new checklist items applied
- [ ] Plugin-root README.md has the Maintenance section with the reinstall trap
- [ ] New 4-slide HTML sample in samples/, screenshots QA'd by a fresh subagent
- [ ] Existing pptx sample still validates
- [ ] v1.3.0 installed, cache clean, symlink verified, memory updated
- [ ] CHANGELOG.md records contributions AND rejections per resource
- [ ] chief-of-staff audit run; must-fix findings resolved

Sources: https://ui-skills.com · https://designsystemchecklist.com ·
https://reui.io/components · https://coss.com/ui
