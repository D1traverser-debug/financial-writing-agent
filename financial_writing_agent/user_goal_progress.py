"""Read-only user-outcome trace from the one Financial Article Aggregate.

Stage advance, hashes, signed receipts and Word binaries are not claims that
the *user's instructions* were semantically satisfied. This projection is
derived from the existing state/requirements, never a second owner or tracker.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .current_admission import validate_state
from .owner_guard import STAGE_INDEX, TERMINAL_STATUS
from .task_requirements import canonical_digest, validate_requirement_authority
from .task_intake import TASK_INTAKE_CONTRACT_VERSION


def inspect_user_goal_progress(state: Mapping[str, Any]) -> dict[str, Any]:
    """Explain every active user requirement and remaining business outcome.

    Returns structural evidence only. A trusted editorial/user outcome reviewer
    must evaluate actual content before any real satisfaction can be claimed.
    """
    validate_state(state)
    authority = validate_requirement_authority(state["task_requirement_authority"])
    stage = str(state["current_stage"])
    index = STAGE_INDEX[stage]
    receipts = state["execution_receipts"]
    active_goal_review = state.get("goal_outcome_review")
    review_history = state.get("goal_outcome_review_history", [])
    latest_review = (
        review_history[-1].get("attestation")
        if isinstance(review_history, list) and review_history
        and isinstance(review_history[-1], Mapping) else None
    )
    semantic_review = active_goal_review if isinstance(active_goal_review, Mapping) else latest_review
    semantic_results = (
        semantic_review.get("requirement_results", [])
        if isinstance(semantic_review, Mapping) else []
    )
    semantic_by_id = {
        entry.get("requirement_id"): entry
        for entry in semantic_results
        if isinstance(entry, Mapping)
    } if isinstance(semantic_results, list) else {}
    criteria = (
        state.get("task_intake_manifest", {}).get("success_criteria", [])
        if isinstance(state.get("task_intake_manifest"), Mapping) else []
    )
    semantic_criteria = (
        semantic_review.get("success_criteria_results", [])
        if isinstance(semantic_review, Mapping) else []
    )
    criteria_by_id = {
        entry.get("criterion_id"): entry
        for entry in semantic_criteria
        if isinstance(entry, Mapping)
    } if isinstance(semantic_criteria, list) else {}
    criteria_rows = [
        {
            "criterion_id": item.get("criterion_id"),
            "statement": item.get("statement"),
            "result": (
                criteria_by_id.get(item.get("criterion_id"), {}).get("result")
                if isinstance(criteria_by_id.get(item.get("criterion_id")), Mapping)
                else "NOT_YET_REVIEWED"
            ),
            "evidence_refs": (
                list(criteria_by_id[item.get("criterion_id")].get("evidence_refs", []))
                if isinstance(criteria_by_id.get(item.get("criterion_id")), Mapping)
                else []
            ),
        }
        for item in criteria if isinstance(item, Mapping)
    ]
    rows: list[dict[str, Any]] = []
    for item in authority["active_requirements"]:
        requirement_id = item["requirement_id"]
        due_stage = item["affects_from_stage"]
        due_index = STAGE_INDEX[due_stage]
        digest = canonical_digest(item)
        admitted: list[dict[str, Any]] = []
        for receipt in receipts:
            if not isinstance(receipt, Mapping) or receipt.get("stage") != due_stage:
                continue
            bindings = receipt.get("input_bindings", {})
            if not isinstance(bindings, Mapping):
                continue
            evidence = bindings.get("task_requirement_satisfaction", [])
            if not isinstance(evidence, list):
                continue
            for entry in evidence:
                if (isinstance(entry, Mapping)
                        and entry.get("requirement_id") == requirement_id
                        and entry.get("requirement_sha256") == digest
                        and entry.get("result") == "SATISFIED"):
                    admitted.append({
                        "evidence_refs": list(entry.get("evidence_refs", [])),
                        "stage": due_stage,
                    })
        if index < due_index:
            structural = "AWAITING_REQUIRED_STAGE"
        elif index == due_index:
            # Even if a past revision once satisfied this stage, the current
            # cursor means it must be executed and reviewed again before exit.
            structural = "DUE__STAGE_SATISFACTION_STILL_REQUIRED"
        else:
            structural = (
                "ADMITTED_STAGE_RECEIPT__SEMANTIC_CORRECTNESS_UNPROVEN"
                if admitted else "MISSING_STAGE_SATISFACTION_RECEIPT"
            )
        semantic = semantic_by_id.get(requirement_id)
        semantic_result = semantic.get("result") if isinstance(semantic, Mapping) else None
        rows.append({
            "requirement_id": requirement_id,
            "original_requirement": item["statement"],
            "source_kind": item["source_kind"],
            "origin_evidence_ref": item["evidence_ref"],
            "scopes": list(item["scopes"]),
            "due_stage": due_stage,
            "stage_structural_status": structural,
            "admitted_stage_evidence": admitted,
            "independent_goal_review_result": semantic_result or "NOT_YET_REVIEWED",
            "independent_goal_review_evidence": (
                list(semantic.get("evidence_refs", []))
                if isinstance(semantic, Mapping) else []
            ),
            "article_semantic_satisfaction_verified": (
                semantic_result == "SATISFIED"
                and isinstance(active_goal_review, Mapping)
                and state.get("status") == TERMINAL_STATUS
            ),
            "user_acceptance_verified": False,
        })
    expected = list(state["required_outputs"])
    recorded = state.get("delivery_artifacts", {})
    present = sorted(set(recorded) & set(expected))
    missing = sorted(set(expected) - set(recorded))
    intake_required = state.get("task_intake_contract_version") == TASK_INTAKE_CONTRACT_VERSION
    active_goal_review_verified = (
        isinstance(active_goal_review, Mapping)
        and state.get("status") == TERMINAL_STATUS
        and active_goal_review.get("decision") == "PASS"
    )
    latest_goal_decision = (
        semantic_review.get("decision")
        if isinstance(semantic_review, Mapping) else None
    )
    return {
        "task_id": state["task_id"],
        "task_intake_status": (
            "INDEPENDENTLY_REVIEWED_AND_ADMITTED"
            if intake_required and state.get("current_stage") != "INTAKE"
            else "AWAITING_INTAKE_REVIEW" if intake_required
            else "LEGACY_TASK_WITHOUT_GOAL_FIRST_INTAKE"
        ),
        "task_intake_manifest_sha256": state.get("task_intake_manifest_sha256"),
        "latest_independent_goal_review_decision": latest_goal_decision or "OPEN",
        "independent_goal_outcome_verified": active_goal_review_verified,
        "independent_goal_outcome_review_sha256": (
            canonical_digest(active_goal_review)
            if active_goal_review_verified else None
        ),
        "success_criteria_progress": criteria_rows,
        "current_stage": stage,
        "business_state_status": state["status"],
        "requirement_revision": authority["revision"],
        "requirement_digest": state["task_requirement_digest"],
        "active_user_requirement_count": len(rows),
        "requirement_progress": rows,
        "output_contract_count": len(expected),
        "output_metadata_present": present,
        "output_metadata_missing": missing,
        "business_writing_pass_execution_verified": False,
        "current_primary_source_factual_entailment_verified": False,
        "real_user_article_quality_acceptance_verified": False,
        "all_user_writing_goals_verified": active_goal_review_verified,
        "assurance": "ONE_OWNER_READ_ONLY_REQUIREMENT_TRACE__NO_SEMANTIC_SELF_CERTIFICATION",
    }
