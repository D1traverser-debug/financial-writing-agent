from __future__ import annotations

from copy import deepcopy

import pytest

from financial_writing_agent.candidate_integrity import (
    CandidateIntegrityError,
    validate_feedback_candidate_isolation,
    validate_transition_candidate_isolation,
)


def _receipt(
    stage: str,
    *,
    task_id: str,
    review_status: str | None = None,
    revision_target: str | None = None,
) -> dict:
    action_id = f"{task_id}:TRANSITION:test-action"
    bindings: dict[str, object] = {"from_stage": stage}
    subject: dict[str, object] = {"task_id": task_id, "from_stage": stage}
    if review_status is not None:
        bindings["review_status"] = review_status
    if revision_target is not None:
        bindings["revision_target"] = revision_target
    if review_status == "REVISE":
        subject["to_stage"] = revision_target
    elif review_status == "FAIL":
        subject["to_stage"] = stage
        subject["blocked"] = True
    else:
        subject["to_stage"] = stage
    output_refs = [f"workspaces/articles/{task_id}/STATE.json"]
    if stage != "INTAKE":
        output_refs.append(f"workspaces/articles/{task_id}/{stage}.json")
    return {
        "receipt_contract_version": "1.1",
        "receipt_id": "receipt:test",
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
        "task_id": "candidate-nested-test",
        "prompt": "fixed",
        "source_refs": ["s1"],
        "current_stage": stage,
        "status": "IN_PROGRESS",
        "next_action": "next",
        "stage_artifacts": {
            "RESEARCH": {"path": "r", "blob_sha": "r1"},
            "RESEARCH_AUDIT": {"path": "ra", "blob_sha": "ra1"},
        },
        "review_decisions": {
            "RESEARCH_AUDIT": {"status": "PASS", "artifact_ref": {"path": "ra", "blob_sha": "ra1"}}
        },
        "delivery_artifacts": {},
        "execution_receipts": [{"input_bindings": {"from_stage": "RESEARCH_AUDIT"}}],
        "updated_at": "before",
    }
    if schema == "1.3":
        state["writing_kernel_version"] = "1.0"
        state["quality_evidence"] = {
            "research_decision": {"selected_candidate_id": "B"},
        }
    return state


def _transition_after(before: dict, *, review_status: str | None = None, revision_target: str | None = None) -> dict:
    after = deepcopy(before)
    after["execution_receipts"] = list(before["execution_receipts"]) + [
        _receipt(
            str(before["current_stage"]),
            task_id=str(before["task_id"]),
            review_status=review_status,
            revision_target=revision_target,
        )
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
    after = deepcopy(before)
    after["learning_evidence"][0]["summary"] = "rewritten"
    after["learning_evidence"].append({"sample_type": "USER_FEEDBACK", "summary": "new"})
    after["open_system_impact"].append(
        {"signal_id": "new", "status": "OPEN", "trigger_sample_type": "USER_FEEDBACK"}
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [
        {
            "subject_bindings": {"sample_type": "USER_FEEDBACK", "signal_id": "new"},
            "input_bindings": {"feedback_summary": "new", "signal_status": "OPEN"},
        }
    ]
    after["updated_at"] = "after"
    with pytest.raises(CandidateIntegrityError, match="cannot rewrite prior history"):
        validate_feedback_candidate_isolation(before, after)


def test_canonical_revision_may_remove_only_invalidated_nested_state():
    before = _base("FINAL_AUDIT", schema="1.3")
    before["stage_artifacts"].update(
        {
            "EDITORIAL": {"path": "e", "blob_sha": "e1"},
            "TITLE": {"path": "t", "blob_sha": "t1"},
            "DRAFT": {"path": "d", "blob_sha": "d1"},
            "EDITORIAL_AUDIT": {"path": "ea", "blob_sha": "ea1"},
            "DELIVERY": {"path": "del", "blob_sha": "del1"},
            "MECHANICAL_AUDIT": {"path": "ma", "blob_sha": "ma1"},
            "FINAL_AUDIT": {"path": "fa", "blob_sha": "fa1"},
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
    after["current_stage"] = "EDITORIAL"
    after["stage_artifacts"] = {
        key: value for key, value in before["stage_artifacts"].items() if key in {"RESEARCH", "RESEARCH_AUDIT"}
    }
    after["review_decisions"] = {"RESEARCH_AUDIT": before["review_decisions"]["RESEARCH_AUDIT"]}
    after["quality_evidence"] = {"research_decision": before["quality_evidence"]["research_decision"]}
    after["delivery_artifacts"] = {}

    validate_transition_candidate_isolation(before, after)
