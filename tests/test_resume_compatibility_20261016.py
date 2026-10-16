import pytest

from financial_writing_agent.owner_guard import (
    GithubChatGuardError,
    advance_state,
    build_initial_state as build_legacy_owner_state,
)
from financial_writing_agent.owner_lifecycle import block_review_failure_state, resume_blocked_state
from financial_writing_agent.resume_compatibility import (
    ResumeCompatibilityDecision,
    ResumeCompatibilityError,
    assess_resume_compatibility,
    require_material_resume_admission,
)


_HISTORICAL_ONLY = ResumeCompatibilityDecision.HISTORICAL_PROVENANCE_ONLY.value


def _legacy_state() -> dict:
    return {
        "task_id": "legacy-task",
        "status": "IN_PROGRESS",
        "current_stage": "DELIVERY",
        "learning_evidence": [],
        "open_system_impact": [],
    }


def test_legacy_state_cannot_silently_continue_as_current_quality():
    result = assess_resume_compatibility(_legacy_state(), intent=None)
    assert result["decision"] == ResumeCompatibilityDecision.CURRENT_SUCCESSOR_REQUIRED.value
    with pytest.raises(ResumeCompatibilityError):
        require_material_resume_admission(_legacy_state(), intent=None)


def test_explicit_historical_provenance_continuation_is_bounded_not_current_quality():
    result = require_material_resume_admission(
        _legacy_state(), intent=_HISTORICAL_ONLY
    )
    assert result["decision"] == ResumeCompatibilityDecision.HISTORICAL_PROVENANCE_ONLY.value


def test_current_kernel_state_continues_normally():
    state = _legacy_state()
    state["writing_kernel_version"] = "1.0"
    state["quality_evidence"] = {}
    result = require_material_resume_admission(state, intent=None)
    assert result["decision"] == ResumeCompatibilityDecision.CURRENT_STATE.value


def test_material_rejection_strengthens_successor_reason():
    state = _legacy_state()
    state["learning_evidence"] = [{"sample_type": "USER_REJECTION"}]
    result = assess_resume_compatibility(state, intent=None)
    assert result["decision"] == ResumeCompatibilityDecision.CURRENT_SUCCESSOR_REQUIRED.value
    assert "corrective feedback" in result["reason"]


def test_direct_owner_advance_cannot_bypass_post_evolution_resume_admission():
    state = build_legacy_owner_state(
        task_id="legacy-owner-bypass",
        prompt="legacy historical article",
        source_refs=[],
        executor_identity="test:legacy-init",
    )
    assert "writing_kernel_version" not in state

    with pytest.raises(GithubChatGuardError, match="current-kernel successor"):
        advance_state(
            state,
            previous_state_blob_sha="a" * 40,
            executor_identity="test:bypass",
        )

    historical = advance_state(
        state,
        previous_state_blob_sha="a" * 40,
        executor_identity="test:historical",
        resume_intent=_HISTORICAL_ONLY,
    )
    assert historical["current_stage"] == "RESEARCH"
    receipt = historical["execution_receipts"][-1]
    assert receipt["input_bindings"]["historical_resume_decision"] == _HISTORICAL_ONLY
    assert receipt["input_bindings"]["historical_resume_reason"]


def _blocked_legacy_review_state():
    state = build_legacy_owner_state(
        task_id="legacy-blocked-bypass",
        prompt="legacy blocked article",
        source_refs=[],
        executor_identity="test:legacy-init",
    )
    state = advance_state(
        state,
        previous_state_blob_sha="b0",
        executor_identity="test:historical",
        resume_intent=_HISTORICAL_ONLY,
    )
    state = advance_state(
        state,
        previous_state_blob_sha="b1",
        executor_identity="test:historical",
        artifact_key="RESEARCH",
        artifact_path="workspaces/articles/legacy-blocked-bypass/stages/RESEARCH.json",
        artifact_blob_sha="research-blob",
        resume_intent=_HISTORICAL_ONLY,
    )
    return block_review_failure_state(
        state,
        previous_state_blob_sha="b2",
        executor_identity="test:historical",
        artifact_key="RESEARCH_AUDIT",
        artifact_path="workspaces/articles/legacy-blocked-bypass/reviews/RESEARCH_AUDIT.json",
        artifact_blob_sha="audit-fail",
        revision_target="RESEARCH",
        resume_intent=_HISTORICAL_ONLY,
    )


def test_direct_blocked_resume_cannot_bypass_post_evolution_resume_admission():
    blocked = _blocked_legacy_review_state()
    with pytest.raises(GithubChatGuardError, match="current-kernel successor"):
        resume_blocked_state(
            blocked,
            previous_state_blob_sha="b3",
            executor_identity="test:bypass",
            repair_evidence=["repair://evidence"],
        )

    resumed = resume_blocked_state(
        blocked,
        previous_state_blob_sha="b3",
        executor_identity="test:historical",
        repair_evidence=["repair://evidence"],
        resume_intent=_HISTORICAL_ONLY,
    )
    assert resumed["current_stage"] == "RESEARCH"
    receipt = resumed["execution_receipts"][-1]
    assert receipt["input_bindings"]["historical_resume_decision"] == _HISTORICAL_ONLY
    assert receipt["input_bindings"]["historical_resume_reason"]
