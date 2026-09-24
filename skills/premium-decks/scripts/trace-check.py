#!/usr/bin/env python3
"""Check that every number on every slide traces to a source.

A number on a slide passes when one of these holds:
  1. It equals (at its stated precision) a fact from facts.jsonl whose id the
     slide's speaker notes cite, e.g. "[F0027]".
  2. The slide's notes carry a derivation line containing that number and at
     least one fact id, e.g. "calc: $72M = 150 bps x $4.82B [F0027]".
  3. It appears in a deck-data.json whose top level says "illustrative": true
     (the data contract for invented figures).
Ignored: slide numbers, bare years, dates, period labels (Q1, FY25), footnote
markers, tracker section numbers, and list ordinals.

Prints UNTRACED lines and exits 1 if any number is untraced.
Usage: python3 trace-check.py deck.pptx|deck.html brief/facts.jsonl [--data deck-data.json]
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
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


def check(deck_path: str, facts_path: str, data_path: str | None) -> tuple[list[str], int]:
    deck = deck_model.load(deck_path)
    facts = load_facts(Path(facts_path))
    illus = illustrative_values(Path(data_path) if data_path else None)
    problems, total = [], 0
    for s in deck.slides:
        cited = [facts[i] for i in cited_ids(s.notes) if i in facts]
        unknown = [i for i in FACT_ID.findall(s.notes) if i not in facts]
        for i in unknown:
            problems.append(f"UNKNOWN slide {s.index}: notes cite {i}, which is not in {facts_path}")
        # A statement runs to the next "calc:" marker or line break; it counts when it cites a fact id.
        calc_lines = [ln for ln in re.split(r"\n|(?=calc:)", s.notes) if FACT_ID.search(ln)]
        for raw, num in slide_numbers(s):
            total += 1
            if any(matches(num, f) for f in cited):
                continue
            digits = re.sub(r"[^\d.]", "", raw)
            if digits and any(digits in re.sub(r"[^\d.\s]", " ", ln).split() or raw in ln for ln in calc_lines):
                continue
            value = num.value
            assert not isinstance(value, str)  # slide_numbers builds pseudo-facts from parsed numbers
            if any(abs(v - value) < 1e-9 for v in illus):
                continue
            problems.append(f"UNTRACED slide {s.index}: {raw!r} in “{num.text[:70]}”")
    return problems, total


def main() -> int:
    ap = argparse.ArgumentParser(description="Trace every slide number to a cited fact.")
    ap.add_argument("deck")
    ap.add_argument("facts")
    ap.add_argument("--data", help='deck-data.json with top-level "illustrative": true')
    args = ap.parse_args()
    problems, total = check(args.deck, args.facts, args.data)
    for p in problems:
        print(p)
    print(f"trace-check: {total} number(s) checked, {len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
