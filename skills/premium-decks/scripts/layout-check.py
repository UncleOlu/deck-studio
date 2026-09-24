#!/usr/bin/env python3
"""Check a .pptx deck's geometry: overflow, drift, near-miss alignment, collisions.

From the shape geometry (no render needed):
  - text that cannot fit its box at its font size (estimate; autofit boxes skipped)
  - shapes that leave the slide
  - title, source line, and tracker positions drifting between content slides
    (the cover and the closing slide are bookends and are not compared)
  - near-miss alignment: left edges 0.02-0.12" apart (meant to align, did not)
From a rendered PDF (optional, --pdf; needs poppler's pdftotext):
  - words that overlap other words (text collision)
  - words outside the page

HTML decks: geometry lives in the browser; use the screenshot QA in html-mode.md.
Prints ERROR/WARN lines; exits 1 on any ERROR.
Usage: python3 layout-check.py deck.pptx [--pdf deck.pdf]
"""
from __future__ import annotations

import argparse
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import deck_model  # noqa: E402

DRIFT_IN = 0.04
NEAR_MISS = (0.02, 0.12)
AVG_CHAR_EM = 0.50       # average glyph width as a share of the font size (Latin text, mixed case)
LINE_HEIGHT = 1.2
DEFAULT_PT = 18.0


def text_fits(sh) -> tuple[bool, float]:
    """Estimate the text height a box needs; return (fits, need/available)."""
    if sh.autofit or not sh.paragraphs or sh.w <= 0 or sh.h <= 0:
        return True, 0.0
    left, top, right, bottom = sh.insets
    width_in = max(sh.w - left - right, 0.1)
    need = 0.0
    for i, para in enumerate(sh.paragraphs):
        pt = (sh.para_pts[i] if i < len(sh.para_pts) and sh.para_pts[i] else 0) or sh.font_pt or DEFAULT_PT
        # Width from each run's own size: a "52 → 19 min" line mixes 28pt and 66pt runs.
        sized, unsized = sh.para_em[i] if i < len(sh.para_em) else (0.0, len(para))
        width_pt = (sized + unsized * (sh.font_pt or DEFAULT_PT)) * AVG_CHAR_EM
        lines = max(1, math.ceil(width_pt / (width_in * 72))) + para.count("\n")
        need += lines * pt * LINE_HEIGHT / 72
    avail = max(sh.h - top - bottom, 0.05)
    ratio = need / avail
    return ratio <= 1.08, ratio


def intrudes(sh, ratio: float, others) -> str:
    """Name of a shape the overflowing text would run into, or ''."""
    over_top, over_bottom = sh.y + sh.h, sh.y + sh.h * ratio
    for o in others:
        if o is sh or o.w == 0 or o.kind == "other":
            continue
        if o.x < sh.x + sh.w and sh.x < o.x + o.w and o.y < over_bottom and over_top <= o.y + o.h:
            return o.name
    return ""


def role(sh, slide) -> str:
    name = sh.name.lower()
    is_title_text = bool(slide.title) and sh.text.strip() == slide.title
    if sh.placeholder in ("title", "ctrTitle") or name.startswith("title") or is_title_text:
        return "title"
    if name.startswith("tracker"):
        return "tracker"
    if re.match(r"^\s*(sources?|notes?)\s*:", sh.text, re.I) or name.startswith("source"):
        return "source"
    return ""


def geometry_checks(deck) -> tuple[list[str], list[str]]:
    errs, warns = [], []
    anchors: dict[str, list[tuple[int, float, float, float]]] = {"title": [], "source": [], "tracker": []}
    for s in deck.slides:
        lefts = []
        for sh in s.shapes:
            if sh.w == 0 and sh.h == 0:
                continue
            if sh.x < -0.01 or sh.y < -0.01 or sh.x + sh.w > deck.width + 0.01 or sh.y + sh.h > deck.height + 0.01:
                errs.append(f"ERROR slide {s.index}: '{sh.name}' extends off the slide")
            if sh.kind == "text" and sh.text.strip() and sh.placeholder not in ("sldNum", "dt", "ftr"):
                fits, ratio = text_fits(sh)
                if not fits:
                    hit = intrudes(sh, ratio, s.shapes)
                    msg = (f"slide {s.index}: '{sh.name}' text needs ~{ratio:.0%} of its box height: "
                           f"“{sh.text[:50]}”")
                    if hit:
                        errs.append(f"ERROR {msg} and runs into '{hit}'")
                    else:
                        warns.append(f"WARN {msg} (spills past its box; nothing below it)")
                lefts.append((round(sh.x, 3), sh.name))
            r = role(sh, s)
            if r and 1 < s.index < len(deck.slides):  # the cover and closing slides are bookends
                anchors[r].append((s.index, sh.x, sh.y, sh.w))
        xs = sorted({x for x, _ in lefts})
        for a, b in zip(xs, xs[1:]):
            if NEAR_MISS[0] <= b - a <= NEAR_MISS[1]:
                names = [n for x, n in lefts if x in (a, b)]
                warns.append(f"WARN slide {s.index}: left edges {a:.2f}\" and {b:.2f}\" nearly align "
                             f"({', '.join(names[:3])}) — snap to one grid line")
    for r, pts in anchors.items():
        if len(pts) < 3:
            continue
        for key, i in (("x", 1), ("y", 2), ("width", 3)):
            vals = sorted(p[i] for p in pts)
            mode = max(set(round(v, 2) for v in vals), key=lambda v: sum(abs(x - v) < 0.005 for x in vals))
            for p in pts:
                if abs(p[i] - mode) > DRIFT_IN:
                    errs.append(f"ERROR slide {p[0]}: {r} {key} is {p[i]:.2f}\"; the deck standard is {mode:.2f}\"")
    return errs, warns


def pdf_checks(pdf: Path) -> tuple[list[str], list[str]]:
    if not shutil.which("pdftotext"):
        return [], ["WARN: pdftotext not found — install poppler to run the render checks"]
    if not pdf.exists():
        return [f"ERROR: {pdf} does not exist — render the deck first (scripts/pptx2pdf.py)"], []
    out = subprocess.run(["pdftotext", "-bbox", str(pdf), "-"], capture_output=True, text=True, timeout=300, check=True)
    errs = []
    page = 0
    pw = ph = 0.0
    words: list[tuple[float, float, float, float, str]] = []

    def flush():
        hits = 0
        for i, a in enumerate(words):
            if a[0] < -1 or a[1] < -1 or a[2] > pw + 1 or a[3] > ph + 1:
                errs.append(f"ERROR page {page}: “{a[4]}” lies outside the page")
            for b in words[i + 1:]:
                ix = min(a[2], b[2]) - max(a[0], b[0])
                iy = min(a[3], b[3]) - max(a[1], b[1])
                if ix > 1.5 and iy > 0.35 * min(a[3] - a[1], b[3] - b[1]):
                    hits += 1
                    if hits <= 3:
                        errs.append(f"ERROR page {page}: “{a[4]}” collides with “{b[4]}”")
        if hits > 3:
            errs.append(f"ERROR page {page}: {hits - 3} more collisions")

    for line in out.stdout.splitlines():
        m = re.search(r'<page width="([\d.]+)" height="([\d.]+)"', line)
        if m:
            if page:
                flush()
            page += 1
            pw, ph = float(m.group(1)), float(m.group(2))
            words = []
            continue
        m = re.search(r'<word xMin="([\d.-]+)" yMin="([\d.-]+)" xMax="([\d.-]+)" yMax="([\d.-]+)">(.*?)</word>', line)
        if m:
            words.append((float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5)))
    if page:
        flush()
    return errs, []


def main() -> int:
    ap = argparse.ArgumentParser(description="Check deck geometry.")
    ap.add_argument("deck")
    ap.add_argument("--pdf")
    args = ap.parse_args()
    if not args.deck.lower().endswith(".pptx"):
        print("layout-check reads .pptx geometry; for HTML decks use the browser screenshot QA.")
        return 0
    deck = deck_model.load(args.deck)
    errs, warns = geometry_checks(deck)
    if args.pdf:
        e2, w2 = pdf_checks(Path(args.pdf))
        errs += e2
        warns += w2
    for line in errs + warns:
        print(line)
    print(f"layout-check: {len(deck.slides)} slide(s), {len(errs)} error(s), {len(warns)} warning(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
