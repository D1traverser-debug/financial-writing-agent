from __future__ import annotations

from .engine import WorkflowError, WritingEngine
from .models import GateStatus, Stage, WritingState
from .workflow_spec import pass_target, require_revision_target


class WorkflowController:
    """Code-owned routing. The model never decides whether a mandatory stage exists."""

    def __init__(self, engine: WritingEngine):
        self.engine = engine

    @staticmethod
    def _pass_target(stage: Stage) -> Stage:
        target = pass_target(stage)
        if target is None:
            raise WorkflowError(f"No PASS/forward route from {stage}")
        return target

    @staticmethod
    def _revision_target(stage: Stage, target: str) -> Stage:
        try:
            return require_revision_target(stage, target)
        except ValueError as exc:
            raise WorkflowError(str(exc)) from exc

    def advance(self, state: WritingState) -> WritingState:
        s = state.stage
        if s == Stage.INTAKE:
            self._require_pass(state, "runtime_initialized")
            return self.engine.transition(state, self._pass_target(s), reason="runtime initialized")

        if s == Stage.RESEARCH:
            self._require_pass(state, "research_output")
            return self.engine.transition(state, self._pass_target(s), reason="research package ready")

        if s == Stage.RESEARCH_AUDIT:
            status = self._status(state, "research_audit")
            if status == GateStatus.PASS:
                self._require_semantic_pass(state, "research_audit")
                return self.engine.transition(state, self._pass_target(s), reason="research audit passed")
            if status == GateStatus.REVISE:
                return self.engine.transition(
                    state,
                    self._revision_target(s, state.working.get("research_revise_target", "RESEARCH")),
                    reason="research audit requested revision",
                )
            raise WorkflowError("research_audit must be PASS or REVISE before advancing")

        if s == Stage.EDITORIAL:
            self._require_pass(state, "editorial_plan")
            return self.engine.transition(state, self._pass_target(s), reason="TopicDNA and mode-specific structures frozen")

        if s == Stage.TITLE:
            status = self._status(state, "title_audit")
            if status == GateStatus.PASS:
                return self.engine.transition(state, self._pass_target(s), reason="headline candidate/search-evidence package passed")
            if status == GateStatus.REVISE:
                return self.engine.transition(state, self._revision_target(s, "TITLE"), reason="headline revision loop")
            raise WorkflowError("title_audit must be PASS or REVISE")

        if s == Stage.DRAFT:
            status = self._status(state, "draft_output")
            if status == GateStatus.PASS:
                return self.engine.transition(state, self._pass_target(s), reason="draft frozen for stage-separated audits")
            if status == GateStatus.REVISE:
                return self.engine.transition(state, self._revision_target(s, "DRAFT"), reason="draft coverage/navigation guard requested revision")
            raise WorkflowError("draft_output must be PASS or REVISE")

        if s == Stage.EDITORIAL_AUDIT:
            status = self._status(state, "editorial_audit")
            if status == GateStatus.PASS:
                self._require_semantic_pass(state, "hook_audit")
                self._require_semantic_pass(state, "style_audit")
                self._require_semantic_pass(state, "editorial_audit")
                return self.engine.transition(state, self._pass_target(s), reason="Reader Funnel + Authorial Prose + general editorial audits passed with owner-runtime execution proof")
            if status == GateStatus.REVISE:
                target = state.working.get("revise_target", "DRAFT")
                revision = self._revision_target(s, target)
                return self.engine.transition(state, revision, reason=f"editorial revision target={target}")
            raise WorkflowError("editorial_audit must be PASS or REVISE")

        if s == Stage.DELIVERY:
            self._require_pass(state, "delivery_output")
            return self.engine.transition(state, self._pass_target(s), reason="Word artifacts built")

        if s == Stage.MECHANICAL_AUDIT:
            status = self._status(state, "mechanical_audit")
            if status == GateStatus.PASS:
                return self.engine.transition(state, self._pass_target(s), reason="mechanical Word audit passed")
            if status == GateStatus.REVISE:
                return self.engine.transition(state, self._revision_target(s, "DELIVERY"), reason="mechanical defects require rebuild")
            raise WorkflowError("mechanical_audit must PASS or REVISE")

        if s == Stage.FINAL_AUDIT:
            status = self._status(state, "final_audit")
            if status == GateStatus.PASS:
                self._require_semantic_pass(state, "final_audit")
                # Completion owns its own proof-bearing gate checks but the legal target
                # still comes from the canonical workflow specification.
                if self._pass_target(s) != Stage.COMPLETE:
                    raise WorkflowError("FINAL_AUDIT canonical PASS target must be COMPLETE")
                return self.engine.complete(state)
            if status == GateStatus.REVISE:
                target = state.working.get("final_revise_target", "EDITORIAL")
                revision = self._revision_target(s, target)
                return self.engine.transition(state, revision, reason=f"final audit revision target={target}")
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

    @classmethod
    def _require_semantic_pass(cls, state: WritingState, name: str) -> None:
        cls._require_pass(state, name)
        if not state.semantic_gate_proof_valid(name):
            raise WorkflowError(
                f"semantic gate {name} PASS lacks current owner-runtime stage execution proof; "
                "CHAT_BRIDGED/self-authored provenance cannot advance the workflow"
            )
