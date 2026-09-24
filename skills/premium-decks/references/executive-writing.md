# Executive Writing

Executives have little time. Every slide must give its conclusion first and
earn every word after it. Write all deck copy with the rules below. They apply
to both modes.

## Takeaway first (assertion-evidence)

- The slide title is a complete sentence that states the finding.
  Write "Unit cost fell 18% after route consolidation", not "Cost update".
- The body proves the title. If the body does not support the title, change one
  of them.
- The first slide after the cover states the recommendation or the main
  conclusion. Do not save it for the end.
- Each slide answers one question the audience has. Name that question before
  you write the slide. Delete slides that answer no question.

## ASD-STE100 style rules

Apply Simplified Technical English as much as possible:

1. Use the active voice. Write "We reduced transit time", not "Transit time was
   reduced".
2. Keep instructions to 20 words or fewer. Keep descriptive sentences to 25
   words or fewer.
3. Give one instruction or one fact per sentence.
4. Keep paragraphs to 6 sentences or fewer. One topic per paragraph.
5. Use one term for one thing through the whole deck. Do not alternate between
   "customer", "client", and "account" for the same entity.
6. Use a verb to express an action. Do not hide the action in a noun. Write
   "we will decide", not "a decision will be made".
7. Use simple present or past tense where possible. Avoid stacked modals
   ("could potentially begin to").
8. Start warnings and asks with the action: "Approve the budget by March 1."

## Banned language

- Dramatic clichés and framing devices: "the gap is not closing, it's
  widening", "X is dead, meet Y", "now more than ever", "at an inflection
  point", "a perfect storm", "game-changer", "paradigm shift".
- Metaphors and hyperbole: "explosive growth", "skyrocketing", "crushing it",
  "10x mindset", "north star" (as a metaphor), "journey", "unlock",
  "supercharge", "revolutionary", "cutting-edge".
- Vague intensifiers: "very", "significantly", "dramatically", "massive" —
  replace each with the number. "Revenue grew 34%" beats "revenue grew
  dramatically".
- Rhetorical questions as titles. State the answer instead.
- Filler openers: "In today's fast-paced world", "As we all know".

Describe facts literally and let the numbers carry the weight. If a claim has
no number, either find the number or mark the claim as an estimate.

## Numbers

- Round to the precision the decision needs: "$4.2M", not "$4,218,377.42".
- Give every number a comparison: prior period, target, or benchmark.
  A number without a reference point is not information.
- Maximum ~3 numbers per slide unless the slide is a table or dashboard the
  audience will study.
- State the source and date of external figures in a caption.

**Format every number the same way through the deck.**
(Sources: the Foundations items at https://designsystemchecklist.com, and the
`Intl.*` rules in the Vercel Web Interface Guidelines fetched by
`antfu/web-design-guidelines` at https://ui-skills.com.)

- One precision per metric family. If one revenue figure is `$4.2M`, every
  revenue figure is one decimal. Do not mix `$4.2M` and `$4,180,000`.
- One unit style. Pick `%` or "percent", `M` or "million", and keep it.
- Right-align numeric columns and set them tabular, so the decimal points line
  up down the column and a figure does not change width between slides.
- En dash for ranges (`Q1–Q3`, `12–18 months`), not a hyphen. A non-breaking
  space between a number and its unit (`14 days`, `$4.2M ARR`) so the pair
  never breaks across a line.
- One date format deck-wide (`30 Sep 2026`, not `9/30/26` on the next slide).
  When code computes a figure at render time, format it with
  `Intl.NumberFormat` / `Intl.DateTimeFormat` rather than by hand.

## Persuasion structure (use literally, not dramatically)

The copywriting formulas in `data/slide-copy.csv` (PAS, AIDA, FAB,
Before-After-Bridge) define slide ORDER and content selection. Use them for
structure. Do not use their promotional tone. A "problem" slide states the
problem with numbers; it does not agitate with adjectives.

Standard executive deck order (adapt as needed):
1. Title: subject, audience, date.
2. Recommendation or main conclusion, with the 2–3 numbers that justify it.
3. Situation: the facts, measured.
4. Options or analysis: what was considered, with trade-offs quantified.
5. The ask: decision needed, owner, and date.

## Self-check before delivery

Read every slide aloud once. For each sentence ask: does an executive need
this sentence to make the decision? Delete it if the answer is no.
