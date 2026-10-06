from __future__ import annotations

import os
from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from pydantic import Field

from . import mcp_server as impl
from .mcp_contracts import FILE_INGEST_TOOL, READ_ONLY_TOOL, STATE_WRITE_TOOL, WritingTaskList, WritingTaskSummary
from .models import ContentMode
from .schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, OpenAIFileRef, ResearchPackage, StyleAuditDecision, VisualPackage


def _summary(raw: dict) -> WritingTaskSummary:
    return WritingTaskSummary.model_validate(raw)


mcp = MCPServer(
    "Financial Writing Agent",
    instructions=(
        "Use this server only for publishable A-share financial writing and continuation. "
        "Resume unfinished tasks before starting new ones. Start runtime state before research. "
        "Follow the returned next_action and never skip a gate. The model owns research, writing, audits and image generation; "
        "the runtime owns state, schemas, legal transitions, Word construction and mechanical QA."
    ),
)


@mcp.tool(title="Start financial writing task", annotations=STATE_WRITE_TOOL, structured_output=True)
def start_writing_task(
    prompt: Annotated[str, Field(min_length=1, description="The user's concrete publishable financial-writing request.")],
    source_refs: Annotated[list[str] | None, Field(description="Explicit source URLs or references supplied for this task.")] = None,
    target_platforms: Annotated[list[str] | None, Field(description="Explicit destination platforms; omit to use the formal default routing.")] = None,
    visuals_enabled: Annotated[bool | None, Field(description="Explicit visual override; omit to use runtime defaults.")] = None,
    visual_profile_ref: Annotated[str | None, Field(description="Reference to an already-approved visual/avatar profile when available.")] = None,
    content_mode: Annotated[ContentMode | None, Field(description="Explicit content mode override only when the request clearly requires it.")] = None,
) -> WritingTaskSummary:
    """Create a new persisted writing workflow. Use only for a genuinely new publishable finance-writing task after ruling out a relevant unfinished task."""
    return _summary(impl.start_writing_task(
        prompt=prompt,
        source_refs=source_refs,
        target_platforms=target_platforms,
        visuals_enabled=visuals_enabled,
        visual_profile_ref=visual_profile_ref,
        content_mode=content_mode.value if content_mode else None,
    ))


@mcp.tool(title="Get writing task", annotations=READ_ONLY_TOOL, structured_output=True)
def get_writing_task(
    task_id: Annotated[str, Field(min_length=1, description="Exact persisted task ID returned by this runtime.")],
    detail: Annotated[bool, Field(description="Return gates, artifacts and trace details when true.")] = True,
) -> WritingTaskSummary:
    """Read one persisted writing task without changing it. Use after task listing or when an exact task ID is already known."""
    return _summary(impl.get_writing_task(task_id, detail=detail))


@mcp.tool(title="List recent writing tasks", annotations=READ_ONLY_TOOL, structured_output=True)
def list_recent_writing_tasks(
    limit: Annotated[int, Field(ge=1, le=50, description="Maximum number of recent tasks to return.")] = 10,
    include_complete: Annotated[bool, Field(description="Include already completed tasks when true.")] = False,
) -> WritingTaskList:
    """List recent persisted writing tasks for reliable continuation. Read-only and intended to prevent starting duplicate workflows or asking the user to repeat context."""
    return WritingTaskList(tasks=[_summary(item) for item in impl.list_recent_writing_tasks(limit=limit, include_complete=include_complete)])


@mcp.tool(title="Record retrieved knowledge context", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_knowledge_context(
    task_id: Annotated[str, Field(min_length=1)],
    refs: Annotated[list[str], Field(min_length=1, description="Real references already retrieved through connected durable knowledge stores.")],
    notes: Annotated[list[str] | None, Field(description="Optional concise notes about reuse boundaries or conflicts.")] = None,
) -> WritingTaskSummary:
    """Record receipts for connected knowledge that ChatGPT actually retrieved during RESEARCH. This does not perform external retrieval itself."""
    return _summary(impl.record_knowledge_context(task_id, refs, notes))


@mcp.tool(title="Submit research package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_research(task_id: Annotated[str, Field(min_length=1)], research: ResearchPackage) -> WritingTaskSummary:
    """Validate and freeze the complete ResearchPackage at RESEARCH, including evidence, broad/deep cognition and explicit bounded-coverage stopping conditions."""
    return _summary(impl.submit_research(task_id, research.model_dump(mode="json")))


@mcp.tool(title="Submit research audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_research_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> WritingTaskSummary:
    """Record the independent research-audit verdict. PASS advances, REVISE must target RESEARCH, and FAIL blocks the persisted workflow."""
    return _summary(impl.submit_research_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Submit editorial plan", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_editorial_plan(task_id: Annotated[str, Field(min_length=1)], editorial_plan: EditorialPlan) -> WritingTaskSummary:
    """Validate TopicDNA and multiple candidate structures at EDITORIAL, including all emphasis fields required by the current content contract."""
    return _summary(impl.submit_editorial_plan(task_id, editorial_plan.model_dump(mode="json")))


@mcp.tool(title="Submit headline package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_headlines(task_id: Annotated[str, Field(min_length=1)], headlines: HeadlinePackage) -> WritingTaskSummary:
    """Validate candidate headline sets and selected-title membership at TITLE. Required candidate counts differ by formal article and WeChat sticker mode."""
    return _summary(impl.submit_headlines(task_id, headlines.model_dump(mode="json")))


@mcp.tool(title="Submit draft package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_draft(task_id: Annotated[str, Field(min_length=1)], draft: DraftPackage) -> WritingTaskSummary:
    """Validate every draft required by the TaskContract at DRAFT. DUAL must contain both articles and risk text is an explicit required field rather than an optional prose convention."""
    return _summary(impl.submit_draft(task_id, draft.model_dump(mode="json")))


@mcp.tool(title="Submit style audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_style_audit(task_id: Annotated[str, Field(min_length=1)], report: StyleAuditDecision) -> WritingTaskSummary:
    """Record the independent anti-AI/style rubric at EDITORIAL_AUDIT. This gate must pass before the general editorial audit may pass."""
    return _summary(impl.submit_style_audit(task_id, report.model_dump(mode="json")))


@mcp.tool(title="Submit editorial audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_editorial_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> WritingTaskSummary:
    """Record the independent semantic editorial verdict. PASS requires a passed style gate; REVISE may target only TITLE or DRAFT; FAIL blocks."""
    return _summary(impl.submit_editorial_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(
    title="Submit publication visuals",
    annotations=FILE_INGEST_TOOL,
    meta={"openai/fileParams": ["files"]},
    structured_output=True,
)
def submit_visual_package(
    task_id: Annotated[str, Field(min_length=1)],
    visual_package: VisualPackage,
    files: Annotated[list[OpenAIFileRef], Field(min_length=1, description="ChatGPT-authorized generated/uploaded image file parameters referenced by file_id.")],
) -> WritingTaskSummary:
    """Accept real image file parameters at DELIVERY, validate mode/count/ratio/avatar requirements, copy bytes into task storage and record the visual gate. It never accepts server paths as user input."""
    return _summary(impl.submit_visual_package(task_id, visual_package.model_dump(mode="json"), files))


@mcp.tool(title="Build and mechanically audit delivery", annotations=STATE_WRITE_TOOL, structured_output=True)
def build_and_mechanically_audit_delivery(task_id: Annotated[str, Field(min_length=1)]) -> WritingTaskSummary:
    """Build the contract-required publication artifacts and run deterministic formatting, file-identity, image-count and render checks before final semantic audit."""
    return _summary(impl.build_and_mechanically_audit_delivery(task_id))


@mcp.tool(title="Record knowledge writeback outcome", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_knowledge_writeback(
    task_id: Annotated[str, Field(min_length=1)],
    status: Literal["PASS", "N_A"],
    refs: Annotated[list[str] | None, Field(description="Actual connected-store receipt references when writeback succeeded.")] = None,
    notes: Annotated[list[str] | None, Field(description="Reason/boundary notes; required by the runtime for N_A.")] = None,
) -> WritingTaskSummary:
    """Record the explicit connected-knowledge writeback decision at FINAL_AUDIT. PASS needs receipts; N_A needs an explicit reason; this tool never performs the external write itself."""
    return _summary(impl.record_knowledge_writeback(task_id, status, refs, notes))


@mcp.tool(title="Submit final audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_final_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> WritingTaskSummary:
    """Record the final independent red-team verdict. PASS requires prior artifact/gate completion plus an explicit knowledge-sync decision and may complete the task."""
    return _summary(impl.submit_final_audit(task_id, decision.model_dump(mode="json")))


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    mcp.run(transport="streamable-http", host=host, port=port, streamable_http_path="/mcp", stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
