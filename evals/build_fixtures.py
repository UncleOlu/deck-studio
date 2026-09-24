#!/usr/bin/env python3
"""Generate the eval fixture folders (fictional, deliberately messy).

Every company, person, and figure here is invented. Each consulting/banking
fixture plants:
  - mixed units or scales across files,
  - exactly one conflicting figure for the same metric (listed in PLANTED),
  - at least one irrelevant file the deck must ignore.

Run from anywhere: python3 build_fixtures.py  (needs openpyxl)
Outputs are deterministic; re-running overwrites the fixture folders.
"""
from __future__ import annotations

import csv
import json
import random
from datetime import datetime
from pathlib import Path

from openpyxl import Workbook

ROOT = Path(__file__).resolve().parent / "cases"
random.seed(20260922)

# Planted conflicts: fixture -> (metric, value A @ locator, value B @ locator).
PLANTED = {
    "grocer-costout": ("FY25 revenue", "$4,820M @ store_pnl_FY25.xlsx!Summary!B3",
                       "$4.61B @ cfo_email.txt"),
    "market-entry": ("2029 addressable market", "EUR 6.26B (formula) @ market_sizing.xlsx!Summary!C9",
                     "EUR 7.4B @ partner_notes.md"),
    "steerco-update": ("Finance go-live date", "2027-03 @ workstream_status.csv",
                       "May 2027 @ pmo_weekly_note.md"),
    "take-private-valuation": ("Diluted shares outstanding", "58.2M @ capitalization.xlsx!Cap!B4",
                               "57.4M @ management_projections.xlsx!Notes!A3"),
    "sell-side-pitch": ("FY25 adjusted EBITDA", "$91M @ tidewater_financials.xlsx!P&L!F9",
                        "$86M @ owner_call_notes.md"),
}


FIXED_TIME = datetime(2026, 9, 22)


def save(wb: Workbook, path: Path) -> None:
    """Save with pinned timestamps so rebuilding yields identical bytes."""
    wb.properties.created = wb.properties.modified = FIXED_TIME
    wb.save(path)


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.strip() + "\n")


def write_csv(path: Path, header: list[str], rows: list[list]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


# ---------------------------------------------------------------- grocer
def grocer(d: Path) -> None:
    wb = Workbook()
    s = wb.active
    s.title = "Summary"
    s.append(["Harvest Lane Markets — FY25 summary", "$M"])
    s.append(["Stores", 142])
    s.append(["Revenue", 4820])
    s.append(["COGS", 3470])
    s.append(["Store labour", 578])
    s.append(["Shrink", 140])
    s.append(["Occupancy", 265])
    s.append(["Other store opex", 169])
    s.append(["EBIT", "=B3-B4-B5-B6-B7-B8"])
    s.append(["EBIT margin", "=B9/B3"])
    st = wb.create_sheet("Stores ($k)")
    st.append(["store_id", "format", "region", "revenue_k", "labour_k", "shrink_k", "sq_ft"])
    formats = [("Superstore", 52000, 0.112), ("Neighbourhood", 28000, 0.128), ("Express", 14000, 0.141)]
    for i in range(1, 143):
        fmt, base, lab = formats[0] if i <= 40 else formats[1] if i <= 110 else formats[2]
        rev = round(base * random.uniform(0.8, 1.2))
        st.append([f"HL{i:03d}", fmt, random.choice(["North", "Central", "Coastal"]), rev,
                   round(rev * lab * random.uniform(0.9, 1.15)), round(rev * random.uniform(0.022, 0.036)),
                   {"Superstore": 48000, "Neighbourhood": 22000, "Express": 7000}[fmt]])
    save(wb, d / "store_pnl_FY25.xlsx")
    write_csv(d / "peer_benchmarks.csv", ["peer", "labour_pct_sales", "shrink_pct_sales", "ebit_margin_pct"],
              [["Peer A (public filings)", 10.4, 2.1, 4.9], ["Peer B (public filings)", 11.0, 2.4, 4.1],
               ["Peer C (industry survey)", 11.6, 2.6, 3.6], ["Median", 11.0, 2.4, 4.1]])
    write(d / "interview_notes.md", """
# Store operations interviews — March 2026 (internal)

**VP Store Ops.** Scheduling is still built by store managers in spreadsheets. Labour hours
do not flex with traffic; Tuesday mornings are overstaffed by our own estimate of 15-20%.

**Director, Loss Prevention.** Fresh (produce, bakery) is ~60% of shrink. Markdown timing is
manual. Express stores have the worst shrink rate because of short shelf life ranges.

**Regional Manager, Coastal.** Self-checkout adoption is 22% of transactions vs ~40% at the
peer we lose staff to. Staff turnover in Express is above 70% a year.
""")
    write(d / "cfo_email.txt", """
From: CFO
To: Strategy team
Subject: What I need for the April board

Team — the board wants a credible path to +150 bps EBIT margin within 24 months without
closing stores. Revenue was $4.61B last year, so every 10 bps is ~$4.6M. Please focus on
labour and shrink; we already have a procurement programme running. Keep it to what the
data supports and tell me what you would do first.
""")
    write(d / "office_party_menu.txt", "Spring social: tacos, lemonade, vegan option. RSVP by Friday.")
    write_csv(d / "it_ticket_export.csv", ["ticket", "status", "summary"],
              [[1001, "closed", "Printer offline HQ-3"], [1002, "open", "VPN drops"], [1003, "open", "New laptop"]])


# ---------------------------------------------------------------- market entry
def market_entry(d: Path) -> None:
    wb = Workbook()
    s = wb.active
    s.title = "Summary"
    s.append(["Kestrel Robotics — EU warehouse AMR market (EUR M)", "2025", "2029"])
    for country, v25, v29 in [("Germany", 910, 1720), ("France", 520, 1010), ("UK (GBP M)", 480, 930),
                              ("Netherlands", 300, 640), ("Poland", 170, 450), ("Spain", 240, 520),
                              ("Rest of EU", 390, 830)]:
        s.append([country, v25, v29])
    s.append(["Total (UK converted at 1.17)", "=B2+B3+B4*1.17+B5+B6+B7+B8", "=C2+C3+C4*1.17+C5+C6+C7+C8"])
    save(wb, d / "market_sizing.xlsx")
    write_csv(d / "competitors.csv",
              ["competitor", "hq", "eu_revenue_usd_m", "installed_sites_eu", "price_per_robot_usd_k"],
              [["Competitor North", "DE", 410, 620, 38], ["Competitor Atlas", "US", 260, 310, 34],
               ["Competitor Fjord", "NO", 150, 240, 41], ["Kestrel (US only today)", "US", 0, 0, 29]])
    write(d / "customer_interviews.md", """
# 12 EU warehouse operator interviews (Feb 2026)

- 9 of 12 said labour availability is the #1 driver for automation, ahead of cost.
- 7 of 12 require a local service engineer within 4 hours; only 2 would accept remote-first.
- Payback threshold quoted: median 24 months (range 18-36).
- Germany and Netherlands operators already run pilots; Poland operators cite capex constraints.
""")
    write(d / "partner_notes.md", """
Partner notes after the kick-off: the addressable market in 2029 is EUR 7.4B per the trade
association deck. Client leadership wants a go / no-go on entering one EU country first, and
which one. Budget ceiling for year-one entry: USD 40M.
""")
    write(d / "travel_itinerary.md", "Flight LH401 JFK-FRA Tue 18:10. Hotel near Messe. Return Fri.")


# ---------------------------------------------------------------- steerco
def steerco(d: Path) -> None:
    write_csv(d / "workstream_status.csv",
              ["workstream", "owner", "status_rag", "pct_complete", "planned_go_live", "note"],
              [["Finance (ERP GL/AP/AR)", "Controller", "Amber", 64, "2027-03",
                "Data migration mock 2 slipped 3 weeks"],
               ["Procurement", "CPO", "Green", 71, "2027-03", "On track"],
               ["HR & Payroll", "CHRO", "Red", 38, "2027-06", "Payroll vendor contract unsigned"],
               ["Supply chain", "COO", "Green", 55, "2027-06", "On track"],
               ["Reporting & analytics", "CFO office", "Amber", 42, "2027-06", "Scope added: 14 new reports"]])
    wb = Workbook()
    s = wb.active
    s.title = "Budget ($k)"
    s.append(["Workstream", "Budget", "Actual to date", "Forecast at completion"])
    for row in [["Finance", 8200, 5900, 9100], ["Procurement", 3100, 2050, 3000], ["HR & Payroll", 4400, 1800, 5300],
                ["Supply chain", 5600, 2900, 5500], ["Reporting", 2300, 1100, 2900],
                ["PMO & change", 2400, 1500, 2500]]:
        s.append(row)
    s.append(["Total", "=SUM(B2:B7)", "=SUM(C2:C7)", "=SUM(D2:D7)"])
    save(wb, d / "budget_tracker.xlsx")
    write(d / "risks_log.md", """
| # | Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|---|
| R1 | Payroll vendor contract not signed by 30 Oct | High | High | Escalate to CEO; fallback vendor | CHRO |
| R2 | Data migration quality (vendor master 11% duplicates) | Medium | High | Add cleansing sprint | Controller |
| R3 | Change fatigue in hospitals during winter peak | Medium | Medium | Move training to Feb | PMO |
""")
    write(d / "pmo_weekly_note.md", """
PMO weekly — Project Meridian for Calder Health. Finance go-live now tracking to May 2027
after the mock-2 slip. SteerCo on 14 Oct must decide: (1) approve $1.4M contingency draw for
HR & Payroll, (2) accept the 14 extra reports or defer them to wave 2.
""")
    write(d / "lunch_order.txt", "SteerCo lunch: 12 sandwiches, 2 GF, coffee for 14.")


# ---------------------------------------------------------------- take-private
def take_private(d: Path) -> None:
    wb = Workbook()
    c = wb.active
    c.title = "Cap"
    c.append(["Ashgrove Industrial (NYSE: ASHG, fictional) — capitalization", "value", "unit"])
    c.append(["Share price (unaffected, 30 Jun 2026)", 33.10, "$"])
    c.append(["Offer price (sponsor proposal)", 41.50, "$"])
    c.append(["Diluted shares outstanding", 58.2, "M"])
    c.append(["Net debt", 612, "$M"])
    c.append(["LTM EBITDA", 238, "$M"])
    save(wb, d / "capitalization.xlsx")
    wb = Workbook()
    p = wb.active
    p.title = "Projections ($M)"
    p.append(["", "FY26E", "FY27E", "FY28E", "FY29E", "FY30E"])
    p.append(["Revenue", 1610, 1705, 1810, 1905, 1990])
    p.append(["EBITDA", 250, 272, 296, 318, 336])
    p.append(["Capex", 71, 75, 79, 82, 85])
    p.append(["Unlevered FCF", 118, 131, 146, 160, 171])
    n = wb.create_sheet("Notes")
    n.append(["Management case prepared for the Special Committee, Aug 2026."])
    n.append(["WACC range used by management: 8.5%-9.5%; terminal growth 2.0%-3.0%."])
    n.append(["Per-share values should use 57.4M diluted shares (treasury method at offer)."])
    save(wb, d / "management_projections.xlsx")
    write_csv(d / "trading_comps.csv", ["company", "ev_usd_m", "ebitda_ltm_usd_m", "ebitda_ntm_usd_m"],
              [["Peer Alder", 5120, 480, 505], ["Peer Birch", 2890, 301, 322], ["Peer Cedar", 7400, 690, 720],
               ["Peer Dogwood", 1980, 221, 230], ["Peer Elm", 3350, 305, 331]])
    write_csv(d / "precedent_transactions.csv", ["date", "target", "acquirer", "ev_usd_m", "ev_ltm_ebitda_x"],
              [["2023-05", "Target One", "Sponsor A", 2100, 10.2], ["2024-02", "Target Two", "Strategic B", 3900, 11.8],
               ["2024-11", "Target Three", "Sponsor C", 1450, 9.4],
               ["2025-09", "Target Four", "Strategic D", 5200, 12.5]])
    rows, price = [], 29.0
    for i in range(52):
        price = round(price * random.uniform(0.97, 1.035), 2)
        rows.append([f"2025-W{i + 1:02d}", price])
    write_csv(d / "share_price_52w.csv", ["week", "close_usd"], rows)
    write(d / "parking_memo.txt", "Garage level 2 closed for resurfacing next week. Use level 4.")


# ---------------------------------------------------------------- sell-side
def sell_side(d: Path) -> None:
    wb = Workbook()
    s = wb.active
    s.title = "P&L"
    s.append(["Tidewater Specialty Foods ($M)", "FY21", "FY22", "FY23", "FY24", "FY25"])
    s.append(["Net sales", 402, 455, 511, 568, 640])
    s.append(["Gross profit", 121, 141, 163, 187, 218])
    s.append(["Reported EBITDA", 48, 57, 66, 74, 84])
    s.append(["Add-back: owner compensation above market", 3, 3, 3, 3, 3])
    s.append(["Add-back: one-off plant move", 0, 0, 0, 2, 4])
    s.append(["", "", "", "", "", ""])
    s.append(["", "", "", "", "", ""])
    s.append(["Adjusted EBITDA", "=B4+B5+B6", "=C4+C5+C6", "=D4+D5+D6", "=E4+E5+E6", "=F4+F5+F6"])
    save(wb, d / "tidewater_financials.xlsx")
    write_csv(d / "buyer_universe.csv", ["buyer", "type", "rationale", "capacity_usd_bn"],
              [["Strategic Harbor Foods", "strategic", "Adds refrigerated sauces", 12],
               ["Strategic Meridian Brands", "strategic", "Fills US East Coast gap", 8],
               ["Sponsor Granite Capital", "financial", "Food platform fund IV", 6],
               ["Sponsor Lakeshore Partners", "financial", "Buy-and-build thesis", 3],
               ["Strategic Norland (EU)", "strategic", "US market entry", 15]])
    write_csv(d / "sector_multiples.csv", ["segment", "ev_ntm_ebitda_x_median", "n_deals_2023_2026"],
              [["Specialty foods (branded)", 13.1, 18], ["Private label food", 9.4, 11], ["Refrigerated", 12.2, 7]])
    write(d / "owner_call_notes.md", """
Call with founder-owner (Tidewater), 9 Sep 2026. Owner says adjusted EBITDA was $86M last year
and wants "north of $1.1B". Wants to know timing (sell in H1 2027?), likely buyers, and whether
to keep a minority stake. Management team of 6 would stay.
""")
    write(d / "golf_outing.txt", "Client golf outing moved to 3 Oct. Tee times from 08:30.")


# ---------------------------------------------------------------- keynote fixtures
def keynote_allhands(d: Path) -> None:
    write(d / "brief.md", """
Company: Lumen Notes (fictional note-taking app), 140 employees.
Event: annual all-hands, 20-minute talk by the CEO.
Message: we are moving from "notes" to "shared team memory". Three bets for 2027: live
collaboration, offline-first sync, and an API. Share the 2026 numbers below; celebrate the
support team.
2026: 1.9M monthly active users (2025: 1.2M); paid teams 8,400 (2025: 5,100);
median sync latency 180 ms (2025: 420 ms); support CSAT 94%.
""")


def keynote_conference(d: Path) -> None:
    write(d / "brief.md", """
Conference talk (30 min, technical-leaning audience): "What 3 years of on-call data taught us".
Fictional company: Fernbank Cloud. Data: 1,140 incidents 2023-2025; 61% caused by config
changes; median time-to-mitigate fell from 52 min (2023) to 19 min (2025) after adopting
staged rollouts; pages per engineer per week fell 3.1 -> 1.2. Close with three practices.
""")


FIXTURES = {
    "grocer-costout": grocer,
    "market-entry": market_entry,
    "steerco-update": steerco,
    "take-private-valuation": take_private,
    "sell-side-pitch": sell_side,
    "keynote-allhands": keynote_allhands,
    "keynote-conference": keynote_conference,
}


def main() -> None:
    for name, build in FIXTURES.items():
        d = ROOT / name / "input"
        d.mkdir(parents=True, exist_ok=True)
        build(d)
    (ROOT.parent / "planted.json").write_text(json.dumps(PLANTED, indent=2) + "\n")
    print("built:", ", ".join(FIXTURES))


if __name__ == "__main__":
    main()
