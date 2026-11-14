from __future__ import annotations

import json
from pathlib import Path

from financial_writing_agent.writing_kernel import (
    INTERACTION_PRODUCT_PASSES,
    LONGFORM_PRODUCT_PASSES,
    PASS_CONTRACTS,
    PASS_DEPENDENCIES,
    PASS_STAGE_OWNERSHIP,
    SHARED_RESEARCH_PASSES,
    WritingPass,
    validate_kernel,
)


def test_kernel_is_acyclic_complete_and_has_one_stage_owner_per_pass():
    assert validate_kernel() == []
    assert set(PASS_CONTRACTS) == set(PASS_DEPENDENCIES)
    assert set(PASS_STAGE_OWNERSHIP) == set(PASS_CONTRACTS)
    assert len(PASS_CONTRACTS) == 16


def test_draft_is_not_allowed_to_self_certify_or_change_thesis():
    forbidden = PASS_CONTRACTS[WritingPass.DRAFT_GENERATION].forbidden_jobs
    assert "self-certify quality" in forbidden
    assert "change governing thesis without returning upstream" in forbidden


def test_longform_review_keeps_retention_originality_fact_and_style_separate():
    final_deps = set(PASS_DEPENDENCIES[WritingPass.FINAL_SYNTHESIS])
    assert WritingPass.READER_RETENTION_AUDIT in final_deps
    assert WritingPass.ORIGINALITY_AUDIT in final_deps
    assert WritingPass.FACT_INTEGRITY_AUDIT in final_deps
    assert WritingPass.STYLE_AUDIT in final_deps


def test_research_adversarial_and_private_synthesis_precede_thesis_selection():
    assert WritingPass.RESEARCH_ADVERSARIAL in PASS_DEPENDENCIES[WritingPass.THESIS_ADJUDICATION]
    assert WritingPass.PRIVATE_RESEARCH_SYNTHESIS in PASS_DEPENDENCIES[WritingPass.THESIS_ADJUDICATION]


def test_headline_is_an_explicit_product_scoped_pass_between_editorial_and_draft():
    assert WritingPass.HEADLINE_ADJUDICATION in PASS_CONTRACTS
    assert WritingPass.HEADLINE_ADJUDICATION in PASS_DEPENDENCIES[WritingPass.DRAFT_GENERATION]
    assert PASS_STAGE_OWNERSHIP[WritingPass.HEADLINE_ADJUDICATION] == "TITLE"
    assert "product_mode" in PASS_CONTRACTS[WritingPass.HEADLINE_ADJUDICATION].required_inputs


def test_deep_and_broad_are_two_branches_after_one_shared_research_spine():
    assert len(SHARED_RESEARCH_PASSES) == 5
    assert len(LONGFORM_PRODUCT_PASSES) == 9
    assert WritingPass.STORY_ARCHITECTURE in LONGFORM_PRODUCT_PASSES
    assert WritingPass.HEADLINE_ADJUDICATION in LONGFORM_PRODUCT_PASSES
    assert WritingPass.FINAL_SYNTHESIS in LONGFORM_PRODUCT_PASSES
    assert not (set(SHARED_RESEARCH_PASSES) & set(LONGFORM_PRODUCT_PASSES))


def test_interaction_product_is_independently_adapted_and_audited():
    assert INTERACTION_PRODUCT_PASSES == (
        WritingPass.PLATFORM_INTERACTION_ADAPTATION,
        WritingPass.PLATFORM_INTERACTION_AUDIT,
    )
    assert PASS_STAGE_OWNERSHIP[WritingPass.PLATFORM_INTERACTION_ADAPTATION] == "DRAFT"
    assert PASS_STAGE_OWNERSHIP[WritingPass.PLATFORM_INTERACTION_AUDIT] == "EDITORIAL_AUDIT"
    forbidden = PASS_CONTRACTS[WritingPass.PLATFORM_INTERACTION_ADAPTATION].forbidden_jobs
    assert "truncate or paraphrase a long-form article as the interaction product" in forbidden


def test_private_research_synthesis_is_a_real_graph_dependency_not_only_documented():
    from financial_writing_agent.private_research import PRIVATE_RESEARCH_CONTRACT_VERSION

    assert PRIVATE_RESEARCH_CONTRACT_VERSION == "1.1"
    synthesis = WritingPass.PRIVATE_RESEARCH_SYNTHESIS
    thesis = WritingPass.THESIS_ADJUDICATION
    assert synthesis in PASS_CONTRACTS
    assert WritingPass.RESEARCH_ADVERSARIAL in PASS_DEPENDENCIES[synthesis]
    assert synthesis in PASS_DEPENDENCIES[thesis]
    assert "publication_distillation" in PASS_CONTRACTS[synthesis].outputs
    assert "draft publication prose" in PASS_CONTRACTS[synthesis].forbidden_jobs
    assert validate_kernel() == []


def test_domain_execution_contract_matches_real_writing_kernel_graph():
    contract = json.loads(
        (Path(__file__).resolve().parents[1] / "config/EXECUTION_CONTRACT.json")
        .read_text(encoding="utf-8")
    )
    declared = [WritingPass(x) for x in contract["internal_passes"]]
    assert set(declared) == set(PASS_CONTRACTS) == set(PASS_DEPENDENCIES)
    assert declared.index(WritingPass.RESEARCH_ADVERSARIAL) < declared.index(
        WritingPass.PRIVATE_RESEARCH_SYNTHESIS
    ) < declared.index(WritingPass.THESIS_ADJUDICATION)
    assert contract["execution"]["portfolio_pass_orchestrator"] == (
        "financial_writing_agent.writing_kernel.execute_portfolio_stage"
    )
    assert contract["execution"]["portfolio_in_memory_replay_helper"] == (
        "financial_writing_agent.writing_kernel.execute_portfolio_writing"
    )
    assert contract["execution"]["portfolio_stage_sequence"] == [
        "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT",
        "EDITORIAL_AUDIT",
    ]
    assert contract["execution"]["in_memory_replay_is_production_execution"] is False


def test_production_execution_is_resumable_one_owner_stage_per_call():
    from financial_writing_agent.writing_kernel import (
        INTERNAL_PORTFOLIO_STAGE_SEQUENCE,
        execute_portfolio_stage,
        start_portfolio_context,
    )

    assert INTERNAL_PORTFOLIO_STAGE_SEQUENCE == (
        "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT",
        "EDITORIAL_AUDIT",
    )
    assert callable(start_portfolio_context)
    assert callable(execute_portfolio_stage)
