#!/usr/bin/env python3
"""Build the blind discrimination set: generated slides vs real hold-out slides.

Both sides get the SAME treatment, so provenance cannot be read from branding:
  - resized to 1280 px wide, white-padded to 16:9;
  - two thin bands painted out on every slide: the top 4.5% (trackers, running
    labels) and the bottom 6.5% (footers, page numbers, confidentiality). No
    band reaches a title. Logos and names that remain are covered by the judge
    instruction to ignore branding and content domain.
Real slides come only from hold-out decks (never coded, never used for rules),
from pages 3..N-2, skipping near-blank pages. Generated slides are content
slides (not cover, not disclaimer) from the given PDFs.

Output (outside the repo, since it contains real decks):
  ~/deck-corpus/judge/<set>/items/<id>.jpg and ~/deck-corpus/judge/<set>/key.json
Usage: python3 build_discrimination.py <set-name> --generated a.pdf b.pdf ... [--n-real 20] [--seed 7]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageStat

CORPUS = Path.home() / "deck-corpus"
W, H = 1280, 720


def normalise(img: Image.Image) -> Image.Image:
    img = img.convert("RGB")
    scale = min(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)))
    canvas = Image.new("RGB", (W, H), "white")
    canvas.paste(img, ((W - img.width) // 2, (H - img.height) // 2))
    d = ImageDraw.Draw(canvas)
    top = (H - img.height) // 2  # mask thin bands of the slide itself, not of the padding
    d.rectangle([0, 0, W, top + int(img.height * 0.045)], fill="white")         # trackers, running labels
    d.rectangle([0, top + int(img.height * 0.935), W, H], fill="white")         # footers, page numbers
    return canvas


def blank(img: Image.Image) -> bool:
    return ImageStat.Stat(img.convert("L")).stddev[0] < 18


def real_pages(n: int, rng: random.Random) -> list[Path]:
    rows = []
    for name in ("manifest.jsonl", "manifest-aggregators.jsonl", "manifest-public.jsonl"):
        p = CORPUS / name
        if p.exists():
            rows += [json.loads(line) for line in p.read_text().splitlines() if line.strip()]
    hold = [r for r in rows if r.get("holdout")]
    by_genre: dict[str, list[dict]] = {}
    for r in hold:
        by_genre.setdefault("banking" if r["genre"].startswith("banking") else "consulting", []).append(r)
    picks: list[Path] = []
    for _genre, decks in sorted(by_genre.items()):  # half banking, half consulting
        pool = []
        for r in decks:
            pages = sorted((CORPUS / "renders" / r["id"] / "pages").glob("page-*.jpg"))
            pool += pages[2:-2]
        rng.shuffle(pool)
        taken = 0
        for p in pool:
            if taken >= n // 2:
                break
            with Image.open(p) as im:
                if not blank(im):
                    picks.append(p)
                    taken += 1
    return picks


def generated_pages(pdfs: list[Path], tmp: Path) -> list[Path]:
    out = []
    for pdf in pdfs:
        stem = hashlib.sha256(str(pdf).encode()).hexdigest()[:8]
        subprocess.run(["pdftoppm", "-r", "100", "-jpeg", str(pdf), str(tmp / stem)], check=True, timeout=600)
        pages = sorted(tmp.glob(f"{stem}-*.jpg"), key=lambda p: int(p.stem.rsplit("-", 1)[1]))
        out += pages[2:]  # skip the cover and the page after it (disclaimer or agenda in books)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name")
    ap.add_argument("--generated", nargs="+", required=True)
    ap.add_argument("--n-real", type=int, default=20)
    ap.add_argument("--n-generated", type=int, default=20)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    if not args.name.replace("-", "").isalnum():
        raise SystemExit("set name must be alphanumeric with dashes")
    rng = random.Random(args.seed)  # noqa: S311 — reproducible sampling, not security
    out = CORPUS / "judge" / args.name
    items = out / "items"
    items.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as t:
        gen = generated_pages([Path(p) for p in args.generated], Path(t))
        rng.shuffle(gen)
        gen = [p for p in gen if not blank(Image.open(p))][: args.n_generated]
        real = real_pages(args.n_real, rng)[: args.n_real]
        entries = [("generated", p) for p in gen] + [("real", p) for p in real]
        rng.shuffle(entries)
        key = {}
        for i, (label, p) in enumerate(entries, 1):
            item = f"S{i:02d}"
            with Image.open(p) as im:
                normalise(im).save(items / f"{item}.jpg", quality=85)
            key[item] = {"label": label, "source": str(p)}
    (out / "key.json").write_text(json.dumps(key, indent=1))
    print(f"{len(key)} items ({sum(v['label'] == 'real' for v in key.values())} real) → {items}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
