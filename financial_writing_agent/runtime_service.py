from __future__ import annotations

from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any

from .adapters.deterministic import DeliveryExecutor, MechanicalAuditExecutor, finalize_audit_artifact
from .controller import WorkflowController
from .engine import WorkflowError, WritingEngine
from .models import GateStatus, Stage, WritingState
from .routing import build_task_contract
from .schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, HookAuditDecision, ResearchPackage, StyleAuditDecision
from .state_recovery import apply_revision_cleanup as _apply_revision_cleanup
from .state_recovery import mark_revision_cleanup as _mark_revision_cleanup
from .store import SQLiteStateStore
from .system_impact import open_system_impact_signals, system_impact_next_action
from .workflow_spec import invalidated_gate_names_from, revision_targets

DATA_DIR = Path(os.getenv("FINANCIAL_WRITING_DATA_DIR", "/data"))
DB_PATH = Path(os.getenv("FINANCIAL_WRITING_DB", str(DATA_DIR / "financial_writing_state.db")))
RUNS_DIR = Path(os.getenv("FINANCIAL_WRITING_RUNS", str(DATA_DIR / "runs")))
REQUIRE_RENDER = os.getenv("FINANCIAL_WRITING_REQUIRE_RENDER", "1").lower() not in {"0", "false", "no"}

LEARNING_SAMPLE_TYPES = {
    "USER_EDIT",
    "USER_FEEDBACK",
    "USER_ACCEPTANCE",
    "USER_REJECTION",
    "POST_PUBLICATION_PERFORMANCE",
}

store = SQLiteStateStore(DB_PATH)
engine = WritingEngine(store)
controller = WorkflowController(engine)


def _load(task_id: str) -> WritingState:
    # SQLiteStateStore restores every task through the shared state_recovery boundary,
    # so all owner-native entrypoints consume the same crash-reconciled view.
    state = store.load(task_id)
    if state is None:
        raise ValueError(f"task not found: {task_id}")
    return state


def _require_stage(state: WritingState, expected: Stage) -> None:
    if state.stage != expected:
        raise ValueError(f"task {state.contract.task_id} is at {state.stage.value}, expected {expected.value}")


def _gate_status(state: WritingState, name: str) -> str:
    gate = state.gates.get(name)
    return gate.status.value if gate else "NOT_RUN"


def _invalidate(
    state: WritingState,
    gate_names: tuple[str, ...],
    *,
    reason: str,
    clear_artifacts: bool = False,
    clear_working_keys: tuple[str, ...] = (),
) -> None:
    for name in gate_names:
        if name in state.gates:
            state.set_gate(name, GateStatus.NOT_RUN, [], reason)
    for key in clear_working_keys:
        state.working.pop(key, None)
    if clear_artifacts:
        state.artifacts.clear()
        state.working.pop("output_dir", None)
        state.working.pop("render_manifest", None)
    state.add_trace("QA_INVALIDATED", reason)


def _invalidate_knowledge_writeback(state: WritingState, reason: str) -> None:
    if "knowledge_sync" in state.gates:
        state.set_gate("knowledge_sync", GateStatus.NOT_RUN, [], reason)
    state.working.pop("knowledge_writeback_refs", None)
    state.working.pop("knowledge_writeback_notes", None)


def _canonical_revision_target_names(stage: Stage) -> set[str]:
    return {target.value for target in revision_targets(stage)}


def _cleanup_after_revision(state: WritingState, target: str, *, reason: str) -> None:
    _apply_revision_cleanup(state, target, reason=reason)
    store.save(state)


def _invalidate_for_stage_change(
    state: WritingState,
    stage: Stage,
    *,
    reason: str,
    clear_working_keys: tuple[str, ...],
    invalidate_knowledge: bool = False,
) -> None:
    _invalidate(
        state,
        invalidated_gate_names_from(stage),
        reason=reason,
        clear_artifacts=True,
        clear_working_keys=clear_working_keys,
    )
    if invalidate_knowledge:
        _invalidate_knowledge_writeback(state, reason)


def _completion_checklist(state: WritingState) -> dict[str, Any]:
    research = state.working.get("research") or {}
    cognition = research.get("cognition") or {}
    return {
        "runtime_gates": "PASS" if state.stage == Stage.COMPLETE else "INCOMPLETE",
        "research_evidence": _gate_status(state, "research_audit"),
        "editorial": {
            "general_editorial": _gate_status(state, "editorial_audit"),
            "reader_funnel": _gate_status(state, "hook_audit"),
            "authorial_prose": _gate_status(state, "style_audit"),
        },
        "bold_skim_path": _gate_status(state, "mechanical_audit"),
        "word_render": _gate_status(state, "mechanical_audit"),
        "compliance_risk": _gate_status(state, "final_audit"),
        "writing_dna_evidence_samples": len(state.working.get("learning_samples", [])),
        "knowledge": {
            "sync_gate": _gate_status(state, "knowledge_sync"),
            "reused_refs": len(cognition.get("prior_knowledge_refs", [])),
            "writeback_candidates": len(research.get("knowledge_writeback_candidates", [])),
            "writeback_receipts": len(state.working.get("knowledge_writeback_refs", [])),
        },
    }


def _next_action(state: WritingState) -> str:
    impact_action = system_impact_next_action(state)
    if impact_action:
        return impact_action
    if state.stage == Stage.BLOCKED:
        cursor = state.blocked_resume_stage.value if state.blocked_resume_stage else "UNKNOWN"
        return f"repair the recorded blocker, then call resume_blocked_task; recovery cursor={cursor}"
    if state.stage == Stage.RESEARCH_AUDIT:
        return (
            "call run_semantic_audit_stage with stage=RESEARCH_AUDIT for owner-runtime PASS certification; "
            "submit_research_audit is REVISE/FAIL-only"
        )
    if state.stage == Stage.EDITORIAL_AUDIT:
        if _gate_status(state, "hook_audit") == "REVISE" or _gate_status(state, "style_audit") == "REVISE":
            return "follow the recorded revision target; dedicated audit REVISE must route back before general editorial PASS"
        return (
            "call run_semantic_audit_stage with stage=EDITORIAL_AUDIT for owner-runtime Reader Funnel, "
            "Authorial Prose and general editorial PASS certification; submit_*audit is REVISE/FAIL-only"
        )
    if state.stage == Stage.FINAL_AUDIT:
        if _gate_status(state, "knowledge_sync") not in {"PASS", "N_A"}:
            return (
                "record knowledge writeback PASS/N_A, then call run_semantic_audit_stage with stage=FINAL_AUDIT "
                "for owner-runtime PASS certification"
            )
        return "call run_semantic_audit_stage with stage=FINAL_AUDIT for owner-runtime PASS certification"
    return {
        Stage.INTAKE: "advance runtime initialization",
        Stage.RESEARCH: "reuse durable prior knowledge when available, research broadly/currently, then submit_research",
        Stage.EDITORIAL: "build shared TopicDNA plus mode-specific deep/broad plans, then call submit_editorial_plan",
        Stage.TITLE: "research current WeChat search intent, generate reader-fit headline candidates, then call submit_headlines",
        Stage.DRAFT: "draft every applicable Word article with explicit bold skim anchors, then call submit_draft",
        Stage.DELIVERY: "call build_and_mechanically_audit_delivery",
        Stage.MECHANICAL_AUDIT: "call build_and_mechanically_audit_delivery",
        Stage.COMPLETE: "deliver publication Word artifact(s), audit Word, and the visible chat QA checklist; optional later feedback/performance may be recorded as Writing DNA evidence",
        Stage.RESEARCH_AUDIT: "unreachable",
        Stage.EDITORIAL_AUDIT: "unreachable",
        Stage.FINAL_AUDIT: "unreachable",
        Stage.BLOCKED: "unreachable",
    }[state.stage]


def _summary(state: WritingState, *, detail: bool = False) -> dict[str, Any]:
    research = state.working.get("research") or {}
    samples = state.working.get("learning_samples") or []
    signals = open_system_impact_signals(state)
    summary: dict[str, Any] = {
        "task_id": state.contract.task_id,
        "status": "BLOCKED" if state.stage == Stage.BLOCKED else ("COMPLETE" if state.stage == Stage.COMPLETE else "IN_PROGRESS"),
        "current_stage": state.stage.value,
        "topic": research.get("topic"),
        "prompt_preview": state.contract.prompt[:180],
        "content_mode": state.contract.content_mode.value,
        "distribution_mode": state.contract.distribution_mode.value,
        "delivery_channel": state.contract.delivery_channel.value,
        "required_outputs": [kind.value for kind in state.contract.required_outputs],
        "gate_status": {name: gate.status.value for name, gate in state.gates.items()},
        "blocked_reason": state.blocked_reason,
        "blocked_resume_stage": state.blocked_resume_stage.value if state.blocked_resume_stage else None,
        "learning_sample_count": len(samples),
        "open_system_impact_count": len(signals),
        "updated_at": state.updated_at.isoformat(),
        "next_action": _next_action(state),
    }
    if detail:
        summary["source_refs"] = state.contract.source_refs
        summary["gates"] = {name: {"status": gate.status.value, "evidence": gate.evidence, "notes": gate.notes} for name, gate in state.gates.items()}
        summary["artifacts"] = {kind.value: {"path": artifact.path, "exists": artifact.exists, "sha256": artifact.sha256} for kind, artifact in state.artifacts.items()}
        summary["learning_samples"] = samples
        summary["system_impact_signals"] = list(state.working.get("system_impact_signals", []))
    if state.stage == Stage.COMPLETE:
        summary["completion_checklist"] = _completion_checklist(state)
    return summary


def _save_and_advance(state: WritingState) -> WritingState:
    # The transition itself is the durable checkpoint. Pre-saving a stage payload before
    # transition creates a crash window where gate/state disagree, so do not persist here.
    return controller.advance(state)


def _validate_revision_target(decision: GateDecision, allowed: set[str], label: str) -> None:
    if decision.status in {"REVISE", "FAIL"} and decision.revision_target not in allowed:
        raise ValueError(f"{label} {decision.status} revision_target must be one of {sorted(allowed)}")


def _apply_gate_decision(state: WritingState, gate_name: str, decision: GateDecision, *, revision_key: str | None = None) -> WritingState:
    status = GateStatus(decision.status)
    state.set_gate(gate_name, status, decision.evidence, "; ".join(decision.defects + decision.remaining_boundaries))
    if revision_key and decision.revision_target:
        state.working[revision_key] = decision.revision_target
    state.add_trace("MCP_STAGE_OUTPUT", f"{gate_name}={status.value}")
    if status == GateStatus.FAIL:
        resume_stage = Stage(decision.revision_target) if decision.revision_target else state.stage
        return engine.block(state, f"{gate_name} failed: {'; '.join(decision.defects)}", resume_stage=resume_stage)
    cleanup_reason = None
    if status == GateStatus.REVISE and decision.revision_target:
        cleanup_reason = f"{gate_name} requested {decision.revision_target} revision"
        _mark_revision_cleanup(state, decision.revision_target, reason=cleanup_reason)
    advanced = _save_and_advance(state)
    if cleanup_reason and decision.revision_target:
        _cleanup_after_revision(advanced, decision.revision_target, reason=cleanup_reason)
    return advanced


def _validate_editorial_for_contract(state: WritingState, payload: EditorialPlan) -> None:
    mode = state.contract.distribution_mode.value
    if mode in {"FINANCE_DEEP", "DUAL"}:
        if payload.finance_deep is None or payload.finance_deep.coverage_policy != "MATERIAL_COMPLETE":
            raise ValueError("FINANCE_DEEP requires MATERIAL_COMPLETE editorial plan")
    elif payload.finance_deep is not None:
        raise ValueError("FINANCE_DEEP plan supplied for non-deep contract")
    if mode in {"FINANCE_BROAD", "DUAL"}:
        if payload.finance_broad is None or payload.finance_broad.coverage_policy != "SELECTIVE_TRAFFIC":
            raise ValueError("FINANCE_BROAD requires SELECTIVE_TRAFFIC editorial plan")
    elif payload.finance_broad is not None:
        raise ValueError("FINANCE_BROAD plan supplied for non-broad contract")


def _validate_headlines_for_contract(state: WritingState, payload: HeadlinePackage) -> None:
    for label, candidates, selected, applicable in [
        ("FINANCE_DEEP", payload.finance_deep_candidates, payload.finance_deep_selected, state.contract.distribution_mode.value in {"FINANCE_DEEP", "DUAL"}),
        ("FINANCE_BROAD", payload.finance_broad_candidates, payload.finance_broad_selected, state.contract.distribution_mode.value in {"FINANCE_BROAD", "DUAL"}),
    ]:
        if applicable:
            if not (8 <= len(candidates) <= 12) or not selected:
                raise ValueError(f"{label} requires 8-12 candidates and one selected title")
            chosen = next((c for c in candidates if c.title == selected), None)
            if chosen is None or not chosen.wechat_search_terms or not chosen.search_evidence_refs:
                raise ValueError(f"{label} selected title requires current search terms and evidence refs")


def _validate_draft_for_contract(state: WritingState, payload: DraftPackage) -> None:
    if state.contract.distribution_mode.value in {"FINANCE_DEEP", "DUAL"} and payload.finance_deep is None:
        raise ValueError("applicable FINANCE_DEEP draft is missing")
    if state.contract.distribution_mode.value in {"FINANCE_BROAD", "DUAL"} and payload.finance_broad is None:
        raise ValueError("applicable FINANCE_BROAD draft is missing")


def start_writing_task(prompt: str, source_refs: list[str] | None = None, target_platforms: list[str] | None = None) -> dict[str, Any]:
    contract = build_task_contract(prompt=prompt, source_refs=source_refs or [], target_platforms=target_platforms or [])
    return _summary(controller.advance(engine.start(contract)))


def get_writing_task(task_id: str, detail: bool = True) -> dict[str, Any]:
    return _summary(_load(task_id), detail=detail)


def _visible_for_continuation(state: WritingState, *, include_complete: bool) -> bool:
    if include_complete:
        return True
    return state.stage != Stage.COMPLETE or bool(open_system_impact_signals(state))


def _recent_visible_states(limit: int, *, include_complete: bool) -> list[WritingState]:
    wanted = max(1, min(int(limit), 50))
    if include_complete:
        return store.list_recent(limit=wanted)

    selected: list[WritingState] = []
    offset = 0
    page_size = 50
    while len(selected) < wanted:
        page = store.list_recent(limit=page_size, offset=offset)
        if not page:
            break
        for state in page:
            if _visible_for_continuation(state, include_complete=False):
                selected.append(state)
                if len(selected) >= wanted:
                    break
        offset += len(page)
        if len(page) < page_size:
            break
    return selected[:wanted]


def list_recent_writing_tasks(limit: int = 10, include_complete: bool = False) -> list[dict[str, Any]]:
    return [_summary(state) for state in _recent_visible_states(limit, include_complete=include_complete)]


def resume_blocked_task(task_id: str) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.BLOCKED)
    return _summary(engine.resume_blocked(state), detail=True)


def record_writing_learning_sample(
    task_id: str,
    sample_type: str,
    summary: str,
    source_refs: list[str] | None = None,
    original_excerpt: str = "",
    revised_excerpt: str = "",
    metrics: dict[str, str | int | float] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """Append raw Writing-DNA evidence without promoting it into a durable rule."""
    state = _load(task_id)
    if sample_type not in LEARNING_SAMPLE_TYPES:
        raise ValueError(f"unsupported learning sample type: {sample_type}")
    clean_summary = summary.strip()
    if not clean_summary:
        raise ValueError("learning sample summary must not be empty")
    refs = list(dict.fromkeys(source_refs or []))
    if sample_type == "USER_EDIT" and not ((original_excerpt.strip() and revised_excerpt.strip()) or refs):
        raise ValueError("USER_EDIT requires original+revised excerpts or at least one source ref")
    metric_map = metrics or {}
    if sample_type == "POST_PUBLICATION_PERFORMANCE" and not (metric_map or refs):
        raise ValueError("POST_PUBLICATION_PERFORMANCE requires metrics or a source ref")
    record = {
        "sample_type": sample_type,
        "summary": clean_summary,
        "source_refs": refs,
        "original_excerpt": original_excerpt,
        "revised_excerpt": revised_excerpt,
        "metrics": metric_map,
        "notes": notes or [],
        "recorded_stage": state.stage.value,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "promotion_status": "RAW_EVIDENCE_ONLY",
    }
    state.working.setdefault("learning_samples", []).append(record)
    state.add_trace("WRITING_LEARNING_SAMPLE", f"type={sample_type}; refs={len(refs)}; metrics={len(metric_map)}")
    store.save(state)
    return _summary(state, detail=True)


def record_knowledge_context(task_id: str, refs: list[str], notes: list[str] | None = None) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH)
    state.working["knowledge_context_refs"] = list(dict.fromkeys(refs))
    state.working["knowledge_context_notes"] = notes or []
    state.add_trace("KNOWLEDGE_CONTEXT", f"refs={len(refs)}")
    store.save(state)
    return _summary(state)


def submit_research(task_id: str, research: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH)
    payload = ResearchPackage.model_validate(research)
    _invalidate_for_stage_change(
        state,
        Stage.RESEARCH,
        reason="research package changed; all downstream editorial/draft/QA evidence is stale",
        clear_working_keys=("editorial_plan", "headlines", "draft", "hook_audit", "style_audit", "revise_target", "final_revise_target"),
        invalidate_knowledge=True,
    )
    state.working["research"] = payload.model_dump(mode="json")
    state.set_gate(
        "research_output",
        GateStatus.PASS,
        [
            f"evidence_items={len(payload.evidence_ledger)}",
            f"universe={len(payload.universe)}",
            f"coverage={payload.coverage.coverage_status}",
            f"sweeps={payload.coverage.sweeps_completed}",
            f"market_explanation_scope={payload.market_explanation_scope}",
        ],
    )
    state.add_trace("MCP_STAGE_OUTPUT", "research package accepted")
    return _summary(_save_and_advance(state))


def submit_research_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH_AUDIT)
    payload = GateDecision.model_validate(decision)
    _validate_revision_target(payload, _canonical_revision_target_names(Stage.RESEARCH_AUDIT), "research_audit")
    return _summary(_apply_gate_decision(state, "research_audit", payload, revision_key="research_revise_target"))


def submit_editorial_plan(task_id: str, editorial_plan: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL)
    payload = EditorialPlan.model_validate(editorial_plan)
    _validate_editorial_for_contract(state, payload)
    _invalidate_for_stage_change(
        state,
        Stage.EDITORIAL,
        reason="editorial plan changed; all downstream title/draft/QA evidence is stale",
        clear_working_keys=("headlines", "draft", "hook_audit", "style_audit", "revise_target", "final_revise_target"),
    )
    state.working["editorial_plan"] = payload.model_dump(mode="json")
    evidence = ["shared TopicDNA"]
    if payload.finance_deep:
        evidence.append(f"deep_completeness_obligations={len(payload.finance_deep.completeness_obligations)}")
    if payload.finance_broad:
        evidence.append(f"broad_core_contradictions={len(payload.finance_broad.core_contradictions)}")
    state.set_gate("editorial_plan", GateStatus.PASS, evidence)
    state.add_trace("MCP_STAGE_OUTPUT", "editorial plan accepted")
    return _summary(_save_and_advance(state))


def submit_headlines(task_id: str, headlines: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.TITLE)
    payload = HeadlinePackage.model_validate(headlines)
    _validate_headlines_for_contract(state, payload)
    _invalidate_for_stage_change(
        state,
        Stage.TITLE,
        reason="headline selection changed; draft and downstream QA are stale",
        clear_working_keys=("draft", "hook_audit", "style_audit", "revise_target", "final_revise_target"),
    )
    state.working["headlines"] = payload.model_dump(mode="json")
    state.set_gate("title_audit", GateStatus.PASS, ["8-12 candidates per applicable mode", "selected titles have target-reader fit, promised payoff, and current WeChat search evidence"])
    state.add_trace("MCP_STAGE_OUTPUT", "title_audit=PASS")
    return _summary(_save_and_advance(state))


def submit_draft(task_id: str, draft: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.DRAFT)
    payload = DraftPackage.model_validate(draft)
    _validate_draft_for_contract(state, payload)
    _invalidate_for_stage_change(
        state,
        Stage.DRAFT,
        reason="draft changed; semantic/mechanical/final QA must be rerun",
        clear_working_keys=("hook_audit", "style_audit", "revise_target", "final_revise_target"),
    )
    state.working["draft"] = payload.model_dump(mode="json")
    anchors = sum(len(p.skim_path_anchors) for p in [payload.finance_deep, payload.finance_broad] if p)
    state.set_gate("draft_output", GateStatus.PASS, ["all required drafts frozen", f"explicit_bold_skim_anchors={anchors}"])
    state.add_trace("MCP_STAGE_OUTPUT", "draft package accepted")
    return _summary(_save_and_advance(state))


def submit_hook_audit(task_id: str, report: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL_AUDIT)
    payload = HookAuditDecision.model_validate(report)
    status = GateStatus(payload.status)
    state.set_gate("hook_audit", status, payload.evidence, "; ".join(payload.revision_notes))
    state.working["hook_audit"] = payload.model_dump(mode="json")
    state.add_trace("MCP_STAGE_OUTPUT", f"hook_audit={status.value}")
    if status == GateStatus.REVISE:
        target = payload.revision_target or "DRAFT"
        state.set_gate("editorial_audit", GateStatus.REVISE, payload.evidence, "Reader Funnel gate requires revision before general editorial audit")
        state.working["revise_target"] = target
        cleanup_reason = f"Reader Funnel audit requested {target} revision"
        _mark_revision_cleanup(state, target, reason=cleanup_reason)
        advanced = _save_and_advance(state)
        _cleanup_after_revision(advanced, target, reason=cleanup_reason)
        return _summary(advanced)
    store.save(state)
    return _summary(state)


def submit_style_audit(task_id: str, report: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL_AUDIT)
    payload = StyleAuditDecision.model_validate(report)
    status = GateStatus(payload.status)
    notes = "; ".join(payload.detected_patterns + payload.reasoning_findings + payload.revision_notes)
    state.set_gate("style_audit", status, payload.evidence, notes)
    state.working["style_audit"] = payload.model_dump(mode="json")
    state.add_trace("MCP_STAGE_OUTPUT", f"style_audit={status.value}")
    if status == GateStatus.REVISE:
        state.set_gate("editorial_audit", GateStatus.REVISE, payload.evidence, "Authorial Prose gate requires draft revision before general editorial audit")
        state.working["revise_target"] = "DRAFT"
        cleanup_reason = "Authorial Prose audit requested DRAFT revision"
        _mark_revision_cleanup(state, "DRAFT", reason=cleanup_reason)
        advanced = _save_and_advance(state)
        _cleanup_after_revision(advanced, "DRAFT", reason=cleanup_reason)
        return _summary(advanced)
    store.save(state)
    return _summary(state)


def submit_editorial_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL_AUDIT)
    payload = GateDecision.model_validate(decision)
    _validate_revision_target(payload, _canonical_revision_target_names(Stage.EDITORIAL_AUDIT), "editorial_audit")
    if payload.status == "PASS":
        if _gate_status(state, "hook_audit") != "PASS":
            raise ValueError("hook_audit must PASS before editorial_audit can PASS")
        if _gate_status(state, "style_audit") != "PASS":
            raise ValueError("style_audit must PASS before editorial_audit can PASS")
    return _summary(_apply_gate_decision(state, "editorial_audit", payload, revision_key="revise_target"))


def build_and_mechanically_audit_delivery(task_id: str) -> dict[str, Any]:
    state = _load(task_id)
    if state.stage == Stage.DELIVERY:
        try:
            state = DeliveryExecutor(root=RUNS_DIR).execute(state)
        except Exception as exc:
            return _summary(engine.block(state, f"delivery executor error: {type(exc).__name__}: {exc}", resume_stage=Stage.DELIVERY))
        state.add_trace("MCP_DETERMINISTIC", "Word-only delivery executor completed")
        if state.gates.get("delivery_output") is None or state.gates["delivery_output"].status != GateStatus.PASS:
            return _summary(engine.block(state, "delivery_output did not pass", resume_stage=Stage.DELIVERY))
        state = controller.advance(state)
    _require_stage(state, Stage.MECHANICAL_AUDIT)
    try:
        state = MechanicalAuditExecutor(require_render=REQUIRE_RENDER).execute(state)
    except Exception as exc:
        return _summary(engine.block(state, f"mechanical audit executor error: {type(exc).__name__}: {exc}", resume_stage=Stage.MECHANICAL_AUDIT))
    state.add_trace("MCP_DETERMINISTIC", "mechanical audit executor completed")
    cleanup_reason = None
    if state.gates.get("mechanical_audit") and state.gates["mechanical_audit"].status == GateStatus.REVISE:
        cleanup_reason = "mechanical audit requires Word rebuild"
        _mark_revision_cleanup(state, "DELIVERY", reason=cleanup_reason)
    advanced = controller.advance(state)
    if cleanup_reason and advanced.stage == Stage.DELIVERY:
        _cleanup_after_revision(advanced, "DELIVERY", reason=cleanup_reason)
    return _summary(advanced, detail=True)


def record_knowledge_writeback(task_id: str, status: str, refs: list[str] | None = None, notes: list[str] | None = None) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.FINAL_AUDIT)
    if status not in {"PASS", "N_A"}:
        raise ValueError("knowledge writeback status must be PASS or N_A")
    receipts = list(dict.fromkeys(refs or []))
    note_list = notes or []
    if status == "PASS" and not receipts:
        raise ValueError("knowledge writeback PASS requires at least one receipt ref")
    if status == "N_A" and not note_list:
        raise ValueError("knowledge writeback N_A requires an explicit reason")
    state.working["knowledge_writeback_refs"] = receipts
    state.working["knowledge_writeback_notes"] = note_list
    state.set_gate("knowledge_sync", GateStatus(status), receipts or ["explicit N_A"], "; ".join(note_list))
    state.add_trace("KNOWLEDGE_WRITEBACK", f"status={status}; refs={len(receipts)}")
    store.save(state)
    return _summary(state)


def submit_final_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.FINAL_AUDIT)
    payload = GateDecision.model_validate(decision)
    _validate_revision_target(payload, _canonical_revision_target_names(Stage.FINAL_AUDIT), "final_audit")
    if payload.status == "PASS":
        for required_gate in ("hook_audit", "style_audit", "editorial_audit", "mechanical_audit"):
            if _gate_status(state, required_gate) != "PASS":
                raise ValueError(f"{required_gate} must PASS before final_audit PASS")
        if _gate_status(state, "knowledge_sync") not in {"PASS", "N_A"}:
            raise ValueError("record_knowledge_writeback PASS/N_A before final_audit PASS")
    status = GateStatus(payload.status)
    state.set_gate("final_audit", status, payload.evidence, "; ".join(payload.defects + payload.remaining_boundaries))
    if payload.revision_target:
        state.working["final_revise_target"] = payload.revision_target
    state.add_trace("MCP_STAGE_OUTPUT", f"final_audit={status.value}")
    if status == GateStatus.FAIL:
        resume_stage = Stage(payload.revision_target) if payload.revision_target else Stage.EDITORIAL
        return _summary(engine.block(state, f"final_audit failed: {'; '.join(payload.defects)}", resume_stage=resume_stage))
    cleanup_reason = None
    if status == GateStatus.REVISE and payload.revision_target:
        cleanup_reason = f"final audit requested {payload.revision_target} revision"
        _mark_revision_cleanup(state, payload.revision_target, reason=cleanup_reason)
    if status == GateStatus.PASS:
        finalize_audit_artifact(state)
    try:
        advanced = controller.advance(state)
    except WorkflowError as exc:
        return _summary(engine.block(state, str(exc), resume_stage=state.stage))
    if cleanup_reason and payload.revision_target:
        _cleanup_after_revision(advanced, payload.revision_target, reason=cleanup_reason)
    return _summary(advanced, detail=True)
