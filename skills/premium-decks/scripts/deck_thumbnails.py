#!/usr/bin/env python3
"""Render a deck to a labelled thumbnail grid for fast visual review.

Input: a .pptx (rendered to PDF first with pptx2pdf.py) or a .pdf.
Output: <stem>-grid-NN.jpg, each a grid of up to cols x rows slides labelled
with their slide number. Needs poppler's pdftoppm and Pillow.

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

LABEL_H = 24
GAP = 10


def to_pdf(deck: Path) -> Path:
    if deck.suffix.lower() == ".pdf":
        return deck
    script = Path(__file__).with_name("pptx2pdf.py")
    subprocess.run([sys.executable, str(script), str(deck)], check=True, timeout=900)
    pdf = deck.with_suffix(".pdf")
    if not pdf.exists():
        raise SystemExit(f"render produced no PDF next to {deck}")
    return pdf


def main() -> int:
    ap = argparse.ArgumentParser(description="Labelled thumbnail grid of a deck.")
    ap.add_argument("deck")
    ap.add_argument("--cols", type=int, default=3)
    ap.add_argument("--rows", type=int, default=3)
    ap.add_argument("--width", type=int, default=520, help="thumbnail width in px")
    args = ap.parse_args()
    if not shutil.which("pdftoppm"):
        raise SystemExit("pdftoppm not found: install poppler (brew install poppler / apt install poppler-utils)")
    deck = Path(args.deck).resolve()
    pdf = to_pdf(deck)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "60", "-jpeg", str(pdf), str(Path(tmp) / "p")], check=True, timeout=900)
        pages = sorted(Path(tmp).glob("p-*.jpg"), key=lambda p: int(p.stem.split("-")[-1]))
        per = args.cols * args.rows
        outputs = []
        for start in range(0, len(pages), per):
            group = pages[start:start + per]
            thumbs = []
            for p in group:
                with Image.open(p) as im:
                    im = im.convert("RGB")
                    thumbs.append(im.resize((args.width, round(im.height * args.width / im.width))))
            th = max(t.height for t in thumbs) + LABEL_H
            rows = (len(thumbs) + args.cols - 1) // args.cols
            sheet = Image.new("RGB", (args.cols * (args.width + GAP) + GAP, rows * (th + GAP) + GAP), "white")
            draw = ImageDraw.Draw(sheet)
            for i, t in enumerate(thumbs):
                x = GAP + (i % args.cols) * (args.width + GAP)
                y = GAP + (i // args.cols) * (th + GAP)
                draw.text((x, y + 5), f"Slide {start + i + 1}", fill=(40, 40, 40))
                sheet.paste(t, (x, y + LABEL_H))
                draw.rectangle([x - 1, y + LABEL_H - 1, x + t.width, y + LABEL_H + t.height], outline=(200, 200, 200))
            out = deck.with_name(f"{deck.stem}-grid-{start // per + 1:02d}.jpg")
            sheet.save(out, quality=85)
            outputs.append(out)
    for o in outputs:
        print(o)
    return 0


if __name__ == "__main__":
    sys.exit(main())
