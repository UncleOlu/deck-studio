#!/usr/bin/env python3
"""Render corpus decks to page images, sample pages, and build labelled contact sheets.

Development tool — reads and writes only inside the local corpus directory.

For every row in the merged manifests:
  - PDF sources: `pdftoppm -r 100 -jpeg` for pages, `pdftotext -layout` for text.
  - EDGAR sources: the page images already exist; they are downscaled copies.
  - Sampling: pages 1-4, then evenly spaced pages up to --sample pages total.
  - Contact sheets: sampled pages in 2x2 grids, each cell labelled with its
    page number, so a coder reads 4 pages per image.

Writes <corpus>/renders/<deck-id>/{pages/,sheets/,text.txt,sample.json}.
Usage: python3 render.py [--corpus ~/deck-corpus] [--sample 12] [--only ID_SUBSTRING]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw

MAX_W = 1100
CELL_W = 800
SAFE_ID = re.compile(r"^[a-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def load_manifests(corpus: Path) -> list[dict[str, Any]]:
    rows, seen = [], set()
    for name in ("manifest.jsonl", "manifest-aggregators.jsonl", "manifest-public.jsonl"):
        path = corpus / name
        if not path.exists():
            continue
        for line in path.read_text().splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("sha256") in seen:
                continue
            seen.add(row.get("sha256"))
            rows.append(row)
    return rows


def contained(root: Path, rel: str) -> Path:
    target = (root / rel).resolve()
    if root.resolve() not in target.parents:
        raise ValueError(f"path escapes corpus: {rel}")
    return target


def sample_pages(n: int, k: int) -> list[int]:
    head = list(range(1, min(n, 4) + 1))
    rest = n - len(head)
    want = max(0, min(k - len(head), rest))
    if want == 0:
        return head
    step = rest / want
    tail = sorted({len(head) + 1 + int(i * step + step / 2) for i in range(want)})
    return head + [p for p in tail if p <= n]


def render_pdf(pdf: Path, pages_dir: Path, out: Path) -> None:
    subprocess.run(
        ["pdftoppm", "-r", "100", "-jpeg", "-jpegopt", "quality=80", str(pdf), str(pages_dir / "page")],
        check=True,
        timeout=900,
    )
    for img in pages_dir.glob("page-*.jpg"):  # normalise numbering to page-NNN.jpg
        num = int(img.stem.split("-")[-1])
        img.rename(pages_dir / f"page-{num:03d}.jpg")
    subprocess.run(["pdftotext", "-layout", str(pdf), str(out / "text.txt")], check=True, timeout=300)


def copy_images(src_dir: Path, pages_dir: Path) -> None:
    for i, img in enumerate(sorted(p for p in src_dir.iterdir() if p.name.startswith("page-")), 1):
        with Image.open(img) as opened:
            im = opened.convert("RGB")
            if im.width > MAX_W:
                im = im.resize((MAX_W, round(im.height * MAX_W / im.width)))
            im.save(pages_dir / f"page-{i:03d}.jpg", quality=80)


def contact_sheets(pages_dir: Path, pages: list[int], sheets_dir: Path) -> int:
    count = 0
    for s in range(0, len(pages), 4):
        group = pages[s : s + 4]
        cells = []
        for p in group:
            with Image.open(pages_dir / f"page-{p:03d}.jpg") as opened:
                im = opened.convert("RGB")
                cells.append((p, im.resize((CELL_W, round(im.height * CELL_W / im.width)))))
        cell_h = max(c[1].height for c in cells) + 28
        sheet = Image.new("RGB", (CELL_W * 2 + 12, cell_h * 2 + 12), "white")
        draw = ImageDraw.Draw(sheet)
        for i, (p, im) in enumerate(cells):
            x, y = (i % 2) * (CELL_W + 12), (i // 2) * (cell_h + 12)
            draw.rectangle([x, y, x + CELL_W, y + 26], fill=(20, 20, 20))
            draw.text((x + 8, y + 7), f"PAGE {p}", fill=(255, 255, 0))
            sheet.paste(im, (x, y + 28))
        count += 1
        sheet.save(sheets_dir / f"sheet-{count:02d}.jpg", quality=82)
    return count


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(Path.home() / "deck-corpus"))
    ap.add_argument("--sample", type=int, default=12)
    ap.add_argument("--only", default="")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    corpus = Path(args.corpus).expanduser()
    renders = corpus / "renders"
    done = 0
    for row in load_manifests(corpus):
        deck_id = row["id"]
        if args.only and args.only not in deck_id:
            continue
        if not SAFE_ID.match(deck_id):
            print(f"skip unsafe id {deck_id!r}", file=sys.stderr)
            continue
        out = contained(renders, deck_id)
        if (out / "sample.json").exists() and not args.force:
            continue
        pages_dir, sheets_dir = out / "pages", out / "sheets"
        shutil.rmtree(out, ignore_errors=True)
        pages_dir.mkdir(parents=True)
        sheets_dir.mkdir()
        try:
            src = contained(corpus, deck_id)
            if src.is_dir():
                copy_images(src, pages_dir)
            else:
                render_pdf(contained(corpus, deck_id + ".pdf"), pages_dir, out)
        except (subprocess.SubprocessError, OSError, ValueError) as err:
            print(f"! {deck_id}: {err}", file=sys.stderr)
            shutil.rmtree(out, ignore_errors=True)
            continue
        n = len(list(pages_dir.glob("page-*.jpg")))
        pages = sample_pages(n, args.sample)
        sheets = contact_sheets(pages_dir, pages, sheets_dir)
        (out / "sample.json").write_text(
            json.dumps({"id": deck_id, "page_count": n, "sampled_pages": pages, "sheets": sheets}) + "\n"
        )
        done += 1
        print(f"{deck_id}: {n} pages, sampled {len(pages)}, {sheets} sheets")
    print(f"rendered {done}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
