from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .owner_guard import (
    MAIN_STATE_REF,
    SELF_ATTESTED_RECEIPT,
    GithubChatGuardError as OwnerGuardError,
    _invalidate_from,
    _new_receipt,
    _state_path,
    _utc_now,
    advance_state,
    validate_state,
)
from .models import Stage
from .workflow_spec import REVIEW_STAGE_NAMES, revision_targets

MATERIAL_FEEDBACK_TYPES = {"USER_EDIT", "USER_FEEDBACK", "USER_REJECTION"}
OWNER_CLOSURE_ATTESTATION = "SELF_ATTESTED_OWNER_EVIDENCE_BINDING"
ROOT_CAUSE_LAYERS = {
    "ACCOUNT_OR_PRODUCT_INSTRUCTION",
    "STARTUP_OR_ROUTING_INSTRUCTION",
    "REPOSITORY_POLICY",
    "RUNTIME_OR_SCHEMA",
    "TEST_OR_EVAL",
    "OWNER_BINDING",
    "PRODUCT_CAPABILITY",
    "EVIDENCE_OR_PROPAGATION",
}
SYSTEM_IMPACT_DECISIONS = {"LOCAL_ONLY", "SYSTEM_MAINTENANCE_REQUIRED", "NO_CHANGE_WITH_REASON"}
ASSURANCE_LADDER = [
    "DECLARED",
    "WIRED",
    "REGRESSION_VERIFIED",
    "ACTION_LEVEL_SELF_ATTESTED",
    "ACTION_LEVEL_INDEPENDENTLY_VERIFIED",
    "LIVE_OUTCOME_VERIFIED",
]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise OwnerGuardError(message)


def _clean_string_list(values: list[str] | None, *, label: str, required: bool = True) -> list[str]:
    cleaned = list(dict.fromkeys(value.strip() for value in (values or []) if isinstance(value, str) and value.strip()))
    if required:
        _require(bool(cleaned), f"{label} requires at least one non-empty item")
    return cleaned


def _allowed_revision_targets(stage: str) -> set[str]:
    try:
        stage_enum = Stage(stage)
    except ValueError:
        return set()
    return {target.value for target in revision_targets(stage_enum)}


def _normalize_alternatives(alternatives: list[Mapping[str, Any]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in alternatives:
        mechanism = str(raw.get("mechanism", "")).strip()
        failure_mode = str(raw.get("failure_mode", "")).strip()
        _require(bool(mechanism and failure_mode), "each system-impact alternative requires mechanism and failure_mode")
        _require(mechanism not in seen, "system-impact alternatives must use distinct mechanisms")
        seen.add(mechanism)
        normalized.append({"mechanism": mechanism, "failure_mode": failure_mode})
    _require(len(normalized) >= 2, "system-impact review requires at least two credible alternatives")
    return normalized


def block_review_failure_state(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    artifact_key: str,
    artifact_path: str,
    artifact_blob_sha: str,
    revision_target: str,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    """Persist a review FAIL together with its canonical repair target.

    The base guard blocks FAIL in place. This helper makes the recovery cursor explicit
    in the same action receipt so later recovery cannot invent a target after the fact.
    """
    _require(state_ref == MAIN_STATE_REF, "Financial owner material mutations must target main")
    validate_state(state)
    stage = str(state.get("current_stage", ""))
    _require(stage in REVIEW_STAGE_NAMES, "review failure blocking requires a canonical review stage")
    allowed = _allowed_revision_targets(stage)
    _require(revision_target in allowed, f"{stage} FAIL revision_target must be one of {sorted(allowed)}")

    blocked = advance_state(
        state,
        previous_state_blob_sha=previous_state_blob_sha,
        executor_identity=executor_identity,
        artifact_key=artifact_key,
        artifact_path=artifact_path,
        artifact_blob_sha=artifact_blob_sha,
        review_status="FAIL",
        revision_target=revision_target,
        state_ref=state_ref,
    )
    _require(blocked.get("status") == "BLOCKED", "review FAIL must produce BLOCKED state")
    receipt = blocked["execution_receipts"][-1]
    _require(receipt["input_bindings"].get("review_status") == "FAIL", "blocking receipt must bind review_status=FAIL")
    _require(receipt["input_bindings"].get("revision_target") == revision_target, "blocking receipt must persist the canonical recovery cursor")
    return blocked


def _blocking_recovery_cursor(state: Mapping[str, Any]) -> str:
    stage = str(state.get("current_stage", ""))
    for receipt in reversed(list(state.get("execution_receipts", []))):
        if receipt.get("stage") != stage:
            continue
        bindings = receipt.get("input_bindings", {})
        if bindings.get("review_status") != "FAIL":
            continue
        target = str(bindings.get("revision_target", "")).strip()
        _require(target in _allowed_revision_targets(stage), "BLOCKED state has no valid persisted canonical recovery cursor")
        return target
    raise OwnerGuardError("BLOCKED state has no persisted FAIL receipt with a recovery cursor")


def resume_blocked_state(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    repair_evidence: list[str],
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    """Resume a blocked review through the target chosen when the FAIL was persisted."""
    _require(state_ref == MAIN_STATE_REF, "Financial owner material mutations must target main")
    validate_state(state)
    before = deepcopy(dict(state))
    _require(before.get("status") == "BLOCKED", "only BLOCKED owner state may be resumed")
    failed_stage = str(before.get("current_stage", ""))
    _require(failed_stage in REVIEW_STAGE_NAMES, "BLOCKED recovery requires a canonical review-stage failure")
    evidence = _clean_string_list(repair_evidence, label="repair_evidence")
    failed_review = before.get("review_decisions", {}).get(failed_stage)
    _require(isinstance(failed_review, Mapping) and failed_review.get("status") == "FAIL", "BLOCKED recovery requires the persisted FAIL review decision")

    target = _blocking_recovery_cursor(before)
    after = deepcopy(before)
    invalidated = _invalidate_from(after, target)
    after["status"] = "IN_PROGRESS"
    after["current_stage"] = target
    after["next_action"] = f"repair and persist a fresh {target} artifact before guarded advancement"
    after.setdefault("recovery_history", []).append(
        {
            "failed_stage": failed_stage,
            "resume_target": target,
            "repair_evidence": evidence,
            "invalidated_stage_refs": invalidated,
            "resumed_at": _utc_now(),
        }
    )

    receipt = _new_receipt(
        task_id=str(before["task_id"]),
        stage=failed_stage,
        capability_id="financial_owner_blocked_recovery",
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="RESUME_BLOCKED",
        subject_bindings={"task_id": before["task_id"], "failed_stage": failed_stage, "resume_target": target},
        input_bindings={"repair_evidence": evidence, "invalidated_stage_refs": invalidated},
        output_refs=[_state_path(str(before["task_id"]))],
        state_ref=state_ref,
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    validate_state(after)
    _require(after["execution_receipts"][:-1] == before["execution_receipts"], "prior execution receipts are immutable")
    _require(after["current_stage"] == target, "BLOCKED recovery must use the persisted canonical target")
    return after


def review_system_impact_state(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    signal_id: str,
    problem_statement: str,
    root_cause_layer: str,
    generalization_scope: str,
    alternatives: list[Mapping[str, Any]],
    selected_mechanism: str,
    selection_rationale: str,
    authority_surface: str,
    regression_or_eval_plan: list[str],
    evidence_refs: list[str],
    decision: str,
    decision_reason: str,
    maintenance_ref: str | None = None,
    validation_refs: list[str] | None = None,
    assurance_ceiling: str | None = None,
    remaining_open: list[str] | None = None,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    """Classify or close one material-feedback system-impact obligation.

    Closure is evidence-bound but remains self-attested at the current chat/provider
    assurance level. It never manufactures provider-attested independence.
    """
    _require(state_ref == MAIN_STATE_REF, "Financial owner material mutations must target main")
    validate_state(state)
    before = deepcopy(dict(state))
    _require(bool(str(signal_id).strip()), "signal_id is required")
    _require(decision in SYSTEM_IMPACT_DECISIONS, f"unsupported system-impact decision: {decision}")
    _require(root_cause_layer in ROOT_CAUSE_LAYERS, f"unsupported root_cause_layer: {root_cause_layer}")

    problem = problem_statement.strip()
    scope = generalization_scope.strip()
    selected = selected_mechanism.strip()
    rationale = selection_rationale.strip()
    authority = authority_surface.strip()
    decision_note = decision_reason.strip()
    _require(all([problem, scope, selected, rationale, authority, decision_note]), "system-impact review requires non-empty diagnosis, authority and decision rationale")

    normalized_alternatives = _normalize_alternatives(alternatives)
    _require(selected in {item["mechanism"] for item in normalized_alternatives}, "selected_mechanism must exactly match one reviewed alternative")
    regression_plan = _clean_string_list(regression_or_eval_plan, label="regression_or_eval_plan")
    refs = _clean_string_list(evidence_refs, label="evidence_refs")
    open_items = _clean_string_list(remaining_open, label="remaining_open", required=False)

    open_signals = list(before.get("open_system_impact", []))
    matches = [(index, item) for index, item in enumerate(open_signals) if item.get("signal_id") == signal_id]
    _require(len(matches) == 1, "system-impact signal must exist exactly once in open_system_impact")
    index, original_signal = matches[0]
    _require(original_signal.get("status") in {"OPEN", "MAINTENANCE_REQUIRED"}, "system-impact signal is not open")
    _require(original_signal.get("trigger_sample_type") in MATERIAL_FEEDBACK_TYPES, "system-impact signal must originate from material corrective feedback")

    review_core = {
        "problem_statement": problem,
        "root_cause_layer": root_cause_layer,
        "generalization_scope": scope,
        "alternatives": normalized_alternatives,
        "selected_mechanism": selected,
        "selection_rationale": rationale,
        "authority_surface": authority,
        "regression_or_eval_plan": regression_plan,
        "evidence_refs": refs,
        "decision": decision,
        "decision_reason": decision_note,
    }

    after = deepcopy(before)
    current = deepcopy(after["open_system_impact"][index])
    existing_review = current.get("review")
    action = "SYSTEM_IMPACT_REVIEW"

    if existing_review is None:
        _require(current.get("status") == "OPEN", "first system-impact review requires OPEN status")
        _require(not maintenance_ref and not validation_refs and not assurance_ceiling, "first system-impact review must classify before maintenance closure")
        current["review"] = {**review_core, "reviewed_at": _utc_now()}
        if decision == "SYSTEM_MAINTENANCE_REQUIRED":
            current["status"] = "MAINTENANCE_REQUIRED"
            current["remaining_open"] = open_items or ["evidence-bound maintenance closure remains required"]
            current["control_signal"] = {
                "signal_id": f"fwa-{before['task_id']}-{signal_id}",
                "signal_type": "USER_REPORTED_SYSTEMIC_FAILURE",
                "source": "FINANCIAL_WRITING_AGENT_RUNTIME",
                "observed_at": _utc_now(),
                "subject": f"writing-task:{before['task_id']}:{signal_id}",
                "summary": problem,
                "evidence_refs": list(dict.fromkeys([str(current.get("sample_ref", "")).strip(), f"github-state://{before['task_id']}/open_system_impact/{signal_id}", *refs])) if str(current.get("sample_ref", "")).strip() else list(dict.fromkeys([f"github-state://{before['task_id']}/open_system_impact/{signal_id}", *refs])),
                "severity": "MEDIUM",
                "authority": "NON_AUTHORITATIVE_CONTROL_SIGNAL",
            }
            after["open_system_impact"][index] = current
        else:
            current["status"] = "REVIEWED_NO_MAINTENANCE"
            current["remaining_open"] = open_items
            after["open_system_impact"].pop(index)
            after.setdefault("system_impact_history", []).append(current)
    else:
        comparable_existing = {key: existing_review.get(key) for key in review_core}
        _require(comparable_existing == review_core, "system-impact review diagnosis is immutable across maintenance closure")
        _require(current.get("status") == "MAINTENANCE_REQUIRED", "system-impact signal is not awaiting maintenance closure")
        _require(decision == "SYSTEM_MAINTENANCE_REQUIRED", "maintenance closure cannot change the original decision")
        clean_maintenance_ref = (maintenance_ref or "").strip()
        clean_validation_refs = _clean_string_list(validation_refs, label="validation_refs")
        _require(bool(clean_maintenance_ref), "maintenance closure requires maintenance_ref")
        _require(assurance_ceiling in ASSURANCE_LADDER, "maintenance closure requires a recognized assurance_ceiling")
        _require(
            ASSURANCE_LADDER.index(str(assurance_ceiling)) >= ASSURANCE_LADDER.index("REGRESSION_VERIFIED"),
            "maintenance closure requires evidence labeled at least REGRESSION_VERIFIED",
        )
        current["status"] = "MAINTENANCE_CLOSED"
        current["maintenance_closure"] = {
            "maintenance_ref": clean_maintenance_ref,
            "validation_refs": clean_validation_refs,
            "evidence_assurance_ceiling": assurance_ceiling,
            "closure_attestation": OWNER_CLOSURE_ATTESTATION,
            "receipt_verification_status": SELF_ATTESTED_RECEIPT,
            "remaining_open": open_items,
            "closed_at": _utc_now(),
        }
        current["remaining_open"] = open_items
        after["open_system_impact"].pop(index)
        after.setdefault("system_impact_history", []).append(current)
        action = "SYSTEM_IMPACT_CLOSE"

    receipt = _new_receipt(
        task_id=str(before["task_id"]),
        stage=str(before["current_stage"]),
        capability_id="financial_owner_system_impact_lifecycle",
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind=action,
        subject_bindings={"task_id": before["task_id"], "signal_id": signal_id, "decision": decision},
        input_bindings={
            "problem_statement": problem,
            "authority_surface": authority,
            "maintenance_ref": maintenance_ref,
            "validation_refs": list(validation_refs or []),
            "evidence_assurance_ceiling": assurance_ceiling,
            "closure_attestation": OWNER_CLOSURE_ATTESTATION if action == "SYSTEM_IMPACT_CLOSE" else None,
        },
        output_refs=[_state_path(str(before["task_id"]))],
        state_ref=state_ref,
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    validate_state(after)
    _require(after["execution_receipts"][:-1] == before["execution_receipts"], "prior execution receipts are immutable")
    return after
