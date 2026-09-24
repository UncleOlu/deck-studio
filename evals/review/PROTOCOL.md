# Independent review study

The blind judge asks whether a deck *looks* expert-made. This study asks what
matters to a user: how much work a real reviewer needs before the deck is
decision-ready. Run it before claiming any time or quality benefit.

## What is measured

| Measure | How | Why |
|---|---|---|
| Time to approval | reviewer logs active minutes until they would send it | the cost a deck saves or adds |
| Revision rounds | times the reviewer sent it back to the builder | how often the storyline or data was wrong |
| Numbers corrected | `review_diff.py` (text, tables, chart data) | evidence integrity in practice |
| Factual errors found | reviewer's count of wrong claims, not wording | errors the checks missed |
| Structure changed | slides added, removed, moved; titles rewritten | whether the storyline held |
| Editability | charts the reviewer replaced with pictures; reviewer's 1–5 rating of editing effort | the "client-editable" claim |
| Would send | yes / no at the end | the bottom line |

## Design

1. **Reviewers:** at least 5 people who build or approve decks for a living
   (consulting, finance, operations), none involved in deck-studio.
2. **Decks:** each reviewer gets 2–3 recurring analytical decks from real or
   realistic source folders (an operating review, a cost diagnostic, a
   supplier review, a SteerCo update). Use folders the reviewer knows, so they
   can judge the numbers.
3. **Comparison:** for each folder, also time the reviewer's usual way (their
   own draft or a colleague's first draft) where possible. Without a baseline
   the study still measures residual work, but cannot claim time saved.
4. **Blinding:** tell reviewers a draft was prepared for them, not by what.
5. **Procedure, per deck:**
   1. Build the deck with the skill as a user would; keep the builder's QA
      report (`qa-deck.py`) and do not fix anything by hand afterwards.
   2. Save the delivered file as `<deck_id>-delivered.pptx`.
   3. The reviewer edits until they would send it; each time they send it
      back, record a revision round and rebuild from their comments.
   4. Save the result as `<deck_id>-approved.pptx`.
   5. Run `python3 review_diff.py <deck_id>-delivered.pptx <deck_id>-approved.pptx
      --json <deck_id>-diff.json`.
   6. Fill one row of `review-log.csv`.
6. **Summary:** `python3 summarize.py review-log.csv` prints medians and
   ranges per register and overall.

## Reading the results

- Report medians and ranges, not means; with 5–15 decks, say so.
- A deck that needed a number corrected is a failure of the evidence chain,
  whatever the QA report said. List each one with its cause (wrong source,
  wrong calculation, cited but not verified, not in the facts).
- Compare numbers corrected with the deck's QA report: were the corrected
  figures among the "cited but not verified" warnings? If so, the warnings
  work; if not, the checker has a blind spot to fix.
- Do not claim "send without edits". Claim what the data shows, for example
  "median 25 minutes to approval, 0 numbers corrected in 9 of 12 decks".

## Limits

`review_diff.py` matches slides by title; a title rewritten beyond recognition
counts as one slide removed and one added. Check the per-slide JSON when the
structure counts look high.
