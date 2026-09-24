# Storyline — from a fact base to a ghost deck

Read this for the `consulting` and `banking` registers before you design
anything. A deck is an argument first and a layout second. This file turns
`brief/facts.jsonl` into a ghost deck that the user approves before you build.

Method sources: Barbara Minto, *The Pyramid Principle* (situation–complication–
question–answer, vertical and horizontal logic); the issue-tree and
hypothesis-driven practice described in public MBB training material; and the
corpus study in `research/corpus-findings.md`, which measured how real client
and banker decks apply these ideas.

## 1. Frame the governing question

Write one sentence: **"Should/how/what [decision-maker] [decision] by
[date/constraint]?"** Take it from the user's ask and the brief. Examples:

- "How can Harvest Lane add 150 bps of EBIT margin in 24 months without store
  closures?"
- "Is $41.50 per share a fair price for Ashgrove's unaffiliated holders?"

If you cannot write it, ask the user one question. Do not guess the decision.

## 2. Resolve the fact base first

Open `brief/conflicts.md`. For each pair, pick the value that the more
authoritative source gives. Prefer a system extract over a note, and a
filed or audited figure over an estimate. Record the choice in one line in
`brief/decisions.md`. Tell the user about each conflict in your final message.
Read `brief/sources.md` and mark every file that is irrelevant to the question.
Do not use those files.

## 3. Build the issue tree (MECE)

Break the question into 2–4 branches that are **mutually exclusive and
collectively exhaustive**:

- **Tests:** no item (cost line, customer, cause) belongs to two branches, and
  the branches together cover the whole parent. One fact may support several
  branches; one item may not sit in two.
- **Driver trees** for "how much" questions: profit = price × volume − cost, and
  margin = profit ÷ revenue (a rate, not an amount).
  Split each cost into rate × quantity.
- **Hypothesis trees** for "should we" questions. Each branch is a claim that
  must be true for the answer to hold, such as: the market is big enough, we
  can win, and it pays back.
- Stop splitting when a branch maps to an analysis you can show on one slide.

## 4. Synthesise: the "so what" ladder

For every analysis, climb three rungs. Put only the top rung in the title.

| Rung | Question | Example |
|---|---|---|
| Fact | What does the data say? | Express stores lose 3.4% of sales to shrink |
| So what | Why does it matter? | That is 1.0 pt above the peer median, a $19M a year gap at retail value |
| Now what | What should the reader do or believe? | Fix Express markdown timing first: it is 0.6 pt of the gap, the largest share |

A title that only states the fact is a **summary**, not a synthesis. Reject it.
A title that states an action with no evidence on the page is an **assertion
without support**. Reject that too.

## 5. Structure: answer first

- **Consulting:** use situation → complication → resolution, told answer
  first. The exec summary sits at slide 2 (at the latest slide 3). It is the
  whole pyramid in one page: the governing answer, then 3–5 supporting
  arguments, each with its key number. Every later section proves one
  argument, in the same order.
- **Banking board book:** the fixed analysis sequence is expected. Its order
  is:
  1. situation overview;
  2. valuation summary (football field);
  3. the analyses: trading comps, precedents, DCF, and premia;
  4. appendix.

  The valuation summary is the answer page and sits by slide 3. See
  `banking-pitchbook.md`.
- **SteerCo update:** status, then decisions needed, then detail. The
  decisions go on slide 2, and the RAG detail follows.
- **Data gaps never become the story.** Answer with what the data supports,
  state the assumption in a note on the page where it matters, and list the
  gaps in the appendix and your hand-over message. Never build main-body
  pages such as "Analyses pending further information", "Open data items",
  or cards that say "Not performed": blind judges scored those decks 2 of 5
  on synthesis and decision-readiness. On slides, name the business source
  ("Management projections, June 2026"), never the builder's inputs ("the
  file", "the workbook", "data not provided"). `storyline-lint.py` fails both.

## 6. Write the ghost deck

Produce `brief/ghost-deck.md` before any slide code:

```
# Governing question: <one sentence>
# Answer: <one sentence>
| # | Action title (the finding, ≤ register limit) | Framework / chart | Evidence (fact ids) | Section |
|---|---|---|---|---|
| 1 | Cover | — | — | — |
| 2 | Executive summary: <answer> | dot-dash text | F0027, F0031 | — |
| 3 | <argument 1 as a sentence> | waterfall | F0027, F0033 | 1 Labour |
```

Pick each slide's framework from `frameworks.md` by *the question the slide
answers*, not by variety.

## 7. Test the logic

- **Horizontal logic:** read the titles alone, top to bottom
  (`storyline-lint.py --titles`). They must read as a complete argument that a
  busy executive can accept without opening a single chart. If a gap appears,
  a slide is missing. If two titles say the same thing, merge them.
- **Vertical logic:** each body proves its own title and nothing else. If the
  evidence supports a weaker claim, weaken the title.
- **Red team:** run the partner review in `partner-review.md` on the ghost
  deck. Fix every "must fix" before the user sees it.

## 8. Checkpoint

Show the user the ghost deck: the governing question, the answer, the
numbered titles with their frameworks, and the conflicts you resolved. Wait
for approval. Skip the wait only when the user has said to proceed without
checkpoints. Record that in `brief/decisions.md`.

## 9. Keep the trace

Every number you put on a slide comes from a fact id. Cite the ids in that
slide's speaker notes, e.g. `Revenue $4.82B [F0027]`. A computed figure gets
a `calc:` line the checker can recompute (arithmetic and `SUM`/`AVERAGE`/
`MEDIAN`/`MIN`/`MAX`, not prose), and a figure you chose goes on an `assume:`
line: `assume: 15 bps (margin target per lever)` then
`calc: $7.2M = 15 bps x $4.82B [F0027]`. `trace-check.py` fails wrong
arithmetic and untraced numbers, and warns on numbers it can only see cited.
