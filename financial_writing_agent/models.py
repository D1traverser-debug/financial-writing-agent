from __future__ import annotations

from datetime import datetime, timezone
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


class DeliveryChannel(str, Enum):
    WORD_FILE_ONLY = "WORD_FILE_ONLY"


class GateStatus(str, Enum):
    NOT_RUN = "NOT_RUN"
    PASS = "PASS"
    REVISE = "REVISE"
    FAIL = "FAIL"
    N_A = "N_A"


class ArtifactKind(str, Enum):
    FINANCE_DEEP_DOCX = "FINANCE_DEEP_DOCX"
    FINANCE_BROAD_DOCX = "FINANCE_BROAD_DOCX"
    AUDIT_DOCX = "AUDIT_DOCX"


SEMANTIC_GATE_STAGES: dict[str, Stage] = {
    "research_audit": Stage.RESEARCH_AUDIT,
    "hook_audit": Stage.EDITORIAL_AUDIT,
    "style_audit": Stage.EDITORIAL_AUDIT,
    "editorial_audit": Stage.EDITORIAL_AUDIT,
    "final_audit": Stage.FINAL_AUDIT,
}


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
    source_refs: list[str] = Field(default_factory=list)
    target_platforms: list[str] = Field(default_factory=list)
    distribution_mode: DistributionMode = DistributionMode.DUAL
    content_mode: ContentMode = ContentMode.FORMAL_ARTICLE
    delivery_channel: DeliveryChannel = DeliveryChannel.WORD_FILE_ONLY
    required_outputs: list[ArtifactKind] = Field(default_factory=list)
    run_constraints: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def populate_required_outputs(self):
        if self.required_outputs:
            return self
        required = [ArtifactKind.AUDIT_DOCX]
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
    gates: dict[str, GateRecord] = Field(default_factory=dict)
    artifacts: dict[ArtifactKind, Artifact] = Field(default_factory=dict)
    working: dict[str, Any] = Field(default_factory=dict)
    trace: list[TraceEvent] = Field(default_factory=list)
    attempts: dict[str, int] = Field(default_factory=dict)
    blocked_reason: str | None = None
    blocked_from_stage: Stage | None = None
    blocked_resume_stage: Stage | None = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def add_trace(self, event: str, detail: str = "") -> None:
        self.trace.append(TraceEvent(seq=len(self.trace) + 1, stage=self.stage, event=event, detail=detail))
        self.updated_at = datetime.now(timezone.utc)

    def _current_stage_runtime_execution_observed(self, stage: Stage) -> bool:
        last_enter = -1
        for i, event in enumerate(self.trace):
            if event.event == "STAGE_ENTER" and event.stage == stage:
                last_enter = i
        if last_enter < 0:
            return False
        started = False
        for event in self.trace[last_enter + 1 :]:
            if event.stage != stage:
                continue
            if event.event == "EXECUTOR_START":
                started = True
            elif event.event == "EXECUTOR_END" and started:
                return True
        return False

    def semantic_gate_proof_valid(self, name: str) -> bool:
        expected_stage = SEMANTIC_GATE_STAGES.get(name)
        gate = self.gates.get(name)
        if expected_stage is None or gate is None or gate.status != GateStatus.PASS:
            return False
        payload = self.working.get(name)
        if not isinstance(payload, dict):
            return False
        provenance = payload.get("provenance")
        if not isinstance(provenance, dict):
            return False
        execution_ref = str(provenance.get("execution_ref", "")).strip()
        reviewer = str(provenance.get("reviewer_identity", "")).strip()
        author = str(provenance.get("author_identity", "")).strip()
        assurance = str(provenance.get("assurance", "")).strip()
        if assurance != "INDEPENDENT_EXECUTOR" or not execution_ref or not reviewer or reviewer == author:
            return False
        expected_prefix = f"{self.contract.task_id}:{expected_stage.value}:"
        if not execution_ref.startswith(expected_prefix):
            return False
        return self._current_stage_runtime_execution_observed(expected_stage)

    def set_gate(self, name: str, status: GateStatus, evidence: list[str] | None = None, notes: str = "") -> None:
        self.gates[name] = GateRecord(name=name, status=status, evidence=evidence or [], notes=notes)
        if status == GateStatus.NOT_RUN:
            self.working.pop(name, None)
        self.updated_at = datetime.now(timezone.utc)

    def add_artifact(self, kind: ArtifactKind, path: str) -> None:
        self.artifacts[kind] = Artifact(kind=kind, path=path, exists=Path(path).exists())
        self.updated_at = datetime.now(timezone.utc)
