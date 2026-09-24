# Frameworks — pick by the question the slide answers

Read this while you write the ghost deck (`storyline.md` §6). Choose a
framework because it answers the slide's question. Never choose one for
variety. Each row names the chart or diagram to build. Recipes for the finance
charts are in `finance-charts.md`.

## Selection table

| The slide answers… | Framework | Build as | Preconditions | Misuse to avoid |
|---|---|---|---|---|
| What drives this number? | **Driver tree** | left-to-right tree, value on each node | Arithmetic identity holds (children add, multiply, or divide to the parent; show the operator on each node) | Branches that overlap; a tree with no numbers |
| How did we get from A to B? | **Waterfall bridge** | stacked bar, invisible base | Steps sum exactly to the change | More than ~8 steps; mixing periods |
| Where is the money made? | **Profit pool** | variable-width bar (width = revenue, height = margin) | Segment revenue and margin known | Using it for one segment |
| How big is each segment, and who wins it? | **Marimekko** | 100% stacked, width = segment size | Share data for every segment | Fewer than 3 segments |
| Which options are best? | **Options × criteria** | table with Harvey balls, one recommended row highlighted | Criteria weighted or ranked; options exclusive | Criteria that restate each other |
| What should we do first? | **Prioritisation 2×2** | scatter, value vs. ease, bubbles sized by a third variable (cost, revenue at stake) | Both axes scored the same way for all items | Items crowded in one quadrant (the axes are wrong) |
| Where do we stand against peers? | **Benchmark bar** | sorted horizontal bar, us highlighted, median line | Like-for-like definitions | Peers chosen to flatter |
| How does it work end to end? | **Value chain / process** | chevrons or stepper, one metric per step | Steps are sequential | Using it for a non-sequence |
| When does what happen? | **Phased roadmap** | gantt bars by workstream, milestones as markers | Dates and owners known | More than ~6 workstreams on one page |
| How sensitive is the answer? | **Sensitivity grid / tornado** | heat-table (2 variables) or tornado (many) | A model that produces the output | Ranges that are not realistic |
| What is it worth? | **Football field** | horizontal range bars by method, offer line | At least 3 valuation methods | Ranges without stated assumptions |
| Is the status on track? | **RAG tracker** | table: workstream, RAG, % complete, next milestone | Consistent RAG definitions stated in a footnote | RAG with no explanation for red/amber |

## Rules

1. **One framework per slide.** Two frameworks mean the slide has two
   ideas. Split it (quality-floor Required 1).
2. **The title states what the framework shows.** The title of a 2×2 names
   the quadrant that matters. The title of a waterfall names the largest
   step. The title of a football field states where the offer falls.
3. **Label the framework's key element in the accent colour.** That is the
   recommended option row, the chosen quadrant, or the largest bridge step.
   Everything else stays neutral (Required 8).
4. **MECE is visible.** When a tree or bridge claims to be complete, its parts
   recombine exactly to the whole: they sum in a bridge or additive tree, and
   multiply or divide otherwise. Express a margin bridge in bps of revenue.
   `integrity-check.py` tests bridge and table arithmetic.
5. **Orient every criterion so more is better.** Write "Guest experience
   protected", not "Guest impact (low is good)": a full Harvey ball must
   always mean "good", or the recommended row reads as the worst.
6. **Frameworks are not decoration.** Use a generic diagram (pyramid,
   circle of arrows, jigsaw) only when its structure carries meaning. Otherwise
   use a table or a chart.

## Consulting archetypes by section (corpus frequencies in `research/corpus-findings.md`)

- **Opening:** exec summary (dot-dash or numbered findings), the situation in
  one chart.
- **Diagnosis:** benchmark bar, driver tree, waterfall, a map for footprint
  questions.
- **Options:** options × criteria, 2×2, sensitivity.
- **Plan:** phased roadmap, RAG tracker, and next steps with owner and date.
