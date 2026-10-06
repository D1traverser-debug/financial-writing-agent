from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from mcp.server.mcpserver import MCPServer

from .adapters.deterministic import DeliveryExecutor, MechanicalAuditExecutor, finalize_audit_artifact
from .checks import load_policy
from .controller import WorkflowController
from .engine import WorkflowError, WritingEngine
from .models import ContentMode, GateStatus, Stage, WritingState
from .routing import build_task_contract
from .schemas import (
    DraftPackage,
    EditorialPlan,
    GateDecision,
    HeadlinePackage,
    OpenAIFileRef,
    ResearchPackage,
    ResolvedVisualAsset,
    ResolvedVisualPackage,
    StyleAuditDecision,
    VisualPackage,
)
from .store import SQLiteStateStore

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("FINANCIAL_WRITING_DATA_DIR", "/data"))
DB_PATH = Path(os.getenv("FINANCIAL_WRITING_DB", str(DATA_DIR / "financial_writing_state.db")))
RUNS_DIR = Path(os.getenv("FINANCIAL_WRITING_RUNS", str(DATA_DIR / "runs")))
REQUIRE_RENDER = os.getenv("FINANCIAL_WRITING_REQUIRE_RENDER", "1").lower() not in {"0", "false", "no"}
POLICY = load_policy(PROJECT_ROOT / "config" / "policy.json")

store = SQLiteStateStore(DB_PATH)
engine = WritingEngine(store)
controller = WorkflowController(engine)

mcp = MCPServer(
    "Financial Writing Agent",
    instructions=(
        "Use this runtime for A-share financial content creation, continuation and publication packaging. "
        "For a continuation, list/load unfinished tasks before starting a new one. For a new task, start the runtime before research. "
        "The server owns legal transitions, validation, checkpointing, Word construction and mechanical audit. "
        "ChatGPT owns connected-knowledge retrieval, live research, high-judgment writing/audits and creative image generation. "
        "When visuals are enabled, generated images must be passed through submit_visual_package as ChatGPT file parameters; "
        "never invent server paths or public URLs. Never bypass a failed or revision gate."
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
    return gate.status.value if gate else "NOT_RUN"


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
        if state.contract.visuals_enabled and "resolved_visual_package" not in state.working:
            return "generate real publication images and call submit_visual_package with file params, then call build_and_mechanically_audit_delivery"
        return "call build_and_mechanically_audit_delivery"
    if state.stage == Stage.EDITORIAL_AUDIT and _gate_status(state, "style_audit") != "PASS":
        return "run the independent anti-AI/style judge and call submit_style_audit before submit_editorial_audit"
    return {
        Stage.INTAKE: "advance runtime initialization",
        Stage.RESEARCH: "reuse connected durable knowledge when available, research broadly/currently, then submit_research",
        Stage.RESEARCH_AUDIT: "independently audit research and call submit_research_audit",
        Stage.EDITORIAL: "build TopicDNA and multiple candidate structures, then call submit_editorial_plan",
        Stage.TITLE: "generate/judge headline candidates, then call submit_headlines",
        Stage.DRAFT: "draft every applicable content output, then call submit_draft",
        Stage.EDITORIAL_AUDIT: "call submit_editorial_audit after style_audit passes",
        Stage.MECHANICAL_AUDIT: "call build_and_mechanically_audit_delivery",
        Stage.FINAL_AUDIT: "record knowledge writeback PASS/N_A, then call submit_final_audit",
        Stage.COMPLETE: "deliver recorded artifacts plus the visible completion checklist",
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
        "visuals_enabled": state.contract.visuals_enabled,
        "required_outputs": [kind.value for kind in state.contract.required_outputs],
        "gate_status": {name: gate.status.value for name, gate in state.gates.items()},
        "blocked_reason": state.blocked_reason,
        "updated_at": state.updated_at.isoformat(),
        "next_action": _next_action(state),
    }
    if detail:
        summary["source_refs"] = state.contract.source_refs
        summary["visual_profile_ref"] = state.contract.visual_profile_ref
        summary["gates"] = {
            name: {"status": gate.status.value, "evidence": gate.evidence, "notes": gate.notes}
            for name, gate in state.gates.items()
        }
        summary["artifacts"] = {
            kind.value: {"path": artifact.path, "exists": artifact.exists, "sha256": artifact.sha256}
            for kind, artifact in state.artifacts.items()
        }
        summary["trace_tail"] = [event.model_dump(mode="json") for event in state.trace[-8:]]
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
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        if not payload.wechat_sticker_emphasis:
            raise ValueError("WECHAT_STICKER_POST editorial plan requires wechat_sticker_emphasis")
        return
    if state.contract.distribution_mode.value in {"FINANCE_DEEP", "DUAL"} and not payload.finance_deep_emphasis:
        raise ValueError("applicable FINANCE_DEEP plan requires finance_deep_emphasis")
    if state.contract.distribution_mode.value in {"FINANCE_BROAD", "DUAL"} and not payload.finance_broad_emphasis:
        raise ValueError("applicable FINANCE_BROAD plan requires finance_broad_emphasis")


def _validate_headlines_for_contract(state: WritingState, payload: HeadlinePackage) -> None:
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        if not (4 <= len(payload.wechat_sticker_candidates) <= 12) or not payload.wechat_sticker_selected:
            raise ValueError("WECHAT_STICKER_POST requires 4-12 candidates and one selected title")
        return
    if state.contract.distribution_mode.value in {"FINANCE_DEEP", "DUAL"}:
        if not (8 <= len(payload.finance_deep_candidates) <= 12) or not payload.finance_deep_selected:
            raise ValueError("FINANCE_DEEP requires 8-12 candidates and one selected title")
    if state.contract.distribution_mode.value in {"FINANCE_BROAD", "DUAL"}:
        if not (8 <= len(payload.finance_broad_candidates) <= 12) or not payload.finance_broad_selected:
            raise ValueError("FINANCE_BROAD requires 8-12 candidates and one selected title")


def _validate_draft_for_contract(state: WritingState, payload: DraftPackage) -> None:
    if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
        if payload.wechat_sticker_post is None:
            raise ValueError("WECHAT_STICKER_POST task requires draft.wechat_sticker_post")
        if payload.finance_deep is not None or payload.finance_broad is not None:
            raise ValueError("WECHAT_STICKER_POST must not include formal-article payloads")
        return
    if state.contract.distribution_mode.value in {"FINANCE_DEEP", "DUAL"} and payload.finance_deep is None:
        raise ValueError("applicable FINANCE_DEEP draft is missing")
    if state.contract.distribution_mode.value in {"FINANCE_BROAD", "DUAL"} and payload.finance_broad is None:
        raise ValueError("applicable FINANCE_BROAD draft is missing")
    if payload.wechat_sticker_post is not None:
        raise ValueError("formal-article task must not include WECHAT_STICKER_POST payload")


def _safe_asset_name(file_ref: OpenAIFileRef) -> str:
    digest = hashlib.sha256(file_ref.file_id.encode("utf-8")).hexdigest()[:20]
    suffix = Path(file_ref.file_name or "").suffix.lower()
    if not suffix:
        suffix = {"image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp"}.get(file_ref.mime_type or "", ".img")
    return digest + suffix


def _download_visual_files(task_id: str, files: list[OpenAIFileRef]) -> dict[str, str]:
    max_bytes = int(POLICY.get("visuals", {}).get("max_file_bytes", 25 * 1024 * 1024))
    asset_dir = RUNS_DIR / task_id / "assets"
    asset_dir.mkdir(parents=True, exist_ok=True)
    result: dict[str, str] = {}
    for file_ref in files:
        if file_ref.file_id in result:
            raise ValueError(f"duplicate file_id: {file_ref.file_id}")
        if file_ref.mime_type and not file_ref.mime_type.startswith("image/"):
            raise ValueError(f"visual file must be image/*: {file_ref.file_id}")
        parsed = urlparse(file_ref.download_url)
        if parsed.scheme != "https":
            raise ValueError("ChatGPT file download_url must use https")
        request = Request(file_ref.download_url, headers={"User-Agent": "financial-writing-agent/0.2"})
        with urlopen(request, timeout=30) as response:
            if urlparse(response.geturl()).scheme != "https":
                raise ValueError("visual download redirected to non-https URL")
            data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError(f"visual file too large: {file_ref.file_id}")
        path = asset_dir / _safe_asset_name(file_ref)
        path.write_bytes(data)
        result[file_ref.file_id] = str(path)
    return result


@mcp.tool()
def start_writing_task(
    prompt: str,
    source_refs: list[str] | None = None,
    target_platforms: list[str] | None = None,
    visuals_enabled: bool | None = None,
    visual_profile_ref: str | None = None,
    content_mode: str | None = None,
) -> dict[str, Any]:
    """Start a NEW financial-writing task before any research or drafting. Use only when no relevant unfinished runtime task should be resumed. Creates persistent task state and advances to RESEARCH; 微信贴图 can route to WECHAT_STICKER_POST."""
    explicit_mode = ContentMode(content_mode) if content_mode else None
    contract = build_task_contract(prompt=prompt, source_refs=source_refs or [], target_platforms=target_platforms or [], visuals_enabled=visuals_enabled, visual_profile_ref=visual_profile_ref, content_mode=explicit_mode)
    state = controller.advance(engine.start(contract))
    return _summary(state)


@mcp.tool()
def get_writing_task(task_id: str, detail: bool = True) -> dict[str, Any]:
    """Read one persisted writing task by exact task_id. Use after list_recent_writing_tasks or when a task_id is already known; does not change state. Set detail=false for a compact status."""
    return _summary(_load(task_id), detail=detail)


@mcp.tool()
def list_recent_writing_tasks(limit: int = 10, include_complete: bool = False) -> list[dict[str, Any]]:
    """List recent writing tasks with prompt/topic previews so ChatGPT can recover the right unfinished task without asking the user to repeat it. Read-only; completed tasks are excluded by default."""
    states = store.list_recent(limit=max(1, min(limit, 50)))
    if not include_complete:
        states = [state for state in states if state.stage != Stage.COMPLETE]
    return [_summary(state) for state in states]


@mcp.tool()
def record_knowledge_context(task_id: str, refs: list[str], notes: list[str] | None = None) -> dict[str, Any]:
    """Record references retrieved through connected durable knowledge stores during RESEARCH. Use after ChatGPT actually reads relevant Notion/Drive/StockBase/EventBase material; this records receipts only and never pretends the runtime performed the external read."""
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH)
    state.working["knowledge_context_refs"] = list(dict.fromkeys(refs))
    state.working["knowledge_context_notes"] = notes or []
    state.add_trace("KNOWLEDGE_CONTEXT", f"refs={len(refs)}")
    store.save(state)
    return _summary(state)


@mcp.tool()
def submit_research(task_id: str, research: dict[str, Any]) -> dict[str, Any]:
    """Submit the complete structured ResearchPackage at RESEARCH after broad/deep current research. Validates evidence, cognition and explicit coverage/stop conditions, freezes the package, and advances to independent RESEARCH_AUDIT."""
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH)
    payload = ResearchPackage.model_validate(research)
    state.working["research"] = payload.model_dump(mode="json")
    state.set_gate("research_output", GateStatus.PASS, [f"evidence_items={len(payload.evidence_ledger)}", f"universe={len(payload.universe)}", f"coverage={payload.coverage.coverage_status}", f"sweeps={payload.coverage.sweeps_completed}", f"knowledge_writeback_candidates={len(payload.knowledge_writeback_candidates)}"])
    state.add_trace("MCP_STAGE_OUTPUT", "research package accepted")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_research_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    """Submit the independent research-audit verdict at RESEARCH_AUDIT. PASS advances; REVISE must explicitly target RESEARCH; FAIL blocks. Evidence is mandatory."""
    state = _load(task_id)
    _require_stage(state, Stage.RESEARCH_AUDIT)
    payload = GateDecision.model_validate(decision)
    _validate_revision_target(payload, {"RESEARCH"}, "research_audit")
    return _summary(_apply_gate_decision(state, "research_audit", payload))


@mcp.tool()
def submit_editorial_plan(task_id: str, editorial_plan: dict[str, Any]) -> dict[str, Any]:
    """Submit TopicDNA plus at least two candidate structures at EDITORIAL. The selected structure must be one of the candidates and applicable platform emphasis must be present; advances to TITLE."""
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL)
    payload = EditorialPlan.model_validate(editorial_plan)
    _validate_editorial_for_contract(state, payload)
    state.working["editorial_plan"] = payload.model_dump(mode="json")
    state.set_gate("editorial_plan", GateStatus.PASS, ["TopicDNA", f"structures={len(payload.candidates)}", f"selected={payload.selected_structure.name}"])
    state.add_trace("MCP_STAGE_OUTPUT", "editorial plan accepted")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_headlines(task_id: str, headlines: dict[str, Any]) -> dict[str, Any]:
    """Submit headline candidates at TITLE after judging them. Formal applicable modes require 8-12 candidates each; sticker mode requires 4-12. Every selected title must come from its candidate list."""
    state = _load(task_id)
    _require_stage(state, Stage.TITLE)
    payload = HeadlinePackage.model_validate(headlines)
    _validate_headlines_for_contract(state, payload)
    state.working["headlines"] = payload.model_dump(mode="json")
    state.set_gate("title_audit", GateStatus.PASS, ["candidate counts and selected-title membership validated"])
    state.add_trace("MCP_STAGE_OUTPUT", "title_audit=PASS")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_draft(task_id: str, draft: dict[str, Any]) -> dict[str, Any]:
    """Submit every draft payload required by the TaskContract at DRAFT. DUAL must include both FINANCE_DEEP and FINANCE_BROAD immediately; risk/disclaimer text is a required explicit field and is appended deterministically during delivery."""
    state = _load(task_id)
    _require_stage(state, Stage.DRAFT)
    payload = DraftPackage.model_validate(draft)
    _validate_draft_for_contract(state, payload)
    state.working["draft"] = payload.model_dump(mode="json")
    state.set_gate("draft_output", GateStatus.PASS, ["all contract-required draft payloads validated and frozen"])
    state.add_trace("MCP_STAGE_OUTPUT", "draft package accepted")
    return _summary(_save_and_advance(state))


@mcp.tool()
def submit_style_audit(task_id: str, report: dict[str, Any]) -> dict[str, Any]:
    """Record the independent anti-AI/style audit at EDITORIAL_AUDIT before the general editorial audit. A five-part rubric must be internally consistent; REVISE requires concrete revision notes. Does not advance by itself."""
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
    """Submit the independent semantic editorial verdict at EDITORIAL_AUDIT. PASS is illegal until style_audit passes; REVISE may target only TITLE or DRAFT; FAIL blocks."""
    state = _load(task_id)
    _require_stage(state, Stage.EDITORIAL_AUDIT)
    payload = GateDecision.model_validate(decision)
    _validate_revision_target(payload, {"TITLE", "DRAFT"}, "editorial_audit")
    if payload.status == "PASS" and _gate_status(state, "style_audit") != "PASS":
        raise ValueError("style_audit must PASS before editorial_audit can PASS")
    return _summary(_apply_gate_decision(state, "editorial_audit", payload, revision_key="revise_target"))


@mcp.tool(meta={"openai/fileParams": ["files"]})
def submit_visual_package(task_id: str, visual_package: dict[str, Any], files: list[OpenAIFileRef]) -> dict[str, Any]:
    """Submit real generated image files at DELIVERY when visuals are enabled. Each VisualAsset references a ChatGPT file_id supplied in files; the server securely copies those image bytes into task storage, validates applicable modes/ratios/avatar flags and sticker image-count limits, then records the visual gate. Never pass arbitrary server paths or URLs."""
    state = _load(task_id)
    _require_stage(state, Stage.DELIVERY)
    if not state.contract.visuals_enabled:
        raise ValueError("task visuals_enabled=false; do not submit a visual package")
    payload = VisualPackage.model_validate(visual_package)
    referenced_ids = {asset.file_id for asset in payload.assets}
    supplied_ids = {file_ref.file_id for file_ref in files}
    missing = referenced_ids - supplied_ids
    if missing:
        raise ValueError(f"missing ChatGPT file param(s) for visual assets: {sorted(missing)}")
    resolved_paths = _download_visual_files(task_id, [file_ref for file_ref in files if file_ref.file_id in referenced_ids])

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
        assets = [asset for asset in payload.assets if asset.article_mode == mode]
        if not assets:
            raise ValueError(f"missing visuals for applicable mode: {mode}")
        if mode == "WECHAT_STICKER_POST":
            if not any(asset.role in {"sticker", "hero"} for asset in assets):
                raise ValueError("WeChat sticker mode requires at least one sticker/hero image")
            draft = DraftPackage.model_validate(state.working["draft"])
            limit = draft.wechat_sticker_post.constraints.image_max_count if draft.wechat_sticker_post else None
            if limit is not None and len(assets) > limit:
                raise ValueError(f"sticker image count exceeds verified platform limit: {len(assets)} > {limit}")
        else:
            heroes = [asset for asset in assets if asset.role == "hero"]
            if len(heroes) != 1:
                raise ValueError(f"{mode} requires exactly one hero visual")
            if any(asset.aspect_ratio != "16:9" for asset in assets):
                raise ValueError(f"{mode} formal visuals must declare aspect_ratio=16:9")
        if payload.avatar_required and any(not asset.avatar_included for asset in assets):
            raise ValueError(f"approved avatar missing from one or more {mode} visuals")
        evidence.append(f"{mode}_visuals={len(assets)}")

    resolved = ResolvedVisualPackage(
        assets=[ResolvedVisualAsset(**asset.model_dump(), local_path=resolved_paths[asset.file_id]) for asset in payload.assets],
        avatar_required=payload.avatar_required,
        target_chars_per_section_image=payload.target_chars_per_section_image,
        planning_notes=payload.planning_notes,
    )
    state.working["visual_package"] = payload.model_dump(mode="json")
    state.working["resolved_visual_package"] = resolved.model_dump(mode="json")
    state.set_gate("visual_assets", GateStatus.PASS, evidence)
    state.add_trace("MCP_STAGE_OUTPUT", "visual package accepted from ChatGPT file params")
    store.save(state)
    return _summary(state)


@mcp.tool()
def build_and_mechanically_audit_delivery(task_id: str) -> dict[str, Any]:
    """Build required Word/text artifacts and run deterministic mechanical/render checks. Use only at DELIVERY or MECHANICAL_AUDIT after required visual files are submitted. May move the task to FINAL_AUDIT or back to DELIVERY for repair."""
    state = _load(task_id)
    if state.stage == Stage.DELIVERY:
        if state.contract.visuals_enabled and "resolved_visual_package" not in state.working:
            raise ValueError("real visual files are required before delivery; call submit_visual_package first")
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
    return _summary(state, detail=True)


@mcp.tool()
def record_knowledge_writeback(task_id: str, status: str, refs: list[str] | None = None, notes: list[str] | None = None) -> dict[str, Any]:
    """Record the explicit knowledge-writeback outcome at FINAL_AUDIT. Use PASS only after connected-store writeback actually succeeds and include receipts; use N_A with a reason when no reusable item or writable destination exists. Required before final PASS."""
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


@mcp.tool()
def submit_final_audit(task_id: str, decision: dict[str, Any]) -> dict[str, Any]:
    """Submit the final independent red-team verdict at FINAL_AUDIT. PASS requires an explicit knowledge_sync PASS/N_A decision and all prior gates/artifacts; REVISE may target only EDITORIAL or DELIVERY; FAIL blocks. PASS generates the audit report and may complete the task."""
    state = _load(task_id)
    _require_stage(state, Stage.FINAL_AUDIT)
    payload = GateDecision.model_validate(decision)
    _validate_revision_target(payload, {"EDITORIAL", "DELIVERY"}, "final_audit")
    if payload.status == "PASS" and _gate_status(state, "knowledge_sync") not in {"PASS", "N_A"}:
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


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    mcp.run(transport="streamable-http", host=host, port=port, streamable_http_path="/mcp", stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
