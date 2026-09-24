// Northlane Freight (fictional) — 5-slide exec pitch, premium-decks Mode A
const pptxgen = require("pptxgenjs");

// ---- design tokens (declare once, reference everywhere) ----
const C = {
  bg: "FFFFFF",       // background
  fg: "1A1D23",       // foreground text
  brand: "0F3D5C",    // dominant navy
  support: "D8E4EC",  // support tone
  accent: "E8843C",   // accent — sparing, semantic
  mutedOnDark: "AFC6D6",
};
const F = { display: "Cambria", body: "Calibri" };
const T = { title: 40, header: 22, body: 15, caption: 11, stat: 66 };
const S = { margin: 0.6, gap: 0.4 };

const softShadow = () => ({ type: "outer", color: "000000", opacity: 0.18, blur: 14, offset: 3, angle: 90 });

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.33 x 7.5
const W = 13.33, H = 7.5;

// ---------- Slide 1 — title (dark full-bleed) ----------
{
  const s = pres.addSlide();
  s.addNotes("Talk track: the recommendation and the one number that justifies it. Source: lane-level contribution model (illustrative, fictional company).");
  s.background = { color: C.brand };
  s.addText("Northlane Freight", {
    x: S.margin, y: 2.55, w: W - 2 * S.margin, h: 1.1, align: "center",
    fontFace: F.display, fontSize: 48, bold: true, color: "FFFFFF", margin: 0,
  });
  s.addText("Freight orchestration for mid-market shippers", {
    x: S.margin, y: 3.7, w: W - 2 * S.margin, h: 0.55, align: "center",
    fontFace: F.body, fontSize: 18, color: C.mutedOnDark, margin: 0,
  });
  s.addText("Investment committee · March 2026", {
    x: S.margin, y: 6.4, w: W - 2 * S.margin, h: 0.4, align: "center",
    fontFace: F.body, fontSize: T.caption, color: C.mutedOnDark, margin: 0,
  });
  s.addNotes("Fictional company. 5-slide exec pitch sample for the premium-decks skill.");
}

// ---------- Slide 2 — recommendation first (split: stat left, facts right) ----------
{
  const s = pres.addSlide();
  s.addNotes("Talk track: mid-market shippers overpay on spot loads. Source: DAT spot vs. contract dry-van rates, 2025 average (illustrative).");
  s.background = { color: C.bg };
  s.addText("Recommendation: invest $2.0M to expand the carrier network into Texas", {
    x: S.margin, y: 0.55, w: W - 2 * S.margin, h: 1.0,
    fontFace: F.display, fontSize: 32, bold: true, color: C.fg, margin: 0,
  });
  // left: payback stat
  s.addText("11", {
    x: S.margin, y: 2.3, w: 4.4, h: 1.9, align: "center",
    fontFace: F.display, fontSize: 110, bold: true, color: C.brand, margin: 0,
  });
  s.addText("months to payback, from lane-level contribution margin", {
    x: S.margin, y: 4.3, w: 4.4, h: 0.9, align: "center",
    fontFace: F.body, fontSize: T.body, color: C.fg, margin: 0,
  });
  // right: three supporting facts as quiet cards
  const facts = [
    ["$4.6M ARR run-rate", "up from $2.1M four quarters ago"],
    ["14% freight-cost reduction", "median across 38 active customers"],
    ["94% net revenue retention", "vs. 87% logistics-SaaS benchmark"],
  ];
  facts.forEach((f, i) => {
    const y = 2.3 + i * 1.5;
    s.addShape(pres.ShapeType.roundRect, {
      x: 5.9, y, w: 6.8, h: 1.15, rectRadius: 0.12,
      fill: { color: C.support }, line: { type: "none" }, shadow: softShadow(),
    });
    s.addText([
      { text: f[0], options: { bold: true, fontSize: 17, color: C.brand, breakLine: true } },
      { text: f[1], options: { fontSize: 13, color: C.fg } },
    ], { x: 6.25, y: y + 0.12, w: 6.2, h: 0.95, fontFace: F.body, margin: 0, valign: "middle" });
  });
}

// ---------- Slide 3 — the problem, measured (text left, chart right) ----------
{
  const s = pres.addSlide();
  s.addNotes("Talk track: growth and retention are both above benchmark. Source: Northlane ARR and net revenue retention by quarter; logistics-SaaS benchmark (illustrative).");
  s.background = { color: C.bg };
  s.addText("Mid-market shippers pay 22% more per load than enterprise shippers", {
    x: S.margin, y: 0.55, w: W - 2 * S.margin, h: 1.0,
    fontFace: F.display, fontSize: 32, bold: true, color: C.fg, margin: 0,
  });
  s.addText([
    { text: "Enterprise shippers get contract rates through dedicated procurement teams. Mid-market shippers book on the spot market.", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "The difference is $405 per load. A shipper that moves 4,000 loads per year pays $1.6M more than an enterprise peer.", options: { breakLine: true } },
    { text: "", options: { breakLine: true } },
    { text: "Northlane pools mid-market volume and books it at contract rates.", options: { bold: true } },
  ], {
    x: S.margin, y: 2.1, w: 5.3, h: 4.2, fontFace: F.body, fontSize: T.body,
    color: C.fg, margin: 0, lineSpacing: 22,
  });
  s.addChart(pres.ChartType.bar, [
    { name: "Cost per load", labels: ["Enterprise", "Mid-market"], values: [1840, 2245] },
  ], {
    x: 6.5, y: 2.1, w: 6.2, h: 4.3, barDir: "bar",
    chartColors: [C.brand], showLegend: false,
    showValue: true, dataLabelPosition: "outEnd", dataLabelColor: C.fg,
    dataLabelFontFace: F.body, dataLabelFontSize: 13, dataLabelFormatCode: "$#,##0",
    catAxisLabelColor: C.fg, catAxisLabelFontFace: F.body, catAxisLabelFontSize: 13,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showTitle: false, valAxisMaxVal: 2600,
  });
  s.addText("Spot vs. contract dry-van rates, 2025 average — DAT benchmark (illustrative)", {
    x: 6.5, y: 6.55, w: 6.2, h: 0.35, fontFace: F.body, fontSize: T.caption,
    color: "6B7480", margin: 0,
  });
}

// ---------- Slide 4 — traction (chart left, metrics right) ----------
{
  const s = pres.addSlide();
  s.addNotes("Talk track: one decision, owner, and date. Source: network operations plan (illustrative).");
  s.background = { color: C.bg };
  s.addText("ARR more than doubled in four quarters, with retention above benchmark", {
    x: S.margin, y: 0.55, w: W - 2 * S.margin, h: 1.0,
    fontFace: F.display, fontSize: 32, bold: true, color: C.fg, margin: 0,
  });
  s.addChart(pres.ChartType.line, [
    { name: "ARR ($M)", labels: ["Q1 25", "Q2 25", "Q3 25", "Q4 25"], values: [2.1, 2.9, 3.8, 4.6] },
  ], {
    x: S.margin, y: 2.1, w: 6.6, h: 4.3,
    chartColors: [C.brand], lineSize: 3, lineSmooth: false,
    lineDataSymbol: "circle", lineDataSymbolSize: 8,
    showLegend: false, showValue: true, dataLabelPosition: "t",
    dataLabelColor: C.brand, dataLabelFontFace: F.body, dataLabelFontSize: 12,
    dataLabelFormatCode: "$0.0\\M",
    catAxisLabelColor: C.fg, catAxisLabelFontFace: F.body, catAxisLabelFontSize: 12,
    valAxisHidden: true, valGridLine: { style: "none" }, catGridLine: { style: "none" },
    showTitle: false, valAxisMaxVal: 5.5, valAxisMinVal: 0,
  });
  const metrics = [
    ["38", "active customers, up from 17 a year ago"],
    ["94%", "net revenue retention (benchmark: 87%)"],
    ["4", "of top 10 accounts expanded to new lanes in Q4"],
  ];
  metrics.forEach((m, i) => {
    const y = 2.1 + i * 1.5;
    s.addText(m[0], {
      x: 7.8, y, w: 1.7, h: 1.2, align: "right",
      fontFace: F.display, fontSize: 40, bold: true, color: C.accent, margin: 0, valign: "middle",
    });
    s.addText(m[1], {
      x: 9.7, y, w: 3.0, h: 1.2, fontFace: F.body, fontSize: 13.5,
      color: C.fg, margin: 0, valign: "middle",
    });
  });
}

// ---------- Slide 5 — the ask (dark close) ----------
{
  const s = pres.addSlide();
  s.background = { color: C.brand };
  s.addText("Approve $2.0M by March 15 to open the Texas lanes", {
    x: S.margin, y: 0.8, w: W - 2 * S.margin, h: 0.9,
    fontFace: F.display, fontSize: T.title, bold: true, color: "FFFFFF", margin: 0,
  });
  s.addText("Approve $2.0M by March 15 to contract 40 carriers across the Texas triangle.", {
    x: S.margin, y: 2.0, w: 10.5, h: 1.3,
    fontFace: F.body, fontSize: 22, color: "FFFFFF", margin: 0,
  });
  const rows = [
    ["Decision owner", "Head of Network Operations"],
    ["Funds released", "April 1, 2026"],
    ["First Texas lanes live", "June 2026"],
    ["Review gate", "September 2026 — continue only if payback tracks under 12 months"],
  ];
  rows.forEach((r, i) => {
    const y = 3.7 + i * 0.75;
    s.addText(r[0], {
      x: S.margin, y, w: 3.4, h: 0.6, fontFace: F.body, fontSize: T.body,
      bold: true, color: C.mutedOnDark, margin: 0, valign: "middle",
    });
    s.addText(r[1], {
      x: 4.2, y, w: 8.4, h: 0.6, fontFace: F.body, fontSize: T.body,
      color: "FFFFFF", margin: 0, valign: "middle",
    });
  });
}

pres.writeFile({ fileName: "northlane-pitch.pptx" }).then(() => console.log("written"));
