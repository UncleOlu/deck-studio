"""The strategic-alternatives sample (banking register, kind "pitch"), built through the ingest path.

Halden Freight Systems and every figure here are invented. The page order follows
references/banking-pitchbook.md (Sell-side / strategic-alternatives skeleton), which comes
from research/pitchbook-findings.md: key considerations, situation, valuation, alternatives,
buyer universe, process, recommendation, next steps, disclaimer at the back.
Called from build_samples.py.
"""

from __future__ import annotations

import csv
import statistics
from pathlib import Path
from typing import Any, Callable, Protocol

from openpyxl import Workbook


class FactLookup(Protocol):
    """The part of build_samples.Facts this module reads (a structural type avoids a circular import)."""

    rows: list[dict[str, Any]]

    def id(self, file: str, locator: str) -> str: ...

    def val(self, file: str, locator: str) -> float: ...

    def span(self, file: str) -> str: ...


CURRENT_DATE = "1 Sep 2026"
BUYERS = [  # code, type, tier, capacity $bn (market cap or fund size), rationale
    ("Strategic A", "Strategic", 1, 14.2, "Adds cross-border lanes; overlap in three hubs"),
    ("Strategic B", "Strategic", 1, 9.8, "Fills its cold-chain gap"),
    ("Strategic C", "Strategic", 2, 4.1, "Regional consolidation"),
    ("Sponsor D", "Sponsor", 1, 18.0, "Logistics platform in its current fund"),
    ("Sponsor E", "Sponsor", 2, 6.5, "Prior freight investments"),
]


def halden_inputs(d: Path, save: Callable[[Workbook, Path], None], write: Callable[[Path, str], None]) -> None:
    d.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    c = wb.active
    c.title = "Cap"
    c.append(["Halden Freight Systems (fictional) — capitalization", "value", "unit"])
    c.append([f"Share price ({CURRENT_DATE})", 18.60, "$"])
    c.append(["Diluted shares outstanding", 86.0, "M"])
    c.append(["Net debt", 410, "$M"])
    c.append(["LTM EBITDA", 212, "$M"])
    c.append(["LTM revenue", 1480, "$M"])
    save(wb, d / "capitalization.xlsx")
    wb = Workbook()
    p = wb.active
    p.title = "Projections ($M)"
    p.append(["", "FY26E", "FY27E", "FY28E", "FY29E", "FY30E"])
    p.append(["Revenue", 1560, 1640, 1720, 1800, 1870])
    p.append(["EBITDA", 228, 246, 263, 279, 294])
    p.append(["Unlevered FCF", 118, 131, 144, 156, 167])
    n = wb.create_sheet("Notes")
    n.append(["Management case prepared for the Board, August 2026."])
    n.append(["WACC range used by management: 8.5%-9.5%; terminal growth 2.0%-3.0%."])
    save(wb, d / "management_projections.xlsx")
    with (d / "trading_comps.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["company", "ev_usd_m", "ebitda_ltm_usd_m", "ebitda_ntm_usd_m"])
        w.writerows(
            [
                ["Peer Arden", 3900, 402, 425],
                ["Peer Bexley", 2650, 298, 315],
                ["Peer Cairn", 5200, 498, 530],
                ["Peer Dunmore", 1800, 214, 226],
                ["Peer Esker", 4400, 418, 447],
            ]
        )
    with (d / "precedent_transactions.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "target", "acquirer", "ev_usd_m", "ev_ltm_ebitda_x"])
        w.writerows(
            [
                ["2023-05", "Target Kappa", "Strategic P", 1500, 9.6],
                ["2024-02", "Target Lambda", "Sponsor Q", 2300, 10.4],
                ["2025-04", "Target Mu", "Strategic R", 3100, 11.8],
                ["2026-01", "Target Nu", "Sponsor S", 1900, 10.1],
            ]
        )
    with (d / "share_price_52w.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["week", "close_usd"])
        for i in range(52):  # deterministic: a dip into early 2026, then a partial recovery
            dip = -3.4 * (1 - abs(i - 22) / 22) if i < 44 else 0.0
            wobble = ((i * 29) % 5 - 2) * 0.15
            w.writerow([f"W{i + 1:02d}", round(19.9 + dip - 1.2 * i / 51 + wobble, 2)])
    with (d / "buyer_universe.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["buyer", "type", "tier", "capacity_usd_bn", "rationale"])
        w.writerows(BUYERS)
    write(d / "parking_memo.txt", "Level 2 of the car park is closed for resurfacing next week.")


def pitch(fx: FactLookup, src: Path) -> dict[str, Any]:
    C, MP, TC, PT, SP, BU = (
        "capitalization.xlsx",
        "management_projections.xlsx",
        "trading_comps.csv",
        "precedent_transactions.csv",
        "share_price_52w.csv",
        "buyer_universe.csv",
    )
    px, sh, nd, ltm = (fx.val(C, f"Cap!B{r}") for r in (2, 3, 4, 5))
    i_px, i_sh, i_nd, i_ltm = (fx.id(C, f"Cap!B{r}") for r in (2, 3, 4, 5))
    ntm, i_ntm = fx.val(MP, "Projections ($M)!B3"), fx.id(MP, "Projections ($M)!B3")
    fcf = [fx.val(MP, f"Projections ($M)!{c}4") for c in "BCDEF"]
    i_fcf = [fx.id(MP, f"Projections ($M)!{c}4") for c in "BCDEF"]
    wacc_ids = [f["id"] for f in fx.rows if f["file"] == MP and f["locator"] == "Notes!A2 (text)"]
    prices = [float(r["close_usd"]) for r in csv.DictReader((src / SP).open())]
    lo_px, hi_px = min(prices), max(prices)
    i_lo = next(f["id"] for f in fx.rows if f["file"] == SP and float(f["value"]) == lo_px)
    i_hi = next(f["id"] for f in fx.rows if f["file"] == SP and float(f["value"]) == hi_px)
    ev_now = px * sh + nd

    def ps(e: float) -> float:
        return (e - nd) / sh

    comps = []
    for r, name in enumerate(("Peer Arden", "Peer Bexley", "Peer Cairn", "Peer Dunmore", "Peer Esker"), start=2):
        e, l_, t = (fx.val(TC, f"row {r}, {k}") for k in ("ev_usd_m", "ebitda_ltm_usd_m", "ebitda_ntm_usd_m"))
        comps.append((name, e, l_, t))
    ltm_x = sorted(e / l_ for _, e, l_, _ in comps)
    ntm_x = sorted(e / t for _, e, _, t in comps)
    ntm_rng = (round(ntm_x[1], 1), round(ntm_x[-2], 1))  # drop the lowest and the highest multiple
    prec_x = [fx.val(PT, f"row {r}, ev_ltm_ebitda_x") for r in (2, 3, 4, 5)]
    pr_lo, pr_hi = min(prec_x), max(prec_x)

    def dcf(w: float, g: float) -> float:
        pv = sum(c / (1 + w) ** (i + 1) for i, c in enumerate(fcf))
        return ps(pv + fcf[-1] * (1 + g) / (w - g) / (1 + w) ** 5)

    flat = [dcf(w, g) for w in (0.085, 0.09, 0.095) for g in (0.02, 0.025, 0.03)]
    ranges = [
        ("52-week trading range", lo_px, hi_px),
        (
            f"Trading comps ({ntm_rng[0]:.1f}x–{ntm_rng[1]:.1f}x FY26E EBITDA)",
            ps(ntm_rng[0] * ntm),
            ps(ntm_rng[1] * ntm),
        ),
        (f"Precedent transactions ({pr_lo}x–{pr_hi}x LTM EBITDA)", ps(pr_lo * ltm), ps(pr_hi * ltm)),
        ("DCF (WACC 8.5%–9.5%, TGR 2.0%–3.0%)", min(flat), max(flat)),
    ]
    above = sum(lo > px for _, lo, _ in ranges)
    if not 0 < above < len(ranges):
        raise ValueError("the valuation title assumes some, not all, ranges sit wholly above the share price")
    steps = [21.0, 23.0, 25.0]
    cols = [px] + steps

    def at(p: float) -> tuple[float, float, float, float]:
        eq = p * sh
        return eq, eq + nd, (eq + nd) / ltm, (eq + nd) / ntm

    grid = [at(p) for p in cols]
    tiers = sorted(BUYERS, key=lambda b: (b[1] != "Strategic", b[2]))
    buyer_rows = [[f"{kind} · tier {tier}", code, f"{cap:.1f}", why] for code, kind, tier, cap, why in tiers]
    cap_ids = ", ".join(fx.id(BU, f"row {r}, capacity_usd_bn") for r in range(2, 2 + len(BUYERS)))
    return {
        "_about": "Fictional strategic-alternatives sample built by samples/build_samples.py from "
        "samples/source/halden-freight/input via scripts/ingest.py. Page order follows the sell-side skeleton in "
        "references/banking-pitchbook.md. Build: node build-pitchbook.js pitchbook-pitch.sample.json",
        "output": "halden-strategic-alternatives.pptx",
        "kind": "pitch",
        "meta": {
            "title": "Project Heron — strategic alternatives review",
            "author": "Advisor team",
            "label": "Confidential · Preliminary draft",
        },
        "sections": ["Situation", "Valuation", "Alternatives", "Process"],
        "slides": [
            {
                "type": "cover",
                "title": "Project Heron: strategic alternatives review",
                "subtitle": "Discussion materials for the Board of Halden Freight Systems",
                "footer": "Fictional sample · deck-studio",
                "notes": "Fictional company and data. Built from samples/source/halden-freight/input via "
                "scripts/ingest.py.",
            },
            {
                "type": "exec-summary",
                "title": "Key considerations",
                "points": [
                    {
                        "lead": "Is the plan worth more than a sale?",
                        "text": "Compare the stand-alone DCF with what buyers can pay today.",
                    },
                    {
                        "lead": "Who could pay the most?",
                        "text": "Two tier-1 strategics overlap Halden's hubs and could pay for the savings.",
                    },
                    {
                        "lead": "How much certainty does the Board need?",
                        "text": "A sponsor offers speed; a strategic may need antitrust review.",
                    },
                    {
                        "lead": "What would a process cost the business?",
                        "text": "A short process with a small, tiered buyer list limits disruption.",
                    },
                ],
                "notes": "Framing page: questions for the Board, no figures. Answers follow the analysis (valuation, "
                "alternatives, buyers, process) and the recommendation comes after them.",
            },
            {
                "type": "table",
                "section": "Situation",
                "title": f"Market snapshot: ${px:.2f} per share, {ev_now / ltm:.1f}x LTM EBITDA",
                "unit": "($ in millions, except per-share values)",
                "header": ["Metric", "Value", "Basis"],
                "align": ["l", "r", "l"],
                "colW": [5.2, 2.2, 4.9],
                "rows": [
                    {"cells": [f"Share price ({CURRENT_DATE})", f"${px:.2f}", "Market close"], "kind": "subject"},
                    ["52-week low / high", f"${lo_px:.2f} / ${hi_px:.2f}", "Weekly closes"],
                    ["Diluted shares", f"{sh:.1f}M", "Capitalization table"],
                    ["Equity value", f"{px * sh:,.0f}", "Price × diluted shares"],
                    ["Net debt", f"{nd:,.0f}", "Capitalization table"],
                    ["Enterprise value", f"{ev_now:,.0f}", "Equity value + net debt"],
                    [f"EV / LTM EBITDA (${ltm:.0f}M)", f"{ev_now / ltm:.1f}x", "EV / LTM EBITDA"],
                    [f"EV / FY26E EBITDA (${ntm:.0f}M)", f"{ev_now / ntm:.1f}x", "Management case"],
                ],
                "source": f"Company capitalization table; weekly closing prices to {CURRENT_DATE}; management "
                "projections (August 2026)",
                "notes": f"Price [{i_px}]; low [{i_lo}]; high [{i_hi}]; shares [{i_sh}]; net debt [{i_nd}]; LTM EBITDA "
                f"[{i_ltm}]; FY26E EBITDA [{i_ntm}]. calc: {px * sh:,.0f} = {px} x {sh} [{i_px}, {i_sh}]. calc: "
                f"{ev_now:,.0f} = {px * sh:,.0f} + {nd:.0f} [{i_nd}]. calc: {ev_now / ltm:.1f}x = {ev_now:,.0f} / "
                f"{ltm:.0f} [{i_ltm}]. calc: {ev_now / ntm:.1f}x = {ev_now:,.0f} / {ntm:.0f} [{i_ntm}].",
            },
            {
                "type": "table",
                "section": "Valuation",
                "title": "Illustrative analysis at various prices",
                "unit": "($ in millions, except per-share values)",
                "header": ["", "Current", "Illustrative", "Illustrative", "Illustrative"],
                "align": ["l", "r", "r", "r", "r"],
                "colW": [3.9, 2.1, 2.1, 2.1, 2.1],
                "rows": [
                    {"cells": ["Price per share"] + [f"${p:.2f}" for p in cols], "kind": "subject"},
                    ["Premium to current"] + ["—"] + [f"{100 * (p / px - 1):.1f}%" for p in steps],
                    ["Equity value"] + [f"{g[0]:,.0f}" for g in grid],
                    ["Enterprise value"] + [f"{g[1]:,.0f}" for g in grid],
                    ["EV / LTM EBITDA"] + [f"{g[2]:.1f}x" for g in grid],
                    ["EV / FY26E EBITDA"] + [f"{g[3]:.1f}x" for g in grid],
                ],
                "source": "Company capitalization table; management projections (August 2026)",
                "notes": f"calc: illustrative prices $21.00, $23.00, $25.00 = steps chosen for discussion [{i_px}]. "
                + " ".join(
                    f"calc: at ${p:.2f}: premium {100 * (p / px - 1):.1f}% = {p} / {px} - 1; equity "
                    f"{g[0]:,.0f} = {p} x {sh}; EV {g[1]:,.0f} = {g[0]:,.0f} + {nd:.0f}; {g[2]:.1f}x = "
                    f"{g[1]:,.0f} / {ltm:.0f}; {g[3]:.1f}x = {g[1]:,.0f} / {ntm:.0f} [{i_px}, {i_sh}, {i_nd}, "
                    f"{i_ltm}, {i_ntm}]."
                    for p, g in zip(cols, grid)
                ),
            },
            {
                "type": "football-field",
                "section": "Valuation",
                "title": f"Illustrative valuation: {above} of {len(ranges)} ranges sit above ${px:.2f}",
                "unit": "(Implied value per share, $) (1)",
                "min": 10,
                "max": 30,
                "step": 5,
                "ranges": [{"label": lab, "low": round(lo, 2), "high": round(hi, 2)} for lab, lo, hi in ranges],
                "lines": [{"value": px, "label": f"Current ${px:.2f}"}],
                "source": f"Management projections (August 2026); peer company filings; precedent transaction "
                f"announcements; weekly closing prices to {CURRENT_DATE}",
                "footnotes": [
                    f"Per-share values use {sh:.1f}M diluted shares and ${nd:.0f}M net debt. Comps drop the "
                    "lowest and highest multiple. DCF discounts FY26E–FY30E unlevered FCF, end-year "
                    "convention."
                ],
                "notes": f"52-week range ${lo_px:.2f} [{i_lo}] to ${hi_px:.2f} [{i_hi}]. "
                + " ".join(
                    f"calc: {lab}: ${lo:.2f} to ${hi:.2f} per share = (multiple x EBITDA - {nd:.0f}) / {sh} "
                    f"[{i_ntm}, {i_ltm}, {i_nd}, {i_sh}, {fx.span(TC)}, {fx.span(PT)}]."
                    for lab, lo, hi in ranges[1:3]
                )
                + f" calc: DCF ${min(flat):.2f} to ${max(flat):.2f} = 3 x 3 grid of WACC and TGR [{', '.join(i_fcf)}, "
                f"{', '.join(wacc_ids)}]. calc: {above} of {len(ranges)} ranges start above ${px:.2f} [{i_px}]. "
                f"calc: comps range {ntm_rng[0]:.1f}x–{ntm_rng[1]:.1f}x = second-lowest and second-highest of "
                f"{', '.join(f'{x:.1f}x' for x in ntm_x)} [{fx.span(TC)}].",
            },
            {
                "type": "table",
                "section": "Valuation",
                "title": f"Trading comps: peers trade at a {statistics.median(ntm_x):.1f}x FY26E median",
                "unit": "($ in millions)",
                "header": ["Company", "Enterprise value", "EV / LTM EBITDA", "EV / NTM EBITDA"],
                "colW": [4.8, 2.5, 2.5, 2.5],
                "rows": [[n, f"{e:,.0f}", f"{e / l_:.1f}x", f"{e / t:.1f}x"] for n, e, l_, t in comps]
                + [
                    {
                        "cells": [
                            "Median",
                            f"{statistics.median(c[1] for c in comps):,.0f}",
                            f"{statistics.median(ltm_x):.1f}x",
                            f"{statistics.median(ntm_x):.1f}x",
                        ],
                        "kind": "summary",
                    },
                    {
                        "cells": [
                            "Halden at current",
                            f"{ev_now:,.0f}",
                            f"{ev_now / ltm:.1f}x",
                            f"{ev_now / ntm:.1f}x",
                        ],
                        "kind": "subject",
                    },
                ],
                "source": f"Peer company filings; company capitalization table as of {CURRENT_DATE}",
                "notes": " ".join(
                    f"calc: {n} {e / l_:.1f}x = {e:,.0f} / {l_:.0f} and {e / t:.1f}x = {e:,.0f} / {t:.0f} "
                    f"[{fx.span(TC)}]."
                    for n, e, l_, t in comps
                )
                + f" calc: medians = middle of five values [{fx.span(TC)}]. calc: Halden {ev_now:,.0f}, "
                f"{ev_now / ltm:.1f}x, {ev_now / ntm:.1f}x [{i_px}, {i_sh}, {i_nd}, {i_ltm}, {i_ntm}].",
            },
            {
                "type": "options",
                "section": "Alternatives",
                "title": "Alternatives: four paths compared on the Board's criteria",
                "criteria": ["Value to shareholders", "Certainty of value", "Speed to close", "Low disruption"],
                "options": [
                    {"name": "Stand-alone plan", "scores": [2, 1, 4, 4]},
                    {"name": "Leveraged recapitalisation", "scores": [2, 2, 3, 3]},
                    {"name": "Sale to a strategic", "scores": [4, 3, 1, 2]},
                    {"name": "Sale to a sponsor", "scores": [3, 3, 3, 3]},
                ],
                "notes": "Qualitative advisor scoring for discussion; no figures on this page. No option is marked "
                "recommended here: the recommendation follows the buyer and process pages.",
            },
            {
                "type": "table",
                "section": "Alternatives",
                "title": "Buyer universe: three strategics and two sponsors, tiered",
                "unit": "(Capacity: market capitalisation or fund size, $ in billions)",
                "header": ["Tier", "Buyer", "Capacity", "Rationale"],
                "align": ["l", "l", "r", "l"],
                "colW": [2.6, 2.2, 1.6, 5.9],
                "rows": buyer_rows,
                "source": "Advisor buyer screen; public filings and fund announcements",
                "notes": f"Capacities [{cap_ids}]. Buyer names are code names.",
            },
            {
                "type": "roadmap",
                "section": "Process",
                "title": "Illustrative process: launch in September, signing in December",
                "periods": ["Sep 2026", "Oct 2026", "Nov 2026", "Dec 2026"],
                "rows": [
                    {"name": "Preparation and buyer outreach", "start": 0, "end": 0.6},
                    {
                        "name": "First round: indications",
                        "start": 0.6,
                        "end": 1.6,
                        "milestones": [{"at": 1.6, "label": "Board: shortlist"}],
                    },
                    {"name": "Second round: diligence and bids", "start": 1.6, "end": 3.0, "accent": True},
                    {
                        "name": "Negotiation and signing",
                        "start": 3.0,
                        "end": 3.5,
                        "milestones": [{"at": 3.5, "label": "Board: approve"}],
                    },
                ],
                "notes": "Plan dates for discussion, not facts.",
            },
            {
                "type": "text",
                "section": "Process",
                "title": "Recommendation and next steps",
                "points": [
                    {
                        "lead": "Recommendation.",
                        "text": "Run a targeted sale process to the two tier-1 strategics and Sponsor D, keeping the "
                        "stand-alone plan as the walk-away.",
                    },
                    {
                        "lead": "Why.",
                        "text": "Most valuation ranges sit above today's price, the tier-1 strategics can "
                        "pay for hub savings, and a tiered list limits disruption.",
                    },
                    {
                        "lead": "Next steps.",
                        "text": "Board approval of the process; advisers prepare the teaser and "
                        "management presentation; outreach starts in September.",
                    },
                ],
                "notes": "Recommendation in the advisor's voice, after the analysis (research/pitchbook-findings.md "
                "rule 4). It restates earlier pages and adds no new figures.",
            },
            {
                "type": "disclaimer",
                "title": "Disclaimer",
                "text": "These materials were prepared for the Board's use in reviewing strategic alternatives. "
                "They rely on public information and on projections prepared by management, which we have not verified "
                "independently. They are preliminary and illustrative, are not a valuation opinion, and are not a "
                "recommendation to any shareholder. The company and figures are fictional.",
                "notes": "Disclaimer written for this sample and placed at the back, as in 5 of 8 coded pitch books.",
            },
        ],
    }
