#!/usr/bin/env python3
"""Un-blind and summarise a judge workflow result.

Usage: python3 score.py <workflow-result.json> <pair-name>
  pair key:   ~/deck-corpus/judge/keys/<pair-name>.json      (case -> {A: label, B: label})
  disc key:   ~/deck-corpus/judge/<disc-set>/key.json        (from the result's discDir)
Writes evals/reports/judge-<pair-name>.md.
"""
from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

DIMS = ["storyline", "synthesis", "framework_fit", "page_grammar", "data_integrity", "visual_quality",
        "decision_readiness"]


def main() -> int:
    result = json.loads(Path(sys.argv[1]).read_text())
    pair = sys.argv[2]
    key = json.loads((Path.home() / "deck-corpus" / "judge" / "keys" / f"{pair}.json").read_text())
    per_label: dict[str, dict[str, list[int]]] = {}
    prefs: dict[str, int] = {}
    rows = []
    for r in result["rubric"]:
        k = key[r["case"]]
        for side in ("A", "B"):
            lab = k[side]
            for d in DIMS:
                per_label.setdefault(lab, {}).setdefault(d, []).append(r[side][d])
        pref = k.get(r["preferred"], "tie") if r["preferred"] != "tie" else "tie"
        prefs[pref] = prefs.get(pref, 0) + 1
        rows.append((r["case"], k["A"], sum(r["A"].values()) / len(DIMS), k["B"], sum(r["B"].values()) / len(DIMS),
                     pref))
    labels = sorted(per_label)
    out = [f"# Blind judge — {pair}", "", "## Rubric means (1–5) by dimension", "",
           "| Dimension | " + " | ".join(labels) + " |", "|---|" + "---|" * len(labels)]
    for d in DIMS:
        out.append(f"| {d} | " + " | ".join(f"{statistics.mean(per_label[lab][d]):.2f}" for lab in labels) + " |")
    out.append("| **overall** | " + " | ".join(
        f"**{statistics.mean(v for d in DIMS for v in per_label[lab][d]):.2f}**" for lab in labels) + " |")
    out += ["", "## Per case (mean over dimensions)", "", "| Case | A | A score | B | B score | Preferred |",
            "|---|---|---|---|---|---|"]
    out += [f"| {c} | {a} | {sa:.2f} | {b} | {sb:.2f} | {p} |" for c, a, sa, b, sb, p in rows]
    out += ["", "Preferences: " + ", ".join(f"{k} {v}" for k, v in sorted(prefs.items()))]
    disc = result.get("discrimination") or []
    if disc and result.get("discKey"):
        dkey = json.loads(Path(result["discKey"]).read_text())
        out += ["", "## Discrimination (generated vs real)", ""]
        accs = []
        for i, judge in enumerate(disc, 1):
            calls = {c["item"].replace(".jpg", ""): c for c in judge["calls"]}
            correct = sum(1 for item, v in dkey.items() if item in calls and calls[item]["call"] == v["label"])
            n = sum(1 for item in dkey if item in calls)
            accs.append(correct / n if n else 0)
            gen_called_gen = [calls[i2]["reason"] for i2, v in dkey.items()
                              if v["label"] == "generated" and i2 in calls and calls[i2]["call"] == "generated"]
            out.append(f"- Judge {i}: accuracy {correct}/{n} = {100 * correct / max(n, 1):.0f}%")
            for reason in gen_called_gen[:4]:
                out.append(f"  - tell: {reason}")
        out.append(f"- **Mean accuracy {100 * statistics.mean(accs):.0f}%** (target ≤ 65%; 50% = chance)")
    report = Path(__file__).resolve().parents[1] / "reports" / f"judge-{pair}.md"
    report.write_text("\n".join(out) + "\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
