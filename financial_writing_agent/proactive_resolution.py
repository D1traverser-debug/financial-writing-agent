from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping
from uuid import uuid4

from .current_admission import bind_current_governance_receipt, validate_state
from .owner_guard import MAIN_STATE_REF, _new_receipt, _state_path, _utc_now


class ProactiveResolutionError(ValueError):
    pass


OUTCOMES = {"RESOLVED", "PROVISIONAL", "UNRESOLVED"}
CONFIDENCE_LEVELS = {"HIGH", "MEDIUM", "LOW", "NONE"}
ESCALATION_REASONS = {
    "UNRESOLVED_MATERIAL_AMBIGUITY",
    "FABRICATION_RISK",
    "REQUIRED_EVIDENCE_UNAVAILABLE",
    "USER_EXPLICIT_CONFIRMATION",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ProactiveResolutionError(message)


def _clean(values: list[str] | None, *, label: str, required: bool = True) -> list[str]:
    cleaned = list(dict.fromkeys(v.strip() for v in (values or []) if isinstance(v, str) and v.strip()))
    if required:
        _require(bool(cleaned), f"{label} requires at least one non-empty item")
    return cleaned


def _nonempty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def record_proactive_resolution_state(
    state: Mapping[str, Any],
    *,
    previous_state_blob_sha: str,
    executor_identity: str,
    target: str,
    attempted_sources: list[str],
    evidence_refs: list[str],
    outcome: str,
    candidate: str | None = None,
    confidence: str = "NONE",
    contradictions_or_unknowns: list[str] | None = None,
    validation_plan: list[str] | None = None,
    safe_to_continue: bool,
    state_ref: str = MAIN_STATE_REF,
) -> dict[str, Any]:
    """Persist one owner-native recovery attempt through the current Article Aggregate.

    This is an action receipt, not a claim that the recovered candidate is true. A
    provisional candidate remains bounded by its evidence, confidence and validation
    plan. The caller records the concrete sources it actually inspected.
    """

    _require(state_ref == MAIN_STATE_REF, "Financial proactive resolution must target main owner state")
    validate_state(state)
    _require(_nonempty(target), "target is required")
    _require(outcome in OUTCOMES, f"unsupported outcome: {outcome}")
    _require(confidence in CONFIDENCE_LEVELS, f"unsupported confidence: {confidence}")
    sources = _clean(attempted_sources, label="attempted_sources")
    refs = _clean(evidence_refs, label="evidence_refs")
    unknowns = _clean(contradictions_or_unknowns, label="contradictions_or_unknowns", required=False)
    plan = _clean(validation_plan, label="validation_plan", required=False)
    candidate_text = (candidate or "").strip()

    if outcome == "RESOLVED":
        _require(candidate_text != "", "RESOLVED requires a concrete evidence-bound candidate/result")
        _require(safe_to_continue, "RESOLVED must be safe_to_continue")
        _require(confidence in {"HIGH", "MEDIUM"}, "RESOLVED requires HIGH or MEDIUM confidence")
    elif outcome == "PROVISIONAL":
        _require(candidate_text != "", "PROVISIONAL requires a concrete provisional candidate")
        _require(safe_to_continue, "PROVISIONAL must be safe_to_continue")
        _require(confidence in {"HIGH", "MEDIUM", "LOW"}, "PROVISIONAL requires bounded non-NONE confidence")
        _require(bool(plan), "PROVISIONAL requires a validation_plan")
    else:
        _require(not safe_to_continue, "UNRESOLVED cannot be marked safe_to_continue")
        _require(bool(unknowns), "UNRESOLVED requires contradictions_or_unknowns explaining why progress is unsafe")

    before = deepcopy(dict(state))
    after = deepcopy(before)
    attempt_id = f"proactive-resolution:{uuid4()}"
    entry = {
        "attempt_id": attempt_id,
        "target": target.strip(),
        "attempted_sources": sources,
        "evidence_refs": refs,
        "outcome": outcome,
        "candidate": candidate_text or None,
        "confidence": confidence,
        "contradictions_or_unknowns": unknowns,
        "validation_plan": plan,
        "safe_to_continue": safe_to_continue,
        "recorded_at": _utc_now(),
    }
    after.setdefault("proactive_resolution_history", []).append(entry)

    receipt = _new_receipt(
        task_id=str(before["task_id"]),
        stage=str(before["current_stage"]),
        capability_id="financial_owner_proactive_resolution_admission",
        executor_identity=executor_identity,
        previous_state_blob_sha=previous_state_blob_sha,
        action_kind="PROACTIVE_RESOLUTION",
        subject_bindings={"task_id": before["task_id"], "target": target.strip(), "attempt_id": attempt_id},
        input_bindings={
            "attempted_sources": sources,
            "evidence_refs": refs,
            "outcome": outcome,
            "confidence": confidence,
            "safe_to_continue": safe_to_continue,
            "contradictions_or_unknowns": unknowns,
            "validation_plan": plan,
        },
        output_refs=[_state_path(str(before["task_id"]))],
        state_ref=state_ref,
    )
    after["execution_receipts"] = list(before["execution_receipts"]) + [receipt]
    after["updated_at"] = _utc_now()
    bind_current_governance_receipt(after)
    validate_state(after)
    return after


def latest_resolution_for_target(state: Mapping[str, Any], target: str) -> Mapping[str, Any] | None:
    wanted = target.strip()
    for item in reversed(list(state.get("proactive_resolution_history", []))):
        if item.get("target") == wanted:
            return item
    return None


def proactive_resolution_disposition(state: Mapping[str, Any], target: str) -> str:
    latest = latest_resolution_for_target(state, target)
    _require(latest is not None, "no proactive-resolution attempt exists for target")
    outcome = latest.get("outcome")
    if outcome == "RESOLVED":
        return "CONTINUE_WITH_RESOLVED_EVIDENCE"
    if outcome == "PROVISIONAL" and latest.get("safe_to_continue") is True:
        return "CONTINUE_WITH_PROVISIONAL_CANDIDATE"
    if outcome == "UNRESOLVED" and latest.get("safe_to_continue") is False:
        return "USER_ESCALATION_ELIGIBLE"
    raise ProactiveResolutionError("latest proactive-resolution entry has no valid disposition")


def require_user_escalation_admission(state: Mapping[str, Any], *, target: str, reason: str) -> Mapping[str, Any]:
    """Fail closed when the Agent tries to externalize a recoverable dependency too early."""

    validate_state(state)
    _require(reason in ESCALATION_REASONS, f"unsupported escalation reason: {reason}")

    if reason == "USER_EXPLICIT_CONFIRMATION":
        return {"decision": "USER_ESCALATION_ADMITTED", "reason": reason, "attempt_id": None}

    latest = latest_resolution_for_target(state, target)
    _require(latest is not None, "user escalation denied: no proactive-resolution attempt exists for target")
    _require(
        latest.get("outcome") == "UNRESOLVED" and latest.get("safe_to_continue") is False,
        "user escalation denied: available recovery produced a safe resolved/provisional path; continue with that evidence-bound result instead",
    )
    _require(bool(latest.get("contradictions_or_unknowns")), "user escalation denied: unresolved attempt has no concrete blocker/unknown")
    return {
        "decision": "USER_ESCALATION_ADMITTED",
        "reason": reason,
        "attempt_id": latest.get("attempt_id"),
        "target": target.strip(),
    }
