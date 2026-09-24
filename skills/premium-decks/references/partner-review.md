# Partner review — red-team the deck before the user sees it

Run this twice. The first pass is on the ghost deck (`brief/ghost-deck.md`),
before any build. The second is on the rendered images, after QA. When a
subagent is available, give the review to a fresh one: it must not have seen
your reasoning. Hand it this file, the ghost deck or images, `brief/facts.jsonl`,
and `brief/decisions.md`. It returns a list of findings, each marked
**must fix** or **consider**. Fix every must-fix, re-render, and repeat until
none remain.

The questions below are the ones a senior partner or managing director asks
in a real review. Each question names the failure it catches.

## Pass 1 — the argument (ghost deck)

1. **What is the answer?** Can you say it in one sentence from slide 2 alone?
   (Catches: a buried answer.)
2. **Does it answer the question the client asked?** Compare the answer with
   the governing question. (Catches: answering an easier question.)
3. **Read only the titles. Is the argument complete and in order?** (Catches:
   missing steps and repeated points.)
4. **Is each title a synthesis or only a fact?** "Shrink is 3.4%" is only a
   fact. (Catches: summary instead of insight.)
5. **Are the branches MECE?** Could one item (a cost line, a customer, a cause) sit in two sections? Is a whole
   category missing? (Catches: overlap and gaps.)
6. **What is the strongest objection the client will raise, and which slide
   answers it?** (Catches: an unaddressed counter-argument.)
7. **Is every recommendation actionable?** Each one needs an owner, a first
   step, a date, and the value at stake. (Catches: advice nobody can act on.)
8. **Which conflicts in the data did we resolve, and would the client agree
   with each choice?** (Catches: silent data choices.)

## Pass 2 — the page (rendered images)

9. **Does each chart prove its title?** Cover the title. Would a reader draw
   the same conclusion from the chart? (Catches: a chart that does not
   support its title.)
10. **Where does the eye land first on each page?** It must land on the datum
    in the title. (Catches: the accent colour on the wrong element.)
11. **Is every number sourced, and does every number match?** Check that a
    metric keeps one value across slides and that the units are stated.
    (Catches: trace and consistency defects that the scripts missed.)
12. **Is anything on the page not needed for the decision?** Delete it.
    (Catches: clutter and data dumps.)
13. **Would this page survive being printed in black and white and read
    without the presenter?** (Catches: colour-only meaning and missing
    labels.)
14. **Does the deck look like one author made it?** Check title positions,
    fonts, tracker, and footers. (Catches: drift.)
15. **What would embarrass us if the client's CFO checked it?** Look at
    arithmetic, dates, names, and the client's own numbers quoted back
    wrongly. (Catches: credibility killers.)

## Output format

```
PASS <1|2> — <n> must fix, <m> consider
[must fix] slide 4 · Q9 · Chart shows cost per store; title claims cost per hour.
[consider] slide 7 · Q12 · Remove the third callout; it repeats the title.
```
