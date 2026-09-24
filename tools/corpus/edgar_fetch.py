#!/usr/bin/env python3
"""Fetch banker board books (EX-99.(c) exhibits) from SEC EDGAR for the research corpus.

Development tool — not part of the skill. Downloads go to a local corpus
directory outside the repository; nothing fetched here is ever committed.

How it works:
  1. EDGAR full-text search finds going-private filings (SC 13E3 and
     amendments) whose text names a given advisor.
  2. The filing index lists every exhibit; EX-99.(c) exhibits are the
     reports, opinions, and board presentations the banks delivered.
  3. An exhibit is kept as a deck when its HTML wraps >= MIN_PAGES page
     images. The page images are saved as-is (they are the rendered slides).

SEC fair-access policy: the User-Agent must declare a contact. It is read from
the SEC_USER_AGENT environment variable and never written anywhere. Requests
are throttled to at most 4 per second.

Usage:
  SEC_USER_AGENT="Name contact@example.com" python3 edgar_fetch.py --dry-run
  SEC_USER_AGENT="..." python3 edgar_fetch.py --per-advisor 4
"""
from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import os
import re
import shutil
import sys
import time
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

FTS_URL = "https://efts.sec.gov/LATEST/search-index"
ARCHIVE_PREFIX = "https://www.sec.gov/Archives/edgar/data/"
MIN_INTERVAL_S = 0.25
MIN_PAGES = 6
SAFE_NAME = re.compile(r"^[A-Za-z0-9._-]{1,120}$")
EXHIBIT_C = re.compile(r"^EX-99\.?\s*\(?C\)?", re.I)

# Advisor -> search phrase. Strata: bulge bracket and elite boutique.
ADVISORS = {
    "Goldman Sachs": ("bulge", '"Goldman Sachs"'),
    "Morgan Stanley": ("bulge", '"Morgan Stanley"'),
    "J.P. Morgan": ("bulge", '"J.P. Morgan Securities"'),
    "BofA Securities": ("bulge", '"BofA Securities"'),
    "Citigroup": ("bulge", '"Citigroup Global Markets"'),
    "Lazard": ("boutique", '"Lazard"'),
    "Evercore": ("boutique", '"Evercore"'),
    "Centerview": ("boutique", '"Centerview Partners"'),
    "Moelis": ("boutique", '"Moelis"'),
    "PJT Partners": ("boutique", '"PJT Partners"'),
    "Houlihan Lokey": ("boutique", '"Houlihan Lokey"'),
    "Jefferies": ("boutique", '"Jefferies"'),
}
FORMS = "SC 13E3,SC 13E3/A"

_last_request = 0.0


def user_agent() -> str:
    ua = os.environ.get("SEC_USER_AGENT", "").strip()
    if "@" not in ua:
        sys.exit("SEC_USER_AGENT must be set to 'Name contact-email' (SEC fair-access policy).")
    return ua


def fetch(url: str, ua: str) -> bytes:
    """GET with throttling. Only sec.gov hosts are allowed."""
    global _last_request
    host = urllib.parse.urlparse(url).hostname or ""
    if host not in ("efts.sec.gov", "www.sec.gov"):
        raise ValueError(f"refusing non-SEC host: {host}")
    wait = MIN_INTERVAL_S - (time.monotonic() - _last_request)
    if wait > 0:
        time.sleep(wait)
    req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept-Encoding": "identity"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                _last_request = time.monotonic()
                return resp.read()
        except urllib.error.HTTPError as err:
            _last_request = time.monotonic()
            if err.code in (429, 503) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            raise
        except (TimeoutError, urllib.error.URLError, http.client.IncompleteRead, ConnectionError) as err:
            _last_request = time.monotonic()
            if attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            raise RuntimeError(f"network failure after 3 attempts: {err}") from err
    raise RuntimeError("unreachable")


def search_filings(phrase: str, start: str, end: str, ua: str, pages: int = 2) -> list[dict]:
    """Return unique root filings (cik, adsh, date, company) matching the phrase."""
    seen: dict[str, dict] = {}
    for page in range(pages):
        params = {
            "q": f'{phrase} "discussion materials"',
            "forms": FORMS,
            "dateRange": "custom",
            "startdt": start,
            "enddt": end,
            "from": str(page * 100),
        }
        data = json.loads(fetch(f"{FTS_URL}?{urllib.parse.urlencode(params)}", ua))
        hits = data.get("hits", {}).get("hits", [])
        for hit in hits:
            src = hit["_source"]
            adsh = src["adsh"]
            ciks = src.get("ciks") or []
            if not ciks or adsh in seen:
                continue
            seen[adsh] = {
                "cik": str(int(ciks[0])),
                "adsh": adsh,
                "date": src.get("file_date", ""),
                "company": (src.get("display_names") or [""])[0].split("  (")[0].strip(),
                "form": src.get("form", ""),
            }
        if len(hits) < 100:
            break
    return sorted(seen.values(), key=lambda f: f["date"])


class _IndexParser(HTMLParser):
    """Collect (document href, type) rows from an EDGAR filing index page."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: list[tuple[str, str]] = []
        self._cells: list[str] = []
        self._href = ""
        self._in_td = False

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._cells, self._href = [], ""
        elif tag == "td":
            self._in_td = True
            self._cells.append("")
        elif tag == "a" and self._in_td:
            href = dict(attrs).get("href") or ""
            if href.startswith("/Archives/") and not self._href:
                self._href = href

    def handle_endtag(self, tag):
        if tag == "td":
            self._in_td = False
        elif tag == "tr" and self._href and len(self._cells) >= 4:
            self.rows.append((self._href, self._cells[3].strip()))

    def handle_data(self, data):
        if self._in_td and self._cells:
            self._cells[-1] += data


def exhibit_c_docs(filing: dict, ua: str) -> list[str]:
    nodash = filing["adsh"].replace("-", "")
    url = f"{ARCHIVE_PREFIX}{filing['cik']}/{nodash}/{filing['adsh']}-index.htm"
    parser = _IndexParser()
    parser.feed(fetch(url, ua).decode("utf-8", "replace"))
    return [
        "https://www.sec.gov" + href
        for href, doc_type in parser.rows
        if EXHIBIT_C.match(doc_type) and href.lower().endswith((".htm", ".html"))
    ]


def page_images(doc_url: str, html: str) -> list[str]:
    base = doc_url.rsplit("/", 1)[0] + "/"
    out = []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html, re.I):
        name = src.rsplit("/", 1)[-1]
        if SAFE_NAME.match(name) and name.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
            out.append(base + name)
    return list(dict.fromkeys(out))


def safe_dir(root: Path, *parts: str) -> Path:
    for part in parts:
        if not SAFE_NAME.match(part):
            raise ValueError(f"unsafe path component: {part!r}")
    target = root.joinpath(*parts).resolve()
    if root.resolve() not in target.parents:
        raise ValueError("path escapes corpus root")
    return target


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=str(Path.home() / "deck-corpus" / "edgar"))
    ap.add_argument("--manifest", default=str(Path.home() / "deck-corpus" / "manifest.jsonl"))
    ap.add_argument("--start", default="2015-01-01")
    ap.add_argument("--end", default="2026-09-01")
    ap.add_argument("--per-advisor", type=int, default=4, help="max decks kept per advisor")
    ap.add_argument("--per-company", type=int, default=2, help="max decks kept per target company")
    ap.add_argument("--dry-run", action="store_true", help="list candidate filings; download nothing")
    args = ap.parse_args()

    ua = user_agent()
    out_root = Path(args.out).expanduser()
    manifest = Path(args.manifest).expanduser()
    known = set()
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            if line.strip():
                known.add(json.loads(line).get("sha256"))

    per_company: dict[str, int] = {}
    per_advisor: dict[str, int] = {}
    if manifest.exists():
        for line in manifest.read_text().splitlines():
            if line.strip():
                row = json.loads(line)
                if row.get("publisher") == "SEC EDGAR":
                    per_advisor[row["firm"]] = per_advisor.get(row["firm"], 0) + 1
    for advisor, (stratum, phrase) in ADVISORS.items():
        filings = search_filings(phrase, args.start, args.end, ua)
        # Spread across years: prefer one filing per year before repeats.
        by_year: dict[str, list[dict]] = {}
        for f in filings:
            by_year.setdefault(f["date"][:4], []).append(f)
        ordered = []
        while any(by_year.values()):
            for year in sorted(by_year):
                if by_year[year]:
                    ordered.append(by_year[year].pop(0))
        print(f"\n## {advisor} [{stratum}] — {len(filings)} candidate filings")
        if args.dry_run:
            for f in ordered[:12]:
                print(f"  {f['date']}  {f['form']:<10} {f['company'][:48]}  {f['adsh']}")
            continue

        kept = per_advisor.get(advisor, 0)
        for filing in ordered:
            if kept >= args.per_advisor:
                break
            if per_company.get(filing["cik"], 0) >= args.per_company:
                continue
            try:
                docs = exhibit_c_docs(filing, ua)
            except Exception as err:  # network or parse failure: report and skip this filing
                print(f"  ! index failed {filing['adsh']}: {err}", file=sys.stderr)
                continue
            for doc_url in docs:
                if kept >= args.per_advisor or per_company.get(filing["cik"], 0) >= args.per_company:
                    break
                try:
                    html = fetch(doc_url, ua).decode("utf-8", "replace")
                except (RuntimeError, urllib.error.HTTPError) as err:
                    print(f"  ! exhibit failed {doc_url}: {err}", file=sys.stderr)
                    continue
                images = page_images(doc_url, html)
                if len(images) < MIN_PAGES:
                    continue
                first = fetch(images[0], ua)
                digest = hashlib.sha256(first).hexdigest()
                if digest in known:
                    continue  # the same book re-filed in an amendment
                deck_id = f"{filing['adsh']}_{doc_url.rsplit('/', 1)[-1].rsplit('.', 1)[0]}"
                deck_dir = safe_dir(out_root, deck_id)
                partial = safe_dir(out_root, deck_id + ".partial")
                shutil.rmtree(partial, ignore_errors=True)
                partial.mkdir(parents=True)
                try:
                    for i, img_url in enumerate(images, 1):
                        data = first if i == 1 else fetch(img_url, ua)
                        ext = img_url.rsplit(".", 1)[-1].lower()
                        (partial / f"page-{i:03d}.{ext}").write_bytes(data)
                except (RuntimeError, urllib.error.HTTPError) as err:
                    print(f"  ! deck download failed {deck_id}: {err}", file=sys.stderr)
                    shutil.rmtree(partial, ignore_errors=True)
                    continue
                shutil.rmtree(deck_dir, ignore_errors=True)
                partial.rename(deck_dir)  # a deck appears only when every page arrived
                row = {
                    "id": f"edgar/{deck_id}",
                    "url": doc_url,
                    "publisher": "SEC EDGAR",
                    "firm": advisor,  # search stratum; the coder confirms the advisor from the cover
                    "firm_stratum": stratum,
                    "company": filing["company"],
                    "date": filing["date"],
                    "genre": "banking-board-book",
                    "deck_type": "going-private board presentation",
                    "industry": "",
                    "pages": len(images),
                    "license_note": "Public SEC filing; bank retains copyright. Local study only; never redistributed.",
                    "sha256": digest,
                    "holdout": False,
                }
                with manifest.open("a") as fh:
                    fh.write(json.dumps(row) + "\n")
                known.add(digest)
                kept += 1
                per_company[filing["cik"]] = per_company.get(filing["cik"], 0) + 1
                print(f"  + {filing['date']} {filing['company'][:40]} — {len(images)} pages")
        print(f"  kept {kept}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
