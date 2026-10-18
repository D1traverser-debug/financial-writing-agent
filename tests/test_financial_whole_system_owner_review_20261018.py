"""Financial Writing owner review: source contract consistency and honest quality ceiling.

The review deliberately does not promote a new article quality standard or add
another current-task or evolution owner.
"""
import json
from pathlib import Path

from financial_writing_agent.current_admission import build_initial_state
from financial_writing_agent.private_research import (
    PRIVATE_RESEARCH_CONTRACT_VERSION,
    SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS,
)
from financial_writing_agent.quality_regression import evaluate_corpus_readiness

ROOT = Path(__file__).resolve().parents[1]


def _j(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_product_authority_matches_actual_private_research_default():
    requirements = (ROOT / "docs/product_requirements.md").read_text(encoding="utf-8")
    execution = _j("config/EXECUTION_CONTRACT.json")
    assert PRIVATE_RESEARCH_CONTRACT_VERSION == "1.1"
    assert "1.0" in SUPPORTED_PRIVATE_RESEARCH_CONTRACT_VERSIONS
    assert "`private_research_contract_version=1.1`" in requirements
    assert "`private_research_contract_version=1.0` by default" not in requirements
    assert execution["current_state_admission"]["new_task_entrypoint"] == (
        "financial_writing_agent.current_admission.build_initial_state"
    )


def test_review_does_not_relabel_greens_as_independent_editorial_quality():
    corpus = _j("evals/quality_regression.json")
    readiness = evaluate_corpus_readiness(corpus)
    report = (ROOT / "evals/FINANCIAL_WHOLE_SYSTEM_OWNER_REVIEW_20261018.md").read_text(encoding="utf-8")
    if readiness.status != "PROMOTION_READY":
        assert "LIVE END-TO-END PRODUCT ASSURANCE OPEN" in report
        assert "LIVE_CURRENT_QUALITY_AND_READER_VALUE_NOT_ADMITTED" in report
        assert "quality_regression.evaluate_corpus_readiness" in report
    assert len(corpus["cases"]) >= 2


def test_current_successor_is_not_conflated_with_historical_article_completion():
    v2 = _j("workspaces/articles/cross-border-ecommerce-20261016-v2/STATE.json")
    v3 = _j("workspaces/articles/cross-border-ecommerce-20261016-v3/STATE.json")
    assert v2["current_stage"] == "RESEARCH_AUDIT"
    assert v3["current_stage"] == "RESEARCH"
    assert v3["task_requirement_contract_version"] == "1.0"
    assert v3["task_requirement_authority"]["active_requirements"]
    assert not v3["delivery_artifacts"]
    assert v3["status"] == "IN_PROGRESS"


def test_assessment_keeps_single_article_owner_and_no_shadow_workflow():
    report = (ROOT / "evals/FINANCIAL_WHOLE_SYSTEM_OWNER_REVIEW_20261018.md").read_text(encoding="utf-8")
    assert "ONE Financial business/authority owner" in report
    assert "review dimensions" in report
    assert "not three replacement stage machines" in report
    assert not (ROOT / "state/TASK_INDEX.json").exists()
