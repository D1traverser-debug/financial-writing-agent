from __future__ import annotations

from copy import deepcopy

import pytest

from financial_writing_agent.candidate_integrity import (
    CandidateIntegrityError,
    validate_feedback_candidate_isolation,
    validate_transition_candidate_isolation,
)


TASK_ID = "candidate-review-followup"
STATE_PATH = f"workspaces/articles/{TASK_ID}/STATE.json"


def _artifact(stage: str) -> dict[str, str]:
    return {
        "path": f"workspaces/articles/{TASK_ID}/{stage}.json",
        "blob_sha": f"{stage.lower()}-blob",
    }


def test_feedback_receipt_cannot_smuggle_review_recovery_bindings() -> None:
    before = {
        "schema_version": "1.2",
        "task_id": TASK_ID,
        "current_stage": "RESEARCH_AUDIT",
        "status": "BLOCKED",
        "learning_evidence": [],
        "open_system_impact": [],
        "execution_receipts": [],
        "updated_at": "before",
    }
    after = deepcopy(before)
    after["learning_evidence"].append(
        {"sample_type": "USER_FEEDBACK", "summary": "new feedback"}
    )
    after["open_system_impact"].append(
        {
            "signal_id": "feedback-signal",
            "status": "OPEN",
            "trigger_sample_type": "USER_FEEDBACK",
        }
    )
    action_id = f"{TASK_ID}:MATERIAL_FEEDBACK:test-action"
    after["execution_receipts"].append(
        {
            "receipt_contract_version": "1.1",
            "receipt_id": "receipt:feedback-followup",
            "action_id": action_id,
            "task_id": TASK_ID,
            "execution_ref": f"github-chat://{TASK_ID}/{action_id}",
            "subject_bindings": {
                "task_id": TASK_ID,
                "sample_type": "USER_FEEDBACK",
                "signal_id": "feedback-signal",
            },
            "input_bindings": {
                "feedback_summary": "new feedback",
                "signal_status": "OPEN",
                "review_status": "FAIL",
                "revision_target": "RESEARCH",
            },
            "output_refs": [STATE_PATH],
        }
    )
    after["updated_at"] = "after"

    with pytest.raises(CandidateIntegrityError, match="feedback receipt cannot bind review_status"):
        validate_feedback_candidate_isolation(before, after)


def test_revise_receipt_must_bind_pre_invalidation_review_artifact() -> None:
    reviewed_artifact = _artifact("RESEARCH_AUDIT")
    before = {
        "schema_version": "1.2",
        "task_id": TASK_ID,
        "current_stage": "RESEARCH_AUDIT",
        "status": "IN_PROGRESS",
        "next_action": "review",
        "stage_artifacts": {
            "RESEARCH": _artifact("RESEARCH"),
            "RESEARCH_AUDIT": reviewed_artifact,
        },
        "review_decisions": {},
        "delivery_artifacts": {},
        "execution_receipts": [],
        "updated_at": "before",
    }
    after = deepcopy(before)
    after["current_stage"] = "RESEARCH"
    after["stage_artifacts"] = {}
    after["review_decisions"] = {}
    forged_artifact = {
        "path": f"workspaces/articles/{TASK_ID}/unrelated.json",
        "blob_sha": "unrelated-blob",
    }
    action_id = f"{TASK_ID}:TRANSITION:test-revise"
    after["execution_receipts"].append(
        {
            "receipt_contract_version": "1.1",
            "receipt_id": "receipt:revise-followup",
            "action_id": action_id,
            "task_id": TASK_ID,
            "execution_ref": f"github-chat://{TASK_ID}/{action_id}",
            "subject_bindings": {
                "task_id": TASK_ID,
                "from_stage": "RESEARCH_AUDIT",
                "to_stage": "RESEARCH",
            },
            "input_bindings": {
                "from_stage": "RESEARCH_AUDIT",
                "review_status": "REVISE",
                "revision_target": "RESEARCH",
                "required_artifact_key": "RESEARCH_AUDIT",
                "required_artifact_blob_sha": forged_artifact["blob_sha"],
            },
            "output_refs": [STATE_PATH, forged_artifact["path"]],
        }
    )
    after["updated_at"] = "after"

    with pytest.raises(CandidateIntegrityError, match="artifact output must equal admitted stage artifact path"):
        validate_transition_candidate_isolation(before, after)
