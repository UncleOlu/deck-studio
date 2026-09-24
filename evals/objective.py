#!/usr/bin/env python3
"""Score harvested eval runs with the deterministic QA scripts.

For each case in evals/runs/<label>/, finds the delivered .pptx (and its
PDF) and runs: validate_pptx, storyline-lint (register from the case tags),
integrity-check, layout-check --pdf, copy-lint, and trace-check (against a
fresh ingest of the case input). Writes evals/reports/objective-<label>.md and
prints a summary. Counts come from each script's own summary line.

Usage: python3 objective.py <label> [<label> ...]
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

EVALS = Path(__file__).resolve().parent
SCRIPTS = EVALS.parent / "skills" / "premium-decks" / "scripts"
PY = sys.executable


def run(args: list[str]) -> tuple[int, str]:
    r = subprocess.run([PY, *args], capture_output=True, text=True, timeout=900)
    return r.returncode, (r.stdout + r.stderr).strip()


def count(pattern: str, text: str) -> int:
    m = re.search(pattern, text)
    return int(m.group(1)) if m else -1


def register_of(case: str) -> str:
    tags = json.loads((EVALS / "cases" / case / "case.yaml").read_text()).get("tags", [])
    return next((t for t in tags if t in ("consulting", "banking", "keynote")), "consulting")


def score_case(case_dir: Path, case: str) -> dict:
    decks = sorted(p for p in case_dir.rglob("*.pptx") if not p.name.startswith("~$"))
    if not decks:
        return {"case": case, "deck": None}
    deck = max(decks, key=lambda p: p.stat().st_mtime)
    pdf = deck.with_suffix(".pdf")
    reg = register_of(case)
    out = {"case": case, "deck": deck.name, "register": reg}
    code, text = run([str(SCRIPTS / "validate_pptx.py"), str(deck)])
    out["valid"] = code == 0
    _, text = run([str(SCRIPTS / "storyline-lint.py"), str(deck), "--register", reg])
    out["storyline_errors"] = count(r"(\d+) error\(s\)", text)
    _, text = run([str(SCRIPTS / "integrity-check.py"), str(deck)])
    out["integrity_errors"] = count(r"(\d+) error\(s\)", text)
    args = [str(SCRIPTS / "layout-check.py"), str(deck)] + (["--pdf", str(pdf)] if pdf.exists() else [])
    _, text = run(args)
    out["layout_errors"] = count(r"(\d+) error\(s\)", text)
    _, text = run([str(SCRIPTS / "copy-lint.py"), str(deck)])
    out["copy_warnings"] = max(count(r"(\d+) finding\(s\)", text), 0)
    inp = EVALS / "cases" / case / "input"
    with tempfile.TemporaryDirectory() as tmp:
        run([str(SCRIPTS / "ingest.py"), str(inp), "--out", tmp])
        # the skill's data contract: figures in a deck-data.json marked "illustrative" count as traced
        # (trace-check itself refuses a data file without that flag)
        data = deck.parent / "deck-data.json"
        extra = ["--data", str(data)] if data.exists() else []
        _, text = run([str(SCRIPTS / "trace-check.py"), str(deck), str(Path(tmp) / "facts.jsonl"), *extra])
    out["numbers"] = count(r"(\d+) number\(s\) checked", text)
    out["untraced"] = count(r"(\d+) problem\(s\)", text)
    slides = run([str(SCRIPTS / "storyline-lint.py"), str(deck), "--titles"])[1].splitlines()
    out["slides"] = len(slides)
    return out


def main() -> int:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    for label in sys.argv[1:]:
        root = EVALS / "runs" / label
        rows = [score_case(d / "with", d.name) for d in sorted(root.iterdir()) if (d / "with").is_dir()]
        cols = ["case", "register", "slides", "valid", "storyline_errors", "integrity_errors", "layout_errors",
                "copy_warnings", "numbers", "untraced"]
        lines = [f"# Objective QA — {label}", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        for r in rows:
            lines.append("| " + " | ".join(str(r.get(c, "—")) for c in cols) + " |")
        report = EVALS / "reports" / f"objective-{label}.md"
        report.write_text("\n".join(lines) + "\n")
        print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
