#!/usr/bin/env python3
"""Write research/corpus-sources.md from the corpus manifests: counts, method, and one row per deck (URL only)."""
from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = Path.home() / "deck-corpus"


def main() -> int:
    rows = []
    for name in ("manifest.jsonl", "manifest-aggregators.jsonl", "manifest-public.jsonl"):
        p = CORPUS / name
        if p.exists():
            rows += [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    genre = collections.Counter(r["genre"] for r in rows)
    held = collections.Counter(r["genre"] for r in rows if r["holdout"])
    strata = collections.Counter(r["firm_stratum"] for r in rows).most_common()
    out = ["# Corpus sources", "",
           f"{len(rows)} public decks studied for `corpus-findings.md`. The files are not in this repository; each row",
           "gives the public URL. Rows marked **hold-out** were never coded and are reserved for the blind",
           "discrimination test.", "", "## Counts", "", "| Genre | Decks | Hold-out |", "|---|---|---|"]
    out += [f"| {g} | {genre[g]} | {held[g]} |" for g in sorted(genre)]
    out += ["", "Firm stratum: " + ", ".join(f"{k} {v}" for k, v in strata), "", "## Collection method", "",
            "- **SEC EDGAR**: `tools/corpus/edgar_fetch.py` — full-text search of SC 13E3 filings naming each "
            "of 12 "
            "advisors, then the EX-99.(c) exhibits with at least 6 page images; at most 5 books per advisor and 2 per "
            "company per run.",
            "- **Aggregators** (Slideworks, SlideScience, Analyst Academy, Slidebook.io, 10X EBITDA, "
            "Alexander Jarvis): "
            "free, public material only, downloaded from the original public host where one existed. SlideScience "
            "returned 403; Slidebook.io and Alexander Jarvis gate their files, so they contributed notes only.",
            "- **Public-sector client decks**: engagement deliverables published by public bodies (legislatures, "
            "councils, regulators, agencies).",
            "", "## Decks", "", "| Genre | Firm | Year | Deck type | Source | Hold-out |", "|---|---|---|---|---|---|"]
    for r in sorted(rows, key=lambda r: (r["genre"], r["firm"], str(r["date"]))):
        out.append(f"| {r['genre']} | {r['firm']} | {str(r['date'])[:4]} | {r.get('deck_type', '')} | <{r['url']}> | "
                   f"{'hold-out' if r['holdout'] else ''} |")
    pitch_path = CORPUS / "manifest-pitch.jsonl"
    pitch = [json.loads(line) for line in pitch_path.read_text().splitlines() if line.strip()] \
        if pitch_path.exists() else []
    if pitch:  # a separate study: kept out of the counts above and out of corpus-stats.md
        out += ["", "## Pitch-style discussion materials (added 2026-09-23)", "",
                f"{len(pitch)} more public decks studied for `pitchbook-findings.md`. They are not counted in the "
                f"{len(rows)} above or used in",
                "`corpus-stats.md`. None is hold-out; all were coded. Collection: EDGAR full-text search of SC 13E3 / "
                "SC 13E3/A / SC TO-T",
                "filings for pitch phrases (process timeline, buyer universe, strategic alternatives), then the "
                "EX-99.(c) exhibits.",
                "", "| Genre | Firm | Year | Deck type | Source | Hold-out |", "|---|---|---|---|---|---|"]
        for r in sorted(pitch, key=lambda r: (r["genre"], r["firm"], str(r["date"]))):
            out.append(f"| {r['genre']} | {r['firm']} | {str(r['date'])[:4]} | {r.get('deck_type', '')} | "
                       f"<{r['url']}> | |")
    (ROOT / "research" / "corpus-sources.md").write_text("\n".join(out) + "\n")
    print(f"{len(rows)} decks → research/corpus-sources.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
