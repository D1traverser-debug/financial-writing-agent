"""Conservative hard-negative checks before sourcing a financial assertion.

This catches *direct contradictions*; it does NOT establish semantic
entailment, causal truth, primary-source authority or independent review.
When a comparison is ambiguous rather than clearly false, leave it for
external editorial adjudication instead of reporting a fake semantic PASS.
"""
from __future__ import annotations

import re
import unicodedata

_PERIOD = re.compile(
    r"(20\d{2})\s*(?:年)?\s*(上半年|下半年|前三季度|第一季度|第二季度|第三季度|第四季度|全年|年度|年报|半年度|[HQ][1-4]|FY)",
    flags=re.I,
)
_PERIOD_ALIASES = {
    "上半年": "H1", "半年度": "H1", "下半年": "H2",
    "第一季度": "Q1", "第二季度": "Q2",
    "第三季度": "Q3", "第四季度": "Q4",
    "前三季度": "Q1-Q3",
    "全年": "FY", "年度": "FY", "年报": "FY",
}


def _canonical_periods(text: str) -> set[tuple[str, str]]:
    """Normalize equivalent Chinese/English spellings without losing the year.

    This prevents false direct-contradiction reports; it does not certify
    financial source entailment, publication freshness or editorial quality.
    """
    return {
        (year, _PERIOD_ALIASES.get(period, period.upper()))
        for year, period in _PERIOD.findall(text)
    }


_NUMBER_UNIT = re.compile(r"(\d+(?:\.\d+)?)\s*(万亿元|亿元|万美元|亿美元|万元|万|元|%|％)")
_DIRECTION_NUMBER = re.compile(
    r"(?:同比|环比|较上期|较去年同期)?\s*"
    r"(增长|上升|增加|提升|扩大|下降|下滑|减少|降低|收缩)\s*"
    r"(?:约|超过|近)?\s*(\d+(?:\.\d+)?)\s*(%|％|万亿元|亿元|万元|亿美元|元)?"
)
_POSITIVE = frozenset({"增长", "上升", "增加", "提升", "扩大"})
_NEGATIVE = frozenset({"下降", "下滑", "减少", "降低", "收缩"})
_METRIC = ("营业收入", "净利润", "毛利率", "收入", "利润", "成本", "订单", "库存", "销售额", "出口", "进口", "现金流")


class FinancialFactConflict(ValueError):
    pass


def _clean(text: str) -> str:
    return unicodedata.normalize("NFKC", str(text)).replace("**", "").replace("__", "")


def _unit(value: str) -> str:
    return "%" if value in {"％", "%"} else value


def _numeric_units(text: str) -> dict[str, set[str]]:
    result: dict[str, set[str]] = {}
    for match in _NUMBER_UNIT.finditer(text):
        result.setdefault(match.group(1), set()).add(_unit(match.group(2)))
    return result


def _number_directions(text: str) -> dict[tuple[str, str], set[str]]:
    facts: dict[tuple[str, str], set[str]] = {}
    for match in _DIRECTION_NUMBER.finditer(text):
        direction, number, unit = match.groups()
        kind = "UP" if direction in _POSITIVE else "DOWN"
        facts.setdefault((number, _unit(unit or "")), set()).add(kind)
    return facts


def _metric_direction(text: str, metric: str) -> set[str]:
    # A short local metric phrase can be matched without falsely asserting
    # every clause in the full source paragraph has one global direction.
    matched: set[str] = set()
    for m in re.finditer(re.escape(metric), text):
        trailing = text[m.end():m.end() + 24]
        trailing = re.split(r"[。；，,;]", trailing, maxsplit=1)[0]
        direction = re.search(
            r"(增长|上升|增加|提升|扩大|下降|下滑|减少|降低|收缩)",
            trailing,
        )
        if direction:
            matched.add("UP" if direction.group(1) in _POSITIVE else "DOWN")
    return matched


def reject_direct_fact_contradictions(claim: str, source_excerpt: str) -> None:
    """Fail closed only on unambiguous contradictions observable in both texts."""
    public, source = _clean(claim), _clean(source_excerpt)
    public_periods = _canonical_periods(public)
    source_periods = _canonical_periods(source)
    if public_periods and source_periods and not public_periods.issubset(source_periods):
        raise FinancialFactConflict("SOURCE_TRACE_CONFLICT_REPORTING_PERIOD")

    claimed_units, source_units = _numeric_units(public), _numeric_units(source)
    for number, units in claimed_units.items():
        observed = source_units.get(number, set())
        if observed and not units.issubset(observed):
            raise FinancialFactConflict(f"SOURCE_TRACE_CONFLICT_NUMERIC_UNIT:{number}")

    public_directions = _number_directions(public)
    source_directions = _number_directions(source)
    for pair, expected in public_directions.items():
        actual = source_directions.get(pair, set())
        if len(expected) == len(actual) == 1 and expected != actual:
            raise FinancialFactConflict(f"SOURCE_TRACE_CONFLICT_FINANCIAL_DIRECTION:{pair[0]}")

    for metric in _METRIC:
        if metric not in public or metric not in source:
            continue
        expected = _metric_direction(public, metric)
        actual = _metric_direction(source, metric)
        if len(expected) == len(actual) == 1 and expected != actual:
            raise FinancialFactConflict(f"SOURCE_TRACE_CONFLICT_METRIC_DIRECTION:{metric}")
