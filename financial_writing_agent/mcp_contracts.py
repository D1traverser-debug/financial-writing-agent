from __future__ import annotations

from datetime import datetime
from typing import Literal

from mcp.types import ToolAnnotations
from pydantic import BaseModel, ConfigDict, Field


GateStatusText = Literal["NOT_RUN", "PASS", "REVISE", "FAIL", "N_A"]
TaskStatusText = Literal["IN_PROGRESS", "BLOCKED", "COMPLETE"]
StageText = Literal[
    "INTAKE", "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT",
    "EDITORIAL_AUDIT", "DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT", "COMPLETE", "BLOCKED",
]
ContentModeText = Literal["FORMAL_ARTICLE", "WECHAT_STICKER_POST"]
DistributionModeText = Literal["FINANCE_DEEP", "FINANCE_BROAD", "DUAL"]
DeliveryChannelText = Literal["WORD_FILE_ONLY", "CHAT_TEXT"]


class PublicResultModel(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


READ_ONLY_TOOL = ToolAnnotations(
    read_only_hint=True,
    destructive_hint=False,
    open_world_hint=False,
    idempotent_hint=True,
)

STATE_WRITE_TOOL = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    open_world_hint=False,
    idempotent_hint=False,
)

FILE_INGEST_TOOL = ToolAnnotations(
    read_only_hint=False,
    destructive_hint=False,
    open_world_hint=False,
    idempotent_hint=False,
)


class GateSummary(PublicResultModel):
    status: GateStatusText
    evidence: list[str] = Field(default_factory=list)
    notes: str = ""


class ArtifactSummary(PublicResultModel):
    file_name: str
    exists: bool
    sha256: str | None = None
    resource_uri: str
    mime_type: str


class StyleChecklist(PublicResultModel):
    editorial: GateStatusText
    anti_ai_style: GateStatusText


class KnowledgeChecklist(PublicResultModel):
    context_gate: GateStatusText
    sync_gate: GateStatusText
    reused_refs: int = Field(ge=0)
    writeback_candidates: int = Field(ge=0)
    writeback_receipts: int = Field(ge=0)


class CompletionChecklist(PublicResultModel):
    runtime_gates: Literal["PASS", "INCOMPLETE"]
    research_evidence: GateStatusText
    structure_style_continuity: StyleChecklist
    word_render: GateStatusText
    compliance_risk: GateStatusText
    visuals: GateStatusText
    knowledge: KnowledgeChecklist


class WritingTaskSummary(PublicResultModel):
    task_id: str
    status: TaskStatusText
    current_stage: StageText
    topic: str | None = None
    prompt_preview: str
    content_mode: ContentModeText
    distribution_mode: DistributionModeText
    delivery_channel: DeliveryChannelText
    visuals_enabled: bool
    required_outputs: list[str]
    gate_status: dict[str, GateStatusText] = Field(default_factory=dict)
    blocked_reason: str | None = None
    updated_at: datetime
    next_action: str
    source_refs: list[str] | None = None
    visual_profile_ref: str | None = None
    gates: dict[str, GateSummary] | None = None
    artifacts: dict[str, ArtifactSummary] | None = None
    render_pages: dict[str, list[str]] | None = None
    completion_checklist: CompletionChecklist | None = None


class WritingTaskList(PublicResultModel):
    tasks: list[WritingTaskSummary]
