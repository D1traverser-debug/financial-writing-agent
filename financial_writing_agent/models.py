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


SEMANTIC_PASS_GATES = frozenset({
    "research_audit",
    "hook_audit",
    "style_audit",
    "editorial_audit",
    "final_audit",
})
SEMANTIC_EXECUTION_RECEIPTS_KEY = "_semantic_execution_receipts"


class GateRecord(BaseModel):
    name: str
    status: GateStatus = GateStatus.NOT_RUN
    evidence: list[str] = Field(default_factory=list)
    notes: str = ""
    execution_proof_ref: str | None = None
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

    def semantic_execution_proof_valid(self, execution_proof_ref: str | None) -> bool:
        if not execution_proof_ref:
            return False
        receipts = self.working.get(SEMANTIC_EXECUTION_RECEIPTS_KEY)
        if not isinstance(receipts, dict):
            return False
        receipt = receipts.get(execution_proof_ref)
        if not isinstance(receipt, dict):
            return False
        return (
            receipt.get("execution_ref") == execution_proof_ref
            and receipt.get("task_id") == self.contract.task_id
            and receipt.get("stage") == self.stage.value
            and receipt.get("status") == "OWNER_RUNTIME_EXECUTED"
            and receipt.get("assurance") == "STAGE_SEPARATED_OWNER_RUNTIME"
        )

    def semantic_gate_proof_valid(self, name: str) -> bool:
        gate = self.gates.get(name)
        if gate is None or gate.status != GateStatus.PASS:
            return False
        proof_ref = gate.execution_proof_ref
        if not proof_ref:
            return False
        receipts = self.working.get(SEMANTIC_EXECUTION_RECEIPTS_KEY)
        if not isinstance(receipts, dict):
            return False
        receipt = receipts.get(proof_ref)
        if not isinstance(receipt, dict):
            return False
        return (
            receipt.get("execution_ref") == proof_ref
            and receipt.get("task_id") == self.contract.task_id
            and receipt.get("status") == "OWNER_RUNTIME_EXECUTED"
            and receipt.get("assurance") == "STAGE_SEPARATED_OWNER_RUNTIME"
            and receipt.get("gate_name") == name
        )

    def set_gate(
        self,
        name: str,
        status: GateStatus,
        evidence: list[str] | None = None,
        notes: str = "",
        *,
        execution_proof_ref: str | None = None,
    ) -> None:
        if name in SEMANTIC_PASS_GATES and status == GateStatus.PASS:
            if not self.semantic_execution_proof_valid(execution_proof_ref):
                raise ValueError(f"semantic gate {name} PASS requires a current owner-runtime execution proof")
            receipt = self.working[SEMANTIC_EXECUTION_RECEIPTS_KEY][execution_proof_ref]
            if receipt.get("gate_name") != name:
                raise ValueError(
                    f"semantic gate proof mismatch: proof={receipt.get('gate_name')} gate={name}"
                )
        self.gates[name] = GateRecord(
            name=name,
            status=status,
            evidence=evidence or [],
            notes=notes,
            execution_proof_ref=execution_proof_ref,
        )
        self.updated_at = datetime.now(timezone.utc)

    def add_artifact(self, kind: ArtifactKind, path: str) -> None:
        self.artifacts[kind] = Artifact(kind=kind, path=path, exists=Path(path).exists())
        self.updated_at = datetime.now(timezone.utc)
