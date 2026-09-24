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
import stat
import sys
from collections.abc import Callable
from pathlib import Path

KEEP = {".pptx", ".pdf", ".html", ".json", ".js", ".md", ".jsonl", ".csv"}
MAX_BYTES = 60 * 1024 * 1024
RUNS = Path(__file__).resolve().parent / "runs"


def is_shared_temp(mode: int) -> bool:
    """World-writable with the sticky bit, as a system temp directory is."""
    return mode & 0o1777 == 0o1777


def owned_run_dir(trace: str, shared_temp: Callable[[int], bool] = is_shared_temp) -> Path | None:
    """The eval's kept run dir for a trace path, only if it is ours to open and delete: an `e-*`
    directory (not a symlink) owned by this user, directly inside a shared sticky temp directory.
    The path comes from a result file, so a string-prefix check is not enough."""
    t = Path(trace)
    if not t.is_absolute() or ".." in t.parts or len(t.parents) < 3:
        return None
    root = t.parents[1]
    try:
        st_root, st_parent = root.lstat(), root.parent.stat()
    except OSError:
        return None
    if not root.name.startswith("e-") or not stat.S_ISDIR(st_root.st_mode) or st_root.st_uid != os.getuid():
        return None
    if not shared_temp(st_parent.st_mode):
        return None
    return root


def unseal(root: Path) -> Path | None:
    """Make the sealed working directory readable: owner read and enter only."""
    sealed = root / "sealed"
    for p in (root, sealed, sealed / "home", sealed / "home" / "cwd"):
        if p.exists() and not p.is_symlink():
            os.chmod(p, 0o500)
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
                root = owned_run_dir(trace)
                if root is None:
                    print(f"{case['name']} [{arm}#{i}]: no kept dir ({run.get('error') or 'no trace'})")
                    continue
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
                (dest / "run.json").write_text(
                    json.dumps(
                        {k: run.get(k) for k in ("score", "passed", "turns", "costUsd", "durationSeconds", "error")}
                        | {"graders": run.get("graders")},
                        indent=2,
                    )
                )
                # Deleting the sealed tree needs owner read, write and enter on each directory: 0o700 is the
                # owner-only minimum, and the tree is removed on the next line.
                for p in root.rglob("*"):
                    if p.is_dir() and not p.is_symlink():
                        try:
                            # nosemgrep: python.lang.security.audit.insecure-file-permissions.insecure-file-permissions
                            os.chmod(p, 0o700)
                        except PermissionError:
                            pass
                shutil.rmtree(root, ignore_errors=True)
                print(f"{case['name']} [{arm}#{i}]: {copied} file(s) → {dest.relative_to(RUNS.parent)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
