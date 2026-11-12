"""Financial owner-native publication scope gate.

This does not replace a journalist, authenticated source readback or a reviewer.
It prevents a task-scoped publication requirement from disappearing between the
Article Aggregate, research universe, Word builder and visible delivery.
"""
from __future__ import annotations

import re
from typing import Any, Mapping

from .checks import check_deep_company_grounding, paragraph_has_named_economic_comparison, payload_text
from .company_identity import (CompanyIdentityError, canonical_company_name,
                               require_retained_universe_reconciliation)
from .current_admission import requirement_context_for_scope

# This is a supported *specific task invariant*, not a vocabulary of arbitrary
# user requests to silently infer from their English/Chinese phrasing.
FULL_UNIVERSE_REQUIREMENT = "deep_complete_retained_universe"
SCOPE_ASSURANCE = "STRUCTURAL_TASK_SCOPE_ONLY__FACTS_AND_EDITORIAL_NOT_INDEPENDENTLY_VERIFIED"
_WEAK_ROLE_EXPLANATION = re.compile(
    r"弱相关|弱关联|非核心|间接|概念标签|标签性|主营占比|证据有限|"
    r"兑现不足|尚未兑现|缺乏直接|暂无直接|关联较弱|缺少直接|被排除|不构成核心"
)


class TaskPublicationError(ValueError):
    """The owner's current task-scoped publication obligation was not established."""


def _field(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, Mapping):
        return value.get(key, default)
    return getattr(value, key, default)


def _passages(article: Any) -> list[str]:
    return [
        str(_field(block, "text", ""))
        for block in (_field(article, "blocks", []) or [])
        if _field(block, "kind") in {"lead", "body"}
    ]


def verify_task_publication_scope(
    state: Mapping[str, Any],
    article: Any,
    research: Any,
    *,
    product_mode: str = "FINANCE_DEEP",
) -> dict[str, Any]:
    """Inspect actual current task obligations and its proposed public article.

    Only explicitly implemented requirement IDs are automatically admitted;
    an unknown natural-language requirement is NOT silently called SATISFIED.
    The source facts, completeness of live market recall, and reader quality
    are outside this deterministic gate and must be checked separately.
    """
    if product_mode not in {"FINANCE_DEEP", "FINANCE_BROAD"}:
        raise TaskPublicationError(f"unsupported publication mode: {product_mode}")
    context = requirement_context_for_scope(state, product_mode)
    required_ids = {str(item["requirement_id"]) for item in context["requirements"]}
    if product_mode == "FINANCE_BROAD":
        if required_ids:
            raise TaskPublicationError(
                f"unimplemented FINANCE_BROAD task requirements cannot be silently passed: {sorted(required_ids)}"
            )
        return {
            "task_id": state["task_id"], "requirement_digest": context["digest"],
            "requirement_revision": context["revision"], "mode": product_mode,
            "validated_requirement_ids": [], "strict_universe_visibility": False,
            "company_names_checked": 0, "observed_stage": state["current_stage"],
            "assurance": SCOPE_ASSURANCE,
        }

    unknown = required_ids - {FULL_UNIVERSE_REQUIREMENT}
    if unknown:
        raise TaskPublicationError(f"unimplemented FINANCE_DEEP task requirements: {sorted(unknown)}")
    strict = FULL_UNIVERSE_REQUIREMENT in required_ids
    if research is None:
        raise TaskPublicationError("FINANCE_DEEP requires structured company research for scope validation")
    universe = _field(research, "universe")
    if not isinstance(universe, list):
        raise TaskPublicationError("research.universe must be a structured list")
    findings = list(check_deep_company_grounding(article, research))
    seen: set[str] = set()
    for item in universe:
        name = canonical_company_name(_field(item, "name", ""))
        if not name:
            findings.append("research.universe has unnamed retained company")
        elif name in seen:
            findings.append(f"duplicate retained company identity: {name}")
        seen.add(name)
    if strict:
        if not universe:
            findings.append("full-universe task cannot pass with empty retained universe")
        coverage = _field(research, "universe_coverage")
        if _field(coverage, "status") != "COMPLETE":
            findings.append("full-universe task requires research.universe_coverage.status=COMPLETE")
        classes = _field(coverage, "classes", []) or []
        if not classes:
            findings.append("full-universe task requires classified value-chain coverage")
        accounted: set[str] = set()
        for item in classes:
            accounted.update(canonical_company_name(name) for name in (_field(item, "included_companies", []) or []))
        unaccounted = seen - accounted
        if unaccounted:
            findings.append(f"retained companies have no included value-chain classification: {sorted(unaccounted)}")

        public_text = canonical_company_name(payload_text(article))
        missing = sorted(name for name in seen if name and name not in public_text)
        if missing:
            findings.append(f"FINANCE_DEEP silently omitted retained companies (including non-material): {missing}")

        passages = [canonical_company_name(passage) for passage in _passages(article)]
        for item in universe:
            name = canonical_company_name(_field(item, "name", ""))
            if name and _field(item, "materiality") in {"SECONDARY", "REFERENCE_ONLY", "NON_MATERIAL"}:
                if name in public_text and not any(
                    name in passage and _WEAK_ROLE_EXPLANATION.search(passage) for passage in passages
                ):
                    findings.append(f"weak/incidental retained company lacks visible explanation: {name}")

        by_class: dict[str, list[str]] = {}
        for item in universe:
            if _field(item, "materiality") == "MATERIAL":
                class_name = str(_field(item, "value_chain_class", "")).strip()
                if class_name:
                    by_class.setdefault(class_name, []).append(canonical_company_name(_field(item, "name", "")))
        for class_name, names in sorted(by_class.items()):
            if len(set(names)) < 2:
                continue
            if not any(
                paragraph_has_named_economic_comparison(passage, names)
                for passage in passages
            ):
                findings.append(
                    f"full-universe segment lacks named economic comparison: {class_name}"
                )
    baseline_receipt = None
    if strict:
        # The real current cross-border task has 174 immutable user-retained
        # historical tickers; a synthetically self-declared COMPLETE 3-name
        # research list must not bypass that actual owner obligation.
        try:
            baseline_receipt = require_retained_universe_reconciliation(str(state["task_id"]), research)
        except CompanyIdentityError as exc:
            findings.append(str(exc))
    if findings:
        raise TaskPublicationError("; ".join(dict.fromkeys(findings)))
    return {
        "task_id": state["task_id"],
        "requirement_digest": context["digest"],
        "requirement_revision": context["revision"],
        "mode": product_mode,
        "validated_requirement_ids": sorted(required_ids),
        "strict_universe_visibility": strict,
        "company_names_checked": len(seen) if strict else 0,
        "historical_universe_baseline": baseline_receipt,
        "observed_stage": state["current_stage"],
        "assurance": SCOPE_ASSURANCE,
    }
