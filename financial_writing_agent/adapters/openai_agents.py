"""Optional OpenAI Agents SDK implementation for high-judgment stages.

The Python state machine remains authoritative. Model specialists execute only inside a
stage-specific contract: canonical references own business semantics, the contract owns
context/tool/output boundaries, and the SDK judge run cannot create workflow authority.
"""
from __future__ import annotations

import json
import os
from typing import Any

from ..checks import analyze_template_scaffolding, check_deep_company_grounding, payload_text
from ..models import GateStatus, Stage, WritingState
from ..resources import read_reference
from ..schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, HookAuditDecision, ResearchPackage, StyleAuditDecision
from ..specialist_contracts import projected_artifacts, projected_gates, projected_working, specialist_contract
from .deterministic import finalize_audit_artifact


class OpenAIAgentsUnavailable(RuntimeError):
    pass


def require_sdk():
    try:
        from agents import Agent, RunConfig, Runner, WebSearchTool  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise OpenAIAgentsUnavailable("Install optional dependency with: pip install 'financial-writing-agent[openai]'") from exc
    return Agent, RunConfig, Runner, WebSearchTool


def load_reference(name: str) -> str:
    return read_reference(name)


def _specialist_instructions(specialist_id: str) -> str:
    contract = specialist_contract(specialist_id)
    canonical = "\n\n".join(load_reference(name) for name in contract.reference_names)
    forbidden = "; ".join(contract.forbidden_actions)
    return (
        canonical
        + "\n\nEXECUTION BOUNDARY (not a second business-rule source):\n"
        + contract.execution_instruction
        + f"\nOutput schema: {contract.output_schema}."
        + f"\nForbidden actions: {forbidden}."
    )


def _state_context(state: WritingState, specialist_id: str) -> str:
    """Project only the state slices authorized for one specialist contract."""
    contract = specialist_contract(specialist_id)
    if contract.stage != state.stage:
        raise RuntimeError(
            f"specialist context stage mismatch: {specialist_id} owns {contract.stage.value}, current={state.stage.value}"
        )
    payload = {
        "contract": state.contract.model_dump(mode="json"),
        "working": projected_working(state.working, specialist_id),
        "gates": {
            key: value.model_dump(mode="json")
            for key, value in projected_gates(state.gates, specialist_id).items()
        },
        "artifacts": projected_artifacts(state.artifacts, specialist_id),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


class OpenAIStageExecutor:
    def __init__(self, stage: Stage, *, model: str | None = None):
        self.stage = stage
        self.model = model or os.getenv("FINANCIAL_WRITING_MODEL")

    def _run(
        self,
        *,
        state: WritingState,
        specialist_id: str,
        output_type: type[Any],
    ):
        contract = specialist_contract(specialist_id)
        if contract.stage != self.stage or state.stage != self.stage:
            raise RuntimeError(
                f"specialist stage mismatch: specialist={contract.stage.value}, executor={self.stage.value}, state={state.stage.value}"
            )
        if contract.output_schema != output_type.__name__:
            raise RuntimeError(
                f"specialist output mismatch: {specialist_id} contract={contract.output_schema}, runtime={output_type.__name__}"
            )

        Agent, RunConfig, Runner, WebSearchTool = require_sdk()
        tools = [WebSearchTool(search_context_size="high", external_web_access=True)] if contract.web_access else []
        instructions = _specialist_instructions(specialist_id)
        if contract.author_identity is not None:
            execution_ref = f"{state.contract.task_id}:{self.stage.value}:{contract.display_name}"
            instructions += (
                "\n\nAUDIT PROVENANCE CONTRACT: this is a separate SDK judge run, not writer self-review. "
                f"Set provenance.assurance='INDEPENDENT_EXECUTOR', provenance.reviewer_identity={contract.display_name!r}, "
                f"provenance.author_identity={contract.author_identity!r}, provenance.execution_ref={execution_ref!r}. "
                "Do not claim provider-isolated assurance; this field only proves a separate stage-bound executor run."
            )

        kwargs: dict[str, Any] = {
            "name": contract.display_name,
            "instructions": instructions,
            "output_type": output_type,
            "tools": tools,
        }
        if self.model:
            kwargs["model"] = self.model
        agent = Agent(**kwargs)
        run_config = RunConfig(
            workflow_name="Financial Writing Agent",
            group_id=state.contract.task_id,
            trace_metadata={
                "stage": self.stage.value,
                "distribution_mode": state.contract.distribution_mode.value,
                "content_mode": state.contract.content_mode.value,
                "executor_name": contract.display_name,
                "specialist_id": specialist_id,
            },
            trace_include_sensitive_data=False,
        )
        result = Runner.run_sync(
            agent,
            _state_context(state, specialist_id),
            max_turns=16,
            run_config=run_config,
        )
        return result.final_output

    def execute(self, state: WritingState) -> WritingState:
        if state.stage != self.stage:
            raise RuntimeError(f"executor stage mismatch: expected {self.stage}, got {state.stage}")
        method = getattr(self, f"_execute_{self.stage.value.lower()}", None)
        if method is None:
            raise RuntimeError(f"OpenAI executor not implemented for {self.stage.value}")
        return method(state)

    def _execute_research(self, state: WritingState) -> WritingState:
        out: ResearchPackage = self._run(
            state=state,
            specialist_id="researcher",
            output_type=ResearchPackage,
        )
        state.working["research"] = out.model_dump(mode="json")
        state.set_gate(
            "research_output",
            GateStatus.PASS,
            [
                f"evidence_items={len(out.evidence_ledger)}",
                f"universe={len(out.universe)}",
                f"universe_coverage={out.universe_coverage.status}",
                f"value_chain_classes={len(out.universe_coverage.classes)}",
                f"market_explanation_scope={out.market_explanation_scope}",
            ],
        )
        return state

    def _execute_research_audit(self, state: WritingState) -> WritingState:
        out: GateDecision = self._run(
            state=state,
            specialist_id="research_auditor",
            output_type=GateDecision,
        )
        state.set_gate("research_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        state.working["research_audit"] = out.model_dump(mode="json")
        if out.revision_target:
            state.working["research_revise_target"] = out.revision_target
        return state

    def _execute_editorial(self, state: WritingState) -> WritingState:
        out: EditorialPlan = self._run(
            state=state,
            specialist_id="editorial_architect",
            output_type=EditorialPlan,
        )
        state.working["editorial_plan"] = out.model_dump(mode="json")
        state.set_gate("editorial_plan", GateStatus.PASS, ["shared TopicDNA", "topic-specific mode structures", "deep company coverage obligations"])
        return state

    def _execute_title(self, state: WritingState) -> WritingState:
        out: HeadlinePackage = self._run(
            state=state,
            specialist_id="headline_engine",
            output_type=HeadlinePackage,
        )
        state.working["headlines"] = out.model_dump(mode="json")
        state.set_gate("title_audit", GateStatus.PASS, ["headline reader-fit/search-evidence package", "angle-family diversity schema passed"])
        return state

    def _execute_draft(self, state: WritingState) -> WritingState:
        out: DraftPackage = self._run(
            state=state,
            specialist_id="writer",
            output_type=DraftPackage,
        )
        state.working["draft"] = out.model_dump(mode="json")

        research = ResearchPackage.model_validate(state.working["research"])
        errors: list[str] = []
        if out.finance_deep is not None:
            errors.extend(check_deep_company_grounding(out.finance_deep, research))
        if errors:
            state.working["draft_guard_errors"] = errors
            state.set_gate("draft_output", GateStatus.REVISE, ["deterministic deep-company grounding guard"], "; ".join(errors))
        else:
            state.working.pop("draft_guard_errors", None)
            state.set_gate("draft_output", GateStatus.PASS, ["structured draft package frozen", "deep universe grounding guard passed"])
        return state

    def _execute_editorial_audit(self, state: WritingState) -> WritingState:
        draft = DraftPackage.model_validate(state.working["draft"])
        template_reports: dict[str, dict[str, Any]] = {}
        if draft.finance_deep is not None:
            template_reports["FINANCE_DEEP"] = analyze_template_scaffolding(payload_text(draft.finance_deep))
        if draft.finance_broad is not None:
            template_reports["FINANCE_BROAD"] = analyze_template_scaffolding(payload_text(draft.finance_broad))
        state.working["template_signal_report"] = template_reports

        hook_out: HookAuditDecision = self._run(
            state=state,
            specialist_id="reader_funnel_judge",
            output_type=HookAuditDecision,
        )
        state.set_gate("hook_audit", GateStatus(hook_out.status), hook_out.evidence, "; ".join(hook_out.revision_notes))
        state.working["hook_audit"] = hook_out.model_dump(mode="json")

        prose_out: StyleAuditDecision = self._run(
            state=state,
            specialist_id="authorial_prose_judge",
            output_type=StyleAuditDecision,
        )
        template_revise = any(report.get("requires_revise") for report in template_reports.values())
        prose_status = "REVISE" if template_revise else prose_out.status
        prose_notes = list(prose_out.detected_patterns + prose_out.reasoning_findings + prose_out.revision_notes)
        if template_revise:
            prose_notes.append(f"deterministic template cluster requires revision: {json.dumps(template_reports, ensure_ascii=False)}")
        state.set_gate("style_audit", GateStatus(prose_status), prose_out.evidence, "; ".join(prose_notes))
        state.working["style_audit"] = {
            **prose_out.model_dump(mode="json"),
            "effective_status": prose_status,
            "deterministic_template_guard": template_reports,
        }

        if hook_out.status != "PASS" or prose_status != "PASS":
            target = "TITLE" if hook_out.status == "REVISE" and hook_out.revision_target == "TITLE" else "DRAFT"
            evidence = hook_out.evidence + prose_out.evidence
            state.set_gate("editorial_audit", GateStatus.REVISE, evidence, "dedicated Reader Funnel/Authorial Prose gate requires revision")
            state.working["revise_target"] = target
            return state

        out: GateDecision = self._run(
            state=state,
            specialist_id="general_editorial_judge",
            output_type=GateDecision,
        )
        state.set_gate("editorial_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        state.working["editorial_audit"] = out.model_dump(mode="json")
        if out.revision_target:
            state.working["revise_target"] = out.revision_target
        return state

    def _execute_final_audit(self, state: WritingState) -> WritingState:
        out: GateDecision = self._run(
            state=state,
            specialist_id="final_auditor",
            output_type=GateDecision,
        )
        state.set_gate("final_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        state.working["final_audit"] = out.model_dump(mode="json")
        if out.revision_target:
            state.working["final_revise_target"] = out.revision_target
        if out.status == "PASS":
            finalize_audit_artifact(state)
        return state


def build_openai_executors(*, model: str | None = None) -> dict[Stage, OpenAIStageExecutor]:
    return {
        stage: OpenAIStageExecutor(stage, model=model)
        for stage in {
            Stage.RESEARCH,
            Stage.RESEARCH_AUDIT,
            Stage.EDITORIAL,
            Stage.TITLE,
            Stage.DRAFT,
            Stage.EDITORIAL_AUDIT,
            Stage.FINAL_AUDIT,
        }
    }
