import pytest
from pydantic import ValidationError

from financial_writing_agent.schemas import AuditProvenance, GateDecision


def test_chat_self_review_can_issue_route_level_pass():
    decision = GateDecision(
        status="PASS",
        evidence=["frozen artifact reviewed against the applicable rubric"],
        provenance=AuditProvenance(
            assurance="CHAT_SELF_REVIEW",
            reviewer_identity="chat-self",
            author_identity="chat-self",
        ),
        remaining_boundaries=["independent certification remains open"],
    )

    assert decision.status == "PASS"
    assert decision.provenance.assurance == "CHAT_SELF_REVIEW"
    assert "independent certification remains open" in decision.remaining_boundaries


def test_independent_executor_claim_requires_execution_reference():
    with pytest.raises(ValidationError, match="independent audit requires execution_ref"):
        AuditProvenance(
            assurance="INDEPENDENT_EXECUTOR",
            reviewer_identity="reviewer-2",
            author_identity="author-1",
            execution_ref="",
        )


def test_independent_executor_claim_requires_distinct_reviewer_identity():
    with pytest.raises(ValidationError, match="reviewer_identity must differ from author_identity"):
        AuditProvenance(
            assurance="INDEPENDENT_EXECUTOR",
            reviewer_identity="same-actor",
            author_identity="same-actor",
            execution_ref="trace://review/123",
        )


def test_independent_executor_claim_is_valid_with_distinct_evidenced_provenance():
    provenance = AuditProvenance(
        assurance="INDEPENDENT_EXECUTOR",
        reviewer_identity="reviewer-2",
        author_identity="author-1",
        execution_ref="trace://review/123",
    )

    assert provenance.assurance == "INDEPENDENT_EXECUTOR"
    assert provenance.execution_ref == "trace://review/123"
