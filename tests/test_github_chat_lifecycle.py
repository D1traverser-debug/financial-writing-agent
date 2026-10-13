import pytest

from financial_writing_agent.github_chat_guard import (
    GithubChatGuardError,
    advance_state,
    attach_material_feedback,
    build_initial_state,
)
from financial_writing_agent.github_chat_lifecycle import (
    resume_blocked_state,
    review_system_impact_state,
)


def _initial():
    return build_initial_state(
        task_id="lifecycle-task",
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
        artifact_path="workspaces/articles/lifecycle-task/stages/RESEARCH.json",
        artifact_blob_sha="research-blob",
    )


def _blocked_research_audit():
    state = _to_research_audit()
    return advance_state(
        state,
        previous_state_blob_sha="s2",
        executor_identity="chat-session:test",
        artifact_key="RESEARCH_AUDIT",
        artifact_path="workspaces/articles/lifecycle-task/reviews/RESEARCH_AUDIT.json",
        artifact_blob_sha="audit-fail-blob",
        review_status="FAIL",
    )


def test_blocked_state_requires_explicit_repair_evidence_and_reruns_exact_stage():
    blocked = _blocked_research_audit()
    assert blocked["status"] == "BLOCKED"
    assert blocked["current_stage"] == "RESEARCH_AUDIT"

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
        repair_evidence=["maintenance://repair-1", "test://regression-pass"],
    )
    assert resumed["status"] == "IN_PROGRESS"
    assert resumed["current_stage"] == "RESEARCH_AUDIT"
    assert "RESEARCH_AUDIT" not in resumed["stage_artifacts"]
    assert "RESEARCH_AUDIT" not in resumed["review_decisions"]
    assert resumed["recovery_history"][-1]["recovery_stage"] == "RESEARCH_AUDIT"
    assert resumed["execution_receipts"][-1]["capability_id"] == "github_chat_blocked_recovery"


def _state_with_feedback():
    state = _initial()
    return attach_material_feedback(
        state,
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
        problem_statement="chat lifecycle is incomplete",
        root_cause_layer="RUNTIME_OR_SCHEMA",
        generalization_scope="GITHUB_CHAT feedback lifecycle",
        alternatives=[
            {"mechanism": "add deterministic lifecycle", "failure_mode": "more adapter code"},
            {"mechanism": "leave debt open", "failure_mode": "permanent stale maintenance debt"},
        ],
        selected_mechanism="add deterministic lifecycle",
        selection_rationale="preserve owner-native lifecycle semantics without fake native receipts",
        authority_surface="financial_writing_agent.github_chat_lifecycle",
        regression_or_eval_plan=["unit lifecycle regression"],
        evidence_refs=["issue://impact-1"],
        decision="SYSTEM_MAINTENANCE_REQUIRED",
        decision_reason="systemic adapter lifecycle gap",
    )


def test_system_impact_can_escalate_then_close_with_bound_evidence():
    state = _state_with_feedback()
    reviewed = review_system_impact_state(
        state,
        previous_state_blob_sha="f1",
        executor_identity="chat-session:test",
        **_review_kwargs(),
    )
    assert reviewed["open_system_impact"][0]["status"] == "MAINTENANCE_REQUIRED"
    assert reviewed["open_system_impact"][0]["review"]["decision"] == "SYSTEM_MAINTENANCE_REQUIRED"

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
        validation_refs=["ci://run", "test://lifecycle"],
        assurance_ceiling="REGRESSION_VERIFIED",
        **_review_kwargs(),
    )
    assert closed["open_system_impact"] == []
    assert closed["system_impact_history"][-1]["status"] == "MAINTENANCE_CLOSED"
    assert closed["system_impact_history"][-1]["maintenance_closure"]["maintenance_ref"] == "pr://repair"
    assert closed["execution_receipts"][-1]["capability_id"] == "github_chat_system_impact_lifecycle"


def test_local_only_review_moves_signal_out_of_open_debt():
    state = _state_with_feedback()
    kwargs = _review_kwargs()
    kwargs["decision"] = "LOCAL_ONLY"
    kwargs["decision_reason"] = "bounded to this article"
    reviewed = review_system_impact_state(
        state,
        previous_state_blob_sha="f1",
        executor_identity="chat-session:test",
        **kwargs,
    )
    assert reviewed["open_system_impact"] == []
    assert reviewed["system_impact_history"][-1]["status"] == "REVIEWED_NO_MAINTENANCE"


def test_maintenance_closure_cannot_rewrite_original_diagnosis():
    state = _state_with_feedback()
    reviewed = review_system_impact_state(
        state,
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
            validation_refs=["ci://run"],
            assurance_ceiling="REGRESSION_VERIFIED",
            **changed,
        )
