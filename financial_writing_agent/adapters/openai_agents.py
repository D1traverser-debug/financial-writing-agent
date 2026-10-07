"""Optional OpenAI Agents SDK implementation for high-judgment stages.

The Python state machine remains authoritative. The SDK is used only inside a stage;
it cannot skip, insert, or complete stages on its own. Creative image generation,
render-page visual inspection and connected-store I/O are orchestrated by the
ChatGPT/MCP plugin path, not this standalone diagnostic adapter.
"""
from __future__ import annotations

import json
import os
from typing import Any

from ..harness import freeze_acceptance_contract, validate_draft_against_acceptance
from ..models import ContentMode, GateStatus, Stage, WritingState
from ..resources import read_reference
from ..schemas import DraftPackage, EditorialPlan, FinalAuditDecision, GateDecision, HeadlinePackage, ResearchPackage, StyleAuditDecision
from .deterministic import finalize_audit_artifact


class OpenAIAgentsUnavailable(RuntimeError):
    pass


def require_sdk():
    try:
        from agents import Agent, RunConfig, Runner, WebSearchTool  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise OpenAIAgentsUnavailable(
            "Install optional dependency with: pip install 'financial-writing-agent[openai]'"
        ) from exc
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

    def _run(
        self,
        *,
        name: str,
        instructions: str,
        output_type: type[Any],
        prompt: str,
        group_id: str,
        web: bool = False,
    ):
        Agent, RunConfig, Runner, WebSearchTool = require_sdk()
        tools = [WebSearchTool(search_context_size="high", external_web_access=True)] if web else []
        kwargs: dict[str, Any] = {
            "name": name,
            "instructions": instructions,
            "output_type": output_type,
            "tools": tools,
        }
        if self.model:
            kwargs["model"] = self.model
        agent = Agent(**kwargs)
        run_config = RunConfig(
            workflow_name="Financial Writing Agent",
            group_id=group_id,
            trace_metadata={"stage": self.stage.value, "executor": name},
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
        instructions = load_reference("research.md") + "\n\n" + load_reference("knowledge.md")
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md") + "\n\nVerify current WeChat sticker-post limits/mechanics with live web evidence and preserve sources for the later PlatformConstraintSnapshot."
        instructions += (
            "\n\nReturn the required ResearchPackage. Use live web research. Do not draft the article. "
            "For evidence that can support a headline, opening, H1 or central conclusion, set core_safe=true only after recording an auditable verification_status. "
            "Independent cross-checks must identify a genuinely independent source group; a lone authoritative source must use SINGLE_SOURCE_ATTRIBUTED with allowed_wording."
        )
        out: ResearchPackage = self._run(
            name="Financial Writing Researcher",
            instructions=instructions,
            output_type=ResearchPackage,
            web=True,
            group_id=state.contract.task_id,
            prompt=f"USER TASK:\n{state.contract.prompt}\n\nSOURCE REFS:\n{state.contract.source_refs}\n",
        )
        state.working["research"] = out.model_dump(mode="json")
        state.set_gate(
            "research_output",
            GateStatus.PASS,
            [
                f"evidence_items={len(out.evidence_ledger)}",
                f"core_safe={sum(item.core_safe for item in out.evidence_ledger)}",
                f"universe={len(out.universe)}",
                f"review_queue={len(out.review_queue)}",
                f"failed_tools={len(out.failed_tools_or_sources)}",
            ],
        )
        return state

    def _execute_research_audit(self, state: WritingState) -> WritingState:
        instructions = load_reference("audit.md") + "\n\nAudit only the research package against the research and knowledge reference rules. Check evidence verification status and source independence rather than accepting core_safe labels at face value."
        out: GateDecision = self._run(
            name="Financial Writing Research Auditor",
            instructions=instructions,
            output_type=GateDecision,
            web=False,
            group_id=state.contract.task_id,
            prompt=_state_context(state),
        )
        state.set_gate("research_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        if out.revision_target:
            state.working["research_revise_target"] = out.revision_target
        return state

    def _execute_editorial(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("style.md") + "\n\n" + load_reference("structure_patterns.md")
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md") + "\n\nReturn a wechat_sticker mode plan. Design a concise image-first structure; do not force long-article H1 architecture."
        else:
            instructions += (
                "\n\nReturn one independent ModeEditorialPlan for every applicable distribution mode. "
                "For DUAL, finance_deep and finance_broad must each generate their own 2-3 candidate structures and select independently after TopicDNA; sharing the research base does not mean sharing one outline."
            )
        instructions += "\n\nBuild TopicDNA and candidate structures. Do not draft body text."
        out: EditorialPlan = self._run(
            name="Financial Writing Editorial Architect",
            instructions=instructions,
            output_type=EditorialPlan,
            web=False,
            group_id=state.contract.task_id,
            prompt=_state_context(state),
        )
        state.working["editorial_plan"] = out.model_dump(mode="json")
        evidence = ["TopicDNA"]
        if out.finance_deep:
            evidence.append(f"FINANCE_DEEP_structures={len(out.finance_deep.candidates)}")
        if out.finance_broad:
            evidence.append(f"FINANCE_BROAD_structures={len(out.finance_broad.candidates)}")
        if out.wechat_sticker:
            evidence.append(f"WECHAT_STICKER_structures={len(out.wechat_sticker.candidates)}")
        state.set_gate("editorial_plan", GateStatus.PASS, evidence)
        return state

    def _execute_title(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("style.md")
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md") + "\n\nGenerate sticker-post title candidates that complement the image hook. Do not assume remembered platform character limits; use the verified research context."
        else:
            instructions += (
                "\n\nGenerate 8-12 genuinely different candidates per applicable mode. Every candidate must record a verified factual_anchor, one primary information gap, and the opening_payoff that will satisfy the click."
            )
        out: HeadlinePackage = self._run(
            name="Financial Writing Headline Engine",
            instructions=instructions,
            output_type=HeadlinePackage,
            web=False,
            group_id=state.contract.task_id,
            prompt=_state_context(state),
        )
        state.working["headlines"] = out.model_dump(mode="json")
        applicable: list[bool] = []
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            applicable.append(bool(out.wechat_sticker_selected))
        else:
            if state.contract.distribution_mode.value in {"FINANCE_DEEP", "DUAL"}:
                applicable.append(bool(out.finance_deep_selected))
            if state.contract.distribution_mode.value in {"FINANCE_BROAD", "DUAL"}:
                applicable.append(bool(out.finance_broad_selected))
        status = GateStatus.PASS if applicable and all(applicable) else GateStatus.REVISE
        state.set_gate("title_audit", status, [f"applicable_modes={len(applicable)}"])
        if status == GateStatus.PASS:
            freeze_acceptance_contract(state)
        return state

    def _execute_draft(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("style.md") + "\n\n" + load_reference("delivery.md")
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md") + "\n\nReturn only wechat_sticker_post in DraftPackage. Its PlatformConstraintSnapshot must come from current research evidence; keep copy concise/useful, include an interaction prompt when appropriate, and include a compact information-dense risk_disclaimer field."
        else:
            instructions += (
                "\n\nDraft the applicable article mode(s) against the frozen acceptance_contract. "
                "Each formal article must start with exactly one independent lead, followed immediately by the first H1. "
                "Use the frozen selected title and selected structure; return risk text only in risk_disclaimer."
            )
        out: DraftPackage = self._run(
            name="Financial Writing Writer",
            instructions=instructions,
            output_type=DraftPackage,
            web=False,
            group_id=state.contract.task_id,
            prompt=_state_context(state),
        )
        evidence = validate_draft_against_acceptance(state, out)
        state.working["draft"] = out.model_dump(mode="json")
        state.set_gate("draft_output", GateStatus.PASS, ["structured draft package frozen", *evidence])
        return state

    def _execute_editorial_audit(self, state: WritingState) -> WritingState:
        style_instructions = load_reference("style.md") + "\n\nAct as a dedicated style judge independent from the writer. Audit only AI-template fingerprints, paragraph/section transitions, repetitive rhetorical constructions, rhythm problems, empty bridges and unsupported extreme/superlative language."
        style_out: StyleAuditDecision = self._run(
            name="Financial Writing Anti-AI Style Judge",
            instructions=style_instructions,
            output_type=StyleAuditDecision,
            web=False,
            group_id=state.contract.task_id,
            prompt=_state_context(state),
        )
        state.set_gate("style_audit", GateStatus(style_out.status), style_out.evidence, "; ".join(style_out.detected_patterns + style_out.transition_findings + style_out.extreme_language_findings + style_out.revision_notes))
        state.working["style_audit"] = style_out.model_dump(mode="json")
        if style_out.status != "PASS":
            state.set_gate("editorial_audit", GateStatus.REVISE, style_out.evidence, "style audit requires draft revision")
            state.working["revise_target"] = "DRAFT"
            return state

        instructions = load_reference("audit.md") + "\n\nAudit the frozen draft and acceptance_contract for evidence, reasoning continuity, hook payoff, information density, platform fit and compliance. The dedicated style gate has already passed; do not replace it with writer self-assessment."
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md")
        out: GateDecision = self._run(
            name="Financial Writing Editorial Auditor",
            instructions=instructions,
            output_type=GateDecision,
            web=False,
            group_id=state.contract.task_id,
            prompt=_state_context(state),
        )
        state.set_gate("editorial_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        if out.revision_target:
            state.working["revise_target"] = out.revision_target
        return state

    def _execute_final_audit(self, state: WritingState) -> WritingState:
        instructions = load_reference("audit.md") + "\n\n" + load_reference("style.md")
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md")
        instructions += (
            "\n\nPerform final red-team review of the frozen content against the acceptance_contract and recorded mechanical audit. "
            "Follow the exact acceptance_evidence KEY: evidence inventory in audit.md. "
            "This standalone diagnostic path does not provide rendered page images to the judge, so reviewed_render_pages must be empty and you must not claim visual page inspection."
        )
        out: FinalAuditDecision = self._run(
            name="Financial Writing Final Auditor",
            instructions=instructions,
            output_type=FinalAuditDecision,
            web=False,
            group_id=state.contract.task_id,
            prompt=_state_context(state),
        )
        if out.status == "PASS" and not out.acceptance_evidence:
            raise RuntimeError("standalone final PASS requires acceptance_evidence")
        if out.reviewed_render_pages:
            raise RuntimeError("standalone final auditor cannot claim render-page inspection")
        evidence = out.evidence + out.acceptance_evidence
        state.set_gate("final_audit", GateStatus(out.status), evidence, "; ".join(out.defects + out.remaining_boundaries))
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
