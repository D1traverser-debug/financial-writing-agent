import pytest

from financial_writing_agent.current_admission import build_initial_state
from financial_writing_agent.proactive_resolution import (
    ProactiveResolutionError,
    proactive_resolution_disposition,
    record_proactive_resolution_state,
    require_user_escalation_admission,
)


def _state():
    return build_initial_state(
        task_id="TEST-PROACTIVE-001",
        prompt="写一篇财经稿",
        source_refs=[],
        executor_identity="pytest",
    )


def test_user_escalation_is_denied_without_recovery_attempt():
    with pytest.raises(ProactiveResolutionError, match="no proactive-resolution attempt"):
        require_user_escalation_admission(
            _state(),
            target="voice_profile",
            reason="UNRESOLVED_MATERIAL_AMBIGUITY",
        )


def test_missing_best_voice_sample_continues_with_provisional_candidate_instead_of_asking_user():
    state = record_proactive_resolution_state(
        _state(),
        previous_state_blob_sha="abc123",
        executor_identity="pytest",
        target="voice_profile",
        attempted_sources=[
            "durable_user_corrections",
            "prior_user_edited_outputs",
            "current_conversation_context",
        ],
        evidence_refs=[
            "evals/USER_FEEDBACK_SYSTEM_IMPACT_2026-10-15_VOICE_FIRST_ANTI_AI.md",
            "references/reader_value.md",
        ],
        outcome="PROVISIONAL",
        candidate="medium-confidence restrained finance voice: evidence-first, no source-scaffolding, avoid formulaic anti-AI templates",
        confidence="MEDIUM",
        contradictions_or_unknowns=["no explicitly approved canonical full-article voice sample yet"],
        validation_plan=["validate on the next real Financial article and refine from user edits/acceptance"],
        safe_to_continue=True,
    )

    assert proactive_resolution_disposition(state, "voice_profile") == "CONTINUE_WITH_PROVISIONAL_CANDIDATE"
    latest = state["proactive_resolution_history"][-1]
    assert latest["attempted_sources"][0] == "durable_user_corrections"
    assert state["execution_receipts"][-1]["capability_id"] == "financial_owner_proactive_resolution_admission"
    assert state["execution_receipts"][-1]["input_bindings"]["task_requirement_contract_version"] == "1.0"

    with pytest.raises(ProactiveResolutionError, match="continue with that evidence-bound result"):
        require_user_escalation_admission(
            state,
            target="voice_profile",
            reason="UNRESOLVED_MATERIAL_AMBIGUITY",
        )


def test_genuinely_unresolved_dependency_can_be_escalated_after_attempted_recovery():
    state = record_proactive_resolution_state(
        _state(),
        previous_state_blob_sha="abc123",
        executor_identity="pytest",
        target="publication_authorization",
        attempted_sources=["current_task_authority", "durable_user_constraints"],
        evidence_refs=["workspaces/articles/TEST-PROACTIVE-001/STATE.json", "references/maintenance.md"],
        outcome="UNRESOLVED",
        candidate=None,
        confidence="NONE",
        contradictions_or_unknowns=["publication authorization is an explicit user choice and is not present"],
        validation_plan=[],
        safe_to_continue=False,
    )

    assert proactive_resolution_disposition(state, "publication_authorization") == "USER_ESCALATION_ELIGIBLE"
    admission = require_user_escalation_admission(
        state,
        target="publication_authorization",
        reason="REQUIRED_EVIDENCE_UNAVAILABLE",
    )
    assert admission["decision"] == "USER_ESCALATION_ADMITTED"
    assert admission["attempt_id"] == state["proactive_resolution_history"][-1]["attempt_id"]


def test_explicit_user_confirmation_request_does_not_require_recovery_receipt():
    admission = require_user_escalation_admission(
        _state(),
        target="title_choice",
        reason="USER_EXPLICIT_CONFIRMATION",
    )
    assert admission["decision"] == "USER_ESCALATION_ADMITTED"
