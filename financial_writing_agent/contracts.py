from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from .models import GateStatus, Stage


class StageResult(BaseModel):
    """Structured return value from a high-judgment stage executor."""
    stage: Stage
    status: GateStatus
    payload: dict[str, Any] = Field(default_factory=dict)
    evidence: list[str] = Field(default_factory=list)
    feedback: str = ""
    revise_target: str | None = None


class JudgeResult(BaseModel):
    verdict: Literal["PASS", "REVISE", "FAIL"]
    evidence: list[str] = Field(default_factory=list)
    feedback: str = ""
    revise_target: str | None = None
