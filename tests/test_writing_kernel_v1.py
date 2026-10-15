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
