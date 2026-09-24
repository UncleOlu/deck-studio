#!/usr/bin/env python3
"""Run the whole QA gate on a deck and report each check as PASS, WARN, SKIP, or FAIL.

  validate_pptx (Mode A) → render (pptx2pdf) → storyline-lint → trace-check (when
  a facts file is given) → integrity-check → layout-check (collisions need a PDF
  rendered in this run) → copy-lint → token validator (Mode B) → thumbnails.

  PASS  the check ran and found nothing
  WARN  it ran and found something advisory (copy findings, cited-but-unverified numbers)
  SKIP  it did not run (no render, HTML deck, no facts file for a keynote deck)
  FAIL  it found an error, or the checker itself crashed

The summary says whether the automated checks were complete, and always reminds
that the visual review (looking at every rendered slide) is a separate, manual step.
Exit 1 on any FAIL; with --strict, also on any SKIP. Usage:
  python3 qa-deck.py deck.pptx --register consulting --facts brief/facts.jsonl [--data deck-data.json]
  python3 qa-deck.py deck.html --register keynote
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent


def run(script: str, *args: str) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(HERE / script), *args], capture_output=True, text=True, timeout=1500)
    return r.returncode, (r.stdout + r.stderr).strip()


def summary(out: str) -> str:
    lines = [ln for ln in out.splitlines() if ln.strip()]
    return lines[-1] if lines else "(no output)"


WARN_COUNT = re.compile(r"(\d+) (?:warning|finding)\(s\)")


def classify(name: str, code: int, out: str, advisory: bool = False) -> tuple[str, str]:
    """(status, one-line detail) for a checker's exit code and output."""
    if "Traceback (most recent call last)" in out:
        return "FAIL", f"the checker crashed: {summary(out)}"
    line = summary(out)
    if code not in (0, 1):
        return "FAIL", f"exited with code {code}: {line}"
    if code == 1:
        return ("WARN" if advisory else "FAIL"), line
    m = WARN_COUNT.search(line)
    return ("WARN" if m and int(m.group(1)) > 0 else "PASS"), line


def main() -> int:
    ap = argparse.ArgumentParser(description="Run every QA check on a deck.")
    ap.add_argument("deck")
    ap.add_argument("--register", choices=["keynote", "consulting", "banking"], required=True)
    ap.add_argument("--facts", help="brief/facts.jsonl from ingest.py (required for consulting/banking)")
    ap.add_argument("--data", help='deck-data.json with "illustrative": true')
    ap.add_argument("--no-render", action="store_true", help="skip rendering (collision checks are then skipped)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any check was skipped")
    args = ap.parse_args()
    deck = Path(args.deck)
    if not deck.exists():
        print(f"not found: {deck}")
        return 2
    started = time.time()
    pptx = deck.suffix.lower() == ".pptx"
    rows: list[tuple[str, str, str]] = []  # (status, check, detail)

    def check(name: str, script: str, *argv: str, advisory: bool = False) -> str:
        code, out = run(script, *argv)
        status, detail = classify(name, code, out, advisory)
        rows.append((status, name, detail))
        return status

    fresh_pdf: Path | None = None
    if pptx:
        check("validate", "validate_pptx.py", str(deck), "--native-charts")
        pdf = deck.with_suffix(".pdf")
        if args.no_render:
            rows.append(("SKIP", "render", "--no-render given; no PDF from this run"))
        else:
            code, out = run("pptx2pdf.py", str(deck))
            # a renderer that fails before a fallback succeeds leaves its error last on stderr; report the outcome
            outcome = re.search(r"^(Converted with .*|REPAIRED: .*|No renderer succeeded.*)$", out, re.M)
            status, _ = classify("render", code if code in (0, 1) else 1, out)
            rows.append((status, "render", outcome.group(1) if outcome else summary(out)))
            # only a PDF written by this run: an older one would check the previous build's layout
            if status == "PASS" and pdf.exists() and pdf.stat().st_mtime >= started - 1:
                fresh_pdf = pdf
    else:
        check("tokens", "slide-token-validator.py", str(deck))
        rows.append(("SKIP", "render", "HTML deck: review it in a browser at 1280×720 and 1024×576"))

    check("storyline", "storyline-lint.py", str(deck), "--register", args.register)
    if args.facts:
        extra = ["--data", args.data] if args.data else []
        check("trace", "trace-check.py", str(deck), args.facts, *extra)
    elif args.register != "keynote":
        rows.append(("FAIL", "trace", "no --facts given: consulting/banking decks must trace every number"))
    else:
        rows.append(("SKIP", "trace", "keynote deck without --facts"))
    check("integrity", "integrity-check.py", str(deck))
    if pptx:
        code, out = run("layout-check.py", str(deck), *(["--pdf", str(fresh_pdf)] if fresh_pdf else []))
        status, detail = classify("layout", code, out)
        rows.append((status, "layout", detail))
        if not fresh_pdf:
            rows.append(("SKIP", "collisions", "needs a PDF rendered in this run"))
        elif "SKIPPED:" in out:
            rows.append(("SKIP", "collisions", "no PDF text reader: install requirements.txt"))
    else:
        rows.append(("SKIP", "collisions", "HTML deck: check overflow in the browser screenshots"))
    check("copy", "copy-lint.py", str(deck), advisory=True)  # copy findings are advice; a crash still fails
    grids = ""
    if fresh_pdf:
        code, out = run("deck_thumbnails.py", str(fresh_pdf))
        status, _ = classify("thumbnails", code, out)
        grids = re.sub(r"\s+", " ", out)[:160]
        rows.append((status, "thumbnails", grids))

    for status, name, detail in rows:
        print(f"{status:<5} {name:<11} {detail}")
    count = {k: sum(r[0] == k for r in rows) for k in ("PASS", "WARN", "SKIP", "FAIL")}
    skipped = [r[1] for r in rows if r[0] == "SKIP"]
    failed = [r[1] for r in rows if r[0] == "FAIL"]
    print(
        f"qa-deck: {count['PASS']} passed, {count['WARN']} with warnings, {count['SKIP']} skipped, "
        f"{count['FAIL']} failed" + (f" — fix: {', '.join(failed)}" if failed else "")
    )
    print("  automated checks: " + ("complete" if not skipped else f"incomplete — not run: {', '.join(skipped)}"))
    print(
        "  visual review: not automated — look at every rendered slide"
        + (f" ({grids.split()[0]} …)" if grids else "")
        + " before sending"
    )
    return 1 if failed or (args.strict and skipped) else 0


if __name__ == "__main__":
    sys.exit(main())
