# Coder protocol — deck deconstruction (codebook v3)

Used by every coding agent. The codebook is `coding-schema.json`, which sits
next to this file.

## Input

For one deck you get:

- `sample.json`: the page count and the sampled page numbers;
- `sheets/sheet-NN.jpg`: 2×2 contact sheets, each cell labelled `PAGE n`;
- `pages/page-NNN.jpg`: every page, for a closer look when a cell is too
  small to read;
- `text.txt`: the extracted text, where one exists (EDGAR books are
  image-only).

## Procedure

1. Read every contact sheet. For **deck-level** fields you may also open
   other pages:
   - Find the exec summary by opening pages 2–6.
   - Find the appendix by searching `text.txt` for "Appendix", or by opening
     the pages around 70–85% of the deck.
2. Code **one slide record per sampled page**, in page order. Code only what
   is visible. Do not infer intent.
3. Use `other` / `none` rather than forcing a fit. Use the archetype that
   matches the page's **main** content block.
4. `title_is_assertion`: true only for a full-sentence claim that states a
   finding. Examples:
   - "Premiums paid have held near 27% since 2004" → true.
   - "Premiums Paid Over Time" → false.
   - A question → false.
   - The cover, agenda, dividers, and disclaimers → false.
   - A sentence about method, not a finding ("We built a forecast model")
     → false.
5. **Which line is the title.** Use the page-specific headline. A running
   section name printed above it is navigation: code it as
   `navigation_system: breadcrumb-text` and `has_tracker: true`. Do not count
   it in `title_words`.
   `title_words` counts whitespace-separated tokens of that headline and
   excludes the unit line.
6. `accent_on_one_datum`: true only when one highlight colour singles out
   the datum that carries the point, and everything else is neutral or
   secondary.
7. v3 archetypes: `credentials` (league table or tombstones of past deals),
   `structure-chart` (ownership or legal-entity diagram), `company-profile`
   (one-page profile of a buyer or counterparty), `redacted` (the content is
   blacked out).
8. `advisor_or_firm_on_cover`: copy the name exactly as printed. Write
   `none` if there is none.

## Output

- Write exactly one JSON file, valid against `coding-schema.json`, to the
  path you are given.
- `coder` is your coder label.
- Add no keys and no commentary.
- Never copy slide text into the record beyond counts and enums. The records
  store conventions, not content.
