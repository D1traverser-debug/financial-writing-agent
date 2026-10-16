from copy import deepcopy

import pytest

from financial_writing_agent.candidate_integrity import (
    CandidateIntegrityError,
    validate_feedback_candidate_isolation,
    validate_transition_candidate_isolation,
)
from financial_writing_agent.owner_lifecycle import _blocking_recovery_cursor


TASK_ID = "final-review-findings"
STAGE = "RESEARCH_AUDIT"
TARGET = "RESEARCH"
ARTIFACT = {
    "path": f"workspaces/articles/{TASK_ID}/reviews/RESEARCH_AUDIT.json",
    "blob_sha": "audit-blob",
}


def _feedback_before() -> dict:
    return {
        "schema_version": "1.2",
        "task_id": TASK_ID,
        "current_stage": STAGE,
        "learning_evidence": [],
        "open_system_impact": [],
        "execution_receipts": [],
        "updated_at": "before",
    }


def _feedback_after(before: dict) -> dict:
    after = deepcopy(before)
    after["learning_evidence"] = [{"sample_type": "USER_FEEDBACK", "summary": "material correction"}]
    after["open_system_impact"] = [
        {"signal_id": "impact-1", "status": "OPEN", "trigger_sample_type": "USER_FEEDBACK"}
    ]
    action_id = f"{TASK_ID}:MATERIAL_FEEDBACK:feedback-1"
    after["execution_receipts"] = [
        {
            "receipt_contract_version": "1.1",
            "receipt_id": "receipt:feedback-1",
            "action_id": action_id,
            "task_id": TASK_ID,
            "execution_ref": f"github-chat://{TASK_ID}/{action_id}",
            "subject_bindings": {
                "task_id": TASK_ID,
                "sample_type": "USER_FEEDBACK",
                "signal_id": "impact-1",
            },
            "input_bindings": {
                "feedback_summary": "material correction",
                "signal_status": "OPEN",
            },
            "output_refs": [f"workspaces/articles/{TASK_ID}/STATE.json"],
        }
    ]
    after["updated_at"] = "after"
    return after


def _revise_before(*, include_review_artifact: bool = True) -> dict:
    artifacts = {
        "RESEARCH": {
            "path": f"workspaces/articles/{TASK_ID}/stages/RESEARCH.json",
            "blob_sha": "research-blob",
        }
    }
    if include_review_artifact:
        artifacts[STAGE] = deepcopy(ARTIFACT)
    return {
        "schema_version": "1.2",
        "task_id": TASK_ID,
        "status": "IN_PROGRESS",
        "current_stage": STAGE,
        "next_action": "review",
        "stage_artifacts": artifacts,
        "review_decisions": {},
        "delivery_artifacts": {},
        "execution_receipts": [],
        "updated_at": "before",
    }


def _revise_after(before: dict) -> dict:
    after = deepcopy(before)
    after["current_stage"] = TARGET
    after["next_action"] = "revise"
    after["stage_artifacts"] = {}
    after["review_decisions"] = {}
    after["delivery_artifacts"] = {}
    action_id = f"{TASK_ID}:TRANSITION:revise-1"
    after["execution_receipts"] = [
        {
            "receipt_contract_version": "1.1",
            "receipt_id": "receipt:revise-1",
            "action_id": action_id,
            "task_id": TASK_ID,
            "execution_ref": f"github-chat://{TASK_ID}/{action_id}",
            "subject_bindings": {
                "task_id": TASK_ID,
                "from_stage": STAGE,
                "to_stage": TARGET,
            },
            "input_bindings": {
                "from_stage": STAGE,
                "review_status": "REVISE",
                "revision_target": TARGET,
                "required_artifact_key": STAGE,
                "required_artifact_blob_sha": ARTIFACT["blob_sha"],
            },
            "output_refs": [
                f"workspaces/articles/{TASK_ID}/STATE.json",
                ARTIFACT["path"],
            ],
        }
    ]
    after["updated_at"] = "after"
    return after


def test_feedback_receipt_cannot_carry_review_recovery_bindings():
    before = _feedback_before()
    after = _feedback_after(before)
    after["execution_receipts"][-1]["input_bindings"]["review_status"] = "FAIL"
    after["execution_receipts"][-1]["input_bindings"]["revision_target"] = TARGET
    with pytest.raises(CandidateIntegrityError, match="feedback receipt cannot bind review_status"):
        validate_feedback_candidate_isolation(before, after)


def test_public_revise_receipt_must_bind_authoritative_before_artifact():
    before = _revise_before()
    after = _revise_after(before)
    validate_transition_candidate_isolation(before, after)

    forged = deepcopy(after)
    forged["execution_receipts"][-1]["output_refs"][1] = f"workspaces/articles/{TASK_ID}/other.json"
    with pytest.raises(CandidateIntegrityError, match="artifact output must equal admitted stage artifact path"):
        validate_transition_candidate_isolation(before, forged)

    forged = deepcopy(after)
    forged["execution_receipts"][-1]["input_bindings"]["required_artifact_blob_sha"] = "other-blob"
    with pytest.raises(CandidateIntegrityError, match="artifact SHA must equal admitted stage artifact blob_sha"):
        validate_transition_candidate_isolation(before, forged)


def test_public_revise_fails_closed_without_authoritative_before_artifact():
    before = _revise_before(include_review_artifact=False)
    after = _revise_after(before)
    with pytest.raises(CandidateIntegrityError, match="required to corroborate public REVISE candidate"):
        validate_transition_candidate_isolation(before, after)


def test_blocked_recovery_cursor_ignores_feedback_receipt_with_fail_bindings():
    canonical_action = f"{TASK_ID}:TRANSITION:canonical-fail"
    canonical = {
        "stage": STAGE,
        "action_id": canonical_action,
        "capability_id": "github_chat_review_stages",
        "subject_bindings": {
            "task_id": TASK_ID,
            "from_stage": STAGE,
            "to_stage": STAGE,
            "blocked": True,
        },
        "input_bindings": {"review_status": "FAIL", "revision_target": TARGET},
    }
    poison_action = f"{TASK_ID}:MATERIAL_FEEDBACK:poison"
    poison = {
        "stage": STAGE,
        "action_id": poison_action,
        "capability_id": "github_chat_learning_evidence_capture",
        "subject_bindings": {"task_id": TASK_ID, "sample_type": "USER_FEEDBACK", "signal_id": "poison"},
        "input_bindings": {"review_status": "FAIL", "revision_target": "TITLE"},
    }
    state = {
        "task_id": TASK_ID,
        "current_stage": STAGE,
        "execution_receipts": [canonical, poison],
    }
    assert _blocking_recovery_cursor(state) == TARGET
