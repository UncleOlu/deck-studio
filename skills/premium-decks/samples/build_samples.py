#!/usr/bin/env python3
"""Build the three ingest-path samples end to end, from fictional inputs that no eval case shares.

  1. Write fictional source folders: samples/source/alder-vale-hotels/input/ (consulting)
     and samples/source/corvane-instruments/input/ (banking board book), and
     samples/source/halden-freight/input/ (banking strategic-alternatives pitch).
  2. Run scripts/ingest.py on each → samples/source/<name>/brief/.
  3. Compute every slide figure FROM THE FACT BASE (facts looked up by file and
     cell), and write templates/consulting-deck.sample.json and
     templates/pitchbook.sample.json with fact ids and calc: lines in the notes.

Then build and QA with the builders (see SKILL.md). Every company, person, and
figure here is invented. Usage: python3 build_samples.py
"""

from __future__ import annotations

import csv
import json
import statistics
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from openpyxl import Workbook

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pitch_sample  # noqa: E402

HERE = Path(__file__).resolve().parent
SKILL = HERE.parent
SRC = HERE / "source"
FIXED = datetime(2026, 9, 1)


def save(wb: Workbook, path: Path) -> None:
    wb.properties.created = wb.properties.modified = FIXED
    wb.save(path)


def write(path: Path, text: str) -> None:
    path.write_text(text.strip() + "\n")


# ------------------------------------------------------------------ inputs
HOTELS = [  # name, segment, rooms, rooms revenue $k, housekeeping $k, energy $k, room-nights sold
    ("AV Harbourside", "City", 240, 31200, 3870, 2310, 70100),
    ("AV Old Town", "City", 180, 23900, 3060, 1790, 52600),
    ("AV Riverside", "City", 210, 26800, 3160, 2020, 60900),
    ("AV Station", "City", 160, 19100, 2640, 1610, 46400),
    ("AV Cathedral", "City", 150, 18400, 2120, 1350, 42700),
    ("AV Airport", "Airport", 300, 27600, 4300, 2980, 88800),
    ("AV Airport South", "Airport", 260, 22100, 3620, 2710, 76100),
    ("AV Lakeside", "Resort", 120, 21400, 3230, 1920, 27900),
    ("AV Dunes", "Resort", 140, 24800, 3810, 2350, 31600),
    ("AV Pinewood", "Resort", 110, 17300, 2580, 1760, 24400),
]


def alder_vale_inputs(d: Path) -> None:
    d.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    s = wb.active
    s.title = "Summary"
    tot = [sum(h[3] for h in HOTELS), sum(h[4] for h in HOTELS), sum(h[5] for h in HOTELS), sum(h[6] for h in HOTELS)]
    s.append(["Alder & Vale Hotels — FY25 summary", "$M"])
    s.append(["Hotels", len(HOTELS)])
    s.append(["Rooms revenue", round(tot[0] / 1000, 1)])
    s.append(["Housekeeping cost", round(tot[1] / 1000, 1)])
    s.append(["Energy cost", round(tot[2] / 1000, 1)])
    s.append(["Other operating cost", 142.6])
    s.append(["Hotel EBITDA", "=B3-B4-B5-B6"])
    s.append(["EBITDA margin", "=B7/B3"])
    h = wb.create_sheet("Hotels ($k)")
    h.append(["hotel", "segment", "rooms", "rooms_revenue_k", "housekeeping_k", "energy_k", "room_nights"])
    for row in HOTELS:
        h.append(list(row))
    save(wb, d / "hotel_pnl_FY25.xlsx")
    with (d / "peer_benchmarks.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["peer", "housekeeping_pct_rooms_revenue", "energy_usd_per_room_night"])
        w.writerows(
            [
                ["Peer North (public filings)", 12.4, 31.5],
                ["Peer Crest (public filings)", 12.9, 34.9],
                ["Peer Bay (industry survey)", 13.4, 36.8],
                ["Median", 12.9, 34.9],
            ]
        )
    write(
        d / "gm_interviews.md",
        """
# General manager interviews — July 2026 (internal)

**GM, AV Airport.** Rooms are cleaned to a full-service standard every day, even for one-night
stays. Guests on short stays tell us they would accept a light refresh.

**GM, AV Dunes.** HVAC in guest rooms runs whether or not the room is sold. We estimate unsold
rooms account for about 30% of guest-room energy in the low season.

**Director of Engineering.** Only 3 of 10 hotels (Harbourside, Old Town, Lakeside) have
occupancy-linked thermostats. Retrofits cost about $1,100 per room and pay back in under two
years at current tariffs.
""",
    )
    write(
        d / "coo_email.txt",
        """
From: COO
Subject: Board question on hotel margins

The board wants to know whether housekeeping and energy can lift hotel EBITDA margin by 2 points
without cutting service. Rooms revenue was about $240M last year. Please size it and tell me
where to start.
""",
    )
    write(d / "holiday_rota.txt", "August holiday rota: finance team cover list attached. Submit swaps by Friday.")


def corvane_inputs(d: Path) -> None:
    d.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    c = wb.active
    c.title = "Cap"
    c.append(["Corvane Instruments (fictional) — capitalization", "value", "unit"])
    c.append(["Share price (unaffected, 15 May 2026)", 21.40, "$"])
    c.append(["Offer price (sponsor proposal)", 27.00, "$"])
    c.append(["Diluted shares outstanding", 114.0, "M"])
    c.append(["Net debt", 845, "$M"])
    c.append(["LTM EBITDA", 310, "$M"])
    save(wb, d / "capitalization.xlsx")
    wb = Workbook()
    p = wb.active
    p.title = "Projections ($M)"
    p.append(["", "FY26E", "FY27E", "FY28E", "FY29E", "FY30E"])
    p.append(["Revenue", 2240, 2360, 2490, 2610, 2720])
    p.append(["EBITDA", 332, 356, 381, 404, 425])
    p.append(["Unlevered FCF", 176, 192, 209, 224, 238])
    n = wb.create_sheet("Notes")
    n.append(["Management case prepared for the Special Committee, June 2026."])
    n.append(["WACC range used by management: 8.0%-9.0%; terminal growth 2.0%-3.0%."])
    n.append(["Per-share values should use 112.6M diluted shares (treasury method at the offer)."])
    save(wb, d / "management_projections.xlsx")
    with (d / "trading_comps.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["company", "ev_usd_m", "ebitda_ltm_usd_m", "ebitda_ntm_usd_m"])
        w.writerows(
            [
                ["Peer Aster", 6150, 612, 645],
                ["Peer Brio", 3420, 371, 392],
                ["Peer Calder", 8800, 812, 861],
                ["Peer Delta", 2480, 283, 297],
                ["Peer Ember", 4010, 402, 428],
            ]
        )
    with (d / "precedent_transactions.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["date", "target", "acquirer", "ev_usd_m", "ev_ltm_ebitda_x"])
        w.writerows(
            [
                ["2023-03", "Target Alpha", "Sponsor E", 2900, 9.8],
                ["2024-06", "Target Beta", "Strategic F", 5100, 11.9],
                ["2025-01", "Target Gamma", "Sponsor G", 1800, 9.1],
                ["2025-11", "Target Omega", "Strategic H", 6400, 12.2],
            ]
        )
    with (d / "share_price_52w.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["week", "close_usd"])
        for i in range(52):  # deterministic path: a slow climb with a wobble, high 21.9 in late 2025
            wobble = ((i * 37) % 7 - 3) * 0.18
            price = round(17.2 + 4.3 * i / 51 + wobble, 2)
            w.writerow([f"2025-W{i + 1:02d}", price])
    write(d / "canteen_menu.txt", "Canteen this week: soup, salad bar, vegetarian curry on Thursday.")


# ------------------------------------------------------------------ fact lookup
class Facts:
    def __init__(self, brief: Path) -> None:
        self.rows: list[dict[str, Any]] = [
            json.loads(line) for line in (brief / "facts.jsonl").read_text().splitlines() if line.strip()
        ]

    def at(self, file: str, locator: str) -> dict[str, Any]:
        for f in self.rows:
            if f["file"] == file and f["locator"] == locator:
                return f
        raise KeyError(f"no fact at {file} {locator}")

    def id(self, file: str, locator: str) -> str:
        fact_id: str = self.at(file, locator)["id"]
        return fact_id

    def val(self, file: str, locator: str) -> float:
        return float(self.at(file, locator)["value"])

    def find(self, file: str, value: float) -> str:
        """Id of the first fact in a file with this value (for figures quoted in prose)."""
        for f in self.rows:
            if f["file"] == file and not isinstance(f["value"], str) and abs(float(f["value"]) - value) < 1e-9:
                fact_id: str = f["id"]
                return fact_id
        raise KeyError(f"no fact {value} in {file}")

    def span(self, file: str) -> str:
        ids = [f["id"] for f in self.rows if f["file"] == file]
        return f"{ids[0]}-{ids[-1]}"


def ingest(folder: Path) -> Facts:
    out = folder.parent / "brief"  # beside the input: ingest refuses to write inside it
    subprocess.run([sys.executable, str(SKILL / "scripts" / "ingest.py"), str(folder), "--out", str(out)], check=True)
    return Facts(out)


def m(v: float) -> str:
    return f"${v:,.1f}M" if v < 100 else f"${v:,.0f}M"


# ------------------------------------------------------------------ consulting sample
def consulting(fx: Facts) -> dict[str, Any]:
    X, P = "hotel_pnl_FY25.xlsx", "peer_benchmarks.csv"
    rev, hk, en, oth = (fx.val(X, f"Summary!B{r}") for r in (3, 4, 5, 6))
    ebitda = rev - hk - en - oth
    i_rev, i_hk, i_en, i_eb, i_n = (fx.id(X, f"Summary!B{r}") for r in (3, 4, 5, 7, 2))
    hk_med, en_med = fx.val(P, "row 5, housekeeping_pct_rooms_revenue"), fx.val(P, "row 5, energy_usd_per_room_night")
    i_hkm, i_enm = fx.id(P, "row 5, housekeeping_pct_rooms_revenue"), fx.id(P, "row 5, energy_usd_per_room_night")
    nights = sum(h[6] for h in HOTELS)
    hk_pct = 100 * hk / rev
    en_night = en * 1e6 / nights
    hk_gap = hk - hk_med / 100 * rev
    en_gap = (en_night - en_med) * nights / 1e6
    total = hk_gap + en_gap
    margin0, margin1 = round(100 * ebitda / rev, 1), round(100 * (ebitda + total) / rev, 1)  # as displayed
    seg: dict[str, list[int]] = {}
    for h in HOTELS:
        s = seg.setdefault(h[1], [0, 0, 0, 0])
        s[0] += h[3]
        s[1] += h[4]
        s[2] += h[5]
        s[3] += h[6]
    seg_hk = {k: 100 * v[1] / v[0] for k, v in seg.items()}
    hot_hk = max(seg_hk, key=seg_hk.__getitem__)
    order_hk = sorted(seg_hk, key=seg_hk.__getitem__)
    seg_en = {k: v[2] * 1000 / v[3] for k, v in seg.items()}
    order_en = sorted(seg_en, key=seg_en.__getitem__)
    rows_span = fx.span(X)
    top_hk = max(((h[0], 100 * h[4] / h[3]) for h in HOTELS), key=lambda t: t[1])
    top_en = max(((h[0], h[5] * 1000 / h[6]) for h in HOTELS), key=lambda t: t[1])
    conflict_email = next(f for f in fx.rows if f["file"] == "coo_email.txt" and f["unit"] == "USD")
    i_10 = fx.find("gm_interviews.md", 10)
    controlled = {"AV Harbourside", "AV Old Town", "AV Lakeside"}
    retro_rooms = sum(h[2] for h in HOTELS if h[0] not in controlled)
    budget = retro_rooms * 1100 / 1e6
    i_1100 = fx.find("gm_interviews.md", 1100)
    peers = [
        (fx.val(P, f"row {r}, housekeeping_pct_rooms_revenue"), fx.id(P, f"row {r}, housekeeping_pct_rooms_revenue"), n)
        for r, n in ((2, "Peer North"), (3, "Peer Crest"), (4, "Peer Bay"))
    ]
    calc_hk = (
        f"calc: housekeeping {hk_pct:.1f}% = {hk:.1f} / {rev:.1f} [{i_hk}, {i_rev}]. calc: gap "
        f"{m(hk_gap)} = {hk:.1f} - {hk_med}% x {rev:.1f} [{i_hkm}]."
    )
    calc_en = (
        f"calc: energy ${en_night:.1f} per room-night = {en:.1f}M / {nights:,} room-nights (sum of hotel rows) "
        f"[{i_en}, {rows_span}]. calc: gap {m(en_gap)} = ({en_night:.1f} - {en_med}) x {nights:,} [{i_enm}]."
    )
    return {
        "_about": "Fictional sample built by samples/build_samples.py from samples/source/alder-vale-hotels/input via "
        "scripts/ingest.py. Every number cites a fact id or a calc: line. Build: node build-consulting.js "
        "consulting-deck.sample.json",
        "output": "alder-vale-margin-diagnostic.pptx",
        "meta": {
            "title": "Alder & Vale Hotels — housekeeping and energy diagnostic",
            "author": "Strategy team",
            "label": "Draft for discussion",
        },
        "sections": ["Diagnosis", "Levers", "Plan", "Appendix"],
        "slides": [
            {
                "type": "cover",
                "title": (
                    "Housekeeping and energy can fund most of the board's margin target"
                    if margin1 - margin0 < 2
                    else "Housekeeping and energy can fund the board's margin target"
                ),
                "subtitle": "Alder & Vale Hotels · diagnostic for the COO",
                "footer": "Fictional sample · deck-studio",
                "notes": f"Fictional company and data. Built from samples/source/alder-vale-hotels/input via scripts/ingest.py. "
                f"Data decision: the COO email gives rooms revenue as about $240M [{conflict_email['id']}]; the "
                f"FY25 summary gives {m(rev)} [{i_rev}]. The deck uses the summary, the system figure.",
            },
            {
                "type": "exec-summary",
                "section": "Diagnosis",
                "title": f"Matching the peer median on housekeeping and energy adds {margin1 - margin0:.1f} pts of EBITDA margin",
                "answer": f"The two gaps are worth {m(total)} a year and lift EBITDA margin from {margin0:.1f}% to "
                f"{margin1:.1f}%, without cutting the service standard guests notice.",
                "points": [
                    {
                        "lead": f"Housekeeping costs {hk_pct:.1f}% of rooms revenue, above the {hk_med}% peer median: "
                        f"{m(hk_gap)} a year.",
                        "dashes": [
                            f"{hot_hk} hotels run highest at {seg_hk[hot_hk]:.1f}%.",
                            "Every room gets a full clean daily, even on one-night stays.",
                        ],
                    },
                    {
                        "lead": f"Energy costs ${en_night:.1f} per room-night sold, above the ${en_med} median: "
                        f"{m(en_gap)} a year.",
                        "dashes": [
                            "Guest-room HVAC runs whether or not the room is sold.",
                            "Only 3 of 10 hotels have occupancy-linked thermostats.",
                        ],
                    },
                    {
                        "lead": (
                            f"Together the gaps close {margin1 - margin0:.1f} of the 2 points the board asked for."
                            if margin1 - margin0 < 2
                            else f"Together the gaps add {margin1 - margin0:.1f} points, more than the 2 the board asked for."
                        ),
                        "dashes": [
                            "The rest of the ask needs levers outside this review."
                            if margin1 - margin0 < 2
                            else "The surplus gives room to protect service scores."
                        ],
                    },
                    {
                        "lead": "Start with a light-refresh standard for short stays and thermostat retrofits.",
                        "dashes": ["Each acts on the largest driver of its gap."],
                    },
                ],
                "notes": f"Rooms revenue {m(rev)} [{i_rev}]; housekeeping {m(hk)} [{i_hk}]; energy {m(en)} [{i_en}]; "
                f"EBITDA {m(ebitda)} [{i_eb}]; peer medians [{i_hkm}, {i_enm}]. {calc_hk} {calc_en} calc: "
                f"{m(total)} = {hk_gap:.1f} + {en_gap:.1f}. calc: {margin0:.1f}% = {ebitda:.1f} / {rev:.1f}; "
                f"{margin1:.1f}% = ({ebitda:.1f} + {total:.1f}) / {rev:.1f}; {margin1 - margin0:.1f} pts = "
                f"{margin1:.1f} - {margin0:.1f} [{i_rev}]. calc: {hot_hk} {seg_hk[hot_hk]:.1f}% from the "
                f"hotel rows [{rows_span}]. Board ask 2 points [{fx.find('coo_email.txt', 2)}]. Thermostats "
                f"3 of 10 [{fx.find('gm_interviews.md', 3)}, {i_10}, {i_n}].",
            },
            {
                "type": "chart",
                "section": "Diagnosis",
                "title": f"Housekeeping costs {hk_pct:.1f}% of rooms revenue, highest in {hot_hk} hotels at "
                f"{seg_hk[hot_hk]:.1f}%",
                "kind": "column",
                "labels": order_hk + ["All hotels", "Peer median"],
                "series": [
                    {
                        "name": "Housekeeping, % of rooms revenue",
                        "values": [round(seg_hk[k], 1) for k in order_hk] + [round(hk_pct, 1), hk_med],
                    }
                ],
                "highlight": len(order_hk) - 1,
                "format": '0.0"%"',
                "unit": "Housekeeping cost, % of rooms revenue, FY25, by segment",
                "source": "Alder & Vale FY25 hotel P&L (hotel rows); peer benchmarks (public filings, industry survey)",
                "side": {
                    "points": [
                        {
                            "lead": "Short stays drive it.",
                            "text": "Airport guests stay one night, and every room still gets a full daily clean.",
                        },
                        {
                            "lead": "Guests would accept less.",
                            "text": "Short-stay guests say a light refresh is enough (GM interviews).",
                        },
                    ]
                },
                "notes": f"calc: segment % = sum(housekeeping_k) / sum(rooms_revenue_k) per segment: City "
                f"{seg_hk['City']:.1f}%, Resort {seg_hk['Resort']:.1f}%, Airport {seg_hk['Airport']:.1f}% "
                f"[{rows_span}]. Total {hk_pct:.1f}% [{i_hk}, {i_rev}]; median {hk_med}% [{i_hkm}].",
            },
            {
                "type": "chart",
                "section": "Diagnosis",
                "title": f"Energy costs ${en_night:.1f} per room-night sold, ${en_night - en_med:.1f} above the peer median",
                "kind": "column",
                "labels": order_en + ["All hotels", "Peer median"],
                "series": [
                    {
                        "name": "Energy, $ per room-night",
                        "values": [round(seg_en[k], 1) for k in order_en] + [round(en_night, 1), en_med],
                    }
                ],
                "highlight": len(order_en) - 1,
                "format": '"$"0.0',
                "unit": "Energy cost, $ per room-night sold, FY25, by segment",
                "source": "Alder & Vale FY25 hotel P&L (hotel rows); peer benchmarks; GM interview (AV Dunes), July 2026",
                "side": {
                    "points": [
                        {
                            "lead": "Empty rooms still use energy.",
                            "text": "Unsold rooms take about 30% of guest-room energy in the low season "
                            "(AV Dunes GM estimate).",
                        },
                        {
                            "lead": f"{order_en[-1]} hotels pay most.",
                            "text": f"{order_en[-1]} hotels spend ${seg_en[order_en[-1]]:.1f} a room-night, against ${en_med} "
                            "for the peer median.",
                        },
                    ]
                },
                "notes": f"calc: segment $/room-night = sum(energy_k) x 1000 / sum(room_nights): City "
                f"{seg_en['City']:.1f}, Airport {seg_en['Airport']:.1f}, Resort {seg_en['Resort']:.1f} "
                f"[{rows_span}]. {calc_en} calc: {en_night - en_med:.1f} = {en_night:.1f} - {en_med} [{i_enm}]. "
                f"30% [{fx.find('gm_interviews.md', 30)}].",
            },
            {
                "type": "waterfall",
                "section": "Diagnosis",
                "title": f"Closing both gaps lifts hotel EBITDA from {m(ebitda)} to {m(ebitda + total)}",
                "steps": [
                    {"label": "FY25 EBITDA", "value": round(ebitda, 1), "total": True, "display": m(ebitda)},
                    {"label": "Housekeeping to median", "value": round(hk_gap, 1), "display": f"+{m(hk_gap)}"},
                    {"label": "Energy to median", "value": round(en_gap, 1), "display": f"+{m(en_gap)}"},
                    {
                        "label": "EBITDA at median",
                        "value": round(ebitda + total, 1),
                        "total": True,
                        "display": m(ebitda + total),
                    },
                ],
                "accentStep": 1 if hk_gap >= en_gap else 2,
                "unit": "Hotel EBITDA, $ millions, FY25 base",
                "source": "Alder & Vale FY25 hotel P&L; peer benchmarks",
                "side": {
                    "points": [
                        {
                            "lead": f"The margin moves from {margin0:.1f}% to {margin1:.1f}%.",
                            "text": (
                                "That is most of the board's 2-point ask."
                                if margin1 - margin0 < 2
                                else "That exceeds the board's 2-point ask."
                            ),
                        }
                    ]
                },
                "notes": f"EBITDA {m(ebitda)} [{i_eb}]. {calc_hk} {calc_en} calc: {m(ebitda + total)} = {ebitda:.1f} + "
                f"{hk_gap:.1f} + {en_gap:.1f}; {margin0:.1f}% and {margin1:.1f}% on {rev:.1f} [{i_rev}]. "
                f"calc: 2-point ask [{fx.find('coo_email.txt', 2)}].",
            },
            {
                "type": "text",
                "section": "Levers",
                "title": "Three levers act on how rooms are cleaned, cooled, and scheduled; two come first",
                "points": [
                    {
                        "lead": "Light refresh for short stays.",
                        "text": "Clean one-night rooms to a refresh standard "
                        "(bed, bathroom, bins) and keep the full clean for stays of two nights or more.",
                    },
                    {
                        "lead": "Occupancy-linked thermostats.",
                        "text": "Set unsold rooms to a set-back temperature. Only 3 "
                        "of 10 hotels have the controls; a retrofit costs about $1,100 per room.",
                    },
                    {
                        "lead": "Housekeeping scheduling.",
                        "text": "Plan housekeeping hours from forecast departures, not from a fixed daily roster.",
                    },
                ],
                "takeaway": "The first two levers leave what guests notice unchanged.",
                "source": "General manager and engineering interviews, July 2026",
                "notes": f"Interview facts: short-stay standard [{fx.find('gm_interviews.md', 3)}]; thermostats 3 of "
                f"10 and $1,100 per room [{fx.find('gm_interviews.md', 3)}, "
                f"{fx.find('gm_interviews.md', 1100)}].",
            },
            {
                "type": "options",
                "section": "Levers",
                "title": "The light-refresh standard and thermostat retrofits score highest; start with both",
                "criteria": [
                    "Size of the gap it closes",
                    "Speed to impact",
                    "Guest experience protected",
                    "Evidence in the data",
                ],
                "options": [
                    {"name": "Light refresh for short stays", "scores": [4, 4, 3, 3], "recommended": True},
                    {"name": "Occupancy-linked thermostats", "scores": [3, 2, 4, 3], "recommended": True},
                    {"name": "Housekeeping scheduling", "scores": [2, 3, 4, 2]},
                    {"name": "Supplier re-tender", "scores": [1, 2, 4, 1]},
                ],
                "notes": "Qualitative team scoring from the interviews and the P&L; there are no numbers on this slide.",
            },
            {
                "type": "roadmap",
                "section": "Plan",
                "title": "Both first levers go live within a year",
                "periods": ["Q4 2026", "Q1 2027", "Q2 2027", "Q3 2027", "Q4 2027", "Q1 2028"],
                "rows": [
                    {
                        "name": "Light refresh (Airport first)",
                        "start": 0,
                        "end": 2,
                        "accent": True,
                        "milestones": [{"at": 1, "label": "Guest survey read-out"}],
                    },
                    {
                        "name": "Thermostat retrofits",
                        "start": 0,
                        "end": 4,
                        "accent": True,
                        "milestones": [{"at": 1.5, "label": "Resorts complete"}],
                    },
                    {"name": "Housekeeping scheduling", "start": 2, "end": 6},
                ],
                "notes": "Phasing is the team's proposal for approval; the dates are plan dates, not facts.",
            },
            {
                "type": "table",
                "section": "Plan",
                "title": f"The COO can approve the Airport pilot and a ${budget:.1f}M retrofit budget this quarter",
                "header": ["Decision or action", "Owner", "When"],
                "align": ["l", "l", "l"],
                "colW": [7.3, 2.6, 2.4],
                "rows": [
                    {
                        "cells": ["Approve the light-refresh pilot at both Airport hotels", "COO", "This quarter"],
                        "kind": "subject",
                    },
                    [
                        f"Approve thermostat retrofits: 7 hotels, {retro_rooms:,} rooms, ${budget:.1f}M",
                        "COO",
                        "This quarter",
                    ],
                    ["Confirm FY25 rooms revenue: summary vs the figure in the email", "Finance", "Before the board"],
                    ["Set the guest-satisfaction guardrail for the pilot", "Operations", "Before launch"],
                ],
                "source": "Alder & Vale FY25 hotel P&L; COO email; interviews",
                "notes": f"calc: 7 hotels = 10 hotels less the 3 with controls [{i_n}, "
                f"{fx.find('gm_interviews.md', 3)}]. calc: {retro_rooms:,} rooms = rooms in the 7 hotels "
                f"without controls [{rows_span}]. calc: ${budget:.1f}M = {retro_rooms:,} x $1,100 [{i_1100}]. "
                f"Revenue figures [{i_rev}, {conflict_email['id']}].",
            },
            {"type": "divider", "section": "Appendix", "title": "Appendix"},
            {
                "type": "table",
                "section": "Appendix",
                "title": f"Appendix: {top_hk[0]} has the highest housekeeping share ({top_hk[1]:.1f}%) and "
                f"{top_en[0]} the highest energy cost per room-night (${top_en[1]:.1f})",
                "header": [
                    "Hotel",
                    "Segment",
                    "Rooms",
                    "Housekeeping, % of rooms revenue",
                    "Energy, $ per room-night sold",
                ],
                "align": ["l", "l", "r", "r", "r"],
                "colW": [3.0, 1.9, 1.4, 3.0, 3.0],
                "rows": [
                    [h[0], h[1], f"{h[2]:,}", f"{100 * h[4] / h[3]:.1f}%", f"${h[5] * 1000 / h[6]:.1f}"] for h in HOTELS
                ]
                + [
                    {
                        "cells": [
                            "All hotels",
                            "",
                            f"{sum(h[2] for h in HOTELS):,}",
                            f"{hk_pct:.1f}%",
                            f"${en_night:.1f}",
                        ],
                        "kind": "summary",
                    }
                ],
                "source": "Alder & Vale FY25 hotel P&L (hotel rows)",
                "notes": "Hotel rows ["
                + rows_span
                + "]. "
                + " ".join(
                    f"calc: {h[0]} {100 * h[4] / h[3]:.1f}% = {h[4]:,} / {h[3]:,} and "
                    f"${h[5] * 1000 / h[6]:.1f} = {h[5]:,}k / {h[6]:,} room-nights [{rows_span}]."
                    for h in HOTELS
                )
                + f" calc: {sum(h[2] for h in HOTELS):,} rooms = sum of hotel rows [{rows_span}]. {calc_hk} {calc_en}",
            },
            {
                "type": "chart",
                "section": "Appendix",
                "title": (
                    f"Appendix: housekeeping at {hk_pct:.1f}% sits above all three peers "
                    f"({min(p[0] for p in peers)}%–{max(p[0] for p in peers)}%)"
                    if hk_pct > max(p[0] for p in peers)
                    else f"Appendix: housekeeping at {hk_pct:.1f}% sits inside the peer range "
                    f"({min(p[0] for p in peers)}%–{max(p[0] for p in peers)}%)"
                ),
                "kind": "bar",
                "labels": [p[2] for p in sorted(peers)] + ["Alder & Vale"],
                "series": [
                    {
                        "name": "Housekeeping, % of rooms revenue",
                        "values": [p[0] for p in sorted(peers)] + [round(hk_pct, 1)],
                    }
                ],
                "highlight": 3,
                "format": '0.0"%"',
                "unit": "Housekeeping cost, % of rooms revenue, FY25",
                "source": "Peer benchmarks (public filings, industry survey); Alder & Vale FY25 hotel P&L",
                "notes": "Peers "
                + ", ".join(f"{n} {v}% [{i}]" for v, i, n in peers)
                + f". Alder & Vale {hk_pct:.1f}% [{i_hk}, {i_rev}].",
            },
        ],
    }


# ------------------------------------------------------------------ banking sample
def banking(fx: Facts) -> dict[str, Any]:
    C, MP, TC, PT, SP = (
        "capitalization.xlsx",
        "management_projections.xlsx",
        "trading_comps.csv",
        "precedent_transactions.csv",
        "share_price_52w.csv",
    )
    unaff, offer, sh_cap, nd, ltm = (fx.val(C, f"Cap!B{r}") for r in (2, 3, 4, 5, 6))
    i_un, i_of, i_shc, i_nd, i_ltm = (fx.id(C, f"Cap!B{r}") for r in (2, 3, 4, 5, 6))
    sh_note = next(f for f in fx.rows if f["file"] == MP and f["locator"] == "Notes!A3 (text)")
    sh = float(sh_note["value"])
    ntm = fx.val(MP, "Projections ($M)!B3")
    i_ntm = fx.id(MP, "Projections ($M)!B3")
    fcf = [fx.val(MP, f"Projections ($M)!{c}4") for c in "BCDEF"]
    i_fcf = [fx.id(MP, f"Projections ($M)!{c}4") for c in "BCDEF"]
    wacc_ids = [f["id"] for f in fx.rows if f["file"] == MP and f["locator"] == "Notes!A2 (text)"]
    prices = [float(r["close_usd"]) for r in csv.DictReader((SRC / "corvane-instruments" / "input" / SP).open())]
    px_ids = [f for f in fx.rows if f["file"] == SP]
    lo_px, hi_px = min(prices), max(prices)
    avg_px = sum(prices) / len(prices)
    if max(unaff, hi_px, avg_px, lo_px) != hi_px:
        raise ValueError("the premiums title assumes the 2025 high is the highest reference price")
    i_lo = next(f["id"] for f in px_ids if float(f["value"]) == lo_px)
    i_hi = next(f["id"] for f in px_ids if float(f["value"]) == hi_px)
    eq = offer * sh
    ev = eq + nd

    def ps(e: float) -> float:
        return (e - nd) / sh

    comps = []
    for r, name in ((2, "Peer Aster"), (3, "Peer Brio"), (4, "Peer Calder"), (5, "Peer Delta"), (6, "Peer Ember")):
        e, l_, t = (fx.val(TC, f"row {r}, {k}") for k in ("ev_usd_m", "ebitda_ltm_usd_m", "ebitda_ntm_usd_m"))
        ids = [fx.id(TC, f"row {r}, {k}") for k in ("ev_usd_m", "ebitda_ltm_usd_m", "ebitda_ntm_usd_m")]
        comps.append((name, e, l_, t, ids))
    ltm_x = sorted(e / l_ for _, e, l_, _, _ in comps)
    ntm_x = sorted(e / t for _, e, _, t, _ in comps)
    ltm_rng = (ltm_x[1], ltm_x[-2])  # symmetric: drop the lowest and the highest multiple
    ntm_rng = (ntm_x[1], ntm_x[-2])
    prec = []
    for r in (2, 3, 4, 5):
        prec.append(
            (
                fx.val(PT, f"row {r}, ev_usd_m"),
                fx.val(PT, f"row {r}, ev_ltm_ebitda_x"),
                fx.id(PT, f"row {r}, ev_usd_m"),
                fx.id(PT, f"row {r}, ev_ltm_ebitda_x"),
            )
        )
    pr_lo, pr_hi = min(p[1] for p in prec), max(p[1] for p in prec)

    def dcf(w: float, g: float) -> float:
        pv = sum(c / (1 + w) ** (i + 1) for i, c in enumerate(fcf))
        return ps(pv + fcf[-1] * (1 + g) / (w - g) / (1 + w) ** 5)

    waccs, tgrs = [0.080, 0.0825, 0.085, 0.0875, 0.090], [0.020, 0.025, 0.030]
    grid = [[round(dcf(w, g), 2) for g in tgrs] for w in waccs]
    flat = [v for r in grid for v in r]
    ranges = [
        ("2025 trading range", lo_px, hi_px),
        (
            f"Trading comps ({ntm_rng[0]:.1f}x–{ntm_rng[1]:.1f}x FY26E EBITDA)",
            ps(ntm_rng[0] * ntm),
            ps(ntm_rng[1] * ntm),
        ),
        (f"Trading comps ({ltm_rng[0]:.1f}x–{ltm_rng[1]:.1f}x LTM EBITDA)", ps(ltm_rng[0] * ltm), ps(ltm_rng[1] * ltm)),
        (f"Precedent transactions ({pr_lo}x–{pr_hi}x LTM EBITDA)", ps(pr_lo * ltm), ps(pr_hi * ltm)),
        ("DCF (WACC 8.0%–9.0%, TGR 2.0%–3.0%)", min(flat), max(flat)),
    ]
    comps_span = fx.span(TC)
    n_above = sum(hi < offer for _, _, hi in ranges)
    if not 0 < n_above < len(ranges) or any(lo > offer for _, lo, _ in ranges):
        raise ValueError("football-field title assumes the offer is above some ranges and inside the rest")
    calc_ranges = " ".join(
        f"calc: {lab}: ${lo:.2f} to ${hi:.2f} per share = (multiple x EBITDA - {nd:.0f}) / {sh}"
        f" [{i_ntm}, {i_ltm}, {i_nd}, {sh_note['id']}, {comps_span}, {fx.span(PT)}]."
        for lab, lo, hi in ranges[1:4]
    )
    return {
        "_about": "Fictional sample built by samples/build_samples.py from samples/source/corvane-instruments/input via "
        "scripts/ingest.py. Every number cites a fact id or a calc: line. Build: node build-pitchbook.js "
        "pitchbook.sample.json",
        "output": "corvane-special-committee-book.pptx",
        "kind": "board-book",
        "meta": {
            "title": "Project Cobalt — discussion materials for the Special Committee",
            "author": "Advisor team",
            "label": "Confidential · Preliminary draft",
        },
        "sections": ["Situation", "Valuation", "Analyses"],
        "slides": [
            {
                "type": "cover",
                "title": "Project Cobalt: discussion materials",
                "subtitle": "Prepared for the Special Committee of the Board of Corvane Instruments",
                "footer": "Fictional sample · deck-studio",
                "notes": f"Fictional company and data. Built from samples/source/corvane-instruments/input via scripts/ingest.py. "
                f"Data decision: diluted shares appear as {sh_cap}M [{i_shc}] and {sh}M [{sh_note['id']}]; "
                f"per-share values use {sh}M, as management directs.",
            },
            {
                "type": "disclaimer",
                "title": "Disclaimer",
                "text": "These materials were prepared for the Special Committee's use in evaluating the proposal. They "
                "rely on public information and on projections prepared by management, which we have not verified "
                "independently. They are preliminary, are not a fairness opinion, and are not a recommendation to "
                "any shareholder. The company and figures are fictional.",
                "notes": "Disclaimer written for this sample; never copy a bank's legal text.",
            },
            {
                "type": "table",
                "section": "Situation",
                "title": f"The ${offer:.2f} offer is a {100 * (offer / unaff - 1):.1f}% premium to the unaffected price "
                f"and {ev / ltm:.1f}x LTM EBITDA",
                "unit": "($ in millions, except per-share values)",
                "header": ["Metric", "Value", "Basis"],
                "align": ["l", "r", "l"],
                "colW": [5.2, 2.2, 4.9],
                "rows": [
                    {"cells": ["Offer price per share", f"${offer:.2f}", "Sponsor proposal"], "kind": "subject"},
                    ["Unaffected share price (15 May 2026)", f"${unaff:.2f}", "Capitalization table"],
                    ["Premium to unaffected price", f"{100 * (offer / unaff - 1):.1f}%", "Offer / unaffected − 1"],
                    ["Premium to 2025 high close (1)", f"{100 * (offer / hi_px - 1):.1f}%", f"High close ${hi_px:.2f}"],
                    ["Diluted shares (2)", f"{sh}M", "Treasury method at the offer (management)"],
                    ["Implied equity value", f"${eq:,.0f}", "Offer × diluted shares"],
                    ["Net debt", f"${nd:,.0f}", "Capitalization table"],
                    ["Implied enterprise value", f"${ev:,.0f}", "Equity value + net debt"],
                    [f"EV / LTM EBITDA (${ltm:.0f}M)", f"{ev / ltm:.1f}x", "EV / LTM EBITDA"],
                    [f"EV / FY26E EBITDA (${ntm:.0f}M)", f"{ev / ntm:.1f}x", "EV / FY26E EBITDA"],
                ],
                "source": "Company capitalization table; management projections (June 2026); daily closing prices, calendar 2025",
                "footnotes": [
                    "Data note: the share price history covers calendar 2025 only, so the 2025 high is shown and "
                    "labelled as such rather than a 52-week high to the 15 May 2026 unaffected date.",
                    f"Data note: the capitalization table shows {sh_cap}M diluted shares; management directs "
                    f"{sh}M (treasury method at the offer) for per-share values.",
                ],
                "notes": f"Offer [{i_of}]; unaffected [{i_un}]; shares [{sh_note['id']}, {i_shc}]; net debt [{i_nd}]; LTM "
                f"EBITDA [{i_ltm}]; FY26E EBITDA [{i_ntm}]; 52-week high [{i_hi}]. calc: "
                f"{100 * (offer / unaff - 1):.1f}% = {offer} / {unaff} - 1 [{i_of}, {i_un}]. calc: {100 * (offer / hi_px - 1):.1f}%"
                f" = {offer} / {hi_px} - 1 [{i_hi}]. calc: ${eq:,.0f} = {offer} x {sh} [{i_of}]. calc: "
                f"${ev:,.0f} = {eq:,.0f} + {nd:.0f} [{i_nd}]. calc: {ev / ltm:.1f}x = {ev:,.0f} / {ltm:.0f} "
                f"[{i_ltm}]. calc: {ev / ntm:.1f}x = {ev:,.0f} / {ntm:.0f} [{i_ntm}].",
            },
            {
                "type": "football-field",
                "section": "Valuation",
                "title": f"The ${offer:.2f} offer sits above {n_above} of {len(ranges)} valuation ranges and inside "
                f"the other {len(ranges) - n_above}",
                "unit": "(Implied value per share, $) (1)",
                "min": 10,
                "max": 35,
                "step": 5,
                "ranges": [{"label": lab, "low": round(lo, 2), "high": round(hi, 2)} for lab, lo, hi in ranges],
                "lines": [
                    {"value": offer, "label": f"Offer ${offer:.2f}"},
                    {"value": unaff, "label": f"Unaffected ${unaff:.2f}", "accent": False},
                ],
                "source": "Management projections (June 2026); peer company filings; precedent transaction announcements; "
                "daily closing prices, calendar 2025",
                "footnotes": [
                    f"Per-share values use {sh}M diluted shares and ${nd:.0f}M net debt. Comps ranges drop the "
                    "lowest and highest multiple. DCF discounts FY26E–FY30E unlevered FCF to the start of FY26 (end-year "
                    "convention; no stub-period adjustment for the May 2026 valuation date)."
                ],
                "notes": f"52-week range ${lo_px:.2f} [{i_lo}] to ${hi_px:.2f} [{i_hi}]. {calc_ranges} calc: DCF "
                f"${min(flat):.2f} to ${max(flat):.2f} from the sensitivity grid [{', '.join(i_fcf)}, "
                f"{', '.join(wacc_ids)}]. Offer [{i_of}]; unaffected [{i_un}]. calc: {n_above} of {len(ranges)} ranges end below "
                f"${offer:.2f} [{i_of}].",
            },
            {
                "type": "chart",
                "section": "Analyses",
                "title": f"The smallest premium is to the 2025 high: the ${offer:.2f} offer is "
                f"{100 * (offer / hi_px - 1):.1f}% above it",
                "kind": "column",
                "labels": ["Unaffected (15 May 2026)", "2025 high", "2025 average", "2025 low"],
                "series": [
                    {
                        "name": "Premium implied by the offer",
                        "values": [round(100 * (offer / v - 1), 1) for v in (unaff, hi_px, avg_px, lo_px)],
                    }
                ],
                "highlight": 1,  # the 2025 high: the smallest premium (checked where the prices load)
                "format": '0.0"%"',
                "unit": f"(Premium implied by the ${offer:.2f} offer, %)",
                "source": "Company capitalization table; daily closing prices, calendar 2025",
                "notes": f"Offer [{i_of}]; unaffected [{i_un}]; 2025 high [{i_hi}]; 2025 low [{i_lo}]; closes "
                f"[{fx.span(SP)}]. calc: {100 * (offer / unaff - 1):.1f}% = {offer} / {unaff} - 1 [{i_of}, {i_un}]. calc: "
                f"{100 * (offer / hi_px - 1):.1f}% = {offer} / {hi_px} - 1 [{i_of}, {i_hi}]. calc: "
                f"{100 * (offer / avg_px - 1):.1f}% = {offer} / {avg_px:.2f} - 1, where ${avg_px:.2f} is the mean of "
                f"{len(prices)} 2025 closes [{i_of}, {fx.span(SP)}]. calc: "
                f"{100 * (offer / lo_px - 1):.1f}% = {offer} / {lo_px} - 1 [{i_of}, {i_lo}].",
            },
            {
                "type": "table",
                "section": "Analyses",
                "title": f"Trading comps: the offer values Corvane at {ev / ltm:.1f}x LTM EBITDA against a "
                f"{statistics.median(ltm_x):.1f}x peer median",
                "unit": "($ in millions)",
                "header": ["Company", "Enterprise value", "EV / LTM EBITDA", "EV / NTM EBITDA"],
                "colW": [4.8, 2.5, 2.5, 2.5],
                "rows": [[n, f"{e:,.0f}", f"{e / l_:.1f}x", f"{e / t:.1f}x"] for n, e, l_, t, _ in comps]
                + [
                    {
                        "cells": [
                            "Median",
                            f"{statistics.median([c[1] for c in comps]):,.0f}",
                            f"{statistics.median(ltm_x):.1f}x",
                            f"{statistics.median(ntm_x):.1f}x",
                        ],
                        "kind": "summary",
                    },
                    {
                        "cells": ["Corvane at offer (1)", f"{ev:,.0f}", f"{ev / ltm:.1f}x", f"{ev / ntm:.1f}x"],
                        "kind": "subject",
                    },
                ],
                "source": "Peer company filings; company capitalization table; management projections (June 2026)",
                "footnotes": ["NTM EBITDA for Corvane is management's FY26E."],
                "notes": " ".join(
                    f"calc: {n} {e / l_:.1f}x = {e:,.0f} / {l_:.0f} and {e / t:.1f}x = {e:,.0f} / {t:.0f} "
                    f"[{', '.join(ids)}]."
                    for n, e, l_, t, ids in comps
                )
                + f" calc: medians EV {statistics.median([c[1] for c in comps]):,.0f}, LTM "
                f"{statistics.median(ltm_x):.1f}x, NTM {statistics.median(ntm_x):.1f}x = middle of five values "
                f"[{comps_span}]. calc: Corvane {ev:,.0f}, {ev / ltm:.1f}x, {ev / ntm:.1f}x [{i_of}, "
                f"{sh_note['id']}, {i_nd}, {i_ltm}, {i_ntm}].",
            },
            {
                "type": "table",
                "section": "Analyses",
                "title": f"Precedents: the offer's {ev / ltm:.1f}x LTM EBITDA compares with a "
                f"{statistics.median(p[1] for p in prec):.1f}x transaction median",
                "unit": "($ in millions)",
                "header": ["Date", "Target", "Acquirer", "Enterprise value", "EV / LTM EBITDA"],
                "colW": [1.6, 2.8, 2.8, 2.5, 2.6],
                "align": ["l", "l", "l", "r", "r"],
                "rows": [
                    ["Mar 2023", "Target Alpha", "Sponsor E", f"{prec[0][0]:,.0f}", f"{prec[0][1]}x"],
                    ["Jun 2024", "Target Beta", "Strategic F", f"{prec[1][0]:,.0f}", f"{prec[1][1]}x"],
                    ["Jan 2025", "Target Gamma", "Sponsor G", f"{prec[2][0]:,.0f}", f"{prec[2][1]}x"],
                    ["Nov 2025", "Target Omega", "Strategic H", f"{prec[3][0]:,.0f}", f"{prec[3][1]}x"],
                    {
                        "cells": [
                            "",
                            "Median",
                            "",
                            f"{statistics.median(p[0] for p in prec):,.0f}",
                            f"{statistics.median(p[1] for p in prec):.1f}x",
                        ],
                        "kind": "summary",
                    },
                    {"cells": ["", "Corvane at offer", "", f"{ev:,.0f}", f"{ev / ltm:.1f}x"], "kind": "subject"},
                ],
                "source": "Precedent transaction announcements; company capitalization table",
                "notes": f"Transactions [{fx.span(PT)}]. calc: median EV "
                f"{statistics.median(p[0] for p in prec):,.0f} and multiple "
                f"{statistics.median(p[1] for p in prec):.1f}x = mean of the middle two values [{fx.span(PT)}]. "
                f"calc: Corvane {ev:,.0f} and {ev / ltm:.1f}x [{i_of}, {sh_note['id']}, {i_nd}, {i_ltm}].",
            },
            {
                "type": "sensitivity",
                "section": "Analyses",
                "title": f"DCF: {sum(v >= offer for v in flat)} of 15 cases reach the ${offer:.2f} offer; the base case "
                f"is ${grid[2][1]:.2f}",
                "unit": "(Implied value per share, $) (1)",
                "corner": "WACC \\ TGR",
                "cols": ["2.0%", "2.5%", "3.0%"],
                "rows": [f"{w * 100:.2f}%" for w in waccs],
                "values": grid,
                "threshold": offer,
                "format": "usd2",
                "base": [2, 1],
                "source": "Management projections (June 2026); management WACC and growth ranges",
                "side": {
                    "points": [
                        {"lead": "Base case.", "text": f"${grid[2][1]:.2f} at 8.5% WACC and 2.5% growth."},
                        {
                            "lead": "Against the offer.",
                            "text": f"{sum(v >= offer for v in flat)} of 15 cases reach ${offer:.2f}.",
                        },
                    ]
                },
                "footnotes": [
                    "Unlevered FCF FY26E–FY30E; Gordon-growth terminal value; discounted to the start of FY26 with no "
                    "stub-period adjustment."
                ],
                "notes": " ".join(
                    f"calc: ${grid[i][j]:.2f} at WACC {waccs[i] * 100:.2f}%, TGR {tgrs[j] * 100:.1f}% "
                    f"[{', '.join(i_fcf)}, {i_nd}, {sh_note['id']}]."
                    for i in range(5)
                    for j in range(3)
                )
                + f" calc: 8.25% and 8.75% are steps inside the management range [{', '.join(wacc_ids)}]. "
                f"calc: {sum(v >= offer for v in flat)} of 15 cases = count of the 5 x 3 grid at or above the "
                f"offer [{i_of}, {', '.join(wacc_ids)}].",
            },
        ],
    }


def main() -> int:
    alder, corvane = SRC / "alder-vale-hotels" / "input", SRC / "corvane-instruments" / "input"
    halden = SRC / "halden-freight" / "input"
    alder_vale_inputs(alder)
    corvane_inputs(corvane)
    pitch_sample.halden_inputs(halden, save, write)
    fa, fc, fh = ingest(alder), ingest(corvane), ingest(halden)
    (SKILL / "templates" / "consulting-deck.sample.json").write_text(
        json.dumps(consulting(fa), indent=1, ensure_ascii=False) + "\n"
    )
    (SKILL / "templates" / "pitchbook.sample.json").write_text(
        json.dumps(banking(fc), indent=1, ensure_ascii=False) + "\n"
    )
    (SKILL / "templates" / "pitchbook-pitch.sample.json").write_text(
        json.dumps(pitch_sample.pitch(fh, halden), indent=1, ensure_ascii=False) + "\n"
    )
    print("wrote templates/consulting-deck.sample.json, pitchbook.sample.json, and pitchbook-pitch.sample.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
