"""Optional OpenAI Agents SDK implementation for high-judgment stages.

The Python state machine remains authoritative. The SDK is used only inside a stage;
it cannot skip, insert, or complete stages on its own. Creative image generation and
connected-store I/O are orchestrated by the ChatGPT/MCP plugin path, not this adapter.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ..models import ContentMode, GateStatus, Stage, WritingState
from ..schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, ResearchPackage, StyleAuditDecision
from .deterministic import finalize_audit_artifact


class OpenAIAgentsUnavailable(RuntimeError):
    pass


def require_sdk():
    try:
        from agents import Agent, Runner, WebSearchTool  # type: ignore
    except ImportError as exc:  # pragma: no cover
        raise OpenAIAgentsUnavailable(
            "Install optional dependency with: pip install 'financial-writing-agent[openai]'"
        ) from exc
    return Agent, Runner, WebSearchTool


def load_reference(name: str) -> str:
    root = Path(__file__).resolve().parents[2]
    return (root / "references" / name).read_text(encoding="utf-8")


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
        self.model = model or os.getenv("FINANCIAL_WRITING_MODEL", "gpt-6.1-sol")

    def _run(self, *, name: str, instructions: str, output_type: type[Any], prompt: str, web: bool = False):
        Agent, Runner, WebSearchTool = require_sdk()
        tools = [WebSearchTool(search_context_size="high", external_web_access=True)] if web else []
        agent = Agent(name=name, model=self.model, instructions=instructions, output_type=output_type, tools=tools)
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
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md") + "\n\nVerify current WeChat sticker-post limits/mechanics with live web evidence and preserve sources for the later PlatformConstraintSnapshot."
        instructions += "\n\nReturn the required ResearchPackage. Use live web research. Do not draft the article."
        out: ResearchPackage = self._run(
            name="Financial Writing Researcher",
            instructions=instructions,
            output_type=ResearchPackage,
            web=True,
            prompt=f"USER TASK:\n{state.contract.prompt}\n\nSOURCE REFS:\n{state.contract.source_refs}\n",
        )
        state.working["research"] = out.model_dump(mode="json")
        state.set_gate("research_output", GateStatus.PASS, [f"evidence_items={len(out.evidence_ledger)}", f"universe={len(out.universe)}"])
        return state

    def _execute_research_audit(self, state: WritingState) -> WritingState:
        instructions = load_reference("audit.md") + "\n\nAudit only the research package against references/research.md and references/knowledge.md."
        out: GateDecision = self._run(
            name="Financial Writing Research Auditor",
            instructions=instructions,
            output_type=GateDecision,
            web=False,
            prompt=_state_context(state),
        )
        state.set_gate("research_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects))
        return state

    def _execute_editorial(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("style.md") + "\n\n" + load_reference("structure_patterns.md")
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md") + "\n\nDesign a concise image-first sticker-post structure; do not force long-article H1 architecture."
        instructions += "\n\nBuild TopicDNA and multiple candidate structures. Do not draft body text."
        out: EditorialPlan = self._run(
            name="Financial Writing Editorial Architect",
            instructions=instructions,
            output_type=EditorialPlan,
            web=False,
            prompt=_state_context(state),
        )
        state.working["editorial_plan"] = out.model_dump(mode="json")
        state.set_gate("editorial_plan", GateStatus.PASS, ["TopicDNA", f"structures={len(out.candidates)}"])
        return state

    def _execute_title(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("style.md")
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md") + "\n\nGenerate sticker-post title candidates that complement the image hook. Do not assume remembered platform character limits; use the verified research context."
        else:
            instructions += "\n\nGenerate 8-12 candidates per applicable mode and select after judging finance relevance, factual support, information gap, cognitive load and extreme-language risk."
        out: HeadlinePackage = self._run(
            name="Financial Writing Headline Engine",
            instructions=instructions,
            output_type=HeadlinePackage,
            web=False,
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
        state.set_gate("title_audit", GateStatus.PASS if applicable and all(applicable) else GateStatus.REVISE, [f"applicable_modes={len(applicable)}"])
        return state

    def _execute_draft(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("style.md") + "\n\n" + load_reference("delivery.md")
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md") + "\n\nReturn only wechat_sticker_post in DraftPackage. Its PlatformConstraintSnapshot must come from current research evidence; keep copy concise/useful, include an interaction prompt when appropriate, and include a compact information-dense risk disclaimer."
        else:
            instructions += "\n\nDraft the applicable article mode(s). Use Simplified Chinese, continuous logically connected prose and include a topic-specific risk/disclaimer H1 at the end."
        out: DraftPackage = self._run(
            name="Financial Writing Writer",
            instructions=instructions,
            output_type=DraftPackage,
            web=False,
            prompt=_state_context(state),
        )
        state.working["draft"] = out.model_dump(mode="json")
        state.set_gate("draft_output", GateStatus.PASS, ["structured draft package frozen"])
        return state

    def _execute_editorial_audit(self, state: WritingState) -> WritingState:
        style_instructions = load_reference("style.md") + "\n\nAct as a dedicated style judge independent from the writer. Audit only AI-template fingerprints, paragraph/section transitions, repetitive rhetorical constructions, rhythm problems, empty bridges and unsupported extreme/superlative language."
        style_out: StyleAuditDecision = self._run(
            name="Financial Writing Anti-AI Style Judge",
            instructions=style_instructions,
            output_type=StyleAuditDecision,
            web=False,
            prompt=_state_context(state),
        )
        state.set_gate("style_audit", GateStatus(style_out.status), style_out.evidence, "; ".join(style_out.detected_patterns + style_out.transition_findings + style_out.extreme_language_findings + style_out.revision_notes))
        state.working["style_audit"] = style_out.model_dump(mode="json")
        if style_out.status != "PASS":
            state.set_gate("editorial_audit", GateStatus.REVISE, style_out.evidence, "style audit requires draft revision")
            state.working["revise_target"] = "DRAFT"
            return state

        instructions = load_reference("audit.md") + "\n\nAudit the frozen draft for evidence, reasoning continuity, hook payoff, information density, platform fit and compliance. The dedicated style gate has already passed; do not replace it with writer self-assessment."
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md")
        out: GateDecision = self._run(
            name="Financial Writing Editorial Auditor",
            instructions=instructions,
            output_type=GateDecision,
            web=False,
            prompt=_state_context(state),
        )
        state.set_gate("editorial_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects))
        if out.revision_target:
            state.working["revise_target"] = out.revision_target
        return state

    def _execute_final_audit(self, state: WritingState) -> WritingState:
        instructions = load_reference("audit.md") + "\n\n" + load_reference("style.md") + "\n\n" + load_reference("visuals.md")
        if state.contract.content_mode == ContentMode.WECHAT_STICKER_POST:
            instructions += "\n\n" + load_reference("platforms.md")
        instructions += "\n\nPerform final red-team review of frozen content plus recorded mechanical/visual audit."
        out: GateDecision = self._run(
            name="Financial Writing Final Auditor",
            instructions=instructions,
            output_type=GateDecision,
            web=False,
            prompt=_state_context(state),
        )
        state.set_gate("final_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        if out.revision_target:
            state.working["final_revise_target"] = out.revision_target
        if out.status == "PASS":
            finalize_audit_artifact(state)
        return state


def build_openai_executors(*, model: str | None = None) -> dict[Stage, OpenAIStageExecutor]:
    return {
        s: OpenAIStageExecutor(s, model=model)
        for s in {
            Stage.RESEARCH,
            Stage.RESEARCH_AUDIT,
            Stage.EDITORIAL,
            Stage.TITLE,
            Stage.DRAFT,
            Stage.EDITORIAL_AUDIT,
            Stage.FINAL_AUDIT,
        }
    }
