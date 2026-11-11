from financial_writing_agent.writing_kernel import (
    PASS_CONTRACTS,
    PASS_DEPENDENCIES,
    WritingPass,
    validate_kernel,
)


def test_kernel_is_acyclic_and_complete():
    assert validate_kernel() == []
    assert set(PASS_CONTRACTS) == set(PASS_DEPENDENCIES)


def test_draft_is_not_allowed_to_self_certify_or_change_thesis():
    forbidden = PASS_CONTRACTS[WritingPass.DRAFT_GENERATION].forbidden_jobs
    assert "self-certify quality" in forbidden
    assert "change governing thesis without returning upstream" in forbidden


def test_retention_originality_fact_and_style_are_separate_review_passes():
    final_deps = set(PASS_DEPENDENCIES[WritingPass.FINAL_SYNTHESIS])
    assert WritingPass.READER_RETENTION_AUDIT in final_deps
    assert WritingPass.ORIGINALITY_AUDIT in final_deps
    assert WritingPass.FACT_INTEGRITY_AUDIT in final_deps
    assert WritingPass.STYLE_AUDIT in final_deps


def test_research_adversarial_must_precede_thesis_selection():
    assert WritingPass.RESEARCH_ADVERSARIAL in PASS_DEPENDENCIES[WritingPass.THESIS_ADJUDICATION]


def test_private_research_synthesis_is_a_real_graph_dependency_not_only_documented():
    """A publishable thesis must consume adversarial evidence plus the actual brief."""
    from financial_writing_agent.private_research import PRIVATE_RESEARCH_CONTRACT_VERSION
    assert PRIVATE_RESEARCH_CONTRACT_VERSION == "1.1"
    synthesis = WritingPass.PRIVATE_RESEARCH_SYNTHESIS
    thesis = WritingPass.THESIS_ADJUDICATION
    assert synthesis in PASS_CONTRACTS
    assert WritingPass.RESEARCH_ADVERSARIAL in PASS_DEPENDENCIES[synthesis]
    assert synthesis in PASS_DEPENDENCIES[thesis]
    assert "private_research_brief" in PASS_CONTRACTS[thesis].required_inputs
    assert "publication_distillation" in PASS_CONTRACTS[synthesis].outputs
    assert "draft publication prose" in PASS_CONTRACTS[synthesis].forbidden_jobs
    assert validate_kernel() == []


def test_domain_execution_contract_matches_real_writing_kernel_graph():
    import json
    from pathlib import Path
    contract = json.loads(
        (Path(__file__).resolve().parents[1] / "config/EXECUTION_CONTRACT.json")
        .read_text(encoding="utf-8")
    )
    declared = [WritingPass(x) for x in contract["internal_passes"]]
    assert set(declared) == set(PASS_CONTRACTS) == set(PASS_DEPENDENCIES)
    assert declared.index(WritingPass.RESEARCH_ADVERSARIAL) < declared.index(
        WritingPass.PRIVATE_RESEARCH_SYNTHESIS
    ) < declared.index(WritingPass.THESIS_ADJUDICATION)
