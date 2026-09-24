#!/usr/bin/env python3
"""Check that every number on every slide traces to a source, and verify the arithmetic.

Each visible number gets one status:
  verified  it equals a fact the notes cite ("[F0027]") and the slide text names
            that fact's metric; or it is the result of a calc: line whose
            arithmetic checks out and whose inputs are facts or other results
  cited     the notes cite facts for it, but the checker cannot confirm it: the
            value matches a cited fact the slide text does not name, or the
            calc: line has prose or unsourced inputs (a WARNING)
  assumption  it is declared on an "assume:" line in the notes (the author's choice,
            reported separately from facts)
  illustrative  it appears in a deck-data.json marked "illustrative": true
  untraced  nothing supports it (a FAILURE)
  calc-error  it is the result of a calc: line whose arithmetic is wrong (a FAILURE)
Every calc: line is also checked on its own: wrong arithmetic fails even if the
result is not on the slide. See calc_verify.py for the calc: grammar.
Ignored: slide numbers, bare years, dates, period labels (Q1, FY25), footnote
markers, tracker section numbers, and list ordinals.

Exit 1 on any untraced number or calc error; warnings do not fail.
Usage: python3 trace-check.py deck.pptx|deck.html brief/facts.jsonl [--data deck-data.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import calc_verify  # noqa: E402
import deck_model  # noqa: E402
import ingest  # noqa: E402

FACT_ID = re.compile(r"\bF\d{4}\b")
FACT_RANGE = re.compile(r"\bF(\d{4})\s*[-–]\s*F(\d{4})\b")


def cited_ids(notes: str) -> list[str]:
    """Fact ids cited in notes; a range "F0093-F0107" cites every id in it."""
    ids = FACT_ID.findall(notes)
    for a, b in FACT_RANGE.findall(notes):
        lo, hi = int(a), int(b)
        if 0 < hi - lo <= 2000:
            ids += [f"F{i:04d}" for i in range(lo, hi + 1)]
    return list(dict.fromkeys(ids))


def load_facts(path: Path) -> dict[str, ingest.Fact]:
    out = {}
    for line in path.read_text().splitlines():
        if line.strip():
            f = ingest.Fact(**json.loads(line))
            out[f.id] = f
    return out


def illustrative_values(path: Path | None) -> list[float]:
    if not path:
        return []
    data = json.loads(path.read_text())
    if not (isinstance(data, dict) and data.get("illustrative") is True):
        return []
    vals: list[float] = []

    def walk(o: Any) -> None:
        if isinstance(o, bool):
            return
        if isinstance(o, (int, float)):
            vals.append(float(o))
        elif isinstance(o, dict):
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
        elif isinstance(o, str):
            for v, *_ in ingest.numbers_in(o):
                vals.append(v)

    walk(data)
    return vals


# A section label is "N Name" with no other digits; a wrapped strip may start with a bare name or end with a bare
# number. "Pilot Stores 240 · Control Stores 238" is data, not a strip, because its names carry figures.
SEG = r"(?:\d{1,2}\s+)?[A-Z][A-Za-z&'’\- ]{0,30}"
SECTION_STRIP = re.compile(rf"{SEG}(?:\s*·\s*{SEG})*(?:\s*·\s*\d{{1,2}})?")


def slide_numbers(slide: deck_model.Slide) -> list[tuple[str, ingest.Fact]]:
    """Visible figures on the slide as (display string, pseudo-fact)."""
    out: list[tuple[str, ingest.Fact]] = []
    for block in slide.texts:
        if slide.tracker and block.strip() == slide.tracker:
            continue  # section numbers in the tracker are labels
        for line in block.splitlines():
            stripped = line.strip()
            line = re.sub(r"(?:^|(?<=\s))\(\d{1,2}\)(?=\s|$)", "", line)  # footnote markers "(1)"
            line = re.sub(
                r"\b\d{1,2}(?=\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})", "", line
            )  # the day in "15 May 2026" belongs to a date
            if re.fullmatch(r"\d{1,3}", stripped):
                continue  # a lone small integer: page number or footnote marker
            if (
                SECTION_STRIP.fullmatch(stripped)
                and re.search(r"(?:^|·)\s*\d{1,2}\s+[A-Z]", stripped)
                and ("·" in stripped or re.match(r"\d{1,2}\s{2,}[A-Z]", stripped))
            ):
                continue  # section labels: "1 Baseline · 2 Labour", an agenda row "2   Levers", or a wrapped strip
            for v, unit, scale, s, e in ingest.numbers_in(line):
                if re.match(r"^\s*\d{1,2}[.)]\s", line) and s == len(line) - len(line.lstrip()):
                    continue  # list ordinal
                raw = line[s:e].strip()
                out.append((raw, ingest.Fact("S", v, unit, scale, "", ingest.window(line, s, e), "", "")))
    return out


def matches(num: ingest.Fact, fact: ingest.Fact) -> bool:
    if fact.unit == "date" or isinstance(fact.value, str):
        return False
    if num.unit and fact.unit and num.unit != fact.unit and not {num.unit, fact.unit} <= {"USD", "EUR", "GBP", ""}:
        return False
    if num.unit in ("%", "x", "bps") and fact.unit not in (num.unit, ""):
        return False
    for f in (fact, ingest.Fact(fact.id, fact.value, fact.unit, 1.0, "", "", "", "")):
        # Tables often print a fact without its scale word ("4,820" for $4,820M).
        if ingest.same_at_precision(num, f):
            return True
        rescaled = ingest.Fact("S", num.value, num.unit, f.scale, "", "", "", "")
        if num.scale == 1.0 and ingest.same_at_precision(rescaled, f):
            return True
    return False


# usable in an expression without a source: unit conversions and the scale words k / M / bn
CONSTANTS = {1.0, 2.0, 100.0, 1000.0, 1e6, 1e9}


@dataclass
class NumberResult:
    slide: int
    raw: str
    text: str
    status: str  # verified | assumption | cited | illustrative | untraced | calc-error
    detail: str = ""


@dataclass
class CalcResult:
    slide: int
    status: str  # verified | cited | error
    text: str
    detail: str = ""


@dataclass
class Report:
    numbers: list[NumberResult] = field(default_factory=list)
    calcs: list[CalcResult] = field(default_factory=list)
    unknown: list[str] = field(default_factory=list)

    def failures(self) -> list[str]:
        out = list(self.unknown)
        out += [f"CALC ERROR slide {c.slide}: {c.detail} — “{c.text[:90]}”" for c in self.calcs if c.status == "error"]
        out += [
            f"UNTRACED slide {n.slide}: {n.raw!r} in “{n.text[:70]}”" for n in self.numbers if n.status == "untraced"
        ]
        return out

    def warnings(self) -> list[str]:
        return [f"CITED slide {n.slide}: {n.raw!r} — {n.detail}" for n in self.numbers if n.status == "cited"]


def table_context(slide: deck_model.Slide) -> dict[str, str]:
    """Cell text -> its row label and column header, so a bare table figure has words to match."""
    ctx: dict[str, str] = {}
    for t in slide.tables:
        if not t.rows:
            continue
        header = t.rows[0]
        for row in t.rows[1:]:
            ctx.setdefault(row[0].strip(), header[0])  # a row label sits under the corner header ("WACC \\ TGR")
            for c, cell in enumerate(row[1:], start=1):
                head = header[c] if c < len(header) else ""
                ctx.setdefault(cell.strip(), f"{row[0]} {head}")
    return ctx


def names_metric(num: ingest.Fact, fact: ingest.Fact, extra: str, notes: str) -> bool:
    """The slide names the fact's metric, or the note clause that cites the fact binds it to this figure."""
    context = ingest.label_words(f"{num.text} {extra}")
    if context & (ingest.match_words(fact) or ingest.label_words(fact.text)):
        return True
    key = fact.text.partition(" | ")[0]  # a csv row keyed by a date: "2023-03" on the slide as "Mar 2023"
    if {d for d, *_ in ingest.dates_in(key)} & {d for d, *_ in ingest.dates_in(f"{num.text} {extra}")}:
        return True
    for clause in re.split(r"[;\n]|\.\s", notes):
        if fact.id in cited_ids(clause):
            bare = FACT_ID.sub(" ", clause)
            if context & ingest.label_words(bare) or any(
                abs(v - float(num.value)) < 1e-9 for v, *_ in ingest.numbers_in(bare)
            ):
                return True
    return False


def literal_sourced(v: float, cited: list[ingest.Fact], results: list[float], illus: list[float]) -> bool:
    if v in CONSTANTS or any(abs(v - x) < 1e-9 for x in illus):
        return True
    probe = ingest.Fact("S", v, "", 1.0, "", "", "", "")
    if any(
        isinstance(f.value, (int, float))
        and ingest.same_at_precision(probe, ingest.Fact(f.id, f.value, "", 1.0, "", "", "", ""))
        for f in cited
    ):
        return True
    return any(calc_verify.close(r, v, v) for r in results)


def check_report(deck_path: str, facts_path: str, data_path: str | None) -> Report:
    deck = deck_model.load(deck_path)
    facts = load_facts(Path(facts_path))
    illus = illustrative_values(Path(data_path) if data_path else None)
    report = Report()
    # 1. arithmetic of every calc: segment, deck-wide
    arith: list[tuple[deck_model.Slide, calc_verify.Result]] = []
    for s in deck.slides:
        for seg in calc_verify.segments(s.notes):
            arith.append((s, calc_verify.check_arithmetic(seg, facts)))
    results = [r.segment.lhs_value for _, r in arith if r.status == "ok"]
    assumed = {s.index: calc_verify.assumptions(s.notes) for s in deck.slides}
    # 2. a correct segment is verified only when every plain number in it is sourced
    seg_status: dict[int, list[tuple[calc_verify.Result, str]]] = {}
    for s, r in arith:
        cited = [facts[i] for i in cited_ids(s.notes) if i in facts]
        if r.status == "ok":
            loose = [v for v in r.literals if not literal_sourced(v, cited, results, illus + assumed[s.index])]
            status = "verified" if not loose else "cited"
            detail = "" if not loose else "inputs with no source: " + ", ".join(f"{v:g}" for v in loose)
        elif r.status == "error":
            status, detail = "error", r.detail
        else:
            status, detail = "cited", r.detail
        seg_status.setdefault(s.index, []).append((r, status))
        report.calcs.append(CalcResult(s.index, status, r.segment.text, detail))
    # a verified result can be shown again on another slide (EV on the comps page); small bare counts cannot
    verified_results = [
        (r.segment.lhs_value, r.segment.lhs_unit)
        for _, r in arith
        if any(c.text == r.segment.text and c.status == "verified" for c in report.calcs)
    ]
    # 3. every visible number
    for s in deck.slides:
        cited = [facts[i] for i in cited_ids(s.notes) if i in facts]
        report.unknown += [
            f"UNKNOWN slide {s.index}: notes cite {i}, which is not in {facts_path}"
            for i in FACT_ID.findall(s.notes)
            if i not in facts
        ]
        cells = table_context(s)
        segs = seg_status.get(s.index, [])
        # a statement runs to the next "calc:" marker or line break; it cites when it names a fact id
        cite_lines = [ln for ln in re.split(r"\n|(?=calc:)", s.notes) if FACT_ID.search(ln)]
        for raw, num in slide_numbers(s):
            value = num.value
            assert not isinstance(value, str)  # slide_numbers builds pseudo-facts from parsed numbers
            by_value = [f for f in cited if matches(num, f)]
            extra = next((c for cell, c in cells.items() if cell and cell in num.text), "")
            hits = [
                (r, st)
                for r, st in segs
                if calc_verify.close(value, r.segment.lhs_value, value)
                and (r.segment.lhs_raw.lstrip("$€£+-") in raw or raw.lstrip("$€£+-") in r.segment.lhs_raw)
            ]
            elsewhere = (num.unit or len(re.sub(r"[^\d]", "", raw).lstrip("0")) >= 3) and any(
                calc_verify.close(value, v, value) and (u == num.unit or not u) for v, u in verified_results
            )
            if (
                any(names_metric(num, f, extra, s.notes) for f in by_value)
                or any(st == "verified" for _, st in hits)
                or elsewhere
            ):
                status, detail = "verified", ""
            elif any(calc_verify.close(value, a, value) for a in assumed[s.index]):
                status, detail = "assumption", ""
            elif any(st == "error" for _, st in hits):
                status, detail = "calc-error", next(r.detail for r, st in hits if st == "error")
            elif by_value:
                status = "cited"
                detail = f"equals {by_value[0].id} ({by_value[0].text[:50]!r}), but the slide text does not name it"
            elif hits:
                status, detail = "cited", "its calc: line cannot be verified (prose, units, or unsourced inputs)"
            elif (digits := re.sub(r"[^\d.]", "", raw)) and any(
                digits in re.sub(r"[^\d.\s]", " ", ln).split() or raw in ln for ln in cite_lines
            ):
                status, detail = "cited", "named in a note that cites facts, with no checkable calc: line"
            elif any(abs(v - value) < 1e-9 for v in illus):
                status, detail = "illustrative", ""
            else:
                status, detail = "untraced", ""
            report.numbers.append(NumberResult(s.index, raw, num.text, status, detail))
    return report


def check(deck_path: str, facts_path: str, data_path: str | None) -> tuple[list[str], int]:
    """Failures and the count of numbers checked (the pre-1.1 interface)."""
    report = check_report(deck_path, facts_path, data_path)
    return report.failures(), len(report.numbers)


def main() -> int:
    ap = argparse.ArgumentParser(description="Trace every slide number to a cited fact.")
    ap.add_argument("deck")
    ap.add_argument("facts")
    ap.add_argument("--data", help='deck-data.json with top-level "illustrative": true')
    args = ap.parse_args()
    report = check_report(args.deck, args.facts, args.data)
    problems, warnings = report.failures(), report.warnings()
    for p in problems:
        print(p)
    for w in warnings:
        print(f"WARN {w}")
    kinds = ("verified", "assumption", "cited", "illustrative")
    counts = {k: sum(n.status == k for n in report.numbers) for k in kinds}
    calcs_ok = sum(c.status == "verified" for c in report.calcs)
    print(
        f"trace-check: {len(report.numbers)} number(s) checked, {len(problems)} problem(s), "
        f"{len(warnings)} warning(s) — {counts['verified']} verified, {counts['assumption']} assumption(s), "
        f"{counts['cited']} cited but not verified, {counts['illustrative']} illustrative; "
        f"{calcs_ok}/{len(report.calcs)} calc(s) verified"
    )
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
