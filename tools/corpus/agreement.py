#!/usr/bin/env python3
"""Validate coding records and compute inter-coder agreement (Cohen's kappa).

Development tool. Reads <corpus>/coding/<coder>/<deck>.json records.

  python3 agreement.py validate             # schema-check every record
  python3 agreement.py kappa A B            # kappa between coders A and B on shared decks
  python3 agreement.py kappa 'c*' 'd*'      # pooled primary vs pooled double-coders
Kappa is reported per field for the gated fields (archetype, chart_type,
title_is_assertion) plus a few deck-level fields for information.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((ROOT / "research" / "coding-schema.json").read_text())
CODING = Path.home() / "deck-corpus" / "coding"
GATED = ("archetype", "chart_type", "title_is_assertion")
INFO_SLIDE = ("has_source_line", "has_takeaway_box", "has_unit_line", "has_tracker", "text_density")
INFO_DECK = ("storyline_type", "navigation_system", "exec_summary_form", "footnote_system")
THRESHOLD = 0.7


def records(coder: str) -> dict[str, dict]:
    """Records for one coder, or a pooled group given as a glob such as 'c*'."""
    out = {}
    for d in sorted(CODING.glob(coder)):
        for f in sorted(d.glob("*.json")):
            out.setdefault(f.stem, json.loads(f.read_text()))
    return out


def validate() -> int:
    v = Draft202012Validator(SCHEMA)
    bad = 0
    for f in sorted(CODING.glob("*/*.json")):
        errs = list(v.iter_errors(json.loads(f.read_text())))
        if errs:
            bad += 1
            print(f"INVALID {f.relative_to(CODING)}: {errs[0].message[:160]}")
    print(f"validated {len(list(CODING.glob('*/*.json')))} records, {bad} invalid")
    return 1 if bad else 0


def kappa(pairs: list[tuple]) -> float:
    if not pairs:
        return float("nan")
    n = len(pairs)
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb.get(k, 0) for k in ca) / (n * n)
    return 1.0 if pe == 1 else (po - pe) / (1 - pe)


def compare(a: str, b: str) -> int:
    ra, rb = records(a), records(b)
    shared = sorted(set(ra) & set(rb))
    print(f"shared decks: {len(shared)}")
    slide_pairs: dict[str, list] = {f: [] for f in GATED + INFO_SLIDE}
    deck_pairs: dict[str, list] = {f: [] for f in INFO_DECK}
    for deck in shared:
        sa = {s["page"]: s for s in ra[deck]["slides"]}
        sb = {s["page"]: s for s in rb[deck]["slides"]}
        for page in sorted(set(sa) & set(sb)):
            for f in slide_pairs:
                slide_pairs[f].append((sa[page][f], sb[page][f]))
        for f in deck_pairs:
            deck_pairs[f].append((ra[deck]["deck"][f], rb[deck]["deck"][f]))
    ok = True
    for f, pairs in slide_pairs.items():
        k = kappa(pairs)
        gate = f in GATED
        ok &= (k >= THRESHOLD) if gate else True
        print(f"{'GATE' if gate else 'info'} {f:<20} n={len(pairs):<4} kappa={k:.2f}"
              f"{'' if not gate else ('  PASS' if k >= THRESHOLD else '  FAIL')}")
    for f, pairs in deck_pairs.items():
        print(f"info {f:<20} n={len(pairs):<4} agreement={sum(x == y for x, y in pairs)}/{len(pairs)}")
    return 0 if ok else 1


def disagreements(a: str, b: str) -> int:
    ra, rb = records(a), records(b)
    for deck in sorted(set(ra) & set(rb)):
        sa = {s["page"]: s for s in ra[deck]["slides"]}
        sb = {s["page"]: s for s in rb[deck]["slides"]}
        for page in sorted(set(sa) & set(sb)):
            diffs = {f: (sa[page][f], sb[page][f]) for f in GATED if sa[page][f] != sb[page][f]}
            if diffs:
                print(f"{deck} p{page}: {diffs}")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "validate"
    if cmd == "validate":
        sys.exit(validate())
    if cmd in ("kappa", "diff") and len(sys.argv) == 4:
        sys.exit(compare(sys.argv[2], sys.argv[3]) if cmd == "kappa" else disagreements(sys.argv[2], sys.argv[3]))
    sys.exit(__doc__)
