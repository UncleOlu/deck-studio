#!/usr/bin/env python3
"""Render a deck to a labelled thumbnail grid for fast visual review.

Input: a .pptx (rendered to PDF first with pptx2pdf.py) or a .pdf.
Output: <stem>-grid-NN.jpg, each a grid of up to cols x rows slides labelled
with their slide number. Uses poppler's pdftoppm when installed, else pypdfium2; needs Pillow.

Usage: python3 deck_thumbnails.py deck.pptx|deck.pdf [--cols 3] [--rows 3] [--width 520]
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pptx2pdf  # noqa: E402

LABEL_H = 24
GAP = 10


def to_pdf(deck: Path) -> Path:
    if deck.suffix.lower() == ".pdf":
        return deck
    if pptx2pdf.convert(str(deck)) not in (0, 3):
        raise SystemExit(f"could not render {deck} to PDF")
    pdf = deck.with_suffix(".pdf")
    if not pdf.exists():
        raise SystemExit(f"render produced no PDF next to {deck}")
    return pdf


def make_grids(deck: Path, cols: int = 3, rows: int = 3, width: int = 520) -> list[Path]:
    """Write <stem>-grid-NN.jpg beside the deck and return their paths."""
    deck = deck.resolve()
    pdf = to_pdf(deck)
    with tempfile.TemporaryDirectory() as tmp:
        if shutil.which("pdftoppm"):
            subprocess.run(["pdftoppm", "-r", "60", "-jpeg", str(pdf), str(Path(tmp) / "p")], check=True, timeout=900)
        else:  # no poppler: pypdfium2 (a pip dependency) renders the same pages
            import pypdfium2 as pdfium

            doc = pdfium.PdfDocument(str(pdf))
            try:
                for n, page in enumerate(doc, start=1):
                    page.render(scale=60 / 72).to_pil().convert("RGB").save(Path(tmp) / f"p-{n}.jpg", quality=90)
            finally:
                doc.close()
        pages = sorted(Path(tmp).glob("p-*.jpg"), key=lambda p: int(p.stem.split("-")[-1]))
        per = cols * rows
        outputs = []
        for start in range(0, len(pages), per):
            group = pages[start : start + per]
            thumbs: list[Image.Image] = []
            for p in group:
                with Image.open(p) as src:
                    rgb = src.convert("RGB")
                    thumbs.append(rgb.resize((width, round(rgb.height * width / rgb.width))))
            th = max(t.height for t in thumbs) + LABEL_H
            n_rows = (len(thumbs) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * (width + GAP) + GAP, n_rows * (th + GAP) + GAP), "white")
            draw = ImageDraw.Draw(sheet)
            for i, t in enumerate(thumbs):
                x = GAP + (i % cols) * (width + GAP)
                y = GAP + (i // cols) * (th + GAP)
                draw.text((x, y + 5), f"Slide {start + i + 1}", fill=(40, 40, 40))
                sheet.paste(t, (x, y + LABEL_H))
                draw.rectangle([x - 1, y + LABEL_H - 1, x + t.width, y + LABEL_H + t.height], outline=(200, 200, 200))
            out = deck.with_name(f"{deck.stem}-grid-{start // per + 1:02d}.jpg")
            sheet.save(out, quality=85)
            outputs.append(out)
    return outputs


def main() -> int:
    ap = argparse.ArgumentParser(description="Labelled thumbnail grid of a deck.")
    ap.add_argument("deck")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--width", type=int, default=520, help="thumbnail width in px")
    args = ap.parse_args()
    for o in make_grids(Path(args.deck), args.cols, args.rows, args.width):
        print(o)
    return 0


if __name__ == "__main__":
    sys.exit(main())
