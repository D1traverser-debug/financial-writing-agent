from __future__ import annotations

import os
from datetime import datetime
from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations
from pydantic import BaseModel, Field

from . import mcp_server as impl
from .models import ArtifactKind, ContentMode, DeliveryChannel, DistributionMode, GateStatus, Stage
from .schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, OpenAIFileRef, ResearchPackage, StyleAuditDecision, VisualPackage


class GateView(BaseModel):
    status: str
    evidence: list[str] = Field(default_factory=list)
    notes: str = ""


class ArtifactView(BaseModel):
    path: str
    exists: bool
    sha256: str | None = None


class TraceView(BaseModel):
    seq: int
    stage: Stage
    event: str
    detail: str = ""
    at: datetime


class StyleChecklist(BaseModel):
    editorial: str
    anti_ai_style: str


class KnowledgeChecklist(BaseModel):
    sync_gate: str
    reused_refs: int
    writeback_candidates: int
    writeback_receipts: int


class CompletionChecklist(BaseModel):
    runtime_gates: str
    research_evidence: str
    structure_style_continuity: StyleChecklist
    word_render: str
    compliance_risk: str
    visuals: str
    knowledge: KnowledgeChecklist


class TaskSummary(BaseModel):
    task_id: str
    status: Literal["IN_PROGRESS", "BLOCKED", "COMPLETE"]
    current_stage: Stage
    topic: str | None = None
    prompt_preview: str
    content_mode: ContentMode
    distribution_mode: DistributionMode
    delivery_channel: DeliveryChannel
    visuals_enabled: bool
    required_outputs: list[ArtifactKind]
    gate_status: dict[str, str]
    blocked_reason: str | None = None
    updated_at: datetime
    next_action: str
    source_refs: list[str] | None = None
    visual_profile_ref: str | None = None
    gates: dict[str, GateView] | None = None
    artifacts: dict[str, ArtifactView] | None = None
    trace_tail: list[TraceView] | None = None
    completion_checklist: CompletionChecklist | None = None


class TaskListResult(BaseModel):
    tasks: list[TaskSummary]


def _summary(raw: dict) -> TaskSummary:
    return TaskSummary.model_validate(raw)


def _write_annotations(*, open_world: bool = False) -> ToolAnnotations:
    return ToolAnnotations(read_only_hint=False, destructive_hint=False, idempotent_hint=False, open_world_hint=open_world)


def _read_annotations() -> ToolAnnotations:
    return ToolAnnotations(read_only_hint=True, destructive_hint=False, idempotent_hint=True, open_world_hint=False)


mcp = MCPServer(
    "Financial Writing Agent",
    instructions=(
        "Use this server only for publishable A-share financial writing and continuation. "
        "Resume unfinished tasks before starting new ones. Start runtime state before research. "
        "Follow the returned next_action and never skip a gate. The model owns research, writing, audits and image generation; "
        "the runtime owns state, schemas, legal transitions, Word construction and mechanical QA."
    ),
)


@mcp.tool(
    title="Start financial writing task",
    annotations=_write_annotations(),
    structured_output=True,
)
def start_writing_task(
    prompt: Annotated[str, Field(min_length=1, description="The user's concrete publishable financial-writing request.")],
    source_refs: Annotated[list[str] | None, Field(description="Explicit source URLs or references supplied for this task.")] = None,
    target_platforms: Annotated[list[str] | None, Field(description="Explicit destination platforms; omit to use the formal default routing.")] = None,
    visuals_enabled: Annotated[bool | None, Field(description="Explicit visual override; omit to use runtime defaults.")] = None,
    visual_profile_ref: Annotated[str | None, Field(description="Reference to an already-approved visual/avatar profile when available.")] = None,
    content_mode: Annotated[ContentMode | None, Field(description="Explicit content mode override only when the request clearly requires it.")] = None,
) -> TaskSummary:
    """Create a new persisted writing workflow. Use only for a genuinely new publishable finance-writing task after ruling out a relevant unfinished task."""
    return _summary(impl.start_writing_task(
        prompt=prompt,
        source_refs=source_refs,
        target_platforms=target_platforms,
        visuals_enabled=visuals_enabled,
        visual_profile_ref=visual_profile_ref,
        content_mode=content_mode.value if content_mode else None,
    ))


@mcp.tool(title="Get writing task", annotations=_read_annotations(), structured_output=True)
def get_writing_task(
    task_id: Annotated[str, Field(min_length=1, description="Exact persisted task ID returned by this runtime.")],
    detail: Annotated[bool, Field(description="Return gates, artifacts and trace details when true.")] = True,
) -> TaskSummary:
    """Read one persisted writing task without changing it. Use after task listing or when an exact task ID is already known."""
    return _summary(impl.get_writing_task(task_id, detail=detail))


@mcp.tool(title="List recent writing tasks", annotations=_read_annotations(), structured_output=True)
def list_recent_writing_tasks(
    limit: Annotated[int, Field(ge=1, le=50, description="Maximum number of recent tasks to return.")] = 10,
    include_complete: Annotated[bool, Field(description="Include already completed tasks when true.")] = False,
) -> TaskListResult:
    """List recent persisted writing tasks for reliable continuation. Read-only and intended to prevent starting duplicate workflows or asking the user to repeat context."""
    return TaskListResult(tasks=[_summary(item) for item in impl.list_recent_writing_tasks(limit=limit, include_complete=include_complete)])


@mcp.tool(title="Record retrieved knowledge context", annotations=_write_annotations(), structured_output=True)
def record_knowledge_context(
    task_id: Annotated[str, Field(min_length=1)],
    refs: Annotated[list[str], Field(min_length=1, description="Real references already retrieved through connected durable knowledge stores.")],
    notes: Annotated[list[str] | None, Field(description="Optional concise notes about reuse boundaries or conflicts.")] = None,
) -> TaskSummary:
    """Record receipts for connected knowledge that ChatGPT actually retrieved during RESEARCH. This does not perform external retrieval itself."""
    return _summary(impl.record_knowledge_context(task_id, refs, notes))


@mcp.tool(title="Submit research package", annotations=_write_annotations(), structured_output=True)
def submit_research(task_id: Annotated[str, Field(min_length=1)], research: ResearchPackage) -> TaskSummary:
    """Validate and freeze the complete ResearchPackage at RESEARCH, including evidence, broad/deep cognition and explicit bounded-coverage stopping conditions."""
    return _summary(impl.submit_research(task_id, research.model_dump(mode="json")))


@mcp.tool(title="Submit research audit", annotations=_write_annotations(), structured_output=True)
def submit_research_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> TaskSummary:
    """Record the independent research-audit verdict. PASS advances, REVISE must target RESEARCH, and FAIL blocks the persisted workflow."""
    return _summary(impl.submit_research_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Submit editorial plan", annotations=_write_annotations(), structured_output=True)
def submit_editorial_plan(task_id: Annotated[str, Field(min_length=1)], editorial_plan: EditorialPlan) -> TaskSummary:
    """Validate TopicDNA and multiple candidate structures at EDITORIAL, including all emphasis fields required by the current content contract."""
    return _summary(impl.submit_editorial_plan(task_id, editorial_plan.model_dump(mode="json")))


@mcp.tool(title="Submit headline package", annotations=_write_annotations(), structured_output=True)
def submit_headlines(task_id: Annotated[str, Field(min_length=1)], headlines: HeadlinePackage) -> TaskSummary:
    """Validate candidate headline sets and selected-title membership at TITLE. Required candidate counts differ by formal article and WeChat sticker mode."""
    return _summary(impl.submit_headlines(task_id, headlines.model_dump(mode="json")))


@mcp.tool(title="Submit draft package", annotations=_write_annotations(), structured_output=True)
def submit_draft(task_id: Annotated[str, Field(min_length=1)], draft: DraftPackage) -> TaskSummary:
    """Validate every draft required by the TaskContract at DRAFT. DUAL must contain both articles and risk text is an explicit required field rather than an optional prose convention."""
    return _summary(impl.submit_draft(task_id, draft.model_dump(mode="json")))


@mcp.tool(title="Submit style audit", annotations=_write_annotations(), structured_output=True)
def submit_style_audit(task_id: Annotated[str, Field(min_length=1)], report: StyleAuditDecision) -> TaskSummary:
    """Record the independent anti-AI/style rubric at EDITORIAL_AUDIT. This gate must pass before the general editorial audit may pass."""
    return _summary(impl.submit_style_audit(task_id, report.model_dump(mode="json")))


@mcp.tool(title="Submit editorial audit", annotations=_write_annotations(), structured_output=True)
def submit_editorial_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> TaskSummary:
    """Record the independent semantic editorial verdict. PASS requires a passed style gate; REVISE may target only TITLE or DRAFT; FAIL blocks."""
    return _summary(impl.submit_editorial_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(
    title="Submit publication visuals",
    annotations=_write_annotations(open_world=True),
    meta={"openai/fileParams": ["files"]},
    structured_output=True,
)
def submit_visual_package(
    task_id: Annotated[str, Field(min_length=1)],
    visual_package: VisualPackage,
    files: Annotated[list[OpenAIFileRef], Field(min_length=1, description="ChatGPT-authorized generated/uploaded image file parameters referenced by file_id.")],
) -> TaskSummary:
    """Accept real image file parameters at DELIVERY, validate mode/count/ratio/avatar requirements, copy bytes into task storage and record the visual gate. It never accepts server paths as user input."""
    return _summary(impl.submit_visual_package(task_id, visual_package.model_dump(mode="json"), files))


@mcp.tool(title="Build and mechanically audit delivery", annotations=_write_annotations(), structured_output=True)
def build_and_mechanically_audit_delivery(task_id: Annotated[str, Field(min_length=1)]) -> TaskSummary:
    """Build the contract-required publication artifacts and run deterministic formatting, file-identity, image-count and render checks before final semantic audit."""
    return _summary(impl.build_and_mechanically_audit_delivery(task_id))


@mcp.tool(title="Record knowledge writeback outcome", annotations=_write_annotations(), structured_output=True)
def record_knowledge_writeback(
    task_id: Annotated[str, Field(min_length=1)],
    status: Literal["PASS", "N_A"],
    refs: Annotated[list[str] | None, Field(description="Actual connected-store receipt references when writeback succeeded.")] = None,
    notes: Annotated[list[str] | None, Field(description="Reason/boundary notes; required by the runtime for N_A.")] = None,
) -> TaskSummary:
    """Record the explicit connected-knowledge writeback decision at FINAL_AUDIT. PASS needs receipts; N_A needs an explicit reason; this tool never performs the external write itself."""
    return _summary(impl.record_knowledge_writeback(task_id, status, refs, notes))


@mcp.tool(title="Submit final audit", annotations=_write_annotations(), structured_output=True)
def submit_final_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> TaskSummary:
    """Record the final independent red-team verdict. PASS requires prior artifact/gate completion plus an explicit knowledge-sync decision and may complete the task."""
    return _summary(impl.submit_final_audit(task_id, decision.model_dump(mode="json")))


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    mcp.run(transport="streamable-http", host=host, port=port, streamable_http_path="/mcp", stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
