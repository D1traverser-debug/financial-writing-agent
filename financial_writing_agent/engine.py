from __future__ import annotations

from .models import ArtifactKind, GateStatus, Stage, TaskContract, WritingState
from .store import SQLiteStateStore


class WorkflowError(RuntimeError):
    pass


ALLOWED_TRANSITIONS: dict[Stage, set[Stage]] = {
    Stage.INTAKE: {Stage.RESEARCH, Stage.BLOCKED},
    Stage.RESEARCH: {Stage.RESEARCH_AUDIT, Stage.BLOCKED},
    Stage.RESEARCH_AUDIT: {Stage.RESEARCH, Stage.EDITORIAL, Stage.BLOCKED},
    Stage.EDITORIAL: {Stage.TITLE, Stage.BLOCKED},
    Stage.TITLE: {Stage.TITLE, Stage.DRAFT, Stage.BLOCKED},
    Stage.DRAFT: {Stage.EDITORIAL_AUDIT, Stage.BLOCKED},
    Stage.EDITORIAL_AUDIT: {Stage.TITLE, Stage.DRAFT, Stage.DELIVERY, Stage.BLOCKED},
    Stage.DELIVERY: {Stage.MECHANICAL_AUDIT, Stage.BLOCKED},
    Stage.MECHANICAL_AUDIT: {Stage.DELIVERY, Stage.FINAL_AUDIT, Stage.BLOCKED},
    Stage.FINAL_AUDIT: {Stage.EDITORIAL, Stage.DELIVERY, Stage.COMPLETE, Stage.BLOCKED},
    Stage.COMPLETE: set(),
    Stage.BLOCKED: {Stage.INTAKE, Stage.RESEARCH, Stage.EDITORIAL, Stage.DELIVERY, Stage.FINAL_AUDIT},
}


class WritingEngine:
    def __init__(self, store: SQLiteStateStore):
        self.store = store

    def start(self, contract: TaskContract) -> WritingState:
        state = WritingState(contract=contract)
        state.add_trace("RUNTIME_STARTED", "TaskContract initialized before source retrieval or drafting")
        state.set_gate("runtime_initialized", GateStatus.PASS, ["TaskContract exists", "State store active"])
        state.set_gate("knowledge_sync", GateStatus.NOT_RUN, [], "Explicit PASS/N_A writeback decision required before final completion")
        self.store.save(state)
        return state

    def transition(self, state: WritingState, next_stage: Stage, *, reason: str = "") -> WritingState:
        if next_stage not in ALLOWED_TRANSITIONS[state.stage]:
            raise WorkflowError(f"Illegal transition: {state.stage} -> {next_stage}")
        state.add_trace("STAGE_EXIT", reason)
        state.stage = next_stage
        state.add_trace("STAGE_ENTER", reason)
        self.store.save(state)
        return state

    def block(self, state: WritingState, reason: str) -> WritingState:
        state.blocked_reason = reason
        if state.stage != Stage.BLOCKED:
            self.transition(state, Stage.BLOCKED, reason=reason)
        self.store.save(state)
        return state

    def record_gate(self, state: WritingState, name: str, status: GateStatus, evidence: list[str], notes: str = "") -> None:
        state.set_gate(name, status, evidence, notes)
        state.add_trace("GATE", f"{name}={status}")
        self.store.save(state)

    def increment_attempt(self, state: WritingState, key: str) -> int:
        state.attempts[key] = state.attempts.get(key, 0) + 1
        self.store.save(state)
        return state.attempts[key]

    def assert_can_complete(self, state: WritingState) -> None:
        failed = [name for name, gate in state.gates.items() if gate.status in {GateStatus.FAIL, GateStatus.REVISE, GateStatus.NOT_RUN}]
        if failed:
            raise WorkflowError(f"Unresolved gates: {failed}")
        missing: list[ArtifactKind] = []
        for kind in state.contract.required_outputs:
            artifact = state.artifacts.get(kind)
            if not artifact or not artifact.exists:
                missing.append(kind)
        if missing:
            raise WorkflowError(f"Missing required outputs: {missing}")
        if state.stage != Stage.FINAL_AUDIT:
            raise WorkflowError("Completion is only legal from FINAL_AUDIT")

    def complete(self, state: WritingState) -> WritingState:
        self.assert_can_complete(state)
        return self.transition(state, Stage.COMPLETE, reason="All applicable gates and required outputs passed")
