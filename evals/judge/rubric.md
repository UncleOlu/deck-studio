# Deck rubric — used by the blind judge (Phase 5)

The judge sees rendered slide images only (plus the governing ask from the
case prompt). It does not know which skill version made the deck. Score each
dimension 1–5 using the anchors. A score of 3 is competent work. A score of 5
is what a top consulting or banking team would send without further edits.
Anchors are calibrated against Olu's grades (`evals/judge/calibration.md`).

| Dimension | 1 | 3 | 5 |
|---|---|---|---|
| **Storyline** | Topic order, answer missing or last | Answer present; sections follow but some titles restate facts | Answer on slide 2; titles alone tell a complete, MECE argument |
| **Synthesis** | Titles are labels ("Labour overview") | Titles state facts ("Shrink is 3.4%") | Titles state implications with numbers ("Fixing Express markdowns is worth $19M, the largest shrink lever") |
| **Framework fit** | Charts chosen for variety; wrong form for the data | Reasonable forms; some decorative | Every visual is the form that answers that slide's question (bridge for change, football field for value, 2×2 for priority) |
| **Page grammar** | No unit lines, no sources, inconsistent positions | Most pages sourced; minor drift | Every page: action title, unit line where numeric, source line, tracker/page number, consistent positions |
| **Data integrity** | Numbers conflict across slides or do not add up | Numbers consistent; some untraced or unexplained | Every number consistent, sums hold, conflicts in the inputs resolved and disclosed |
| **Visual quality** | Default Office look, clutter, overflow | Clean, a few crowded pages | Restrained palette, accent only on the datum, generous whitespace, no overflow |
| **Decision-readiness** | Reader cannot tell what to decide | The ask is present but vague | The decision, owner, date, and value at stake are explicit |

Return JSON: one integer per dimension, plus a ≤40-word rationale naming the
weakest slide.

## Discrimination test (grammar and storyline only)

The judge sees a shuffled set of single slides. Half are from generated
decks; half are from real hold-out corpus decks, cropped to remove logos and
client names. For each slide it answers "generated" or "real", with a
confidence from 1 to 5. The target is judge accuracy ≤ 65% on
**page grammar and storyline** cues. A judge that can tell our slides apart
only by content domain has not found a grammar defect. The judge explains
each "generated" call, and those explanations become the defect list.
