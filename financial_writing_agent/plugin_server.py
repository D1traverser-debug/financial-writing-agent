from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, ResourceLink, TextContent
from pydantic import Field

from . import runtime_service as impl
from .checks import sha256_file
from .mcp_contracts import FILE_INGEST_TOOL, READ_ONLY_TOOL, STATE_WRITE_TOOL, WritingTaskList, WritingTaskSummary
from .models import ArtifactKind, ContentMode
from .schemas import DraftPackage, EditorialPlan, FinalAuditDecision, GateDecision, HeadlinePackage, OpenAIFileRef, ResearchPackage, StyleAuditDecision, VisualPackage

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
JSON_MIME = "application/json"
TEXT_MIME = "text/plain; charset=utf-8"
PNG_MIME = "image/png"


def _artifact_public_fields(kind: str, path_value: str) -> dict[str, str]:
    file_name = Path(path_value).name
    if kind in {
        ArtifactKind.FINANCE_DEEP_DOCX.value,
        ArtifactKind.FINANCE_BROAD_DOCX.value,
        ArtifactKind.WECHAT_STICKER_DOCX.value,
        ArtifactKind.AUDIT_DOCX.value,
    }:
        return {"file_name": file_name, "resource_uri": f"writing-docx://artifact/{kind}", "mime_type": DOCX_MIME}
    if kind == ArtifactKind.VISUAL_MANIFEST_JSON.value:
        return {"file_name": file_name, "resource_uri": f"writing-json://artifact/{kind}", "mime_type": JSON_MIME}
    return {"file_name": file_name, "resource_uri": f"writing-text://artifact/{kind}", "mime_type": TEXT_MIME}


def _publicize(raw: dict) -> dict:
    clean = dict(raw)
    task_id = clean.get("task_id")
    if task_id and "effective_time_boundary" not in clean:
        clean["effective_time_boundary"] = impl._load(task_id).contract.effective_time_boundary
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
    return WritingTaskSummary.model_validate(_publicize(raw))


def _resource_bytes(task_id: str, kind: str, allowed: set[ArtifactKind]) -> bytes:
    state = impl._load(task_id)
    try:
        artifact_kind = ArtifactKind(kind)
    except ValueError as exc:
        raise ValueError(f"unknown artifact kind: {kind}") from exc
    if artifact_kind not in allowed:
        raise ValueError(f"artifact kind not valid for this resource: {kind}")
    artifact = state.artifacts.get(artifact_kind)
    if artifact is None or not artifact.exists:
        raise FileNotFoundError(f"artifact not available: {kind}")
    path = Path(artifact.path).resolve()
    runs_root = impl.RUNS_DIR.resolve()
    if not path.is_relative_to(runs_root):
        raise ValueError("artifact path escaped configured runs storage")
    if not path.is_file():
        raise FileNotFoundError(f"artifact file missing: {kind}")
    if not artifact.sha256:
        raise ValueError(f"artifact has no recorded checksum: {kind}")
    actual_sha = sha256_file(path)
    if actual_sha != artifact.sha256:
        raise ValueError(f"artifact checksum mismatch at resource read: {kind}")
    return path.read_bytes()


def _render_page_bytes(task_id: str, kind: str, page: int) -> bytes:
    state = impl._load(task_id)
    pages = (state.working.get("render_manifest") or {}).get(kind)
    if not pages:
        raise FileNotFoundError(f"render pages not available for {kind}")
    if page < 1 or page > len(pages):
        raise FileNotFoundError(f"render page out of range: {kind} page {page}")
    path = Path(pages[page - 1]).resolve()
    runs_root = impl.RUNS_DIR.resolve()
    if not path.is_relative_to(runs_root):
        raise ValueError("render page path escaped configured runs storage")
    if not path.is_file() or path.suffix.lower() != ".png":
        raise FileNotFoundError(f"render page missing: {kind} page {page}")
    return path.read_bytes()


def _result_with_artifacts(summary: WritingTaskSummary) -> CallToolResult:
    content = [TextContent(type="text", text=f"Writing task {summary.task_id} is {summary.status} at {summary.current_stage}. {summary.next_action}")]
    for kind, artifact in (summary.artifacts or {}).items():
        if artifact.exists:
            content.append(
                ResourceLink(
                    type="resource_link",
                    uri=artifact.resource_uri,
                    name=artifact.file_name,
                    mime_type=artifact.mime_type,
                    description=f"{kind} publication artifact for writing task {summary.task_id}",
                )
            )
    for kind, uris in (summary.render_pages or {}).items():
        for index, uri in enumerate(uris, start=1):
            content.append(
                ResourceLink(
                    type="resource_link",
                    uri=uri,
                    name=f"{kind}-page-{index}.png",
                    mime_type=PNG_MIME,
                    description=f"Rendered page {index} of {kind}; inspect before claiming visual page QA PASS",
                )
            )
    return CallToolResult(content=content, structured_content=summary.model_dump(mode="json"))


mcp = MCPServer(
    "Financial Writing Agent",
    instructions=(
        "Use this server only for publishable A-share financial writing and continuation. "
        "Decide explicit continuation versus a genuinely new task before using persisted task state. "
        "Only explicit continuation intent may restore an unfinished task; a new task must start fresh even when unfinished tasks exist, while durable learning may still be reused. "
        "Start runtime state before research. "
        "Treat effective_time_boundary returned by the task summary as the frozen evidence cutoff for research and final time-integrity review. "
        "Record durable-knowledge recall as PASS or explicit N_A before research submission. "
        "If a task is BLOCKED, repair the dependency and call resume_writing_task; never start a duplicate task merely to bypass BLOCKED. "
        "Follow the returned next_action and never skip a gate. The model owns research, writing, audits and image generation; "
        "the runtime owns state, schemas, legal transitions, acceptance contracts, Word construction and mechanical QA. "
        "When render-page resources are returned, inspect every page before submitting a PASS final audit."
    ),
)


@mcp.resource("writing-docx://{task_id}/{kind}", mime_type=DOCX_MIME)
def read_docx_artifact(task_id: str, kind: str) -> bytes:
    """Read one completed Word artifact belonging to a persisted writing task."""
    return _resource_bytes(task_id, kind, {ArtifactKind.FINANCE_DEEP_DOCX, ArtifactKind.FINANCE_BROAD_DOCX, ArtifactKind.WECHAT_STICKER_DOCX, ArtifactKind.AUDIT_DOCX})


@mcp.resource("writing-json://{task_id}/{kind}", mime_type=JSON_MIME)
def read_json_artifact(task_id: str, kind: str) -> bytes:
    """Read one JSON artifact belonging to a persisted writing task."""
    return _resource_bytes(task_id, kind, {ArtifactKind.VISUAL_MANIFEST_JSON})


@mcp.resource("writing-text://{task_id}/{kind}", mime_type=TEXT_MIME)
def read_text_artifact(task_id: str, kind: str) -> bytes:
    """Read one plain-text artifact belonging to a persisted writing task."""
    return _resource_bytes(task_id, kind, {ArtifactKind.CHAT_TEXT})


@mcp.resource("writing-render://{task_id}/{kind}/{page}", mime_type=PNG_MIME)
def read_render_page(task_id: str, kind: str, page: int) -> bytes:
    """Read one rendered Word page PNG so the final auditor can actually inspect pagination, clipping, whitespace and image placement."""
    return _render_page_bytes(task_id, kind, page)


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
    return _summary(impl.start_writing_task(prompt=prompt, source_refs=source_refs, target_platforms=target_platforms, visuals_enabled=visuals_enabled, visual_profile_ref=visual_profile_ref, content_mode=content_mode.value if content_mode else None))


@mcp.tool(title="Get writing task", annotations=READ_ONLY_TOOL, structured_output=True)
def get_writing_task(task_id: Annotated[str, Field(min_length=1, description="Exact persisted task ID returned by this runtime.")], detail: Annotated[bool, Field(description="Return gates, publication artifact resources and rendered-page evidence when true.")] = True) -> WritingTaskSummary:
    """Read one persisted writing task without changing it. Use after task listing or when an exact task ID is already known."""
    return _summary(impl.get_writing_task(task_id, detail=detail))


@mcp.tool(title="Resume blocked writing task", annotations=STATE_WRITE_TOOL, structured_output=True)
def resume_writing_task(task_id: Annotated[str, Field(min_length=1, description="Exact BLOCKED task ID to resume at its recorded original stage.")]) -> WritingTaskSummary:
    """Resume only a BLOCKED task after its external dependency or contract defect has been repaired. The runtime chooses the recorded original stage; callers cannot skip to an arbitrary stage."""
    return _summary(impl.resume_writing_task(task_id))


@mcp.tool(title="List recent writing tasks", annotations=READ_ONLY_TOOL, structured_output=True)
def list_recent_writing_tasks(limit: Annotated[int, Field(ge=1, le=50, description="Maximum number of recent tasks to return.")] = 10, include_complete: Annotated[bool, Field(description="Include already completed tasks when true.")] = False) -> WritingTaskList:
    """List recent persisted writing tasks for reliable continuation. Read-only and intended to prevent starting duplicate workflows or asking the user to repeat context."""
    return WritingTaskList(tasks=[_summary(item) for item in impl.list_recent_writing_tasks(limit=limit, include_complete=include_complete)])


@mcp.tool(title="Record durable knowledge recall outcome", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_knowledge_context(
    task_id: Annotated[str, Field(min_length=1)],
    status: Literal["PASS", "N_A"],
    refs: Annotated[list[str] | None, Field(description="Real references actually retrieved from durable prior knowledge when status=PASS.")] = None,
    notes: Annotated[list[str] | None, Field(description="Reuse/conflict notes, or the explicit reason durable knowledge is unavailable/not applicable when status=N_A.")] = None,
) -> WritingTaskSummary:
    """Close the pre-research durable-knowledge recall gate. PASS requires real retrieved references; N_A requires an explicit reason. This prevents silently skipping connected prior knowledge."""
    return _summary(impl.record_knowledge_context(task_id, status, refs, notes))


@mcp.tool(title="Submit research package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_research(task_id: Annotated[str, Field(min_length=1)], research: ResearchPackage) -> WritingTaskSummary:
    """Validate and freeze the complete ResearchPackage at RESEARCH after the knowledge-context PASS/N_A decision, including auditable evidence verification, broad/deep cognition, review-queue receipts and bounded coverage."""
    return _summary(impl.submit_research(task_id, research.model_dump(mode="json")))


@mcp.tool(title="Submit research audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_research_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> WritingTaskSummary:
    """Record the independent research-audit verdict. PASS advances, REVISE must target RESEARCH, and FAIL blocks the persisted workflow."""
    return _summary(impl.submit_research_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Submit editorial plan", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_editorial_plan(task_id: Annotated[str, Field(min_length=1)], editorial_plan: EditorialPlan) -> WritingTaskSummary:
    """Validate TopicDNA and independent mode-specific candidate structures at EDITORIAL, including focus, company-selection basis and outline-collision evidence."""
    return _summary(impl.submit_editorial_plan(task_id, editorial_plan.model_dump(mode="json")))


@mcp.tool(title="Submit headline package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_headlines(task_id: Annotated[str, Field(min_length=1)], headlines: HeadlinePackage) -> WritingTaskSummary:
    """Validate unique candidate headline sets, factual anchors, opening-payoff design and selected-title membership, then freeze the article acceptance contract."""
    return _summary(impl.submit_headlines(task_id, headlines.model_dump(mode="json")))


@mcp.tool(title="Submit draft package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_draft(task_id: Annotated[str, Field(min_length=1)], draft: DraftPackage) -> WritingTaskSummary:
    """Validate every required draft against the frozen acceptance contract, including independent lead placement, selected title and frozen H1 structure."""
    return _summary(impl.submit_draft(task_id, draft.model_dump(mode="json")))


@mcp.tool(title="Submit style audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_style_audit(task_id: Annotated[str, Field(min_length=1)], report: StyleAuditDecision) -> WritingTaskSummary:
    """Record the independent anti-AI/style rubric at EDITORIAL_AUDIT. This gate must pass before the general editorial audit may pass."""
    return _summary(impl.submit_style_audit(task_id, report.model_dump(mode="json")))


@mcp.tool(title="Submit editorial audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_editorial_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> WritingTaskSummary:
    """Record the independent semantic editorial verdict. PASS requires a passed style gate; REVISE may target TITLE or DRAFT and invalidates stale downstream checks."""
    return _summary(impl.submit_editorial_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Submit publication visuals", annotations=FILE_INGEST_TOOL, meta={"openai/fileParams": ["files"]}, structured_output=True)
def submit_visual_package(task_id: Annotated[str, Field(min_length=1)], visual_package: VisualPackage, files: Annotated[list[OpenAIFileRef], Field(min_length=1, description="ChatGPT-authorized generated/uploaded image file parameters referenced by file_id.")]) -> WritingTaskSummary:
    """Accept authorized image file parameters at DELIVERY, validate mode/count/ratio/avatar requirements, safely copy bytes into task storage and record the visual gate."""
    return _summary(impl.submit_visual_package(task_id, visual_package.model_dump(mode="json"), files))


@mcp.tool(title="Build and mechanically audit delivery", annotations=STATE_WRITE_TOOL, structured_output=True)
def build_and_mechanically_audit_delivery(task_id: Annotated[str, Field(min_length=1)]) -> Annotated[CallToolResult, WritingTaskSummary]:
    """Build required publication artifacts, run deterministic Word/render checks, and return both final-artifact links and page-render resources for visual inspection."""
    return _result_with_artifacts(_summary(impl.build_and_mechanically_audit_delivery(task_id)))


@mcp.tool(title="Record knowledge writeback outcome", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_knowledge_writeback(task_id: Annotated[str, Field(min_length=1)], status: Literal["PASS", "N_A"], refs: Annotated[list[str] | None, Field(description="Actual durable-store receipt references when writeback succeeded.")] = None, notes: Annotated[list[str] | None, Field(description="Reason/boundary notes; required by the runtime for N_A.")] = None) -> WritingTaskSummary:
    """Record the explicit durable-knowledge writeback decision at FINAL_AUDIT. PASS needs real receipts; N_A needs an explicit reason; core writing can continue without an external store."""
    return _summary(impl.record_knowledge_writeback(task_id, status, refs, notes))


@mcp.tool(title="Submit final audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_final_audit(task_id: Annotated[str, Field(min_length=1)], decision: FinalAuditDecision) -> Annotated[CallToolResult, WritingTaskSummary]:
    """Record the final red-team verdict. PASS requires criterion-keyed acceptance evidence, explicit knowledge-sync status and an exact list of every rendered page actually inspected."""
    return _result_with_artifacts(_summary(impl.submit_final_audit(task_id, decision.model_dump(mode="json"))))


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    mcp.run(transport="streamable-http", host=host, port=port, streamable_http_path="/mcp", stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
