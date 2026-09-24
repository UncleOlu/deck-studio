#!/usr/bin/env python3
"""Convert a .pptx to PDF for visual QA.

Tries renderers in order: LibreOffice (soffice) -> Microsoft PowerPoint
(AppleScript) -> Keynote (AppleScript). PowerPoint and Keynote are
macOS-only fallbacks for machines without LibreOffice.

Usage: python3 pptx2pdf.py deck.pptx [out.pdf]
Then:  python3 deck_thumbnails.py out.pdf   (contact sheets of every slide)
"""

from __future__ import annotations

import glob
import os
import re
import shutil
import subprocess
import sys
import uuid
from collections.abc import Callable

# Default install locations when soffice is not on PATH (macOS app bundle, Linux packages, Windows).
SOFFICE_CANDIDATES = (
    "/Applications/LibreOffice.app/Contents/MacOS/soffice",
    "/usr/lib/libreoffice/program/soffice",
    "/opt/libreoffice/program/soffice",
    "/snap/bin/libreoffice",
    r"C:\Program Files\LibreOffice\program\soffice.exe",
    r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
)


def find_soffice() -> str | None:
    exe = shutil.which("soffice") or shutil.which("libreoffice")
    if exe:
        return exe
    found = next((c for c in SOFFICE_CANDIDATES if os.path.isfile(c)), None)
    if found:
        return found
    versioned = sorted(glob.glob("/opt/libreoffice*/program/soffice"), reverse=True)  # upstream Linux .deb/.rpm
    return versioned[0] if versioned else None


def soffice_convert(src: str, out_pdf: str) -> bool:
    exe = find_soffice()
    if not exe:
        return False
    outdir = os.path.dirname(os.path.abspath(out_pdf)) or "."
    r = subprocess.run(
        [exe, "--headless", "--convert-to", "pdf", "--outdir", outdir, src],
        capture_output=True,
        timeout=300,
    )
    produced = os.path.join(outdir, os.path.splitext(os.path.basename(src))[0] + ".pdf")
    if r.returncode == 0 and os.path.exists(produced):
        if os.path.abspath(produced) != os.path.abspath(out_pdf):
            shutil.move(produced, out_pdf)
        return True
    return False


def applescript_convert(app: str, src: str, out_pdf: str) -> bool:
    if sys.platform != "darwin" or not os.path.exists(f"/Applications/{app}.app"):
        return False
    src = os.path.abspath(src)
    out_pdf = os.path.abspath(out_pdf)
    # Paths reach AppleScript as argv, never inside the script text, so a quote in a path cannot inject code.
    if app == "Microsoft PowerPoint":
        script = """
        on run argv
            with timeout of 600 seconds
                tell application "Microsoft PowerPoint"
                    open POSIX file (item 1 of argv)
                    delay 1
                    set docName to name of active presentation
                    save active presentation in POSIX file (item 2 of argv) as save as PDF
                    close active presentation saving no
                    return docName
                end tell
            end timeout
        end run"""
    else:  # Keynote
        script = """
        on run argv
            tell application "Keynote"
                set doc to open POSIX file (item 1 of argv)
                delay 1
                export doc to POSIX file (item 2 of argv) as PDF
                close doc saving no
            end tell
        end run"""
    try:
        r = subprocess.run(["osascript", "-e", script, src, out_pdf], capture_output=True, timeout=660)
    except subprocess.TimeoutExpired:
        return False
    if r.returncode != 0:
        sys.stderr.write(r.stderr.decode(errors="replace") + "\n")
        close_render_copy(app, os.path.basename(src))
        return False
    if "repaired" in r.stdout.decode(errors="replace").lower():
        # PowerPoint opened the file only after repairing it: a real defect in the deck. The PDF shows the
        # repaired version; fail so QA reports it.
        REPAIRED.append(src)
    return os.path.exists(out_pdf)


REPAIRED: list[str] = []


def close_render_copy(app: str, name: str) -> None:
    """After a failed export, close our render copy so it cannot block the next open."""
    if app != "Microsoft PowerPoint" or not re.fullmatch(r"[\w.\- ]+\.pptx", name):
        return
    script = (
        'on run argv\nwith timeout of 30 seconds\ntell application "Microsoft PowerPoint" to close '
        "(every presentation whose name is (item 1 of argv)) saving no\nend timeout\nend run"
    )
    subprocess.run(["osascript", "-e", script, name], capture_output=True, timeout=60)


def convert(src: str, out_pdf: str | None = None) -> int:
    """Render src to PDF. Returns 0 (rendered), 3 (rendered after a PowerPoint repair), 1 (no
    renderer succeeded), or 2 (input not found). Importable, so callers need no subprocess."""
    REPAIRED.clear()
    pdf: str = out_pdf or os.path.splitext(src)[0] + ".pdf"
    if not os.path.exists(src):
        print(f"Input not found: {src}")
        return 2
    if os.path.exists(pdf):
        os.remove(pdf)
    # Render a uniquely named copy. PowerPoint and Keynote export a document that is already open
    # from memory, so re-rendering the same file name after a rebuild can silently export the stale
    # version. A fresh name forces a fresh open.
    stem, ext = os.path.splitext(src)
    fresh = f"{stem}.render-{uuid.uuid4().hex[:8]}{ext}"
    shutil.copyfile(src, fresh)
    try:
        renderers: list[tuple[str, Callable[[], bool]]] = [
            ("LibreOffice", lambda: soffice_convert(fresh, pdf)),
            (
                "Microsoft PowerPoint",
                lambda: (
                    applescript_convert("Microsoft PowerPoint", fresh, pdf)
                    or applescript_convert("Microsoft PowerPoint", fresh, pdf)
                ),
            ),  # one retry after cleanup
            ("Keynote", lambda: applescript_convert("Keynote", fresh, pdf)),
        ]
        for name, fn in renderers:
            if fn():
                if REPAIRED:
                    print(
                        f"REPAIRED: PowerPoint had to repair {os.path.basename(src)} before it would open. "
                        "The PDF shows the repaired file; fix the generator (see pptx-mode.md, 'Never hand-edit "
                        "OOXML')."
                    )
                    return 3
                print(f"Converted with {name}: {pdf}")
                return 0
    finally:
        os.remove(fresh)
    print(
        "No renderer succeeded. Install LibreOffice, or grant osascript Automation permission for PowerPoint/Keynote."
    )
    return 1


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    return convert(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)


if __name__ == "__main__":
    sys.exit(main())
