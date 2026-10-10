from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, ResourceLink, TextContent
from pydantic import Field

from . import runtime_service as impl
from .mcp_contracts import LearningSampleType, READ_ONLY_TOOL, STATE_WRITE_TOOL, WritingTaskList, WritingTaskSummary
from .methodology_receipts import record_artifact_io_receipt, record_learning_evolution_receipt
from .models import ArtifactKind, GateStatus, Stage
from .schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, HookAuditDecision, ResearchPackage, StyleAuditDecision
from .semantic_runtime import run_owner_semantic_audit_stage

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
DOCX_KINDS = {ArtifactKind.FINANCE_DEEP_DOCX, ArtifactKind.FINANCE_BROAD_DOCX, ArtifactKind.AUDIT_DOCX}


def _artifact_public_fields(kind: str, path_value: str) -> dict[str, str]:
    artifact_kind = ArtifactKind(kind)
    if artifact_kind not in DOCX_KINDS:
        raise ValueError(f"unsupported publication artifact kind: {kind}")
    return {
        "file_name": Path(path_value).name,
        "resource_uri": f"writing-docx://artifact/{kind}",
        "mime_type": DOCX_MIME,
    }


def _publicize(raw: dict) -> dict:
    clean = dict(raw)
    task_id = clean.get("task_id")
    clean.pop("trace_tail", None)
    artifacts: dict[str, dict] = {}
    for kind, value in (clean.get("artifacts") or {}).items():
        item = dict(value)
        path_value = item.pop("path", "")
        item.pop("download_url", None)
        item.update(_artifact_public_fields(kind, path_value))
        item["resource_uri"] = item["resource_uri"].replace("artifact/", f"{task_id}/")
        artifacts[kind] = item
    if "artifacts" in clean:
        clean["artifacts"] = artifacts
    return clean


def _summary(raw: dict) -> WritingTaskSummary:
    enriched = dict(raw)
    task_id = enriched.get("task_id")
    detail_requested = any(key in enriched for key in ("source_refs", "gates", "artifacts", "learning_samples"))
    if isinstance(task_id, str) and task_id and detail_requested:
        try:
            state = impl._load(task_id)
        except ValueError:
            state = None
        if state is not None:
            enriched["methodology_profile_runs"] = list(state.working.get("methodology_profile_runs", []))
    return WritingTaskSummary.model_validate(_publicize(enriched))


def _resource_bytes(task_id: str, kind: str) -> bytes:
    state = impl._load(task_id)
    try:
        artifact_kind = ArtifactKind(kind)
    except ValueError as exc:
        raise ValueError(f"unknown artifact kind: {kind}") from exc
    if artifact_kind not in DOCX_KINDS:
        raise ValueError(f"artifact kind not valid for Word resource: {kind}")
    artifact = state.artifacts.get(artifact_kind)
    if artifact is None or not artifact.exists:
        raise FileNotFoundError(f"artifact not available: {kind}")
    path = Path(artifact.path).resolve()
    runs_root = impl.RUNS_DIR.resolve()
    if not path.is_relative_to(runs_root) or not path.is_file():
        raise FileNotFoundError(f"artifact file missing or outside task storage: {kind}")
    return path.read_bytes()


def _result_with_artifacts(summary: WritingTaskSummary) -> CallToolResult:
    content = [TextContent(type="text", text=f"Writing task {summary.task_id} is {summary.status} at {summary.current_stage}. {summary.next_action}")]
    for kind, artifact in (summary.artifacts or {}).items():
        if artifact.exists:
            content.append(ResourceLink(type="resource_link", uri=artifact.resource_uri, name=artifact.file_name, mime_type=artifact.mime_type, description=f"{kind} Word artifact for writing task {summary.task_id}"))
    return CallToolResult(content=content, structured_content=summary.model_dump(mode="json"))


def _reject_unverified_semantic_pass(status: str, gate_name: str) -> None:
    if status == "PASS":
        raise ValueError(
            f"{gate_name} PASS cannot be certified by a CHAT_BRIDGED submission. "
            "Call run_semantic_audit_stage so the owner runtime executes and proves the audit stage."
        )


mcp = MCPServer(
    "Financial Writing Agent",
    instructions=(
        "Use this server only for publishable A-share financial writing and continuation. "
        "Resume unfinished tasks before starting new ones, start runtime state before research, and never skip a gate. "
        "Financial Writing v0.8 is Word-only, has no image workflow, and has no legacy text-artifact compatibility surface. "
        "BLOCKED tasks preserve an explicit recovery cursor and must be resumed with resume_blocked_task after the blocker is repaired. "
        "Raw user edits, feedback and post-publication performance may be recorded as Writing DNA evidence, but a single sample never auto-promotes itself into a durable rule. "
        "CHAT_BRIDGED audit payloads may request revision or report failure, but they cannot certify semantic PASS. Use run_semantic_audit_stage for owner-runtime Research, Editorial or Final audit certification. "
        "Methodology profile receipts are unverified owner receipts only; they never self-certify operational conformance and require Universal independent evidence verification. "
        "The model owns research and drafting; semantic PASS authority requires the owner-runtime stage execution path; the runtime owns state, schemas, legal transitions, Word construction and mechanical QA."
    ),
)


@mcp.resource("writing-docx://{task_id}/{kind}", mime_type=DOCX_MIME)
def read_docx_artifact(task_id: str, kind: str) -> bytes:
    """Read one completed Word artifact belonging to a persisted financial-writing task."""
    return _resource_bytes(task_id, kind)


@mcp.tool(title="Start financial writing task", annotations=STATE_WRITE_TOOL, structured_output=True)
def start_writing_task(
    prompt: Annotated[str, Field(min_length=1, description="The user's concrete publishable financial-writing request.")],
    source_refs: Annotated[list[str] | None, Field(description="Explicit source URLs or references supplied for this task.")] = None,
    target_platforms: Annotated[list[str] | None, Field(description="Explicit destination platforms; omit to use the formal default routing.")] = None,
) -> WritingTaskSummary:
    """Create a persisted Word-only financial-writing workflow after continuation checks, fixing the task contract before any research, outlining, drafting or delivery begins."""
    return _summary(impl.start_writing_task(prompt=prompt, source_refs=source_refs, target_platforms=target_platforms))


@mcp.tool(title="Get writing task", annotations=READ_ONLY_TOOL, structured_output=True)
def get_writing_task(task_id: Annotated[str, Field(min_length=1)], detail: Annotated[bool, Field(description="Return gates, learning evidence, methodology receipts and publication artifact resources when true.")] = True) -> WritingTaskSummary:
    """Read one exact persisted financial-writing task, including its legal stage, blocked recovery cursor, optional gate evidence, raw Writing DNA evidence, unverified methodology action receipts and Word artifact resources, without mutating runtime state."""
    return _summary(impl.get_writing_task(task_id, detail=detail))


@mcp.tool(title="List recent writing tasks", annotations=READ_ONLY_TOOL, structured_output=True)
def list_recent_writing_tasks(limit: Annotated[int, Field(ge=1, le=50)] = 10, include_complete: bool = False) -> WritingTaskList:
    """List recent persisted writing-task metadata for reliable continuation without expanding detailed methodology receipts or asking the user to repeat saved context."""
    return WritingTaskList(tasks=[_summary(item) for item in impl.list_recent_writing_tasks(limit=limit, include_complete=include_complete)])


@mcp.tool(title="Resume blocked writing task", annotations=STATE_WRITE_TOOL, structured_output=True)
def resume_blocked_task(task_id: Annotated[str, Field(min_length=1)]) -> WritingTaskSummary:
    """Resume a BLOCKED writing task from its persisted recovery cursor after the external dependency or contract defect that caused the block has been repaired; never guesses a new stage."""
    return _summary(impl.resume_blocked_task(task_id))


@mcp.tool(title="Record writing learning sample", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_writing_learning_sample(
    task_id: Annotated[str, Field(min_length=1)],
    sample_type: LearningSampleType,
    summary: Annotated[str, Field(min_length=1, description="Concise statement of what the user changed, accepted/rejected, or what performance data showed.")],
    source_refs: Annotated[list[str] | None, Field(description="Optional durable references to a final draft, analytics view, message, file or other evidence.")] = None,
    original_excerpt: Annotated[str, Field(description="Optional original wording for a USER_EDIT sample.")] = "",
    revised_excerpt: Annotated[str, Field(description="Optional user-revised wording for a USER_EDIT sample.")] = "",
    metrics: Annotated[dict[str, str | int | float] | None, Field(description="Optional observed publication metrics such as impressions, reads, CTR, completion, shares or follows.")] = None,
    notes: list[str] | None = None,
) -> WritingTaskSummary:
    """Append raw Writing DNA evidence to the persisted task and emit an unverified action-scoped evolution receipt without changing article gates or silently promoting one sample into a global writing rule."""
    impl.record_writing_learning_sample(
        task_id,
        sample_type,
        summary,
        source_refs=source_refs,
        original_excerpt=original_excerpt,
        revised_excerpt=revised_excerpt,
        metrics=metrics,
        notes=notes,
    )
    state = impl._load(task_id)
    record_learning_evolution_receipt(state)
    impl.store.save(state)
    return _summary(impl.get_writing_task(task_id, detail=True))


@mcp.tool(title="Record retrieved knowledge context", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_knowledge_context(task_id: Annotated[str, Field(min_length=1)], refs: Annotated[list[str], Field(min_length=1)], notes: list[str] | None = None) -> WritingTaskSummary:
    """Record real durable-knowledge references retrieved before open-web expansion so prior knowledge reuse is auditable and never silently substituted for current verification."""
    return _summary(impl.record_knowledge_context(task_id, refs, notes))


@mcp.tool(title="Submit research package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_research(task_id: Annotated[str, Field(min_length=1)], research: ResearchPackage) -> WritingTaskSummary:
    """Validate and freeze the bounded ResearchPackage, including evidence, company universe, explicit market-explanation activation scope, counterevidence and repeated-sweep coverage."""
    return _summary(impl.submit_research(task_id, research.model_dump(mode="json")))


@mcp.tool(title="Submit research audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_research_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> WritingTaskSummary:
    """Submit conservative CHAT_BRIDGED research-audit REVISE/FAIL evidence. PASS certification must use run_semantic_audit_stage."""
    _reject_unverified_semantic_pass(decision.status, "research_audit")
    return _summary(impl.submit_research_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Submit editorial plan", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_editorial_plan(task_id: Annotated[str, Field(min_length=1)], editorial_plan: EditorialPlan) -> WritingTaskSummary:
    """Validate shared TopicDNA plus independent mode contracts: material-complete FINANCE_DEEP obligations and selective-traffic FINANCE_BROAD contradictions and compression rules."""
    return _summary(impl.submit_editorial_plan(task_id, editorial_plan.model_dump(mode="json")))


@mcp.tool(title="Submit headline package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_headlines(task_id: Annotated[str, Field(min_length=1)], headlines: HeadlinePackage) -> WritingTaskSummary:
    """Validate 8–12 headline candidates per mode with target-reader fit, click reason, promised payoff, information gap, cognitive load, current WeChat search evidence and optional broader-finance relevance."""
    return _summary(impl.submit_headlines(task_id, headlines.model_dump(mode="json")))


@mcp.tool(title="Submit draft package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_draft(task_id: Annotated[str, Field(min_length=1)], draft: DraftPackage) -> WritingTaskSummary:
    """Validate and freeze every required formal draft, including risk text and exact bold skim-path anchors that must later survive deterministic Word construction and QA."""
    return _summary(impl.submit_draft(task_id, draft.model_dump(mode="json")))


@mcp.tool(title="Submit reader funnel audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_hook_audit(task_id: Annotated[str, Field(min_length=1)], report: HookAuditDecision) -> WritingTaskSummary:
    """Submit conservative CHAT_BRIDGED Reader Funnel REVISE evidence. PASS certification is performed by the owner runtime through run_semantic_audit_stage at EDITORIAL_AUDIT."""
    _reject_unverified_semantic_pass(report.status, "hook_audit")
    return _summary(impl.submit_hook_audit(task_id, report.model_dump(mode="json")))


@mcp.tool(title="Submit authorial prose audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_style_audit(task_id: Annotated[str, Field(min_length=1)], report: StyleAuditDecision) -> WritingTaskSummary:
    """Submit conservative CHAT_BRIDGED Authorial Prose REVISE evidence. PASS certification is performed by the owner runtime through run_semantic_audit_stage at EDITORIAL_AUDIT."""
    _reject_unverified_semantic_pass(report.status, "style_audit")
    return _summary(impl.submit_style_audit(task_id, report.model_dump(mode="json")))


@mcp.tool(title="Submit editorial audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_editorial_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> WritingTaskSummary:
    """Submit conservative CHAT_BRIDGED general-editorial REVISE/FAIL evidence. PASS certification must use run_semantic_audit_stage."""
    _reject_unverified_semantic_pass(decision.status, "editorial_audit")
    return _summary(impl.submit_editorial_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Run owner semantic audit stage", annotations=STATE_WRITE_TOOL, structured_output=True)
def run_semantic_audit_stage(
    task_id: Annotated[str, Field(min_length=1)],
    stage: Literal["RESEARCH_AUDIT", "EDITORIAL_AUDIT", "FINAL_AUDIT"],
) -> Annotated[CallToolResult, WritingTaskSummary]:
    """Request proof-bearing semantic PASS certification from the owner-native server runtime. The server executes the actual stage-separated judge run(s); caller-supplied PASS is not accepted as proof. If the SDK/model runtime is unavailable or the judge cannot establish PASS, the authoritative workflow remains non-complete/recoverable."""
    state = impl._load(task_id)
    audited = run_owner_semantic_audit_stage(state, expected_stage=Stage(stage), impl=impl)
    return _result_with_artifacts(_summary(impl._summary(audited, detail=True)))


@mcp.tool(title="Build and mechanically audit delivery", annotations=STATE_WRITE_TOOL, structured_output=True)
def build_and_mechanically_audit_delivery(task_id: Annotated[str, Field(min_length=1)]) -> Annotated[CallToolResult, WritingTaskSummary]:
    """Build required Word artifacts, run deterministic mechanical/render checks, and persist an unverified action-scoped artifact_io receipt for later independent Universal verification."""
    raw = impl.build_and_mechanically_audit_delivery(task_id)
    state = impl._load(task_id)
    mechanical_gate = state.gates.get("mechanical_audit")
    if mechanical_gate is not None and mechanical_gate.status == GateStatus.PASS:
        record_artifact_io_receipt(state)
        impl.store.save(state)
        raw = impl.get_writing_task(task_id, detail=True)
    return _result_with_artifacts(_summary(raw))


@mcp.tool(title="Record knowledge writeback outcome", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_knowledge_writeback(task_id: Annotated[str, Field(min_length=1)], status: Literal["PASS", "N_A"], refs: list[str] | None = None, notes: list[str] | None = None) -> WritingTaskSummary:
    """Record the explicit durable-knowledge writeback decision before final completion, requiring real receipt references for PASS or an explicit boundary reason for N_A."""
    return _summary(impl.record_knowledge_writeback(task_id, status, refs, notes))


@mcp.tool(title="Submit final audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_final_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> Annotated[CallToolResult, WritingTaskSummary]:
    """Submit conservative CHAT_BRIDGED final-audit REVISE/FAIL evidence. Final PASS/COMPLETE certification must use run_semantic_audit_stage."""
    _reject_unverified_semantic_pass(decision.status, "final_audit")
    return _result_with_artifacts(_summary(impl.submit_final_audit(task_id, decision.model_dump(mode="json"))))


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    mcp.run(transport="streamable-http", host=host, port=port, streamable_http_path="/mcp", stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
