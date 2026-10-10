"""Optional OpenAI Agents SDK implementation for high-judgment stages.

The Python state machine remains authoritative. The SDK is used only inside a stage;
it cannot skip, insert, recover or complete stages on its own.
"""
from __future__ import annotations

import json
import os
from typing import Any

from ..checks import analyze_template_scaffolding, check_deep_company_grounding, payload_text
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

    def _run(
        self,
        *,
        state: WritingState,
        name: str,
        instructions: str,
        output_type: type[Any],
        prompt: str,
        web: bool = False,
        audit_author_identity: str | None = None,
    ):
        Agent, RunConfig, Runner, WebSearchTool = require_sdk()
        tools = [WebSearchTool(search_context_size="high", external_web_access=True)] if web else []
        if audit_author_identity is not None:
            execution_ref = f"{state.contract.task_id}:{self.stage.value}:{name}"
            instructions += (
                "\n\nAUDIT PROVENANCE CONTRACT: this is a separate SDK judge run, not writer self-review. "
                f"Set provenance.assurance='INDEPENDENT_EXECUTOR', provenance.reviewer_identity={name!r}, "
                f"provenance.author_identity={audit_author_identity!r}, provenance.execution_ref={execution_ref!r}. "
                "Do not claim provider-isolated assurance; this field only proves a separate stage-bound executor run."
            )
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
                "executor_name": name,
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
            "For company/theme topics, first enumerate every material economic/value-chain class, then build a broad A-share recall set from at least two materially different recall sources before deep-diving familiar names. "
            "Populate universe_coverage class-by-class, including included companies, explicit exclusions/unresolved candidates and stop reason. Do not call coverage SATURATED merely because a second search found no new facts about the same two or three companies. "
            "Each universe company needs value_chain_class and materiality. MATERIAL means omission from FINANCE_DEEP could change a financially literate reader's judgment; SECONDARY may be grouped; REFERENCE_ONLY is context only. "
            "Set market_explanation_scope=REQUIRED only when price action, theme/market selection, leadership, continuation/reversal or another cross-sectional price-formation question is materially part of the task. A company universe by itself is not enough."
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
        instructions = load_reference("audit.md") + "\n\n" + load_reference("research.md") + "\n\n" + load_reference("market_explanation.md")
        instructions += (
            "\n\nAudit only the research package. If REVISE or FAIL, revision_target must be RESEARCH. "
            "Red-team Universe recall: compare the declared value-chain classes against the topic's economic chain and test whether obvious A-share peers/classes are silently missing. A handful of deeply researched familiar companies is not complete universe coverage. "
            "If any material class/company is omitted without an explicit evidence-bounded exclusion, REVISE."
        )
        out: GateDecision = self._run(
            state=state,
            name="Financial Writing Research Auditor",
            instructions=instructions,
            output_type=GateDecision,
            prompt=_state_context(state),
            audit_author_identity="Financial Writing Researcher",
        )
        state.set_gate("research_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        state.working["research_audit"] = out.model_dump(mode="json")
        if out.revision_target:
            state.working["research_revise_target"] = out.revision_target
        return state

    def _execute_editorial(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("style.md")
        instructions += (
            "\n\nBuild shared TopicDNA and at least two topic-specific candidate structures per applicable mode before selecting one. "
            "FINANCE_DEEP must use MATERIAL_COMPLETE with explicit completeness_obligations and no core_contradictions/compression_candidates. It is not a 'pick representative names' version. "
            "For FINANCE_DEEP, populate company_coverage_obligations from the research universe: every MATERIAL company must be named in the article; SECONDARY names can be grouped by value-chain class if doing so preserves the relevant comparison. "
            "Any validation/monitoring/realization section must connect its signals back to affected stocks/classes instead of ending with a generic industry checklist. "
            "FINANCE_BROAD may use SELECTIVE_TRAFFIC with 1-3 core_contradictions. Do not draft body text and do not select from a canned structure library."
        )
        out: EditorialPlan = self._run(state=state, name="Financial Writing Editorial Architect", instructions=instructions, output_type=EditorialPlan, prompt=_state_context(state))
        state.working["editorial_plan"] = out.model_dump(mode="json")
        state.set_gate("editorial_plan", GateStatus.PASS, ["shared TopicDNA", "topic-specific mode structures", "deep company coverage obligations"])
        return state

    def _execute_title(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("platforms.md")
        instructions += (
            "\n\nUse current web/search evidence for WeChat search-intent terms before final selection. Generate 8-12 candidates per applicable mode. "
            "The pool must use at least five genuinely different angle_family values; changing synonyms inside one 'X不在Y/真正看Z/这次看什么' mold is not diversity. "
            "Each candidate must state angle_family, intended reader, click reason, promised payoff, current search term(s) and real evidence refs. "
            "Prefer titles that contain a concrete event/change plus a financially consequential distinction. Generic suspense, empty colloquial questions and reusable formula titles fail unless account evidence specifically supports them. "
            "Broader cross-industry finance relevance is optional and must never be forced. Do not invent search volume."
        )
        out: HeadlinePackage = self._run(state=state, name="Financial Writing Headline Engine", instructions=instructions, output_type=HeadlinePackage, web=True, prompt=_state_context(state))
        state.working["headlines"] = out.model_dump(mode="json")
        state.set_gate("title_audit", GateStatus.PASS, ["headline reader-fit/search-evidence package", "angle-family diversity schema passed"])
        return state

    def _execute_draft(self, state: WritingState) -> WritingState:
        instructions = load_reference("editorial.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("style.md") + "\n\n" + load_reference("delivery.md")
        instructions += (
            "\n\nDraft every applicable formal article in Simplified Chinese. Never use tables. "
            "Use H1s as clear macro navigation. Add H2/H3 numbering only when the current section contains genuine parallel analytical branches, categories or steps that materially improve comprehension. Never create lower-level numbering merely because the article is long, covers many companies, has several H1s, or to satisfy a visual quota. Sequential reasoning may remain continuous prose. "
            "FINANCE_DEEP must discharge every completeness_obligation and every company_coverage_obligation. It must name every MATERIAL company from research and may group SECONDARY companies only when the class-level treatment still explains why they matter. "
            "If a section tells the reader what to validate/watch next, map each material signal to the affected named stocks or value-chain class; do not end with an industry-only checklist after discussing stocks elsewhere. "
            "Do not repeatedly stage the argument with formulae such as '真正的X不是Y而是Z', '如果只看…', '这正是…', '最值得写清楚…'. Use them only when the exact sentence earns its place. "
            "FINANCE_BROAD may use its selective traffic route. Use explicit **bold** for key terms, key data and key judgment sentences; provide at least three exact skim_path_anchors per article. Return risk text only in risk_disclaimer."
        )
        out: DraftPackage = self._run(state=state, name="Financial Writing Writer", instructions=instructions, output_type=DraftPackage, prompt=_state_context(state))
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

        hook_instructions = load_reference("hooks.md") + (
            "\n\nAct as an independent Reader Funnel Judge. Audit the frozen selected title, the whole candidate pool's strategy diversity, actual first three complete sentences, H1s, representative paragraph transitions and final substantive payoff. "
            "Reject a title pool that is mostly one rhetorical mold with synonym swaps even if strings are unique. Reject a selected title whose curiosity comes mainly from vague '真正/这次/该看什么' staging rather than concrete information value. "
            "Use revision_target=TITLE only when the selected title/search promise itself must change; otherwise use DRAFT."
        )
        hook_out: HookAuditDecision = self._run(
            state=state,
            name="Financial Writing Reader Funnel Judge",
            instructions=hook_instructions,
            output_type=HookAuditDecision,
            prompt=_state_context(state),
            audit_author_identity="Financial Writing Headline Engine / Financial Writing Writer",
        )
        state.set_gate("hook_audit", GateStatus(hook_out.status), hook_out.evidence, "; ".join(hook_out.revision_notes))
        state.working["hook_audit"] = hook_out.model_dump(mode="json")

        prose_instructions = load_reference("style.md") + (
            "\n\nAct as an independent Natural Authorial Prose Judge. Audit the frozen draft against the exact nine-part rubric. "
            "The state includes template_signal_report from a deterministic cluster detector. One normal phrase is not a defect, but a requires_revise=true report is mandatory evidence that template_redundancy_control cannot PASS until the repeated rhetorical scaffolding is rewritten. "
            "If REVISE, revision_target must be DRAFT."
        )
        prose_out: StyleAuditDecision = self._run(
            state=state,
            name="Financial Writing Authorial Prose Judge",
            instructions=prose_instructions,
            output_type=StyleAuditDecision,
            prompt=_state_context(state),
            audit_author_identity="Financial Writing Writer",
        )
        template_revise = any(report.get("requires_revise") for report in template_reports.values())
        prose_status = "REVISE" if template_revise else prose_out.status
        prose_notes = list(prose_out.detected_patterns + prose_out.reasoning_findings + prose_out.revision_notes)
        if template_revise:
            prose_notes.append(f"deterministic template cluster requires revision: {json.dumps(template_reports, ensure_ascii=False)}")
        state.set_gate("style_audit", GateStatus(prose_status), prose_out.evidence, "; ".join(prose_notes))
        state.working["style_audit"] = {**prose_out.model_dump(mode="json"), "effective_status": prose_status, "deterministic_template_guard": template_reports}

        if hook_out.status != "PASS" or prose_status != "PASS":
            target = "TITLE" if hook_out.status == "REVISE" and hook_out.revision_target == "TITLE" else "DRAFT"
            evidence = hook_out.evidence + prose_out.evidence
            state.set_gate("editorial_audit", GateStatus.REVISE, evidence, "dedicated Reader Funnel/Authorial Prose gate requires revision")
            state.working["revise_target"] = target
            return state

        instructions = load_reference("audit.md") + (
            "\n\nAudit the frozen draft for evidence, FINANCE_DEEP completeness / FINANCE_BROAD legal compression, universe-to-article company coverage, stock-grounded validation/monitoring sections, semantically justified navigation, market-explanation discipline when activated, skim-path coherence and compliance. "
            "FINANCE_DEEP is not allowed to call itself complete while silently omitting MATERIAL companies/classes or replacing company coverage with a few representative names. "
            "Dedicated Reader Funnel and Authorial Prose gates already passed. If an upstream defect is discovered, use the earliest correct revision_target among RESEARCH, EDITORIAL, TITLE or DRAFT."
        )
        out: GateDecision = self._run(
            state=state,
            name="Financial Writing Editorial Auditor",
            instructions=instructions,
            output_type=GateDecision,
            prompt=_state_context(state),
            audit_author_identity="Financial Writing Writer",
        )
        state.set_gate("editorial_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        state.working["editorial_audit"] = out.model_dump(mode="json")
        if out.revision_target:
            state.working["revise_target"] = out.revision_target
        return state

    def _execute_final_audit(self, state: WritingState) -> WritingState:
        instructions = load_reference("audit.md") + "\n\n" + load_reference("hooks.md") + "\n\n" + load_reference("style.md")
        instructions += (
            "\n\nPerform final red-team review of frozen Word content plus recorded mechanical audit. Reconfirm universe completeness, MATERIAL-company appearance, stock-grounded monitoring/validation sections, title-pool strategy diversity, semantically justified navigation and template-cluster status. "
            "Do not audit or request images; Financial Writing has no visual workflow. If a defect is upstream, use the earliest correct revision_target among RESEARCH, EDITORIAL, TITLE, DRAFT or DELIVERY."
        )
        out: GateDecision = self._run(
            state=state,
            name="Financial Writing Final Auditor",
            instructions=instructions,
            output_type=GateDecision,
            prompt=_state_context(state),
            audit_author_identity="Financial Writing Writer / Delivery Executor",
        )
        state.set_gate("final_audit", GateStatus(out.status), out.evidence, "; ".join(out.defects + out.remaining_boundaries))
        state.working["final_audit"] = out.model_dump(mode="json")
        if out.revision_target:
            state.working["final_revise_target"] = out.revision_target
        if out.status == "PASS":
            finalize_audit_artifact(state)
        return state


def build_openai_executors(*, model: str | None = None) -> dict[Stage, OpenAIStageExecutor]:
    return {stage: OpenAIStageExecutor(stage, model=model) for stage in {Stage.RESEARCH, Stage.RESEARCH_AUDIT, Stage.EDITORIAL, Stage.TITLE, Stage.DRAFT, Stage.EDITORIAL_AUDIT, Stage.FINAL_AUDIT}}
