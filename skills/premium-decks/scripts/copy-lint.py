#!/usr/bin/env python3
"""Lint deck copy against the executive-writing rules.

Extracts visible text from a .pptx or .html deck and flags:
  - banned cliches, metaphors, and hyperbole
  - vague intensifiers that should be a number
  - sentences longer than 25 words
  - filler openers

Warnings, not errors: read each hit and fix or consciously keep it.
Usage: python3 copy-lint.py deck.pptx|deck.html
"""
import re
import sys
import zipfile

BANNED = [
    r"game.?chang", r"paradigm shift", r"now more than ever", r"inflection point",
    r"perfect storm", r"skyrocket", r"explosive growth", r"crushing it",
    r"north star", r"\bunlock", r"supercharg", r"revolutionar", r"cutting.?edge",
    r"\bjourney\b", r"is dead\b", r"\b10x\b", r"world.?class", r"best.?in.?class",
    r"seamless", r"\bleverage\b", r"\brobust\b", r"synerg", r"holistic",
    r"empower", r"\bdelve\b", r"not closing.{0,10}widening",
    r"in today's", r"as we all know", r"fast.?paced world",
]
INTENSIFIERS = [r"\bvery\b", r"\bsignificantly\b", r"\bdramatically\b", r"\bmassive\b", r"\bhugely\b"]
MAX_WORDS = 25


def pptx_text(path):
    out = []
    with zipfile.ZipFile(path) as z:
        slides = sorted(n for n in z.namelist() if re.match(r"ppt/slides/slide\d+\.xml$", n))
        for name in slides:
            xml = z.read(name).decode("utf-8", errors="replace")
            num = re.search(r"slide(\d+)", name).group(1)
            for para in re.findall(r"<a:p>(.*?)</a:p>", xml, re.S):
                runs = re.findall(r"<a:t>([^<]*)</a:t>", para)
                text = "".join(runs).strip()
                if text:
                    out.append((f"slide {num}", text))
    return out


def html_text(path):
    src = open(path, encoding="utf-8", errors="replace").read()
    src = re.sub(r"<(script|style)\b.*?</\1>", " ", src, flags=re.S | re.I)
    out = []
    for m in re.finditer(r">([^<>]+)<", src):
        text = re.sub(r"\s+", " ", m.group(1)).strip()
        if text and not text.startswith("<!"):
            out.append(("html", text))
    return out


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    path = sys.argv[1]
    blocks = pptx_text(path) if path.lower().endswith((".pptx", ".potx")) else html_text(path)
    hits = 0
    for where, text in blocks:
        low = text.lower()
        for pat in BANNED:
            if re.search(pat, low):
                hits += 1
                print(f"[banned]      {where}: /{pat}/ in: {text[:90]}")
        for pat in INTENSIFIERS:
            if re.search(pat, low):
                hits += 1
                print(f"[intensifier] {where}: {pat} — replace with the number: {text[:90]}")
        for sent in re.split(r"[.!?]+\s", text):
            n = len(sent.split())
            if n > MAX_WORDS:
                hits += 1
                print(f"[long: {n}w]   {where}: {sent[:90]}")
    print(f"\n{hits} finding(s) across {len(blocks)} text block(s)." if hits
          else f"Clean: {len(blocks)} text block(s), no findings.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
