"""Stable company identity and historical task-retained universe checks.

A snapshot baseline is NOT a current market universe completeness certificate.
Failure must block silent omission; changing economic coverage requires fresh
source review, explicit task requirement revision and a new maintained baseline.
"""
from __future__ import annotations

import json
import re
import unicodedata
from importlib.resources import files
from typing import Any, Mapping

_NAME_SPACE = re.compile(r"\s+")


class CompanyIdentityError(ValueError):
    pass


def canonical_company_name(name: Any) -> str:
    value = unicodedata.normalize("NFKC", str(name))
    return _NAME_SPACE.sub("", value).strip()


def canonical_ticker(ticker: Any) -> str:
    if not isinstance(ticker, str) or not ticker.strip():
        raise CompanyIdentityError("COMPANY_TICKER_REQUIRED")
    value = unicodedata.normalize("NFKC", ticker).strip()
    if not re.fullmatch(r"(?:[0-9]{6})(?:\.(?:SH|SZ|BJ))?", value, flags=re.I):
        raise CompanyIdentityError("COMPANY_TICKER_INVALID")
    return value[:6]


def task_retained_universe_baseline(task_id: str) -> dict[str, Any] | None:
    raw = json.loads(
        files("financial_writing_agent").joinpath(
            "resources/task_universe_baselines.json"
        ).read_text(encoding="utf-8")
    )
    if raw.get("schema_version") != "1.0":
        raise CompanyIdentityError("TASK_UNIVERSE_BASELINE_SCHEMA_INVALID")
    if raw.get("task_id") != task_id:
        return None
    universe = raw.get("required_companies")
    if not isinstance(universe, list) or not universe:
        raise CompanyIdentityError("TASK_UNIVERSE_BASELINE_MISSING")
    codes = [canonical_ticker(company["ticker"]) for company in universe]
    if len(codes) != len(set(codes)):
        raise CompanyIdentityError("TASK_UNIVERSE_BASELINE_DUPLICATE_TICKER")
    return raw


def require_retained_universe_reconciliation(task_id: str, research: Any) -> dict[str, Any] | None:
    baseline = task_retained_universe_baseline(task_id)
    if baseline is None:
        return None
    expected = {
        canonical_ticker(item["ticker"]): canonical_company_name(item["name"])
        for item in baseline["required_companies"]
    }
    universe = getattr(research, "universe", None)
    if universe is None and isinstance(research, Mapping):
        universe = research.get("universe")
    if not isinstance(universe, list):
        raise CompanyIdentityError("TASK_UNIVERSE_RESEARCH_LIST_MISSING")
    actual: dict[str, str] = {}
    for item in universe:
        ticker = item.get("ticker") if isinstance(item, Mapping) else getattr(item, "ticker", None)
        name = item.get("name") if isinstance(item, Mapping) else getattr(item, "name", None)
        code = canonical_ticker(ticker)
        if code in actual:
            raise CompanyIdentityError(f"TASK_UNIVERSE_DUPLICATE_TICKER:{code}")
        canonical = canonical_company_name(name)
        if not canonical:
            raise CompanyIdentityError(f"TASK_UNIVERSE_NAME_MISSING:{code}")
        actual[code] = canonical
    missing = sorted(set(expected) - set(actual))
    if missing:
        raise CompanyIdentityError(f"TASK_RETAINED_UNIVERSE_TRUNCATED:{len(missing)}:{missing}")
    renamed = sorted(
        code for code in expected
        if code in actual and actual[code] != expected[code]
    )
    if renamed:
        raise CompanyIdentityError(f"TASK_RETAINED_UNIVERSE_IDENTITY_MISMATCH:{renamed}")
    return {
        "assurance": "HISTORICAL_TICKER_BASELINE_RECONCILED__CURRENT_MARKET_COMPLETENESS_NOT_VERIFIED",
        "baseline_as_of": baseline["snapshot_as_of"],
        "baseline_required_count": len(expected),
        "research_retained_count": len(actual),
        "baseline_source": baseline["source"],
    }
