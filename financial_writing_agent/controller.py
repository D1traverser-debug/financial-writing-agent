from __future__ import annotations

from .engine import WorkflowError, WritingEngine
from .models import GateStatus, Stage, WritingState


class WorkflowController:
    """Code-owned routing. The model never decides whether a mandatory stage exists."""

    def __init__(self, engine: WritingEngine):
        self.engine = engine

    def advance(self, state: WritingState) -> WritingState:
        s = state.stage
        if s == Stage.INTAKE:
            self._require_pass(state, "runtime_initialized")
            return self.engine.transition(state, Stage.RESEARCH, reason="runtime initialized")

        if s == Stage.RESEARCH:
            self._require_pass(state, "research_output")
            return self.engine.transition(state, Stage.RESEARCH_AUDIT, reason="research package ready")

        if s == Stage.RESEARCH_AUDIT:
            status = self._status(state, "research_audit")
            if status == GateStatus.PASS:
                return self.engine.transition(state, Stage.EDITORIAL, reason="research audit passed")
            if status == GateStatus.REVISE:
                return self.engine.transition(state, Stage.RESEARCH, reason="research audit requested revision")
            raise WorkflowError("research_audit must be PASS or REVISE before advancing")

        if s == Stage.EDITORIAL:
            self._require_pass(state, "editorial_plan")
            return self.engine.transition(state, Stage.TITLE, reason="TopicDNA and structures frozen")

        if s == Stage.TITLE:
            status = self._status(state, "title_audit")
            if status == GateStatus.PASS:
                return self.engine.transition(state, Stage.DRAFT, reason="headline hook passed")
            if status == GateStatus.REVISE:
                return self.engine.transition(state, Stage.TITLE, reason="headline revision loop")
            raise WorkflowError("title_audit must be PASS or REVISE")

        if s == Stage.DRAFT:
            self._require_pass(state, "draft_output")
            return self.engine.transition(state, Stage.EDITORIAL_AUDIT, reason="draft frozen for independent audit")

        if s == Stage.EDITORIAL_AUDIT:
            status = self._status(state, "editorial_audit")
            if status == GateStatus.PASS:
                return self.engine.transition(state, Stage.DELIVERY, reason="semantic editorial audit passed")
            if status == GateStatus.REVISE:
                target = state.working.get("revise_target", "DRAFT")
                next_stage = Stage.TITLE if target == "TITLE" else Stage.DRAFT
                return self.engine.transition(state, next_stage, reason=f"editorial revision target={target}")
            raise WorkflowError("editorial_audit must be PASS or REVISE")

        if s == Stage.DELIVERY:
            self._require_pass(state, "delivery_output")
            return self.engine.transition(state, Stage.MECHANICAL_AUDIT, reason="artifacts built")

        if s == Stage.MECHANICAL_AUDIT:
            status = self._status(state, "mechanical_audit")
            if status in {GateStatus.PASS, GateStatus.N_A}:
                return self.engine.transition(state, Stage.FINAL_AUDIT, reason="mechanical audit satisfied")
            if status == GateStatus.REVISE:
                return self.engine.transition(state, Stage.DELIVERY, reason="mechanical defects require rebuild")
            raise WorkflowError("mechanical_audit must be PASS or REVISE")

        if s == Stage.FINAL_AUDIT:
            status = self._status(state, "final_audit")
            if status == GateStatus.PASS:
                return self.engine.complete(state)
            if status == GateStatus.REVISE:
                target = state.working.get("final_revise_target", "EDITORIAL")
                next_stage = Stage.DELIVERY if target == "DELIVERY" else Stage.EDITORIAL
                return self.engine.transition(state, next_stage, reason=f"final audit revision target={target}")
            raise WorkflowError("final_audit must be PASS or REVISE")

        raise WorkflowError(f"No automatic advance from {s}")

    @staticmethod
    def _status(state: WritingState, name: str) -> GateStatus:
        gate = state.gates.get(name)
        return gate.status if gate else GateStatus.NOT_RUN

    @classmethod
    def _require_pass(cls, state: WritingState, name: str) -> None:
        if cls._status(state, name) != GateStatus.PASS:
            raise WorkflowError(f"gate {name} must PASS before leaving {state.stage}")
