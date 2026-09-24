#!/usr/bin/env python3
"""Check a deck's arithmetic and cross-slide consistency.

  1. Waterfalls (a stacked bar with an invisible base series): every floating
     bar starts where the previous bar ended, and the closing total equals the
     opening total plus the steps.
  2. Shares: pie/doughnut charts and 100%-stacked charts whose values are
     percentages sum to 100 (±0.5 for rounding).
  3. Tables with a "Total" row or column: the parts sum to the total, at the
     precision printed.
  4. One value per metric: figures with a unit whose labels share a phrase
     (two adjacent words, e.g. "adjusted EBITDA") but whose values differ on
     two slides.
  6. Bar charts whose value axis starts above zero (bars then overstate differences).
  5. Footnotes: superscript markers (and inline "(n)" markers on slides with numbered notes)
     run 1, 2, 3… in order, and each
     marker has a matching note line on that slide.

Prints ERROR lines and exits 1 on any. Usage: python3 integrity-check.py deck.pptx|deck.html
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deck_model  # noqa: E402
import ingest  # noqa: E402

TOL = 0.5


def check_waterfall(idx: int, ch: deck_model.Chart) -> list[str]:
    if (
        ch.kind != "barChart"
        or ch.grouping != "stacked"
        or ch.bar_dir == "bar"
        or not any(s["invisible"] for s in ch.series)
    ):
        return []  # waterfalls are vertical; a horizontal floating bar is a range chart (football field)
    base = next(s for s in ch.series if s["invisible"])["values"]
    visible = [s["values"] for s in ch.series if not s["invisible"]]
    n = len(base)
    tops = [base[i] + sum(v[i] for v in visible if i < len(v)) for i in range(n)]
    errs: list[str] = []
    if n < 3:
        return errs
    tol = max(1e-6, 0.005 * max(abs(t) for t in tops))  # rounding slack: 0.5% of the chart's range
    level = tops[0]  # the opening total stands on zero
    for i in range(1, n - 1):
        lo, hi = base[i], tops[i]
        if abs(lo - level) <= tol:
            level = hi  # an increase: starts at the level, ends higher
        elif abs(hi - level) <= tol:
            level = lo  # a decrease: hangs from the level, ends lower
        else:
            label = ch.categories[i] if i < len(ch.categories) else f"bar {i + 1}"
            errs.append(
                f"ERROR slide {idx}: waterfall bar '{label}' floats at {lo:g}–{hi:g}, "
                f"but the running total is {level:g}"
            )
            level = hi
    if abs(tops[-1] - level) > tol or base[-1] > tol:
        errs.append(
            f"ERROR slide {idx}: waterfall closing total is {tops[-1]:g}, "
            f"but the opening plus the steps gives {level:g}"
        )
    return errs


def check_bar_baseline(idx: int, ch: deck_model.Chart) -> list[str]:
    """Bars encode value by length: a value axis that starts above zero exaggerates differences."""
    if ch.kind not in ("barChart", "bar3DChart") or any(s["invisible"] for s in ch.series):
        return []  # floating bars (waterfalls, football fields) do not encode value by length
    vals = [v for s in ch.series if not s["invisible"] for v in s["values"]]
    if not vals or min(vals) < 0:
        return []
    if ch.axis_min is not None and ch.axis_min > 0:
        return [
            f"ERROR slide {idx}: bar chart value axis starts at {ch.axis_min:g}, not 0 — bars overstate "
            "the differences; start the axis at zero (or use a dot plot)"
        ]
    if ch.axis_min is None and max(vals) > 0 and min(vals) / max(vals) > 5 / 6:
        # PowerPoint's automatic axis drops the zero baseline when the smallest bar exceeds ~5/6 of the largest.
        return [
            f"ERROR slide {idx}: bar values {min(vals):g}–{max(vals):g} are close together, so PowerPoint's "
            "automatic axis will not start at zero; set the value-axis minimum to 0"
        ]
    return []


def check_shares(idx: int, ch: deck_model.Chart) -> list[str]:
    errs: list[str] = []
    if ch.kind in ("pieChart", "doughnutChart", "pie3DChart"):
        for s in ch.series:
            total = sum(s["values"])
            if 90 <= total <= 110 and abs(total - 100) > TOL:
                errs.append(f"ERROR slide {idx}: pie/doughnut shares sum to {total:g}%, not 100%")
    if ch.grouping == "percentStacked" and ch.series:
        n = max(len(s["values"]) for s in ch.series)
        for i in range(n):
            total = sum(s["values"][i] for s in ch.series if i < len(s["values"]) and not s["invisible"])
            if 90 <= total <= 110 and abs(total - 100) > TOL:
                cat = ch.categories[i] if i < len(ch.categories) else f"bar {i + 1}"
                errs.append(f"ERROR slide {idx}: 100% stack '{cat}' sums to {total:g}")
    return errs


def cell_value(text: str) -> tuple[float, int] | None:
    t = text.strip().replace("—", "").replace("–", "")
    if not t:
        return None
    found = ingest.numbers_in(t)
    if len(found) != 1:
        return None
    v, unit, scale, s, e = found[0]
    if len(t) - (e - s) > 3:  # a number inside words is a label, not a figure
        return None
    return v, ingest.decimals(v)


def check_table(idx: int, rows: list[list[str]]) -> list[str]:
    errs: list[str] = []
    if len(rows) < 3:
        return errs
    total_rows = [i for i, r in enumerate(rows) if r and re.match(r"^\s*(total|sum)\b", r[0], re.I)]
    for ti in total_rows:
        for c in range(1, len(rows[ti])):
            tv = cell_value(rows[ti][c])
            if tv is None:
                continue
            start = next(
                (j + 1 for j in range(ti - 1, -1, -1) if rows[j] and re.match(r"^\s*(sub)?total\b", rows[j][0], re.I)),
                1,
            )
            cells = [cell_value(rows[j][c]) for j in range(start, ti) if c < len(rows[j])]
            parts = [p for p in cells if p is not None]
            if len(parts) < 2 or re.search(r"%|margin|x\b", rows[0][c] if c < len(rows[0]) else "", re.I):
                continue
            s = sum(p[0] for p in parts)
            precision = max([tv[1]] + [p[1] for p in parts])
            tol = 0.5 * 10**-precision * (len(parts) + 1)
            if abs(s - tv[0]) > tol:
                head = rows[0][c] if c < len(rows[0]) else f"column {c + 1}"
                errs.append(
                    f"ERROR slide {idx}: table column '{head}' parts sum to {s:g}, "
                    f"but the '{rows[ti][0]}' row says {tv[0]:g}"
                )
    return errs


BOUNDARY = re.compile(r"[(;|•:]|\.\s|\bvs\.?\b|\bversus\b|\bcompared\b|\bagainst\b", re.I)
RANGE_DASH = re.compile(r"^\s*[–—-]\s*[$€£]?\d|[$€£]?\d[\d.,]*\s*[a-z%]*\s*[–—-]\s*$", re.I)


def clause_context(line: str, spans: list[tuple[int, int]], i: int) -> str:
    """Words that label figure i: what follows it up to the next figure or clause break,
    else the two words before it. Keeps a benchmark beside a figure from sharing its label."""
    a, b = spans[i]
    nxt = spans[i + 1][0] if i + 1 < len(spans) else len(line)
    after = line[b:nxt]
    cut = BOUNDARY.search(after)
    after = after[: cut.start()] if cut else after
    words = after.split()[:4]
    if len(ingest.label_words(" ".join(words))) < 2:
        prev = spans[i - 1][1] if i else 0
        before = line[prev:a]
        cuts = list(BOUNDARY.finditer(before))
        before = before[cuts[-1].end() :] if cuts else before
        words = before.split()[-3:] + words
    return " ".join(words + [line[a:b]])


QUALIFIERS = {
    "median",
    "mean",
    "average",
    "peer",
    "peers",
    "total",
    "benchmark",
    "target",
    "range",
    "high",
    "low",
    "current",
    "implied",
    "selected",
    "estimated",
}


def bigrams(text: str) -> set[tuple[str, str]]:
    # "52-week" stays one token, so a 52-week and a 26-week average never share a phrase
    words = [
        ingest.SYNONYMS.get(w, w)
        for w in re.findall(r"\d+-[a-z]+|[a-z][a-z-]+", text.lower())
        if w not in ingest.STOP and len(w) > 2
    ]
    return set(zip(words, words[1:]))


def check_consistency(deck: deck_model.Deck) -> list[str]:
    facts: list[ingest.Fact] = []
    for s in deck.slides:
        for block in s.texts[1:] + [s.title]:
            for line in block.splitlines():
                if re.match(r"^\s*(\(\d+\)\s*)?data note\s*:", line, re.I):
                    continue  # a disclosed source conflict states both values on purpose
                found = ingest.numbers_in(line)
                spans = [(a, b) for *_, a, b in found]
                for i, (v, unit, scale, a, b) in enumerate(found):
                    if RANGE_DASH.search(line[b : b + 4]) or RANGE_DASH.search(line[max(0, a - 12) : a]):
                        continue  # a range endpoint ("9.0x–11.0x") is not a stand-alone value
                    ctx = clause_context(line, spans, i)
                    facts.append(
                        ingest.Fact(
                            f"S{s.index}",
                            v,
                            unit,
                            scale,
                            ingest.period_of(ctx),
                            ctx,
                            f"slide {s.index}",
                            f"slide {s.index}",
                        )
                    )
    facts = [f for f in facts if f.unit or f.scale != 1.0]  # unitless integers are counts, pages, ordinals
    errs: list[str] = []
    for fa, fb, shared in ingest.find_conflicts(facts):
        shared_phrases = {bg for bg in bigrams(fa.text) & bigrams(fb.text) if not set(bg) <= QUALIFIERS}
        if not shared_phrases:  # "peer median" alone names no metric
            continue  # one shared word is too weak on slides; require a shared phrase ("adjusted EBITDA")
        errs.append(
            f"ERROR slides {fa.file[6:]} and {fb.file[6:]}: '{', '.join(sorted(shared))}' is "
            f"{ingest.fmt(fa)} on one and {ingest.fmt(fb)} on the other — one value per metric deck-wide"
        )
    return errs


# Inline "(1)"–"(9)" after a word or closing bracket. Counted only on slides that carry numbered note lines,
# so "Phase (2)" on a slide without notes is a label; "(12)" and "$(3)m" are values, never markers.
INLINE_MARKER = re.compile(r"(?<=[A-Za-z%)\]])\s?\(([1-9])\)(?![\w%])")
NOTE_LINE = re.compile(r"^\s*(?:\(\d{1,2}\)|\d{1,2}[.)])\s+\S")


def check_footnotes(s: deck_model.Slide) -> list[str]:
    markers: list[str] = []
    for sh in s.shapes:
        for m in sh.superscripts:
            markers += [x for x in re.split(r"[,\s]+", m) if x.isdigit()]
    lines = [ln for sh in s.shapes if sh.kind == "text" for ln in sh.text.splitlines()]
    if not any(ln.strip() for ln in lines):
        lines = [ln for block in s.texts[1:] for ln in block.splitlines()]  # HTML: no text shapes
    if any(NOTE_LINE.match(ln) for ln in lines):
        for line in lines:
            if not deck_model.FOOTNOTE_RE.match(line) and not re.match(r"^\s*(Notes?|Sources?)\s*:", line, re.I):
                markers += INLINE_MARKER.findall(line)
    if not markers:
        return []
    errs: list[str] = []
    seen: list[str] = []
    for m in markers:
        if m not in seen:
            seen.append(m)
    expected = [str(i) for i in range(1, len(seen) + 1)]
    if seen != expected:
        errs.append(
            f"ERROR slide {s.index}: footnote markers appear as {', '.join(seen)}; number them 1… in reading order"
        )
    notes = " ".join(s.footnotes)
    for m in seen:
        if not re.search(rf"(^|\s|\(){m}[.)]?\s+\S", notes):
            errs.append(f"ERROR slide {s.index}: footnote marker {m} has no note line on the slide")
    return errs


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    deck = deck_model.load(sys.argv[1])
    errs: list[str] = []
    for s in deck.slides:
        for ch in s.charts:
            errs += [f"ERROR slide {s.index}: {msg}" for msg in ch.problems]
            if ch.series:  # HTML charts carry data only when a recipe declares it (html-finance.md)
                errs += check_waterfall(s.index, ch) + check_shares(s.index, ch) + check_bar_baseline(s.index, ch)
        for t in s.tables:
            errs += check_table(s.index, t.rows)
        errs += check_footnotes(s)
    errs += check_consistency(deck)
    for e in errs:
        print(e)
    print(f"integrity-check: {len(deck.slides)} slide(s), {len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
