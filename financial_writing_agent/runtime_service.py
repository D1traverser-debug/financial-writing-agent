from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .adapters.deterministic import DeliveryExecutor, MechanicalAuditExecutor, finalize_audit_artifact
from .engine import WorkflowError, WritingEngine
from .models import GateStatus, Stage, WritingState
from .routing import build_task_contract
from .schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, HookAuditDecision, ResearchPackage, StyleAuditDecision
from .store import SQLiteStateStore

DATA_DIR = Path(os.getenv("FINANCIAL_WRITING_DATA_DIR", "/data"))
DB_PATH = Path(os.getenv("FINANCIAL_WRITING_DB", str(DATA_DIR / "financial_writing_state.db")))
RUNS_DIR = Path(os.getenv("FINANCIAL_WRITING_RUNS", str(DATA_DIR / "runs")))
REQUIRE_RENDER = os.getenv("FINANCIAL_WRITING_REQUIRE_RENDER", "1").lower() not in {"0", "false", "no"}

store = SQLiteStateStore(DB_PATH)
engine = WritingEngine(store)
from .controller import WorkflowController
controller = WorkflowController(engine)


def _load(task_id: str) -> WritingState:
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


def _invalidate(state: WritingState, gate_names: tuple[str, ...], *, reason: str, clear_artifacts: bool = False) -> None:
    for name in gate_names:
        if name in state.gates:
            state.set_gate(name, GateStatus.NOT_RUN, [], reason)
    for key in ("hook_audit", "style_audit", "render_manifest"):
        state.working.pop(key, None)
    if clear_artifacts:
        state.artifacts.clear()
        state.working.pop("output_dir", None)
    state.add_trace("QA_INVALIDATED", reason)


def _completion_checklist(state: WritingState) -> dict[str, Any]:
    research = state.working.get("research") or {}
    cognition = research.get("cognition") or {}
    return {
        "runtime_gates": "PASS" if state.stage == Stage.COMPLETE else "INCOMPLETE",
        "research_evidence": _gate_status(state, "research_audit"),
        "editorial": {
            "general_editorial": _gate_status(state, "editorial_audit"),
            "hook": _gate_status(state, "hook_audit"),
            "human_voice": _gate_status(state, "style_audit"),
        },
        "bold_skim_path": _gate_status(state, "mechanical_audit"),
        "word_render": _gate_status(state, "mechanical_audit"),
        "compliance_risk": _gate_status(state, "final_audit"),
        "knowledge": {
            "sync_gate": _gate_status(state, "knowledge_sync"),
            "reused_refs": len(cognition.get("prior_knowledge_refs", [])),
            "writeback_candidates": len(research.get("knowledge_writeback_candidates", [])),
            "writeback_receipts": len(state.working.get("knowledge_writeback_refs", [])),
        },
    }


def _next_action(state: WritingState) -> str:
    if state.stage == Stage.EDITORIAL_AUDIT:
        missing = []
        if _gate_status(state, "hook_audit") != "PASS":
            missing.append("submit_hook_audit")
        if _gate_status(state, "style_audit") != "PASS":
            missing.append("submit_style_audit")
        if missing:
            return "run independent " + " and ".join(missing) + " before submit_editorial_audit"
    return {
        Stage.INTAKE: "advance runtime initialization",
        Stage.RESEARCH: "reuse durable prior knowledge when available, research broadly/currently, then submit_research",
        Stage.RESEARCH_AUDIT: "independently audit research and call submit_research_audit",
        Stage.EDITORIAL: "build shared TopicDNA plus mode-specific deep/broad plans, then call submit_editorial_plan",
        Stage.TITLE: "research current WeChat search intent, generate/judge headline candidates, then call submit_headlines",
        Stage.DRAFT: "draft every applicable Word article with explicit bold skim anchors, then call submit_draft",
        Stage.EDITORIAL_AUDIT: "call submit_editorial_audit after hook_audit and style_audit pass",
        Stage.DELIVERY: "call build_and_mechanically_audit_delivery",
        Stage.MECHANICAL_AUDIT: "call build_and_mechanically_audit_delivery",
        Stage.FINAL_AUDIT: "record knowledge writeback PASS/N_A, then call submit_final_audit",
        Stage.COMPLETE: "deliver publication Word artifact(s), audit Word, and the visible chat QA checklist; do not paste article body",
        Stage.BLOCKED: "inspect blocked_reason and repair the dependency or contract defect before resuming",
    }[state.stage]


def _summary(state: WritingState, *, detail: bool = False) -> dict[str, Any]:
    research = state.working.get("research") or {}
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
        "updated_at": state.updated_at.isoformat(),
        "next_action": _next_action(state),
    }
    if detail:
        summary["source_refs"] = state.contract.source_refs
        summary["gates"] = {name: {"status": gate.status.value, "evidence": gate.evidence, "notes": gate.notes} for name, gate in state.gates.items()}
        summary["artifacts"] = {kind.value: {"path": artifact.path, "exists": artifact.exists, "sha256": artifact.sha256} for kind, artifact in state.artifacts.items()}
    if state.stage == Stage.COMPLETE:
        summary["completion_checklist"] = _completion_checklist(state)
    return summary


def _save_and_advance(state: WritingState) -> WritingState:
    store.save(state)
    return controller.advance(state)


def _validate_revision_target(decision: GateDecision, allowed: set[str], label: str) -> None:
    if decision.status == "REVISE" and decision.revision_target not in allowed:
        raise ValueError(f"{label} REVISE revision_target must be one of {sorted(allowed)}")


def _apply_gate_decision(state: WritingState, gate_name: str, decision: GateDecision, *, revision_key: str | None = None) -> WritingState:
    status = GateStatus(decision.status)
    state.set_gate(gate_name, status, decision.evidence, "; ".join(decision.defects + decision.remaining_boundaries))
    if revision_key and decision.revision_target:
        state.working[revision_key] = decision.revision_target
    state.add_trace("MCP_STAGE_OUTPUT", f"{gate_name}={status.value}")
    if status == GateStatus.FAIL:
        return engine.block(state, f"{gate_name} failed: {'; '.join(decision.defects)}")
    return _save_and_advance(state)


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


def list_recent_writing_tasks(limit: int = 10, include_complete: bool = False) -> list[dict[str, Any]]:
    states = store.list_recent(limit=max(1, min(limit, 50)))
    if not include_complete:
        states = [state for state in states if state.stage != Stage.COMPLETE]
    return [_summary(state) for state in states]


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
    state.working["research"] = payload.model_dump(mode="json")
    state.set_gate("research_output", GateStatus.PASS, [f"evidence_items={len(payload.evidence_ledger)}", f"universe={len(payload.universe)}", f"coverage={payload.coverage.coverage_status}", f"sweeps={payload.coverage.sweeps_completed}"])
    state.add_trace("MCP_STAGE_OUTPUT", "research package accepted")
    return _summary(_save_and_advance(state))


def submit_research_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH_AUDIT)
    payload = GateDecision.model_validate(decision)
    _validate_revision_target(payload, {"RESEARCH"}, "research_audit")
    return _summary(_apply_gate_decision(state, "research_audit", payload))


def submit_editorial_plan(task_id: str, editorial_plan: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL)
    payload = EditorialPlan.model_validate(editorial_plan)
    _validate_editorial_for_contract(state, payload)
    _invalidate(state, ("title_audit", "draft_output", "hook_audit", "style_audit", "editorial_audit", "delivery_output", "mechanical_audit", "final_audit"), reason="editorial plan changed; all downstream title/draft/QA evidence is stale", clear_artifacts=True)
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
    _invalidate(state, ("draft_output", "hook_audit", "style_audit", "editorial_audit", "delivery_output", "mechanical_audit", "final_audit"), reason="headline selection changed; draft and downstream QA are stale", clear_artifacts=True)
    state.working["headlines"] = payload.model_dump(mode="json")
    state.set_gate("title_audit", GateStatus.PASS, ["8-12 candidates per applicable mode", "selected titles have cross-finance reason + current WeChat search evidence"])
    state.add_trace("MCP_STAGE_OUTPUT", "title_audit=PASS")
    return _summary(_save_and_advance(state))


def submit_draft(task_id: str, draft: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.DRAFT)
    payload = DraftPackage.model_validate(draft)
    _validate_draft_for_contract(state, payload)
    _invalidate(state, ("hook_audit", "style_audit", "editorial_audit", "delivery_output", "mechanical_audit", "final_audit"), reason="draft changed; semantic/mechanical/final QA must be rerun", clear_artifacts=True)
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
    store.save(state)
    return _summary(state)


def submit_style_audit(task_id: str, report: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL_AUDIT)
    payload = StyleAuditDecision.model_validate(report)
    status = GateStatus(payload.status)
    notes = "; ".join(payload.detected_patterns + payload.transition_findings + payload.revision_notes)
    state.set_gate("style_audit", status, payload.evidence, notes)
    state.working["style_audit"] = payload.model_dump(mode="json")
    state.add_trace("MCP_STAGE_OUTPUT", f"style_audit={status.value}")
    store.save(state)
    return _summary(state)


def submit_editorial_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL_AUDIT)
    payload = GateDecision.model_validate(decision)
    _validate_revision_target(payload, {"TITLE", "DRAFT"}, "editorial_audit")
    if payload.status == "PASS":
        if _gate_status(state, "hook_audit") != "PASS":
            raise ValueError("hook_audit must PASS before editorial_audit can PASS")
        if _gate_status(state, "style_audit") != "PASS":
            raise ValueError("style_audit must PASS before editorial_audit can PASS")
    return _summary(_apply_gate_decision(state, "editorial_audit", payload, revision_key="revise_target"))


def build_and_mechanically_audit_delivery(task_id: str) -> dict[str, Any]:
    state = _load(task_id)
    if state.stage == Stage.DELIVERY:
        state = DeliveryExecutor(root=RUNS_DIR).execute(state)
        state.add_trace("MCP_DETERMINISTIC", "Word-only delivery executor completed")
        store.save(state)
        if state.gates.get("delivery_output") is None or state.gates["delivery_output"].status != GateStatus.PASS:
            return _summary(engine.block(state, "delivery_output did not pass"))
        state = controller.advance(state)
    _require_stage(state, Stage.MECHANICAL_AUDIT)
    state = MechanicalAuditExecutor(require_render=REQUIRE_RENDER).execute(state)
    state.add_trace("MCP_DETERMINISTIC", "mechanical audit executor completed")
    store.save(state)
    return _summary(controller.advance(state), detail=True)


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
    _validate_revision_target(payload, {"EDITORIAL", "DELIVERY"}, "final_audit")
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
        return _summary(engine.block(state, f"final_audit failed: {'; '.join(payload.defects)}"))
    if status == GateStatus.PASS:
        finalize_audit_artifact(state)
        store.save(state)
    try:
        state = controller.advance(state)
    except WorkflowError as exc:
        state = engine.block(state, str(exc))
    return _summary(state, detail=True)
