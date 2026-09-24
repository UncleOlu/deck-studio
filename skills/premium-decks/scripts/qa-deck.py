#!/usr/bin/env python3
"""Run the whole QA gate on a deck and print one line per check.

  validate_pptx (Mode A) → render (pptx2pdf) → storyline-lint → trace-check (when
  a facts file is given) → integrity-check → layout-check --pdf → copy-lint
  → token validator (Mode B) → thumbnails.

Exit 0 only when every check reports zero errors. Warnings are listed but do
not fail the gate. Usage:
  python3 qa-deck.py deck.pptx --register consulting --facts brief/facts.jsonl [--data deck-data.json]
  python3 qa-deck.py deck.html --register keynote
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(HERE / script), *args], capture_output=True, text=True, timeout=1500)
    return r.returncode, (r.stdout + r.stderr).strip()


def summary(out: str) -> str:
    lines = [ln for ln in out.splitlines() if ln.strip()]
    return lines[-1] if lines else "(no output)"


def main() -> int:
    ap = argparse.ArgumentParser(description="Run every QA check on a deck.")
    ap.add_argument("deck")
    ap.add_argument("--register", choices=["keynote", "consulting", "banking"], required=True)
    ap.add_argument("--facts", help="brief/facts.jsonl from ingest.py (required for consulting/banking)")
    ap.add_argument("--data", help="deck-data.json with \"illustrative\": true")
    ap.add_argument("--no-render", action="store_true", help="skip rendering (layout collisions are then skipped)")
    args = ap.parse_args()
    deck = Path(args.deck)
    if not deck.exists():
        print(f"not found: {deck}")
        return 2
    pptx = deck.suffix.lower() == ".pptx"
    checks: list[tuple[str, int, str]] = []

    if pptx:
        code, out = run("validate_pptx.py", str(deck), "--native-charts")
        checks.append(("validate", code, summary(out)))
        pdf = deck.with_suffix(".pdf")
        if not args.no_render:
            code, out = run("pptx2pdf.py", str(deck))
            # a renderer that fails before a fallback succeeds leaves its error last on stderr; report the outcome
            outcome = re.search(r"^(Converted with .*|REPAIRED: .*|No renderer succeeded.*)$", out, re.M)
            checks.append(("render", code, outcome.group(1) if outcome else summary(out)))
    else:
        code, out = run("slide-token-validator.py", str(deck))
        checks.append(("tokens", code, summary(out)))
        pdf = None

    code, out = run("storyline-lint.py", str(deck), "--register", args.register)
    checks.append(("storyline", code, summary(out)))
    if args.facts:
        extra = ["--data", args.data] if args.data else []
        code, out = run("trace-check.py", str(deck), args.facts, *extra)
        checks.append(("trace", code, summary(out)))
    elif args.register != "keynote":
        checks.append(("trace", 1, "no --facts given: consulting/banking decks must trace every number"))
    code, out = run("integrity-check.py", str(deck))
    checks.append(("integrity", code, summary(out)))
    if pptx:
        la = [str(deck)] + (["--pdf", str(pdf)] if pdf and pdf.exists() else [])
        code, out = run("layout-check.py", *la)
        checks.append(("layout", code, summary(out)))
    code, out = run("copy-lint.py", str(deck))
    checks.append(("copy", 0, summary(out)))  # copy-lint findings are advisory
    if pptx and pdf and pdf.exists():
        code, out = run("deck_thumbnails.py", str(pdf))
        checks.append(("thumbnails", code, re.sub(r"\s+", " ", out)[:160]))

    failed = [c for c in checks if c[1] != 0]
    for name, code, line in checks:
        print(f"{'FAIL' if code else 'ok  '}  {name:<11} {line}")
    print(f"qa-deck: {len(checks) - len(failed)}/{len(checks)} checks passed"
          + ("" if not failed else f" — fix: {', '.join(c[0] for c in failed)}"))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
