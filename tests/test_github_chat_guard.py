from copy import deepcopy

import pytest

from financial_writing_agent.github_chat_guard import (
    CHAT_REVIEW_ASSURANCE,
    TERMINAL_STATUS,
    GithubChatGuardError,
    advance_state,
    attach_material_feedback,
    build_initial_state,
    validate_state,
    validate_transition,
)


def _initial():
    return build_initial_state(
        task_id="guard-task",
        prompt="write a test article",
        distribution_mode="FINANCE_DEEP",
        source_refs=["source://one"],
        executor_identity="chat-session:test",
    )


def _advance_research(state):
    state = advance_state(state, previous_state_blob_sha="state-0", executor_identity="chat-session:test")
    return advance_state(
        state,
        previous_state_blob_sha="state-1",
        executor_identity="chat-session:test",
        artifact_key="RESEARCH",
        artifact_path="workspaces/articles/guard-task/stages/RESEARCH.json",
        artifact_blob_sha="research-blob",
    )


def test_initial_state_is_receipt_bound_and_self_attested():
    state = _initial()
    assert state["execution_mode"] == "GITHUB_CHAT"
    assert state["current_stage"] == "INTAKE"
    assert state["review_assurance"] == CHAT_REVIEW_ASSURANCE
    receipt = state["execution_receipts"][-1]
    assert receipt["capability_id"] == "github_chat_workflow"
    assert receipt["input_bindings"]["previous_state_blob_sha"] == "NEW_FILE"
    assert receipt["verification_status"] == "SELF_ATTESTED_CHAT_EXECUTION_RECEIPT"


def test_research_cannot_advance_without_persisted_artifact():
    state = advance_state(_initial(), previous_state_blob_sha="state-0", executor_identity="chat-session:test")
    with pytest.raises(GithubChatGuardError, match="stage_artifacts.RESEARCH"):
        advance_state(state, previous_state_blob_sha="state-1", executor_identity="chat-session:test")


def test_stage_skip_is_rejected_even_if_state_is_manually_tampered():
    before = _advance_research(_initial())
    after = deepcopy(before)
    after["current_stage"] = "DRAFT"
    after["stage_artifacts"]["RESEARCH_AUDIT"] = {
        "path": "workspaces/articles/guard-task/reviews/RESEARCH_AUDIT.json",
        "blob_sha": "review-blob",
    }
    after["review_decisions"]["RESEARCH_AUDIT"] = {
        "status": "PASS",
        "artifact_ref": after["stage_artifacts"]["RESEARCH_AUDIT"],
        "assurance": CHAT_REVIEW_ASSURANCE,
        "revision_target": None,
    }
    receipt = deepcopy(before["execution_receipts"][-1])
    receipt["receipt_id"] = "receipt:tampered"
    receipt["action_id"] = "guard-task:tampered"
    receipt["stage"] = "RESEARCH_AUDIT"
    receipt["capability_id"] = "github_chat_review_stages"
    receipt["input_bindings"] = {"previous_state_blob_sha": "state-2"}
    after["execution_receipts"] = before["execution_receipts"] + [receipt]
    with pytest.raises(GithubChatGuardError, match="must advance to EDITORIAL"):
        validate_transition(before, after, previous_state_blob_sha="state-2")


def test_research_audit_pass_requires_review_artifact_and_stays_chat_self_review():
    state = _advance_research(_initial())
    with pytest.raises(GithubChatGuardError, match="stage_artifacts.RESEARCH_AUDIT"):
        advance_state(
            state,
            previous_state_blob_sha="state-2",
            executor_identity="chat-session:test",
            review_status="PASS",
        )

    state = advance_state(
        state,
        previous_state_blob_sha="state-2",
        executor_identity="chat-session:test",
        artifact_key="RESEARCH_AUDIT",
        artifact_path="workspaces/articles/guard-task/reviews/RESEARCH_AUDIT.json",
        artifact_blob_sha="review-blob",
        review_status="PASS",
    )
    assert state["current_stage"] == "EDITORIAL"
    assert state["review_decisions"]["RESEARCH_AUDIT"]["assurance"] == CHAT_REVIEW_ASSURANCE
    assert state["execution_receipts"][-1]["capability_id"] == "github_chat_review_stages"


def test_chat_assurance_cannot_be_upgraded_by_state_edit():
    state = _initial()
    state["review_assurance"] = "INDEPENDENT_EXECUTOR"
    with pytest.raises(GithubChatGuardError, match="CHAT_SELF_REVIEW"):
        validate_state(state)


def test_material_negative_feedback_and_open_system_impact_are_one_guarded_checkpoint():
    state = _initial()
    updated = attach_material_feedback(
        state,
        previous_state_blob_sha="state-0",
        executor_identity="chat-session:test",
        sample={"sample_type": "USER_REJECTION", "summary": "material rejection"},
        system_impact={
            "signal_id": "impact-1",
            "status": "OPEN",
            "trigger_sample_type": "USER_REJECTION",
        },
    )
    assert updated["learning_evidence"][-1]["sample_type"] == "USER_REJECTION"
    assert updated["open_system_impact"][-1]["signal_id"] == "impact-1"
    receipt = updated["execution_receipts"][-1]
    assert receipt["capability_id"] == "github_chat_learning_evidence_capture"
    assert receipt["input_bindings"]["previous_state_blob_sha"] == "state-0"


def test_final_chat_review_uses_bounded_terminal_status_not_native_complete():
    state = _initial()
    # Build the straight-through path with persisted artifacts at every stage.
    state = advance_state(state, previous_state_blob_sha="s0", executor_identity="chat-session:test")
    state = advance_state(
        state,
        previous_state_blob_sha="s1",
        executor_identity="chat-session:test",
        artifact_key="RESEARCH",
        artifact_path="workspaces/articles/guard-task/stages/RESEARCH.json",
        artifact_blob_sha="a1",
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s2",
        executor_identity="chat-session:test",
        artifact_key="RESEARCH_AUDIT",
        artifact_path="workspaces/articles/guard-task/reviews/RESEARCH_AUDIT.json",
        artifact_blob_sha="a2",
        review_status="PASS",
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s3",
        executor_identity="chat-session:test",
        artifact_key="EDITORIAL",
        artifact_path="workspaces/articles/guard-task/stages/EDITORIAL.json",
        artifact_blob_sha="a3",
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s4",
        executor_identity="chat-session:test",
        artifact_key="TITLE",
        artifact_path="workspaces/articles/guard-task/stages/TITLE.json",
        artifact_blob_sha="a4",
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s5",
        executor_identity="chat-session:test",
        artifact_key="DRAFT",
        artifact_path="workspaces/articles/guard-task/stages/DRAFT.json",
        artifact_blob_sha="a5",
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s6",
        executor_identity="chat-session:test",
        artifact_key="EDITORIAL_AUDIT",
        artifact_path="workspaces/articles/guard-task/reviews/EDITORIAL_AUDIT.json",
        artifact_blob_sha="a6",
        review_status="PASS",
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s7",
        executor_identity="chat-session:test",
        artifact_key="DELIVERY",
        artifact_path="workspaces/articles/guard-task/publication/DELIVERY.json",
        artifact_blob_sha="a7",
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s8",
        executor_identity="chat-session:test",
        artifact_key="MECHANICAL_AUDIT",
        artifact_path="workspaces/articles/guard-task/reviews/MECHANICAL_AUDIT.json",
        artifact_blob_sha="a8",
        review_status="PASS",
    )
    state = advance_state(
        state,
        previous_state_blob_sha="s9",
        executor_identity="chat-session:test",
        artifact_key="FINAL_AUDIT",
        artifact_path="workspaces/articles/guard-task/reviews/FINAL_AUDIT.json",
        artifact_blob_sha="a9",
        review_status="PASS",
    )
    assert state["status"] == TERMINAL_STATUS
    assert state["status"] != "COMPLETE"
    assert state["current_stage"] == "FINAL_AUDIT"
