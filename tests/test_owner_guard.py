from copy import deepcopy

import pytest

from financial_writing_agent.owner_guard import (
    CHAT_REVIEW_ASSURANCE,
    MODE_SOURCE_USER_EXPLICIT,
    TERMINAL_STATUS,
    GithubChatGuardError,
    advance_state,
    attach_material_feedback,
    build_initial_state,
    validate_state,
    validate_transition,
)


def _initial():
    # Public creation is now schema 1.3. These tests intentionally exercise the
    # historical 1.2 owner-state semantics that must remain resumable/readable.
    state = build_initial_state(
        task_id="guard-task",
        prompt="write a test article",
        source_refs=["source://one"],
        executor_identity="chat-session:test",
    )
    state["schema_version"] = "1.2"
    state.pop("writing_kernel_version", None)
    state.pop("quality_evidence", None)
    for receipt in state["execution_receipts"]:
        receipt["input_bindings"].pop("writing_kernel_version", None)
        receipt["input_bindings"].pop("quality_admission_path", None)
    return state


def _delivery(kind: str, file_name: str, char: str = "a"):
    return {"kind": kind, "file_name": file_name, "sha256": char * 64}


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


def test_initial_state_is_receipt_bound_self_attested_and_owner_contract_parity():
    state = _initial()
    assert state["execution_mode"] == "GITHUB_CHAT"
    assert state["current_stage"] == "INTAKE"
    assert state["review_assurance"] == CHAT_REVIEW_ASSURANCE
    assert state["state_ref"] == "main"
    assert state["distribution_mode"] == "PORTFOLIO"
    assert state["delivery_channel"] == "WORD_FILE_ONLY"
    assert state["required_outputs"] == [
        "AUDIT_DOCX",
        "FINANCE_DEEP_DOCX",
        "FINANCE_BROAD_DOCX",
        "PLATFORM_INTERACTION_PACK_DOCX",
    ]
    receipt = state["execution_receipts"][-1]
    assert receipt["capability_id"] == "github_chat_workflow"
    assert receipt["input_bindings"]["previous_state_blob_sha"] == "NEW_FILE"
    assert receipt["input_bindings"]["state_ref"] == "main"
    assert receipt["input_bindings"]["distribution_mode_override_evidence"] is None
    assert receipt["verification_status"] == "SELF_ATTESTED_CHAT_EXECUTION_RECEIPT"


def test_distribution_mode_cannot_be_silently_narrowed_by_chat():
    with pytest.raises(GithubChatGuardError, match="USER_EXPLICIT_OVERRIDE"):
        build_initial_state(
            task_id="silent-narrow",
            prompt="normal article with no platform override",
            source_refs=[],
            executor_identity="chat-session:test",
            distribution_mode="FINANCE_BROAD",
        )


def test_user_explicit_distribution_override_requires_exact_prompt_evidence():
    with pytest.raises(GithubChatGuardError, match="exact user prompt evidence"):
        build_initial_state(
            task_id="missing-evidence",
            prompt="这篇只要宽版",
            source_refs=[],
            executor_identity="chat-session:test",
            distribution_mode="FINANCE_BROAD",
            distribution_mode_source=MODE_SOURCE_USER_EXPLICIT,
        )

    with pytest.raises(GithubChatGuardError, match="exact substring"):
        build_initial_state(
            task_id="mismatched-evidence",
            prompt="这篇只要宽版",
            source_refs=[],
            executor_identity="chat-session:test",
            distribution_mode="FINANCE_BROAD",
            distribution_mode_source=MODE_SOURCE_USER_EXPLICIT,
            distribution_mode_override_evidence="用户只要广义财经版",
        )


def test_user_explicit_distribution_override_is_auditable():
    state = build_initial_state(
        task_id="explicit-broad",
        prompt="这篇只要宽版，其他按默认流程",
        source_refs=[],
        executor_identity="chat-session:test",
        distribution_mode="FINANCE_BROAD",
        distribution_mode_source=MODE_SOURCE_USER_EXPLICIT,
        distribution_mode_override_evidence="只要宽版",
    )
    assert state["distribution_mode"] == "FINANCE_BROAD"
    assert state["required_outputs"] == ["AUDIT_DOCX", "FINANCE_BROAD_DOCX"]
    init_bindings = state["execution_receipts"][0]["input_bindings"]
    assert init_bindings["distribution_mode_source"] == MODE_SOURCE_USER_EXPLICIT
    assert init_bindings["distribution_mode_override_evidence"] == "只要宽版"


def test_research_cannot_advance_without_persisted_artifact():
    state = advance_state(_initial(), previous_state_blob_sha="state-0", executor_identity="chat-session:test")
    with pytest.raises(GithubChatGuardError, match="stage_artifacts.RESEARCH"):
        advance_state(state, previous_state_blob_sha="state-1", executor_identity="chat-session:test")


def test_foreign_article_artifact_cannot_satisfy_current_stage():
    state = advance_state(_initial(), previous_state_blob_sha="state-0", executor_identity="chat-session:test")
    with pytest.raises(GithubChatGuardError, match="current article workspace"):
        advance_state(
            state,
            previous_state_blob_sha="state-1",
            executor_identity="chat-session:test",
            artifact_key="RESEARCH",
            artifact_path="workspaces/articles/other-task/stages/RESEARCH.json",
            artifact_blob_sha="foreign-blob",
        )


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
    receipt["input_bindings"] = {"previous_state_blob_sha": "state-2", "state_ref": "main"}
    after["execution_receipts"] = before["execution_receipts"] + [receipt]
    with pytest.raises(
        GithubChatGuardError,
        match="must advance to EDITORIAL|transition receipt must bind review_status",
    ):
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


def test_revision_invalidates_target_and_all_downstream_artifact_refs_and_delivery_manifest():
    state = _advance_research(_initial())
    state["delivery_artifacts"] = {
        "FINANCE_DEEP_DOCX": _delivery("FINANCE_DEEP_DOCX", "deep.docx"),
        "FINANCE_BROAD_DOCX": _delivery("FINANCE_BROAD_DOCX", "broad.docx", "b"),
    }
    state = advance_state(
        state,
        previous_state_blob_sha="state-2",
        executor_identity="chat-session:test",
        artifact_key="RESEARCH_AUDIT",
        artifact_path="workspaces/articles/guard-task/reviews/RESEARCH_AUDIT.json",
        artifact_blob_sha="review-old",
        review_status="REVISE",
        revision_target="RESEARCH",
    )
    assert state["current_stage"] == "RESEARCH"
    assert state["stage_artifacts"] == {}
    assert state["review_decisions"] == {}
    assert state["delivery_artifacts"] == {}
    assert "RESEARCH" in state["execution_receipts"][-1]["input_bindings"]["invalidated_stage_refs"]
    with pytest.raises(GithubChatGuardError, match="stage_artifacts.RESEARCH"):
        advance_state(state, previous_state_blob_sha="state-3", executor_identity="chat-session:test")


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
    assert receipt["input_bindings"]["state_ref"] == "main"


def _advance_to_delivery():
    state = _initial()
    state = advance_state(state, previous_state_blob_sha="s0", executor_identity="chat-session:test")
    state = advance_state(state, previous_state_blob_sha="s1", executor_identity="chat-session:test", artifact_key="RESEARCH", artifact_path="workspaces/articles/guard-task/stages/RESEARCH.json", artifact_blob_sha="a1")
    state = advance_state(state, previous_state_blob_sha="s2", executor_identity="chat-session:test", artifact_key="RESEARCH_AUDIT", artifact_path="workspaces/articles/guard-task/reviews/RESEARCH_AUDIT.json", artifact_blob_sha="a2", review_status="PASS")
    state = advance_state(state, previous_state_blob_sha="s3", executor_identity="chat-session:test", artifact_key="EDITORIAL", artifact_path="workspaces/articles/guard-task/stages/EDITORIAL.json", artifact_blob_sha="a3")
    state = advance_state(state, previous_state_blob_sha="s4", executor_identity="chat-session:test", artifact_key="TITLE", artifact_path="workspaces/articles/guard-task/stages/TITLE.json", artifact_blob_sha="a4")
    state = advance_state(state, previous_state_blob_sha="s5", executor_identity="chat-session:test", artifact_key="DRAFT", artifact_path="workspaces/articles/guard-task/stages/DRAFT.json", artifact_blob_sha="a5")
    return advance_state(state, previous_state_blob_sha="s6", executor_identity="chat-session:test", artifact_key="EDITORIAL_AUDIT", artifact_path="workspaces/articles/guard-task/reviews/EDITORIAL_AUDIT.json", artifact_blob_sha="a6", review_status="PASS")


def test_portfolio_delivery_cannot_drop_required_article_output():
    state = _advance_to_delivery()
    with pytest.raises(GithubChatGuardError, match="article delivery outputs mismatch"):
        advance_state(
            state,
            previous_state_blob_sha="s7",
            executor_identity="chat-session:test",
            artifact_key="DELIVERY",
            artifact_path="workspaces/articles/guard-task/stages/DELIVERY.json",
            artifact_blob_sha="a7",
            delivery_artifacts=[_delivery("FINANCE_BROAD_DOCX", "broad.docx")],
        )


def test_final_chat_review_requires_full_portfolio_and_uses_bounded_terminal():
    state = _advance_to_delivery()
    state = advance_state(
        state,
        previous_state_blob_sha="s7",
        executor_identity="chat-session:test",
        artifact_key="DELIVERY",
        artifact_path="workspaces/articles/guard-task/stages/DELIVERY.json",
        artifact_blob_sha="a7",
        delivery_artifacts=[
            _delivery("FINANCE_DEEP_DOCX", "deep.docx"),
            _delivery("FINANCE_BROAD_DOCX", "broad.docx", "b"),
            _delivery("PLATFORM_INTERACTION_PACK_DOCX", "interaction.docx", "d"),
        ],
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
    with pytest.raises(GithubChatGuardError, match="AUDIT_DOCX"):
        advance_state(
            state,
            previous_state_blob_sha="s9",
            executor_identity="chat-session:test",
            artifact_key="FINAL_AUDIT",
            artifact_path="workspaces/articles/guard-task/reviews/FINAL_AUDIT.json",
            artifact_blob_sha="a9",
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
        audit_artifact=_delivery("AUDIT_DOCX", "WRITING_AUDIT_REPORT.docx", "c"),
    )
    assert state["status"] == TERMINAL_STATUS
    assert state["status"] != "COMPLETE"
    assert state["current_stage"] == "FINAL_AUDIT"
    assert set(state["delivery_artifacts"]) == {
        "FINANCE_DEEP_DOCX",
        "FINANCE_BROAD_DOCX",
        "PLATFORM_INTERACTION_PACK_DOCX",
        "AUDIT_DOCX",
    }
