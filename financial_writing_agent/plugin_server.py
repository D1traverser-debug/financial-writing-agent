from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated, Literal

from mcp.server.mcpserver import MCPServer
from mcp.types import CallToolResult, ResourceLink, TextContent
from pydantic import Field

from . import runtime_service as impl
from .mcp_contracts import READ_ONLY_TOOL, STATE_WRITE_TOOL, WritingTaskList, WritingTaskSummary
from .models import ArtifactKind
from .schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, HookAuditDecision, ResearchPackage, StyleAuditDecision

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
TEXT_MIME = "text/plain; charset=utf-8"


def _artifact_public_fields(kind: str, path_value: str) -> dict[str, str]:
    file_name = Path(path_value).name
    if kind in {ArtifactKind.FINANCE_DEEP_DOCX.value, ArtifactKind.FINANCE_BROAD_DOCX.value, ArtifactKind.AUDIT_DOCX.value}:
        return {"file_name": file_name, "resource_uri": f"writing-docx://artifact/{kind}", "mime_type": DOCX_MIME}
    return {"file_name": file_name, "resource_uri": f"writing-text://artifact/{kind}", "mime_type": TEXT_MIME}


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
    if not path.is_relative_to(runs_root) or not path.is_file():
        raise FileNotFoundError(f"artifact file missing or outside task storage: {kind}")
    return path.read_bytes()


def _result_with_artifacts(summary: WritingTaskSummary) -> CallToolResult:
    content = [TextContent(type="text", text=f"Writing task {summary.task_id} is {summary.status} at {summary.current_stage}. {summary.next_action}")]
    for kind, artifact in (summary.artifacts or {}).items():
        if artifact.exists:
            content.append(ResourceLink(type="resource_link", uri=artifact.resource_uri, name=artifact.file_name, mime_type=artifact.mime_type, description=f"{kind} publication artifact for writing task {summary.task_id}"))
    return CallToolResult(content=content, structured_content=summary.model_dump(mode="json"))


mcp = MCPServer(
    "Financial Writing Agent",
    instructions=(
        "Use this server only for publishable A-share financial writing and continuation. "
        "Resume unfinished tasks before starting new ones. Start runtime state before research. "
        "Follow returned next_action and never skip a gate. Financial Writing is Word-only and has no image workflow. "
        "The model owns research, writing and semantic audits; the runtime owns state, schemas, legal transitions, Word construction and mechanical QA."
    ),
)


@mcp.resource("writing-docx://{task_id}/{kind}", mime_type=DOCX_MIME)
def read_docx_artifact(task_id: str, kind: str) -> bytes:
    """Read one completed Word artifact belonging to a persisted writing task."""
    return _resource_bytes(task_id, kind, {ArtifactKind.FINANCE_DEEP_DOCX, ArtifactKind.FINANCE_BROAD_DOCX, ArtifactKind.AUDIT_DOCX})


@mcp.resource("writing-text://{task_id}/{kind}", mime_type=TEXT_MIME)
def read_text_artifact(task_id: str, kind: str) -> bytes:
    """Read one legacy plain-text artifact from an older persisted task."""
    return _resource_bytes(task_id, kind, {ArtifactKind.CHAT_TEXT})


@mcp.tool(title="Start financial writing task", annotations=STATE_WRITE_TOOL, structured_output=True)
def start_writing_task(
    prompt: Annotated[str, Field(min_length=1, description="The user's concrete publishable financial-writing request.")],
    source_refs: Annotated[list[str] | None, Field(description="Explicit source URLs or references supplied for this task.")] = None,
    target_platforms: Annotated[list[str] | None, Field(description="Explicit destination platforms; omit to use the formal default routing.")] = None,
) -> WritingTaskSummary:
    """Create a new persisted Word-only financial-writing workflow after ruling out a relevant unfinished task."""
    return _summary(impl.start_writing_task(prompt=prompt, source_refs=source_refs, target_platforms=target_platforms))


@mcp.tool(title="Get writing task", annotations=READ_ONLY_TOOL, structured_output=True)
def get_writing_task(task_id: Annotated[str, Field(min_length=1)], detail: Annotated[bool, Field(description="Return gates and publication artifact resources when true.")] = True) -> WritingTaskSummary:
    return _summary(impl.get_writing_task(task_id, detail=detail))


@mcp.tool(title="List recent writing tasks", annotations=READ_ONLY_TOOL, structured_output=True)
def list_recent_writing_tasks(limit: Annotated[int, Field(ge=1, le=50)] = 10, include_complete: bool = False) -> WritingTaskList:
    return WritingTaskList(tasks=[_summary(item) for item in impl.list_recent_writing_tasks(limit=limit, include_complete=include_complete)])


@mcp.tool(title="Record retrieved knowledge context", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_knowledge_context(task_id: Annotated[str, Field(min_length=1)], refs: Annotated[list[str], Field(min_length=1)], notes: list[str] | None = None) -> WritingTaskSummary:
    return _summary(impl.record_knowledge_context(task_id, refs, notes))


@mcp.tool(title="Submit research package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_research(task_id: Annotated[str, Field(min_length=1)], research: ResearchPackage) -> WritingTaskSummary:
    return _summary(impl.submit_research(task_id, research.model_dump(mode="json")))


@mcp.tool(title="Submit research audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_research_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> WritingTaskSummary:
    return _summary(impl.submit_research_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Submit editorial plan", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_editorial_plan(task_id: Annotated[str, Field(min_length=1)], editorial_plan: EditorialPlan) -> WritingTaskSummary:
    """Validate shared TopicDNA plus independent deep/broad mode contracts."""
    return _summary(impl.submit_editorial_plan(task_id, editorial_plan.model_dump(mode="json")))


@mcp.tool(title="Submit headline package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_headlines(task_id: Annotated[str, Field(min_length=1)], headlines: HeadlinePackage) -> WritingTaskSummary:
    """Validate headline candidates, cross-finance click reasons, current WeChat search terms/evidence and selected-title membership."""
    return _summary(impl.submit_headlines(task_id, headlines.model_dump(mode="json")))


@mcp.tool(title="Submit draft package", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_draft(task_id: Annotated[str, Field(min_length=1)], draft: DraftPackage) -> WritingTaskSummary:
    """Validate all contract-required drafts including explicit bold skim-path anchors."""
    return _summary(impl.submit_draft(task_id, draft.model_dump(mode="json")))


@mcp.tool(title="Submit hook audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_hook_audit(task_id: Annotated[str, Field(min_length=1)], report: HookAuditDecision) -> WritingTaskSummary:
    """Record independent title/first-three-sentences/H1/transition hook audit. Must PASS before general editorial PASS."""
    return _summary(impl.submit_hook_audit(task_id, report.model_dump(mode="json")))


@mcp.tool(title="Submit human voice audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_style_audit(task_id: Annotated[str, Field(min_length=1)], report: StyleAuditDecision) -> WritingTaskSummary:
    """Record independent anti-AI/human-voice audit. Must PASS before general editorial PASS."""
    return _summary(impl.submit_style_audit(task_id, report.model_dump(mode="json")))


@mcp.tool(title="Submit editorial audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_editorial_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> WritingTaskSummary:
    """Record general semantic editorial verdict after Hook Gate and Human Voice Gate pass."""
    return _summary(impl.submit_editorial_audit(task_id, decision.model_dump(mode="json")))


@mcp.tool(title="Build and mechanically audit delivery", annotations=STATE_WRITE_TOOL, structured_output=True)
def build_and_mechanically_audit_delivery(task_id: Annotated[str, Field(min_length=1)]) -> Annotated[CallToolResult, WritingTaskSummary]:
    return _result_with_artifacts(_summary(impl.build_and_mechanically_audit_delivery(task_id)))


@mcp.tool(title="Record knowledge writeback outcome", annotations=STATE_WRITE_TOOL, structured_output=True)
def record_knowledge_writeback(task_id: Annotated[str, Field(min_length=1)], status: Literal["PASS", "N_A"], refs: list[str] | None = None, notes: list[str] | None = None) -> WritingTaskSummary:
    return _summary(impl.record_knowledge_writeback(task_id, status, refs, notes))


@mcp.tool(title="Submit final audit", annotations=STATE_WRITE_TOOL, structured_output=True)
def submit_final_audit(task_id: Annotated[str, Field(min_length=1)], decision: GateDecision) -> Annotated[CallToolResult, WritingTaskSummary]:
    return _result_with_artifacts(_summary(impl.submit_final_audit(task_id, decision.model_dump(mode="json"))))


def main() -> None:
    host = os.getenv("MCP_HOST", "127.0.0.1")
    port = int(os.getenv("PORT", os.getenv("MCP_PORT", "8000")))
    mcp.run(transport="streamable-http", host=host, port=port, streamable_http_path="/mcp", stateless_http=True, json_response=True)


if __name__ == "__main__":
    main()
