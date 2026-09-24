#!/usr/bin/env python3
"""Lint a deck's storyline: action titles, exec summary, sources, tracker.

Checks (per register; limits come from research/corpus-findings.md):
  - every content slide title is an action title: a full sentence with a verb,
    at least MIN_WORDS words, at most the register's word limit, not a question
    (banking: neutral topic labels are the norm, so only the length limit applies)
  - banking: numeric slides carry a unit line such as "($ in millions)" (warning)
  - consulting/banking: the exec summary sits at or before slide 3
  - every slide with a chart or data table carries a source line on the slide
    (keynote register: in the slide or its speaker notes)
  - trackers, when used, name one fixed set of sections in order
  - consulting/banking: no data-gap page ("analyses pending", "not performed")
    in the main story, and no slide text about the builder's inputs ("the
    file", "data not provided"): gaps go to the appendix and the hand-over note
Exempt: the cover, agenda/contents, dividers, disclaimers, and slides after an
"Appendix" divider.

Prints ERROR/WARN lines and exits 1 on any ERROR. --titles prints the title
sequence alone: read it top to bottom; it must tell the whole story.

Usage: python3 storyline-lint.py deck.pptx|deck.html [--register consulting] [--titles]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deck_model  # noqa: E402

# Limits by register. Consulting/banking values come from research/corpus-findings.md
# (rule ledger). Keynote uses ASD-STE100 rule 2 (descriptive sentences <= 25 words).
REGISTERS = {
    "keynote":    {"title_max_words": 25, "exec_by": 0, "source_on_slide": False, "assertion": True,
                   "unit_line": False},
    # R1 action titles, R2 <= 20 words (client p90), R4 exec summary by slide 3, R5 on-slide sources
    "consulting": {"title_max_words": 20, "exec_by": 3, "source_on_slide": True, "assertion": True,
                   "unit_line": False},
    # R3 neutral topic labels allowed, <= 12 words (banking p95 = 11); R5 sources; R7 unit line (warning)
    "banking":    {"title_max_words": 12, "exec_by": 3, "source_on_slide": True, "assertion": False,
                   "unit_line": True},
}
UNIT_LINE = re.compile(r"^\s*\((?=[^)]*(?:[$€£%]|US\$|USD|EUR|GBP|in\s+(?:millions|billions|thousands)|per\s+share))"
                       r"[^)]*\)(?:\s*\(\d+\))*\s*$", re.I | re.M)  # a trailing note marker "(1)" is allowed
MIN_WORDS = 5

BASE_VERBS = """accelerate account achieve add affect allow ask beat become begin bring build buy call capture carry
cause change check choose clear close
come complete concentrate contribute cost cover create cut decide decline deliver depend double drive drop
earn enable end enter exceed expand explain face fall finish fit follow free fund gain generate give go
grow halve hold improve increase keep lag lead leave lift limit lose lower make match meet miss move need
offer outgrow outperform pay peak point price protect provide push put raise reach recover reduce release
remain replace require return rise run save sell shift show shrink sit slip slow spend stall stand start
stay support sustain take trail trigger triple turn underperform vary widen win work yield
act adopt agree apply avoid base break catch compare consider continue convert count differ exist expect
feel fix focus form happen help hire invest know learn let like look mean measure open own pass plan play
prefer prepare prevent produce prove reach read recommend record rely remove report represent resolve rest
review risk scale see seem send serve set share slide solve spread stop suggest switch tell test think
track train treat try understand use wait want watch list trade rank equal outpace remain""".split()
IRREGULAR = """is are was were be been being has have had will would can could should must may might does do did
grew grown fell fallen rose risen won lost led held kept left made paid ran sold spent stood took brought
built bought came cut drove driven gave gone went hit let meant put quit read set shut split spread
understood""".split()


def verb_forms() -> set[str]:
    forms = set(IRREGULAR)
    for v in BASE_VERBS:
        forms.add(v)
        forms.add(v + ("es" if v.endswith(("s", "sh", "ch", "x", "o")) else "s"))
        if v.endswith("y") and v[-2] not in "aeiou":
            forms.update({v[:-1] + "ies", v[:-1] + "ied"})
        forms.add(v + "d" if v.endswith("e") else v + "ed")
        if len(v) > 2 and v[-1] not in "aeiouwxy" and v[-2] in "aeiou" and v[-3] not in "aeiou":
            forms.add(v + v[-1] + "ed")
    return forms


VERBS = verb_forms()
NOT_VERBS = {"unaffected", "hundred", "weighted", "adjusted", "diluted", "combined", "related", "limited",
             "detailed", "selected", "estimated", "projected", "red", "shed", "speed"}
EXEMPT_TITLE = re.compile(r"^(agenda|contents|table of contents|appendix|disclaimer|important (information|notice)|"
                          r"notice|thank you|questions|q&a|next steps)\b", re.I)
EXEC_TITLE = re.compile(r"executive summary|summary of (?:valuation )?(analyses|findings|recommendations)"
                        r"|valuation summary"
                        r"|key (findings|takeaways|messages|considerations|questions)|^summary\b|recommendation", re.I)
# Narrow on purpose: "pending" or "to be confirmed" alone is normal SteerCo language, not a gap page.
GAP_TITLE = re.compile(r"\b(analys[ie]s pending|pending (further )?(data|information)|not performed"
                       r"|open data items|data (gaps|requests?)|information (requests?|needed))\b", re.I)
GAP_BODY = re.compile(r"\bnot performed\b|\banalys[ie]s pending\b|\bpending (further )?(data|information)\b", re.I)
# "Open items" / "to be confirmed" titles are a gap page only when the body says *data* is missing;
# "Awaiting CFO sign-off" or "TSA dates TBC" are ordinary SteerCo items.
SOFT_GAP_TITLE = re.compile(r"\b(open|outstanding) items\b|\bto be confirmed\b|\bTBC\b", re.I)
MISSING_DATA = re.compile(r"\b(data|figures?|numbers|inputs?|information|analys[ie]s)\b[^.\n]{0,40}?"
                          r"\b(not (yet )?(received|available|provided|supplied)|missing|outstanding|to follow"
                          r"|TBC|to be confirmed)\b"
                          r"|\bawaiting (the )?[\w-]*\s?(data|figures?|numbers|inputs?|information)\b"
                          r"|\bpending (further )?(data|information|figures)\b", re.I)
# "the data room" is excluded: a sell-side process page names it legitimately. Any "<noun> file" or
# "<noun> spreadsheet" names the build, not a business source; "master file" is a system of record.
SELF_REF = re.compile(r"\b(the|this|our) (input )?(file|files|workbook|spreadsheet|folder|inputs?)\b"
                      r"|\b(?!(?:master|will|to|must|may|can|could|would|should|shall|did|does)\b)[a-z]+ "
                      r"(file|workbook|spreadsheet)s?\b(?! for\b| its\b| an?\b| the\b)"
                      r"|\b(data|figures?|dataset) (was |were |is |are )?not (provided|supplied|given)\b"
                      r"|\bnot (provided|supplied) in the (materials|inputs?|files?)\b", re.I)
SOURCE_RE = re.compile(r"^\s*(sources?|data|note[s]?)\s*:", re.I | re.M)


def words(title: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9$%€£.,'’&/-]+", title)


def is_divider(slide) -> bool:
    body = re.sub(r"\s+", " ", slide.body_text).strip()
    return len(words(slide.title)) <= 6 and len(body.split()) <= 6 and not slide.has_visual


def claim_lines(slide) -> int:
    """Body lines that read as claims: 6+ words with a verb (an exec summary carries 3 or more)."""
    n = 0
    for line in slide.body_text.splitlines():
        ws = {w.lower().strip(".,:;'’") for w in words(line)}
        if len(ws) >= 6 and ws & VERBS:
            n += 1
    return n


def title_problem(title: str, max_words: int, assertion: bool = True) -> str:
    t = title.strip()
    n = len(words(t))
    if not t:
        return "no title found"
    if t.endswith("?"):
        return "title is a question — state the answer"
    lowered_words = {w.lower().strip(".,:;'’") for w in words(t)}
    if not assertion and (n < 6 or not (lowered_words & VERBS)):
        # A neutral banking label; a banking title that makes a claim is held to the consulting limit (R2).
        return f"{n} words; the register limit is {max_words}" if n > max_words else ""
    if not assertion:
        max_words = REGISTERS["consulting"]["title_max_words"]
    if n < MIN_WORDS:
        return f"topic label, not an action title ({n} words)"
    lowered = {w.lower().strip(".,:;'’") for w in words(t)}
    past = {w for w in lowered if len(w) >= 5 and w.endswith("ed") and w not in NOT_VERBS}
    if not (lowered & VERBS or past):
        return "no verb — a title states a finding as a sentence"
    if n > max_words:
        return f"{n} words; the register limit is {max_words}"
    return ""


def lint(path: str, register: str) -> tuple[list[str], list[str], list[str]]:
    cfg = REGISTERS[register]
    deck = deck_model.load(path)
    errors, warns, titles = [], [], []
    in_appendix = False
    exec_at = 0
    front = 0
    tracker_seq = []
    for s in deck.slides:
        titles.append(f"{s.index:>3}. {s.title or '(no title)'}")
        if s.index == 1:
            continue
        if s.index == len(deck.slides) and not s.title and not s.has_visual:
            continue  # a closing bookend ("Thank you", contact page)
        if re.match(r"^\s*appendix", s.title, re.I):
            in_appendix = True
        if s.title.strip().endswith("?"):
            errors.append(f"ERROR slide {s.index}: title is a question — state the answer: {s.title[:90]!r}")
            continue
        if re.match(r"^\s*(disclaimer|important (information|notice)|notice)\b", s.title, re.I):
            front += 1  # legal pages do not count toward the exec-summary position
        if not exec_at and not in_appendix and (EXEC_TITLE.search(s.title) or (
                s.index - front <= max(cfg["exec_by"], 3) and not title_problem(s.title, 99)
                and claim_lines(s) >= 3)):
            exec_at = s.index - front  # a titled summary page, or an answer title backed by 3+ claims
        legal = bool(re.match(r"^\s*(disclaimer|important (information|notice)|notice)\b", s.title, re.I))
        if register != "keynote" and not legal:
            text = f"{s.title}\n{s.body_text}"
            if SELF_REF.search(text):
                hit = SELF_REF.search(text).group(0)
                (warns if in_appendix else errors).append(
                    f"{'WARN' if in_appendix else 'ERROR'} slide {s.index}: slide text talks about the inputs "
                    f"({hit!r}) — name the business source, and put gaps in the hand-over note")
            soft_gap = SOFT_GAP_TITLE.search(s.title) and MISSING_DATA.search(s.body_text)
            if not in_appendix and (GAP_TITLE.search(s.title) or GAP_BODY.search(s.body_text) or soft_gap):
                errors.append(f"ERROR slide {s.index}: data-gap page in the main story — answer with what the data "
                              f"supports; list gaps in the appendix and the hand-over note: {s.title[:70]!r}")
        if in_appendix or EXEMPT_TITLE.match(s.title) or (is_divider(s) and s.index - front != exec_at):
            continue
        # "Executive summary" as a bare title is the corpus norm; its body carries the assertions.
        problem = "" if s.index - front == exec_at else title_problem(s.title, cfg["title_max_words"], cfg["assertion"])
        if problem:
            errors.append(f"ERROR slide {s.index}: {problem}: {s.title[:90]!r}")
        data_slide = bool(s.charts) or any(len(t.rows) >= 3 for t in s.tables)
        if data_slide:
            on_slide = bool(SOURCE_RE.search(s.body_text))
            in_notes = bool(re.search(r"\bsources?\b|F\d{4}", s.notes, re.I))
            if cfg["source_on_slide"] and not on_slide:
                errors.append(f"ERROR slide {s.index}: chart/table slide has no 'Source:' line on the slide")
            elif not cfg["source_on_slide"] and not (on_slide or in_notes):
                errors.append(f"ERROR slide {s.index}: chart/table slide cites no source (slide or notes)")
            if cfg["unit_line"] and not UNIT_LINE.search(s.body_text):
                warns.append(f"WARN slide {s.index}: numeric slide has no unit line such as '($ in millions)'")
        label = s.tracker
        if label:
            tracker_seq.append((s.index, label))
    if cfg["exec_by"]:
        first_content = next((s for s in deck.slides[1:]
                              if not EXEMPT_TITLE.match(s.title) and not is_divider(s)), None)
        # An answer-first slide 2 counts: the plan's standard order puts the recommendation there.
        if not exec_at and first_content is not None and first_content.index <= cfg["exec_by"] \
                and (re.search(r"recommend|should|we propose|the answer", first_content.title, re.I)
                     or first_content.title.split(" ", 1)[0].lower() in BASE_VERBS):  # an imperative is an answer
            exec_at = first_content.index
        if not exec_at or exec_at > cfg["exec_by"]:
            where = f"slide {exec_at}" if exec_at else "nowhere"
            errors.append(f"ERROR deck: executive summary must sit at or before slide {cfg['exec_by']} "
                          f"(found: {where})")
    if tracker_seq:
        order: list[str] = []
        last = -1
        for idx, label in tracker_seq:
            if label not in order:
                order.append(label)
            pos = order.index(label)
            if pos < last:
                errors.append(f"ERROR slide {idx}: tracker goes back to '{label}' — sections must run in order")
            last = pos
        if len(order) > 7:
            warns.append(f"WARN deck: {len(order)} distinct tracker labels — a tracker names at most ~6 sections")
    return errors, warns, titles


def main() -> int:
    ap = argparse.ArgumentParser(description="Lint a deck's storyline.")
    ap.add_argument("deck")
    ap.add_argument("--register", choices=sorted(REGISTERS), default="consulting")
    ap.add_argument("--titles", action="store_true", help="print the title sequence only")
    args = ap.parse_args()
    errors, warns, titles = lint(args.deck, args.register)
    if args.titles:
        print("\n".join(titles))
        return 0
    for line in errors + warns:
        print(line)
    print(f"storyline-lint ({args.register}): {len(errors)} error(s), {len(warns)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
