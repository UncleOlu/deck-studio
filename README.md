# deck-studio

A Claude Code plugin with one skill, **premium-decks**. It turns source files
(spreadsheets, PDFs, notes) into editable executive decks with documented
sources, checked calculations, and an explicit review report, as a
client-editable `.pptx` or a self-contained HTML deck.

- **Three registers.** *Keynote* for talks and all-hands, *consulting* for
  diagnostics and SteerCo updates (answer-first storylines, action titles), and
  *banking* for board books and strategic-alternatives books.
- **Numbers are verified, not just cited.** The folder is ingested into a fact
  base. A figure counts as verified when it matches a cited fact whose metric
  the slide names, or when its `calc:` line recomputes correctly from sourced
  inputs. Wrong arithmetic fails, and figures that are only cited are listed as
  warnings.
- **An explicit review report.** Storyline lint, number verification,
  arithmetic integrity (waterfalls, totals, one value per metric), layout
  collisions, copy lint, and a render check each report PASS, WARN, SKIP, or
  FAIL. The report says when checks were skipped, and that the visual review is
  yours to do.

## Install

```bash
claude plugin marketplace add UncleOlu/deck-studio
claude plugin install deck-studio@deck-studio
```

Then check the machine: `python3 skills/premium-decks/scripts/doctor.py` in the
installed plugin prints what is missing and how to fix it, and
`doctor.py --install` installs the pinned Python packages. Requirements:
Python ≥ 3.9, Node ≥ 18 (pptxgenjs is vendored), and for visual QA a renderer
(LibreOffice on any OS, or PowerPoint or Keynote on macOS).

## 60-second demo

```text
> The folder ./q3-review holds our cost data and the peer benchmarks.
  Build the SteerCo deck on the margin gap, with the decisions we need.
```

The skill ingests the folder, flags conflicting values, proposes a storyline
and ghost deck for approval, builds the `.pptx` from its kit, and runs the QA
gate (`scripts/qa-deck.py`). Worked examples, built end to end from fictional
inputs, are in `skills/premium-decks/samples/`:

| Sample | Register | Built from |
|---|---|---|
| `alder-vale-margin-diagnostic` | consulting | `samples/source/alder-vale-hotels/` |
| `corvane-special-committee-book` | banking (board book) | `samples/source/corvane-instruments/` |
| `halden-strategic-alternatives` | banking (strategic alternatives) | `samples/source/halden-freight/` |
| `northlane-pitch`, `ridgeline-card-cost.html` | keynote | hand-written briefs |

## Before and after

The same fictional SteerCo brief, built by two internal pre-release builds:
v1.3.3 (left) and v1.4 (right), which added the consulting register: action titles, a tracker, sources named as
business documents rather than files, and a decisions page by slide 3. Blind
judges preferred the v1.4 build on this case, but across all seven eval cases they were
split (overall mean 4.02 for both), and they could still tell every generated
slide from a real one; see `evals/reports/`.

| v1.3.3 | v1.4 |
|---|---|
| ![v1.3.3 SteerCo deck](docs/gallery/steerco-before-v1.3.3.jpg) | ![v1.4 SteerCo deck](docs/gallery/steerco-after-v1.4.jpg) |

| Consulting sample | Board-book sample |
|---|---|
| ![Alder Vale margin diagnostic](docs/gallery/alder-vale-consulting.jpg) | ![Corvane special committee book](docs/gallery/corvane-board-book.jpg) |

## Methodology

The consulting and banking rules come from a coded study of public decks:
131 consulting and banking decks (95 coded, 28 held out for a blind
discrimination test), plus 8 banker discussion books from SEC filings for the
strategic-alternatives recipe. Every rule records its support and what was
rejected. See `research/corpus-findings.md`, `research/pitchbook-findings.md`,
and `research/corpus-sources.md` (source URLs only; the decks themselves are
never redistributed). Evals live in `evals/`: seven deck-building cases, six
trigger cases, an objective scorer, a blind judge, and a protocol for an
independent review study (`evals/review/`) that measures time to approval,
revision rounds, and numbers corrected.

Internal builds before 1.0.0 were numbered 1.x–2.0.x and never published;
the eval reports use those numbers as labels.

## Layout

```
skills/premium-decks/
  SKILL.md       routing (mode × register), workflow, QA order
  references/    storyline, frameworks, consulting and banking grammar, finance charts,
                 quality floor, design DNA, PPTX and HTML mode, HTML components and finance
  scripts/       ingest, qa-deck (runs every check), storyline-lint, trace-check,
                 integrity-check, layout-check, validate_pptx, deck_edit, doctor, …
  templates/     the deck kit (pptxgenjs, vendored) and the register builders
  samples/       worked examples; build_samples.py rebuilds the ingest-path samples
research/        the corpus study behind the registers
evals/           eval cases, harvest, objective scorer, blind judge
tests/           pytest suite for the scripts
docs/history/    plans and audits from earlier releases
```

## Development

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt pytest ruff jsonschema
.venv/bin/python -m pytest -q
.venv/bin/ruff check .
```

`CONTRIBUTING.md` covers versioning, the changelog rules, and how to run the
evals. Report security issues as described in `SECURITY.md`.

## Licence

MIT (`LICENSE`), by Olu. Third-party material and its licences are listed in
`NOTICE` and `PROVENANCE.md`.
