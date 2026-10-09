"""Optional OpenAI Agents SDK implementation for high-judgment stages.

The Python state machine remains authoritative. The SDK is used only inside a stage;
it cannot skip, insert, or complete stages on its own.
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
        from agents import Agent, Runner, WebSearchTool  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise OpenAIAgentsUnavailable("Install optional dependency with: pip install 'financial-writing-agent[openai]'") from exc
    return Agent, Runner, WebSearchTool


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

    def _run(self, *, name: str, instructions: str, output_type: type[Any], prompt: str, web: bool = False):
        Agent, Runner, WebSearchTool = require_sdk()
        tools = [WebSearchTool(search_context_size="high", external_web_access=True)] if web else []
        kwargs: dict[str, Any] = {"name": name, "instructions": instructions, "output_type": output_type, "tools": tools}
        if self.model:
            kwargs["model"] = self.model
        agent = Agent(**kwargs)
        result = Runner.run_sync(agent, prompt, max_turns=16)
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
        instructions += "\n\nReturn the required ResearchPackage. Use live web research. Do not draft the article."
        out: ResearchPackage = self._run(
            name="Financial Writing Researcher", instructions=instructions, output_type=ResearchPackage, web=True,
            prompt=f"USER TASK:\n{state.contract.prompt}\n\nSOURCE REFS:\n{state.contract.source_refs}\n",
        )
        state.working["research"] = out.model_dump(mode="json")
        state.set_gate("research_output", GateStatus.PASS, [f"evidence_items={len(out.evidence_ledger)}", f"universe={len(out.universe)}"])
        return state

    def _execute_research_audit(self, state: WritingState) -> WritingState:
        instructions = load_reference("audit.md") + "\n\nAudit only the research package against the research and knowledge reference rules."
        out: GateDecision = self._run(name="Financial Writing Research Auditor", instructions=instructions, output_type=GateDecision, prompt=_state_context(state))
        state.set_gate("research_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects))
        return state

    def _execute_editorial(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("style.md") + "\n\n" + load_reference("structure_patterns.md")
        instructions += (
            "\n\nBuild shared TopicDNA and separate applicable mode plans. FINANCE_DEEP must use MATERIAL_COMPLETE with explicit completeness_obligations and no core_contradictions/compression_candidates. "
            "FINANCE_BROAD must use SELECTIVE_TRAFFIC with 1-3 core_contradictions. Do not draft body text."
        )
        out: EditorialPlan = self._run(name="Financial Writing Editorial Architect", instructions=instructions, output_type=EditorialPlan, prompt=_state_context(state))
        state.working["editorial_plan"] = out.model_dump(mode="json")
        state.set_gate("editorial_plan", GateStatus.PASS, ["shared TopicDNA", "mode-specific editorial contracts"])
        return state

    def _execute_title(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("platforms.md")
        instructions += (
            "\n\nUse current web/search evidence for WeChat search-intent terms before final selection. Generate 8-12 candidates per applicable mode. "
            "Each candidate must state a cross-finance click reason, current search term(s) and real evidence refs. Do not invent search volume."
        )
        out: HeadlinePackage = self._run(name="Financial Writing Headline Engine", instructions=instructions, output_type=HeadlinePackage, web=True, prompt=_state_context(state))
        state.working["headlines"] = out.model_dump(mode="json")
        state.set_gate("title_audit", GateStatus.PASS, ["headline candidate/search evidence package"])
        return state

    def _execute_draft(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("style.md") + "\n\n" + load_reference("delivery.md")
        instructions += (
            "\n\nDraft every applicable formal article in Simplified Chinese. Use numbered hierarchy frequently when it clarifies logic. Never use tables. "
            "FINANCE_DEEP must discharge every completeness_obligation. FINANCE_BROAD may use its selective traffic route. "
            "Use explicit **bold** for key terms, key data and key judgment sentences; provide at least three exact skim_path_anchors per article. "
            "The title + H1s + bold spans must reconstruct the main line. Return risk text only in risk_disclaimer."
        )
        out: DraftPackage = self._run(name="Financial Writing Writer", instructions=instructions, output_type=DraftPackage, prompt=_state_context(state))
        state.working["draft"] = out.model_dump(mode="json")
        state.set_gate("draft_output", GateStatus.PASS, ["structured draft package frozen"])
        return state

    def _execute_editorial_audit(self, state: WritingState) -> WritingState:
        hook_instructions = load_reference("hooks.md") + "\n\nAct as an independent Hook Judge. Audit the frozen selected title, actual first three complete sentences, H1s and representative paragraph transitions."
        hook_out: HookAuditDecision = self._run(name="Financial Writing Hook Judge", instructions=hook_instructions, output_type=HookAuditDecision, prompt=_state_context(state))
        state.set_gate("hook_audit", GateStatus(hook_out.status), hook_out.evidence, "; ".join(hook_out.revision_notes))
        state.working["hook_audit"] = hook_out.model_dump(mode="json")

        voice_instructions = load_reference("style.md") + "\n\nAct as an independent Human Voice Judge. Audit the frozen draft for human reasoning trajectory, reader dialogue, narrative flow, rhythm, repetition, template fingerprints and claim-strength control."
        voice_out: StyleAuditDecision = self._run(name="Financial Writing Human Voice Judge", instructions=voice_instructions, output_type=StyleAuditDecision, prompt=_state_context(state))
        state.set_gate("style_audit", GateStatus(voice_out.status), voice_out.evidence, "; ".join(voice_out.detected_patterns + voice_out.transition_findings + voice_out.revision_notes))
        state.working["style_audit"] = voice_out.model_dump(mode="json")

        if hook_out.status != "PASS" or voice_out.status != "PASS":
            evidence = hook_out.evidence + voice_out.evidence
            notes = "dedicated hook/human-voice gate requires draft revision"
            state.set_gate("editorial_audit", GateStatus.REVISE, evidence, notes)
            state.working["revise_target"] = "DRAFT"
            return state

        instructions = load_reference("audit.md") + "\n\nAudit the frozen draft for evidence, FINANCE_DEEP completeness / FINANCE_BROAD legal compression, reasoning, skim-path coherence and compliance. Dedicated Hook and Human Voice gates already passed."
        out: GateDecision = self._run(name="Financial Writing Editorial Auditor", instructions=instructions, output_type=GateDecision, prompt=_state_context(state))
        state.set_gate("editorial_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects))
        if out.revision_target:
            state.working["revise_target"] = out.revision_target
        return state

    def _execute_final_audit(self, state: WritingState) -> WritingState:
        instructions = load_reference("audit.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("style.md")
        instructions += "\n\nPerform final red-team review of frozen Word content plus recorded mechanical audit. Do not audit or request images; Financial Writing has no visual workflow."
        out: GateDecision = self._run(name="Financial Writing Final Auditor", instructions=instructions, output_type=GateDecision, prompt=_state_context(state))
        state.set_gate("final_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        if out.revision_target:
            state.working["final_revise_target"] = out.revision_target
        if out.status == "PASS":
            finalize_audit_artifact(state)
        return state


def build_openai_executors(*, model: str | None = None) -> dict[Stage, OpenAIStageExecutor]:
    return {stage: OpenAIStageExecutor(stage, model=model) for stage in {Stage.RESEARCH, Stage.RESEARCH_AUDIT, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT, Stage.EDITORIAL_AUDIT, Stage.FINAL_AUDIT}}
