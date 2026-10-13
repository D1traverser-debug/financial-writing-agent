import pytest

from financial_writing_agent.owner_guard import (
    GithubChatGuardError,
    advance_state,
    attach_material_feedback,
    build_initial_state,
)
from financial_writing_agent.owner_lifecycle import (
    OWNER_CLOSURE_ATTESTATION,
    block_review_failure_state,
    resume_blocked_state,
    review_system_impact_state,
)


def _initial():
    return build_initial_state(
        task_id="owner-lifecycle-task",
        prompt="write a test article",
        source_refs=["source://one"],
        executor_identity="chat-session:test",
    )


def _to_research_audit():
    state = _initial()
    state = advance_state(state, previous_state_blob_sha="s0", executor_identity="chat-session:test")
    return advance_state(
        state,
        previous_state_blob_sha="s1",
        executor_identity="chat-session:test",
        artifact_key="RESEARCH",
        artifact_path="workspaces/articles/owner-lifecycle-task/stages/RESEARCH.json",
        artifact_blob_sha="research-blob",
    )


def _blocked_research_audit():
    return block_review_failure_state(
        _to_research_audit(),
        previous_state_blob_sha="s2",
        executor_identity="chat-session:test",
        artifact_key="RESEARCH_AUDIT",
        artifact_path="workspaces/articles/owner-lifecycle-task/reviews/RESEARCH_AUDIT.json",
        artifact_blob_sha="audit-fail-blob",
        revision_target="RESEARCH",
    )


def test_review_fail_persists_canonical_recovery_cursor():
    blocked = _blocked_research_audit()
    assert blocked["status"] == "BLOCKED"
    assert blocked["current_stage"] == "RESEARCH_AUDIT"
    assert blocked["review_decisions"]["RESEARCH_AUDIT"]["status"] == "FAIL"
    assert blocked["execution_receipts"][-1]["input_bindings"]["revision_target"] == "RESEARCH"


def test_review_fail_rejects_noncanonical_recovery_target():
    with pytest.raises(GithubChatGuardError, match="revision_target"):
        block_review_failure_state(
            _to_research_audit(),
            previous_state_blob_sha="s2",
            executor_identity="chat-session:test",
            artifact_key="RESEARCH_AUDIT",
            artifact_path="workspaces/articles/owner-lifecycle-task/reviews/RESEARCH_AUDIT.json",
            artifact_blob_sha="audit-fail-blob",
            revision_target="TITLE",
        )


def test_blocked_recovery_uses_persisted_target_and_invalidates_downstream():
    blocked = _blocked_research_audit()
    with pytest.raises(GithubChatGuardError, match="repair_evidence"):
        resume_blocked_state(
            blocked,
            previous_state_blob_sha="s3",
            executor_identity="chat-session:test",
            repair_evidence=[],
        )

    resumed = resume_blocked_state(
        blocked,
        previous_state_blob_sha="s3",
        executor_identity="chat-session:test",
        repair_evidence=["maintenance://repair", "test://regression"],
    )
    assert resumed["status"] == "IN_PROGRESS"
    assert resumed["current_stage"] == "RESEARCH"
    assert resumed["stage_artifacts"] == {}
    assert resumed["review_decisions"] == {}
    assert resumed["recovery_history"][-1]["resume_target"] == "RESEARCH"
    assert resumed["execution_receipts"][-1]["capability_id"] == "financial_owner_blocked_recovery"


def test_blocked_recovery_rejects_missing_persisted_cursor():
    blocked = _blocked_research_audit()
    blocked["execution_receipts"][-1]["input_bindings"].pop("revision_target")
    with pytest.raises(GithubChatGuardError, match="recovery cursor"):
        resume_blocked_state(
            blocked,
            previous_state_blob_sha="s3",
            executor_identity="chat-session:test",
            repair_evidence=["repair://one"],
        )


def _state_with_feedback():
    return attach_material_feedback(
        _initial(),
        previous_state_blob_sha="f0",
        executor_identity="chat-session:test",
        sample={"sample_type": "USER_REJECTION", "summary": "material rejection"},
        system_impact={
            "signal_id": "impact-1",
            "status": "OPEN",
            "trigger_sample_type": "USER_REJECTION",
        },
    )


def _review_kwargs():
    return dict(
        signal_id="impact-1",
        problem_statement="owner lifecycle was incomplete",
        root_cause_layer="RUNTIME_OR_SCHEMA",
        generalization_scope="single Financial owner lifecycle",
        alternatives=[
            {"mechanism": "add deterministic owner lifecycle", "failure_mode": "additional owner code"},
            {"mechanism": "leave debt open", "failure_mode": "permanent stale maintenance debt"},
        ],
        selected_mechanism="add deterministic owner lifecycle",
        selection_rationale="keep one state authority while preserving evidence-bound recovery and maintenance closure",
        authority_surface="financial_writing_agent.owner_lifecycle",
        regression_or_eval_plan=["unit lifecycle regression"],
        evidence_refs=["issue://impact-1"],
        decision="SYSTEM_MAINTENANCE_REQUIRED",
        decision_reason="systemic owner lifecycle gap",
    )


def test_system_impact_escalates_then_closes_with_bound_self_attested_evidence():
    state = _state_with_feedback()
    reviewed = review_system_impact_state(
        state,
        previous_state_blob_sha="f1",
        executor_identity="chat-session:test",
        **_review_kwargs(),
    )
    item = reviewed["open_system_impact"][0]
    assert item["status"] == "MAINTENANCE_REQUIRED"
    assert item["review"]["decision"] == "SYSTEM_MAINTENANCE_REQUIRED"
    assert item["control_signal"]["authority"] == "NON_AUTHORITATIVE_CONTROL_SIGNAL"

    with pytest.raises(GithubChatGuardError, match="REGRESSION_VERIFIED"):
        review_system_impact_state(
            reviewed,
            previous_state_blob_sha="f2",
            executor_identity="chat-session:test",
            maintenance_ref="pr://repair",
            validation_refs=["ci://run"],
            assurance_ceiling="WIRED",
            **_review_kwargs(),
        )

    closed = review_system_impact_state(
        reviewed,
        previous_state_blob_sha="f2",
        executor_identity="chat-session:test",
        maintenance_ref="pr://repair",
        validation_refs=["test://owner-lifecycle"],
        assurance_ceiling="REGRESSION_VERIFIED",
        **_review_kwargs(),
    )
    assert closed["open_system_impact"] == []
    history = closed["system_impact_history"][-1]
    assert history["status"] == "MAINTENANCE_CLOSED"
    assert history["maintenance_closure"]["closure_attestation"] == OWNER_CLOSURE_ATTESTATION


def test_system_impact_closure_cannot_rewrite_accepted_diagnosis():
    reviewed = review_system_impact_state(
        _state_with_feedback(),
        previous_state_blob_sha="f1",
        executor_identity="chat-session:test",
        **_review_kwargs(),
    )
    changed = _review_kwargs()
    changed["problem_statement"] = "different diagnosis"
    with pytest.raises(GithubChatGuardError, match="immutable"):
        review_system_impact_state(
            reviewed,
            previous_state_blob_sha="f2",
            executor_identity="chat-session:test",
            maintenance_ref="pr://repair",
            validation_refs=["test://owner-lifecycle"],
            assurance_ceiling="REGRESSION_VERIFIED",
            **changed,
        )
