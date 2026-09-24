#!/usr/bin/env python3
"""Ingest a folder of source material into a citable fact base for a deck.

Reads pdf, docx, xlsx, csv, md, txt, and pptx. Writes:
  <out>/sources.md    one section per file: type, size, structure, first lines
  <out>/facts.jsonl   one row per figure: {id, value, unit, scale, period,
                      text, file, locator}
  <out>/conflicts.md  figures that look like the same metric with different
                      values; resolve these BEFORE writing the storyline

Every slide number must later cite a fact id (see trace-check.py).

Safety: the folder is canonicalised; symlinks are skipped; hidden files are
skipped; at most --max-files files and --max-mb MB per file are read. Office
XML is parsed with defusedxml only. Spreadsheet formulas are evaluated by a
small arithmetic parser (numbers, cell refs, + - * /, parentheses, SUM) —
never by eval.

Usage: python3 ingest.py <folder> [--out brief] [--max-files 200] [--max-mb 50]
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

from defusedxml import ElementTree as ET

TEXT_EXT = {".md", ".txt"}
SUPPORTED = TEXT_EXT | {".csv", ".xlsx", ".docx", ".pptx", ".pdf"}
NS = {
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
SCALE_WORDS = {
    "k": 1e3,
    "thousand": 1e3,
    "m": 1e6,
    "mm": 1e6,
    "mn": 1e6,
    "million": 1e6,
    "b": 1e9,
    "bn": 1e9,
    "billion": 1e9,
}
CURRENCY = {"$": "USD", "usd": "USD", "€": "EUR", "eur": "EUR", "£": "GBP", "gbp": "GBP"}
STOP = set(
    """a an the of to in on for and or is was were be been are at by with from as that this it its
our we they their per should use used about over under than into last next year years total vs
usd eur gbp value values unit units pct bps pts basis points percent""".split()
)
SYNONYMS = {
    "sales": "revenue",
    "turnover": "revenue",
    "tam": "market",
    "addressable": "market",
    "golive": "go-live",
    "go": "go-live",
    "live": "go-live",
    "headcount": "employees",
}
MONTHS = {
    m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)
}

NUM_RE = re.compile(
    r"(?P<cur>[$€£]|\b(?:USD|EUR|GBP)\s?)?"
    r"(?P<num>\(?-?\d{1,3}(?:,\d{3})+(?:\.\d+)?\)?|\(?-?\d+(?:\.\d+)?\)?)"
    r"(?:\s?(?P<suf>%|bps|x(?![\w-])|(?:k|m|mm|mn|b|bn)\b|thousand\b|million\b|billion\b))?",
    re.I,
)
DATE_RE = re.compile(
    r"\b(?:(?P<y1>20\d{2})-(?P<m1>0[1-9]|1[0-2])\b"
    r"|(?P<mon>jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(?P<y2>20\d{2}))",
    re.I,
)
PERIOD_RE = re.compile(r"\b(FY\s?\d{2,4}E?|Q[1-4]\s?(?:FY)?\s?\d{2,4}|H[12]\s?\d{2,4}|20\d{2}E?|LTM|NTM)\b", re.I)


@dataclass
class Fact:
    id: str
    value: float | str
    unit: str
    scale: float
    period: str
    text: str
    file: str
    locator: str


# ------------------------------------------------------------------ number parsing
def parse_number(raw: str) -> float | None:
    neg = raw.startswith("(") and raw.endswith(")")
    try:
        v = float(raw.strip("()").replace(",", ""))
    except ValueError:
        return None
    return -v if neg else v


def scale_hint(text: str) -> tuple[str, float]:
    """Read '($M)', '$k', '(EUR M)', 'USD m' style hints from a sheet title or header."""
    t = text.lower()
    m = re.search(r"(\$|€|£|usd|eur|gbp)\s?(k|m|mm|mn|b|bn|thousand|million|billion)\b", t)
    if m:
        return CURRENCY.get(m.group(1), m.group(1).upper()), SCALE_WORDS[m.group(2)]
    m = re.search(r"\b(k|m|mm|b|bn)\b\s*\)?$", t.strip())
    if m and "(" in t:
        return "", SCALE_WORDS[m.group(1)]
    return "", 1.0


def numbers_in(text: str) -> list[tuple[float, str, float, int, int]]:
    """Return (value, unit, scale, start, end) for each figure in free text."""
    out = []
    for m in NUM_RE.finditer(text):
        raw, suf, cur = m.group("num"), (m.group("suf") or "").lower(), (m.group("cur") or "").strip().lower()
        if raw.endswith(")") and not raw.startswith("("):
            raw = raw[:-1]  # "(Aug 2026)": the bracket closes the phrase, not a negative number
        if raw.startswith("(") and not raw.endswith(")"):
            raw = raw[1:]
        if raw.startswith("-") and re.search(r"[\d%x]\s?$", text[: m.start()]):
            raw = raw[1:]  # "15-20%": the hyphen joins a range; it is not a minus sign
        v = parse_number(raw)
        if v is None:
            continue
        # Skip bare years, list ordinals, and times: they are not figures.
        if not cur and not suf and (re.fullmatch(r"(19|20)\d{2}", raw) or text[m.end() : m.end() + 1] == ":"):
            continue
        if not cur and not suf and text[max(0, m.start() - 1) : m.start()] in ("#", "-"):
            continue
        if not cur and m.start() > 0 and text[m.start() - 1].isalpha():
            continue  # part of a label such as Q1, FY25, H2, mock-2
        if not cur and text[m.end() : m.end() + 1].isalpha() and not suf:
            continue  # part of a token such as 3D, 2nd
        if not cur and not suf and re.match(r"-[A-Za-z]", text[m.end() : m.end() + 2]):
            continue  # a compound modifier such as 52-week or 3-year
        unit = CURRENCY.get(cur, "")
        scale = 1.0
        if suf == "%":
            unit = "%"
        elif suf == "bps":
            unit = "bps"
        elif suf == "x":
            unit = "x"
        elif suf in SCALE_WORDS:
            scale = SCALE_WORDS[suf]
        out.append((v, unit, scale, m.start(), m.end()))
    return out


def dates_in(text: str) -> list[tuple[str, int, int]]:
    out = []
    for m in DATE_RE.finditer(text):
        if m.group("y1"):
            out.append((f"{m.group('y1')}-{m.group('m1')}", m.start(), m.end()))
        else:
            out.append((f"{m.group('y2')}-{MONTHS[m.group('mon').lower()[:3]]:02d}", m.start(), m.end()))
    return out


def period_of(text: str) -> str:
    m = PERIOD_RE.search(text)
    return m.group(1).upper().replace(" ", "") if m else ""


def window(text: str, start: int, end: int, before: int = 7, after: int = 4) -> str:
    left = text[:start].split()[-before:]
    right = text[end:].split()[:after]
    return " ".join(left + [text[start:end]] + right)


# ------------------------------------------------------------------ safe formula evaluation
class Formula:
    """Recursive-descent evaluator for spreadsheet arithmetic. No eval()."""

    TOKEN = re.compile(
        r"\s*(?:(?P<num>\d+(?:\.\d+)?)|(?P<ref>\$?[A-Z]{1,3}\$?\d+(?::\$?[A-Z]{1,3}\$?\d+)?)"
        r"|(?P<fn>SUM)\(|(?P<op>[-+*/(),]))"
    )

    def __init__(self, expr: str, lookup: Callable[[str], list[float]]) -> None:
        self.tokens: list[tuple[str, str]] = []
        pos = 0
        expr = expr.lstrip("=").upper()
        while pos < len(expr):
            m = self.TOKEN.match(expr, pos)
            if not m or m.end() == pos:
                raise ValueError(f"unsupported formula near {expr[pos : pos + 10]!r}")
            kind = m.lastgroup
            assert kind is not None  # every alternative of TOKEN is a named group
            self.tokens.append((kind, m.group(kind)))
            pos = m.end()
        self.i, self.lookup = 0, lookup

    def peek(self) -> tuple[str, str] | tuple[None, None]:
        return self.tokens[self.i] if self.i < len(self.tokens) else (None, None)

    def take(self) -> tuple[str, str] | tuple[None, None]:
        tok = self.peek()
        self.i += 1
        return tok

    def value(self) -> float:
        v = self.expr()
        if self.i != len(self.tokens):
            raise ValueError("trailing tokens")
        return v

    def expr(self) -> float:
        v = self.term()
        while self.peek() in (("op", "+"), ("op", "-")):
            op = self.take()[1]
            v = v + self.term() if op == "+" else v - self.term()
        return v

    def term(self) -> float:
        v = self.factor()
        while self.peek() in (("op", "*"), ("op", "/")):
            op = self.take()[1]
            rhs = self.factor()
            v = v * rhs if op == "*" else v / rhs
        return v

    def factor(self) -> float:
        kind, tok = self.take()
        if kind == "op" and tok == "-":
            return -self.factor()
        if kind == "num":
            assert tok is not None  # a token with a kind always carries its text
            return float(tok)
        if kind == "ref":
            assert tok is not None
            vals = self.lookup(tok.replace("$", ""))
            if len(vals) != 1:
                raise ValueError("range outside SUM")
            return vals[0]
        if kind == "fn":
            total = 0.0
            while True:
                k, t = self.take()
                if k == "ref":
                    assert t is not None
                    total += sum(self.lookup(t.replace("$", "")))
                else:
                    self.i -= 1
                    total += self.expr()
                k, t = self.take()
                if t == ")":
                    return total
                if t != ",":
                    raise ValueError("bad SUM")
        if kind == "op" and tok == "(":
            v = self.expr()
            if self.take() != ("op", ")"):
                raise ValueError("missing )")
            return v
        raise ValueError(f"unexpected token {tok!r}")


def col_index(col: str) -> int:
    n = 0
    for ch in col:
        n = n * 26 + ord(ch) - 64
    return n


def split_ref(ref: str) -> tuple[str, int]:
    m = re.fullmatch(r"([A-Z]+)(\d+)", ref)
    if not m:
        raise ValueError(ref)
    return m.group(1), int(m.group(2))


# ------------------------------------------------------------------ readers
MAX_MEMBER_BYTES = 64 * 1024 * 1024  # decompressed cap per Office XML part: a small file can inflate without limit
MAX_FILE_BYTES = 256 * 1024 * 1024  # decompressed cap for all parts of one Office file


def _zread(z: zipfile.ZipFile, name: str) -> bytes:
    """Read one zip member, refusing a part whose decompressed size exceeds the cap (zip-bomb guard).
    zipfile stops at the declared size and fails the CRC on a lie, so the declared size is binding."""
    total = sum(i.file_size for i in z.infolist())
    if total > MAX_FILE_BYTES:  # many parts under the per-part cap can still add up
        raise ValueError(
            f"the file decompresses to {total // (1024 * 1024)} MB, over the {MAX_FILE_BYTES // (1024 * 1024)} MB limit"
        )
    size = z.getinfo(name).file_size
    if size > MAX_MEMBER_BYTES:
        raise ValueError(
            f"{name} decompresses to {size // (1024 * 1024)} MB, over the {MAX_MEMBER_BYTES // (1024 * 1024)} MB limit"
        )
    return z.read(name)


def read_xlsx(path: Path) -> tuple[str, list[tuple[str, str, object, str]]]:
    """Return (summary, cells) where cells are (sheet, ref, value, formula)."""
    with zipfile.ZipFile(path) as z:
        names = set(z.namelist())
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(_zread(z, "xl/sharedStrings.xml"))
            for si in root.findall("s:si", NS):
                shared.append("".join(t.text or "" for t in si.iter(f"{{{NS['s']}}}t")))
        wb = ET.fromstring(_zread(z, "xl/workbook.xml"))
        rels = ET.fromstring(_zread(z, "xl/_rels/workbook.xml.rels"))
        target = {r.get("Id"): r.get("Target") for r in rels.findall("rel:Relationship", NS)}
        sheets = []
        for sh in wb.find("s:sheets", NS).findall("s:sheet", NS):
            rid = sh.get(f"{{{NS['r']}}}id")
            t = target[rid].lstrip("/")
            sheets.append((sh.get("name"), t if t.startswith("xl/") else "xl/" + t))
        cells = []
        for name, part in sheets:
            if part not in names:
                continue
            root = ET.fromstring(_zread(z, part))
            for c in root.iter(f"{{{NS['s']}}}c"):
                ref, typ = c.get("r"), c.get("t")
                f_el, v_el = c.find("s:f", NS), c.find("s:v", NS)
                is_el = c.find("s:is", NS)
                formula = ("=" + f_el.text) if f_el is not None and f_el.text else ""
                if typ == "s" and v_el is not None:
                    val: object = shared[int(v_el.text)]
                elif typ == "inlineStr" and is_el is not None:
                    val = "".join(t.text or "" for t in is_el.iter(f"{{{NS['s']}}}t"))
                elif v_el is not None and v_el.text is not None:
                    val = parse_number(v_el.text) if typ not in ("str", "b", "e") else v_el.text
                else:
                    val = None
                cells.append((name, ref, val, formula))
    summary = ", ".join(f"{n}" for n, _ in sheets)
    return f"{len(sheets)} sheet(s): {summary}", cells


def evaluate_formulas(cells: list[tuple[str, str, object, str]]) -> list[tuple[str, str, object, str]]:
    grid: dict[tuple[str, str], object] = {(s, r): v for s, r, v, _ in cells}
    formulas = {(s, r): f for s, r, _, f in cells if f}
    resolving: set[tuple[str, str]] = set()

    def get(sheet: str, ref: str) -> float:
        key = (sheet, ref)
        if key in formulas and grid.get(key) is None:
            if key in resolving:
                raise ValueError("circular reference")
            resolving.add(key)
            try:
                grid[key] = Formula(formulas[key], lambda r: lookup(sheet, r)).value()
            finally:
                resolving.discard(key)
        v = grid.get(key)
        return v if isinstance(v, (int, float)) else 0.0

    def lookup(sheet: str, ref: str) -> list[float]:
        if ":" in ref:
            a, b = ref.split(":")
            (ca, ra), (cb, rb) = split_ref(a), split_ref(b)
            out: list[float] = []
            for row in range(ra, rb + 1):
                for ci in range(col_index(ca), col_index(cb) + 1):
                    col = ""
                    n = ci
                    while n:
                        n, rem = divmod(n - 1, 26)
                        col = chr(65 + rem) + col
                    out.append(get(sheet, f"{col}{row}"))
            return out
        return [get(sheet, ref)]

    for key in formulas:
        try:
            get(*key)
        except (ValueError, ZeroDivisionError):
            grid[key] = None
    return [(s, r, grid.get((s, r)), f) for s, r, _, f in cells]


def xlsx_facts(path: Path, rel: str, new_id: Callable[[], str]) -> tuple[str, list[Fact]]:
    summary, cells = read_xlsx(path)
    cells = evaluate_formulas(cells)
    by_sheet: dict[str, dict[str, tuple[object, str]]] = {}
    for s, r, v, f in cells:
        by_sheet.setdefault(s, {})[r] = (v, f)
    facts: list[Fact] = []
    for sheet, grid in by_sheet.items():
        cur, scale = scale_hint(sheet)
        title = str(grid.get("A1", ("", ""))[0] or "")
        if scale == 1.0:
            cur2, scale = scale_hint(title)
            cur = cur or cur2
        header_row: dict[str, str] = {}
        for ref, (v, _) in grid.items():
            col, row = split_ref(ref)
            if row == 1 and isinstance(v, str):
                header_row[col] = v
        if not cur:
            for h in header_row.values():
                c2, s2 = scale_hint(h)
                if c2 or s2 != 1.0:
                    cur, scale = c2 or cur, s2 if s2 != 1.0 else scale
        unit_col = next((c for c, h in header_row.items() if h.strip().lower() in ("unit", "units")), None)
        sheet_period = period_of(sheet) or period_of(title)
        for ref, (v, f) in grid.items():
            col, row = split_ref(ref)
            if isinstance(v, str) and len(v) > 25 and row > 1:
                # Notes typed into cells carry figures too; read them like prose.
                for pf in prose_facts(v, rel, new_id, "cell"):
                    pf.locator = f"{sheet}!{ref} (text)"
                    facts.append(pf)
                continue
            if not isinstance(v, (int, float)) or isinstance(v, bool):
                continue
            if row == 1:
                continue
            label = grid.get(f"A{row}", ("", ""))[0]
            label = label if isinstance(label, str) else ""
            header = header_row.get(col, "")
            if col == "A":
                continue
            unit, sc = cur, scale
            lab = f"{label} {header}".strip()
            row_unit = grid.get(f"{unit_col}{row}", ("", ""))[0] if unit_col else ""
            if isinstance(row_unit, str) and row_unit.strip():
                ru = row_unit.strip()
                cu, su = scale_hint(ru + ")") if ru[:1] in "$€£" else ("", SCALE_WORDS.get(ru.lower(), 1.0))
                unit = CURRENCY.get(ru[:1], cu) or unit if ru[:1] in "$€£" else ("%" if ru == "%" else "")
                sc = su if ru[:1] not in "$€£" else (scale_hint(ru)[1] if len(ru) > 1 else 1.0)
            c3, s3 = scale_hint(header)
            is_pct = "%" in lab or "margin" in lab.lower()
            if is_pct:
                unit, sc = "%", 1.0
                v = v * 100 if abs(v) < 1 else v
            elif s3 != 1.0:
                unit, sc = c3 or unit, s3
            elif re.search(r"_k\b|\(k\)|\bk\)$", header.lower()):
                sc = 1e3
            elif re.search(r"_m\b|usd_m|_usd_m", header.lower()):
                sc, unit = 1e6, unit or ("USD" if "usd" in header.lower() else unit)
            text = f"{title} | {lab}"
            if f:
                text += f" [formula {f}]"
            facts.append(
                Fact(
                    new_id(),
                    round(v, 6),
                    unit,
                    sc,
                    period_of(header) or period_of(label) or sheet_period,
                    text[:200],
                    rel,
                    f"{sheet}!{ref}",
                )
            )
    return summary, facts


def csv_facts(path: Path, rel: str, new_id: Callable[[], str]) -> tuple[str, list[Fact]]:
    text = path.read_text(errors="replace")
    rows = list(csv.reader(io.StringIO(text)))
    if not rows:
        return "empty", []
    header = rows[0]
    facts: list[Fact] = []
    for r_i, row in enumerate(rows[1:], start=2):
        label = row[0] if row else ""
        for c_i, cell in enumerate(row[1:], start=1):
            h = header[c_i] if c_i < len(header) else f"col{c_i + 1}"
            ds = dates_in(cell)
            if ds and re.fullmatch(r"\s*20\d{2}-\d{2}\s*", cell):
                facts.append(Fact(new_id(), ds[0][0], "date", 1.0, "", f"{label} | {h}"[:200], rel, f"row {r_i}, {h}"))
                continue
            is_plain = re.fullmatch(r"\s*-?[\d,]+(\.\d+)?\s*", cell)
            plain = parse_number(cell.strip().replace(",", "")) if is_plain else None
            if plain is not None and not re.search(r"year|date|period", h, re.I):
                found = [(plain, "", 1.0, 0, len(cell))]  # a bare numeric cell is a value, even 1980
            else:
                found = numbers_in(cell)
            if len(found) != 1:
                continue
            v, unit, sc, _, _ = found[0]
            hl = h.lower()
            if "pct" in hl or "%" in hl:
                unit = "%"
            if re.search(r"_k\b|_usd_k", hl):
                sc = 1e3
            elif re.search(r"_m\b|usd_m", hl):
                sc = 1e6
            elif re.search(r"_bn\b", hl):
                sc = 1e9
            if "usd" in hl:
                unit = unit or "USD"
            elif re.search(r"\beur\b|_eur", hl):
                unit = unit or "EUR"
            if hl.endswith("_x") or "_x_" in hl:
                unit = "x"
            facts.append(
                Fact(
                    new_id(),
                    v,
                    unit,
                    sc,
                    period_of(h) or period_of(label),
                    f"{label} | {h}"[:200],
                    rel,
                    f"row {r_i}, {h}",
                )
            )
    return f"{len(rows) - 1} rows × {len(header)} columns: {', '.join(header)[:160]}", facts


def prose_facts(text: str, rel: str, new_id: Callable[[], str], locator_prefix: str = "line") -> list[Fact]:
    facts: list[Fact] = []
    for ln, line in enumerate(text.splitlines(), 1):
        taken: list[tuple[int, int]] = []
        for d, s, e in dates_in(line):
            facts.append(Fact(new_id(), d, "date", 1.0, "", window(line, s, e)[:200], rel, f"{locator_prefix} {ln}"))
            taken.append((s, e))
        for v, unit, sc, s, e in numbers_in(line):
            if any(s < te and e > ts for ts, te in taken):
                continue
            facts.append(
                Fact(
                    new_id(),
                    v,
                    unit,
                    sc,
                    period_of(window(line, s, e, 5, 3)),
                    window(line, s, e)[:200],
                    rel,
                    f"{locator_prefix} {ln}",
                )
            )
    return facts


def docx_text(path: Path) -> str:
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(_zread(z, "word/document.xml"))
    paras = []
    for p in root.iter(f"{{{NS['w']}}}p"):
        paras.append("".join(t.text or "" for t in p.iter(f"{{{NS['w']}}}t")))
    return "\n".join(p for p in paras if p.strip())


def _slide_number(name: str) -> int:
    m = re.search(r"(\d+)", name.rsplit("/", 1)[1])
    assert m is not None  # callers pass only names matching ppt/slides/slide<N>.xml
    return int(m.group(1))


def pptx_slides(path: Path) -> list[str]:
    out = []
    with zipfile.ZipFile(path) as z:
        names = sorted((n for n in z.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", n)), key=_slide_number)
        for n in names:
            root = ET.fromstring(_zread(z, n))
            paras = ["".join(t.text or "" for t in p.iter(f"{{{NS['a']}}}t")) for p in root.iter(f"{{{NS['a']}}}p")]
            out.append("\n".join(p for p in paras if p.strip()))
    return out


def pdf_errors() -> tuple[type[Exception], ...]:
    """pypdf's own error types (PdfReadError and relatives), when pypdf is installed."""
    try:
        from pypdf.errors import PyPdfError
    except ImportError:
        return ()
    return (PyPdfError,)


def pdf_pages(path: Path) -> list[str]:
    from pypdf import PdfReader  # imported lazily: only needed for PDFs

    return [(page.extract_text() or "") for page in PdfReader(str(path)).pages]


# ------------------------------------------------------------------ conflicts
def label_words(text: str) -> set[str]:
    text = text.lower().replace("go-live", "golive")
    words = set()
    for w in re.findall(r"[a-z][a-z-]+", text):
        if w in STOP or len(w) < 3 and w not in ("go",):
            continue
        words.add(SYNONYMS.get(w, w))
    return words


XLSX_CELL = re.compile(r"^.+![A-Z]{1,3}\d+$")


def kind_of(f: Fact) -> str:
    """csv: one entity per row. xlsx: one metric per row. prose: free text."""
    if f.locator.startswith("row "):
        return "csv"
    return "xlsx" if XLSX_CELL.match(f.locator) else "prose"


def match_words(f: Fact) -> set[str]:
    text = re.sub(r"\[formula [^\]]*\]", "", f.text)
    if kind_of(f) != "xlsx":
        return label_words(text)
    title, _, label = text.partition(" | ")
    words = label_words(label)
    if "total" in label.lower():  # a Total row is the sheet's subject, named in its title
        words |= label_words(title)
    return words


def base_value(f: Fact) -> float:
    return float(f.value) * f.scale


def decimals(v: float) -> int:
    text = f"{v:.6f}".rstrip("0").rstrip(".")
    return len(text.split(".")[1]) if "." in text else 0


def same_at_precision(a: Fact, b: Fact) -> bool:
    """Equal when both round to the same figure at the coarser stated precision."""
    step: float = max(10 ** -decimals(float(a.value)) * a.scale, 10 ** -decimals(float(b.value)) * b.scale)
    return abs(base_value(a) - base_value(b)) <= step / 2 + 1e-9


def unit_family(f: Fact) -> str:
    if f.unit in ("%", "bps", "x", "date"):
        return f.unit
    return "money" if f.unit in ("USD", "EUR", "GBP") else "number"


def find_conflicts(facts: list[Fact]) -> list[tuple[Fact, Fact, set[str]]]:
    out: list[tuple[Fact, Fact, set[str]]] = []
    seen: set[tuple[str, ...]] = set()
    by_family: dict[str, list[Fact]] = {}
    for f in facts:
        by_family.setdefault(unit_family(f), []).append(f)
    for fam, group in by_family.items():
        for i, a in enumerate(group):
            wa = match_words(a)
            for b in group[i + 1 :]:
                if a.file == b.file:
                    continue
                if a.period and b.period and a.period != b.period:
                    continue
                if {kind_of(a), kind_of(b)} == {"csv", "xlsx"}:
                    continue  # a metric-per-row sheet vs an entity-per-row table: different subjects
                if kind_of(a) == kind_of(b) == "csv" and not (
                    label_words(a.text.split(" | ")[0]) & label_words(b.text.split(" | ")[0])
                ):
                    continue  # two tables, different entities
                wb_ = match_words(b)
                shared = wa & wb_
                smaller = min(len(wa), len(wb_)) or 1
                same_period = bool(a.period) and a.period == b.period
                if not (len(shared) >= 2 or (len(shared) == 1 and (smaller == 1 or same_period))):
                    continue
                if fam == "date":
                    same = a.value == b.value
                else:
                    va, vb = base_value(a), base_value(b)
                    if va == 0 or vb == 0:
                        continue
                    ratio = max(abs(va), abs(vb)) / min(abs(va), abs(vb))
                    if ratio > 3:  # different magnitude: almost always a different metric
                        continue
                    same = same_at_precision(a, b)
                if not same:
                    key = tuple(sorted((a.id, b.id)))
                    if key not in seen:
                        seen.add(key)
                        out.append((a, b, shared))
    # A figure with no period is compared only with the latest period of the same metric.
    pruned: list[tuple[Fact, Fact, set[str]]] = []
    for a, b, shared in out:
        dated, undated = (a, b) if a.period and not b.period else (b, a) if b.period and not a.period else (None, None)
        if dated is not None:
            sheet = dated.locator.split("!")[0]
            siblings = [
                f
                for f in facts
                if f.file == dated.file and f.locator.split("!")[0] == sheet and match_words(f) & shared and f.period
            ]
            latest = max((f.period for f in siblings), default=dated.period)
            if dated.period != latest:
                continue
        pruned.append((a, b, shared))
    return pruned


def fmt(f: Fact) -> str:
    if f.unit == "date":
        return str(f.value)
    scale = {1e3: "k", 1e6: "M", 1e9: "B"}.get(f.scale, "")
    prefix = f.unit + " " if f.unit not in ("", "%", "x", "bps") else ""
    suffix = f.unit if f.unit in ("%", "x") else " bps" if f.unit == "bps" else ""
    return f"{prefix}{f.value:g}{scale}{suffix}"


# ------------------------------------------------------------------ main
def collect(root: Path, max_files: int, max_bytes: int) -> tuple[list[Path], list[str]]:
    files: list[Path] = []
    skipped: list[str] = []
    for p in sorted(root.rglob("*")):
        rel = p.relative_to(root).as_posix()
        if any(part.startswith(".") for part in p.relative_to(root).parts):
            continue
        if p.is_symlink():
            skipped.append(f"{rel}: symlink (skipped)")
            continue
        if not p.is_file():
            continue
        if root not in p.resolve().parents:
            skipped.append(f"{rel}: resolves outside the folder (skipped)")
            continue
        if p.suffix.lower() not in SUPPORTED:
            skipped.append(f"{rel}: unsupported type {p.suffix or '(none)'}")
            continue
        if p.stat().st_size > max_bytes:
            skipped.append(f"{rel}: larger than the size cap")
            continue
        if len(files) >= max_files:
            skipped.append(f"{rel}: file cap reached")
            continue
        files.append(p)
    return files, skipped


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Ingest a source folder into a citable fact base.")
    ap.add_argument("folder")
    ap.add_argument("--out", default="brief")
    ap.add_argument("--max-files", type=int, default=200)
    ap.add_argument("--max-mb", type=float, default=50)
    args = ap.parse_args(argv)

    root = Path(args.folder).expanduser()
    if root.is_symlink():
        print("error: the input folder itself is a symlink; pass the real path", file=sys.stderr)
        return 2
    root = root.resolve(strict=True)
    if not root.is_dir():
        print(f"error: not a folder: {root}", file=sys.stderr)
        return 2
    out = Path(args.out).expanduser().resolve()
    if out == root or root in out.parents:
        print("error: --out must be outside the input folder", file=sys.stderr)
        return 2
    out.mkdir(parents=True, exist_ok=True)

    counter = iter(range(1, 10**7))

    def new_id() -> str:
        return f"F{next(counter):04d}"

    files, skipped = collect(root, args.max_files, int(args.max_mb * 1024 * 1024))
    facts: list[Fact] = []
    sources = [f"# Sources — {root.name}\n", f"{len(files)} file(s) read. Cite facts by id from facts.jsonl.\n"]
    for p in files:
        rel = p.relative_to(root).as_posix()
        ext = p.suffix.lower()
        size_kb = p.stat().st_size / 1024
        try:
            if ext == ".xlsx":
                summary, fs = xlsx_facts(p, rel, new_id)
                preview = ""
            elif ext == ".csv":
                summary, fs = csv_facts(p, rel, new_id)
                preview = "\n".join(p.read_text(errors="replace").splitlines()[:3])
            elif ext in TEXT_EXT:
                text = p.read_text(errors="replace")
                fs = prose_facts(text, rel, new_id)
                summary, preview = f"{len(text.split())} words", "\n".join(text.strip().splitlines()[:4])
            elif ext == ".docx":
                text = docx_text(p)
                fs = prose_facts(text, rel, new_id, "para")
                summary, preview = f"{len(text.split())} words", "\n".join(text.splitlines()[:4])
            elif ext == ".pptx":
                slides = pptx_slides(p)
                fs = []
                for i, s in enumerate(slides, 1):
                    fs += prose_facts(s, rel, new_id, f"slide {i} line")
                summary, preview = f"{len(slides)} slides", (slides[0] if slides else "")[:300]
            else:
                pages = pdf_pages(p)
                fs = []
                for i, s in enumerate(pages, 1):
                    fs += prose_facts(s, rel, new_id, f"page {i} line")
                summary, preview = f"{len(pages)} pages", (pages[0] if pages else "")[:300]
        except (
            zipfile.BadZipFile,
            KeyError,
            ET.ParseError,
            ValueError,
            UnicodeDecodeError,
            IndexError,
            AttributeError,
            *pdf_errors(),
        ) as err:  # one bad file lands in "Not read"; it never stops the run
            skipped.append(f"{rel}: could not parse ({type(err).__name__}: {err})")
            continue
        facts += fs
        sources.append(
            f"## {rel}\n\n- Type: {ext[1:]} · {size_kb:.0f} KB · {summary}\n- Facts extracted: {len(fs)}"
            + (f" ({fs[0].id}–{fs[-1].id})" if fs else "")
            + "\n"
        )
        if preview:
            sources.append("```\n" + preview.strip()[:400] + "\n```\n")
    if skipped:
        sources.append("## Not read\n\n" + "\n".join(f"- {s}" for s in skipped) + "\n")
    (out / "sources.md").write_text("\n".join(sources))
    with (out / "facts.jsonl").open("w") as fh:
        for f in facts:
            fh.write(json.dumps(asdict(f)) + "\n")

    conflicts = find_conflicts(facts)
    lines = [
        "# Possible conflicts",
        "",
        "Each pair looks like the same metric with different values. Decide which value is right,",
        "cite that fact id, and state the choice in the speaker notes. Resolve before the storyline.",
        "",
    ]
    if not conflicts:
        lines.append("None found. Still read the sources: this check matches labels, not meaning.")
    for a, b, shared in conflicts:
        lines.append(
            f"- **{', '.join(sorted(shared))}**: {fmt(a)} ({a.id}, {a.file} {a.locator}) vs "
            f"{fmt(b)} ({b.id}, {b.file} {b.locator})"
        )
        lines.append(f"  - {a.id}: {a.text}")
        lines.append(f"  - {b.id}: {b.text}")
    (out / "conflicts.md").write_text("\n".join(lines) + "\n")
    print(
        f"{len(files)} files, {len(facts)} facts, {len(conflicts)} possible conflicts, {len(skipped)} not read → {out}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
