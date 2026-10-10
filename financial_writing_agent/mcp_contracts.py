from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from mcp.types import ToolAnnotations
from pydantic import BaseModel, ConfigDict, Field


GateStatusText = Literal["NOT_RUN", "PASS", "REVISE", "FAIL", "N_A"]
TaskStatusText = Literal["IN_PROGRESS", "BLOCKED", "COMPLETE"]
StageText = Literal[
    "INTAKE", "RESEARCH", "RESEARCH_AUDIT", "EDITORIAL", "TITLE", "DRAFT",
    "EDITORIAL_AUDIT", "DELIVERY", "MECHANICAL_AUDIT", "FINAL_AUDIT", "COMPLETE", "BLOCKED",
]
ContentModeText = Literal["FORMAL_ARTICLE"]
DistributionModeText = Literal["FINANCE_DEEP", "FINANCE_BROAD", "DUAL"]
DeliveryChannelText = Literal["WORD_FILE_ONLY"]
LearningSampleType = Literal[
    "USER_EDIT",
    "USER_FEEDBACK",
    "USER_ACCEPTANCE",
    "USER_REJECTION",
    "POST_PUBLICATION_PERFORMANCE",
]
MethodologyHookStatusText = Literal["INVOKED", "NOT_APPLICABLE_FOR_ACTION"]
MethodologyReceiptVerificationText = Literal["UNVERIFIED_OWNER_RECEIPT"]


class PublicResultModel(BaseModel):
    model_config = ConfigDict(extra="ignore", str_strip_whitespace=True)


READ_ONLY_TOOL = ToolAnnotations(read_only_hint=True, destructive_hint=False, open_world_hint=False, idempotent_hint=True)
STATE_WRITE_TOOL = ToolAnnotations(read_only_hint=False, destructive_hint=False, open_world_hint=False, idempotent_hint=False)


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


class LearningSampleSummary(PublicResultModel):
    sample_type: LearningSampleType
    summary: str
    source_refs: list[str] = Field(default_factory=list)
    original_excerpt: str = ""
    revised_excerpt: str = ""
    metrics: dict[str, str | int | float] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
    recorded_stage: StageText
    recorded_at: datetime
    promotion_status: Literal["RAW_EVIDENCE_ONLY"] = "RAW_EVIDENCE_ONLY"


class MethodologyHookAssessmentSummary(PublicResultModel):
    status: MethodologyHookStatusText
    reason: str
    evidence_refs: list[str] = Field(default_factory=list)


class MethodologyProfileRunSummary(PublicResultModel):
    receipt_contract_version: Literal["1.2"]
    profile_id: Literal["artifact_io", "operational_hygiene", "evolution"]
    profile_version: Literal["1.0"]
    activation_id: str
    trigger: str
    invoked_hooks: list[str] = Field(default_factory=list)
    hook_assessments: dict[str, MethodologyHookAssessmentSummary] = Field(default_factory=dict)
    evidence_refs: list[str] = Field(default_factory=list)
    verification_status: MethodologyReceiptVerificationText


class EditorialChecklist(PublicResultModel):
    general_editorial: GateStatusText
    reader_funnel: GateStatusText
    authorial_prose: GateStatusText


class KnowledgeChecklist(PublicResultModel):
    sync_gate: GateStatusText
    reused_refs: int = Field(ge=0)
    writeback_candidates: int = Field(ge=0)
    writeback_receipts: int = Field(ge=0)


class CompletionChecklist(PublicResultModel):
    runtime_gates: Literal["PASS", "INCOMPLETE"]
    research_evidence: GateStatusText
    editorial: EditorialChecklist
    bold_skim_path: GateStatusText
    word_render: GateStatusText
    compliance_risk: GateStatusText
    writing_dna_evidence_samples: int = Field(ge=0)
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
    required_outputs: list[str]
    gate_status: dict[str, GateStatusText] = Field(default_factory=dict)
    blocked_reason: str | None = None
    blocked_resume_stage: StageText | None = None
    learning_sample_count: int = Field(ge=0)
    updated_at: datetime
    next_action: str
    source_refs: list[str] | None = None
    gates: dict[str, GateSummary] | None = None
    artifacts: dict[str, ArtifactSummary] | None = None
    learning_samples: list[LearningSampleSummary] | None = None
    methodology_profile_runs: list[MethodologyProfileRunSummary] | None = None
    completion_checklist: CompletionChecklist | None = None


class WritingTaskList(PublicResultModel):
    tasks: list[WritingTaskSummary]
