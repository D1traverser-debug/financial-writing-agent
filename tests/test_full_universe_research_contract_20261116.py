import pytest

from financial_writing_agent.full_universe_research import (
    validate_full_universe_research_package,
)
from financial_writing_agent.portfolio_coordinator import (
    PortfolioCoordinatorError,
    _stage_payload,
)
from financial_writing_agent.schemas import ResearchPackage


SOURCE_A = "source://eastmoney/bk1115/2026-11-16"
SOURCE_B = "source://tonghuashun/cross-border/2026-11-16"
MATERIAL_NAMES = ("甲公司", "乙公司")


def _company(name, ticker, *, materiality="MATERIAL", source_refs=None):
    source_refs = source_refs or [SOURCE_A, SOURCE_B]
    if materiality == "MATERIAL":
        return {
            "name": name,
            "ticker": ticker,
            "value_chain_class": "DIRECT_SELLERS",
            "materiality": "MATERIAL",
            "relevance": "Direct cross-border seller exposure with a current operating channel.",
            "business_stage": "S4_OPERATING",
            "positive_evidence": ["Current operating revenue is disclosed."],
            "negative_evidence": ["Margin sensitivity remains exposed to platform fees."],
            "why_this": "The company has a direct seller channel and current financial realization.",
            "why_not": [],
            "exposure_type": "DIRECT_EARNINGS",
            "business_purity": "HIGH",
            "financial_realization_status": "REALIZED",
            "financial_realization_evidence": ["FY26 H1 filing reports current cross-border operating revenue."],
            "event_transmission_path": ["Platform fee change -> seller unit economics -> gross margin."],
            "reversal_conditions": ["Reclassify if cross-border revenue falls below materiality or the channel is discontinued."],
            "evidence_refs": list(source_refs),
            "benefit_path": ["Platform fee change -> seller unit economics."],
            "sensitivity_basis": ["Cross-border revenue share and platform fee exposure."],
            "realization_horizon": "FY26 H1 current operating period",
            "reversal_risks": ["Platform fee increases may compress margins."],
        }
    return {
        "name": name,
        "ticker": ticker,
        "value_chain_class": "WEAK_LABEL_ONLY",
        "materiality": "REFERENCE_ONLY",
        "relevance": "Retained only to preserve the complete source universe.",
        "business_stage": "S0_LABEL_ONLY",
        "positive_evidence": [],
        "negative_evidence": ["No separate cross-border revenue contribution is disclosed."],
        "why_this": "",
        "why_not": ["Only a concept-label association is supported; no direct operating or financial path is evidenced."],
        "exposure_type": "NARRATIVE_ONLY",
        "business_purity": "WEAK_OR_LABEL_ONLY",
        "financial_realization_status": "NOT_DISCLOSED",
        "financial_realization_evidence": ["The current filing does not disclose a separate material cross-border revenue contribution."],
        "event_transmission_path": ["No direct event-to-earnings path is currently evidenced; association remains label-level."],
        "reversal_conditions": ["Upgrade only after company disclosure demonstrates a material operating channel and revenue contribution."],
        "evidence_refs": list(source_refs),
        "benefit_path": [],
        "sensitivity_basis": [],
        "realization_horizon": "No current realization disclosed",
        "reversal_risks": ["The concept association may disappear without any change to reported earnings."],
    }


def _dimension(name, company_names):
    return {
        "dimension": name,
        "company_assessments": {
            company: f"{company} assessment for {name}."
            for company in company_names
        },
        "evidence_refs": [SOURCE_A, SOURCE_B],
        "why_it_changes_judgment": f"{name} distinguishes the companies on an economically relevant basis.",
    }


def _package():
    companies = [
        _company("甲公司", "300001"),
        _company("乙公司", "300002"),
        _company("丙公司", "300003", materiality="REFERENCE_ONLY", source_refs=[SOURCE_A]),
    ]
    material_names = list(MATERIAL_NAMES)
    segment_dimensions = [
        _dimension(name, material_names)
        for name in (
            "exposure_directness",
            "business_purity",
            "financial_realization",
            "event_transmission",
            "reversal_conditions",
        )
    ]
    global_dimensions = [
        _dimension("global_economic_strength", material_names),
        _dimension("global_financial_realization", material_names),
    ]
    classes = [
        {
            "class_name": "DIRECT_SELLERS",
            "economic_role": "Direct seller and brand-side cross-border operating exposure.",
            "relationships": ["Platform traffic and payment channels transmit to seller revenue and margin."],
            "source_refs": [SOURCE_A, SOURCE_B],
        },
        {
            "class_name": "WEAK_LABEL_ONLY",
            "economic_role": "Weak concept-label association without a demonstrated direct earnings path.",
            "relationships": ["No direct operating transmission is currently evidenced."],
            "source_refs": [SOURCE_A],
        },
    ]
    return {
        "topic": "Cross-border e-commerce full-universe research",
        "chronology": ["Current concept-source snapshots were retrieved and reconciled."],
        "what_changed": ["The retained universe was rechecked against two current source families."],
        "industry_chain": ["Traffic -> platform -> seller -> logistics/payment -> end customer."],
        "transmission_chain": ["Policy or platform change -> operating cost/revenue -> financial realization -> valuation."],
        "value_chain_coverage": {
            "status": "COMPLETE",
            "classes": classes,
            "transmission_paths": ["Platform rule -> seller unit economics -> earnings."],
            "excluded_or_unresolved_classes": [],
            "recall_sources": [SOURCE_A, SOURCE_B],
            "sufficiency_reason": "Two distinct current source families were reconciled before thesis selection.",
            "thesis_selection_started_after_preflight": True,
            "late_material_class_found": False,
        },
        "universe": companies,
        "universe_coverage": {
            "status": "COMPLETE",
            "as_of": "2026-11-16",
            "classes": [
                {
                    "class_name": "DIRECT_SELLERS",
                    "economic_role": "Direct seller and brand-side cross-border operating exposure.",
                    "included_companies": ["甲公司", "乙公司"],
                    "excluded_companies": [],
                    "unresolved_candidates": [],
                    "source_refs": [SOURCE_A, SOURCE_B],
                },
                {
                    "class_name": "WEAK_LABEL_ONLY",
                    "economic_role": "Weak concept-label association without a demonstrated direct earnings path.",
                    "included_companies": ["丙公司"],
                    "excluded_companies": [],
                    "unresolved_candidates": [],
                    "source_refs": [SOURCE_A],
                },
            ],
            "recall_sources": [SOURCE_A, SOURCE_B],
            "recall_source_families": ["EASTMONEY", "TONGHUASHUN"],
            "exclusions": [],
            "missing_classes": [],
            "stop_reason": "Two independent current concept-source families were reconciled and no material candidate changed the retained universe.",
        },
        "company_decision_map": {
            "material_companies": material_names,
            "dimensions": global_dimensions,
            "segment_comparisons": [
                {
                    "value_chain_class": "DIRECT_SELLERS",
                    "dimensions": segment_dimensions,
                    "current_comparative_verdict": "甲公司 has stronger current realization; 乙公司 has greater sensitivity to platform economics.",
                    "change_conditions": ["Revisit if either company discloses a material change in cross-border revenue share or unit economics."],
                }
            ],
            "current_comparative_verdict": "The direct seller segment has two materially different earnings and sensitivity profiles.",
            "strongest_current_evidence_for": ["Current filings and two-source universe reconciliation."],
            "weaker_or_later_evidence_for": ["The label-only company has no separately disclosed financial realization."],
            "change_conditions": ["Update when current filings or source constituents materially change."],
            "non_actionable_boundary": "This is an evidence-bounded comparison, not a trading recommendation.",
        },
        "market_explanation_scope": "NOT_MATERIAL",
        "market_explanation_scope_reason": "The task is a company-universe and earnings-transmission analysis; no market-wide price explanation is required.",
        "evidence_ledger": [
            {
                "claim": "Current cross-border concept constituent snapshot from provider A.",
                "source": SOURCE_A,
                "date": "2026-11-16",
                "evidence_type": "CONCEPT_SOURCE",
                "confidence": "high",
            },
            {
                "claim": "Current cross-border concept constituent snapshot from provider B.",
                "source": SOURCE_B,
                "date": "2026-11-16",
                "evidence_type": "CONCEPT_SOURCE",
                "confidence": "high",
            },
        ],
        "counterevidence": ["The label-only retained company has no direct disclosed revenue contribution."],
        "unresolved_gaps": [],
        "provisional_theses": ["Direct seller economics matter more than concept-label proximity."],
        "source_boundary": "All claims are bounded to the dated source ledger and current filings.",
        "cognition": {
            "prior_knowledge_refs": [],
            "concept_map": ["Cross-border sellers", "Platform economics", "Financial realization"],
            "adjacent_or_competing_concepts": ["Domestic e-commerce", "Overseas logistics"],
            "industry_logic": ["Direct exposure and financial realization determine economic materiality."],
            "short_term_market_structure": [],
            "knowledge_conflicts": [],
        },
        "coverage": {
            "sweeps_completed": 3,
            "coverage_status": "SATURATED",
            "material_new_items_last_sweep": 0,
            "consecutive_no_delta_sweeps": 2,
            "saturation_evidence_refs": [SOURCE_A, SOURCE_B],
            "concept_coverage": "Two current concept-source families reconciled.",
            "company_coverage": "Every retained company has a typed finding and dated evidence references.",
            "source_diversity": "EASTMONEY and TONGHUASHUN are distinct source families.",
            "excluded_scope": [],
            "stop_reason": "Two consecutive sweeps produced no decision-changing additions or counterexamples.",
        },
    }


def test_full_universe_contract_accepts_company_level_evidence_and_weak_explicit_cases():
    package = validate_full_universe_research_package(_package())
    assert len(package.universe) == 3
    assert package.universe[2].business_purity == "WEAK_OR_LABEL_ONLY"


def test_generic_research_package_remains_parseable_without_task_specific_full_universe_fields():
    payload = _package()
    payload["universe"][0]["business_purity"] = "UNRESOLVED"
    payload["universe"][0]["financial_realization_evidence"] = []
    payload["universe"][0]["event_transmission_path"] = []
    payload["universe"][0]["reversal_conditions"] = []
    payload["universe"][0]["evidence_refs"] = []
    payload["universe_coverage"]["recall_source_families"] = []
    payload["coverage"]["consecutive_no_delta_sweeps"] = 0
    payload["coverage"]["saturation_evidence_refs"] = []
    assert ResearchPackage.model_validate(payload)
    with pytest.raises(ValueError, match="FULL_UNIVERSE_COMPANY_FINANCIAL_REALIZATION_EVIDENCE_MISSING"):
        validate_full_universe_research_package(payload)


def test_full_universe_contract_rejects_missing_company_level_evidence():
    payload = _package()
    payload["universe"][0]["financial_realization_evidence"] = []
    with pytest.raises(ValueError, match="FULL_UNIVERSE_COMPANY_FINANCIAL_REALIZATION_EVIDENCE_MISSING"):
        validate_full_universe_research_package(payload)


def test_full_universe_contract_rejects_unlinked_company_evidence():
    payload = _package()
    payload["universe"][0]["evidence_refs"] = ["source://not-in-ledger"]
    with pytest.raises(ValueError, match="FULL_UNIVERSE_COMPANY_EVIDENCE_REF_NOT_IN_LEDGER"):
        validate_full_universe_research_package(payload)


def test_full_universe_contract_requires_unique_tickers():
    payload = _package()
    payload["universe"][1]["ticker"] = "300001"
    with pytest.raises(ValueError, match="FULL_UNIVERSE_COMPANY_TICKER_DUPLICATE"):
        validate_full_universe_research_package(payload)


def test_full_universe_contract_requires_two_distinct_current_source_families():
    payload = _package()
    payload["universe_coverage"]["recall_source_families"] = ["EASTMONEY", "EASTMONEY"]
    with pytest.raises(ValueError, match="FULL_UNIVERSE_RECALL_REQUIRES_TWO_DISTINCT_SOURCE_FAMILIES"):
        validate_full_universe_research_package(payload)


def test_full_universe_contract_requires_exact_company_class_accounting():
    payload = _package()
    payload["universe_coverage"]["classes"][0]["included_companies"].append("丁公司")
    with pytest.raises(ValueError, match="FULL_UNIVERSE_COMPANY_CLASS_ACCOUNTING_MISMATCH"):
        validate_full_universe_research_package(payload)


def test_full_universe_contract_requires_within_segment_comparison_on_all_required_axes():
    payload = _package()
    payload["company_decision_map"]["segment_comparisons"][0]["dimensions"][4]["dimension"] = "generic_risk"
    with pytest.raises(ValueError, match="FULL_UNIVERSE_SEGMENT_COMPARISON_DIMENSIONS_MISSING"):
        validate_full_universe_research_package(payload)


def test_full_universe_contract_requires_two_no_delta_sweeps_and_evidence():
    payload = _package()
    payload["coverage"]["consecutive_no_delta_sweeps"] = 1
    with pytest.raises(ValueError, match="FULL_UNIVERSE_RESEARCH_SATURATION_NOT_PROVEN"):
        validate_full_universe_research_package(payload)


def test_full_universe_contract_rejects_unresolved_purity_without_reason():
    payload = _package()
    payload["universe"][2]["why_not"] = []
    with pytest.raises(ValueError, match="FULL_UNIVERSE_WEAK_COMPANY_RATIONALE_MISSING"):
        validate_full_universe_research_package(payload)


def test_portfolio_coordinator_rejects_typed_but_incomplete_full_universe_package():
    payload = _package()
    payload["universe"][0]["event_transmission_path"] = []
    state = {
        "required_outputs": ["FINANCE_DEEP"],
        "task_requirement_authority": {
            "active_requirements": [
                {
                    "requirement_id": "full_universe_research_pool",
                    "statement": "Every retained company requires company-level evidence.",
                    "scopes": ["RESEARCH", "PRIVATE_RESEARCH"],
                    "affects_from_stage": "RESEARCH",
                    "source_kind": "USER_EXPLICIT",
                    "evidence_ref": "feedback/USER_REQUIREMENT_FULL_UNIVERSE_20261016.md",
                }
            ]
        },
    }
    context = {"last_stage_result": {"stage_outputs": {"research_package": payload}}}
    with pytest.raises(
        PortfolioCoordinatorError,
        match="PORTFOLIO_FULL_UNIVERSE_RESEARCH_EVIDENCE_CONTRACT_REQUIRED",
    ):
        _stage_payload(context, stage="RESEARCH", state=state)
