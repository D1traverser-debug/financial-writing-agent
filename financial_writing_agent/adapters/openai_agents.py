"""Optional OpenAI Agents SDK implementation for high-judgment stages.

The Python state machine remains authoritative. The SDK is used only inside a stage;
it cannot skip, insert, recover or complete stages on its own.
"""
from __future__ import annotations

import json
import os
from typing import Any

from ..models import GateStatus, Stage, WritingState
from ..resources import read_reference
from ..schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, HookAuditDecision, ResearchPackage, StyleAuditDecision
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


def _state_context(state: WritingState) -> str:
    payload = {
        "contract": state.contract.model_dump(mode="json"),
        "working": state.working,
        "gates": {k: v.model_dump(mode="json") for k, v in state.gates.items()},
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


class OpenAIStageExecutor:
    def __init__(self, stage: Stage, *, model: str | None = None):
        self.stage = stage
        self.model = model or os.getenv("FINANCIAL_WRITING_MODEL")

    def _run(self, *, state: WritingState, name: str, instructions: str, output_type: type[Any], prompt: str, web: bool = False):
        Agent, RunConfig, Runner, WebSearchTool = require_sdk()
        tools = [WebSearchTool(search_context_size="high", external_web_access=True)] if web else []
        kwargs: dict[str, Any] = {"name": name, "instructions": instructions, "output_type": output_type, "tools": tools}
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
            },
            trace_include_sensitive_data=False,
        )
        result = Runner.run_sync(agent, prompt, max_turns=16, run_config=run_config)
        return result.final_output

    def execute(self, state: WritingState) -> WritingState:
        if state.stage != self.stage:
            raise RuntimeError(f"executor stage mismatch: expected {self.stage}, got {state.stage}")
        method = getattr(self, f"_execute_{self.stage.value.lower()}", None)
        if method is None:
            raise RuntimeError(f"OpenAI executor not implemented for {self.stage.value}")
        return method(state)

    def _execute_research(self, state: WritingState) -> WritingState:
        instructions = load_reference("research.md") + "\n\n" + load_reference("knowledge.md") + "\n\n" + load_reference("market_explanation.md")
        instructions += (
            "\n\nReturn the required ResearchPackage. Use live web research. Do not draft the article. "
            "Set market_explanation_scope=REQUIRED only when price action, theme/market selection, leadership, continuation/reversal or another cross-sectional price-formation question is materially part of the task. "
            "A company universe by itself is not enough. Otherwise set market_explanation_scope=NOT_MATERIAL and explain why in market_explanation_scope_reason."
        )
        out: ResearchPackage = self._run(
            state=state,
            name="Financial Writing Researcher",
            instructions=instructions,
            output_type=ResearchPackage,
            web=True,
            prompt=f"USER TASK:\n{state.contract.prompt}\n\nSOURCE REFS:\n{state.contract.source_refs}\n",
        )
        state.working["research"] = out.model_dump(mode="json")
        state.set_gate(
            "research_output",
            GateStatus.PASS,
            [f"evidence_items={len(out.evidence_ledger)}", f"universe={len(out.universe)}", f"market_explanation_scope={out.market_explanation_scope}"],
        )
        return state

    def _execute_research_audit(self, state: WritingState) -> WritingState:
        instructions = load_reference("audit.md") + "\n\n" + load_reference("research.md") + "\n\n" + load_reference("market_explanation.md")
        instructions += "\n\nAudit only the research package. If REVISE or FAIL, revision_target must be RESEARCH."
        out: GateDecision = self._run(state=state, name="Financial Writing Research Auditor", instructions=instructions, output_type=GateDecision, prompt=_state_context(state))
        state.set_gate("research_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        if out.revision_target:
            state.working["research_revise_target"] = out.revision_target
        return state

    def _execute_editorial(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("style.md")
        instructions += (
            "\n\nBuild shared TopicDNA and at least two topic-specific candidate structures per applicable mode before selecting one. "
            "FINANCE_DEEP must use MATERIAL_COMPLETE with explicit completeness_obligations and no core_contradictions/compression_candidates. "
            "FINANCE_BROAD must use SELECTIVE_TRAFFIC with 1-3 core_contradictions. Do not draft body text and do not select from a canned structure library."
        )
        out: EditorialPlan = self._run(state=state, name="Financial Writing Editorial Architect", instructions=instructions, output_type=EditorialPlan, prompt=_state_context(state))
        state.working["editorial_plan"] = out.model_dump(mode="json")
        state.set_gate("editorial_plan", GateStatus.PASS, ["shared TopicDNA", "topic-specific mode structures"])
        return state

    def _execute_title(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("platforms.md")
        instructions += (
            "\n\nUse current web/search evidence for WeChat search-intent terms before final selection. Generate 8-12 candidates per applicable mode. "
            "Each candidate must state the intended reader, target-reader click reason, promised payoff, current search term(s) and real evidence refs. "
            "Broader cross-industry finance relevance is optional and must never be forced. Do not invent search volume."
        )
        out: HeadlinePackage = self._run(state=state, name="Financial Writing Headline Engine", instructions=instructions, output_type=HeadlinePackage, web=True, prompt=_state_context(state))
        state.working["headlines"] = out.model_dump(mode="json")
        state.set_gate("title_audit", GateStatus.PASS, ["headline reader-fit/search-evidence package"])
        return state

    def _execute_draft(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("style.md") + "\n\n" + load_reference("delivery.md")
        instructions += (
            "\n\nDraft every applicable formal article in Simplified Chinese. Use numbered hierarchy frequently when it clarifies logic. Never use tables. "
            "FINANCE_DEEP must discharge every completeness_obligation. FINANCE_BROAD may use its selective traffic route. "
            "Use explicit **bold** for key terms, key data and key judgment sentences; provide at least three exact skim_path_anchors per article. "
            "The title + H1s + bold spans must reconstruct the main line. Return risk text only in risk_disclaimer."
        )
        out: DraftPackage = self._run(state=state, name="Financial Writing Writer", instructions=instructions, output_type=DraftPackage, prompt=_state_context(state))
        state.working["draft"] = out.model_dump(mode="json")
        state.set_gate("draft_output", GateStatus.PASS, ["structured draft package frozen"])
        return state

    def _execute_editorial_audit(self, state: WritingState) -> WritingState:
        hook_instructions = load_reference("hooks.md") + (
            "\n\nAct as an independent Reader Funnel Judge. Audit the frozen selected title, actual first three complete sentences, H1s, representative paragraph transitions and final substantive payoff. "
            "Use revision_target=TITLE only when the selected title/search promise itself must change; otherwise use DRAFT."
        )
        hook_out: HookAuditDecision = self._run(state=state, name="Financial Writing Reader Funnel Judge", instructions=hook_instructions, output_type=HookAuditDecision, prompt=_state_context(state))
        state.set_gate("hook_audit", GateStatus(hook_out.status), hook_out.evidence, "; ".join(hook_out.revision_notes))
        state.working["hook_audit"] = hook_out.model_dump(mode="json")

        prose_instructions = load_reference("style.md") + (
            "\n\nAct as an independent Natural Authorial Prose Judge. Audit the frozen draft against the exact nine-part rubric: fidelity/responsibility, semantic contribution, argument progression, reader calibration, authorial selectivity, evidence specificity, structural/rhythm naturalness, template/redundancy control and uncertainty/rhetoric calibration. "
            "If REVISE, revision_target must be DRAFT."
        )
        prose_out: StyleAuditDecision = self._run(state=state, name="Financial Writing Authorial Prose Judge", instructions=prose_instructions, output_type=StyleAuditDecision, prompt=_state_context(state))
        state.set_gate("style_audit", GateStatus(prose_out.status), prose_out.evidence, "; ".join(prose_out.detected_patterns + prose_out.reasoning_findings + prose_out.revision_notes))
        state.working["style_audit"] = prose_out.model_dump(mode="json")

        if hook_out.status != "PASS" or prose_out.status != "PASS":
            target = "TITLE" if hook_out.status == "REVISE" and hook_out.revision_target == "TITLE" else "DRAFT"
            evidence = hook_out.evidence + prose_out.evidence
            state.set_gate("editorial_audit", GateStatus.REVISE, evidence, "dedicated Reader Funnel/Authorial Prose gate requires revision")
            state.working["revise_target"] = target
            return state

        instructions = load_reference("audit.md") + (
            "\n\nAudit the frozen draft for evidence, FINANCE_DEEP completeness / FINANCE_BROAD legal compression, market-explanation discipline when activated, skim-path coherence and compliance. "
            "Dedicated Reader Funnel and Authorial Prose gates already passed. If an upstream defect is discovered, use the earliest correct revision_target among RESEARCH, EDITORIAL, TITLE or DRAFT."
        )
        out: GateDecision = self._run(state=state, name="Financial Writing Editorial Auditor", instructions=instructions, output_type=GateDecision, prompt=_state_context(state))
        state.set_gate("editorial_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        if out.revision_target:
            state.working["revise_target"] = out.revision_target
        return state

    def _execute_final_audit(self, state: WritingState) -> WritingState:
        instructions = load_reference("audit.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("style.md")
        instructions += (
            "\n\nPerform final red-team review of frozen Word content plus recorded mechanical audit. Do not audit or request images; Financial Writing has no visual workflow. "
            "If a defect is upstream, use the earliest correct revision_target among RESEARCH, EDITORIAL, TITLE, DRAFT or DELIVERY."
        )
        out: GateDecision = self._run(state=state, name="Financial Writing Final Auditor", instructions=instructions, output_type=GateDecision, prompt=_state_context(state))
        state.set_gate("final_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        if out.revision_target:
            state.working["final_revise_target"] = out.revision_target
        if out.status == "PASS":
            finalize_audit_artifact(state)
        return state


def build_openai_executors(*, model: str | None = None) -> dict[Stage, OpenAIStageExecutor]:
    return {stage: OpenAIStageExecutor(stage, model=model) for stage in {Stage.RESEARCH, Stage.RESEARCH_AUDIT, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT, Stage.EDITORIAL_AUDIT, Stage.FINAL_AUDIT}}
