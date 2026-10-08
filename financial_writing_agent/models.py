from __future__ import annotations

from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class Stage(str, Enum):
    INTAKE = "INTAKE"
    RESEARCH = "RESEARCH"
    RESEARCH_AUDIT = "RESEARCH_AUDIT"
    EDITORIAL = "EDITORIAL"
    TITLE = "TITLE"
    DRAFT = "DRAFT"
    BROAD_DERIVATION = "BROAD_DERIVATION"
    EDITORIAL_AUDIT = "EDITORIAL_AUDIT"
    DELIVERY = "DELIVERY"
    MECHANICAL_AUDIT = "MECHANICAL_AUDIT"
    FINAL_AUDIT = "FINAL_AUDIT"
    COMPLETE = "COMPLETE"
    BLOCKED = "BLOCKED"


class DistributionMode(str, Enum):
    FINANCE_DEEP = "FINANCE_DEEP"
    FINANCE_BROAD = "FINANCE_BROAD"
    DUAL = "DUAL"


class ContentMode(str, Enum):
    FORMAL_ARTICLE = "FORMAL_ARTICLE"
    WECHAT_STICKER_POST = "WECHAT_STICKER_POST"


class DeliveryChannel(str, Enum):
    WORD_FILE_ONLY = "WORD_FILE_ONLY"
    CHAT_TEXT = "CHAT_TEXT"
    WORD_AND_CHAT = "WORD_AND_CHAT"


class GateStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    PASS = "PASS"
    REVISE = "REVISE"
    FAIL = "FAIL"
    N_A = "N_A"


class ArtifactKind(str, Enum):
    FINANCE_DEEP_DOCX = "FINANCE_DEEP_DOCX"
    FINANCE_BROAD_DOCX = "FINANCE_BROAD_DOCX"
    WECHAT_STICKER_DOCX = "WECHAT_STICKER_DOCX"
    AUDIT_DOCX = "AUDIT_DOCX"
    VISUAL_MANIFEST_JSON = "VISUAL_MANIFEST_JSON"
    CHAT_TEXT = "CHAT_TEXT"


class GateRecord(BaseModel):
    name: str
    status: GateStatus = GateStatus.NOT_RUN
    evidence: list[str] = Field(default_factory=list)
    notes: str = ""
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Artifact(BaseModel):
    kind: ArtifactKind
    path: str
    exists: bool = False
    sha256: str | None = None


class TaskContract(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid4()))
    prompt: str
    effective_time_boundary: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_refs: list[str] = Field(default_factory=list)
    target_platforms: list[str] = Field(default_factory=list)
    distribution_mode: DistributionMode = DistributionMode.DUAL
    content_mode: ContentMode = ContentMode.FORMAL_ARTICLE
    delivery_channel: DeliveryChannel = DeliveryChannel.WORD_FILE_ONLY
    visuals_enabled: bool = False
    visual_profile_ref: str | None = None
    required_outputs: list[ArtifactKind] = Field(default_factory=list)
    run_constraints: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_contract(self):
        boundary = self.effective_time_boundary
        if boundary.tzinfo is None:
            raise ValueError("effective_time_boundary must include a timezone")
        if boundary.astimezone(timezone.utc) > datetime.now(timezone.utc) + timedelta(minutes=5):
            raise ValueError("effective_time_boundary cannot be materially in the future")

        if self.required_outputs:
            return self
        if self.delivery_channel == DeliveryChannel.CHAT_TEXT:
            self.required_outputs = [ArtifactKind.CHAT_TEXT]
            return self
        required = [ArtifactKind.AUDIT_DOCX]
        if self.delivery_channel == DeliveryChannel.WORD_AND_CHAT:
            required.append(ArtifactKind.CHAT_TEXT)
        if self.visuals_enabled:
            required.append(ArtifactKind.VISUAL_MANIFEST_JSON)
        if self.content_mode == ContentMode.WECHAT_STICKER_POST:
            required.append(ArtifactKind.WECHAT_STICKER_DOCX)
            self.required_outputs = required
            return self
        if self.distribution_mode in (DistributionMode.FINANCE_DEEP, DistributionMode.DUAL):
            required.append(ArtifactKind.FINANCE_DEEP_DOCX)
        if self.distribution_mode in (DistributionMode.FINANCE_BROAD, DistributionMode.DUAL):
            required.append(ArtifactKind.FINANCE_BROAD_DOCX)
        self.required_outputs = required
        return self


class TraceEvent(BaseModel):
    seq: int
    stage: Stage
    event: str
    detail: str = ""
    at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WritingState(BaseModel):
    contract: TaskContract
    stage: Stage = Stage.INTAKE
    checkpoint_version: int = Field(default=0, ge=0)
    gates: dict[str, GateRecord] = Field(default_factory=dict)
    artifacts: dict[ArtifactKind, Artifact] = Field(default_factory=dict)
    working: dict[str, Any] = Field(default_factory=dict)
    trace: list[TraceEvent] = Field(default_factory=list)
    attempts: dict[str, int] = Field(default_factory=dict)
    blocked_reason: str | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def add_trace(self, event: str, detail: str = "") -> None:
        self.trace.append(TraceEvent(seq=len(self.trace) + 1, stage=self.stage, event=event, detail=detail))
        self.updated_at = datetime.now(timezone.utc)

    def set_gate(self, name: str, status: GateStatus, evidence: list[str] | None = None, notes: str = "") -> None:
        self.gates[name] = GateRecord(name=name, status=status, evidence=evidence or [], notes=notes)
        self.updated_at = datetime.now(timezone.utc)

    def add_artifact(self, kind: ArtifactKind, path: str) -> None:
        self.artifacts[kind] = Artifact(kind=kind, path=path, exists=Path(path).exists())
        self.updated_at = datetime.now(timezone.utc)
