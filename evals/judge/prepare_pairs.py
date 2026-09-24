#!/usr/bin/env python3
"""Prepare blind A/B pairs for the rubric judge.

For each case, takes the delivered .pptx from two harvested runs (e.g.
baseline-v1.3.3 and v1.4), re-renders both with the SAME renderer
(scripts/pptx2pdf.py) so render fidelity cannot favour either side, and
writes contact sheets to renders/judge/<pair>/<case>/<A|B>/. Which run is A
is decided by a seeded coin per case and recorded only in
~/deck-corpus/judge/keys/<pair>.json, outside anything the judges read.

Usage: python3 prepare_pairs.py <label-1> <label-2> [--seed 11]
"""

from __future__ import annotations

import argparse
import json
import random
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills" / "premium-decks" / "scripts"
sys.path.insert(0, str(SCRIPTS))
import deck_thumbnails  # noqa: E402
import pptx2pdf  # noqa: E402

RUNS = ROOT / "evals" / "runs"


def deck_of(run_dir: Path) -> Path | None:
    decks = [p for p in run_dir.rglob("*.pptx") if not p.name.startswith("~$") and ".render-" not in p.name]
    return max(decks, key=lambda p: p.stat().st_mtime) if decks else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("first")
    ap.add_argument("second")
    ap.add_argument("--seed", type=int, default=11)
    args = ap.parse_args()
    rng = random.Random(args.seed)  # noqa: S311 — reproducible blinding, not security
    pair = f"{args.first}__vs__{args.second}"
    out = ROOT / "renders" / "judge" / pair
    keys = Path.home() / "deck-corpus" / "judge" / "keys"  # outside the tree the judges read
    keys.mkdir(parents=True, exist_ok=True)
    key = {}
    for case_dir in sorted((RUNS / args.first).iterdir()):
        case = case_dir.name
        decks = {lab: deck_of(RUNS / lab / case / "with") for lab in (args.first, args.second)}
        if not all(decks.values()):
            print(f"skip {case}: missing deck in {[k for k, v in decks.items() if not v]}")
            continue
        order = [args.first, args.second]
        rng.shuffle(order)
        key[case] = {"A": order[0], "B": order[1]}
        for side, lab in zip("AB", order, strict=True):
            d = out / case / side
            if ((d / "deck.pdf").exists() and list(d.glob("deck-grid-*.jpg"))) or (d / "UNOPENABLE").exists():
                continue  # resumable: this side is already rendered (the seeded order is unchanged)
            shutil.rmtree(d, ignore_errors=True)
            d.mkdir(parents=True)
            pptx = d / "deck.pptx"
            src = decks[lab]
            assert src is not None  # guarded by the all(decks.values()) check above
            shutil.copy2(src, pptx)
            for _attempt in range(2):  # PowerPoint occasionally refuses an open; one retry
                rc = pptx2pdf.convert(str(pptx))
                if rc == 3:  # rendered, but only after PowerPoint repaired the file: a defect of that deck
                    repaired = Path.home() / "deck-corpus" / "judge" / "keys" / f"{pair}.repaired.txt"
                    with repaired.open("a") as fh:
                        fh.write(f"{case}\t{lab}\n")
                if rc in (0, 3):
                    break
            else:  # PowerPoint will not open it even after a retry: a hard defect of that deck
                failed = Path.home() / "deck-corpus" / "judge" / "keys" / f"{pair}.unopenable.txt"
                with failed.open("a") as fh:
                    fh.write(f"{case}\t{lab}\n")
                print(f"UNOPENABLE {case}/{side} ({lab}); recorded as a defect")
                (d / "UNOPENABLE").write_text("")  # no label here: judges can read this folder
                continue
            if (d / "UNOPENABLE").exists():
                continue
            deck_thumbnails.make_grids(d / "deck.pdf", cols=2, rows=2, width=760)
            pptx.unlink()  # judges see renders only
        print(f"{case}: A={order[0]} B={order[1]}")
        (keys / f"{pair}.json").write_text(json.dumps(key, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
