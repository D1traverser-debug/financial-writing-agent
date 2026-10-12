from __future__ import annotations

from .models import ArtifactKind, GateStatus, SEMANTIC_GATE_STAGES, Stage, TaskContract, WritingState
from .store import SQLiteStateStore
from .system_impact import pending_system_impact_reviews
from .workflow_spec import LEGAL_TRANSITIONS, RECOVERABLE_STAGES


class WorkflowError(RuntimeError):
    pass


# Backward-compatible public names now derive from the canonical workflow spec.
# Keep them read-only by convention; adapters must not redefine their own broader graph.
ALLOWED_TRANSITIONS: dict[Stage, set[Stage]] = {
    stage: set(targets) for stage, targets in LEGAL_TRANSITIONS.items()
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
        if next_stage not in LEGAL_TRANSITIONS[state.stage]:
            raise WorkflowError(f"Illegal transition: {state.stage} -> {next_stage}")
        state.add_trace("STAGE_EXIT", reason)
        state.stage = next_stage
        state.add_trace("STAGE_ENTER", reason)
        self.store.save(state)
        return state

    def block(self, state: WritingState, reason: str, *, resume_stage: Stage | None = None) -> WritingState:
        if state.stage == Stage.COMPLETE:
            raise WorkflowError("completed tasks cannot be blocked")
        if state.stage == Stage.BLOCKED:
            state.blocked_reason = reason
            if resume_stage is not None:
                if resume_stage not in RECOVERABLE_STAGES:
                    raise WorkflowError(f"invalid blocked resume stage: {resume_stage}")
                state.blocked_resume_stage = resume_stage
            self.store.save(state)
            return state

        origin = state.stage
        cursor = resume_stage or origin
        if cursor not in RECOVERABLE_STAGES:
            raise WorkflowError(f"invalid blocked resume stage: {cursor}")
        state.blocked_reason = reason
        state.blocked_from_stage = origin
        state.blocked_resume_stage = cursor
        self.transition(state, Stage.BLOCKED, reason=reason)
        self.store.save(state)
        return state

    def resume_blocked(self, state: WritingState, *, target_stage: Stage | None = None) -> WritingState:
        if state.stage != Stage.BLOCKED:
            raise WorkflowError("resume_blocked is only legal for BLOCKED tasks")
        target = target_stage or state.blocked_resume_stage
        if target is None or target not in RECOVERABLE_STAGES:
            raise WorkflowError("BLOCKED task has no valid recovery cursor")
        prior_reason = state.blocked_reason or "unspecified blocker"
        state.add_trace("RUNTIME_UNBLOCKED", f"resume={target.value}; prior_reason={prior_reason}")
        state.blocked_reason = None
        state.blocked_from_stage = None
        state.blocked_resume_stage = None
        return self.transition(state, target, reason=f"blocker repaired; resume {target.value}")

    def record_gate(self, state: WritingState, name: str, status: GateStatus, evidence: list[str], notes: str = "") -> None:
        state.set_gate(name, status, evidence, notes)
        state.add_trace("GATE", f"{name}={status}")
        self.store.save(state)

    def increment_attempt(self, state: WritingState, key: str) -> int:
        state.attempts[key] = state.attempts.get(key, 0) + 1
        self.store.save(state)
        return state.attempts[key]

    def assert_can_complete(self, state: WritingState) -> None:
        pending_impact = pending_system_impact_reviews(state)
        if pending_impact:
            ids = [item["signal_id"] for item in pending_impact]
            raise WorkflowError(f"Pending material-feedback system-impact review(s): {ids}")
        failed = [name for name, gate in state.gates.items() if gate.status in {GateStatus.FAIL, GateStatus.REVISE, GateStatus.NOT_RUN}]
        if failed:
            raise WorkflowError(f"Unresolved gates: {failed}")
        missing_semantic_proof = [
            name
            for name in SEMANTIC_GATE_STAGES
            if state.gates.get(name) is not None
            and state.gates[name].status == GateStatus.PASS
            and not state.semantic_gate_proof_valid(name)
        ]
        if missing_semantic_proof:
            raise WorkflowError(f"Semantic PASS lacks current owner-runtime proof: {missing_semantic_proof}")
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
