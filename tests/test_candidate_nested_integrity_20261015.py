from __future__ import annotations

from copy import deepcopy

import pytest

from financial_writing_agent.candidate_integrity import (
    CandidateIntegrityError,
    validate_feedback_candidate_isolation,
    validate_transition_candidate_isolation,
)
from financial_writing_agent.workflow_spec import pass_target_name


TASK_ID = "candidate-nested-test"


def _artifact(stage: str) -> dict:
    return {
        "path": f"workspaces/articles/{TASK_ID}/{stage}.json",
        "blob_sha": f"{stage.lower()}-blob",
    }


def _receipt(
    stage: str,
    *,
    task_id: str,
    to_stage: str | None,
    artifact_ref: dict | None = None,
    review_status: str | None = None,
    revision_target: str | None = None,
) -> dict:
    action_id = f"{task_id}:TRANSITION:test-action-{stage}"
    bindings: dict[str, object] = {"from_stage": stage}
    subject: dict[str, object] = {"task_id": task_id, "from_stage": stage, "to_stage": to_stage}
    if artifact_ref is not None:
        bindings["required_artifact_key"] = stage
        bindings["required_artifact_blob_sha"] = artifact_ref["blob_sha"]
    if review_status is not None:
        bindings["review_status"] = review_status
    if revision_target is not None:
        bindings["revision_target"] = revision_target
    if review_status == "FAIL":
        subject["blocked"] = True
    output_refs = [f"workspaces/articles/{task_id}/STATE.json"]
    if artifact_ref is not None:
        output_refs.append(artifact_ref["path"])
    return {
        "receipt_contract_version": "1.1",
        "receipt_id": f"receipt:test-{stage}",
        "action_id": action_id,
        "task_id": task_id,
        "execution_ref": f"github-chat://{task_id}/{action_id}",
        "subject_bindings": subject,
        "input_bindings": bindings,
        "output_refs": output_refs,
    }


def _base(stage: str = "DRAFT", *, schema: str = "1.2") -> dict:
    state = {
        "schema_version": schema,
        "task_id": TASK_ID,
        "prompt": "fixed",
        "source_refs": ["s1"],
        "current_stage": stage,
        "status": "IN_PROGRESS",
        "next_action": "next",
        "stage_artifacts": {
            "RESEARCH": _artifact("RESEARCH"),
            "RESEARCH_AUDIT": _artifact("RESEARCH_AUDIT"),
        },
        "review_decisions": {
            "RESEARCH_AUDIT": {
                "status": "PASS",
                "artifact_ref": _artifact("RESEARCH_AUDIT"),
                "assurance": "CHAT_SELF_REVIEW",
            }
        },
        "delivery_artifacts": {},
        "execution_receipts": [{"input_bindings": {"from_stage": "RESEARCH_AUDIT"}, "safe_to_continue": True}],
        "updated_at": "before",
    }
    if schema == "1.3":
        state["writing_kernel_version"] = "1.0"
        state["quality_evidence"] = {
            "research_decision": {"selected_candidate_id": "B"},
        }
    return state


def _transition_after(
    before: dict,
    *,
    review_status: str | None = None,
    revision_target: str | None = None,
) -> dict:
    after = deepcopy(before)
    stage = str(before["current_stage"])

    artifact_ref: dict | None = None
    if stage != "INTAKE":
        if review_status == "REVISE":
            artifact_ref = deepcopy(before.get("stage_artifacts", {}).get(stage) or _artifact(stage))
        else:
            artifact_ref = deepcopy(after.get("stage_artifacts", {}).get(stage) or _artifact(stage))
            after.setdefault("stage_artifacts", {})[stage] = deepcopy(artifact_ref)

    if review_status == "REVISE":
        to_stage = revision_target
    elif review_status == "FAIL":
        to_stage = stage
        after["status"] = "BLOCKED"
    else:
        to_stage = pass_target_name(stage)
        if to_stage == "COMPLETE":
            to_stage = stage
            after["status"] = "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"

    after["current_stage"] = to_stage
    if stage in {"RESEARCH_AUDIT", "EDITORIAL_AUDIT", "MECHANICAL_AUDIT", "FINAL_AUDIT"} and review_status in {"PASS", "FAIL"}:
        assert artifact_ref is not None
        after.setdefault("review_decisions", {})[stage] = {
            "status": review_status,
            "artifact_ref": deepcopy(artifact_ref),
            "assurance": "CHAT_SELF_REVIEW",
            "revision_target": None,
        }

    after["execution_receipts"] = deepcopy(before["execution_receipts"]) + [
        _receipt(
            stage,
            task_id=str(before["task_id"]),
            to_stage=to_stage,
            artifact_ref=artifact_ref,
            review_status=review_status,
            revision_target=revision_target,
        )
    ]
    after["updated_at"] = "after"
    return after


def _feedback_after(before: dict, *, signal_id: str = "new") -> dict:
    after = deepcopy(before)
    after.setdefault("learning_evidence", []).append(
        {"sample_type": "USER_FEEDBACK", "summary": "new feedback"}
    )
    after.setdefault("open_system_impact", []).append(
        {"signal_id": signal_id, "status": "OPEN", "trigger_sample_type": "USER_FEEDBACK"}
    )
    action_id = f"{before['task_id']}:MATERIAL_FEEDBACK:test-action"
    after["execution_receipts"] = deepcopy(before["execution_receipts"]) + [
        {
            "receipt_contract_version": "1.1",
            "receipt_id": "receipt:feedback-test",
            "action_id": action_id,
            "task_id": before["task_id"],
            "execution_ref": f"github-chat://{before['task_id']}/{action_id}",
            "subject_bindings": {
                "task_id": before["task_id"],
                "sample_type": "USER_FEEDBACK",
                "signal_id": signal_id,
            },
            "input_bindings": {
                "feedback_summary": "new feedback",
                "signal_status": "OPEN",
            },
            "output_refs": [f"workspaces/articles/{before['task_id']}/STATE.json"],
        }
    ]
    after["updated_at"] = "after"
    return after


def test_transition_cannot_rewrite_upstream_stage_artifact():
    before = _base("DRAFT")
    after = _transition_after(before)
    after["stage_artifacts"]["RESEARCH"]["blob_sha"] = "forged"
    with pytest.raises(CandidateIntegrityError, match="stage_artifacts.*immutable key"):
        validate_transition_candidate_isolation(before, after)


def test_non_review_transition_cannot_rewrite_prior_review_decision():
    before = _base("DRAFT")
    after = _transition_after(before)
    after["review_decisions"]["RESEARCH_AUDIT"]["status"] = "FAIL"
    with pytest.raises(CandidateIntegrityError, match="non-review transition cannot mutate review_decisions"):
        validate_transition_candidate_isolation(before, after)


def test_current_transition_rejects_unknown_quality_evidence_key():
    before = _base("TITLE", schema="1.3")
    after = _transition_after(before)
    after["quality_evidence"]["invented_gate"] = {"pass": True}
    with pytest.raises(CandidateIntegrityError, match="unknown keys"):
        validate_transition_candidate_isolation(before, after)


def test_unrelated_transition_cannot_rewrite_delivery_metadata():
    before = _base("TITLE")
    before["delivery_artifacts"] = {
        "FINANCE_DEEP_DOCX": {"kind": "FINANCE_DEEP_DOCX", "file_name": "deep.docx", "sha256": "0" * 64}
    }
    after = _transition_after(before)
    after["delivery_artifacts"]["FINANCE_DEEP_DOCX"]["sha256"] = "1" * 64
    with pytest.raises(CandidateIntegrityError, match="cannot mutate delivery_artifacts"):
        validate_transition_candidate_isolation(before, after)


def test_feedback_append_cannot_rewrite_prior_learning_history():
    before = _base("RESEARCH")
    before["learning_evidence"] = [{"sample_type": "USER_FEEDBACK", "summary": "old"}]
    before["open_system_impact"] = [
        {"signal_id": "old", "status": "OPEN", "trigger_sample_type": "USER_FEEDBACK"}
    ]
    after = _feedback_after(before)
    after["learning_evidence"][0]["summary"] = "rewritten"
    with pytest.raises(CandidateIntegrityError, match="cannot rewrite prior history"):
        validate_feedback_candidate_isolation(before, after)


def test_canonical_revision_may_remove_only_invalidated_nested_state():
    before = _base("FINAL_AUDIT", schema="1.3")
    before["stage_artifacts"].update(
        {
            "EDITORIAL": _artifact("EDITORIAL"),
            "TITLE": _artifact("TITLE"),
            "DRAFT": _artifact("DRAFT"),
            "EDITORIAL_AUDIT": _artifact("EDITORIAL_AUDIT"),
            "DELIVERY": _artifact("DELIVERY"),
            "MECHANICAL_AUDIT": _artifact("MECHANICAL_AUDIT"),
            "FINAL_AUDIT": _artifact("FINAL_AUDIT"),
        }
    )
    before["review_decisions"].update(
        {
            "EDITORIAL_AUDIT": {"status": "PASS"},
            "MECHANICAL_AUDIT": {"status": "PASS"},
        }
    )
    before["quality_evidence"].update(
        {
            "story_blueprints": [{"product_mode": "FINANCE_DEEP"}],
            "publication_fitnesses": [{"product_mode": "FINANCE_DEEP"}],
        }
    )
    before["delivery_artifacts"] = {
        "FINANCE_DEEP_DOCX": {"kind": "FINANCE_DEEP_DOCX", "file_name": "deep.docx", "sha256": "0" * 64}
    }

    after = _transition_after(before, review_status="REVISE", revision_target="EDITORIAL")
    after["stage_artifacts"] = {
        key: value for key, value in before["stage_artifacts"].items() if key in {"RESEARCH", "RESEARCH_AUDIT"}
    }
    after["review_decisions"] = {"RESEARCH_AUDIT": before["review_decisions"]["RESEARCH_AUDIT"]}
    after["quality_evidence"] = {"research_decision": before["quality_evidence"]["research_decision"]}
    after["delivery_artifacts"] = {}

    validate_transition_candidate_isolation(before, after)


def test_transition_receipts_are_type_strict_append_only():
    before = _base("DRAFT")
    after = _transition_after(before)
    after["execution_receipts"][0]["safe_to_continue"] = 1
    with pytest.raises(CandidateIntegrityError, match="execution_receipts.*cannot rewrite prior history"):
        validate_transition_candidate_isolation(before, after)


def test_feedback_receipts_are_type_strict_append_only():
    before = _base("RESEARCH")
    after = _feedback_after(before)
    after["execution_receipts"][0]["safe_to_continue"] = 1
    with pytest.raises(CandidateIntegrityError, match="execution_receipts.*cannot rewrite prior history"):
        validate_feedback_candidate_isolation(before, after)


@pytest.mark.parametrize("source_status", ["BLOCKED", "DELIVERED_CHAT_REVIEWED__CERTIFICATION_OPEN"])
def test_ordinary_transition_rejects_blocked_or_terminal_source(source_status: str):
    before = _base("DRAFT")
    before["status"] = source_status
    after = _transition_after(before)
    if source_status != "IN_PROGRESS":
        after["status"] = "IN_PROGRESS"
    with pytest.raises(CandidateIntegrityError, match="source state must be IN_PROGRESS"):
        validate_transition_candidate_isolation(before, after)


def test_non_review_transition_rejects_review_bindings():
    before = _base("DRAFT")
    after = _transition_after(before)
    after["execution_receipts"][-1]["input_bindings"]["review_status"] = "REVISE"
    after["execution_receipts"][-1]["input_bindings"]["revision_target"] = "DRAFT"
    with pytest.raises(CandidateIntegrityError, match="not a review stage"):
        validate_transition_candidate_isolation(before, after)


def test_nonterminal_forward_route_must_remain_in_progress():
    before = _base("DRAFT")
    after = _transition_after(before)
    after["status"] = "BLOCKED"
    with pytest.raises(CandidateIntegrityError, match="must remain IN_PROGRESS"):
        validate_transition_candidate_isolation(before, after)


def test_review_decision_must_bind_exact_stage_artifact():
    before = _base("RESEARCH_AUDIT")
    after = _transition_after(before, review_status="PASS")
    after["review_decisions"]["RESEARCH_AUDIT"]["artifact_ref"] = _artifact("RESEARCH")
    with pytest.raises(CandidateIntegrityError, match="artifact_ref must bind the exact admitted stage artifact"):
        validate_transition_candidate_isolation(before, after)


def test_transition_receipt_must_bind_exact_stage_artifact():
    before = _base("DRAFT")
    after = _transition_after(before)
    after["execution_receipts"][-1]["output_refs"][1] = f"workspaces/articles/{TASK_ID}/other.json"
    with pytest.raises(CandidateIntegrityError, match="artifact output must equal admitted stage artifact path"):
        validate_transition_candidate_isolation(before, after)


def test_feedback_rejects_duplicate_open_system_impact_signal_id():
    before = _base("RESEARCH")
    before["learning_evidence"] = [{"sample_type": "USER_FEEDBACK", "summary": "old"}]
    before["open_system_impact"] = [
        {"signal_id": "duplicate", "status": "OPEN", "trigger_sample_type": "USER_FEEDBACK"}
    ]
    after = _feedback_after(before, signal_id="duplicate")
    with pytest.raises(CandidateIntegrityError, match="signal_id must be unique"):
        validate_feedback_candidate_isolation(before, after)


def test_review_fail_requires_stage_allowed_recovery_cursor():
    before = _base("RESEARCH_AUDIT")
    after = _transition_after(before, review_status="FAIL", revision_target="RESEARCH")
    after["execution_receipts"][-1]["input_bindings"].pop("revision_target")
    with pytest.raises(CandidateIntegrityError, match="FAIL revision_target"):
        validate_transition_candidate_isolation(before, after)
