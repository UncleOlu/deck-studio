#!/usr/bin/env python3
"""Measure what a reviewer changed between the delivered deck and the deck they approved.

For the independent-review study (PROTOCOL.md): the edits a reviewer had to make are
the evidence of how close to decision-ready a deck was. Slides are matched by title
(falling back to position), then compared:

  slides_added / slides_removed / slides_moved   structure the reviewer changed
  titles_rewritten                               matched slides whose title changed
  numbers_changed                                figures in text or tables that differ
  chart_values_changed                           chart data points that differ
  text_edit_ratio                                0 = body text untouched, 1 = fully rewritten
  charts_now_pictures                            native charts the reviewer had to replace
                                                 with an image (an editability failure)

Usage: python3 review_diff.py delivered.pptx approved.pptx [--json out.json]
"""

from __future__ import annotations

import argparse
import difflib
import json
import sys
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "skills" / "premium-decks" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import deck_model  # noqa: E402
import ingest  # noqa: E402

TITLE_MATCH = 0.6  # SequenceMatcher ratio above which two titles are the same slide, edited


@dataclass
class SlideChange:
    delivered: int
    approved: int
    title_rewritten: bool
    numbers_changed: int
    chart_values_changed: int
    text_edit_ratio: float
    chart_now_picture: bool


@dataclass
class ReviewDiff:
    delivered_slides: int
    approved_slides: int
    slides_added: int = 0
    slides_removed: int = 0
    slides_moved: int = 0
    titles_rewritten: int = 0
    numbers_changed: int = 0
    chart_values_changed: int = 0
    text_edit_ratio: float = 0.0
    charts_now_pictures: int = 0
    slides: list[SlideChange] = field(default_factory=list)


def _ratio(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _numbers(slide: deck_model.Slide) -> Counter[float]:
    found: Counter[float] = Counter()
    for block in slide.texts[1:]:
        for v, *_ in ingest.numbers_in(block):
            found[round(v, 6)] += 1
    return found


def _chart_values(slide: deck_model.Slide) -> list[float]:
    return [float(v) for ch in slide.charts for s in ch.series if not s["invisible"] for v in s["values"]]


def match(delivered: list[deck_model.Slide], approved: list[deck_model.Slide]) -> list[tuple[int, int]]:
    """Pairs of (delivered index, approved index), best title match first, each slide used once."""
    scored = sorted(
        ((_ratio(d.title, a.title), i, j) for i, d in enumerate(delivered) for j, a in enumerate(approved)),
        reverse=True,
    )
    used_d: set[int] = set()
    used_a: set[int] = set()
    pairs: list[tuple[int, int]] = []
    for score, i, j in scored:
        if score < TITLE_MATCH or i in used_d or j in used_a:
            continue
        pairs.append((i, j))
        used_d.add(i)
        used_a.add(j)
    # untitled slides (no title to match on) pair by position; a titled slide left over was removed or added
    left_d = [i for i in range(len(delivered)) if i not in used_d and not delivered[i].title.strip()]
    left_a = [j for j in range(len(approved)) if j not in used_a and not approved[j].title.strip()]
    pairs += list(zip(left_d, left_a))
    return sorted(pairs)


def diff(delivered_path: str, approved_path: str) -> ReviewDiff:
    d_deck, a_deck = deck_model.load(delivered_path), deck_model.load(approved_path)
    d_slides, a_slides = d_deck.slides, a_deck.slides
    pairs = match(d_slides, a_slides)
    out = ReviewDiff(len(d_slides), len(a_slides))
    out.slides_removed = len(d_slides) - len(pairs)
    out.slides_added = len(a_slides) - len(pairs)
    # a slide moved when its approved position breaks the order of the others (longest increasing run)
    order = [j for _, j in sorted(pairs)]
    keep = _longest_increasing(order)
    out.slides_moved = len(order) - keep
    ratios = []
    for i, j in pairs:
        d, a = d_slides[i], a_slides[j]
        dn, an = _numbers(d), _numbers(a)
        dv, av = _chart_values(d), _chart_values(a)
        changed_chart = sum(1 for x, y in zip(dv, av) if abs(x - y) > 1e-9) + abs(len(dv) - len(av))
        body_d, body_a = "\n".join(d.texts[1:]), "\n".join(a.texts[1:])
        ratio = 1.0 - _ratio(body_d, body_a) if (body_d or body_a) else 0.0
        pics_a = sum(1 for s in a.shapes if s.kind == "picture")
        pics_d = sum(1 for s in d.shapes if s.kind == "picture")
        now_picture = bool(d.charts) and len(a.charts) < len(d.charts) and pics_a > pics_d
        change = SlideChange(
            i + 1,
            j + 1,
            d.title.strip() != a.title.strip(),
            max(sum((dn - an).values()), sum((an - dn).values())),
            changed_chart,
            round(ratio, 3),
            now_picture,
        )
        out.slides.append(change)
        ratios.append(ratio)
    out.titles_rewritten = sum(c.title_rewritten for c in out.slides)
    out.numbers_changed = sum(c.numbers_changed for c in out.slides)
    out.chart_values_changed = sum(c.chart_values_changed for c in out.slides)
    out.charts_now_pictures = sum(c.chart_now_picture for c in out.slides)
    out.text_edit_ratio = round(sum(ratios) / len(ratios), 3) if ratios else 0.0
    return out


def _longest_increasing(seq: list[int]) -> int:
    best: list[int] = []
    for x in seq:
        lo, hi = 0, len(best)
        while lo < hi:
            mid = (lo + hi) // 2
            if best[mid] < x:
                lo = mid + 1
            else:
                hi = mid
        if lo == len(best):
            best.append(x)
        else:
            best[lo] = x
    return len(best)


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure a reviewer's edits between two versions of a deck.")
    ap.add_argument("delivered")
    ap.add_argument("approved")
    ap.add_argument("--json", help="also write the full result, per slide, to this file")
    args = ap.parse_args()
    for p in (args.delivered, args.approved):
        if Path(p).suffix.lower() != ".pptx" or not Path(p).is_file():
            sys.exit(f"review_diff: {p} is not a .pptx file")
    r = diff(args.delivered, args.approved)
    print(
        f"review_diff: {r.delivered_slides} → {r.approved_slides} slides; {r.slides_added} added, "
        f"{r.slides_removed} removed, {r.slides_moved} moved; {r.titles_rewritten} title(s) rewritten; "
        f"{r.numbers_changed} number(s) and {r.chart_values_changed} chart value(s) changed; "
        f"body text edit ratio {r.text_edit_ratio:.2f}; {r.charts_now_pictures} chart(s) replaced by pictures"
    )
    if args.json:
        Path(args.json).write_text(json.dumps(asdict(r), indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
