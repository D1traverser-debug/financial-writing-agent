from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import WritingState

SYSTEM_IMPACT_REVIEW_SAMPLE_TYPES = {"USER_EDIT", "USER_FEEDBACK", "USER_REJECTION"}
OPEN_SYSTEM_IMPACT_STATUSES = {"PENDING_REVIEW", "MAINTENANCE_REQUIRED"}
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


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _signals(state: WritingState) -> list[dict[str, Any]]:
    return state.working.setdefault("system_impact_signals", [])


def system_impact_signal_ref(state: WritingState, signal_id: str) -> str:
    return f"writingstate://{state.contract.task_id}/system_impact_signals/{signal_id}"


def system_impact_review_ref(state: WritingState, signal_id: str) -> str:
    return f"writingstate://{state.contract.task_id}/system_impact_signals/{signal_id}/review"


def _find_signal(state: WritingState, signal_id: str) -> dict[str, Any]:
    for signal in _signals(state):
        if signal.get("signal_id") == signal_id:
            return signal
    raise ValueError(f"system impact signal not found: {signal_id}")


def open_system_impact_signals(state: WritingState) -> list[dict[str, Any]]:
    return [signal for signal in _signals(state) if signal.get("status") in OPEN_SYSTEM_IMPACT_STATUSES]


def pending_system_impact_reviews(state: WritingState) -> list[dict[str, Any]]:
    return [signal for signal in _signals(state) if signal.get("status") == "PENDING_REVIEW"]


def ensure_system_impact_signal_for_latest_sample(state: WritingState) -> dict[str, Any] | None:
    samples = state.working.get("learning_samples") or []
    if not samples:
        raise ValueError("cannot evaluate system impact without persisted learning evidence")
    sample_index = len(samples) - 1
    sample = samples[sample_index]
    if sample.get("sample_type") not in SYSTEM_IMPACT_REVIEW_SAMPLE_TYPES:
        return None

    existing_id = sample.get("system_impact_signal_id")
    if existing_id:
        return _find_signal(state, str(existing_id))

    signal_id = f"impact-{sample_index + 1:04d}"
    sample_ref = f"writingstate://{state.contract.task_id}/learning_samples/{sample_index}"
    signal = {
        "signal_id": signal_id,
        "signal_type": "WRITING_QUALITY_SYSTEM_IMPACT_REVIEW",
        "status": "PENDING_REVIEW",
        "trigger_sample_type": sample["sample_type"],
        "sample_ref": sample_ref,
        "created_at": _now(),
        "review": None,
        "control_signal": None,
        "maintenance_closure": None,
    }
    sample["system_impact_signal_id"] = signal_id
    _signals(state).append(signal)
    state.add_trace(
        "SYSTEM_IMPACT_REVIEW_REQUIRED",
        f"signal={signal_id}; sample_type={sample['sample_type']}; sample_ref={sample_ref}",
    )
    return signal


def _normalize_alternatives(alternatives: list[dict[str, str]]) -> list[dict[str, str]]:
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in alternatives:
        mechanism = str(raw.get("mechanism", "")).strip()
        failure_mode = str(raw.get("failure_mode", "")).strip()
        if not mechanism or not failure_mode:
            raise ValueError("each system-impact alternative requires mechanism and failure_mode")
        if mechanism in seen:
            raise ValueError("system-impact alternatives must use distinct mechanisms")
        seen.add(mechanism)
        normalized.append({"mechanism": mechanism, "failure_mode": failure_mode})
    if len(normalized) < 2:
        raise ValueError("system-impact review requires at least two credible alternatives")
    return normalized


def _clean_nonempty_list(values: list[str] | None, *, label: str, required: bool = True) -> list[str]:
    cleaned = list(dict.fromkeys(value.strip() for value in (values or []) if isinstance(value, str) and value.strip()))
    if required and not cleaned:
        raise ValueError(f"{label} requires at least one non-empty item")
    return cleaned


def apply_system_impact_review(
    state: WritingState,
    *,
    signal_id: str,
    problem_statement: str,
    root_cause_layer: str,
    generalization_scope: str,
    alternatives: list[dict[str, str]],
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
) -> dict[str, Any]:
    signal = _find_signal(state, signal_id)
    if root_cause_layer not in ROOT_CAUSE_LAYERS:
        raise ValueError(f"unsupported root_cause_layer: {root_cause_layer}")
    if decision not in SYSTEM_IMPACT_DECISIONS:
        raise ValueError(f"unsupported system-impact decision: {decision}")

    problem = problem_statement.strip()
    scope = generalization_scope.strip()
    selected = selected_mechanism.strip()
    rationale = selection_rationale.strip()
    authority = authority_surface.strip()
    decision_note = decision_reason.strip()
    if not all([problem, scope, selected, rationale, authority, decision_note]):
        raise ValueError("system-impact review requires non-empty diagnosis, selection, authority and decision rationale")

    normalized_alternatives = _normalize_alternatives(alternatives)
    if selected not in {item["mechanism"] for item in normalized_alternatives}:
        raise ValueError("selected_mechanism must exactly match one reviewed alternative")
    regression_plan = _clean_nonempty_list(regression_or_eval_plan, label="regression_or_eval_plan")
    refs = _clean_nonempty_list(evidence_refs, label="evidence_refs")
    open_items = _clean_nonempty_list(remaining_open, label="remaining_open", required=False)

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

    existing_review = signal.get("review")
    if existing_review is None:
        if maintenance_ref or validation_refs or assurance_ceiling:
            raise ValueError("first system-impact review must classify/escalate before maintenance closure is attached")
        signal["review"] = {**review_core, "reviewed_at": _now()}
        if decision == "SYSTEM_MAINTENANCE_REQUIRED":
            observed_at = _now()
            control_signal_id = f"fwa-{state.contract.task_id}-{signal_id}"
            signal["status"] = "MAINTENANCE_REQUIRED"
            signal["control_signal"] = {
                "signal_id": control_signal_id,
                "signal_type": "USER_REPORTED_SYSTEMIC_FAILURE",
                "source": "FINANCIAL_WRITING_AGENT_RUNTIME",
                "observed_at": observed_at,
                "subject": f"writing-task:{state.contract.task_id}:{signal_id}",
                "summary": problem,
                "evidence_refs": list(dict.fromkeys([signal["sample_ref"], *refs])),
                "severity": "MEDIUM",
                "authority": "NON_AUTHORITATIVE_CONTROL_SIGNAL",
            }
            signal["remaining_open"] = open_items or ["Universal maintenance/evolution closure evidence is required"]
            state.add_trace(
                "SYSTEM_MAINTENANCE_REQUIRED",
                f"signal={signal_id}; control_signal={control_signal_id}; root_cause={root_cause_layer}",
            )
        else:
            signal["status"] = "REVIEWED_NO_MAINTENANCE"
            signal["remaining_open"] = open_items
            state.add_trace(
                "SYSTEM_IMPACT_REVIEW_CLOSED_LOCAL",
                f"signal={signal_id}; decision={decision}; root_cause={root_cause_layer}",
            )
        return signal

    comparable_existing = {key: existing_review.get(key) for key in review_core}
    if comparable_existing != review_core:
        raise ValueError("system-impact review diagnosis is immutable; maintenance closure must reuse the exact accepted review")
    if signal.get("status") != "MAINTENANCE_REQUIRED":
        raise ValueError("system-impact signal is already closed and cannot be re-reviewed")
    if decision != "SYSTEM_MAINTENANCE_REQUIRED":
        raise ValueError("maintenance closure cannot change the original system-impact decision")

    clean_maintenance_ref = (maintenance_ref or "").strip()
    clean_validation_refs = _clean_nonempty_list(validation_refs, label="validation_refs")
    if not clean_maintenance_ref:
        raise ValueError("maintenance closure requires maintenance_ref")
    if assurance_ceiling not in ASSURANCE_LADDER:
        raise ValueError("maintenance closure requires a recognized assurance_ceiling")
    if ASSURANCE_LADDER.index(assurance_ceiling) < ASSURANCE_LADDER.index("REGRESSION_VERIFIED"):
        raise ValueError("maintenance closure requires at least REGRESSION_VERIFIED evidence")

    signal["maintenance_closure"] = {
        "maintenance_ref": clean_maintenance_ref,
        "validation_refs": clean_validation_refs,
        "assurance_ceiling": assurance_ceiling,
        "remaining_open": open_items,
        "closed_at": _now(),
    }
    signal["status"] = "MAINTENANCE_CLOSED"
    signal["remaining_open"] = open_items
    state.add_trace(
        "SYSTEM_MAINTENANCE_CLOSED",
        f"signal={signal_id}; assurance={assurance_ceiling}; maintenance_ref={clean_maintenance_ref}",
    )
    return signal


def system_impact_next_action(state: WritingState) -> str | None:
    pending = pending_system_impact_reviews(state)
    if pending:
        return (
            f"call review_writing_system_impact for signal={pending[0]['signal_id']} before treating the material "
            "writing feedback as locally closed; compare at least two mechanisms and record failure modes"
        )
    maintenance = [signal for signal in _signals(state) if signal.get("status") == "MAINTENANCE_REQUIRED"]
    if maintenance:
        control = maintenance[0].get("control_signal") or {}
        return (
            f"consume system-impact signal={maintenance[0]['signal_id']} control_signal={control.get('signal_id', 'UNKNOWN')} "
            "through the current Universal operational_hygiene@1.0 + evolution@1.0 maintenance loop; after verified "
            "maintenance, call review_writing_system_impact again with the exact maintenance and validation refs"
        )
    return None
