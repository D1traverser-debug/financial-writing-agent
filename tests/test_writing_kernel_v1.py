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
    validate_pass_dataflow,
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



def test_story_architecture_consumes_private_research_distillation_and_adjudicated_comparisons():
    architecture_inputs = set(
        PASS_CONTRACTS[WritingPass.STORY_ARCHITECTURE].required_inputs
    )
    assert {
        "publication_distillation",
        "company_decision_map",
        "change_conditions",
    } <= architecture_inputs
    assert "publication_distillation" in PASS_CONTRACTS[
        WritingPass.PRIVATE_RESEARCH_SYNTHESIS
    ].outputs
    assert {
        "company_decision_map", "change_conditions",
    } <= set(PASS_CONTRACTS[WritingPass.THESIS_ADJUDICATION].outputs)
    # _invoke_pass forwards exactly required_inputs, so these are real model inputs,
    # not merely data that happens to remain in the surrounding shared context.
    assert validate_kernel() == []



def test_fact_integrity_audit_receives_the_admitted_evidence_and_adjudicated_comparison():
    from financial_writing_agent.writing_kernel import _invoke_pass

    node = WritingPass.FACT_INTEGRITY_AUDIT
    required = set(PASS_CONTRACTS[node].required_inputs)
    expected = {
        "edited_draft",
        "evidence_ledger",
        "audited_evidence",
        "selected_thesis",
        "company_decision_map",
        "change_conditions",
        "publication_distillation",
        "product_mode",
    }
    assert required == expected
    assert validate_pass_dataflow() == []

    company_map = {
        "material_companies": ["甲公司", "乙公司"],
        "dimensions": [{
            "dimension": "经营现金流方向",
            "company_assessments": {
                "甲公司": "同比增长",
                "乙公司": "同比下降",
            },
            "evidence_refs": ["issuer-a-q3", "issuer-b-q3"],
        }],
    }
    audited_evidence = {
        "admission": "PASS",
        "evidence_refs": ["issuer-a-q3", "issuer-b-q3"],
        "source_snapshots": {"issuer-a-q3": "sha-a", "issuer-b-q3": "sha-b"},
    }
    current = {
        "edited_draft": "甲公司增长，乙公司下降。",
        "evidence_ledger": [{"claim": "两家公司现金流方向不同。"}],
        "audited_evidence": audited_evidence,
        "selected_thesis": {"statement": "同一行业下现金流兑现出现分化。"},
        "company_decision_map": company_map,
        "change_conditions": ["后续季度现金流方向反转"],
        "publication_distillation": {"core_comparison": "甲增乙降"},
        "product_mode": "FINANCE_DEEP",
    }
    observed = {}

    def execute_pass(actual_node, provided):
        assert actual_node == node
        observed.update(provided)
        return {"fact_findings": {"status": "REVISE", "evidence": ["公司方向对应需复核"]}}

    _invoke_pass(
        node,
        current,
        execute_pass=execute_pass,
        trace=[],
        scope="FINANCE_DEEP",
    )
    assert set(observed) == expected
    assert observed["audited_evidence"] == audited_evidence
    assert observed["company_decision_map"] == company_map
    assert observed["change_conditions"] == ["后续季度现金流方向反转"]


def test_platform_interaction_branches_preserve_the_same_company_decision_context():
    required_context = {
        "selected_thesis",
        "company_decision_map",
        "change_conditions",
        "publication_distillation",
        "audited_evidence",
    }
    for node in (
        WritingPass.PLATFORM_INTERACTION_ADAPTATION,
        WritingPass.PLATFORM_INTERACTION_AUDIT,
    ):
        assert required_context <= set(PASS_CONTRACTS[node].required_inputs)
    assert validate_pass_dataflow() == []


def test_execution_and_manifest_contracts_declare_fact_and_interaction_dataflow():
    root = Path(__file__).resolve().parents[1]
    execution = json.loads(
        (root / "config/EXECUTION_CONTRACT.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (root / "config/FINANCIAL_MANIFEST.json").read_text(encoding="utf-8")
    )
    fact_inputs = list(PASS_CONTRACTS[WritingPass.FACT_INTEGRITY_AUDIT].required_inputs)
    interaction_adaptation_inputs = list(
        PASS_CONTRACTS[WritingPass.PLATFORM_INTERACTION_ADAPTATION].required_inputs
    )
    interaction_audit_inputs = list(
        PASS_CONTRACTS[WritingPass.PLATFORM_INTERACTION_AUDIT].required_inputs
    )
    declared = execution["execution"]["fact_integrity_audit_dataflow"]
    assert declared["required_inputs"] == fact_inputs
    assert declared["missing_input_behavior"] == (
        "BLOCK_FACT_INTEGRITY_AUDIT_BEFORE_MODEL_CALLBACK"
    )
    interaction = execution["execution"]["platform_interaction_dataflow"]
    assert interaction["adaptation_required_inputs"] == interaction_adaptation_inputs
    assert interaction["audit_required_inputs"] == interaction_audit_inputs
    assert manifest["fact_integrity_audit_dataflow"] == declared
    assert manifest["platform_interaction_dataflow"] == interaction


def test_financial_skill_loads_the_authoritative_claim_attribution_audit():
    root = Path(__file__).resolve().parents[1]
    skill = (root / "skills/financial-writing-agent/SKILL.md").read_text(encoding="utf-8")
    audit = (
        root / "skills/financial-writing-agent/references/audit.md"
    ).read_text(encoding="utf-8")
    packaged_audit = (
        root / "financial_writing_agent/resources/references/audit.md"
    ).read_text(encoding="utf-8")

    assert "skills/financial-writing-agent/references/audit.md" in skill
    assert "company_decision_map" in skill
    assert "entity, metric, period, value/unit, direction" in skill
    assert "sentence order" in skill
    assert "semantic entailment" in skill
    assert audit == packaged_audit
    assert "check each company row independently" in audit
