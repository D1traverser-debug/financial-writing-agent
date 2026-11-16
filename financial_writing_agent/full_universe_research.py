"""Strict task-scoped evidence contract for explicitly requested full-universe research."""

from __future__ import annotations

import re
from collections import defaultdict
from typing import Any

from .company_identity import canonical_company_name, canonical_ticker
from .schemas import CompanyDecisionMap, ResearchPackage


REQUIRED_SEGMENT_COMPARISON_DIMENSIONS = frozenset({
    "exposure_directness",
    "business_purity",
    "financial_realization",
    "event_transmission",
    "reversal_conditions",
})


def validate_full_universe_research_package(raw: Any) -> ResearchPackage:
    """Validate a full-universe package beyond the generic ResearchPackage shape.

    This stricter contract is invoked only when the owner has admitted an explicit
    full-universe task requirement. Ordinary Financial tasks retain the generic
    ResearchPackage contract and are not forced into exhaustive-universe research.
    """
    try:
        package = ResearchPackage.model_validate(raw)
    except Exception as exc:
        raise ValueError(f"FULL_UNIVERSE_RESEARCH_PACKAGE_SCHEMA_INVALID: {exc}") from exc

    if not package.universe:
        raise ValueError("FULL_UNIVERSE_RESEARCH_UNIVERSE_EMPTY")
    if package.universe_coverage.status != "COMPLETE":
        raise ValueError("FULL_UNIVERSE_RESEARCH_COVERAGE_NOT_COMPLETE")
    if package.value_chain_coverage.status != "COMPLETE":
        raise ValueError("FULL_UNIVERSE_VALUE_CHAIN_COVERAGE_NOT_COMPLETE")

    as_of = str(package.universe_coverage.as_of or "").strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of) is None:
        raise ValueError("FULL_UNIVERSE_RESEARCH_AS_OF_REQUIRED")

    recall_sources = [str(item).strip() for item in package.universe_coverage.recall_sources]
    recall_families = [
        str(item).strip().casefold()
        for item in package.universe_coverage.recall_source_families
    ]
    if (
        len(recall_sources) < 2
        or len(recall_sources) != len(set(recall_sources))
        or len(recall_families) != len(recall_sources)
        or any(not item for item in recall_families)
        or len(set(recall_families)) < 2
    ):
        raise ValueError("FULL_UNIVERSE_RECALL_REQUIRES_TWO_DISTINCT_SOURCE_FAMILIES")

    evidence_by_source: dict[str, list[Any]] = defaultdict(list)
    for item in package.evidence_ledger:
        source = str(item.source or "").strip()
        if source:
            evidence_by_source[source].append(item)

    def require_dated_source(ref: str, code: str) -> None:
        entries = evidence_by_source.get(str(ref).strip(), [])
        if not entries:
            raise ValueError(f"{code}: {ref}")
        if not any(str(item.date or "").strip() for item in entries):
            raise ValueError(f"FULL_UNIVERSE_EVIDENCE_DATE_MISSING: {ref}")

    def require_nonempty_items(values: Any, code: str, identity: str) -> None:
        items = [str(item).strip() for item in values]
        if not items or any(not item for item in items):
            raise ValueError(f"{code}: {identity}")

    value_chain_recall_sources = [
        str(item).strip() for item in package.value_chain_coverage.recall_sources
    ]
    if (
        len(value_chain_recall_sources) < 2
        or len(value_chain_recall_sources) != len(set(value_chain_recall_sources))
    ):
        raise ValueError("FULL_UNIVERSE_VALUE_CHAIN_RECALL_SOURCES_NOT_DISTINCT")

    for ref in recall_sources:
        require_dated_source(ref, "FULL_UNIVERSE_RECALL_SOURCE_NOT_IN_EVIDENCE_LEDGER")
    for ref in package.value_chain_coverage.recall_sources:
        require_dated_source(ref, "FULL_UNIVERSE_VALUE_CHAIN_RECALL_SOURCE_NOT_IN_EVIDENCE_LEDGER")
    for value_class in package.value_chain_coverage.classes:
        for ref in value_class.source_refs:
            require_dated_source(ref, "FULL_UNIVERSE_VALUE_CHAIN_CLASS_SOURCE_NOT_IN_EVIDENCE_LEDGER")
    for value_class in package.universe_coverage.classes:
        for ref in value_class.source_refs:
            require_dated_source(ref, "FULL_UNIVERSE_COMPANY_CLASS_SOURCE_NOT_IN_EVIDENCE_LEDGER")

    universe_class_names = [
        str(item.class_name).strip() for item in package.universe_coverage.classes
    ]
    chain_class_names = [
        str(item.class_name).strip() for item in package.value_chain_coverage.classes
    ]
    if (
        len(universe_class_names) != len(set(universe_class_names))
        or len(chain_class_names) != len(set(chain_class_names))
        or set(universe_class_names) != set(chain_class_names)
    ):
        raise ValueError("FULL_UNIVERSE_VALUE_CHAIN_AND_COMPANY_CLASS_SETS_MISMATCH")

    excluded_by_class: dict[str, set[str]] = defaultdict(set)
    for value_class in package.universe_coverage.classes:
        included = set(value_class.included_companies)
        excluded = set(value_class.excluded_companies)
        unresolved = set(value_class.unresolved_candidates)
        if included & excluded or included & unresolved or excluded & unresolved:
            raise ValueError("FULL_UNIVERSE_CLASS_ACCOUNTING_CATEGORIES_OVERLAP")
        if unresolved:
            raise ValueError("FULL_UNIVERSE_COMPLETE_COVERAGE_HAS_UNRESOLVED_CANDIDATES")
        excluded_by_class[str(value_class.class_name).strip()] = excluded

    exclusion_records = {
        canonical_company_name(item.name): item
        for item in package.universe_coverage.exclusions
    }
    excluded_names = {
        name for names_in_class in excluded_by_class.values() for name in names_in_class
    }
    if set(exclusion_records) != excluded_names:
        raise ValueError("FULL_UNIVERSE_EXCLUSION_RECORDS_DO_NOT_MATCH_CLASS_LEDGER")
    for class_name, names_in_class in excluded_by_class.items():
        for name in names_in_class:
            record = exclusion_records[name]
            if str(record.value_chain_class).strip() != class_name:
                raise ValueError(f"FULL_UNIVERSE_EXCLUSION_CLASS_MISMATCH: {name}")
            require_nonempty_items(
                record.evidence_refs, "FULL_UNIVERSE_EXCLUSION_EVIDENCE_REFS_MISSING", name
            )
            for ref in record.evidence_refs:
                require_dated_source(ref, "FULL_UNIVERSE_EXCLUSION_EVIDENCE_NOT_IN_LEDGER")

    names: set[str] = set()
    tickers: set[str] = set()
    material_by_class: dict[str, set[str]] = defaultdict(set)
    for company in package.universe:
        name = canonical_company_name(company.name)
        if not name:
            raise ValueError("FULL_UNIVERSE_COMPANY_NAME_REQUIRED")
        names.add(name)

        if not company.ticker:
            raise ValueError(f"FULL_UNIVERSE_COMPANY_TICKER_REQUIRED: {name}")
        try:
            ticker = canonical_ticker(company.ticker)
        except Exception as exc:
            raise ValueError(f"FULL_UNIVERSE_COMPANY_TICKER_INVALID: {name}") from exc
        if not ticker:
            raise ValueError(f"FULL_UNIVERSE_COMPANY_TICKER_REQUIRED: {name}")
        if ticker in tickers:
            raise ValueError(f"FULL_UNIVERSE_COMPANY_TICKER_DUPLICATE: {ticker}")
        tickers.add(ticker)

        if not str(company.business_stage or "").strip():
            raise ValueError(f"FULL_UNIVERSE_COMPANY_BUSINESS_STAGE_MISSING: {ticker}")
        if not str(company.realization_horizon or "").strip():
            raise ValueError(f"FULL_UNIVERSE_COMPANY_REALIZATION_HORIZON_MISSING: {ticker}")
        require_nonempty_items(
            company.financial_realization_evidence,
            "FULL_UNIVERSE_COMPANY_FINANCIAL_REALIZATION_EVIDENCE_MISSING",
            ticker,
        )
        require_nonempty_items(
            company.event_transmission_path,
            "FULL_UNIVERSE_COMPANY_EVENT_TRANSMISSION_PATH_MISSING",
            ticker,
        )
        require_nonempty_items(
            company.reversal_conditions,
            "FULL_UNIVERSE_COMPANY_REVERSAL_CONDITIONS_MISSING",
            ticker,
        )

        if company.materiality == "MATERIAL" and not str(company.why_this or "").strip():
            raise ValueError(f"FULL_UNIVERSE_MATERIAL_COMPANY_RATIONALE_MISSING: {ticker}")
        if company.materiality in {"SECONDARY", "REFERENCE_ONLY"} and (
            not company.why_not or any(not str(item).strip() for item in company.why_not)
        ):
            raise ValueError(f"FULL_UNIVERSE_WEAK_COMPANY_RATIONALE_MISSING: {ticker}")
        if company.business_purity in {"WEAK_OR_LABEL_ONLY", "UNRESOLVED"} and (
            not company.why_not or any(not str(item).strip() for item in company.why_not)
        ):
            raise ValueError(f"FULL_UNIVERSE_COMPANY_PURITY_UNRESOLVED_WITHOUT_REASON: {ticker}")
        if company.financial_realization_status in {
            "NOT_DISCLOSED", "NO_MATERIAL_REALIZATION", "UNRESOLVED",
        } and (
            not company.why_not or any(not str(item).strip() for item in company.why_not)
        ):
            raise ValueError(f"FULL_UNIVERSE_COMPANY_REALIZATION_UNRESOLVED_WITHOUT_REASON: {ticker}")
        if company.exposure_type in {"NARRATIVE_ONLY", "UNCLEAR"} and (
            not company.why_not or any(not str(item).strip() for item in company.why_not)
        ):
            raise ValueError(f"FULL_UNIVERSE_COMPANY_EXPOSURE_UNRESOLVED_WITHOUT_REASON: {ticker}")

        refs = [str(item).strip() for item in company.evidence_refs]
        if len(refs) != len(set(refs)) or any(not item for item in refs):
            raise ValueError(f"FULL_UNIVERSE_COMPANY_EVIDENCE_REFS_INVALID: {ticker}")
        minimum_refs = 2 if company.materiality == "MATERIAL" else 1
        if len(refs) < minimum_refs:
            raise ValueError(f"FULL_UNIVERSE_COMPANY_EVIDENCE_REFS_INSUFFICIENT: {ticker}")
        for ref in refs:
            require_dated_source(ref, f"FULL_UNIVERSE_COMPANY_EVIDENCE_REF_NOT_IN_LEDGER:{ticker}")

        if company.materiality == "MATERIAL":
            material_by_class[str(company.value_chain_class).strip()].add(name)

    included_list = [
        canonical_company_name(name)
        for item in package.universe_coverage.classes
        for name in item.included_companies
    ]
    if len(included_list) != len(set(included_list)):
        raise ValueError("FULL_UNIVERSE_COMPANY_INCLUDED_IN_MULTIPLE_CLASSES")
    if set(included_list) != names:
        missing = sorted(names - set(included_list))
        extra = sorted(set(included_list) - names)
        raise ValueError(
            f"FULL_UNIVERSE_COMPANY_CLASS_ACCOUNTING_MISMATCH: missing={missing}; extra={extra}"
        )

    declared_chain_classes = {
        str(item.class_name).strip() for item in package.value_chain_coverage.classes
    }
    if not {str(item.value_chain_class).strip() for item in package.universe} <= declared_chain_classes:
        raise ValueError("FULL_UNIVERSE_COMPANY_CLASS_MISSING_FROM_VALUE_CHAIN_PREFLIGHT")

    coverage = package.coverage
    if (
        coverage.coverage_status != "SATURATED"
        or coverage.material_new_items_last_sweep != 0
        or coverage.consecutive_no_delta_sweeps < 2
        or coverage.sweeps_completed < coverage.consecutive_no_delta_sweeps
    ):
        raise ValueError("FULL_UNIVERSE_RESEARCH_SATURATION_NOT_PROVEN")
    saturation_refs = [str(item).strip() for item in coverage.saturation_evidence_refs]
    if len(saturation_refs) < 2 or len(saturation_refs) != len(set(saturation_refs)):
        raise ValueError("FULL_UNIVERSE_SATURATION_EVIDENCE_REFS_INSUFFICIENT")
    for ref in saturation_refs:
        require_dated_source(ref, "FULL_UNIVERSE_SATURATION_EVIDENCE_REF_NOT_IN_LEDGER")

    material_names = {
        canonical_company_name(company.name)
        for company in package.universe
        if company.materiality == "MATERIAL"
    }
    decision_map = package.company_decision_map
    if len(material_names) >= 2 and decision_map is None:
        raise ValueError("FULL_UNIVERSE_COMPANY_DECISION_MAP_REQUIRED")
    if decision_map is not None:
        for dimension in decision_map.dimensions:
            if any(not str(value).strip() for value in dimension.company_assessments.values()):
                raise ValueError("FULL_UNIVERSE_GLOBAL_COMPARISON_ASSESSMENT_EMPTY")
            for ref in dimension.evidence_refs:
                require_dated_source(ref, "FULL_UNIVERSE_GLOBAL_COMPARISON_EVIDENCE_NOT_IN_LEDGER")

        expected_segment_classes = {
            class_name for class_name, companies in material_by_class.items()
            if len(companies) >= 2
        }
        segment_map = {
            str(item.value_chain_class).strip(): item
            for item in decision_map.segment_comparisons
        }
        if set(segment_map) != expected_segment_classes:
            missing = sorted(expected_segment_classes - set(segment_map))
            extra = sorted(set(segment_map) - expected_segment_classes)
            raise ValueError(
                f"FULL_UNIVERSE_SEGMENT_COMPARISON_CLASS_SET_MISMATCH: missing={missing}; extra={extra}"
            )
        for class_name, expected_companies in material_by_class.items():
            if len(expected_companies) < 2:
                continue
            comparison = segment_map[class_name]
            dimensions = {item.dimension.strip(): item for item in comparison.dimensions}
            if not REQUIRED_SEGMENT_COMPARISON_DIMENSIONS <= set(dimensions):
                missing = sorted(REQUIRED_SEGMENT_COMPARISON_DIMENSIONS - set(dimensions))
                raise ValueError(
                    f"FULL_UNIVERSE_SEGMENT_COMPARISON_DIMENSIONS_MISSING:{class_name}:{missing}"
                )
            for dimension_name in REQUIRED_SEGMENT_COMPARISON_DIMENSIONS:
                dimension = dimensions[dimension_name]
                if set(dimension.company_assessments) != expected_companies:
                    raise ValueError(
                        f"FULL_UNIVERSE_SEGMENT_COMPARISON_COMPANY_SET_MISMATCH:{class_name}:{dimension_name}"
                    )
                if any(not str(value).strip() for value in dimension.company_assessments.values()):
                    raise ValueError(
                        f"FULL_UNIVERSE_SEGMENT_COMPARISON_ASSESSMENT_EMPTY:{class_name}:{dimension_name}"
                    )
                for ref in dimension.evidence_refs:
                    require_dated_source(ref, "FULL_UNIVERSE_SEGMENT_COMPARISON_EVIDENCE_NOT_IN_LEDGER")

    return package



def validate_full_universe_decision_handoff(
    raw_research_package: Any,
    raw_company_decision_map: Any,
    raw_change_conditions: Any,
) -> ResearchPackage:
    """Bind the actual Story Architecture inputs to the validated research map.

    The package's company map is the evidence-bearing authority. Thesis
    adjudication also emits a top-level map and change-condition list that are
    passed to Story Architecture. For full-universe tasks those values must be
    the same decision, not two independently mutable representations.
    """
    package = validate_full_universe_research_package(raw_research_package)
    package_map = package.company_decision_map
    if package_map is None:
        raise ValueError("FULL_UNIVERSE_COMPANY_DECISION_MAP_REQUIRED")
    try:
        handoff_map = CompanyDecisionMap.model_validate(raw_company_decision_map)
    except Exception as exc:
        raise ValueError(
            f"FULL_UNIVERSE_TOP_LEVEL_COMPANY_DECISION_MAP_INVALID: {exc}"
        ) from exc
    if handoff_map.model_dump(mode="json") != package_map.model_dump(mode="json"):
        raise ValueError(
            "FULL_UNIVERSE_TOP_LEVEL_COMPANY_DECISION_MAP_DIVERGED_FROM_RESEARCH_PACKAGE"
        )

    if not isinstance(raw_change_conditions, list):
        raise ValueError("FULL_UNIVERSE_TOP_LEVEL_CHANGE_CONDITIONS_INVALID")
    handoff_conditions = [
        item.strip() if isinstance(item, str) else ""
        for item in raw_change_conditions
    ]
    package_conditions = [item.strip() for item in package_map.change_conditions]
    if (
        not handoff_conditions
        or any(not item for item in handoff_conditions)
        or handoff_conditions != package_conditions
    ):
        raise ValueError(
            "FULL_UNIVERSE_TOP_LEVEL_CHANGE_CONDITIONS_DIVERGED_FROM_RESEARCH_PACKAGE"
        )
    return package
