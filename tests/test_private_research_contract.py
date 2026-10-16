from copy import deepcopy

import pytest

from financial_writing_agent.private_research import (
    PRIVATE_RESEARCH_CONTRACT_VERSION,
    REQUIRED_MODULES,
    PrivateResearchAdmissionError,
    validate_private_research_brief,
)


def _valid_brief() -> dict:
    return {
        "contract_version": PRIVATE_RESEARCH_CONTRACT_VERSION,
        "as_of": "2026-10-16T15:00:00+08:00",
        "coverage_state": "COMPLETE",
        "modules": {
            name: {
                "status": "APPLICABLE",
                "summary": f"{name} has substantive evidence",
                "evidence_refs": [f"evidence-{name}"],
            }
            for name in REQUIRED_MODULES
        },
        "unresolved_gaps": [],
    }


def test_valid_private_research_brief_is_admitted():
    brief = _valid_brief()
    assert validate_private_research_brief(brief) == brief


def test_missing_required_module_is_rejected():
    brief = _valid_brief()
    brief["modules"].pop("scenario_tree")
    with pytest.raises(PrivateResearchAdmissionError):
        validate_private_research_brief(brief)


def test_applicable_module_requires_evidence_refs():
    brief = _valid_brief()
    brief["modules"]["market_cap_and_liquidity"]["evidence_refs"] = []
    with pytest.raises(PrivateResearchAdmissionError):
        validate_private_research_brief(brief)


def test_not_material_requires_explicit_reason():
    brief = _valid_brief()
    module = brief["modules"]["short_horizon_role_map"]
    module["status"] = "NOT_MATERIAL"
    module["evidence_refs"] = []
    with pytest.raises(PrivateResearchAdmissionError):
        validate_private_research_brief(brief)

    module["reason"] = "market-price behavior is genuinely outside this macro-only task"
    assert validate_private_research_brief(brief)["modules"]["short_horizon_role_map"]["status"] == "NOT_MATERIAL"


def test_complete_cannot_hide_unresolved_gaps_and_bounded_requires_them():
    brief = _valid_brief()
    brief["unresolved_gaps"] = ["company disclosure not yet published"]
    with pytest.raises(PrivateResearchAdmissionError):
        validate_private_research_brief(brief)

    bounded = deepcopy(brief)
    bounded["coverage_state"] = "BOUNDED_WITH_GAPS"
    assert validate_private_research_brief(bounded)["unresolved_gaps"]

    bounded["unresolved_gaps"] = []
    with pytest.raises(PrivateResearchAdmissionError):
        validate_private_research_brief(bounded)
