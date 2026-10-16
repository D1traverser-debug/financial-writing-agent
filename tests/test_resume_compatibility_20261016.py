import pytest

from financial_writing_agent.owner_guard import (
    GithubChatGuardError,
    advance_state,
    build_initial_state as build_legacy_owner_state,
)
from financial_writing_agent.resume_compatibility import (
    ResumeCompatibilityDecision,
    ResumeCompatibilityError,
    assess_resume_compatibility,
    require_material_resume_admission,
)


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
        _legacy_state(), intent=ResumeCompatibilityDecision.HISTORICAL_PROVENANCE_ONLY.value
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
        resume_intent=ResumeCompatibilityDecision.HISTORICAL_PROVENANCE_ONLY.value,
    )
    assert historical["current_stage"] == "RESEARCH"
    receipt = historical["execution_receipts"][-1]
    assert receipt["input_bindings"]["historical_resume_decision"] == ResumeCompatibilityDecision.HISTORICAL_PROVENANCE_ONLY.value
    assert receipt["input_bindings"]["historical_resume_reason"]
