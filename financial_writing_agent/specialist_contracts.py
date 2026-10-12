from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .models import Stage


@dataclass(frozen=True)
class SpecialistContract:
    specialist_id: str
    display_name: str
    stage: Stage
    output_schema: str
    reference_names: tuple[str, ...]
    working_keys: tuple[str, ...]
    gate_keys: tuple[str, ...]
    web_access: bool
    author_identity: str | None
    execution_instruction: str
    artifact_metadata_access: bool = False
    forbidden_actions: tuple[str, ...] = (
        "change or invent workflow stages",
        "silently repair upstream evidence while certifying the current stage",
        "promote chat/self-review into stronger assurance",
        "change durable business rules from one execution",
    )


SPECIALIST_CONTRACTS: dict[str, SpecialistContract] = {
    "researcher": SpecialistContract(
        specialist_id="researcher",
        display_name="Financial Writing Researcher",
        stage=Stage.RESEARCH,
        output_schema="ResearchPackage",
        reference_names=("research.md", "knowledge.md", "market_explanation.md"),
        working_keys=("knowledge_context_refs", "knowledge_context_notes"),
        gate_keys=("runtime_initialized",),
        web_access=True,
        author_identity=None,
        execution_instruction=(
            "Research the user task with current web evidence where required and return only the typed ResearchPackage. "
            "Do not draft the article. Treat the loaded Research/Knowledge/Market Explanation references as the business-semantic authority."
        ),
    ),
    "research_auditor": SpecialistContract(
        specialist_id="research_auditor",
        display_name="Financial Writing Research Auditor",
        stage=Stage.RESEARCH_AUDIT,
        output_schema="GateDecision",
        reference_names=("audit.md", "research.md", "market_explanation.md"),
        working_keys=("research",),
        gate_keys=("research_output",),
        web_access=False,
        author_identity="Financial Writing Researcher",
        execution_instruction=(
            "Audit only the frozen ResearchPackage under the loaded Audit/Research contracts. Do not repair it in place. "
            "Return a typed GateDecision; any non-PASS route must point to the workflow-authorized upstream repair target."
        ),
    ),
    "editorial_architect": SpecialistContract(
        specialist_id="editorial_architect",
        display_name="Financial Writing Editorial Architect",
        stage=Stage.EDITORIAL,
        output_schema="EditorialPlan",
        reference_names=("editorial.md", "hooks.md", "style.md"),
        working_keys=("research", "research_audit"),
        gate_keys=("research_output", "research_audit"),
        web_access=False,
        author_identity=None,
        execution_instruction=(
            "Transform the audited research into the typed EditorialPlan only. Do not draft body prose or alter research evidence. "
            "The loaded Editorial/Reader Funnel/Style references own coverage, structure and handoff semantics."
        ),
    ),
    "headline_engine": SpecialistContract(
        specialist_id="headline_engine",
        display_name="Financial Writing Headline Engine",
        stage=Stage.TITLE,
        output_schema="HeadlinePackage",
        reference_names=("editorial.md", "hooks.md", "platforms.md"),
        working_keys=("research", "editorial_plan"),
        gate_keys=("research_audit", "editorial_plan"),
        web_access=True,
        author_identity=None,
        execution_instruction=(
            "Return only the typed HeadlinePackage for the applicable distribution mode(s). Use current web/search evidence for the "
            "search-intent fields required by the loaded Reader Funnel/Platform contracts. Do not rewrite research or editorial state."
        ),
    ),
    "writer": SpecialistContract(
        specialist_id="writer",
        display_name="Financial Writing Writer",
        stage=Stage.DRAFT,
        output_schema="DraftPackage",
        reference_names=("editorial.md", "hooks.md", "style.md", "delivery.md"),
        working_keys=("research", "editorial_plan", "headlines"),
        gate_keys=("research_audit", "editorial_plan", "title_audit"),
        web_access=False,
        author_identity=None,
        execution_instruction=(
            "Write the applicable formal article payload(s) and return only the typed DraftPackage. Use the frozen research, editorial "
            "plan and selected headlines; do not alter upstream facts, coverage obligations or workflow state."
        ),
    ),
    "reader_funnel_judge": SpecialistContract(
        specialist_id="reader_funnel_judge",
        display_name="Financial Writing Reader Funnel Judge",
        stage=Stage.EDITORIAL_AUDIT,
        output_schema="HookAuditDecision",
        reference_names=("hooks.md",),
        working_keys=("research", "editorial_plan", "headlines", "draft"),
        gate_keys=("title_audit", "draft_output"),
        web_access=False,
        author_identity="Financial Writing Headline Engine / Financial Writing Writer",
        execution_instruction=(
            "Judge only the Reader Funnel dimensions of the frozen title/draft and return HookAuditDecision. Do not rewrite the text, "
            "substitute for Authorial Prose/General Editorial judgment, or change upstream state."
        ),
    ),
    "authorial_prose_judge": SpecialistContract(
        specialist_id="authorial_prose_judge",
        display_name="Financial Writing Authorial Prose Judge",
        stage=Stage.EDITORIAL_AUDIT,
        output_schema="StyleAuditDecision",
        reference_names=("style.md",),
        working_keys=("research", "editorial_plan", "headlines", "draft", "template_signal_report"),
        gate_keys=("draft_output",),
        web_access=False,
        author_identity="Financial Writing Writer",
        execution_instruction=(
            "Judge only the Natural Authorial Prose contract on the frozen draft, using the supplied deterministic template_signal_report "
            "as evidence. Return StyleAuditDecision and do not rewrite the draft during the audit."
        ),
    ),
    "general_editorial_judge": SpecialistContract(
        specialist_id="general_editorial_judge",
        display_name="Financial Writing Editorial Auditor",
        stage=Stage.EDITORIAL_AUDIT,
        output_schema="GateDecision",
        reference_names=("audit.md",),
        working_keys=(
            "research", "editorial_plan", "headlines", "draft", "hook_audit", "style_audit", "template_signal_report"
        ),
        gate_keys=("research_audit", "title_audit", "draft_output", "hook_audit", "style_audit"),
        web_access=False,
        author_identity="Financial Writing Writer",
        execution_instruction=(
            "Perform only the General Editorial audit after the dedicated Reader Funnel and Authorial Prose results supplied in context. "
            "Do not erase or relabel those dedicated decisions. Return GateDecision and route defects to the earliest workflow-authorized repair stage."
        ),
    ),
    "final_auditor": SpecialistContract(
        specialist_id="final_auditor",
        display_name="Financial Writing Final Auditor",
        stage=Stage.FINAL_AUDIT,
        output_schema="GateDecision",
        reference_names=("audit.md", "hooks.md", "style.md"),
        working_keys=(
            "research", "editorial_plan", "headlines", "draft", "research_audit", "hook_audit", "style_audit",
            "editorial_audit", "template_signal_report", "render_manifest", "knowledge_writeback_refs", "knowledge_writeback_notes"
        ),
        gate_keys=(
            "research_output", "research_audit", "editorial_plan", "title_audit", "draft_output", "hook_audit", "style_audit",
            "editorial_audit", "delivery_output", "mechanical_audit", "knowledge_sync"
        ),
        web_access=False,
        author_identity="Financial Writing Writer / Delivery Executor",
        artifact_metadata_access=True,
        execution_instruction=(
            "Perform a read-only final red-team judgment over the frozen publication source, safe artifact metadata and recorded "
            "audit/mechanical evidence. Return GateDecision; do not repair content in place or upgrade assurance beyond the actual executor evidence."
        ),
    ),
}


def specialist_contract(specialist_id: str) -> SpecialistContract:
    try:
        return SPECIALIST_CONTRACTS[specialist_id]
    except KeyError as exc:
        raise ValueError(f"unknown specialist contract: {specialist_id}") from exc


def projected_working(state_working: dict, specialist_id: str) -> dict:
    contract = specialist_contract(specialist_id)
    return {key: state_working[key] for key in contract.working_keys if key in state_working}


def projected_gates(state_gates: dict, specialist_id: str) -> dict:
    contract = specialist_contract(specialist_id)
    return {key: state_gates[key] for key in contract.gate_keys if key in state_gates}


def projected_artifacts(state_artifacts: dict, specialist_id: str) -> dict:
    """Expose only non-path artifact identity/availability to authorized specialists."""
    contract = specialist_contract(specialist_id)
    if not contract.artifact_metadata_access:
        return {}
    return {
        kind.value: {
            "file_name": Path(artifact.path).name,
            "exists": artifact.exists,
            "sha256": artifact.sha256,
        }
        for kind, artifact in state_artifacts.items()
    }
