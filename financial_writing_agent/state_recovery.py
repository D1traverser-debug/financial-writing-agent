from __future__ import annotations

from .models import GateStatus, Stage, WritingState
from .workflow_spec import invalidated_gate_names_from

PENDING_REVISION_CLEANUP = "_pending_revision_cleanup"

# These keys are adapter/runtime payloads rather than business-stage graph truth. The
# gate dependency set itself is always derived from workflow_spec.
REVISION_CLEAR_WORKING_KEYS: dict[Stage, tuple[str, ...]] = {
    Stage.RESEARCH: (
        "editorial_plan", "headlines", "draft", "hook_audit", "style_audit",
        "render_manifest", "revise_target", "final_revise_target",
    ),
    Stage.EDITORIAL: (
        "headlines", "draft", "hook_audit", "style_audit", "render_manifest",
        "revise_target", "final_revise_target",
    ),
    Stage.TITLE: (
        "draft", "hook_audit", "style_audit", "render_manifest", "revise_target", "final_revise_target",
    ),
    Stage.DRAFT: (
        "hook_audit", "style_audit", "render_manifest", "revise_target", "final_revise_target",
    ),
    Stage.DELIVERY: ("render_manifest", "final_revise_target"),
}


def _target_stage(target: str) -> Stage:
    try:
        stage = Stage(target)
    except ValueError as exc:
        raise ValueError(f"unsupported revision target: {target}") from exc
    if stage not in REVISION_CLEAR_WORKING_KEYS:
        raise ValueError(f"unsupported revision target: {target}")
    return stage


def mark_revision_cleanup(state: WritingState, target: str, *, reason: str) -> None:
    stage = _target_stage(target)
    state.working[PENDING_REVISION_CLEANUP] = {
        "target": stage.value,
        "reason": reason.strip() or f"revision cleanup target={stage.value}",
    }


def apply_revision_cleanup(state: WritingState, target: str, *, reason: str) -> None:
    target_stage = _target_stage(target)
    clean_reason = reason.strip() or f"revision cleanup target={target_stage.value}"

    for gate_name in invalidated_gate_names_from(target_stage):
        if gate_name in state.gates:
            state.set_gate(gate_name, GateStatus.NOT_RUN, [], clean_reason)

    for key in REVISION_CLEAR_WORKING_KEYS[target_stage]:
        state.working.pop(key, None)

    state.artifacts.clear()
    state.working.pop("output_dir", None)
    state.working.pop("render_manifest", None)

    if target_stage == Stage.RESEARCH:
        if "knowledge_sync" in state.gates:
            state.set_gate("knowledge_sync", GateStatus.NOT_RUN, [], clean_reason)
        state.working.pop("knowledge_writeback_refs", None)
        state.working.pop("knowledge_writeback_notes", None)

    state.working.pop(PENDING_REVISION_CLEANUP, None)
    state.add_trace("QA_INVALIDATED", clean_reason)


def reconcile_pending_revision_cleanup(state: WritingState) -> bool:
    """Repair a crash between revision transition and downstream invalidation.

    Returns True only when an actual recovery mutation was applied. The persistence
    layer owns the subsequent durable save so every owner-native entrypoint sees the
    same healed state before business execution resumes.
    """
    pending = state.working.get(PENDING_REVISION_CLEANUP)
    if pending is None:
        return False
    if not isinstance(pending, dict):
        raise ValueError("pending revision cleanup marker is malformed")

    target = str(pending.get("target", ""))
    target_stage = _target_stage(target)
    if state.stage != target_stage:
        raise ValueError(
            f"pending revision cleanup stage mismatch: current={state.stage.value}, target={target_stage.value}"
        )

    reason = str(pending.get("reason", "")).strip() or "recover pending revision cleanup"
    apply_revision_cleanup(state, target_stage.value, reason=reason)
    state.add_trace("RECOVERY_RECONCILED", f"completed pending revision cleanup target={target_stage.value}")
    return True
