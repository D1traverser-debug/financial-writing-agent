"""Read-only user-outcome trace from the one Financial Article Aggregate.

Stage advance, hashes, signed receipts and Word binaries are not claims that
the *user's instructions* were semantically satisfied. This projection is
derived from the existing state/requirements, never a second owner or tracker.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .current_admission import validate_state
from .owner_guard import STAGE_INDEX
from .task_requirements import canonical_digest, validate_requirement_authority


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
        rows.append({
            "requirement_id": requirement_id,
            "original_requirement": item["statement"],
            "source_kind": item["source_kind"],
            "origin_evidence_ref": item["evidence_ref"],
            "scopes": list(item["scopes"]),
            "due_stage": due_stage,
            "stage_structural_status": structural,
            "admitted_stage_evidence": admitted,
            "article_semantic_satisfaction_verified": False,
            "user_acceptance_verified": False,
        })
    expected = list(state["required_outputs"])
    recorded = state.get("delivery_artifacts", {})
    present = sorted(set(recorded) & set(expected))
    missing = sorted(set(expected) - set(recorded))
    return {
        "task_id": state["task_id"],
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
        "all_user_writing_goals_verified": False,
        "assurance": "ONE_OWNER_READ_ONLY_REQUIREMENT_TRACE__NO_SEMANTIC_SELF_CERTIFICATION",
    }
