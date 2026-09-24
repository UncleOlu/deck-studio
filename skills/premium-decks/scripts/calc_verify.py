"""Parse and verify the derivations ("calc:" lines) in a deck's speaker notes.

A derivation is written  calc: <label> <result> = <expression> [F0001, F0002]
and several may share one line, separated by ";" (or chained: "a = x / y and
b = x / z"). Figures that are the author's choice rather than data are declared
on their own line:  assume: $21.00, $23.00 (illustrative prices) The expression may use plain
numbers, fact ids as variables (F0012) or ranges (F0001:F0005), + - * / ( ),
"x" or "×" for multiply, SUM / AVERAGE / MEDIAN / MIN / MAX / COUNT(...), and
percentages ("12.9%" means 0.129). Thousands separators and
currency symbols are ignored.

check_arithmetic() evaluates the expression with ingest.Formula (no eval()) and
compares it with the result at the result's printed precision:
  ok        the expression gives the result
  error     it evaluates, but to a different number
  unparsed  it has prose or units the evaluator cannot read (not verifiable)
Whether the expression's inputs are themselves sourced is checked by
trace-check.py, which knows the fact base and the deck's other derivations.
"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ingest  # noqa: E402

FACT_ID = re.compile(r"\bF\d{4}\b")
# a statement ends at its citation "]", a sentence break, a new line, or the next calc:/assume:
STATEMENT = re.compile(r"calc:(.*?(?:\]|(?=\.\s+[A-Z\d]|calc:|assume:|\n|$)))", re.S)
CITATION = re.compile(r"\[[^\]]*\]")
LITERAL = re.compile(r"(?<![F\d.])\d+(?:\.\d+)?")
# a result may round its inputs: allow half a printed step plus 0.2% of the value
REL_SLACK = 0.002


@dataclass
class Segment:
    text: str  # the whole segment, for messages
    lhs_raw: str  # the result as printed, e.g. "$2.4M"
    lhs_value: float  # its number, e.g. 2.4
    lhs_unit: str
    lhs_scale: float  # 1e6 for "$2.6M": an expression may work in units
    rhs: str  # the first expression, as written
    ids: list[str] = field(default_factory=list)  # fact ids cited on the statement
    terms: list[str] = field(default_factory=list)  # every expression said to equal the result (a chain)
    lhs_low: float | None = None  # "$49–52M" states a range: its low end (lhs_value is the high end)


@dataclass
class Result:
    segment: Segment
    status: str  # ok | error | unparsed
    value: float | None = None  # what the first readable expression evaluates to
    literals: list[float] = field(default_factory=list)  # plain numbers used in the expressions
    detail: str = ""


Head = tuple[str, float, str, float, "float | None"]  # (printed, value, unit, scale, range low)
OPERATOR_BEFORE = re.compile(r"[-+*/x×(]\s*[$€£]?\s*$")
# "$49–52M" or "$9–12M annual gains": a range, optionally followed by label words
RANGE_AT_END = re.compile(
    r"[$€£]?(\d[\d,]*(?:\.\d+)?)\s*[–-]\s*[$€£]?\d[\d,]*(?:\.\d+)?[A-Za-z%]*(?:\s+[A-Za-z][\w-]*)*$"
)


def _family(unit: str) -> str:
    return "money" if unit in ("USD", "EUR", "GBP") else unit


def _result_at_end(text: str) -> Head | None:
    """The result stated at the end of text, or None when that number is part of an expression ("4 x 13.1")."""
    text = text.rstrip()
    nums = ingest.numbers_in(text)
    if not nums:
        return None
    value, unit, scale, s, e = nums[-1]
    rng = RANGE_AT_END.search(text)
    if rng and len(nums) >= 2 and nums[-2][3] >= rng.start():
        low = nums[-2][0] * (nums[-2][2] if nums[-2][2] != 1.0 else scale) / scale  # "$49–52M": 49 is in M too
        return text[rng.start() : e].strip(), value, unit, scale, low
    if OPERATOR_BEFORE.search(text[:s]):
        return None
    return text[s:e].strip(), value, unit, scale, None


def segments(notes: str) -> list[Segment]:
    """Every result and the expressions said to equal it, from the notes' calc: statements.

    "a = x / y and b = x / z" holds two results; "EUR 2.5B = 910 + 520 = 1,430" is one result with a
    chain of two expressions that must both agree with it."""
    out: list[Segment] = []

    def emit(head: Head | None, terms: list[str], ids: list[str]) -> None:
        terms = [t.strip() for t in terms if t.strip()]
        if head and terms:
            raw, value, unit, scale, low = head
            out.append(Segment(f"{raw} = {' = '.join(terms)}", raw, value, unit, scale, terms[0], ids, terms, low))

    for m in STATEMENT.finditer(notes):
        statement = m.group(1)
        ids = FACT_ID.findall(" ".join(CITATION.findall(statement)))
        for part in CITATION.sub("", statement).split(";"):
            pieces = part.strip().rstrip(".").strip().split("=")
            head = _result_at_end(pieces[0])
            terms: list[str] = []
            for k, piece in enumerate(pieces[1:], start=1):
                bare = ingest.numbers_in(piece)
                if k < len(pieces) - 1 and " and " in piece:
                    before, after = piece.rsplit(" and ", 1)  # "... / 402 and 9.2x = ..." starts a new result
                    emit(head, terms + [before], ids)
                    head, terms = _result_at_end(after), []
                elif (
                    head
                    and len(bare) == 1
                    and not _is_expression(piece)
                    and _family(bare[0][1]) != _family(head[2])
                    and {bare[0][1], head[2]} != {"%", ""}
                ):
                    # "10 bps = $4.82M = 0.10% x 4820": the unit changes, so a new result starts
                    emit(head, terms, ids)
                    head, terms = _result_at_end(piece), []
                else:
                    terms.append(piece)
            emit(head, terms, ids)
    return out


ASSUME = re.compile(r"assume:(.*?)(?=calc:|assume:|\n|$)", re.S)


def assumptions(notes: str) -> list[float]:
    """Numbers declared as assumptions: "assume: $21.00, $23.00 (illustrative prices)"."""
    return [v for m in ASSUME.finditer(notes) for v, *_ in ingest.numbers_in(CITATION.sub("", m.group(1)))]


def normalise(expr: str) -> str | None:
    """The expression in Formula's grammar, or None if it holds prose or units."""
    e = expr.replace("×", "*").replace("−", "-").replace("–", "-")
    e = re.sub(r"(\d+(?:\.\d+)?)\s*bps\b", r"(\1/10000)", e)  # "15 bps x $4.82B"
    e = re.sub(r"(?<=[\d)%])\s*[xX]\s*(?=[\d(F$€£])", "*", e)  # "18.6 x 86.0" multiplies
    e = re.sub(r"[$€£]", "", e)
    e = re.sub(r"(?<=\d),(?=\d{3}(?!\d))", "", e)  # thousands separators, also in "2,310k"
    e = re.sub(r"\(\s*[^()\d]*\)\s*$", "", e)  # a closing aside such as "(sum of hotel rows)"
    scale = {"k": "1000", "m": "1000000", "bn": "1000000000", "b": "1000000000"}
    e = re.sub(r"(\d+(?:\.\d+)?)(k|M|bn|B)\b", lambda m: f"({m.group(1)}*{scale[m.group(2).lower()]})", e)
    e = re.sub(r"(?<=[\d)])\s+[a-z][a-z-]*(?=\s*(?:[-+*/)]|$))", "", e)  # a unit word: "521,500 room-nights"
    e = re.sub(r"(\d+(?:\.\d+)?)\s*%", r"(\1/100)", e)
    e = e.strip()
    leftover = FACT_ID.sub("", re.sub(r"\b(?:SUM|AVERAGE|MEDIAN|MIN|MAX|COUNT)\(", "(", e, flags=re.I))
    if re.search(r"[A-Za-z]", leftover) or not re.search(r"[\dF]", e):
        return None
    return e


def close(a: float, b: float, printed: float) -> bool:
    step: float = 10 ** -ingest.decimals(printed)
    return bool(abs(a - b) <= step / 2 + REL_SLACK * abs(b) + 1e-9)


def _is_expression(expr: str) -> bool:
    return bool(re.search(r"[-+*/]|\b(?:SUM|AVERAGE|MEDIAN|MIN|MAX|COUNT)\(", expr.lstrip("-")))


def _agrees(v: float, seg: Segment, has_pct: bool) -> bool:
    """The expression's value agrees with the printed result, allowing the ways notes state units."""
    targets = [seg.lhs_value] + ([seg.lhs_low] if seg.lhs_low is not None else [])
    accounting = seg.lhs_raw.lstrip().startswith("(")  # "(61)" prints a negative
    cands = [v]
    if seg.lhs_unit == "%" or has_pct:
        cands.append(v * 100)  # "26.2% = 27.0 / 21.4 - 1" and "1.4 pts = 16.9% - 15.5%"
    if seg.lhs_unit == "bps":
        cands.append(v * 10_000)
    for k in (1e3, 1e6, 1e9):  # "$2.6M = ... x 521,500" in dollars; "EUR 2.5B = 2,530" or a $B cell over $M working
        cands += [v * k / seg.lhs_scale, v / k] if seg.lhs_scale != 1.0 else [v * k, v / k]
    if seg.lhs_scale != 1.0:
        cands.append(v / seg.lhs_scale)
    for c in cands:
        for t in targets:
            if close(abs(c) if accounting else c, abs(t) if accounting else t, t):
                return True
    return False


def check_arithmetic(seg: Segment, facts: dict[str, ingest.Fact]) -> Result:
    def lookup(ref: str) -> list[float]:
        first, _, last = ref.partition(":")  # "F0001:F0005" is every fact in between
        ids = [first] if not last else [f"F{i:04d}" for i in range(int(first[1:]), int(last[1:]) + 1)]
        out = []
        for i in ids:
            fact = facts.get(i)
            if fact is None or isinstance(fact.value, str):
                raise ValueError(f"unknown or non-numeric fact {i}")
            out.append(float(fact.value))
        return out

    evaluated: list[tuple[str, float, bool]] = []  # (term, value, is an expression)
    literals: list[float] = []
    problems: list[str] = []
    for term in seg.terms or [seg.rhs]:
        expr = normalise(term)
        if expr is None:
            problems.append(f"'{term[:40]}' has words or units the checker cannot evaluate")
            continue
        try:
            value = ingest.Formula(expr, lookup).value()
        except (ValueError, ZeroDivisionError, IndexError) as err:
            problems.append(f"cannot evaluate '{term[:40]}': {err}")
            continue
        evaluated.append((term, value, _is_expression(expr)))
        literals += [float(x) for x in LITERAL.findall(FACT_ID.sub(" ", expr))]
    if not evaluated:
        return Result(seg, "unparsed", detail="; ".join(problems))
    first = evaluated[0][1]
    wrong = [(t, v) for t, v, _ in evaluated if not _agrees(v, seg, "%" in t)]
    if any(is_expr for _, _, is_expr in evaluated):
        if wrong:  # an expression that evaluates to a different number is a real contradiction
            t, v = wrong[0]
            return Result(seg, "error", first, literals, f"'{t.strip()[:40]}' gives {v:,.4g}, not {seg.lhs_raw}")
        return Result(seg, "ok", first, literals)
    # only bare restatements ("50% of FY26E UFCF = 59"): agreement is fine, disagreement is ambiguous
    if wrong:
        return Result(seg, "unparsed", first, literals, "a restatement, not a calculation")
    return Result(seg, "ok", first, literals)
