from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

from .github_chat_guard import (
    MAIN_STATE_REF,
    GithubChatGuardError,
    _new_receipt,
    _state_path,
    _utc_now,
    validate_state,
)

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
        raise GithubChatGuardError(message)


def _clean_string_list(values: list[str] | None, *, label: str, required: bool = True) -> list[str]:
    cleaned = list(dict.fromkeys(value.strip() for value in (values or []) if isinstance(value, str) and value.strip()))
    if required:
        _require(bool(cleaned), f"{label} requires at least one non-empty item")
    return cleaned


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


def resume_blocked_state(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    repair_evidence: list[str],
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    """Resume one GITHUB_CHAT task conservatively after an explicit BLOCKED repair.

    Current chat-mode FAIL blocks only on a review stage. Recovery reruns that exact
    review stage and invalidates the failed review artifact/decision so stale evidence
    cannot be reused as a new PASS.
    """
    _require(state_ref == MAIN_STATE_REF, "GITHUB_CHAT material mutations must target main")
    validate_state(state)
    before = deepcopy(dict(state))
    _require(before.get("status") == "BLOCKED", "only BLOCKED chat state may be resumed")
    stage = str(before.get("current_stage", ""))
    _require(stage.endswith("AUDIT"), "BLOCKED recovery currently supports canonical review-stage failures only")
    evidence = _clean_string_list(repair_evidence, label="repair_evidence")

    after = deepcopy(before)
    failed_artifact = after.setdefault("stage_artifacts", {}).pop(stage, None)
    failed_review = after.setdefault("review_decisions", {}).pop(stage, None)
    after["status"] = "IN_PROGRESS"
    after["next_action"] = f"persist a fresh {stage} artifact, then rerun the guarded review transition"
    after.setdefault("recovery_history", []).append(
        {
            "recovery_stage": stage,
            "repair_evidence": evidence,
            "invalidated_artifact": failed_artifact,
            "invalidated_review": failed_review,
            "resumed_at": _utc_now(),
        }
    )

    receipt = _new_receipt(
        task_id=str(before["task_id"]),
        stage=stage,
        capability_id="github_chat_blocked_recovery",
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="RESUME_BLOCKED",
        subject_bindings={"task_id": before["task_id"], "from_status": "BLOCKED", "resume_stage": stage},
        input_bindings={"repair_evidence": evidence, "invalidated_failed_stage_artifact": bool(failed_artifact)},
        output_refs=[_state_path(str(before["task_id"]))],
        state_ref=state_ref,
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    validate_state(after)

    _require(after["current_stage"] == before["current_stage"], "blocked recovery may not guess a different stage")
    _require(stage not in after.get("stage_artifacts", {}), "failed review artifact must be invalidated before retry")
    _require(stage not in after.get("review_decisions", {}), "failed review decision must be invalidated before retry")
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
    """Classify or close one GITHUB_CHAT material-feedback system-impact obligation.

    This mirrors the owner-native business lifecycle at CHAT_SELF_REVIEW assurance:
    OPEN -> reviewed local close, or OPEN -> MAINTENANCE_REQUIRED -> verified closure.
    It does not fabricate owner-native methodology receipts.
    """
    _require(state_ref == MAIN_STATE_REF, "GITHUB_CHAT material mutations must target main")
    validate_state(state)
    before = deepcopy(dict(state))
    _require(bool(str(signal_id).strip()), "signal_id is required")
    _require(decision in SYSTEM_IMPACT_DECISIONS, f"unsupported system-impact decision: {decision}")

    problem = problem_statement.strip()
    scope = generalization_scope.strip()
    selected = selected_mechanism.strip()
    rationale = selection_rationale.strip()
    authority = authority_surface.strip()
    decision_note = decision_reason.strip()
    _require(all([problem, root_cause_layer.strip(), scope, selected, rationale, authority, decision_note]), "system-impact review requires non-empty diagnosis, authority and decision rationale")

    normalized_alternatives = _normalize_alternatives(alternatives)
    _require(selected in {item["mechanism"] for item in normalized_alternatives}, "selected_mechanism must exactly match one reviewed alternative")
    regression_plan = _clean_string_list(regression_or_eval_plan, label="regression_or_eval_plan")
    refs = _clean_string_list(evidence_refs, label="evidence_refs")
    open_items = _clean_string_list(remaining_open, label="remaining_open", required=False)

    open_signals = list(before.get("open_system_impact", []))
    matches = [(index, item) for index, item in enumerate(open_signals) if item.get("signal_id") == signal_id]
    _require(len(matches) == 1, "system-impact signal must exist exactly once in open_system_impact")
    index, existing = matches[0]
    review_core = {
        "problem_statement": problem,
        "root_cause_layer": root_cause_layer.strip(),
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
        _require(not maintenance_ref and not validation_refs and not assurance_ceiling, "first system-impact review must classify before maintenance closure")
        current["review"] = {**review_core, "reviewed_at": _utc_now()}
        if decision == "SYSTEM_MAINTENANCE_REQUIRED":
            current["status"] = "MAINTENANCE_REQUIRED"
            current["remaining_open"] = open_items or ["verified maintenance closure evidence is required"]
            current["control_signal"] = {
                "signal_id": f"fwa-{before['task_id']}-{signal_id}",
                "signal_type": "USER_REPORTED_SYSTEMIC_FAILURE",
                "source": "FINANCIAL_WRITING_AGENT_RUNTIME:GITHUB_CHAT",
                "subject": f"writing-task:{before['task_id']}:{signal_id}",
                "summary": problem,
                "evidence_refs": refs,
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
            "maintenance closure requires at least REGRESSION_VERIFIED evidence",
        )
        current["status"] = "MAINTENANCE_CLOSED"
        current["maintenance_closure"] = {
            "maintenance_ref": clean_maintenance_ref,
            "validation_refs": clean_validation_refs,
            "assurance_ceiling": assurance_ceiling,
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
        capability_id="github_chat_system_impact_lifecycle",
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind=action,
        subject_bindings={"task_id": before["task_id"], "signal_id": signal_id, "decision": decision},
        input_bindings={
            "problem_statement": problem,
            "authority_surface": authority,
            "maintenance_ref": maintenance_ref,
            "validation_refs": list(validation_refs or []),
            "assurance_ceiling": assurance_ceiling,
        },
        output_refs=[_state_path(str(before["task_id"]))],
        state_ref=state_ref,
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    validate_state(after)
    return after
