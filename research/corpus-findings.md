# Corpus findings — how consulting and banking decks are built

The evidence behind the `consulting` and `banking` registers. Every rule the
skill adopted from this study appears in the **rule ledger** below, with the
statistic behind it. Full tables are in `corpus-stats.md`, which is
generated. The sources are listed in `corpus-sources.md`. Coder agreement is in
`agreement.md`.

## Method

1. **Corpus.** 131 public decks, collected 2026-09-22:
   - 65 banker board books (SEC EDGAR EX-99.(c) exhibits from all 12 sampled
     advisors, plus public copies of such exhibits);
   - 19 consulting client deliverables;
   - 26 public-sector client deliverables (published by the client body);
   - 21 decks the firms published themselves.

   No banker *pitch* books were available from free public sources. See
   Limitations.
2. **Hold-out.** About 20% of decks (28), chosen by content hash, were never
   coded and never used to derive a rule. They exist only for the blind
   discrimination test (`evals/judge/rubric.md`). The rule depends only on
   each file's hash, so decks added later never moved in or out.
3. **Sampling.** For each deck, pages 1–4 plus evenly spaced pages, 12 in
   total, rendered as labelled contact sheets. The deck-level fields could
   use any page.
4. **Codebook.** `coding-schema.json`: 15 deck-level and 16 slide-level
   fields.
   - **v1:** piloted on 6 decks by two independent coders. κ was 0.87 for
     archetype, 1.00 for chart type, and 1.00 for assertion titles.
   - **v2:** revised from the pilot notes. The main change fixed which line
     counts as the title when a running section header sits above it.
   - **v3:** added four page types that batch 2 surfaced (credentials,
     structure chart, company profile, redacted page). Every earlier record
     stays valid under v3.
5. **Coding.** Thirteen primary coders coded the 95-deck derive set (1,137
   sampled pages) in three batches.
   - Two decks were unreadable, because their EDGAR images carry no text
     layer. They are excluded.
   - Independent coders double-coded 15 decks (16%). Every gated κ is at
     least 0.70; the values are in `agreement.md`.
   - Text density is reported for information only; no rule relies on it.
6. **Saturation.** Batch 2 (26 board books) surfaced the four page types
   that v3 added. Batch 3, the next 9 readable board books, added no new
   archetype and never needed "other". The page-type vocabulary is saturated
   for board books. The plan's test was 10 decks; the 10th was unreadable.
7. **Coders are LLM agents** reading page images. Agreement between
   independent agents shows the codebook is applied consistently. It does not
   prove the codes match a human expert's; see Limitations.

## Findings

Content slides only: cover, agenda, divider, disclaimer, and appendix are
excluded. *MBB-client* is the McKinsey/BCG/Bain subset of client
deliverables (14 decks, 130 content slides), used as the best-practice
benchmark. Banking figures come from 48 coded board books (366 content
slides).

1. **Consultants write action titles; bankers do not.**
   - Assertion titles: 56% of MBB-client titles and 45% of all client
     titles, but **4% of banking titles**.
   - Board books use neutral topic labels: a median of 5 words, p95 10
     ("Premiums Paid Over Time"). That fits their role: a fairness analysis
     presents; it does not persuade.
2. **Action titles are sentences of about 14 words.** Client assertion
   titles run to a median of 14 words (IQR 10–17, p90 20). 97% of client
   titles fit on at most 2 lines.
3. **Most decks have an exec summary, but many bury it.**
   - An exec summary appears in 79% of MBB-client decks, 74% of client decks,
     and 71% of banking decks (a banker's summary of analyses counts). Its
     median page is 6.
   - In the sampled pages, only 7 of 23 client exec summaries were preceded
     by front matter alone. The rest sit after context or content pages.
4. **The answer-first storyline dominates consulting; a fixed analysis
   sequence dominates banking.**
   - Client decks: answer-first SCR 13, pyramid-grouped 5,
     analysis-sequence 5.
   - Banking: analysis-sequence 40 of 48.
   - The dot-dash text list is the modal consulting exec summary form.
5. **Sources are common; bankers source nearly everything.**
   - A source line appears on 87% of banking chart/table slides, against
     62% for MBB-client and 53% for client decks.
   - Numbered notes plus a source line is the footnote system in 44 of 48
     banking decks and in 10 of 14 MBB decks.
6. **Unit lines are a banking habit.** A unit line under the title appears
   on 39% of banking content slides and 45% of banking chart/table slides,
   against 8–10% of consulting slides. Consultants label units inside the
   chart.
7. **Navigation.** A tracker or breadcrumb appears on 35–40% of content
   slides.
   - MBB decks favour a repeated agenda with the current section
     highlighted (8 of 14) as the divider device.
   - Banking uses title-only divider pages (34 of 48) and a text breadcrumb
     (18 of 48).
8. **Sans-serif titles are universal.** Titles are sans in all 14 MBB-client
   decks and in 45 of 48 banking decks.
9. **Restrained colour.** The median is 3–3.5 meaningful hues. Banking
   primaries are navy (30 of 48) or blue (13 of 48).
10. **Consulting pages are denser than keynote pages.**
    - 43% of MBB-client content slides carry high text density (>120 words).
    - The text-structured page is the most common MBB archetype (18%).
    - Content blocks: median 2.5, p90 5.
11. **The single-datum accent is rarer than the quality floor demands.**
    One highlight colour on the datum that carries the point appears on 22%
    of MBB-client chart slides and 13% of banking chart slides.
12. **Bankers mark the answer with highlight boxes and label every book.**
    - Highlight boxes appear on 43% of banking content slides.
    - 39 of 48 books carry a confidentiality or draft label.
13. **The chart vocabulary is narrow.**
    - MBB-client: tables 13%, vertical bars 12%, waterfalls 7%, stacked bars
      5%, lines 5%.
    - Banking: tables 44%, lines 17% (share-price and multiple histories),
      vertical bars 12%, plus football fields and comps and sensitivity
      tables.

## Rule ledger

Decisions: **adopt** (the skill enforces it), **adopt-stricter** (the rule
exceeds corpus practice on purpose; the reason is given), **reject**.

| # | Proposed rule | Evidence | Decision |
|---|---|---|---|
| R1 | Consulting titles are action titles | Finding 1: 56% MBB-client | **adopt-stricter**: 100% of content slides. The best decks do it; the misses are the weak pages. `storyline-lint` |
| R2 | Consulting action titles ≤ 20 words, ≤ 2 lines | Finding 2: p90 20 words; 97% ≤ 2 lines | **adopt**: `storyline-lint` limit 20 |
| R3 | Banking titles may be neutral topic labels, ≤ 12 words | Finding 1: 4% assertions (n=366), median 5, p95 10 | **adopt, amended after the v1.4 blind eval**: banking skips the assertion test and a bare label stays legal (limit 12), but the recommended form is a label plus the factual finding, never a judgment, held to R2's 20 words. Judges scored label-only books lower on synthesis |
| R4 | Exec summary first, at or before slide 3 (after any disclaimer) | Finding 3: present in 71–79%, but first in only 7/23 client decks | **adopt-stricter**: answer-first is the Pyramid Principle standard. Burying it is the commonest corpus weakness. `storyline-lint` |
| R5 | Chart/table slides carry an on-slide source line | Finding 5: banking 87%, MBB 62% | **adopt** for consulting and banking. Keynote may source in the notes |
| R6 | Numbered notes plus source line as the footnote system | Finding 5: 44/48 banking, 10/14 MBB | **adopt**: `integrity-check` checks marker order and resolution |
| R7 | Unit line under the title on numeric slides | Finding 6: banking 45% of chart slides, consulting 8–10% | **adopt for banking** (warning); **reject for consulting**: label units in the chart |
| R8 | Tracker or agenda-highlight dividers for decks with ≥ 3 sections | Finding 7: 35–40% of content slides; agenda-highlight 8/14 MBB | **adopt** as recommended. `storyline-lint` checks tracker order when present |
| R9 | Sans-serif titles allowed (overrides the "characterful display face" default) | Finding 8: 14/14 MBB, 45/48 banking | **adopt** as a register override. Consulting/banking may use a sober sans title (e.g. Arial Bold) |
| R10 | Dense text pages allowed when structured (bold lead-ins, ≤ 5 blocks) | Finding 10: 43% high density, p90 5 blocks | **adopt** as a register override of the bullet-wall ban, with structure required |
| R11 | Accent on the one datum that carries the point | Finding 11: 22% MBB, 13% banking | **adopt-stricter**: keep quality-floor Required 8. Low corpus compliance is a weakness to beat, not a norm to copy |
| R12 | Waterfall, football field, comps, sensitivity, Harvey balls, Marimekko as native recipes | Finding 13 | **adopt**: `finance-charts.md`, `templates/lib/deck-kit.js` |
| R13 | "So-what" takeaway box on every slide | 12% MBB, 4% banking | **reject** as a requirement: the action title carries the so-what. The box is optional emphasis |
| R14 | 4:3 or Letter page size | 45/48 board books and most client decks are 4:3 or Letter, but the corpus leans to 2010–2020 | **reject**: keep 16:9 (the modern Office default). 4:3 on request |
| R15 | Firm-specific palettes (e.g. a green primary) | Finding 9 | **reject**: never imitate a firm's brand. The register DNAs use a generic navy/ink system |
| R16 | Confidentiality label on banking books | Finding 12: 39/48 | **adopt**: `build-pitchbook.js` defaults the label to "Confidential" |

## Limitations

- **Few true pitch books.** Banks do not publish mandate pitches. The
  closest public material, 8 banker discussion books on strategic
  alternatives and sale processes (SEC EX-99.(c)), is coded separately in
  `pitchbook-findings.md` and drives the sell-side recipe. Only one of the 8
  competes for a mandate, so "why us" pages rest on thin evidence.
- **Selection bias.**
  - Public-sector deliverables and firm-published decks are what is public.
    Private client decks are under-represented.
  - Several decks share a client: 3 USPS decks and several banker books on
    the same deals.
  - The EDGAR sample is capped at 5 books per advisor, which evens out the
    banks but repeats some deals.
  - Page size and density norms lean older.
- **LLM coders.** Agreement measures consistency, not accuracy. Olu's
  calibration grading (Phase 5) anchors the rubric judge to a human expert.
- **Sampling.** Twelve pages per deck. Exec summary position and appendix
  share come from deck-level reading, not from the sample alone.
