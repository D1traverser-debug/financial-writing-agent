import pytest

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
