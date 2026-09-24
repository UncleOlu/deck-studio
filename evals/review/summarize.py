#!/usr/bin/env python3
"""Summarise the independent review study (PROTOCOL.md): medians and ranges per register and overall.

Reads review-log.csv (one row per deck) and, where a row names one, its review_diff.py JSON.
Usage: python3 summarize.py review-log.csv
"""

from __future__ import annotations

import csv
import json
import statistics
import sys
from pathlib import Path
from typing import Any

MEASURES = [
    ("minutes_to_approval", "minutes to approval"),
    ("revision_rounds", "revision rounds"),
    ("numbers_changed", "numbers corrected"),
    ("factual_errors_found", "factual errors found"),
    ("titles_rewritten", "titles rewritten"),
    ("editing_effort_1to5", "editing effort (1 easy – 5 hard)"),
]


def number(v: Any) -> float | None:
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def load(log: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with log.open(newline="") as fh:
        for row in csv.DictReader(fh):
            rec: dict[str, Any] = dict(row)
            diff_path = (row.get("diff_json") or "").strip()
            if diff_path:
                p = (log.parent / diff_path).resolve()
                if not p.is_relative_to(log.parent.resolve()):
                    sys.exit(f"summarize: {diff_path} is outside {log.parent}")
                rec.update(json.loads(p.read_text()))
            rows.append(rec)
    return rows


def describe(rows: list[dict[str, Any]], label: str) -> list[str]:
    out = [f"{label} ({len(rows)} deck(s))"]
    for key, name in MEASURES:
        vals = [v for v in (number(r.get(key)) for r in rows) if v is not None]
        if vals:
            spread = f"range {min(vals):g}–{max(vals):g}, n={len(vals)}"
            out.append(f"  {name}: median {statistics.median(vals):g} ({spread})")
    sends = [r for r in rows if str(r.get("would_send", "")).strip().lower() in ("yes", "no")]
    if sends:
        yes = sum(str(r["would_send"]).strip().lower() == "yes" for r in sends)
        out.append(f"  would send: {yes} of {len(sends)}")
    clean = [r for r in rows if number(r.get("numbers_changed")) == 0]
    if any(number(r.get("numbers_changed")) is not None for r in rows):
        out.append(f"  decks with no number corrected: {len(clean)} of {len(rows)}")
    saved = [
        b - m
        for b, m in ((number(r.get("baseline_minutes")), number(r.get("minutes_to_approval"))) for r in rows)
        if b is not None and m is not None
    ]
    if saved:
        out.append(f"  minutes saved vs baseline: median {statistics.median(saved):g} (n={len(saved)})")
    return out


def main() -> int:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    rows = load(Path(sys.argv[1]))
    if not rows:
        print("summarize: the log has no rows yet")
        return 0
    lines = describe(rows, "All decks")
    for register in sorted({str(r.get("register", "")) for r in rows} - {""}):
        lines += describe([r for r in rows if r.get("register") == register], f"Register: {register}")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
