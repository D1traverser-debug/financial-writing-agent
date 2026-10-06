from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

from .adapters.deterministic import DeliveryExecutor, MechanicalAuditExecutor, finalize_audit_artifact
from .controller import WorkflowController
from .engine import WorkflowError, WritingEngine
from .models import ContentMode, GateStatus, Stage, WritingState
from .routing import build_task_contract
from .schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, ResearchPackage, StyleAuditDecision, VisualPackage
from .store import SQLiteStateStore

DATA_DIR = Path(os.getenv("FINANCIAL_WRITING_DATA_DIR", "/data"))
DB_PATH = Path(os.getenv("FINANCIAL_WRITING_DB", str(DATA_DIR / "financial_writing_state.db")))
RUNS_DIR = Path(os.getenv("FINANCIAL_WRITING_RUNS", str(DATA_DIR / "runs")))
REQUIRE_RENDER = os.getenv("FINANCIAL_WRITING_REQUIRE_RENDER", "1").lower() not in {"0", "false", "no"}

store = SQLiteStateStore(DB_PATH)
engine = WritingEngine(store)
controller = WorkflowController(engine)

mcp = MCPServer(
    "Financial Writing Agent",
    instructions=(
        "Deterministic financial-writing runtime. Start or resume a task before research/drafting. "
        "The server owns legal transitions, checkpointing, publication-ready Word delivery and mechanical audit. "
        "Connected Notion/Drive/knowledge retrieval remains ChatGPT-orchestrator work: record reused knowledge with "
        "record_knowledge_context and writeback receipts with record_knowledge_writeback. "
        "For normal new Word articles visuals are enabled by default; generate images on the ChatGPT side, submit them with "
        "submit_visual_package at DELIVERY, then build the Word files. Never bypass a failed/revision gate."
    ),
)


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
    return gate.status.value if gate else "N_A"


def _completion_checklist(state: WritingState) -> dict[str, Any]:
    research = state.working.get("research") or {}
    cognition = research.get("cognition") or {}
    return {
        "runtime_gates": "PASS" if state.stage == Stage.COMPLETE else "INCOMPLETE",
        "research_evidence": _gate_status(state, "research_audit"),
        "structure_style_continuity": {
            "editorial": _gate_status(state, "editorial_audit"),
            "anti_ai_style": _gate_status(state, "style_audit"),
        },
        "word_render": _gate_status(state, "mechanical_audit"),
        "compliance_risk": _gate_status(state, "final_audit"),
        "visuals": _gate_status(state, "visual_assets") if state.contract.visuals_enabled else "N_A",
        "knowledge": {
            "sync_gate": _gate_status(state, "knowledge_sync"),
            "reused_refs": len(cognition.get("prior_knowledge_refs", [])),
            "writeback_candidates": len(research.get("knowledge_writeback_candidates", [])),
            "writeback_receipts": len(state.working.get("knowledge_writeback_refs", [])),
        },
    }


def _next_action(state: WritingState) -> str:
    if state.stage == Stage.DELIVERY:
        if state.contract.visuals_enabled and "visual_package" not in state.working:
            return "plan/generate publication visuals and call submit_visual_package, then call build_and_mechanically_audit_delivery"
        return "call build_and_mechanically_audit_delivery"
    if state.stage == Stage.EDITORIAL_AUDIT and _gate_status(state, "style_audit") != "PASS":
        return "run the dedicated anti-AI/style judge and call submit_style_audit before submit_editorial_audit"
    return {
        Stage.INTAKE: "advance runtime initialization",
        Stage.RESEARCH: "query connected durable knowledge when available, record_knowledge_context, research broadly/currently, then submit_research",
        Stage.RESEARCH_AUDIT: "independently audit research and call submit_research_audit",
        Stage.EDITORIAL: "build TopicDNA and candidate structures, then call submit_editorial_plan",
        Stage.TITLE: "generate and judge headline candidates, then call submit_headlines",
        Stage.DRAFT: "draft the applicable content mode, then call submit_draft",
        Stage.EDITORIAL_AUDIT: "call submit_editorial_audit",
        Stage.MECHANICAL_AUDIT: "call build_and_mechanically_audit_delivery",
        Stage.FINAL_AUDIT: "write reusable knowledge when a connected store is available, record_knowledge_writeback, then call submit_final_audit",
        Stage.COMPLETE: "deliver recorded artifacts plus the visible completion checklist",
        Stage.BLOCKED: "inspect blocked_reason and repair the runtime dependency before resuming",
    }[state.stage]


def _summary(state: WritingState) -> dict[str, Any]:
    summary = {
        "task_id": state.contract.task_id,
        "status": "BLOCKED" if state.stage == Stage.BLOCKED else ("COMPLETE" if state.stage == Stage.COMPLETE else "IN_PROGRESS"),
        "current_stage": state.stage.value,
        "content_mode": state.contract.content_mode.value,
        "distribution_mode": state.contract.distribution_mode.value,
        "delivery_channel": state.contract.delivery_channel.value,
        "visuals_enabled": state.contract.visuals_enabled,
        "visual_profile_ref": state.contract.visual_profile_ref,
        "required_outputs": [kind.value for kind in state.contract.required_outputs],
        "gates": {
            name: {"status": gate.status.value, "evidence": gate.evidence, "notes": gate.notes}
            for name, gate in state.gates.items()
        },
        "artifacts": {
            kind.value: {"path": artifact.path, "exists": artifact.exists, "sha256": artifact.sha256}
            for kind, artifact in state.artifacts.items()
        },
        "blocked_reason": state.blocked_reason,
        "updated_at": state.updated_at.isoformat(),
        "next_action": _next_action(state),
        "trace_tail": [event.model_dump(mode="json") for event in state.trace[-8:]],
    }
    if state.stage == Stage.COMPLETE:
        summary["completion_checklist"] = _completion_checklist(state)
    return summary


def _save_and_advance(state: WritingState) -> WritingState:
    store.save(state)
    return controller.advance(state)


def _apply_gate_decision(state: WritingState, gate_name: str, decision: GateDecision, *, revision_key: str | None = None) -> WritingState:
    status = GateStatus(decision.status)
    state.set_gate(gate_name, status, decision.evidence, "; ".join(decision.defects + decision.remaining_boundaries))
    if revision_key and decision.revision_target:
        state.working[revision_key] = decision.revision_target
    state.add_trace("MCP_STAGE_OUTPUT", f"{gate_name}={status.value}")
    if status == GateStatus.FAIL:
        return engine.block(state, f"{gate_name} failed: {'; '.join(decision.defects) or 'no defect detail'}")
    return _save_and_advance(state)


@mcp.tool()
def start_writing_task(
    prompt: str,
    source_refs: list[str] | None = None,
    target_platforms: list[str] | None = None,
    visuals_enabled: bool | None = None,
    visual_profile_ref: str | None = None,
    content_mode: str | None = None,
) -> dict[str, Any]:
    """Start a new financial-writing task before research/drafting. 微信贴图 is routed to WECHAT_STICKER_POST."""
    explicit_mode = ContentMode(content_mode) if content_mode else None
    contract = build_task_contract(
        prompt=prompt,
        source_refs=source_refs or [],
        target_platforms=target_platforms or [],
        visuals_enabled=visuals_enabled,
        visual_profile_ref=visual_profile_ref,
        content_mode=explicit_mode,
    )
    state = engine.start(contract)
    state = controller.advance(state)
    return _summary(state)


@mcp.tool()
def get_writing_task(task_id: str) -> dict[str, Any]:
    return _summary(_load(task_id))


@mcp.tool()
def list_recent_writing_tasks(limit: int = 10, include_complete: bool = False) -> list[dict[str, Any]]:
    states = store.list_recent(limit=max(1, min(limit, 50)))
    if not include_complete:
        states = [state for state in states if state.stage != Stage.COMPLETE]
    return [_summary(state) for state in states]


@mcp.tool()
def record_knowledge_context(task_id: str, refs: list[str], notes: list[str] | None = None) -> dict[str, Any]:
    """Record connected-store knowledge retrieved by the ChatGPT orchestrator. Runtime itself does not impersonate Notion/Drive connectors."""
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH)
    state.working["knowledge_context_refs"] = list(dict.fromkeys(refs))
    state.working["knowledge_context_notes"] = notes or []
    state.add_trace("KNOWLEDGE_CONTEXT", f"refs={len(refs)}")
    store.save(state)
    return _summary(state)


@mcp.tool()
def submit_research(task_id: str, research: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH)
    payload = ResearchPackage.model_validate(research)
    state.working["research"] = payload.model_dump(mode="json")
    state.set_gate(
        "research_output",
        GateStatus.PASS,
        [
            f"evidence_items={len(payload.evidence_ledger)}",
            f"universe={len(payload.universe)}",
            f"prior_knowledge_refs={len(payload.cognition.prior_knowledge_refs)}",
            f"knowledge_writeback_candidates={len(payload.knowledge_writeback_candidates)}",
        ],
    )
    state.add_trace("MCP_STAGE_OUTPUT", "research package accepted")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_research_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH_AUDIT)
    return _summary(_apply_gate_decision(state, "research_audit", GateDecision.model_validate(decision)))


@mcp.tool()
def submit_editorial_plan(task_id: str, editorial_plan: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL)
    payload = EditorialPlan.model_validate(editorial_plan)
    state.working["editorial_plan"] = payload.model_dump(mode="json")
    state.set_gate("editorial_plan", GateStatus.PASS, ["TopicDNA", f"structures={len(payload.candidates)}"])
    state.add_trace("MCP_STAGE_OUTPUT", "editorial plan accepted")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_headlines(task_id: str, headlines: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.TITLE)
    payload = HeadlinePackage.model_validate(headlines)
    state.working["headlines"] = payload.model_dump(mode="json")
    applicable: list[bool] = []
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        applicable.append(bool(payload.wechat_sticker_selected))
    else:
        if state.contract.distribution_mode.value in {"FINANCE_DEEP", "DUAL"}:
            applicable.append(bool(payload.finance_deep_selected))
        if state.contract.distribution_mode.value in {"FINANCE_BROAD", "DUAL"}:
            applicable.append(bool(payload.finance_broad_selected))
    status = GateStatus.PASS if applicable and all(applicable) else GateStatus.REVISE
    state.set_gate("title_audit", status, [f"applicable_modes={len(applicable)}"])
    state.add_trace("MCP_STAGE_OUTPUT", f"title_audit={status.value}")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_draft(task_id: str, draft: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.DRAFT)
    payload = DraftPackage.model_validate(draft)
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST and payload.wechat_sticker_post is None:
        raise ValueError("WECHAT_STICKER_POST task requires draft.wechat_sticker_post")
    state.working["draft"] = payload.model_dump(mode="json")
    state.set_gate("draft_output", GateStatus.PASS, ["structured draft package frozen"])
    state.add_trace("MCP_STAGE_OUTPUT", "draft package accepted")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_style_audit(task_id: str, report: dict[str, Any]) -> dict[str, Any]:
    """Dedicated anti-AI/style judge. Run before the general editorial audit."""
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL_AUDIT)
    payload = StyleAuditDecision.model_validate(report)
    status = GateStatus(payload.status)
    notes = "; ".join(payload.detected_patterns + payload.transition_findings + payload.extreme_language_findings + payload.revision_notes)
    state.set_gate("style_audit", status, payload.evidence, notes)
    state.working["style_audit"] = payload.model_dump(mode="json")
    state.add_trace("MCP_STAGE_OUTPUT", f"style_audit={status.value}")
    store.save(state)
    return _summary(state)


@mcp.tool()
def submit_editorial_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL_AUDIT)
    payload = GateDecision.model_validate(decision)
    if payload.status == "PASS" and _gate_status(state, "style_audit") != "PASS":
        raise ValueError("style_audit must PASS before editorial_audit can PASS")
    result = _apply_gate_decision(state, "editorial_audit", payload, revision_key="revise_target")
    return _summary(result)


@mcp.tool()
def submit_visual_package(task_id: str, visual_package: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.DELIVERY)
    if not state.contract.visuals_enabled:
        raise ValueError("task visuals_enabled=false; do not submit a visual package")
    payload = VisualPackage.model_validate(visual_package)
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        applicable = ["WECHAT_STICKER_POST"]
    else:
        applicable = []
        if state.contract.distribution_mode.value in {"FINANCE_DEEP", "DUAL"}:
            applicable.append("FINANCE_DEEP")
        if state.contract.distribution_mode.value in {"FINANCE_BROAD", "DUAL"}:
            applicable.append("FINANCE_BROAD")
    evidence: list[str] = []
    for mode in applicable:
        assets = [a for a in payload.assets if a.article_mode == mode]
        if not assets:
            raise ValueError(f"missing visuals for applicable mode: {mode}")
        if mode == "WECHAT_STICKER_POST":
            if not any(a.role in {"sticker", "hero"} for a in assets):
                raise ValueError("WeChat sticker mode requires at least one sticker/hero image")
        elif not any(a.role == "hero" for a in assets):
            raise ValueError(f"missing hero visual for applicable mode: {mode}")
        if payload.avatar_required and any(not a.avatar_included for a in assets):
            raise ValueError(f"approved avatar missing from one or more {mode} visuals")
        evidence.append(f"{mode}_visuals={len(assets)}")
    state.working["visual_package"] = payload.model_dump(mode="json")
    state.set_gate("visual_assets", GateStatus.PASS, evidence)
    state.add_trace("MCP_STAGE_OUTPUT", "visual package accepted")
    store.save(state)
    return _summary(state)


@mcp.tool()
def build_and_mechanically_audit_delivery(task_id: str) -> dict[str, Any]:
    state = _load(task_id)
    if state.stage == Stage.DELIVERY:
        if state.contract.visuals_enabled and "visual_package" not in state.working:
            raise ValueError("visual package required before delivery; call submit_visual_package first")
        state = DeliveryExecutor(root=RUNS_DIR).execute(state)
        state.add_trace("MCP_DETERMINISTIC", "delivery executor completed")
        store.save(state)
        if state.gates.get("delivery_output") is None or state.gates["delivery_output"].status != GateStatus.PASS:
            return _summary(engine.block(state, "delivery_output did not pass"))
        state = controller.advance(state)

    _require_stage(state, Stage.MECHANICAL_AUDIT)
    state = MechanicalAuditExecutor(require_render=REQUIRE_RENDER).execute(state)
    state.add_trace("MCP_DETERMINISTIC", "mechanical audit executor completed")
    store.save(state)
    state = controller.advance(state)
    return _summary(state)


@mcp.tool()
def record_knowledge_writeback(
    task_id: str,
    status: str,
    refs: list[str] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    """Record connector-side knowledge writeback before final audit. status must be PASS or N_A."""
    state = _load(task_id)
    _require_stage(state, Stage.FINAL_AUDIT)
    if status not in {"PASS", "N_A"}:
        raise ValueError("knowledge writeback status must be PASS or N_A")
    receipts = list(dict.fromkeys(refs or []))
    state.working["knowledge_writeback_refs"] = receipts
    state.working["knowledge_writeback_notes"] = notes or []
    state.set_gate("knowledge_sync", GateStatus(status), receipts, "; ".join(notes or []))
    state.add_trace("KNOWLEDGE_WRITEBACK", f"status={status}; refs={len(receipts)}")
    store.save(state)
    return _summary(state)


@mcp.tool()
def submit_final_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    state = _load(task_id)
    _require_stage(state, Stage.FINAL_AUDIT)
    payload = GateDecision.model_validate(decision)
    status = GateStatus(payload.status)
    state.set_gate("final_audit", status, payload.evidence, "; ".join(payload.defects + payload.remaining_boundaries))
    if payload.revision_target:
        state.working["final_revise_target"] = payload.revision_target
    state.add_trace("MCP_STAGE_OUTPUT", f"final_audit={status.value}")
    if status == GateStatus.FAIL:
        return _summary(engine.block(state, f"final_audit failed: {'; '.join(payload.defects) or 'no defect detail'}"))
    if status == GateStatus.PASS:
        finalize_audit_artifact(state)
        store.save(state)
    try:
        state = controller.advance(state)
    except WorkflowError as exc:
        state = engine.block(state, str(exc))
    return _summary(state)


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    mcp.run(
        transport="streamable-http",
        host=host,
        port=port,
        streamable_http_path="/mcp",
        stateless_http=True,
        json_response=True,
    )


if __name__ == "__main__":
    main()
