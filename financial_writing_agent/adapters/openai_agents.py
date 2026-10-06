"""Optional OpenAI Agents SDK implementation for high-judgment stages.

The Python state machine remains authoritative. The SDK is used only inside a stage;
it cannot skip, insert, or complete stages on its own.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from ..models import ArtifactKind, GateStatus, Stage, WritingState
from ..schemas import DraftPackage, EditorialPlan, GateDecision, HeadlinePackage, ResearchPackage
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
    """One executor instance handles exactly one deterministic runtime stage."""

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
        instructions = load_reference("research.md") + "\n\nReturn the required ResearchPackage. Use live web research. Do not draft the article."
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
        instructions = load_reference("audit.md") + "\n\nAudit only the research package against references/research.md."
        out: GateDecision = self._run(
            name="Financial Writing Research Auditor",
            instructions=instructions,
            output_type=GateDecision,
            web=False,
            prompt=_state_context(state),
        )
        status = GateStatus(out.status)
        state.set_gate("research_audit", status, out.evidence, "; ".join(out.defects))
        return state

    def _execute_editorial(self, state: WritingState) -> WritingState:
        instructions = (
            load_reference("editorial.md")
            + "\n\n"
            + load_reference("structure_patterns.md")
            + "\n\nBuild TopicDNA and multiple candidate structures. Do not draft body text."
        )
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
        instructions = load_reference("editorial.md") + "\n\nGenerate 8-12 candidates per applicable mode and select only after judging finance relevance, factual support, information gap, and cognitive load."
        out: HeadlinePackage = self._run(
            name="Financial Writing Headline Engine",
            instructions=instructions,
            output_type=HeadlinePackage,
            web=False,
            prompt=_state_context(state),
        )
        state.working["headlines"] = out.model_dump(mode="json")
        applicable = []
        if state.contract.distribution_mode.value in {"FINANCE_DEEP", "DUAL"}:
            applicable.append(bool(out.finance_deep_selected))
        if state.contract.distribution_mode.value in {"FINANCE_BROAD", "DUAL"}:
            applicable.append(bool(out.finance_broad_selected))
        state.set_gate("title_audit", GateStatus.PASS if all(applicable) else GateStatus.REVISE, [f"applicable_modes={len(applicable)}"])
        return state

    def _execute_draft(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\nDraft the applicable article mode(s). Preserve the core reasoning chain and include a topic-specific risk/disclaimer H1 at the end."
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
        instructions = load_reference("audit.md") + "\n\nAudit the frozen draft for evidence support, reasoning continuity, hook兑现, information density, platform fit and compliance."
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
        instructions = load_reference("audit.md") + "\n\nPerform final red-team review of the frozen article content plus recorded mechanical audit."
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
    """High-judgment stages only. DELIVERY/MECHANICAL_AUDIT stay deterministic."""
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
