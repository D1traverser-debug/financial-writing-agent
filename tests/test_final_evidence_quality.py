import pytest

from financial_writing_agent.engine import WorkflowError, WritingEngine
from financial_writing_agent.models import DistributionMode, Stage, TaskContract, WritingState


def _final_state() -> WritingState:
    return WritingState(
        contract=TaskContract(
            prompt="最终证据质量测试",
            distribution_mode=DistributionMode.FINANCE_DEEP,
            visuals_enabled=False,
        ),
        stage=Stage.FINAL_AUDIT,
    )


def _complete_evidence(state: WritingState) -> list[str]:
    return [
        f"{key}: frozen final content contains concrete evidence for {key}"
        for key in sorted(WritingEngine._required_final_evidence_keys(state))
    ]


def test_final_acceptance_evidence_rejects_bare_checked_label():
    state = _final_state()
    entries = _complete_evidence(state)
    target = "FINANCE_DEEP.reasoning_continuity"
    entries = [
        f"{target}: checked" if entry.startswith(f"{target}:") else entry
        for entry in entries
    ]
    state.working["final_audit"] = {"acceptance_evidence": entries}

    with pytest.raises(WorkflowError, match="concrete criterion-specific proof"):
        WritingEngine._validate_final_acceptance_evidence(state)


def test_final_acceptance_evidence_rejects_duplicate_required_key():
    state = _final_state()
    entries = _complete_evidence(state)
    entries.append("GLOBAL.evidence_boundary: second conflicting receipt")
    state.working["final_audit"] = {"acceptance_evidence": entries}

    with pytest.raises(WorkflowError, match="duplicate criterion key"):
        WritingEngine._validate_final_acceptance_evidence(state)


def test_final_acceptance_evidence_accepts_concrete_values():
    state = _final_state()
    state.working["final_audit"] = {"acceptance_evidence": _complete_evidence(state)}

    WritingEngine._validate_final_acceptance_evidence(state)
