from __future__ import annotations

from dataclasses import dataclass, field

from financial_writing_agent.models import GateStatus, Stage, WritingState


@dataclass
class PassExecutor:
    gate: str
    evidence: list[str] = field(default_factory=lambda: ["test evidence"])

    def execute(self, state: WritingState) -> WritingState:
        state.set_gate(self.gate, GateStatus.PASS, self.evidence)
        return state


@dataclass
class SequenceExecutor:
    gate: str
    statuses: list[GateStatus]
    calls: int = 0

    def execute(self, state: WritingState) -> WritingState:
        idx = min(self.calls, len(self.statuses) - 1)
        status = self.statuses[idx]
        self.calls += 1
        state.set_gate(self.gate, status, [f"attempt {self.calls}"])
        return state


class ExplodingExecutor:
    def execute(self, state: WritingState) -> WritingState:
        raise RuntimeError("simulated adapter failure")
