"""Read a .pptx or .html deck into a plain slide model for the QA scripts.

Shared by storyline-lint, trace-check, integrity-check, and layout-check.
PPTX XML is parsed with defusedxml; HTML with the standard-library parser.
Geometry is in inches (PPTX only).
"""
from __future__ import annotations

import posixpath
import re
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

from defusedxml import ElementTree as ET

EMU = 914400
NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
R_ID = f"{{{NS['r']}}}id"
R_EMBED = f"{{{NS['r']}}}embed"


@dataclass
class Shape:
    name: str
    kind: str                     # text | table | chart | picture | other
    x: float = 0.0
    y: float = 0.0
    w: float = 0.0
    h: float = 0.0
    text: str = ""
    font_pt: float = 0.0          # largest explicit run size, 0 if inherited
    placeholder: str = ""         # title, ctrTitle, body, ftr, sldNum, ...
    superscripts: list[str] = field(default_factory=list)
    alt: str = ""
    paragraphs: list[str] = field(default_factory=list)
    insets: tuple[float, float, float, float] = (0.1, 0.05, 0.1, 0.05)  # l, t, r, b inches
    autofit: str = ""             # "", "norm" (shrink), "sp" (resize shape)
    para_pts: list[float] = field(default_factory=list)  # largest run size per paragraph (0 = inherited)
    para_em: list[tuple[float, int]] = field(default_factory=list)  # (chars x pt over sized runs, unsized chars)


@dataclass
class Chart:
    kind: str                     # barChart, lineChart, pieChart, doughnutChart, ...
    grouping: str                 # clustered, stacked, percentStacked, standard
    categories: list[str]
    series: list[dict]            # {name, values, invisible}
    html: bool = False
    axis_min: float | None = None  # value-axis minimum when set explicitly
    bar_dir: str = ""              # "col" (vertical) or "bar" (horizontal) for bar charts
    problems: list[str] = field(default_factory=list)  # data the parser could not read (HTML recipes)


@dataclass
class Table:
    rows: list[list[str]]


@dataclass
class Slide:
    index: int
    title: str = ""
    texts: list[str] = field(default_factory=list)   # every visible text block, title first
    notes: str = ""
    shapes: list[Shape] = field(default_factory=list)
    charts: list[Chart] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)
    has_visual: bool = False       # chart, table, picture, svg, canvas
    footnotes: list[str] = field(default_factory=list)  # lines that start with a marker
    layout: str = ""
    tracker: str = ""              # section marker: shape named "tracker*", or short text above the title

    @property
    def body_text(self) -> str:
        return "\n".join(t for t in self.texts if t != self.title)


@dataclass
class Deck:
    path: Path
    kind: str
    width: float = 0.0
    height: float = 0.0
    slides: list[Slide] = field(default_factory=list)


# ------------------------------------------------------------------ PPTX
def _rels(z: zipfile.ZipFile, part: str) -> dict[str, str]:
    base, name = posixpath.split(part)
    rel_part = posixpath.join(base, "_rels", name + ".rels")
    if rel_part not in z.namelist():
        return {}
    root = ET.fromstring(z.read(rel_part))
    out = {}
    for r in root.findall("rel:Relationship", NS):
        target = r.get("Target")
        if r.get("TargetMode") == "External":
            continue
        absolute = target.startswith("/")
        out[r.get("Id")] = target[1:] if absolute else posixpath.normpath(posixpath.join(base, target))
    return out


def _text_of(tx) -> tuple[str, float, list[str], list[str]]:
    text, pt, sups, paras, _, _ = _text_detail(tx)
    return text, pt, sups, paras


def _text_detail(tx):
    """Text, largest run size, superscripts, non-empty paragraphs, each paragraph's largest size, and
    each paragraph's width basis as (sum of characters x point size over sized runs, unsized characters)."""
    paras, sizes, sups, para_pts, para_em = [], [], [], [], []
    for p in tx.iter(f"{{{NS['a']}}}p"):
        runs = []
        p_sizes = []
        run_em: list[tuple[int, float]] = []  # (characters, point size or 0 when inherited)
        for r in p:
            if r.tag == f"{{{NS['a']}}}r":
                rpr = r.find("a:rPr", NS)
                t = r.find("a:t", NS)
                txt = t.text if t is not None and t.text else ""
                if rpr is not None:
                    if rpr.get("sz"):
                        sizes.append(int(rpr.get("sz")) / 100)
                        p_sizes.append(int(rpr.get("sz")) / 100)
                    if rpr.get("baseline") and int(rpr.get("baseline")) > 0 and txt.strip():
                        sups.append(txt.strip())
                run_em.append((len(txt), int(rpr.get("sz")) / 100 if rpr is not None and rpr.get("sz") else 0.0))
                runs.append(txt)
            elif r.tag == f"{{{NS['a']}}}br":
                runs.append("\n")
            elif r.tag == f"{{{NS['a']}}}fld":
                t = r.find("a:t", NS)
                runs.append(t.text if t is not None and t.text else "")
        paras.append("".join(runs))
        para_pts.append(max(p_sizes, default=0.0))
        para_em.append((sum(n * sz for n, sz in run_em if sz), sum(n for n, sz in run_em if not sz)))
    keep = [i for i, p in enumerate(paras) if p.strip()]
    text = "\n".join(paras[i] for i in keep)
    return (text, max(sizes, default=0.0), sups, [paras[i] for i in keep], [para_pts[i] for i in keep],
            [para_em[i] for i in keep])


def _geometry(el) -> tuple[float, float, float, float]:
    xfrm = el.find(".//a:xfrm", NS)
    if xfrm is None:
        xfrm = el.find(".//p:xfrm", NS)
    if xfrm is None:
        return 0.0, 0.0, 0.0, 0.0
    off, ext = xfrm.find("a:off", NS), xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return 0.0, 0.0, 0.0, 0.0
    return (int(off.get("x")) / EMU, int(off.get("y")) / EMU, int(ext.get("cx")) / EMU, int(ext.get("cy")) / EMU)


def _chart(z: zipfile.ZipFile, part: str) -> Chart | None:
    if part not in z.namelist():
        return None
    root = ET.fromstring(z.read(part))
    plot = root.find(".//c:plotArea", NS)
    if plot is None:
        return None
    for el in plot:
        tag = el.tag.split("}")[1]
        if not tag.endswith("Chart"):
            continue
        grouping_el = el.find("c:grouping", NS)
        grouping = grouping_el.get("val") if grouping_el is not None else "standard"
        cats, series = [], []
        for ser in el.findall("c:ser", NS):
            name_el = ser.find(".//c:tx//c:v", NS)
            vals = [float(v.text) for v in ser.findall(".//c:val//c:pt/c:v", NS) if v.text not in (None, "")]
            if not cats:
                cats = [v.text or "" for v in ser.findall(".//c:cat//c:pt/c:v", NS)]
            sppr = ser.find("c:spPr", NS)
            fill = sppr.find("a:solidFill/a:srgbClr", NS) if sppr is not None else None
            # A floating-bar base is hidden either with noFill or by filling it with the white background.
            invisible = sppr is not None and (sppr.find("a:noFill", NS) is not None
                                              or (fill is not None and fill.get("val", "").upper() == "FFFFFF"))
            series.append({"name": name_el.text if name_el is not None else "", "values": vals,
                           "invisible": invisible})
        mn = root.find(".//c:valAx/c:scaling/c:min", NS)
        axis_min = float(mn.get("val")) if mn is not None and mn.get("val") not in (None, "") else None
        bd = el.find("c:barDir", NS)
        return Chart(tag, grouping, cats, series, axis_min=axis_min, bar_dir=bd.get("val") if bd is not None else "")
    return None


def load_pptx(path: Path) -> Deck:
    deck = Deck(path=path, kind="pptx")
    with zipfile.ZipFile(path) as z:
        pres = ET.fromstring(z.read("ppt/presentation.xml"))
        sz = pres.find("p:sldSz", NS)
        if sz is not None:
            deck.width, deck.height = int(sz.get("cx")) / EMU, int(sz.get("cy")) / EMU
        prels = _rels(z, "ppt/presentation.xml")
        order = [prels[s.get(R_ID)] for s in pres.find("p:sldIdLst", NS).findall("p:sldId", NS)]
        for i, part in enumerate(order, 1):
            slide = Slide(index=i)
            root = ET.fromstring(z.read(part))
            rels = _rels(z, part)
            for rid_target in rels.values():
                if "slideLayouts/" in rid_target:
                    slide.layout = posixpath.basename(rid_target)
                if "notesSlides/" in rid_target and rid_target in z.namelist():
                    nroot = ET.fromstring(z.read(rid_target))
                    for sp in nroot.iter(f"{{{NS['p']}}}sp"):
                        ph = sp.find(".//p:nvPr/p:ph", NS)
                        if ph is not None and ph.get("type") == "body":
                            tx = sp.find("p:txBody", NS)
                            if tx is not None:
                                slide.notes = _text_of(tx)[0]
            tree = root.find("p:cSld/p:spTree", NS)
            for el in tree.iter():
                tag = el.tag.split("}")[-1]
                if tag not in ("sp", "graphicFrame", "pic"):
                    continue
                cnv = el.find(".//p:cNvPr", NS)
                name = cnv.get("name", "") if cnv is not None else ""
                x, y, w, h = _geometry(el)
                ph = el.find(".//p:nvPr/p:ph", NS)
                placeholder = (ph.get("type") or "body") if ph is not None else ""
                if tag == "sp":
                    tx = el.find("p:txBody", NS)
                    if tx is None:
                        slide.shapes.append(Shape(name, "other", x, y, w, h, placeholder=placeholder))
                        continue
                    text, pt, sups, paras, para_pts, para_em = _text_detail(tx)
                    body = tx.find("a:bodyPr", NS)
                    insets = (0.1, 0.05, 0.1, 0.05)
                    autofit = ""
                    if body is not None:
                        insets = tuple(int(body.get(k, d)) / EMU for k, d in
                                       (("lIns", 91440), ("tIns", 45720), ("rIns", 91440), ("bIns", 45720)))
                        if body.find("a:normAutofit", NS) is not None:
                            autofit = "norm"
                        elif body.find("a:spAutoFit", NS) is not None:
                            autofit = "sp"
                    shape = Shape(name, "text", x, y, w, h, text, pt, placeholder, sups, "", paras, insets, autofit,
                                  para_pts, para_em)
                    slide.shapes.append(shape)
                    if text.strip():
                        slide.texts.append(text)
                elif tag == "graphicFrame":
                    tbl = el.find(".//a:tbl", NS)
                    chart_ref = el.find(".//c:chart", NS)
                    if tbl is not None:
                        rows = []
                        for tr in tbl.findall("a:tr", NS):
                            rows.append([_text_of(tc.find("a:txBody", NS))[0] if tc.find("a:txBody", NS) is not None
                                         else "" for tc in tr.findall("a:tc", NS)])
                        slide.tables.append(Table(rows))
                        slide.shapes.append(Shape(name, "table", x, y, w, h, "\n".join(" | ".join(r) for r in rows)))
                        slide.texts.append("\n".join(" ".join(r) for r in rows))
                        slide.has_visual = True
                    elif chart_ref is not None:
                        ch = _chart(z, rels.get(chart_ref.get(R_ID), ""))
                        if ch:
                            slide.charts.append(ch)
                        slide.shapes.append(Shape(name, "chart", x, y, w, h))
                        slide.has_visual = True
                elif tag == "pic":
                    alt = cnv.get("descr", "") if cnv is not None else ""
                    slide.shapes.append(Shape(name, "picture", x, y, w, h, alt=alt))
                    slide.has_visual = True
            slide.title = _pick_title(slide, deck.height)
            slide.tracker = _pick_tracker(slide)
            if slide.title in slide.texts:
                slide.texts.remove(slide.title)
            slide.texts.insert(0, slide.title) if slide.title else None
            slide.footnotes = _footnote_lines(slide.texts)
            deck.slides.append(slide)
    return deck


def _pick_title(slide: Slide, height: float) -> str:
    for s in slide.shapes:
        if s.placeholder in ("title", "ctrTitle") and s.text.strip():
            return s.text.strip()
    for s in slide.shapes:
        if s.name.lower().startswith("title") and s.text.strip():
            return s.text.strip()
    # The title is the topmost substantial text in the top band; a larger stat callout sits below it.
    band = [s for s in slide.shapes if s.kind == "text" and s.text.strip() and s.y < max(height, 1) * 0.35
            and len(re.findall(r"[A-Za-z]{2,}", s.text)) >= 3]
    big = [s for s in band if s.font_pt >= 18] or [s for s in band if s.font_pt == 0]
    if not big:
        return band[0].text.strip() if len(band) == 1 else ""
    best = min(big, key=lambda s: (round(s.y, 1), -s.font_pt))
    return best.text.strip()


def _pick_tracker(slide: Slide) -> str:
    for s in slide.shapes:
        if s.name.lower().startswith("tracker") and s.text.strip():
            return s.text.strip()
    title = next((s for s in slide.shapes if slide.title and s.text.strip() == slide.title), None)
    if title is None:
        return ""
    for s in slide.shapes:
        if (s.kind == "text" and s is not title and s.text.strip() and s.y + s.h <= title.y + 0.02
                and len(s.text.split()) <= 12 and not re.fullmatch(r"\s*\d+\s*", s.text)):
            return s.text.strip()
    return ""


FOOTNOTE_RE = re.compile(r"^\s*(?:\(?(\d{1,2}|[a-z])\)?[.)]?\s+[A-Z(\"“]|([¹²³⁴⁵⁶⁷⁸⁹])\s?\S)")


def _footnote_lines(texts: list[str]) -> list[str]:
    out = []
    for block in texts:
        for line in block.splitlines():
            if re.match(r"^\s*(Notes?|Sources?)\s*:", line, re.I) or (FOOTNOTE_RE.match(line) and len(line) < 220):
                out.append(line.strip())
    return out


# ------------------------------------------------------------------ HTML
class _HtmlDeck(HTMLParser):
    VOID = {"br", "img", "hr", "meta", "link", "input", "source", "col", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.slides: list[Slide] = []
        self.cur: Slide | None = None
        self.depth = 0
        self.stack: list[str] = []
        self.buf: list[str] = []
        self.in_notes = 0
        self.notes: list[str] = []
        self.heading: list[str] | None = None
        self.in_sup = False
        self.sups: list[str] = []
        self.in_skip = 0
        self.row: list[str] | None = None
        self.cell: list[str] | None = None
        self.table: list[list[str]] | None = None
        self.tracker_depth = 0
        self.tracker_buf: list[str] = []
        self.wf_depth = 0  # an HTML waterfall (html-finance.md): bars carry --from/--to in style
        self.wf: list[tuple[str, float, float]] = []
        self.wf_bad: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag in self.VOID:
            if self.cur and tag == "img":
                self.cur.has_visual = True
                self.cur.shapes.append(Shape("img", "picture", alt=a.get("alt", "")))
            if tag == "br":
                self.buf.append("\n")
                if self.heading is not None:
                    self.heading.append(" ")
            return
        if tag == "section" and "slide" in classes and self.cur is None:
            self.cur = Slide(index=len(self.slides) + 1)
            self.depth = 0
        if self.cur is None:
            return
        self.depth += 1
        self.stack.append(tag)
        if tag in ("script", "style"):
            self.in_skip += 1
        if tag == "aside" and "notes" in classes:
            self.in_notes = self.depth
        if tag in ("h1", "h2") and not self.cur.title and not self.in_notes:
            self.heading = []
        if tag == "sup":
            self.in_sup = True
        if "tracker" in classes and not self.in_notes:
            self.tracker_depth = self.depth
            self.tracker_buf = []
        if tag in ("svg", "canvas", "table"):
            self.cur.has_visual = True
        if "wf" in classes and not self.wf_depth:
            self.wf_depth, self.wf, self.wf_bad = self.depth, [], []
            self.cur.has_visual = True
        if "wf-bar" in classes and self.wf_depth:
            props = dict(re.findall(r"--(from|to)\s*:\s*([^;]*)", a.get("style") or ""))
            label = a.get("data-label", "") or f"bar {len(self.wf) + len(self.wf_bad) + 1}"
            try:
                self.wf.append((label, float(props["from"]), float(props["to"])))
            except (KeyError, ValueError):
                self.wf_bad.append(label)
        if tag == "canvas" or (tag == "svg" and ("chart" in " ".join(classes) or a.get("role") == "img")):
            self.cur.charts.append(Chart("svg" if tag == "svg" else "canvas", "", [], [], html=True))
        if tag == "table":
            self.table = []
        if tag == "tr" and self.table is not None:
            self.row = []
        if tag in ("td", "th") and self.row is not None:
            self.cell = []
        if tag in ("p", "li", "div", "h1", "h2", "h3", "h4", "figcaption", "td", "th", "tr", "footer"):
            self.buf.append("\n")

    def handle_endtag(self, tag):
        if self.cur is None or tag in self.VOID:
            return
        if tag in ("script", "style") and self.in_skip:
            self.in_skip -= 1
        if tag in ("h1", "h2") and self.heading is not None:
            self.cur.title = re.sub(r"\s+", " ", "".join(self.heading)).strip()
            self.heading = None
        if tag == "sup":
            self.in_sup = False
        if self.tracker_depth and self.depth == self.tracker_depth:
            self.cur.tracker = re.sub(r"\s+", " ", "".join(self.tracker_buf)).strip()
            self.tracker_depth = 0
        if tag in ("td", "th") and self.cell is not None and self.row is not None:
            self.row.append(re.sub(r"\s+", " ", "".join(self.cell)).strip())
            self.cell = None
        if tag == "tr" and self.row is not None and self.table is not None:
            self.table.append(self.row)
            self.row = None
        if tag == "table" and self.table is not None:
            self.cur.tables.append(Table(self.table))
            self.table = None
        if self.in_notes and self.depth == self.in_notes and tag == "aside":
            self.in_notes = 0
        if self.wf_depth and self.depth == self.wf_depth:
            base = [min(f, t) for _, f, t in self.wf]
            span = [abs(t - f) for _, f, t in self.wf]
            self.cur.charts.append(Chart("barChart", "stacked", [lbl for lbl, _, _ in self.wf],
                                         [{"name": "base", "values": base, "invisible": True},
                                          {"name": "bar", "values": span, "invisible": False}],
                                         html=True, bar_dir="col",
                                         problems=[f"waterfall bar '{b}': cannot read a number from --from/--to "
                                                   "(write plain numbers, not calc() or var())" for b in self.wf_bad]
                                         + ([] if self.wf else ["waterfall has no readable bars"])))
            self.wf_depth, self.wf, self.wf_bad = 0, [], []
        if tag in ("p", "li", "div", "h1", "h2", "h3", "h4", "figcaption", "td", "th", "tr"):
            self.buf.append("\n")
        self.depth -= 1
        if self.stack:
            self.stack.pop()
        if self.depth == 0 and tag == "section":
            self._close()

    def handle_data(self, data):
        if self.cur is None or self.in_skip:
            return
        if self.in_notes:
            self.notes.append(data)
            return
        if self.heading is not None:
            self.heading.append(data)
        if self.cell is not None:
            self.cell.append(data)
        if self.tracker_depth:
            self.tracker_buf.append(data)
        if self.in_sup and data.strip():
            self.sups.append(data.strip())
        self.buf.append(data)

    def _close(self):
        text = re.sub(r"[ \t]+", " ", "".join(self.buf))
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        s = self.cur
        s.texts = ([s.title] if s.title else []) + [ln for ln in lines if ln != s.title]
        s.notes = re.sub(r"\s+", " ", "".join(self.notes)).strip()
        s.shapes.append(Shape("sup", "text", superscripts=list(self.sups)))
        s.footnotes = _footnote_lines(s.texts[1:])
        self.slides.append(s)
        self.cur, self.buf, self.notes, self.sups = None, [], [], []


def load_html(path: Path) -> Deck:
    parser = _HtmlDeck()
    parser.feed(path.read_text(errors="replace"))
    return Deck(path=path, kind="html", slides=parser.slides)


def load(path: str | Path) -> Deck:
    p = Path(path)
    if p.suffix.lower() == ".pptx":
        return load_pptx(p)
    if p.suffix.lower() in (".html", ".htm"):
        return load_html(p)
    raise ValueError(f"unsupported deck type: {p.suffix} (expected .pptx or .html)")
