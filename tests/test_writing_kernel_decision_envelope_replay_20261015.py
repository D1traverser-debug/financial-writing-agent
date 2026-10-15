import json
from pathlib import Path

from financial_writing_agent.cognition_governance import DecisionEnvelope, admission_errors

ROOT = Path(__file__).resolve().parents[1]


def test_persisted_writing_kernel_architecture_decision_is_executable_and_admitted():
    payload = json.loads(
        (ROOT / "evals/FINANCIAL_WRITING_KERNEL_DECISION_ENVELOPE_2026-10-15.json").read_text(encoding="utf-8")
    )
    envelope = DecisionEnvelope.model_validate(payload)
    assert envelope.selected_candidate_id == "SINGLE_OWNER_FOCUSED_PASSES"
    assert envelope.saturation is not None
    assert admission_errors(envelope) == []
