#!/usr/bin/env python3
"""Check that this machine can run premium-decks, and say how to fix what is missing.

Required: Python >= 3.9 with python-pptx, lxml, defusedxml, Pillow, openpyxl,
pypdf, pypdfium2; Node >= 18 and the vendored pptxgenjs (Mode A). Optional: a
renderer (LibreOffice, or PowerPoint/Keynote on macOS) for visual QA; poppler
is used when present but no longer needed. Exit 1 when a required item is missing.

Usage: python3 doctor.py [--install]   (--install pip-installs requirements.txt first)
"""

from __future__ import annotations

import importlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

HERE = Path(__file__).resolve().parent
VENDOR = HERE.parent / "templates" / "lib" / "vendor" / "node_modules" / "pptxgenjs"
REQS = HERE.parents[2] / "requirements.txt"  # plugin root
MODULES = {  # import name -> pip name
    "pptx": "python-pptx",
    "lxml": "lxml",
    "defusedxml": "defusedxml",
    "PIL": "Pillow",
    "openpyxl": "openpyxl",
    "pypdf": "pypdf",
    "pypdfium2": "pypdfium2",
}


def _install_hint(tool: str) -> str:
    if sys.platform == "darwin":
        return f"brew install {tool}"
    if sys.platform.startswith("win"):
        return {
            "poppler": "install poppler for Windows and add its bin/ to PATH",
            "libreoffice": "install LibreOffice from libreoffice.org",
        }.get(tool, tool)
    return f"apt install {'poppler-utils' if tool == 'poppler' else tool}"


def check() -> list[tuple[str, bool, bool, str]]:
    """Rows of (item, ok, required, detail)."""
    rows = []
    py_ok = sys.version_info >= (3, 9)
    rows.append(("Python >= 3.9", py_ok, True, sys.version.split()[0]))
    for mod, pip_name in MODULES.items():
        try:
            m = importlib.import_module(mod)
            rows.append((pip_name, True, True, getattr(m, "__version__", "installed")))
        except ImportError:
            fix = f"-r {REQS}" if REQS.is_file() else " ".join(MODULES.values())
            rows.append((pip_name, False, True, f"{sys.executable} -m pip install {fix}"))
    node = shutil.which("node")
    if node:
        out = subprocess.run([node, "--version"], capture_output=True, text=True, timeout=30).stdout.strip()
        major = int(ver.group(1)) if (ver := re.match(r"v(\d+)", out)) else 0
        rows.append(("Node >= 18", major >= 18, True, out or "unknown version"))
    else:
        rows.append(("Node >= 18", False, True, "install Node 18+ (nodejs.org)"))
    rows.append(
        (
            "pptxgenjs (vendored)",
            VENDOR.is_dir(),
            True,
            "present" if VENDOR.is_dir() else f"missing: {VENDOR} — reinstall the plugin",
        )
    )
    import pptx2pdf

    office = pptx2pdf.find_soffice()
    mac_apps = [
        a
        for a in ("Microsoft PowerPoint", "Keynote")
        if sys.platform == "darwin" and Path(f"/Applications/{a}.app").exists()
    ]
    renderer = office or ", ".join(mac_apps)
    rows.append(
        ("renderer (LibreOffice/PowerPoint/Keynote)", bool(renderer), False, renderer or _install_hint("libreoffice"))
    )
    poppler = shutil.which("pdftotext") and shutil.which("pdftoppm")
    rows.append(
        (
            "poppler (optional; pypdfium2 covers it)",
            True,
            False,
            "installed" if poppler else "not installed: pypdfium2 renders thumbnails and reads collisions",
        )
    )
    return rows


def install() -> int:
    """pip-install the pinned requirements into the Python running this script."""
    if not REQS.is_file():
        print(f"doctor: {REQS} not found")
        return 1
    in_venv = sys.prefix != sys.base_prefix
    cmd = [sys.executable, "-m", "pip", "install", "-r", str(REQS)] + ([] if in_venv else ["--user"])
    print("doctor: running " + " ".join(cmd))
    return subprocess.run(cmd, check=False, timeout=900).returncode


def main() -> int:
    if "--install" in sys.argv[1:]:
        code = install()
        if code:
            print(f"doctor: pip exited with code {code}")
            return code
    rows = check()
    width = max(len(r[0]) for r in rows)
    for item, ok, required, detail in rows:
        mark = "ok  " if ok else ("MISS" if required else "warn")
        print(f"[{mark}] {item:<{width}}  {detail}")
    missing = [r[0] for r in rows if r[2] and not r[1]]
    if missing:
        print(f"doctor: {len(missing)} required item(s) missing: {', '.join(missing)}")
        return 1
    optional = [r[0] for r in rows if not r[2] and not r[1]]
    print("doctor: ready" + (f" (visual QA limited: {', '.join(optional)})" if optional else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
