from __future__ import annotations

from copy import deepcopy
from uuid import uuid4
from typing import Any, Mapping

from . import current_admission, owner_guard
from .models import Stage
from .owner_guard import (
    MAIN_STATE_REF,
    SELF_ATTESTED_RECEIPT,
    GithubChatGuardError as OwnerGuardError,
    _admit_historical_material_resume,
    _invalidate_from,
    _new_receipt,
    _state_path,
    _utc_now,
)
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


def _is_current(state: Mapping[str, Any]) -> bool:
    return state.get("writing_kernel_version") == current_admission.WRITING_KERNEL_VERSION


def _validate_owner_state(state: Mapping[str, Any]) -> None:
    if _is_current(state):
        current_admission.validate_state(state)
    else:
        owner_guard.validate_state(state)


def _bind_current_after_mutation(state: dict[str, Any]) -> None:
    if _is_current(state):
        current_admission.bind_current_governance_receipt(state)


def _advance_owner_state(state: Mapping[str, Any], **kwargs: Any) -> dict[str, Any]:
    if _is_current(state):
        return current_admission.advance_state(state, **kwargs)
    return owner_guard.advance_state(state, **kwargs)


def block_review_failure_state(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    artifact_key: str,
    artifact_path: str,
    artifact_blob_sha: str,
    revision_target: str,
    resume_intent: str | None = None,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    """Persist a review FAIL together with its canonical repair target."""
    _require(state_ref == MAIN_STATE_REF, "Financial owner material mutations must target main")
    _validate_owner_state(state)
    stage = str(state.get("current_stage", ""))
    _require(stage in REVIEW_STAGE_NAMES, "review failure blocking requires a canonical review stage")
    allowed = _allowed_revision_targets(stage)
    _require(revision_target in allowed, f"{stage} FAIL revision_target must be one of {sorted(allowed)}")

    blocked = _advance_owner_state(
        state,
        previous_state_blob_sha=previous_state_blob_sha,
        executor_identity=executor_identity,
        artifact_key=artifact_key,
        artifact_path=artifact_path,
        artifact_blob_sha=artifact_blob_sha,
        review_status="FAIL",
        revision_target=revision_target,
        resume_intent=resume_intent,
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
    resume_intent: str | None = None,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    """Resume a blocked review through the target chosen when the FAIL was persisted."""
    _require(state_ref == MAIN_STATE_REF, "Financial owner material mutations must target main")
    _validate_owner_state(state)
    historical_resume = _admit_historical_material_resume(state, resume_intent=resume_intent)
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

    input_bindings: dict[str, Any] = {"repair_evidence": evidence, "invalidated_stage_refs": invalidated}
    if historical_resume is not None:
        input_bindings["historical_resume_decision"] = historical_resume["decision"]
        input_bindings["historical_resume_reason"] = historical_resume["reason"]

    receipt = _new_receipt(
        task_id=str(before["task_id"]),
        stage=failed_stage,
        capability_id="financial_owner_blocked_recovery",
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="RESUME_BLOCKED",
        subject_bindings={"task_id": before["task_id"], "failed_stage": failed_stage, "resume_target": target},
        input_bindings=input_bindings,
        output_refs=[_state_path(str(before["task_id"]))],
        state_ref=state_ref,
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    _bind_current_after_mutation(after)
    _validate_owner_state(after)
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
    _validate_owner_state(state)
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
    _bind_current_after_mutation(after)
    _validate_owner_state(after)
    _require(after["execution_receipts"][:-1] == before["execution_receipts"], "prior execution receipts are immutable")
    return after


def record_nonbinding_intent_state(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    verified_intent: Mapping[str, Any],
    summary: str,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    """Retain the owner's suggestion/idea/issue WITHOUT mutating active requirements.

    The trusted Financial provider port verifies the original user text before
    calling this owner-native transition. This history is one field on the same
    Article Aggregate, not another goal or task registry.
    """
    from .intent_governance import NONBINDING_KINDS

    _require(state_ref == MAIN_STATE_REF, "Financial owner intents may target only main")
    current_admission.validate_state(state)
    _require(bool(str(previous_state_blob_sha).strip()), "intent requires prior Git blob")
    _require(bool(str(executor_identity).strip()), "intent requires executor_identity")
    _require(isinstance(verified_intent, Mapping)
             and verified_intent.get("verified") is True
             and verified_intent.get("intent") in NONBINDING_KINDS,
             "nonbinding intent requires trusted verified source")
    _require(isinstance(summary, str) and bool(summary.strip()),
             "nonbinding intent requires an interpreted summary")
    original = deepcopy(dict(state))
    after = deepcopy(original)
    entries = list(after.get("intent_history", []))
    _require(not any(
        item.get("source_ref") == verified_intent["source_ref"]
        and item.get("excerpt_sha256") == verified_intent["excerpt_sha256"]
        and item.get("intent") == verified_intent["intent"]
        for item in entries
    ), "duplicate nonbinding intent; reconcile existing record rather than replay")

    intent_id = f"financial-owner-intent:{uuid4()}"
    entry = {
        "intent_id": intent_id,
        "intent": verified_intent["intent"],
        "source_ref": verified_intent["source_ref"],
        "source_sha256": verified_intent["source_sha256"],
        "excerpt_sha256": verified_intent["excerpt_sha256"],
        "summary": summary.strip(),
        "status": "OPEN__NONBINDING",
        "recorded_at": _utc_now(),
    }
    after["intent_history"] = entries + [entry]
    receipt = _new_receipt(
        task_id=str(after["task_id"]),
        stage=str(after["current_stage"]),
        capability_id="financial_owner_intent_intake",
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="NONBINDING_OWNER_INTENT",
        subject_bindings={
            "task_id": after["task_id"], "intent_id": intent_id,
            "intent": verified_intent["intent"],
        },
        input_bindings={
            "source_ref": entry["source_ref"],
            "source_sha256": entry["source_sha256"],
            "excerpt_sha256": entry["excerpt_sha256"],
            "status": entry["status"],
        },
        output_refs=[_state_path(str(after["task_id"]))],
        state_ref=state_ref,
    )
    after["execution_receipts"] = list(original["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    current_admission.bind_current_governance_receipt(after)
    current_admission.validate_state(after)
    _require(after["task_requirement_authority"] == original["task_requirement_authority"],
             "nonbinding proposal must never change active user requirements")
    _require(after["task_requirement_digest"] == original["task_requirement_digest"],
             "nonbinding proposal must not change requirement digest")
    return after


def reopen_method_dependent_article_state(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    method_dependency_changes: list[Mapping[str, Any]],
    verified_catalog_blob_sha: str,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    """Reopen earliest affected owner stage after provider-verified method drift.

    This is not a second business graph. The Financial method catalog supplies
    the change-event evidence, and the existing owner graph invalidates only
    descendants of the earliest affected stage, preserving all prior receipts.
    """
    from . import current_admission as admission

    _require(state_ref == MAIN_STATE_REF, "method dependency reopens only Financial main state")
    admission.validate_state(state)
    _require(bool(previous_state_blob_sha and executor_identity),
             "method reopen needs prior state and authorized executor")
    _require(isinstance(verified_catalog_blob_sha, str)
             and len(verified_catalog_blob_sha) == 40,
             "method reopen requires verified Git catalog Blob SHA")
    _require(isinstance(method_dependency_changes, list)
             and bool(method_dependency_changes), "no actual method dependency drift")
    earliest = min(
        (str(item["earliest_affected_stage"]) for item in method_dependency_changes),
        key=lambda name: owner_guard.STAGE_INDEX[name],
    )
    _require(earliest in owner_guard.STAGE_INDEX, "method affected stage is noncanonical")
    old_stage = str(state["current_stage"])
    _require(owner_guard.STAGE_INDEX[old_stage] >= owner_guard.STAGE_INDEX[earliest],
             "method change affects a future stage, no current rollback required")
    working = deepcopy(dict(state))
    admission._archive_invalidated_quality(
        working, reason="METHOD_CATALOG_DEPENDENCY_CHANGE",
        earliest_stage=earliest,
    )
    invalidated = owner_guard._invalidate_from(working, earliest)
    working["status"] = "IN_PROGRESS"
    working["current_stage"] = earliest
    working["next_action"] = (
        f"re-evaluate {earliest} with current verified Financial method catalog "
        "and new method candidate/alternatives"
    )
    working.setdefault("method_dependency_reopen_history", []).append({
        "from_stage": old_stage,
        "to_stage": earliest,
        "changed_methods": deepcopy(method_dependency_changes),
        "catalog_blob_sha": verified_catalog_blob_sha,
        "invalidated_stage_refs": invalidated,
        "reopened_at": _utc_now(),
    })
    receipt = _new_receipt(
        task_id=str(working["task_id"]),
        stage=old_stage,
        capability_id="financial_method_dependency_revalidation",
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="REOPEN_METHOD_DEPENDENCY",
        subject_bindings={
            "task_id": working["task_id"],
            "from_stage": old_stage, "to_stage": earliest,
            "knowledge_ids": [item["knowledge_id"] for item in method_dependency_changes],
        },
        input_bindings={
            "verified_method_catalog_blob_sha": verified_catalog_blob_sha,
            "changed_methods": deepcopy(method_dependency_changes),
            "invalidated_stage_refs": invalidated,
        },
        output_refs=[_state_path(str(working["task_id"]))],
        state_ref=state_ref,
    )
    working["execution_receipts"] = list(state["execution_receipts"]) + [receipt]
    working["updated_at"] = _utc_now()
    admission.bind_current_governance_receipt(working)
    admission.validate_state(working)
    _require(working["execution_receipts"][:-1] == state["execution_receipts"],
             "method reopen must not rewrite old execution receipts")
    return working
