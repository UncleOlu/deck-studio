#!/usr/bin/env python3
"""Write skills/premium-decks/data/slide-archetypes.csv: guidance + measured corpus shares.

The guidance columns are authored here. The share columns are recomputed
from the primary coding records (derive set only), so the CSV always matches
research/corpus-stats.md. Run after tools/corpus/aggregate.py.
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORPUS = Path.home() / "deck-corpus"
OUT = ROOT / "skills" / "premium-decks" / "data" / "slide-archetypes.csv"

# archetype, registers, keywords, answers the question, required elements, build with, avoid when
GUIDE = [
    ("exec-summary", "consulting|banking", "executive summary, answer, key messages, synthesis",
     "What is the answer and why should I believe it?",
     "Governing answer in bold; 3-5 supporting arguments each with its key number; evidence dashes",
     "dot-dash text (storyline.md §5)", "the deck has no single answer yet: fix the storyline first"),
    ("text-structured", "consulting", "structured text, bold lead-in, findings, dense page",
     "What are the points and how do they group?",
     "Action title; bold lead-in per point; <=5 blocks; source if claims are factual",
     "2-column label/explanation grid", "a chart would prove the point faster"),
    ("chart-single", "consulting|banking|keynote", "chart, single chart, evidence, trend, comparison",
     "Does the data support the title's claim?",
     "Action title naming the datum; one chart; accent on the datum; source line",
     "native chart (finance-charts.md)", "two ideas compete: split the slide"),
    ("chart-multi", "banking|consulting", "multiple charts, dashboard, panels, small multiples",
     "How do several related measures move together?",
     "One shared claim; aligned axes; each panel labelled; one source block",
     "2-4 aligned native charts", "panels answer different questions"),
    ("waterfall-bridge", "consulting|banking", "waterfall, bridge, walk, variance, ebitda bridge",
     "How did we get from A to B?", "Steps that sum exactly; largest step in accent; totals labelled",
     "finance-charts.md waterfall", "more than ~8 steps or mixed periods"),
    ("table-data", "consulting|banking", "table, data table, comparison table, matrix",
     "How do these items compare across the same attributes?",
     "Right-aligned numerics; one precision per column; highlighted row for the subject; source",
     "native table", "fewer than 3 rows: use a sentence or a chart"),
    ("comps-table", "banking", "trading comps, comparable companies, multiples, peers",
     "What do peers trade at and where does the subject sit?",
     "EV and multiples columns; median row; subject row tinted; as-of date; definitions",
     "finance-charts.md comps table", "peer set not like-for-like"),
    ("football-field", "banking", "football field, valuation summary, valuation ranges, offer",
     "What is it worth and where does the offer fall?",
     "One bar per method with assumptions in the label; offer line; units; source",
     "finance-charts.md football field", "fewer than 3 methods"),
    ("sensitivity-table", "banking|consulting", "sensitivity, heat map table, wacc, terminal growth",
     "How much does the answer move with the key assumptions?",
     "Two variables; base case outlined; two-step fill against a threshold",
     "finance-charts.md sensitivity table", "the model is not built yet"),
    ("financial-summary", "banking", "financial summary, projections, p&l, management case",
     "What does the business earn now and in the plan?",
     "Periods as columns; case named; units line; margins as %", "native table",
     "used for a single number"),
    ("framework-diagram", "consulting", "framework, 2x2, matrix, driver tree, value chain",
     "How is the problem structured?", "Framework chosen by question (frameworks.md); labelled key element",
     "shapes or bubble chart", "decorative diagrams whose shape carries no meaning"),
    ("findings-table", "consulting", "observations, findings table, recommendations table, assessment",
     "What did we observe and what do we recommend for each area?",
     "Columns: area, observation, implication/recommendation; bold lead-ins", "native table",
     "a single finding: use an action title and a chart"),
    ("situation-context", "consulting|banking", "situation, context, background, overview",
     "What does the reader need to know first?", "The facts, measured; no adjectives",
     "chart or short structured text", "more than one page of background"),
    ("options-evaluation", "consulting", "options, alternatives, criteria, harvey balls, trade-offs",
     "Which option is best, on what criteria?", "Exclusive options; stated criteria; recommended row highlighted",
     "Harvey-ball table (finance-charts.md)", "criteria that restate each other"),
    ("timeline-roadmap", "consulting", "roadmap, timeline, phases, gantt, plan, waves",
     "When does what happen, and who owns it?", "Workstreams, dates, owners, milestones",
     "gantt bars (html-components.md / shapes)", "more than ~6 workstreams on one page"),
    ("recommendation", "consulting", "recommendation, next steps, decisions, ask",
     "What must the reader decide or do?", "Decision, owner, date, value at stake",
     "structured text or table", "no owner or date"),
    ("divider", "consulting|banking", "section divider, agenda highlight, chapter",
     "Where are we in the argument?", "Agenda with current section highlighted (consulting) or title-only (banking)",
     "master layout", "decks with fewer than 3 sections"),
]


def main() -> int:
    man = {}
    for name in ("manifest.jsonl", "manifest-aggregators.jsonl", "manifest-public.jsonl"):
        p = CORPUS / name
        if p.exists():
            for line in p.read_text().splitlines():
                if line.strip():
                    row = json.loads(line)
                    man[row["id"]] = row
    recs = {}
    for d in sorted(CORPUS.glob("coding/c[0-9]*")):
        for f in d.glob("*.json"):
            r = json.loads(f.read_text())
            if not man.get(r["deck_id"], {}).get("holdout", True):
                recs.setdefault(r["deck_id"], r)
    mbb, bank = Counter(), Counter()
    for deck_id, r in recs.items():
        row = man[deck_id]
        is_client = row["genre"] in ("consulting-client", "public-sector-client")
        target = bank if row["genre"] == "banking-board-book" else \
            mbb if is_client and row["firm_stratum"] == "mbb" else None
        if target is not None:
            target.update(s["archetype"] for s in r["slides"])
    nm, nb = sum(mbb.values()) or 1, sum(bank.values()) or 1
    with OUT.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["id", "archetype", "registers", "keywords", "answers_question", "required_elements", "build_with",
                    "avoid_when", "share_mbb_client_pct", "share_banking_pct", "source"])
        for i, (arch, regs, kw, q, req, build, avoid) in enumerate(GUIDE, 1):
            w.writerow([i, arch, regs, kw, q, req, build, avoid, round(100 * mbb[arch] / nm, 1),
                        round(100 * bank[arch] / nb, 1), "deck-studio corpus study (research/corpus-findings.md)"])
    print(f"{len(GUIDE)} archetypes → {OUT} (MBB pages {nm}, banking pages {nb})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
