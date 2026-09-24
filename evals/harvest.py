#!/usr/bin/env python3
"""Copy each eval run's deliverables out of its kept temp dir, then delete the temp dir.

`claude plugin eval --keep-temp --json result.json` leaves one /private/tmp/e-XXXX
dir per run, with the agent's working directory sealed (mode 000) under
sealed/home/cwd. This script unseals only that path, copies the deliverables
(.pptx .pdf .html .json .js .md and brief/) plus the trace into
evals/runs/<label>/<case>/, and removes the temp dir.

Usage: python3 harvest.py result.json <label>
"""
from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

KEEP = {".pptx", ".pdf", ".html", ".json", ".js", ".md", ".jsonl", ".csv"}
MAX_BYTES = 60 * 1024 * 1024
RUNS = Path(__file__).resolve().parent / "runs"


def unseal(root: Path) -> Path | None:
    sealed = root / "sealed"
    for p in (root, sealed, sealed / "home", sealed / "home" / "cwd"):
        if p.exists() and not p.is_symlink():
            os.chmod(p, 0o700)
    cwd = sealed / "home" / "cwd"
    return cwd if cwd.is_dir() else None


def main() -> int:
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    result = json.loads(Path(sys.argv[1]).read_text())
    label = sys.argv[2]
    if not label.replace("-", "").replace(".", "").replace("_", "").isalnum():
        sys.exit("label must be alphanumeric with - . _")
    for case in result["cases"]:
        for arm, runs in case["arms"].items():
            for i, run in enumerate(runs):
                trace = run.get("tracePath") or ""
                if not trace.startswith(("/private/tmp/e-", "/tmp/e-")):  # noqa: S108 — a prefix check, not a temp file
                    print(f"{case['name']} [{arm}#{i}]: no kept dir ({run.get('error') or 'no trace'})")
                    continue
                root = Path(trace).parents[1]
                dest = RUNS / label / case["name"] / (arm if len(runs) == 1 else f"{arm}-{i}")
                dest.mkdir(parents=True, exist_ok=True)
                shutil.copy2(trace, dest / "trace.jsonl")
                cwd = unseal(root)
                copied = 0
                if cwd:
                    for f in cwd.rglob("*"):
                        rel = f.relative_to(cwd)
                        if f.is_symlink() or not f.is_file() or "node_modules" in rel.parts or ".venv" in rel.parts:
                            continue
                        if f.suffix.lower() in KEEP and f.stat().st_size <= MAX_BYTES:
                            (dest / rel).parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(f, dest / rel)
                            copied += 1
                (dest / "run.json").write_text(json.dumps({k: run.get(k) for k in
                                                           ("score", "passed", "turns", "costUsd", "durationSeconds",
                                                            "error")} | {"graders": run.get("graders")}, indent=2))
                for p in root.rglob("*"):
                    if p.is_dir() and not p.is_symlink():
                        try:
                            os.chmod(p, 0o700)
                        except PermissionError:
                            pass
                shutil.rmtree(root, ignore_errors=True)
                print(f"{case['name']} [{arm}#{i}]: {copied} file(s) → {dest.relative_to(RUNS.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
