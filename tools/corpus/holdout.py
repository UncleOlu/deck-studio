#!/usr/bin/env python3
"""Flag the eval hold-out: a stable ~20% of corpus decks, chosen by content hash.

Rule: holdout = int(sha256[:8], 16) % 5 == 0. The rule depends only on the
file's own hash, so adding decks later never moves an existing deck in or out
of the hold-out. No codebook rule may cite a hold-out deck; the blind
discrimination test uses only hold-out decks.

Usage: python3 holdout.py [--corpus ~/deck-corpus]   (rewrites the manifests in place)
"""

from __future__ import annotations

import argparse
import collections
import json
from pathlib import Path

MANIFESTS = ("manifest.jsonl", "manifest-aggregators.jsonl", "manifest-public.jsonl")


def is_holdout(sha: str) -> bool:
    return int(sha[:8], 16) % 5 == 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(Path.home() / "deck-corpus"))
    args = ap.parse_args()
    corpus = Path(args.corpus).expanduser()
    tally: collections.Counter[tuple[str, bool]] = collections.Counter()
    for name in MANIFESTS:
        path = corpus / name
        if not path.exists():
            continue
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        for row in rows:
            row["holdout"] = is_holdout(row["sha256"])
            tally[(row["genre"], row["holdout"])] += 1
        path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    for genre in sorted({g for g, _ in tally}):
        held, kept = tally[(genre, True)], tally[(genre, False)]
        print(f"{genre:<24} derive {kept:>3}  hold-out {held:>3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
