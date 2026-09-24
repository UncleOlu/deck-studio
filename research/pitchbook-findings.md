# Pitch-book findings: banker discussion materials and strategic-alternatives books

This study fills the gap noted in `corpus-findings.md` (Limitations: "No pitch books"). It covers 8
public banker decks from SEC EDGAR EX-99.(c) exhibits. Each is an early-stage book that was
never a fairness book: preliminary discussion materials, strategic-alternatives reviews, a sale-process
kick-off, and a pitch-style book from an advisor to a buyer. Collected and coded 2026-09-23.

## Sources

| # | Bank | Company | Date | Exhibit | Pages | Deck type | Filing URL |
|---|---|---|---|---|---|---|---|
| P1 | Goldman Sachs | Covetrus | 2021-12-09 | (c)(6) | 38 | strategic-alternatives discussion materials | <https://www.sec.gov/Archives/edgar/data/1752836/000119312522213042/d377047dex99c6.htm> |
| P2 | Goldman Sachs / Lincoln Intl | Covetrus | 2021-12 | (c)(7) | 15 | sale-process kick-off materials | <https://www.sec.gov/Archives/edgar/data/1752836/000119312522213042/d377047dex99c7.htm> |
| P3 | J.P. Morgan | Dell | 2012-09-14 | (c)(29) | 44 | first special-committee presentation (feasibility, alternatives, process) | <https://www.sec.gov/Archives/edgar/data/826083/000119312513134621/d505474dex99c29.htm> |
| P4 | Evercore | Dell | 2013-01-15 | (c)(13) | 27 | special-committee presentation (valuation, self-help alternatives, go-shop) | <https://www.sec.gov/Archives/edgar/data/826083/000119312513228037/d505474dex99c13.htm> |
| P5 | Citigroup | Sauer-Danfoss (client: Danfoss) | 2012-11-26 | (c)(2) | 75 | pitch-style discussion materials to a buyer (why Citi, process, valuation, credentials) | <https://www.sec.gov/Archives/edgar/data/865754/000110465913028452/a13-7427_15ex99dc2.htm> |
| P6 | Jefferies | Franchise Group | 2023-04 | (c)(1) | 49 | preliminary materials for discussion (situation, valuation, divestiture, next steps) | <https://www.sec.gov/Archives/edgar/data/1528930/000110465923078458/tm2317758d5_ex-c1.htm> |
| P7 | Morgan Stanley | KnowBe4 | 2022-07-28 | (c)(iii) | 33 | special-committee process update and considerations | <https://www.sec.gov/Archives/edgar/data/1664998/000119312522307513/d323857dex99ciii.htm> |
| P8 | Lazard | Urovant Sciences | 2020-10 | (c)(7) | 16 | special-committee kick-off (valuation approach, timeline, tactics) | <https://www.sec.gov/Archives/edgar/data/1740547/000119312521048264/d22741dex99c7.htm> |

- **How they were found:** EDGAR full-text search over SC 13E3 / SC 13E3/A / SC TO-T filings for
  pitch phrases ("illustrative process timeline", "buyer universe", "potential counterparties",
  "strategic alternatives" + "discussion materials", "buyer outreach"). Each exhibit's page text
  was then read to classify it.
- **Rejected candidates:**
  - Books already in the corpus (Endeavor/Centerview, Astra/PJT, Focus/Moelis, Cornerstone/Jefferies).
  - Pure conflicts-committee valuation books (Teekay/Evercore).
  - Books with no bank named on the cover (Pardes).
  - Books under 12 pages (Qatalyst/AspenTech, Centerview/Clearwire).
- **Counts:** 7 banks. Covetrus and Dell each appear twice, which is within the corpus cap of 2
  books per company.
- **Local files:** page images are in `~/deck-corpus/edgar/<id>/` and renders in
  `~/deck-corpus/renders/edgar/<id>/`. The manifest is `~/deck-corpus/manifest-pitch.jsonl`
  (genre `banking-pitch`, kept separate so `aggregate.py` board-book stats are unchanged). Coding
  records are in `~/deck-corpus/coding-pitch/c14/`. The corpus lives outside the repo, as
  `edgar_fetch.py` already does; `tools/corpus/` holds only scripts and has no ignore rule for data.

## Method

- **Codebook:** v3 (`coding-schema.json`) with no changes. Sampling as in `render.py`: pages 1–4 plus
  evenly spaced pages, 12 per deck. That gives 96 sampled pages, of which 64 are content slides
  (49 carry a chart or table).
- **Coding:** one coder (c14, an LLM agent). No double-coding was done, so there is no κ. Treat the
  slide-level percentages as indicative.
- **Full-deck inventory:** the pitch-specific page counts below come from reading every page of
  every deck, not the sample. EDGAR exhibits carry a per-page text layer, and I checked key pages
  visually.
- **Rule format:** "k/8" is the number of decks that show the feature at least once. Every count is
  over these 8 decks only.

## Slide-level comparison with board books (content slides)

| Metric | Pitch set (n=64 slides, 8 decks) | Board books (corpus-stats, n=366) |
|---|---|---|
| Assertion titles | 3% (2/64, both P7) | 4% |
| Title words, median | 5 (max 12) | 5 (p95 10) |
| Unit line under title | 34% | 39% |
| Source line on chart/table slides | 65% (32/49) | 87% |
| Numbered notes | 30% | 46% |
| Takeaway / so-what box | 8% | 4% |
| Tracker on content slides | 56% | 36% |
| Highlight boxes | 25% | 43% |
| High text density | 28% | 31% |
| Accent on one datum (chart slides) | 4% | 13% |

- **Chart vocabulary:** table 22, none 15, line 12, vertical bar 6, pie 2, gantt 2, football field
  2, area 1, horizontal bar 1, other (funnel) 1.
- **Top archetypes:** chart-multi 16, table-data 9, text-structured 6, org-team 6, chart-single 4,
  timeline-roadmap 3, comps-table 3, redacted 3.

## Rules for a sell-side / strategic-alternatives pitch book

Each rule gives its support as k/8, the pages behind it, and **Δ board**: how the rule differs from
the board-book grammar in `corpus-findings.md`.

1. **End on the process: a timeline page, then a next-steps page. 7/8** have an illustrative
   process timeline (Gantt or phased arrow) keyed to weeks or dates:
   P1 p33, P2 p4–5, P3 p39, P5 p22–23, P6 p42, P7 p7–8, P8 p11. Only P4 has none (its process
   section covers go-shop terms).
   *Δ board:* board books close on valuation; the timeline archetype is absent from the top
   banking archetypes.
2. **Include a buyer universe, tiered and split into strategics vs sponsors. 6/8** name
   potential counterparties:
   - P1 p34–37 and P2 p7 (split by focus, with fund size and rationale);
   - P3 p30–33 (Tier 1/Tier 2 sponsors, then strategics);
   - P4 p24 (strategic acquirers with capacity metrics and commentary);
   - P6 p7 and p41 (outreach funnel; Tier A/B strategics);
   - P7 p5–6 (Tier 1A/1B/2).

   5 of these 6 tier or segment the list. Three decks (P1, P2, P7) redact the names in the public
   filing. *Δ board:* not a board-book page type.
3. **Lay the alternatives side by side before recommending. 4/8** have an options page with
   columns or rows per alternative and merits/considerations or pros/cons:
   - P1 p28: status quo / funded investment case / whole-company sale;
   - P3 p35: process options A/B/C;
   - P4 p19: spin, RMT, IPO, tracking stock, buyback;
   - P5 p15–18: share purchase vs going-private; merger vs tender.

   *Δ board:* options-evaluation is 1% of board-book pages.
4. **State the bank's recommendation in its own voice, near the end. 3/8** have an explicit
   recommendation page:
   - P1 p30–31 "Process Overview & Recommendations" ("GS recommends…");
   - P3 p36 "J.P. Morgan's recommended process";
   - P8 p13 "Preliminary Tactical Recommendations".

   P5 carries the recommendation in the lead sentences instead ("we believe…", p15). Every one
   comes after the analysis. **0/8** put the answer first. *Δ board:* board books present and do
   not recommend. *Δ consulting:* the corpus does not support answer-first for this genre.
5. **Keep the analysis-sequence storyline, but order it situation → valuation → alternatives →
   process.** The coded storyline is analysis-sequence in 5/8 and other in 3/8 (P2 process plan, P5
   pitch, P8 kick-off). In the 7 decks that have both a valuation section and a
   process/alternatives section (all but P2), process/alternatives follows valuation in 5
   (P1, P3, P4, P6, P8). In P5 and P7, process comes first.
6. **Frame the decision with a key-considerations or key-questions page. 5/8** have one:
   P1 p32, P3 p7 and p23, P4 p14, P5 p12–14, P8 p3. These are numbered or boxed text pages.
   *Δ board:* board books rarely carry a text-only framing page (text-structured 6% of banking
   pages).
7. **Titles stay neutral labels of about 5 words.**
   - Assertion titles: 2/64 content slides, both in one deck (P7 p14 and p17, Title Case, chained
     with "…" across pages). Median 5 words.
   - Two decks (P5 Citi, P8 Lazard) put a coloured one-sentence finding directly under the label
     title on most content pages. That is the "label + factual finding" form R3 already recommends.

   *Δ board:* the same as board books. There is no evidence that pitch books switch to consulting
   action titles.
8. **"Why us", credentials, and a named team appear only when the bank is competing for the
   mandate.** Of the 8 decks:
   - 1/8 has a "Why Citi?" page (P5 p5, four ticked reasons);
   - 1/8 has tombstone credentials (P5 p42, grouped by experience type);
   - 2/8 name the team with contacts (P3 p3, P5 p4 and p43);
   - 1/8 has a working-group list (P2 p9–14).

   The 7 books made for an engaged special committee or board carry no "why us" page and no
   tombstones. *Δ board:* credentials are rare in board books too. For a pitch to win a mandate,
   put why-us, team and credentials up front (P5 order: team → why us → market), with fuller
   credentials in the appendix.
9. **Anchor the valuation on the market, then give ranges. 6/8** open the valuation evidence with
   share-price or trading-multiple history (P1, P3, P4, P5, P6, P7). Ranges then appear as:
   - a football field in 4/8 (P4 p20–21, P5 p30, P6 p25, and P8 p4 as an illustrative football
     field with no values);
   - an "analysis at various prices" matrix in 5/8 (P4 p22, P5 p31, P6 p26, P7 p28, P8 p10);
   - premiums or precedent go-private tables in 5/8 (P3 p25, P4 p26–27, P5 p19/35/47–52, P6
     p45–46, P8 p8).

   7/8 label these "Illustrative" or "Preliminary" (P4 uses neither word). *Δ board:* the same
   analyses as board books, but framed as illustrative and usually placed before the process
   section, not as the conclusion.
10. **Stamp the book as a draft, give the target a code name, and put an agenda near the front.**
    - A draft or preliminary label is on 4/8 (P5–P8). The other four are marked only confidential;
      P3 also says "For Discussion Purposes Only".
    - Code names are used in 6/8 (Padlock, Denali ×2, FREEDOM/VICTORY, Orange/Violet,
      Salamander). P1 and P5 use real names.
    - An agenda or table of contents sits at p2–4 in 7/8; P7 opens straight into a section
      divider.

    *Δ board:* the draft label is somewhat commoner than in board books (board: 16 of 48
    draft-type labels).
11. **Navigation is heavier than in board books.**
    - A tracker or section marker appears on 56% of content slides (board 36%).
    - Devices: breadcrumb text in 3/8 (P3 vertical side label, P5 footer, P7 footer), agenda
      repeated with the current item highlighted in 2/8 (P1, P3), a coloured numbered tab in 1/8
      (P8), and a numbered section badge in 1/8 (P2).
12. **Sourcing is looser than in board books.** A source line appears on 65% of chart/table slides
    (board 87%). Numbered notes plus source is the footnote system in 7/8 (P2 has none).
    *Δ board:* keep R5/R6. Pitch material that repeats process or buyer content often drops the
    source line; the rule should still require it for any market data.
13. **Page length and appendix vary.** Page counts are 15–75 (median 35.5). The appendix share
    ranges from 0 (P1, P2, P4) to 0.49 (P5, which appends case studies, SEC rules and a second
    valuation book). Disclaimers go at the back in 5/8 and at the front in 3/8 (P3, P4, P6).

## Differences from the current board-book grammar (summary)

- **Adds these page types:**
  - illustrative process timeline (7/8);
  - tiered buyer universe (6/8);
  - key considerations/questions (5/8);
  - alternatives matrix (4/8);
  - recommendation (3/8);
  - next-steps/roadmap (5/8: P3 p38, P5 p22, P6 p44, P2 p5, P7 p3).
- **Keeps:** neutral topic titles (3% assertions vs 4%), unit lines (34% vs 39%), numbered
  notes plus source, sans titles (6/8; P4 and P8 use serif titles), and navy/blue primaries (8/8).
- **Changes the ending:** process and recommendation close the book. Valuation is the middle act.
- **Does not support** the current recipe's borrowing of consulting answer-first SCR (0/8), or
  "why us"/credentials as standard front matter (1/8, only in the true pitch-for-mandate book).
- **Page size:** 6/8 letter landscape, 2/8 4:3. None is 16:9, which supports keeping R14 as the
  deliberate override.

## Limitations

- **Small sample:** n=8, 7 banks, 2012–2023, and one coder with no κ. The counts are
  existence-in-deck counts, not prevalence estimates.
- **Genre:** these are pitch-*style* books, not true cold pitches to win a mandate. Only P5 comes
  close; the rest were written for an engaged committee. Real banker mandate pitches remain
  unobserved.
- **Redactions:** redacted buyer lists (P1, P2, P7) hide density and naming conventions on those
  pages.
