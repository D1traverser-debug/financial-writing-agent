from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from mcp.server.mcpserver import MCPServer

from .adapters.deterministic import DeliveryExecutor, MechanicalAuditExecutor, finalize_audit_artifact
from .controller import WorkflowController
from .engine import WorkflowError, WritingEngine
from .models import GateStatus, Stage, WritingState
from .routing import build_task_contract
from .schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, ResearchPackage
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
        "Deterministic financial-writing runtime. Always start or resume a writing task before research or drafting. "
        "Submit structured outputs only to the tool matching the current stage. The server owns legal stage transitions, "
        "SQLite checkpointing, Word delivery and mechanical audit. Never bypass a failed or revision gate."
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


def _summary(state: WritingState) -> dict[str, Any]:
    return {
        "task_id": state.contract.task_id,
        "status": "BLOCKED" if state.stage == Stage.BLOCKED else ("COMPLETE" if state.stage == Stage.COMPLETE else "IN_PROGRESS"),
        "current_stage": state.stage.value,
        "distribution_mode": state.contract.distribution_mode.value,
        "delivery_channel": state.contract.delivery_channel.value,
        "required_outputs": [kind.value for kind in state.contract.required_outputs],
        "gates": {
            name: {
                "status": gate.status.value,
                "evidence": gate.evidence,
                "notes": gate.notes,
            }
            for name, gate in state.gates.items()
        },
        "artifacts": {
            kind.value: {
                "path": artifact.path,
                "exists": artifact.exists,
                "sha256": artifact.sha256,
            }
            for kind, artifact in state.artifacts.items()
        },
        "blocked_reason": state.blocked_reason,
        "updated_at": state.updated_at.isoformat(),
        "next_action": _next_action(state),
        "trace_tail": [event.model_dump(mode="json") for event in state.trace[-8:]],
    }


def _next_action(state: WritingState) -> str:
    return {
        Stage.INTAKE: "advance runtime initialization",
        Stage.RESEARCH: "research broadly and call submit_research",
        Stage.RESEARCH_AUDIT: "independently audit research and call submit_research_audit",
        Stage.EDITORIAL: "build TopicDNA and candidate structures, then call submit_editorial_plan",
        Stage.TITLE: "generate and judge headline candidates, then call submit_headlines",
        Stage.DRAFT: "draft the applicable article mode(s), then call submit_draft",
        Stage.EDITORIAL_AUDIT: "independently audit the frozen draft, then call submit_editorial_audit",
        Stage.DELIVERY: "call build_and_mechanically_audit_delivery",
        Stage.MECHANICAL_AUDIT: "call build_and_mechanically_audit_delivery",
        Stage.FINAL_AUDIT: "perform final semantic red-team and call submit_final_audit",
        Stage.COMPLETE: "deliver the recorded artifacts to the user",
        Stage.BLOCKED: "inspect blocked_reason and repair the runtime dependency before resuming",
    }[state.stage]


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
) -> dict[str, Any]:
    """Start a new financial-writing task before doing any research or drafting. Returns the task_id and required next stage."""
    contract = build_task_contract(
        prompt=prompt,
        source_refs=source_refs or [],
        target_platforms=target_platforms or [],
    )
    state = engine.start(contract)
    state = controller.advance(state)
    return _summary(state)


@mcp.tool()
def get_writing_task(task_id: str) -> dict[str, Any]:
    """Load the authoritative checkpoint for one writing task."""
    return _summary(_load(task_id))


@mcp.tool()
def list_recent_writing_tasks(limit: int = 10, include_complete: bool = False) -> list[dict[str, Any]]:
    """List recent persisted writing tasks so a fresh conversation can recover an unfinished task without relying on chat memory."""
    states = store.list_recent(limit=max(1, min(limit, 50)))
    if not include_complete:
        states = [state for state in states if state.stage != Stage.COMPLETE]
    return [_summary(state) for state in states]


@mcp.tool()
def submit_research(task_id: str, research: dict[str, Any]) -> dict[str, Any]:
    """Submit a complete ResearchPackage for a task currently at RESEARCH. This is a write action and advances only through the legal gate."""
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH)
    payload = ResearchPackage.model_validate(research)
    state.working["research"] = payload.model_dump(mode="json")
    state.set_gate(
        "research_output",
        GateStatus.PASS,
        [f"evidence_items={len(payload.evidence_ledger)}", f"universe={len(payload.universe)}"],
    )
    state.add_trace("MCP_STAGE_OUTPUT", "research package accepted")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_research_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    """Submit an independent research audit for a task currently at RESEARCH_AUDIT."""
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH_AUDIT)
    result = _apply_gate_decision(state, "research_audit", GateDecision.model_validate(decision))
    return _summary(result)


@mcp.tool()
def submit_editorial_plan(task_id: str, editorial_plan: dict[str, Any]) -> dict[str, Any]:
    """Submit TopicDNA and the selected article structure for a task currently at EDITORIAL."""
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL)
    payload = EditorialPlan.model_validate(editorial_plan)
    state.working["editorial_plan"] = payload.model_dump(mode="json")
    state.set_gate("editorial_plan", GateStatus.PASS, ["TopicDNA", f"structures={len(payload.candidates)}"])
    state.add_trace("MCP_STAGE_OUTPUT", "editorial plan accepted")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_headlines(task_id: str, headlines: dict[str, Any]) -> dict[str, Any]:
    """Submit headline candidates and selections for a task currently at TITLE."""
    state = _load(task_id)
    _require_stage(state, Stage.TITLE)
    payload = HeadlinePackage.model_validate(headlines)
    state.working["headlines"] = payload.model_dump(mode="json")
    applicable: list[bool] = []
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
    """Submit the frozen structured draft package for a task currently at DRAFT."""
    state = _load(task_id)
    _require_stage(state, Stage.DRAFT)
    payload = DraftPackage.model_validate(draft)
    state.working["draft"] = payload.model_dump(mode="json")
    state.set_gate("draft_output", GateStatus.PASS, ["structured draft package frozen"])
    state.add_trace("MCP_STAGE_OUTPUT", "draft package accepted")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_editorial_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    """Submit an independent draft audit for a task currently at EDITORIAL_AUDIT."""
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL_AUDIT)
    result = _apply_gate_decision(
        state,
        "editorial_audit",
        GateDecision.model_validate(decision),
        revision_key="revise_target",
    )
    return _summary(result)


@mcp.tool()
def build_and_mechanically_audit_delivery(task_id: str) -> dict[str, Any]:
    """Build required Word artifacts and run deterministic mechanical/render QA. Only valid at DELIVERY or MECHANICAL_AUDIT."""
    state = _load(task_id)
    if state.stage == Stage.DELIVERY:
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
def submit_final_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    """Submit the final semantic red-team decision. PASS creates the visible audit report and permits COMPLETE only if every required artifact exists."""
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
