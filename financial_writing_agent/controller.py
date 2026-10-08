from __future__ import annotations

from .engine import WorkflowError, WritingEngine
from .harness import validate_research_against_knowledge_context
from .models import ContentMode, DistributionMode, GateStatus, Stage, WritingState
from .schemas import ResearchPackage


REVISION_LIMIT_KEY = {
    Stage.RESEARCH: "research_max_rounds",
    Stage.TITLE: "title_max_rounds",
    Stage.DRAFT: "draft_max_rounds",
}


class WorkflowController:
    """Code-owned routing. The model never decides whether a mandatory stage exists."""

    def __init__(self, engine: WritingEngine):
        self.engine = engine

    def _consume_revision_budget(self, state: WritingState, target: Stage) -> bool:
        constraint_key = REVISION_LIMIT_KEY.get(target)
        if constraint_key is None:
            return True
        raw_limit = state.contract.run_constraints.get(constraint_key)
        if raw_limit is None:
            return True
        try:
            max_rounds = int(raw_limit)
        except (TypeError, ValueError):
            self.engine.block(state, f"invalid {constraint_key}={raw_limit!r}")
            return False
        if max_rounds < 1:
            self.engine.block(state, f"invalid {constraint_key}={max_rounds}; must be >=1")
            return False

        revision_count = self.engine.increment_attempt(state, f"{target.value.lower()}_revision_count")
        requested_round = revision_count + 1  # initial execution is round 1
        state.add_trace(
            "REVISION_BUDGET",
            f"target={target.value}; requested_round={requested_round}; max_rounds={max_rounds}",
        )
        self.engine.store.save(state)
        if requested_round > max_rounds:
            self.engine.block(
                state,
                f"{target.value} revision budget exhausted: requested_round={requested_round}, max_rounds={max_rounds}",
            )
            return False
        return True

    def advance(self, state: WritingState) -> WritingState:
        s = state.stage
        if s == Stage.INTAKE:
            self._require_pass(state, "runtime_initialized")
            return self.engine.transition(state, Stage.RESEARCH, reason="runtime initialized")

        if s == Stage.RESEARCH:
            self._require_satisfied(state, "knowledge_context")
            self._require_pass(state, "research_output")
            raw_research = state.working.get("research")
            if raw_research is not None:
                payload = ResearchPackage.model_validate(raw_research)
                validate_research_against_knowledge_context(state, payload)
            elif any(event.event == "EXECUTOR_START" and event.stage == Stage.RESEARCH for event in state.trace):
                raise WorkflowError("research executor passed research_output without a structured ResearchPackage")
            return self.engine.transition(state, Stage.RESEARCH_AUDIT, reason="knowledge recall decision and research package ready")

        if s == Stage.RESEARCH_AUDIT:
            status = self._status(state, "research_audit")
            if status == GateStatus.PASS:
                return self.engine.transition(state, Stage.EDITORIAL, reason="research audit passed")
            if status == GateStatus.REVISE:
                if not self._consume_revision_budget(state, Stage.RESEARCH):
                    return state
                reason = state.gates["research_audit"].notes or "research audit requested revision"
                self.engine.invalidate_for_revision(state, Stage.RESEARCH, reason=reason)
                return self.engine.transition(state, Stage.RESEARCH, reason="research audit requested revision")
            raise WorkflowError("research_audit must be PASS or REVISE before advancing")

        if s == Stage.EDITORIAL:
            self._require_pass(state, "editorial_plan")
            return self.engine.transition(state, Stage.TITLE, reason="TopicDNA and applicable initial structure frozen")

        if s == Stage.TITLE:
            status = self._status(state, "title_audit")
            if status == GateStatus.PASS:
                self._require_pass(state, "acceptance_contract")
                return self.engine.transition(state, Stage.DRAFT, reason="headline hook and applicable acceptance contract passed")
            if status == GateStatus.REVISE:
                if not self._consume_revision_budget(state, Stage.TITLE):
                    return state
                reason = state.gates["title_audit"].notes or "headline revision loop"
                self.engine.invalidate_for_revision(state, Stage.TITLE, reason=reason)
                return self.engine.transition(state, Stage.TITLE, reason="headline revision loop")
            raise WorkflowError("title_audit must be PASS or REVISE")

        if s == Stage.DRAFT:
            self._require_pass(state, "draft_output")
            if (
                state.contract.content_mode == ContentMode.FORMAL_ARTICLE
                and state.contract.distribution_mode == DistributionMode.DUAL
            ):
                state.working["broad_derivation_phase"] = "EDITORIAL"
                self.engine.store.save(state)
                return self.engine.transition(
                    state,
                    Stage.BROAD_DERIVATION,
                    reason="FINANCE_DEEP mother draft frozen; derive FINANCE_BROAD now",
                )
            return self.engine.transition(state, Stage.EDITORIAL_AUDIT, reason="draft frozen for independent audit")

        if s == Stage.BROAD_DERIVATION:
            self._require_pass(state, "broad_derivation")
            return self.engine.transition(
                state,
                Stage.EDITORIAL_AUDIT,
                reason="FINANCE_BROAD derived from frozen FINANCE_DEEP mother draft",
            )

        if s == Stage.EDITORIAL_AUDIT:
            status = self._status(state, "editorial_audit")
            if status == GateStatus.PASS:
                return self.engine.transition(state, Stage.DELIVERY, reason="semantic editorial audit passed")
            if status == GateStatus.REVISE:
                target = state.working.get("revise_target", "DRAFT")
                next_stage = Stage.TITLE if target == "TITLE" else Stage.DRAFT
                if not self._consume_revision_budget(state, next_stage):
                    return state
                reason = state.gates["editorial_audit"].notes or f"editorial revision target={target}"
                self.engine.invalidate_for_revision(state, next_stage, reason=reason)
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
                reason = state.gates["mechanical_audit"].notes or "mechanical defects require rebuild"
                self.engine.invalidate_for_revision(state, Stage.DELIVERY, reason=reason)
                return self.engine.transition(state, Stage.DELIVERY, reason="mechanical defects require rebuild")
            raise WorkflowError("mechanical_audit must be PASS or REVISE")

        if s == Stage.FINAL_AUDIT:
            status = self._status(state, "final_audit")
            if status == GateStatus.PASS:
                return self.engine.complete(state)
            if status == GateStatus.REVISE:
                target = state.working.get("final_revise_target", "EDITORIAL")
                mapping = {
                    "RESEARCH": Stage.RESEARCH,
                    "EDITORIAL": Stage.EDITORIAL,
                    "TITLE": Stage.TITLE,
                    "DRAFT": Stage.DRAFT,
                    "DELIVERY": Stage.DELIVERY,
                }
                next_stage = mapping.get(target)
                if next_stage is None:
                    raise WorkflowError(f"unsupported final revision target={target}")
                if not self._consume_revision_budget(state, next_stage):
                    return state
                reason = state.gates["final_audit"].notes or f"final audit revision target={target}"
                self.engine.invalidate_for_revision(state, next_stage, reason=reason)
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

    @classmethod
    def _require_satisfied(cls, state: WritingState, name: str) -> None:
        if cls._status(state, name) not in {GateStatus.PASS, GateStatus.N_A}:
            raise WorkflowError(f"gate {name} must be PASS or N_A before leaving {state.stage}")
