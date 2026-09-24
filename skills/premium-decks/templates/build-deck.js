// board-deck template — 8-slide executive decision deck.
// ALL content comes from a data JSON (arg 1, default ./deck-data.json).
// Layout code carries no numbers and no topic-specific text.
// Usage: node build-deck.js [deck-data.json]
// resolve pptxgenjs from the skill dir OR the working directory
let pptxgen;
try {
  pptxgen = require("pptxgenjs");
} catch {
  pptxgen = require("module").createRequire(
    require("path").join(process.cwd(), "noop.js"))("pptxgenjs");
}
const path = process.argv[2] || "./deck-data.json";
const D = require(require("path").resolve(path));

// ---- design tokens (JSON "theme" overrides any of these) ----
const C = Object.assign({
  bg: "FFFFFF",
  fg: "22252B",
  brand: "5B2333",     // dominant
  support: "EDE6E0",   // tint
  rule: "D8CFC7",      // hairline table rules
  accent: "B08A3E",    // key figures only, large sizes only
  mutedOnDark: "E3CBD2",
  muted: "6B7480",
}, (D.theme && D.theme.colors) || {});
const F = Object.assign({ display: "Bookman Old Style", body: "Arial" }, (D.theme && D.theme.fonts) || {});
const T = { title: 30, body: 14.5, caption: 11 };
const S = { margin: 0.6 };

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";
const W = 13.33;

const title = (s, text, color = C.fg) => s.addText(text, {
  x: S.margin, y: 0.5, w: W - 2 * S.margin, h: 1.15,
  fontFace: F.display, fontSize: T.title, bold: true, color, margin: 0, valign: "top",
});
const disclaimer = D.illustrative ? " [All figures are illustrative placeholders — see the deck data JSON.]" : "";
const notes = (s, txt) => s.addNotes((txt || "") + disclaimer);
const quietChart = {
  showLegend: false, showTitle: false,
  valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
  catAxisLineShow: false,
};

// ---------- 1 · title (dark bookend) ----------
{
  const s = pres.addSlide();
  s.background = { color: C.brand };
  s.addText(D.meeting.title, {
    x: S.margin, y: 2.7, w: W - 2 * S.margin, h: 1.0, align: "center",
    fontFace: F.display, fontSize: 44, bold: true, color: "FFFFFF", margin: 0,
  });
  s.addText(D.meeting.subtitle, {
    x: S.margin, y: 3.85, w: W - 2 * S.margin, h: 0.5, align: "center",
    fontFace: F.body, fontSize: 17, color: C.mutedOnDark, margin: 0,
  });
  s.addText(D.meeting.footer, {
    x: S.margin, y: 6.4, w: W - 2 * S.margin, h: 0.4, align: "center",
    fontFace: F.body, fontSize: T.caption, color: C.mutedOnDark, margin: 0,
  });
  notes(s, D.meeting.notes);
}

// ---------- 2 · recommendation (open stat strip) ----------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  title(s, D.recommendation.title);
  const colW = 3.75, gap = 0.44, x0 = S.margin;
  D.recommendation.stats.slice(0, 3).forEach((st, i) => {
    const x = x0 + i * (colW + gap);
    s.addText(st.value, {
      x, y: 2.5, w: colW, h: 1.3, align: "center",
      fontFace: F.display, fontSize: 46, bold: true, color: C.accent, margin: 0, valign: "top",
    });
    s.addText([
      { text: st.label, options: { bold: true, fontSize: 15, color: C.fg, breakLine: true } },
      { text: st.detail || "", options: { fontSize: 12.5, color: C.muted } },
    ], { x, y: 3.9, w: colW, h: 1.3, align: "center", fontFace: F.body, margin: 0, valign: "top", paraSpaceAfter: 4 });
    if (i > 0) s.addShape(pres.ShapeType.line, {
      x: x - gap / 2 - 0.01, y: 2.7, w: 0, h: 2.2, line: { color: C.rule, width: 1 },
    });
  });
  if (D.recommendation.kicker) s.addText(D.recommendation.kicker, {
    x: S.margin, y: 6.3, w: W - 2 * S.margin, h: 0.5,
    fontFace: F.body, fontSize: T.body, color: C.fg, margin: 0,
  });
  notes(s, D.recommendation.notes);
}

// ---------- 3 · trend (column chart left, prose right) ----------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  title(s, D.trend.title);
  s.addChart(pres.ChartType.bar, [
    { name: D.trend.chart.series, labels: D.trend.chart.labels, values: D.trend.chart.values },
  ], Object.assign({
    x: S.margin, y: 2.1, w: 6.2, h: 4.3, barDir: "col",
    chartColors: [C.brand],
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.fg,
    dataLabelFontFace: F.body, dataLabelFontSize: 13,
    catAxisLabelColor: C.fg, catAxisLabelFontFace: F.body, catAxisLabelFontSize: 13,
    valAxisMaxVal: D.trend.chart.max,
  }, quietChart));
  if (D.trend.chart.caption) s.addText(D.trend.chart.caption, {
    x: S.margin, y: 6.55, w: 6.2, h: 0.35, fontFace: F.body, fontSize: T.caption, color: C.muted, margin: 0,
  });
  const runs = [];
  D.trend.paragraphs.forEach((p, i) => {
    if (i > 0) runs.push({ text: "", options: { breakLine: true } });
    runs.push({ text: p.text, options: { bold: !!p.bold, breakLine: true } });
  });
  s.addText(runs, {
    x: 7.4, y: 2.2, w: 5.3, h: 4.2, fontFace: F.body, fontSize: T.body,
    color: C.fg, margin: 0, lineSpacing: 22, valign: "top",
  });
  notes(s, D.trend.notes);
}

// ---------- 4 · cost/driver breakdown (full-width horizontal bars) ----------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  title(s, D.cost.title);
  // labels/values MUST be ascending so the largest bar renders on top
  s.addChart(pres.ChartType.bar, [
    { name: D.cost.chart.series, labels: D.cost.chart.labels, values: D.cost.chart.values },
  ], Object.assign({
    x: S.margin, y: 2.0, w: W - 2 * S.margin - 0.4, h: 3.7, barDir: "bar",
    chartColors: [C.brand],
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.fg,
    dataLabelFontFace: F.body, dataLabelFontSize: 13,
    dataLabelFormatCode: D.cost.chart.format || "General",
    catAxisLabelColor: C.fg, catAxisLabelFontFace: F.body, catAxisLabelFontSize: 13,
    valAxisMaxVal: D.cost.chart.max,
  }, quietChart));
  if (D.cost.takeaway) s.addText(D.cost.takeaway, {
    x: S.margin, y: 6.0, w: W - 2 * S.margin, h: 0.75,
    fontFace: F.body, fontSize: T.body, color: C.fg, margin: 0, valign: "top",
  });
  if (D.cost.chart.caption) s.addText(D.cost.chart.caption, {
    x: S.margin, y: 6.85, w: 8.0, h: 0.35, fontFace: F.body, fontSize: T.caption, color: C.muted, margin: 0,
  });
  notes(s, D.cost.notes);
}

// ---------- 5 · options table (recommended column highlighted) ----------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  title(s, D.options.title);
  const colX = [4.3, 7.35, 10.4], colW = 2.85, labelX = S.margin;
  const rec = D.options.recommended_index;
  s.addText("RECOMMENDED", {
    x: colX[rec], y: 1.78, w: colW, h: 0.28, align: "center",
    fontFace: F.body, fontSize: 10.5, bold: true, color: C.accent, charSpacing: 2, margin: 0,
  });
  D.options.headers.forEach((h2, i) => {
    if (i === rec) s.addShape(pres.ShapeType.roundRect, {
      x: colX[i], y: 2.1, w: colW, h: 0.5, rectRadius: 0.08,
      fill: { color: C.brand }, line: { type: "none" },
    });
    s.addText(h2, {
      x: colX[i], y: 2.1, w: colW, h: 0.5, align: "center", valign: "middle",
      fontFace: F.body, fontSize: 14.5, bold: true,
      color: i === rec ? "FFFFFF" : C.brand, margin: 0,
    });
  });
  D.options.rows.forEach((r, i) => {
    const y = 2.85 + i * 0.72;
    s.addShape(pres.ShapeType.line, {
      x: labelX, y: y - 0.06, w: W - 2 * S.margin, h: 0, line: { color: C.rule, width: 0.75 },
    });
    s.addText(r[0], {
      x: labelX, y, w: 3.5, h: 0.6, fontFace: F.body, fontSize: T.body,
      bold: true, color: C.muted, margin: 0, valign: "middle",
    });
    r.slice(1).forEach((v, k) => s.addText(v, {
      x: colX[k], y, w: colW, h: 0.6, align: "center", fontFace: F.body,
      fontSize: T.body, bold: k === rec, color: C.fg, margin: 0, valign: "middle",
    }));
  });
  if (D.options.footnote) s.addText(D.options.footnote, {
    x: S.margin, y: 6.7, w: W - 2 * S.margin, h: 0.4,
    fontFace: F.body, fontSize: 12.5, color: C.muted, margin: 0,
  });
  notes(s, D.options.notes);
}

// ---------- 6 · execution timeline ----------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  title(s, D.timeline.title);
  const lineY = 3.2, xs = [1.6, 5.7, 9.8], wNode = 3.4;
  s.addShape(pres.ShapeType.line, {
    x: xs[0] + 0.35, y: lineY, w: xs[2] - xs[0], h: 0, line: { color: C.rule, width: 3 },
  });
  D.timeline.waves.slice(0, 3).forEach((n, i) => {
    s.addShape(pres.ShapeType.ellipse, {
      x: xs[i] + 0.2, y: lineY - 0.15, w: 0.3, h: 0.3,
      fill: { color: C.brand }, line: { type: "none" },
    });
    s.addText([
      { text: n.name, options: { bold: true, fontSize: 15, color: C.brand, breakLine: true } },
      { text: n.action, options: { fontSize: 13.5, color: C.fg } },
    ], {
      x: xs[i] - 1.05, y: lineY + 0.45, w: wNode, h: 1.2, align: "center",
      valign: "top", fontFace: F.body, margin: 0, paraSpaceAfter: 6,
    });
    // fixed y so the accent row aligns regardless of wrap depth
    if (n.saving) s.addText(n.saving, {
      x: xs[i] - 1.05, y: lineY + 1.75, w: wNode, h: 0.4, align: "center",
      valign: "top", fontFace: F.body, fontSize: 13.5, bold: true, color: C.accent, margin: 0,
    });
  });
  if (D.timeline.kicker) s.addText(D.timeline.kicker, {
    x: S.margin, y: 6.3, w: W - 2 * S.margin, h: 0.6,
    fontFace: F.body, fontSize: T.body, color: C.fg, margin: 0,
  });
  notes(s, D.timeline.notes);
}

// ---------- 7 · risks table ----------
{
  const s = pres.addSlide();
  s.background = { color: C.bg };
  title(s, D.risks.title);
  const cols = [
    { x: S.margin, w: 4.3, h: "Risk" },
    { x: 5.1, w: 5.2, h: "Mitigation" },
    { x: 10.5, w: 2.2, h: "Owner" },
  ];
  cols.forEach(c => s.addText(c.h.toUpperCase(), {
    x: c.x, y: 2.1, w: c.w, h: 0.35, fontFace: F.body, fontSize: 11,
    bold: true, color: C.muted, charSpacing: 1.5, margin: 0,
  }));
  D.risks.rows.forEach((r, i) => {
    const y = 2.65 + i * 1.05;
    s.addShape(pres.ShapeType.line, {
      x: S.margin, y: y - 0.08, w: W - 2 * S.margin, h: 0, line: { color: C.rule, width: 0.75 },
    });
    s.addText(r[0], { x: cols[0].x, y, w: cols[0].w, h: 1.0, fontFace: F.body, fontSize: T.body, bold: true, color: C.brand, margin: 0, valign: "top" });
    s.addText(r[1], { x: cols[1].x, y, w: cols[1].w, h: 1.0, fontFace: F.body, fontSize: T.body, color: C.fg, margin: 0, valign: "top" });
    s.addText(r[2], { x: cols[2].x, y, w: cols[2].w, h: 1.0, fontFace: F.body, fontSize: T.body, bold: true, color: C.fg, margin: 0, valign: "top" });
  });
  notes(s, D.risks.notes);
}

// ---------- 8 · the ask (dark bookend) ----------
{
  const s = pres.addSlide();
  s.background = { color: C.brand };
  title(s, D.ask.title || "The ask", "FFFFFF");
  s.addText(D.ask.statement, {
    x: S.margin, y: 1.9, w: 11.0, h: 1.2,
    fontFace: F.body, fontSize: 20, color: "FFFFFF", margin: 0, valign: "top",
  });
  D.ask.rows.forEach((r, i) => {
    const y = 3.6 + i * 0.75;
    s.addText(r[0], {
      x: S.margin, y, w: 3.4, h: 0.6, fontFace: F.body, fontSize: T.body,
      bold: true, color: C.mutedOnDark, margin: 0, valign: "middle",
    });
    s.addText(r[1], {
      x: 4.2, y, w: 8.4, h: 0.6, fontFace: F.body, fontSize: T.body,
      color: "FFFFFF", margin: 0, valign: "middle",
    });
  });
  notes(s, D.ask.notes);
}

const out = D.output || "board-deck.pptx";
pres.writeFile({ fileName: out }).then(() => console.log("written: " + out));
