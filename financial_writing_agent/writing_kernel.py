from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Callable, Mapping
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .models import DistributionMode, Stage, TaskContract
from .schemas import PlatformInteractionPack, ResearchPackage
from .task_requirements import TaskRequirement
from .story_quality import AuditStatus, PublicationFitness
from .workflow_spec import pass_target_name, require_revision_target


class WritingPass(str, Enum):
    KNOWLEDGE_RECALL = "KNOWLEDGE_RECALL"
    RESEARCH_DISCOVERY = "RESEARCH_DISCOVERY"
    RESEARCH_ADVERSARIAL = "RESEARCH_ADVERSARIAL"
    PRIVATE_RESEARCH_SYNTHESIS = "PRIVATE_RESEARCH_SYNTHESIS"
    THESIS_ADJUDICATION = "THESIS_ADJUDICATION"
    STORY_ARCHITECTURE = "STORY_ARCHITECTURE"
    HEADLINE_ADJUDICATION = "HEADLINE_ADJUDICATION"
    DRAFT_GENERATION = "DRAFT_GENERATION"
    READER_RETENTION_AUDIT = "READER_RETENTION_AUDIT"
    EDITORIAL_TRIM = "EDITORIAL_TRIM"
    ORIGINALITY_AUDIT = "ORIGINALITY_AUDIT"
    FACT_INTEGRITY_AUDIT = "FACT_INTEGRITY_AUDIT"
    STYLE_AUDIT = "STYLE_AUDIT"
    FINAL_SYNTHESIS = "FINAL_SYNTHESIS"
    PLATFORM_INTERACTION_ADAPTATION = "PLATFORM_INTERACTION_ADAPTATION"
    PLATFORM_INTERACTION_AUDIT = "PLATFORM_INTERACTION_AUDIT"


@dataclass(frozen=True)
class PassContract:
    purpose: str
    required_inputs: tuple[str, ...]
    forbidden_jobs: tuple[str, ...]
    outputs: tuple[str, ...]


PASS_CONTRACTS: dict[WritingPass, PassContract] = {
    WritingPass.KNOWLEDGE_RECALL: PassContract(
        purpose="recover prior structural, method and company cognition without treating memory as current fact",
        required_inputs=("topic_or_task", "knowledge_sources"),
        forbidden_jobs=("select final thesis", "draft publication prose"),
        outputs=("recalled_knowledge", "revalidation_queue"),
    ),
    WritingPass.RESEARCH_DISCOVERY: PassContract(
        purpose="map the full material value chain, company universe, chronology and evidence before thesis convergence",
        required_inputs=("topic", "recalled_knowledge", "current_sources"),
        forbidden_jobs=("premature thesis lock", "publication prose"),
        outputs=("value_chain_map", "company_universe", "evidence_ledger",
                 "candidate_hypotheses", "discovery_package", "source_evidence_ledger"),
    ),
    WritingPass.RESEARCH_ADVERSARIAL: PassContract(
        purpose="search contradictions, missing chain nodes, disconfirming companies and alternative causal explanations",
        required_inputs=("discovery_package",),
        forbidden_jobs=("protect preferred thesis", "publication prose"),
        outputs=("counterevidence", "rejected_hypotheses", "search_saturation_evidence",
                 "adversarial_package"),
    ),
    WritingPass.PRIVATE_RESEARCH_SYNTHESIS: PassContract(
        purpose="assemble every required evidence-bound PrivateResearchBrief module before selecting a publishable thesis",
        required_inputs=("discovery_package", "adversarial_package",
                         "source_evidence_ledger", "research_requirements"),
        forbidden_jobs=("publish private research scores", "draft publication prose",
                        "hide unresolved material evidence gaps", "select final thesis before module synthesis"),
        outputs=("private_research_brief", "unresolved_research_gaps", "publication_distillation"),
    ),
    WritingPass.THESIS_ADJUDICATION: PassContract(
        purpose="compare credible candidate explanations and select or merge the best evidence-bounded thesis",
        required_inputs=("discovery_package", "adversarial_package", "private_research_brief"),
        forbidden_jobs=("invent evidence", "draft paragraphs"),
        outputs=("selected_thesis", "company_decision_map", "change_conditions", "decision_envelope", "research_package"),
    ),
    WritingPass.STORY_ARCHITECTURE: PassContract(
        purpose="design one product-specific reader journey from the shared audited evidence",
        required_inputs=("selected_thesis", "audited_evidence", "reader_job", "voice_evidence", "product_mode"),
        forbidden_jobs=("reuse the other product's blueprint as a substitute",
                        "full prose drafting", "new factual research except explicit gap repair"),
        outputs=("story_blueprint",),
    ),
    WritingPass.HEADLINE_ADJUDICATION: PassContract(
        purpose="select a product-specific title whose reader promise is supported and paid off by its own blueprint",
        required_inputs=("story_blueprint", "audited_evidence",
                         "headline_search_evidence", "product_mode"),
        forbidden_jobs=("change the governing story promise without returning upstream",
                        "treat candidate count or search volume as proof of reader value",
                        "force a title tournament when the user supplied an exact title"),
        outputs=("headline_decision",),
    ),
    WritingPass.DRAFT_GENERATION: PassContract(
        purpose="write one product from its own blueprint and selected headline using audited material and voice evidence",
        required_inputs=("story_blueprint", "headline_decision", "audited_evidence",
                         "voice_evidence", "product_mode"),
        forbidden_jobs=("self-certify quality", "change governing thesis without returning upstream",
                        "expose governance scaffolding", "derive Broad by shortening Deep"),
        outputs=("draft",),
    ),
    WritingPass.READER_RETENTION_AUDIT: PassContract(
        purpose="locate where a cold reader would stop, skip, feel repetition or lose the promised payoff",
        required_inputs=("draft", "story_blueprint", "product_mode"),
        forbidden_jobs=("defend author intent", "rubric-only PASS without excerpts"),
        outputs=("retention_findings",),
    ),
    WritingPass.EDITORIAL_TRIM: PassContract(
        purpose="remove throat-clearing, repeated conclusions, detached exposition and weak transitions while preserving evidence",
        required_inputs=("draft", "retention_findings", "product_mode"),
        forbidden_jobs=("generic humanizer rewrite", "fabricate anecdotes", "weaken factual boundaries"),
        outputs=("edited_draft",),
    ),
    WritingPass.ORIGINALITY_AUDIT: PassContract(
        purpose="compare distinctive wording and structure against material sources and reject patchwriting",
        required_inputs=("edited_draft", "material_sources", "product_mode"),
        forbidden_jobs=("declare zero plagiarism without evidence",),
        outputs=("originality_findings",),
    ),
    WritingPass.FACT_INTEGRITY_AUDIT: PassContract(
        purpose="recheck material current claims, numbers, causal boundaries and company comparisons against evidence",
        required_inputs=("edited_draft", "evidence_ledger", "product_mode"),
        forbidden_jobs=("style editing that changes meaning",),
        outputs=("fact_findings",),
    ),
    WritingPass.STYLE_AUDIT: PassContract(
        purpose="find generic model scaffolding, register drift, unsupported abstraction and author-voice violations using excerpts",
        required_inputs=("edited_draft", "voice_evidence", "product_mode"),
        forbidden_jobs=("AI-detector scoring", "phrase blacklist as authorship proof"),
        outputs=("style_findings",),
    ),
    WritingPass.FINAL_SYNTHESIS: PassContract(
        purpose="aggregate audit conclusions for the already finalized draft; request DRAFT revision for any material repair",
        required_inputs=("edited_draft", "retention_findings", "originality_findings",
                         "fact_findings", "style_findings", "product_mode"),
        forbidden_jobs=("ignore unresolved MAJOR/CRITICAL findings", "silently change thesis",
                        "rewrite after DRAFT was persisted", "certify another product's draft"),
        outputs=("publication_candidate", "publication_fitness"),
    ),
    WritingPass.PLATFORM_INTERACTION_ADAPTATION: PassContract(
        purpose="independently write native short-form products from audited evidence for the actual target platforms",
        required_inputs=("selected_thesis", "audited_evidence", "reader_job",
                         "voice_evidence", "platform_context", "product_scope"),
        forbidden_jobs=("truncate or paraphrase a long-form article as the interaction product",
                        "invent urgency, fake intimacy or canned engagement"),
        outputs=("platform_interaction_pack",),
    ),
    WritingPass.PLATFORM_INTERACTION_AUDIT: PassContract(
        purpose="audit the interaction product's facts, originality, platform fit, reader value and compliance",
        required_inputs=("platform_interaction_pack", "audited_evidence", "material_sources", "product_scope"),
        forbidden_jobs=("accept platform labels as proof of native fit",
                        "treat post count or engagement prompts as reader-value evidence"),
        outputs=("platform_interaction_fitness",),
    ),
}


PASS_DEPENDENCIES: dict[WritingPass, tuple[WritingPass, ...]] = {
    WritingPass.KNOWLEDGE_RECALL: (),
    WritingPass.RESEARCH_DISCOVERY: (WritingPass.KNOWLEDGE_RECALL,),
    WritingPass.RESEARCH_ADVERSARIAL: (WritingPass.RESEARCH_DISCOVERY,),
    WritingPass.PRIVATE_RESEARCH_SYNTHESIS: (
        WritingPass.RESEARCH_DISCOVERY, WritingPass.RESEARCH_ADVERSARIAL,
    ),
    WritingPass.THESIS_ADJUDICATION: (
        WritingPass.RESEARCH_ADVERSARIAL, WritingPass.PRIVATE_RESEARCH_SYNTHESIS,
    ),
    WritingPass.STORY_ARCHITECTURE: (WritingPass.THESIS_ADJUDICATION,),
    WritingPass.HEADLINE_ADJUDICATION: (WritingPass.STORY_ARCHITECTURE,),
    WritingPass.DRAFT_GENERATION: (
        WritingPass.STORY_ARCHITECTURE, WritingPass.HEADLINE_ADJUDICATION,
    ),
    WritingPass.READER_RETENTION_AUDIT: (WritingPass.DRAFT_GENERATION,),
    WritingPass.EDITORIAL_TRIM: (
        WritingPass.DRAFT_GENERATION, WritingPass.READER_RETENTION_AUDIT,
    ),
    WritingPass.ORIGINALITY_AUDIT: (WritingPass.EDITORIAL_TRIM,),
    WritingPass.FACT_INTEGRITY_AUDIT: (WritingPass.EDITORIAL_TRIM,),
    WritingPass.STYLE_AUDIT: (WritingPass.EDITORIAL_TRIM,),
    WritingPass.FINAL_SYNTHESIS: (
        WritingPass.ORIGINALITY_AUDIT,
        WritingPass.FACT_INTEGRITY_AUDIT,
        WritingPass.STYLE_AUDIT,
        WritingPass.READER_RETENTION_AUDIT,
    ),
    WritingPass.PLATFORM_INTERACTION_ADAPTATION: (WritingPass.THESIS_ADJUDICATION,),
    WritingPass.PLATFORM_INTERACTION_AUDIT: (WritingPass.PLATFORM_INTERACTION_ADAPTATION,),
}


SHARED_RESEARCH_PASSES = (
    WritingPass.KNOWLEDGE_RECALL,
    WritingPass.RESEARCH_DISCOVERY,
    WritingPass.RESEARCH_ADVERSARIAL,
    WritingPass.PRIVATE_RESEARCH_SYNTHESIS,
    WritingPass.THESIS_ADJUDICATION,
)

LONGFORM_PRODUCT_PASSES = (
    WritingPass.STORY_ARCHITECTURE,
    WritingPass.HEADLINE_ADJUDICATION,
    WritingPass.DRAFT_GENERATION,
    WritingPass.READER_RETENTION_AUDIT,
    WritingPass.EDITORIAL_TRIM,
    WritingPass.ORIGINALITY_AUDIT,
    WritingPass.FACT_INTEGRITY_AUDIT,
    WritingPass.STYLE_AUDIT,
    WritingPass.FINAL_SYNTHESIS,
)

INTERACTION_PRODUCT_PASSES = (
    WritingPass.PLATFORM_INTERACTION_ADAPTATION,
    WritingPass.PLATFORM_INTERACTION_AUDIT,
)

# The external Article Graph remains the sole business state machine. This map
# assigns internal work to its existing stages; it does not create new stages.
PASS_STAGE_OWNERSHIP: dict[WritingPass, str] = {
    WritingPass.KNOWLEDGE_RECALL: "RESEARCH",
    WritingPass.RESEARCH_DISCOVERY: "RESEARCH",
    WritingPass.RESEARCH_ADVERSARIAL: "RESEARCH",
    WritingPass.PRIVATE_RESEARCH_SYNTHESIS: "RESEARCH",
    WritingPass.THESIS_ADJUDICATION: "RESEARCH",
    WritingPass.STORY_ARCHITECTURE: "EDITORIAL",
    WritingPass.HEADLINE_ADJUDICATION: "TITLE",
    WritingPass.DRAFT_GENERATION: "DRAFT",
    WritingPass.READER_RETENTION_AUDIT: "DRAFT",
    WritingPass.EDITORIAL_TRIM: "DRAFT",
    WritingPass.ORIGINALITY_AUDIT: "EDITORIAL_AUDIT",
    WritingPass.FACT_INTEGRITY_AUDIT: "EDITORIAL_AUDIT",
    WritingPass.STYLE_AUDIT: "EDITORIAL_AUDIT",
    WritingPass.FINAL_SYNTHESIS: "EDITORIAL_AUDIT",
    WritingPass.PLATFORM_INTERACTION_ADAPTATION: "DRAFT",
    WritingPass.PLATFORM_INTERACTION_AUDIT: "EDITORIAL_AUDIT",
}

PRE_RESEARCH_EXTERNAL_INPUTS = frozenset({
    "topic_or_task", "knowledge_sources", "topic", "current_sources",
    "research_requirements", "reader_job", "voice_evidence", "material_sources",
    "headline_search_evidence", "platform_context",
})
RESEARCH_AUDIT_BOUNDARY_INPUT = "audited_evidence"

LONGFORM_OUTPUT_TO_MODE = {
    "FINANCE_DEEP_DOCX": "FINANCE_DEEP",
    "FINANCE_BROAD_DOCX": "FINANCE_BROAD",
}
INTERACTION_OUTPUT = "PLATFORM_INTERACTION_PACK_DOCX"
AUDIT_OUTPUT = "AUDIT_DOCX"
SUPPORTED_PORTFOLIO_OUTPUTS = {
    AUDIT_OUTPUT, INTERACTION_OUTPUT, *LONGFORM_OUTPUT_TO_MODE.keys(),
}


class WritingPassExecutionError(ValueError):
    """One claimed pass could not consume its inputs or produce its outputs."""


def execution_order(nodes: set[WritingPass] | None = None) -> tuple[WritingPass, ...]:
    """Stable topological order; never iterate an unordered set of passes."""
    selected = set(PASS_CONTRACTS) if nodes is None else set(nodes)
    unknown = selected - set(PASS_CONTRACTS)
    if unknown:
        raise WritingPassExecutionError(
            "WRITING_PASS_UNKNOWN_NODES:" + ",".join(sorted(item.value for item in unknown))
        )
    ordered: list[WritingPass] = []
    visited: set[WritingPass] = set()
    visiting: set[WritingPass] = set()

    def visit(node: WritingPass) -> None:
        if node in visiting:
            raise WritingPassExecutionError(f"WRITING_PASS_CYCLE:{node.value}")
        if node in visited:
            return
        visiting.add(node)
        for dep in PASS_DEPENDENCIES[node]:
            if dep not in selected:
                raise WritingPassExecutionError(
                    f"WRITING_PASS_REQUIRED_DEPENDENCY_NOT_SELECTED:{node.value}:{dep.value}"
                )
            visit(dep)
        visiting.remove(node)
        visited.add(node)
        ordered.append(node)

    for node in WritingPass:
        if node in selected:
            visit(node)
    return tuple(ordered)


def validate_pass_dataflow(nodes: set[WritingPass] | None = None) -> list[str]:
    """Check producer/consumer fields for the selected executable pass subgraph."""
    selected = set(PASS_CONTRACTS) if nodes is None else set(nodes)
    if selected - set(PASS_CONTRACTS):
        return ["WRITING_PASS_NODE_SET_MISMATCH"]
    if set(PASS_CONTRACTS) != set(PASS_DEPENDENCIES):
        return ["WRITING_PASS_NODE_SET_MISMATCH"]

    errors: list[str] = []
    for node in selected:
        missing_deps = set(PASS_DEPENDENCIES[node]) - selected
        if missing_deps:
            errors.append(
                f"{node.value}:DEPENDENCY_NOT_SELECTED:"
                + ",".join(sorted(item.value for item in missing_deps))
            )
    if errors:
        return errors

    available = set(PRE_RESEARCH_EXTERNAL_INPUTS) | {"product_mode", "product_scope"}
    produced: set[str] = set()
    boundary_added = False
    try:
        ordered = execution_order(selected)
    except WritingPassExecutionError as exc:
        return [str(exc)]

    for node in ordered:
        for required in PASS_CONTRACTS[node].required_inputs:
            if required not in available:
                errors.append(f"{node.value}:UNPRODUCED_INPUT:{required}")
        for output in PASS_CONTRACTS[node].outputs:
            if output in produced or output in PRE_RESEARCH_EXTERNAL_INPUTS:
                errors.append(f"{node.value}:DUPLICATE_OR_SHADOWED_OUTPUT:{output}")
            available.add(output)
            produced.add(output)
        if node == WritingPass.THESIS_ADJUDICATION:
            available.add(RESEARCH_AUDIT_BOUNDARY_INPUT)
            boundary_added = True

    if any(
        node in selected
        for node in (WritingPass.STORY_ARCHITECTURE, WritingPass.PLATFORM_INTERACTION_ADAPTATION)
    ) and not boundary_added:
        errors.append("RESEARCH_AUDIT_BOUNDARY_NOT_REACHED")
    return errors


def validate_kernel() -> list[str]:
    errors: list[str] = []
    nodes = set(PASS_CONTRACTS)
    if set(PASS_DEPENDENCIES) != nodes:
        errors.append("pass contracts and dependency graph must have identical nodes")
    try:
        execution_order()
    except WritingPassExecutionError as exc:
        errors.append(str(exc))
    if not errors:
        errors.extend(validate_pass_dataflow())
    covered = (
        set(SHARED_RESEARCH_PASSES)
        | set(LONGFORM_PRODUCT_PASSES)
        | set(INTERACTION_PRODUCT_PASSES)
    )
    if covered != nodes:
        errors.append("portfolio pass scopes must cover every pass exactly once")
    if len(PASS_STAGE_OWNERSHIP) != len(nodes) or set(PASS_STAGE_OWNERSHIP) != nodes:
        errors.append("every internal pass must map to exactly one existing business stage")
    return errors


def _invoke_pass(
    node: WritingPass,
    current: dict[str, Any],
    *,
    execute_pass: Callable[[WritingPass, Mapping[str, Any]], Mapping[str, Any]],
    trace: list[dict[str, Any]],
    scope: str,
) -> None:
    contract = PASS_CONTRACTS[node]
    missing_inputs = [name for name in contract.required_inputs if name not in current]
    if missing_inputs:
        raise WritingPassExecutionError(
            f"WRITING_PASS_MISSING_INPUT:{node.value}:{','.join(missing_inputs)}"
        )
    provided = {name: current[name] for name in contract.required_inputs}
    if "task_requirement_contexts" in current:
        provided["task_requirement_contexts"] = current["task_requirement_contexts"]
    try:
        outcome = execute_pass(node, provided)
    except Exception as exc:
        raise WritingPassExecutionError(
            f"WRITING_PASS_EXECUTION_FAILED:{node.value}:{scope}"
        ) from exc
    if not isinstance(outcome, Mapping):
        raise WritingPassExecutionError(f"WRITING_PASS_OUTPUT_INVALID:{node.value}:{scope}")
    absent = [
        name for name in contract.outputs
        if name not in outcome or outcome[name] is None
    ]
    if absent:
        raise WritingPassExecutionError(
            f"WRITING_PASS_OUTPUT_MISSING:{node.value}:{scope}:{','.join(absent)}"
        )
    unexpected = set(outcome) - set(contract.outputs)
    if unexpected:
        raise WritingPassExecutionError(
            f"WRITING_PASS_UNDECLARED_OUTPUT:{node.value}:{scope}:"
            + ",".join(sorted(unexpected))
        )
    current.update(outcome)
    _append_execution_trace(
        trace,
        pass_name=node.value,
        business_stage=PASS_STAGE_OWNERSHIP[node],
        product_scope=scope,
        inputs=provided,
        outputs={name: outcome[name] for name in contract.outputs},
        status="EXECUTOR_CALLBACK_RETURNED_REQUIRED_OUTPUTS__SEMANTIC_QUALITY_OPEN",
    )


def _admit_research_audit(
    current: dict[str, Any],
    *,
    research_audit: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    trace: list[dict[str, Any]],
) -> dict[str, Any]:
    audit_inputs = deepcopy(dict(current))
    try:
        envelope = research_audit(deepcopy(audit_inputs))
    except Exception as exc:
        raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_EXECUTION_FAILED") from exc
    if (
        not isinstance(envelope, Mapping)
        or envelope.get("status") not in {"PASS", "REVISE", "FAIL"}
        or not isinstance(envelope.get("evidence_refs"), list)
        or not envelope["evidence_refs"]
    ):
        raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_RESULT_INVALID")
    status = str(envelope["status"])
    revision_target = envelope.get("revision_target")
    audited_evidence = envelope.get(RESEARCH_AUDIT_BOUNDARY_INPUT)
    if status == "PASS":
        if not isinstance(audited_evidence, Mapping):
            raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_PASS_REQUIRES_AUDITED_EVIDENCE")
        if revision_target is not None:
            raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_PASS_MUST_NOT_SET_REVISION_TARGET")
        current[RESEARCH_AUDIT_BOUNDARY_INPUT] = deepcopy(dict(audited_evidence))
    elif status == "REVISE":
        try:
            require_revision_target(Stage.RESEARCH_AUDIT, revision_target)
        except Exception as exc:
            raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_REVISE_TARGET_INVALID") from exc
    else:
        try:
            require_revision_target(Stage.RESEARCH_AUDIT, revision_target)
        except Exception as exc:
            raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_FAIL_RECOVERY_TARGET_INVALID") from exc

    result = {
        "status": status,
        "evidence_refs": list(envelope["evidence_refs"]),
        "revision_target": revision_target,
    }
    if isinstance(audited_evidence, Mapping):
        result[RESEARCH_AUDIT_BOUNDARY_INPUT] = deepcopy(dict(audited_evidence))
    current["research_audit_result"] = result
    _append_execution_trace(
        trace,
        pass_name="RESEARCH_AUDIT_BOUNDARY",
        business_stage="RESEARCH_AUDIT",
        product_scope="SHARED",
        inputs=audit_inputs,
        outputs=result,
        status=f"RESEARCH_AUDIT_{status}__SEMANTIC_SUPPORT_NOT_SELF_CERTIFIED",
    )
    return result

def _scope_marker(value: Any) -> str | None:
    if isinstance(value, Mapping):
        marker = value.get("product_mode")
        if isinstance(marker, str):
            return marker
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump(mode="json")
        if isinstance(dumped, Mapping) and isinstance(dumped.get("product_mode"), str):
            return dumped["product_mode"]
    return None


def _require_product_scope(
    current: Mapping[str, Any], *, mode: str, keys: tuple[str, ...],
) -> None:
    for key in keys:
        marker = _scope_marker(current.get(key))
        if marker != mode:
            raise WritingPassExecutionError(
                f"PORTFOLIO_PRODUCT_SCOPE_MISMATCH:{mode}:{key}:{marker or 'MISSING'}"
            )


def _portfolio_modes(required_outputs: set[str]) -> list[str]:
    return [
        mode for output, mode in LONGFORM_OUTPUT_TO_MODE.items()
        if output in required_outputs
    ]


def _canonical_task_outputs() -> set[frozenset[str]]:
    """Use TaskContract as the one output authority, not a second output table."""
    return {
        frozenset(kind.value for kind in TaskContract(
            prompt="contract-validation", distribution_mode=mode,
        ).required_outputs)
        for mode in DistributionMode
    }


def _publication_text(value: Any) -> str:
    """Require inspectable draft/candidate prose, not merely a non-null label."""
    if isinstance(value, str):
        return value.strip()
    if not isinstance(value, Mapping):
        dump = getattr(value, "model_dump", None)
        if callable(dump):
            value = dump(mode="python")
        elif hasattr(value, "blocks"):
            value = {"blocks": getattr(value, "blocks")}
    if not isinstance(value, Mapping):
        return ""
    for key in ("body", "content", "text", "markdown"):
        item = value.get(key)
        if isinstance(item, str) and item.strip():
            return item.strip()
    blocks = value.get("blocks")
    if isinstance(blocks, (list, tuple)):
        parts = []
        for block in blocks:
            if isinstance(block, Mapping):
                text = block.get("text")
            else:
                text = getattr(block, "text", None)
            if isinstance(text, str) and text.strip():
                parts.append(text.strip())
        return "\n".join(parts)
    return ""


def _admit_longform_result(current: Mapping[str, Any], *, mode: str) -> PublicationFitness:
    _require_product_scope(
        current, mode=mode,
        keys=("story_blueprint", "headline_decision", "publication_fitness"),
    )
    for key in ("draft", "edited_draft", "publication_candidate"):
        if not _publication_text(current.get(key)):
            raise WritingPassExecutionError(
                f"PORTFOLIO_PRODUCT_TEXT_MISSING:{mode}:{key}"
            )
    # A post-DRAFT audit is not authorized to rewrite the persisted article.
    # Any material repair must re-enter DRAFT and invalidate old reviews.
    if "".join(_publication_text(current["edited_draft"]).split()) != "".join(
        _publication_text(current["publication_candidate"]).split()
    ):
        raise WritingPassExecutionError(f"PORTFOLIO_AUDIT_REWROTE_DRAFT:{mode}")
    try:
        return PublicationFitness.model_validate(current["publication_fitness"])
    except Exception as exc:
        raise WritingPassExecutionError(
            f"PORTFOLIO_PUBLICATION_FITNESS_INVALID:{mode}"
        ) from exc

def _admit_interaction_result(current: Mapping[str, Any]) -> dict[str, Any]:
    try:
        pack = PlatformInteractionPack.model_validate(
            current["platform_interaction_pack"]
        )
    except Exception as exc:
        raise WritingPassExecutionError(
            "PORTFOLIO_INTERACTION_PACK_INVALID"
        ) from exc
    result = current["platform_interaction_fitness"]
    if (
        not isinstance(result, Mapping)
        or result.get("status") not in {"PASS", "REVISE", "FAIL"}
        or not isinstance(result.get("evidence_refs"), list)
        or not result["evidence_refs"]
    ):
        raise WritingPassExecutionError(
            "PORTFOLIO_INTERACTION_AUDIT_RESULT_INVALID"
        )
    if not pack.independent_rewrite_from_long_form:
        raise WritingPassExecutionError(
            "PORTFOLIO_INTERACTION_NOT_INDEPENDENT"
        )
    status = str(result["status"])
    target = result.get("revision_target")
    if status == "REVISE":
        try:
            require_revision_target(Stage.EDITORIAL_AUDIT, target)
        except Exception as exc:
            raise WritingPassExecutionError("PORTFOLIO_INTERACTION_REVISION_TARGET_INVALID") from exc
    elif target is not None:
        raise WritingPassExecutionError("PORTFOLIO_INTERACTION_NON_REVISE_MUST_NOT_SET_TARGET")
    return {
        "status": status,
        "evidence_refs": list(result["evidence_refs"]),
        "revision_target": target,
    }

def execute_writing_passes(
    seed_inputs: Mapping[str, Any],
    *,
    execute_pass: Callable[[WritingPass, Mapping[str, Any]], Mapping[str, Any]],
    research_audit: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> dict[str, Any]:
    """Execute one long-form product branch plus the interaction branch.

    This lower-level adapter is useful for isolated product tests. New PORTFOLIO
    work must use execute_portfolio_writing so shared research is executed once
    and Deep/Broad receive separate product-scoped branches.
    """
    issues = validate_pass_dataflow()
    if issues:
        raise WritingPassExecutionError("WRITING_PASS_DATAFLOW_INVALID:" + ";".join(issues))
    if not callable(execute_pass) or not callable(research_audit):
        raise WritingPassExecutionError("WRITING_PASS_EXECUTOR_AND_RESEARCH_AUDIT_REQUIRED")
    current = dict(seed_inputs)
    current.setdefault("product_scope", "PLATFORM_INTERACTION")
    missing = (PRE_RESEARCH_EXTERNAL_INPUTS | {"product_mode"}) - set(current)
    if missing:
        raise WritingPassExecutionError(
            "WRITING_PASS_EXTERNAL_INPUTS_MISSING:" + ",".join(sorted(missing))
        )
    if RESEARCH_AUDIT_BOUNDARY_INPUT in current:
        raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_PRESEED_FORBIDDEN")

    trace: list[dict[str, Any]] = []
    for node in execution_order():
        scope = (
            "PLATFORM_INTERACTION" if node in INTERACTION_PRODUCT_PASSES
            else str(current["product_mode"]) if node in LONGFORM_PRODUCT_PASSES
            else "SHARED"
        )
        _invoke_pass(node, current, execute_pass=execute_pass, trace=trace, scope=scope)
        if node == WritingPass.THESIS_ADJUDICATION:
            _admit_research_audit(current, research_audit=research_audit, trace=trace)

    return {
        "schema_version": "2.0",
        "pass_count": len(PASS_CONTRACTS),
        "research_audit_boundary_reached": True,
        "trace": trace,
        "products": current,
        "assurance": (
            "SINGLE_PRODUCT_AND_INTERACTION_CALLBACK_DATAFLOW_EXECUTED"
            "__NOT_PORTFOLIO_OR_EDITORIAL_ACCEPTANCE__NOT_INDEPENDENT_EDITORIAL"
        ),
    }



INTERNAL_PORTFOLIO_STAGE_SEQUENCE = (
    "RESEARCH",
    "RESEARCH_AUDIT",
    "EDITORIAL",
    "TITLE",
    "DRAFT",
    "EDITORIAL_AUDIT",
)
INTERNAL_PORTFOLIO_NEXT_STAGE = {
    **{
        stage: INTERNAL_PORTFOLIO_STAGE_SEQUENCE[index + 1]
        for index, stage in enumerate(INTERNAL_PORTFOLIO_STAGE_SEQUENCE[:-1])
    },
    "EDITORIAL_AUDIT": "DELIVERY",
}
PORTFOLIO_CONTEXT_SCHEMA_VERSION = "1.0"
PORTFOLIO_STAGE_RECEIPT_VERSION = "1.0"


def _json_value(value: Any) -> Any:
    """Convert pass payloads to strict, deterministic JSON without lossy repr()."""
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return _json_value(value.model_dump(mode="json"))
    if isinstance(value, Enum):
        return _json_value(value.value)
    if isinstance(value, Mapping):
        if any(not isinstance(key, str) for key in value):
            raise WritingPassExecutionError("PORTFOLIO_PAYLOAD_MAPPING_KEYS_MUST_BE_STRINGS")
        return {key: _json_value(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise WritingPassExecutionError("PORTFOLIO_PAYLOAD_NONFINITE_NUMBER")
        return value
    raise WritingPassExecutionError(
        f"PORTFOLIO_PAYLOAD_NOT_JSON_SERIALIZABLE:{type(value).__name__}"
    )


def _canonical_bytes(value: Any) -> bytes:
    try:
        return json.dumps(
            _json_value(value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise WritingPassExecutionError("PORTFOLIO_PAYLOAD_CANONICALIZATION_FAILED") from exc


def _payload_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _append_execution_trace(
    trace: list[dict[str, Any]],
    *,
    pass_name: str,
    business_stage: str,
    product_scope: str,
    inputs: Mapping[str, Any],
    outputs: Mapping[str, Any],
    status: str,
) -> None:
    previous = trace[-1].get("receipt_sha256") if trace else None
    body = {
        "receipt_version": "1.0",
        "sequence": len(trace) + 1,
        "pass": pass_name,
        "business_stage": business_stage,
        "product_scope": product_scope,
        "status": status,
        "input_sha256": _payload_sha256(inputs),
        "output_sha256": _payload_sha256(outputs),
        "output_key_sha256": {
            key: _payload_sha256(value) for key, value in sorted(outputs.items())
        },
        "previous_pass_receipt_sha256": previous,
        "assurance": "HASH_BOUND_CALLBACK_OUTPUTS__NOT_PROVIDER_ATTESTATION",
    }
    trace.append({**body, "receipt_sha256": _payload_sha256(body)})


def _portfolio_context_payload(context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value for key, value in context.items()
        if key not in {"stage_receipts", "initial_context_sha256", "revision_history"}
    }


def _portfolio_context_sha256(context: Mapping[str, Any]) -> str:
    return _payload_sha256(_portfolio_context_payload(context))


def _validate_portfolio_request(
    seed_inputs: Mapping[str, Any],
    required_outputs: list[str],
) -> tuple[dict[str, Any], list[str], bool]:
    if not isinstance(required_outputs, list) or len(required_outputs) != len(set(required_outputs)):
        raise WritingPassExecutionError("PORTFOLIO_REQUIRED_OUTPUTS_INVALID")
    requested = set(required_outputs)
    unknown = requested - SUPPORTED_PORTFOLIO_OUTPUTS
    if unknown:
        raise WritingPassExecutionError(
            "PORTFOLIO_OUTPUT_KIND_UNSUPPORTED:" + ",".join(sorted(unknown))
        )
    if AUDIT_OUTPUT not in requested:
        raise WritingPassExecutionError("PORTFOLIO_AUDIT_DOCX_REQUIRED")
    if requested != {AUDIT_OUTPUT} and frozenset(requested) not in _canonical_task_outputs():
        raise WritingPassExecutionError("PORTFOLIO_OUTPUTS_NOT_CANONICAL_TASK_CONTRACT")
    modes = _portfolio_modes(requested)
    interaction_required = INTERACTION_OUTPUT in requested
    if not modes and not interaction_required:
        raise WritingPassExecutionError("PORTFOLIO_HAS_NO_PUBLICATION_PRODUCT")

    active_nodes = set(SHARED_RESEARCH_PASSES)
    if modes:
        active_nodes.update(LONGFORM_PRODUCT_PASSES)
    if interaction_required:
        active_nodes.update(INTERACTION_PRODUCT_PASSES)
    issues = validate_pass_dataflow(active_nodes)
    if issues:
        raise WritingPassExecutionError(
            "PORTFOLIO_PASS_DATAFLOW_INVALID:" + ";".join(issues)
        )

    if not isinstance(seed_inputs, Mapping):
        raise WritingPassExecutionError("PORTFOLIO_SHARED_INPUTS_INVALID")
    shared = dict(seed_inputs)
    if "task_requirement_contexts" in shared:
        raise WritingPassExecutionError("PORTFOLIO_REQUIREMENT_CONTEXTS_MUST_USE_AUTHORITY_BINDING")
    required_shared = {
        "topic_or_task", "knowledge_sources", "topic", "current_sources",
        "research_requirements", "reader_job", "voice_evidence", "material_sources",
    }
    missing = required_shared - set(shared)
    if missing:
        raise WritingPassExecutionError(
            "PORTFOLIO_SHARED_INPUTS_MISSING:" + ",".join(sorted(missing))
        )
    if modes and "headline_search_evidence" not in shared:
        raise WritingPassExecutionError("PORTFOLIO_HEADLINE_SEARCH_EVIDENCE_REQUIRED")
    if interaction_required and "platform_context" not in shared:
        raise WritingPassExecutionError("PORTFOLIO_PLATFORM_CONTEXT_REQUIRED")
    if RESEARCH_AUDIT_BOUNDARY_INPUT in shared:
        raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_PRESEED_FORBIDDEN")
    return shared, modes, interaction_required


def _all_requirement_scopes(modes: list[str], interaction_required: bool) -> list[str]:
    scopes = ["ALL", "RESEARCH", "PRIVATE_RESEARCH", *modes]
    if interaction_required:
        scopes.append("PLATFORM_INTERACTION")
    return sorted(set(scopes))


def _validate_requirement_contexts(
    requirement_contexts: Mapping[str, Any] | None,
    *,
    required_scopes: list[str],
    requirement_digest: str,
) -> dict[str, dict[str, Any]] | None:
    if requirement_contexts is None:
        return None
    if not isinstance(requirement_contexts, Mapping):
        raise WritingPassExecutionError("PORTFOLIO_TASK_REQUIREMENT_CONTEXTS_INVALID")
    missing = set(required_scopes) - set(requirement_contexts)
    if missing:
        raise WritingPassExecutionError(
            "PORTFOLIO_TASK_REQUIREMENT_CONTEXT_SCOPE_MISSING:" + ",".join(sorted(missing))
        )
    selected: dict[str, dict[str, Any]] = {}
    revision: int | None = None
    seen: dict[str, str] = {}
    for scope in required_scopes:
        raw = requirement_contexts[scope]
        if (
            not isinstance(raw, Mapping)
            or set(raw) != {"contract_version", "revision", "digest", "requirements"}
            or raw.get("contract_version") != "1.0"
            or raw.get("digest") != requirement_digest
            or not isinstance(raw.get("revision"), int)
            or raw.get("revision") < 0
            or not isinstance(raw.get("requirements"), list)
        ):
            raise WritingPassExecutionError(
                f"PORTFOLIO_TASK_REQUIREMENT_CONTEXT_INVALID:{scope}"
            )
        if revision is None:
            revision = raw["revision"]
        elif revision != raw["revision"]:
            raise WritingPassExecutionError("PORTFOLIO_TASK_REQUIREMENT_CONTEXT_REVISION_MISMATCH")
        normalized: list[dict[str, Any]] = []
        ids: set[str] = set()
        for item in raw["requirements"]:
            try:
                parsed = TaskRequirement.model_validate(item)
            except Exception as exc:
                raise WritingPassExecutionError(
                    f"PORTFOLIO_TASK_REQUIREMENT_RECORD_INVALID:{scope}"
                ) from exc
            if scope not in parsed.scopes and "ALL" not in parsed.scopes:
                raise WritingPassExecutionError(
                    f"PORTFOLIO_TASK_REQUIREMENT_SCOPE_MISMATCH:{scope}:{parsed.requirement_id}"
                )
            if parsed.requirement_id in ids:
                raise WritingPassExecutionError(
                    f"PORTFOLIO_TASK_REQUIREMENT_DUPLICATE:{scope}:{parsed.requirement_id}"
                )
            ids.add(parsed.requirement_id)
            dumped = parsed.model_dump(mode="json")
            digest = _payload_sha256(dumped)
            if parsed.requirement_id in seen and seen[parsed.requirement_id] != digest:
                raise WritingPassExecutionError(
                    f"PORTFOLIO_TASK_REQUIREMENT_SCOPE_CONFLICT:{parsed.requirement_id}"
                )
            seen[parsed.requirement_id] = digest
            normalized.append(dumped)
        selected[scope] = {
            "contract_version": raw["contract_version"],
            "revision": raw["revision"],
            "digest": raw["digest"],
            "requirements": normalized,
        }
    return selected


def _requirement_scopes_for_stage(
    stage: str, modes: list[str], interaction_required: bool,
) -> list[str]:
    if stage in {"RESEARCH", "RESEARCH_AUDIT"}:
        return ["ALL", "RESEARCH", "PRIVATE_RESEARCH"]
    scopes = ["ALL", *modes]
    if interaction_required and stage in {"DRAFT", "EDITORIAL_AUDIT"}:
        scopes.append("PLATFORM_INTERACTION")
    return sorted(set(scopes))


def _requirement_contexts_for_pass(
    requirement_contexts: Mapping[str, Any] | None, scope: str,
) -> dict[str, Any] | None:
    if requirement_contexts is None:
        return None
    if scope == "SHARED":
        names = ("ALL", "RESEARCH", "PRIVATE_RESEARCH")
    elif scope == "PLATFORM_INTERACTION":
        names = ("ALL", "PLATFORM_INTERACTION")
    else:
        names = ("ALL", scope)
    return {
        name: deepcopy(requirement_contexts[name])
        for name in names if name in requirement_contexts
    }


def _due_requirements_for_stage(
    requirement_contexts: Mapping[str, Any] | None,
    *,
    stage: str,
    modes: list[str],
    interaction_required: bool,
) -> dict[str, dict[str, Any]]:
    if requirement_contexts is None:
        return {}
    due: dict[str, dict[str, Any]] = {}
    for scope in _requirement_scopes_for_stage(stage, modes, interaction_required):
        for item in requirement_contexts[scope]["requirements"]:
            if item["affects_from_stage"] != stage:
                continue
            requirement_id = item["requirement_id"]
            existing = due.get(requirement_id)
            if existing is not None and existing != item:
                raise WritingPassExecutionError(
                    f"PORTFOLIO_TASK_REQUIREMENT_SCOPE_CONFLICT:{requirement_id}"
                )
            due[requirement_id] = item
    return due


def _normalize_stage_requirement_satisfaction(
    raw: list[Mapping[str, Any]] | None,
    *,
    due: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    supplied = list(raw or [])
    if not due:
        if supplied:
            raise WritingPassExecutionError("PORTFOLIO_REQUIREMENT_SATISFACTION_NOT_DUE")
        return []
    if not supplied:
        raise WritingPassExecutionError(
            "PORTFOLIO_REQUIREMENT_SATISFACTION_REQUIRED:" + ",".join(sorted(due))
        )
    normalized: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in supplied:
        if not isinstance(item, Mapping):
            raise WritingPassExecutionError("PORTFOLIO_REQUIREMENT_SATISFACTION_RECORD_INVALID")
        requirement_id = str(item.get("requirement_id", "")).strip()
        if requirement_id not in due or requirement_id in seen:
            raise WritingPassExecutionError(
                f"PORTFOLIO_REQUIREMENT_SATISFACTION_ID_INVALID:{requirement_id or 'MISSING'}"
            )
        if item.get("result") != "SATISFIED":
            raise WritingPassExecutionError(
                f"PORTFOLIO_REQUIREMENT_NOT_SATISFIED:{requirement_id}"
            )
        refs = item.get("evidence_refs")
        if not isinstance(refs, list) or not refs or any(
            not isinstance(ref, str) or not ref.strip() for ref in refs
        ):
            raise WritingPassExecutionError(
                f"PORTFOLIO_REQUIREMENT_EVIDENCE_REFS_REQUIRED:{requirement_id}"
            )
        if len(refs) != len(set(refs)):
            raise WritingPassExecutionError(
                f"PORTFOLIO_REQUIREMENT_EVIDENCE_REFS_DUPLICATED:{requirement_id}"
            )
        normalized.append({
            "requirement_id": requirement_id,
            "result": "SATISFIED",
            "evidence_refs": [ref.strip() for ref in refs],
            "notes": str(item.get("notes", "")).strip(),
        })
        seen.add(requirement_id)
    if seen != set(due):
        raise WritingPassExecutionError(
            "PORTFOLIO_REQUIREMENT_SATISFACTION_INCOMPLETE:"
            + ",".join(sorted(set(due) - seen))
        )
    return sorted(normalized, key=lambda item: item["requirement_id"])


def _append_revision_history(context: dict[str, Any], body: Mapping[str, Any]) -> dict[str, Any]:
    previous = (
        context["revision_history"][-1]["record_sha256"]
        if context.get("revision_history") else None
    )
    record_body = {**deepcopy(dict(body)), "previous_revision_sha256": previous}
    record = {**record_body, "record_sha256": _payload_sha256(record_body)}
    context.setdefault("revision_history", []).append(record)
    return record


def _invalidate_portfolio_outputs_for_revision(
    *,
    target: str,
    seed_inputs: Mapping[str, Any],
    shared: dict[str, Any],
    products: dict[str, dict[str, Any]],
    interaction: dict[str, Any] | None,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, Any] | None]:
    if target == "RESEARCH":
        return (
            deepcopy(dict(seed_inputs)),
            {mode: {} for mode in products},
            {} if interaction is not None else None,
        )
    if target == "EDITORIAL":
        return shared, {mode: {} for mode in products}, {} if interaction is not None else None
    if target == "TITLE":
        return (
            shared,
            {
                mode: {key: value for key, value in item.items() if key == "story_blueprint"}
                for mode, item in products.items()
            },
            {} if interaction is not None else None,
        )
    if target == "DRAFT":
        return (
            shared,
            {
                mode: {
                    key: value for key, value in item.items()
                    if key in {"story_blueprint", "headline_decision"}
                }
                for mode, item in products.items()
            },
            {} if interaction is not None else None,
        )
    raise WritingPassExecutionError(f"PORTFOLIO_REVISION_TARGET_NOT_INTERNAL:{target}")


def _editorial_review_outcome(
    fitnesses: list[PublicationFitness],
    interaction_fitness: Mapping[str, Any] | None,
) -> tuple[str, str | None]:
    statuses = [fitness.final_status.value for fitness in fitnesses]
    revise_targets = [
        fitness.revision_target for fitness in fitnesses
        if fitness.final_status == AuditStatus.REVISE
    ]
    fail_targets: list[str] = []
    if interaction_fitness is not None:
        status = str(interaction_fitness["status"])
        statuses.append(status)
        if status == "REVISE":
            revise_targets.append(interaction_fitness["revision_target"])
        elif status == "FAIL":
            fail_targets.append(interaction_fitness["revision_target"])
    if "FAIL" in statuses:
        if not fail_targets:
            raise WritingPassExecutionError("PORTFOLIO_EDITORIAL_AUDIT_FAIL_TARGET_REQUIRED")
        target = fail_targets[0]
        require_revision_target(Stage.EDITORIAL_AUDIT, target)
        return "FAIL", target
    if "REVISE" in statuses:
        order = ("RESEARCH", "EDITORIAL", "TITLE", "DRAFT")
        if not revise_targets or any(target not in order for target in revise_targets):
            raise WritingPassExecutionError("PORTFOLIO_EDITORIAL_AUDIT_REVISE_TARGET_INVALID")
        for target in revise_targets:
            require_revision_target(Stage.EDITORIAL_AUDIT, target)
        return "REVISE", min(revise_targets, key=order.index)
    return "PASS", None


def _portfolio_stage_receipt(context: Mapping[str, Any]) -> Mapping[str, Any]:
    if context.get("stage_receipts"):
        return context["stage_receipts"][-1]
    if context.get("revision_history"):
        return context["revision_history"][-1]["stage_receipt"]
    raise WritingPassExecutionError("PORTFOLIO_STAGE_RECEIPT_NOT_FOUND")


def _validate_revision_history(context: Mapping[str, Any]) -> None:
    history = context.get("revision_history")
    if not isinstance(history, list):
        raise WritingPassExecutionError("PORTFOLIO_REVISION_HISTORY_INVALID")
    previous = None
    for record in history:
        if not isinstance(record, Mapping):
            raise WritingPassExecutionError("PORTFOLIO_REVISION_RECORD_INVALID")
        body = {key: value for key, value in record.items() if key != "record_sha256"}
        if (
            record.get("previous_revision_sha256") != previous
            or _payload_sha256(body) != record.get("record_sha256")
        ):
            raise WritingPassExecutionError("PORTFOLIO_REVISION_HISTORY_HASH_MISMATCH")
        if record.get("record_type") == "REVISION":
            receipt = record.get("stage_receipt")
            if not isinstance(receipt, Mapping):
                raise WritingPassExecutionError("PORTFOLIO_REVISION_STAGE_RECEIPT_MISSING")
            receipt_body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
            if _payload_sha256(receipt_body) != receipt.get("receipt_sha256"):
                raise WritingPassExecutionError("PORTFOLIO_REVISION_STAGE_RECEIPT_HASH_MISMATCH")
            require_revision_target(Stage(str(record["from_stage"])), str(record["target_stage"]))
        elif record.get("record_type") != "RESUME":
            raise WritingPassExecutionError("PORTFOLIO_REVISION_RECORD_TYPE_INVALID")
        previous = record["record_sha256"]


def validate_portfolio_context(context: Mapping[str, Any]) -> None:
    """Validate task binding, requirement authority, stage generation and hash chains."""
    if not isinstance(context, Mapping):
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_INVALID")
    if context.get("schema_version") != PORTFOLIO_CONTEXT_SCHEMA_VERSION:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_SCHEMA_VERSION_UNSUPPORTED")
    if not isinstance(context.get("task_id"), str) or not context["task_id"].strip():
        raise WritingPassExecutionError("PORTFOLIO_TASK_ID_REQUIRED")
    requirement_digest = context.get("requirement_digest")
    if (
        not isinstance(requirement_digest, str)
        or len(requirement_digest) != 64
        or any(char not in "0123456789abcdef" for char in requirement_digest)
    ):
        raise WritingPassExecutionError("PORTFOLIO_REQUIREMENT_DIGEST_INVALID")

    required = context.get("required_output_kinds")
    seed_inputs = context.get("seed_inputs")
    if not isinstance(required, list) or not isinstance(seed_inputs, Mapping):
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_SEED_INVALID")
    normalized_seed, modes, interaction_required = _validate_portfolio_request(seed_inputs, required)
    if context.get("products", {}).keys() != {mode for mode in modes}:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_PRODUCT_SET_MISMATCH")
    if interaction_required != (isinstance(context.get("interaction"), Mapping)):
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_INTERACTION_SET_MISMATCH")
    if not isinstance(context.get("shared"), Mapping):
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_SHARED_INVALID")
    if context.get("requirement_contexts") is not None:
        _validate_requirement_contexts(
            context["requirement_contexts"],
            required_scopes=_all_requirement_scopes(modes, interaction_required),
            requirement_digest=requirement_digest,
        )

    initial_stage = context.get("initial_stage")
    current_stage = context.get("current_stage")
    if initial_stage not in INTERNAL_PORTFOLIO_STAGE_SEQUENCE:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_INITIAL_STAGE_INVALID")
    if current_stage not in {*INTERNAL_PORTFOLIO_STAGE_SEQUENCE, "DELIVERY"}:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_STAGE_INVALID")
    if not isinstance(context.get("generation"), int) or context["generation"] < 0:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_GENERATION_INVALID")
    execution_status = context.get("execution_status")
    if execution_status not in {"ACTIVE", "BLOCKED"}:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_EXECUTION_STATUS_INVALID")

    receipts = context.get("stage_receipts")
    trace = context.get("trace")
    if not isinstance(receipts, list) or not isinstance(trace, list):
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_RECEIPTS_INVALID")
    initial_sha = context.get("initial_context_sha256")
    if not isinstance(initial_sha, str) or len(initial_sha) != 64:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_INITIAL_DIGEST_MISSING")

    trace_by_sha: dict[str, Mapping[str, Any]] = {}
    previous_pass_sha = None
    for sequence, record in enumerate(trace, start=1):
        if not isinstance(record, Mapping):
            raise WritingPassExecutionError("PORTFOLIO_PASS_RECEIPT_INVALID")
        body = {key: value for key, value in record.items() if key != "receipt_sha256"}
        receipt_sha = record.get("receipt_sha256")
        if (
            record.get("sequence") != sequence
            or record.get("previous_pass_receipt_sha256") != previous_pass_sha
            or _payload_sha256(body) != receipt_sha
            or not isinstance(receipt_sha, str)
        ):
            raise WritingPassExecutionError("PORTFOLIO_PASS_RECEIPT_CHAIN_MISMATCH")
        trace_by_sha[receipt_sha] = record
        previous_pass_sha = receipt_sha

    expected_stage = initial_stage
    expected_input_sha = initial_sha
    previous_stage_sha = None
    last_status = None
    for index, receipt in enumerate(receipts):
        if not isinstance(receipt, Mapping):
            raise WritingPassExecutionError("PORTFOLIO_STAGE_RECEIPT_INVALID")
        body = {key: value for key, value in receipt.items() if key != "receipt_sha256"}
        if _payload_sha256(body) != receipt.get("receipt_sha256"):
            raise WritingPassExecutionError("PORTFOLIO_STAGE_RECEIPT_HASH_MISMATCH")
        stage = receipt.get("stage")
        status = receipt.get("status")
        if (
            receipt.get("receipt_version") != PORTFOLIO_STAGE_RECEIPT_VERSION
            or stage != expected_stage
            or receipt.get("task_id") != context["task_id"]
            or receipt.get("requirement_digest") != requirement_digest
            or receipt.get("previous_stage_receipt_sha256") != previous_stage_sha
            or receipt.get("input_context_sha256") != expected_input_sha
            or status not in {"PASS", "FAIL"}
        ):
            raise WritingPassExecutionError("PORTFOLIO_STAGE_RECEIPT_CHAIN_MISMATCH")
        next_stage = INTERNAL_PORTFOLIO_NEXT_STAGE[stage] if status == "PASS" else stage
        if receipt.get("next_stage") != next_stage:
            raise WritingPassExecutionError("PORTFOLIO_STAGE_RECEIPT_NEXT_STAGE_MISMATCH")
        pass_hashes = receipt.get("pass_receipt_sha256s")
        if not isinstance(pass_hashes, list):
            raise WritingPassExecutionError("PORTFOLIO_STAGE_PASS_RECEIPTS_INVALID")
        for pass_hash in pass_hashes:
            pass_record = trace_by_sha.get(pass_hash)
            if not isinstance(pass_record, Mapping) or pass_record.get("business_stage") != stage:
                raise WritingPassExecutionError("PORTFOLIO_STAGE_PASS_RECEIPT_SET_MISMATCH")
        expected_input_sha = receipt.get("output_context_sha256")
        if not isinstance(expected_input_sha, str) or len(expected_input_sha) != 64:
            raise WritingPassExecutionError("PORTFOLIO_STAGE_OUTPUT_CONTEXT_DIGEST_INVALID")
        previous_stage_sha = receipt["receipt_sha256"]
        expected_stage = next_stage
        last_status = status
        if status == "FAIL" and index != len(receipts) - 1:
            raise WritingPassExecutionError("PORTFOLIO_BLOCKED_STAGE_MUST_BE_LAST")

    if current_stage != expected_stage:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_STAGE_POSITION_INVALID")
    if execution_status == "BLOCKED":
        if last_status != "FAIL" or context.get("blocked_stage") != current_stage:
            raise WritingPassExecutionError("PORTFOLIO_CONTEXT_BLOCKED_RECEIPT_MISMATCH")
    elif last_status == "FAIL" or context.get("blocked_stage") is not None:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_ACTIVE_BLOCKED_MISMATCH")
    if receipts:
        if _portfolio_context_sha256(context) != expected_input_sha:
            raise WritingPassExecutionError("PORTFOLIO_CONTEXT_OUTPUT_DIGEST_MISMATCH")
    elif _portfolio_context_sha256(context) != initial_sha:
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_INITIAL_DIGEST_MISMATCH")
    _validate_revision_history(context)

    last_result = context.get("last_stage_result")
    if last_result is not None:
        if not isinstance(last_result, Mapping) or last_result.get("stage") not in INTERNAL_PORTFOLIO_STAGE_SEQUENCE:
            raise WritingPassExecutionError("PORTFOLIO_LAST_STAGE_RESULT_INVALID")
        if last_result.get("status") not in {"PASS", "REVISE", "FAIL"}:
            raise WritingPassExecutionError("PORTFOLIO_LAST_STAGE_RESULT_STATUS_INVALID")


def start_portfolio_context(
    seed_inputs: Mapping[str, Any],
    *,
    required_outputs: list[str],
    task_id: str,
    requirement_digest: str,
    requirement_contexts: Mapping[str, Any] | None = None,
    current_stage: str = "RESEARCH",
) -> dict[str, Any]:
    """Create a serializable task-bound context from an admitted owner stage."""
    if not isinstance(task_id, str) or not task_id.strip():
        raise WritingPassExecutionError("PORTFOLIO_TASK_ID_REQUIRED")
    if not isinstance(requirement_digest, str) or len(requirement_digest) != 64:
        raise WritingPassExecutionError("PORTFOLIO_REQUIREMENT_DIGEST_INVALID")
    if any(char not in "0123456789abcdef" for char in requirement_digest):
        raise WritingPassExecutionError("PORTFOLIO_REQUIREMENT_DIGEST_INVALID")
    if current_stage not in INTERNAL_PORTFOLIO_STAGE_SEQUENCE:
        raise WritingPassExecutionError("PORTFOLIO_INITIAL_STAGE_NOT_EXECUTABLE")
    shared, modes, interaction_required = _validate_portfolio_request(
        seed_inputs, required_outputs,
    )
    contexts = _validate_requirement_contexts(
        requirement_contexts,
        required_scopes=_all_requirement_scopes(modes, interaction_required),
        requirement_digest=requirement_digest,
    )
    context = {
        "schema_version": PORTFOLIO_CONTEXT_SCHEMA_VERSION,
        "task_id": task_id,
        "requirement_digest": requirement_digest,
        "required_output_kinds": sorted(set(required_outputs)),
        "initial_stage": current_stage,
        "current_stage": current_stage,
        "generation": 0,
        "execution_status": "ACTIVE",
        "blocked_stage": None,
        "seed_inputs": shared,
        "shared": shared,
        "requirement_contexts": contexts,
        "products": {mode: {} for mode in modes},
        "interaction": {} if interaction_required else None,
        "trace": [],
        "stage_receipts": [],
        "revision_history": [],
        "last_stage_result": None,
    }
    context["initial_context_sha256"] = _portfolio_context_sha256(context)
    validate_portfolio_context(context)
    return context


def rebind_portfolio_context_requirements(
    context: Mapping[str, Any],
    *,
    requirement_digest: str,
    requirement_contexts: Mapping[str, Any],
    current_stage: str,
) -> dict[str, Any]:
    """Rebind changed owner requirements and invalidate from the owner-selected stage."""
    validate_portfolio_context(context)
    if current_stage not in INTERNAL_PORTFOLIO_STAGE_SEQUENCE:
        raise WritingPassExecutionError("PORTFOLIO_REQUIREMENT_REBIND_STAGE_INVALID")
    working = deepcopy(dict(context))
    modes = list(working["products"])
    interaction_required = working["interaction"] is not None
    contexts = _validate_requirement_contexts(
        requirement_contexts,
        required_scopes=_all_requirement_scopes(modes, interaction_required),
        requirement_digest=requirement_digest,
    )
    shared, products, interaction = _invalidate_portfolio_outputs_for_revision(
        target=current_stage,
        seed_inputs=working["seed_inputs"],
        shared=deepcopy(working["shared"]),
        products=deepcopy(working["products"]),
        interaction=deepcopy(working["interaction"]),
    )
    previous_digest = working["requirement_digest"]
    working.update({
        "requirement_digest": requirement_digest,
        "requirement_contexts": contexts,
        "shared": shared,
        "products": products,
        "interaction": interaction,
        "initial_stage": current_stage,
        "current_stage": current_stage,
        "generation": working["generation"] + 1,
        "execution_status": "ACTIVE",
        "blocked_stage": None,
        "stage_receipts": [],
        "last_stage_result": None,
    })
    _append_revision_history(working, {
        "record_type": "RESUME",
        "reason": "TASK_REQUIREMENT_DIGEST_CHANGED",
        "from_stage": current_stage,
        "target_stage": current_stage,
        "previous_requirement_digest": previous_digest,
        "new_requirement_digest": requirement_digest,
        "generation": working["generation"],
    })
    working["initial_context_sha256"] = _portfolio_context_sha256(working)
    validate_portfolio_context(working)
    return working


def resume_portfolio_context(
    context: Mapping[str, Any],
    *,
    owner_state: Mapping[str, Any],
) -> dict[str, Any]:
    """Resume a failed review attempt only after the owner state is no longer BLOCKED."""
    validate_portfolio_context(context)
    if context.get("execution_status") != "BLOCKED":
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_NOT_BLOCKED")
    if (
        owner_state.get("status") != "IN_PROGRESS"
        or owner_state.get("current_stage") != context.get("current_stage")
        or owner_state.get("task_id") != context.get("task_id")
        or owner_state.get("task_requirement_digest") != context.get("requirement_digest")
    ):
        raise WritingPassExecutionError("PORTFOLIO_OWNER_RESUME_STATE_MISMATCH")
    failed = context["stage_receipts"][-1]
    working = deepcopy(dict(context))
    _append_revision_history(working, {
        "record_type": "RESUME",
        "reason": "OWNER_RESUMED_BLOCKED_STAGE",
        "from_stage": failed["stage"],
        "target_stage": failed["stage"],
        "failed_stage_receipt": deepcopy(dict(failed)),
        "generation": working["generation"] + 1,
    })
    stage = str(failed["stage"])
    if stage == "RESEARCH_AUDIT":
        working["shared"].pop("research_audit_result", None)
        working["shared"].pop(RESEARCH_AUDIT_BOUNDARY_INPUT, None)
    if stage == "EDITORIAL_AUDIT":
        for item in working["products"].values():
            item.pop("publication_fitness", None)
        if isinstance(working["interaction"], dict):
            working["interaction"].pop("platform_interaction_fitness", None)
    working.update({
        "initial_stage": stage,
        "current_stage": stage,
        "generation": working["generation"] + 1,
        "execution_status": "ACTIVE",
        "blocked_stage": None,
        "stage_receipts": [],
        "last_stage_result": None,
    })
    working["initial_context_sha256"] = _portfolio_context_sha256(working)
    validate_portfolio_context(working)
    return working


def execute_portfolio_stage(
    context: Mapping[str, Any],
    *,
    stage: str,
    execute_pass: Callable[[WritingPass, Mapping[str, Any]], Mapping[str, Any]] | None = None,
    research_audit: Callable[[Mapping[str, Any]], Mapping[str, Any]] | None = None,
    requirement_satisfaction: list[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Execute one stage and return a resumable context for PASS, REVISE or FAIL."""
    validate_portfolio_context(context)
    if context.get("execution_status") != "ACTIVE":
        raise WritingPassExecutionError("PORTFOLIO_CONTEXT_BLOCKED_REQUIRES_OWNER_RESUME")
    if stage != context.get("current_stage"):
        raise WritingPassExecutionError(
            f"PORTFOLIO_STAGE_OUT_OF_ORDER:expected={context.get('current_stage')}:actual={stage}"
        )
    if stage not in INTERNAL_PORTFOLIO_STAGE_SEQUENCE:
        raise WritingPassExecutionError(f"PORTFOLIO_STAGE_NOT_EXECUTABLE:{stage}")
    if stage == "RESEARCH_AUDIT":
        if not callable(research_audit):
            raise WritingPassExecutionError("PORTFOLIO_RESEARCH_AUDIT_CALLBACK_REQUIRED")
    elif not callable(execute_pass):
        raise WritingPassExecutionError("PORTFOLIO_STAGE_EXECUTOR_REQUIRED")

    working = deepcopy(dict(context))
    modes = list(working["products"])
    interaction_required = working["interaction"] is not None
    contexts = working.get("requirement_contexts")
    if contexts is not None:
        contexts = _validate_requirement_contexts(
            contexts,
            required_scopes=_all_requirement_scopes(modes, interaction_required),
            requirement_digest=working["requirement_digest"],
        )
    stage_contexts = (
        _requirement_contexts_for_pass(contexts, "SHARED")
        if contexts is not None and stage in {"RESEARCH", "RESEARCH_AUDIT"}
        else None
    )
    due = _due_requirements_for_stage(
        contexts, stage=stage, modes=modes, interaction_required=interaction_required,
    )
    satisfaction = _normalize_stage_requirement_satisfaction(
        requirement_satisfaction, due=due,
    )

    input_context_sha = _portfolio_context_sha256(working)
    trace_start = len(working["trace"])
    shared = deepcopy(working["shared"])
    products = deepcopy(working["products"])
    interaction = deepcopy(working["interaction"])
    review_status = "PASS"
    revision_target: str | None = None
    fitnesses: list[PublicationFitness] = []
    interaction_fitness: dict[str, Any] | None = None

    if stage == "RESEARCH":
        pass_shared = deepcopy(shared)
        if stage_contexts is not None:
            pass_shared["task_requirement_contexts"] = stage_contexts
        for node in SHARED_RESEARCH_PASSES:
            _invoke_pass(
                node, pass_shared, execute_pass=execute_pass,
                trace=working["trace"], scope="SHARED",
            )
        shared = {
            key: value for key, value in pass_shared.items()
            if key != "task_requirement_contexts"
        }
        active_ids = {
            item["requirement_id"]
            for scope in ("ALL", "RESEARCH", "PRIVATE_RESEARCH")
            for item in (contexts or {}).get(scope, {}).get("requirements", [])
        }
        if "full_universe_research_pool" in active_ids:
            package = shared.get("research_package")
            try:
                ResearchPackage.model_validate(package)
            except Exception as exc:
                raise WritingPassExecutionError(
                    "PORTFOLIO_FULL_UNIVERSE_RESEARCH_PACKAGE_REQUIRED"
                ) from exc

    elif stage == "RESEARCH_AUDIT":
        audit_shared = deepcopy(shared)
        if stage_contexts is not None:
            audit_shared["task_requirement_contexts"] = stage_contexts
        audit_result = _admit_research_audit(
            audit_shared, research_audit=research_audit, trace=working["trace"],
        )
        shared = {
            key: value for key, value in audit_shared.items()
            if key != "task_requirement_contexts"
        }
        review_status = audit_result["status"]
        revision_target = audit_result.get("revision_target")

    elif stage == "EDITORIAL":
        for mode in modes:
            branch = {
                **shared, **products[mode], "product_mode": mode,
            }
            selected_contexts = _requirement_contexts_for_pass(contexts, mode)
            if selected_contexts is not None:
                branch["task_requirement_contexts"] = selected_contexts
            _invoke_pass(
                WritingPass.STORY_ARCHITECTURE, branch,
                execute_pass=execute_pass, trace=working["trace"], scope=mode,
            )
            _require_product_scope(branch, mode=mode, keys=("story_blueprint",))
            products[mode]["story_blueprint"] = branch["story_blueprint"]

    elif stage == "TITLE":
        for mode in modes:
            branch = {**shared, **products[mode], "product_mode": mode}
            selected_contexts = _requirement_contexts_for_pass(contexts, mode)
            if selected_contexts is not None:
                branch["task_requirement_contexts"] = selected_contexts
            _invoke_pass(
                WritingPass.HEADLINE_ADJUDICATION, branch,
                execute_pass=execute_pass, trace=working["trace"], scope=mode,
            )
            _require_product_scope(branch, mode=mode, keys=("headline_decision",))
            products[mode]["headline_decision"] = branch["headline_decision"]

    elif stage == "DRAFT":
        for mode in modes:
            branch = {**shared, **products[mode], "product_mode": mode}
            selected_contexts = _requirement_contexts_for_pass(contexts, mode)
            if selected_contexts is not None:
                branch["task_requirement_contexts"] = selected_contexts
            for node in LONGFORM_PRODUCT_PASSES:
                if PASS_STAGE_OWNERSHIP[node] != "DRAFT":
                    continue
                _invoke_pass(
                    node, branch, execute_pass=execute_pass,
                    trace=working["trace"], scope=mode,
                )
                products[mode].update({
                    name: branch[name] for name in PASS_CONTRACTS[node].outputs
                })
        if interaction is not None:
            branch = {**shared, **interaction, "product_scope": "PLATFORM_INTERACTION"}
            selected_contexts = _requirement_contexts_for_pass(contexts, "PLATFORM_INTERACTION")
            if selected_contexts is not None:
                branch["task_requirement_contexts"] = selected_contexts
            _invoke_pass(
                WritingPass.PLATFORM_INTERACTION_ADAPTATION, branch,
                execute_pass=execute_pass, trace=working["trace"],
                scope="PLATFORM_INTERACTION",
            )
            interaction["platform_interaction_pack"] = branch["platform_interaction_pack"]

    elif stage == "EDITORIAL_AUDIT":
        for mode in modes:
            branch = {**shared, **products[mode], "product_mode": mode}
            selected_contexts = _requirement_contexts_for_pass(contexts, mode)
            if selected_contexts is not None:
                branch["task_requirement_contexts"] = selected_contexts
            for node in LONGFORM_PRODUCT_PASSES:
                if PASS_STAGE_OWNERSHIP[node] != "EDITORIAL_AUDIT":
                    continue
                _invoke_pass(
                    node, branch, execute_pass=execute_pass,
                    trace=working["trace"], scope=mode,
                )
                products[mode].update({
                    name: branch[name] for name in PASS_CONTRACTS[node].outputs
                })
                if node == WritingPass.FINAL_SYNTHESIS:
                    fitnesses.append(_admit_longform_result(branch, mode=mode))
        if interaction is not None:
            branch = {**shared, **interaction, "product_scope": "PLATFORM_INTERACTION"}
            selected_contexts = _requirement_contexts_for_pass(contexts, "PLATFORM_INTERACTION")
            if selected_contexts is not None:
                branch["task_requirement_contexts"] = selected_contexts
            _invoke_pass(
                WritingPass.PLATFORM_INTERACTION_AUDIT, branch,
                execute_pass=execute_pass, trace=working["trace"],
                scope="PLATFORM_INTERACTION",
            )
            interaction_fitness = _admit_interaction_result(branch)
            interaction["platform_interaction_fitness"] = interaction_fitness
        review_status, revision_target = _editorial_review_outcome(
            fitnesses, interaction_fitness,
        )
        if len(products) > 1:
            texts = [
                "".join(_publication_text(item.get("publication_candidate")).split())
                for item in products.values()
            ]
            if len(set(texts)) != len(texts):
                raise WritingPassExecutionError("PORTFOLIO_LONGFORM_BODY_CLONED")

    if review_status == "REVISE":
        try:
            revision_target = require_revision_target(Stage(stage), str(revision_target)).value
        except Exception as exc:
            raise WritingPassExecutionError(
                f"PORTFOLIO_REVIEW_REVISION_TARGET_INVALID:{stage}"
            ) from exc
    elif review_status == "FAIL":
        try:
            revision_target = require_revision_target(Stage(stage), str(revision_target)).value
        except Exception as exc:
            raise WritingPassExecutionError(
                f"PORTFOLIO_REVIEW_FAIL_RECOVERY_TARGET_INVALID:{stage}"
            ) from exc
    elif revision_target is not None:
        raise WritingPassExecutionError("PORTFOLIO_PASS_MUST_NOT_SET_REVISION_TARGET")

    working["shared"] = shared
    working["products"] = products
    working["interaction"] = interaction
    working["last_stage_result"] = {
        "stage": stage,
        "status": review_status,
        "revision_target": revision_target,
        "requirement_satisfaction": satisfaction,
    }
    new_trace = working["trace"][trace_start:]
    previous_stage_sha = (
        working["stage_receipts"][-1]["receipt_sha256"]
        if working["stage_receipts"] else None
    )

    if review_status == "PASS":
        next_stage = INTERNAL_PORTFOLIO_NEXT_STAGE[stage]
        working["current_stage"] = next_stage
        working["execution_status"] = "ACTIVE"
        working["blocked_stage"] = None
        output_context_sha = _portfolio_context_sha256(working)
        receipt_body = {
            "receipt_version": PORTFOLIO_STAGE_RECEIPT_VERSION,
            "task_id": working["task_id"],
            "requirement_digest": working["requirement_digest"],
            "stage": stage,
            "next_stage": next_stage,
            "status": "PASS",
            "revision_target": None,
            "previous_stage_receipt_sha256": previous_stage_sha,
            "input_context_sha256": input_context_sha,
            "output_context_sha256": output_context_sha,
            "pass_receipt_sha256s": [item["receipt_sha256"] for item in new_trace],
            "pass_count": len(new_trace),
            "requirement_satisfaction": satisfaction,
            "assurance": "HASH_BOUND_STAGE_OUTPUTS__OWNER_ADMISSION_REQUIRED",
        }
        working["stage_receipts"].append({
            **receipt_body, "receipt_sha256": _payload_sha256(receipt_body),
        })

    elif review_status == "FAIL":
        working["current_stage"] = stage
        working["execution_status"] = "BLOCKED"
        working["blocked_stage"] = stage
        output_context_sha = _portfolio_context_sha256(working)
        receipt_body = {
            "receipt_version": PORTFOLIO_STAGE_RECEIPT_VERSION,
            "task_id": working["task_id"],
            "requirement_digest": working["requirement_digest"],
            "stage": stage,
            "next_stage": stage,
            "status": "FAIL",
            "revision_target": revision_target,
            "previous_stage_receipt_sha256": previous_stage_sha,
            "input_context_sha256": input_context_sha,
            "output_context_sha256": output_context_sha,
            "pass_receipt_sha256s": [item["receipt_sha256"] for item in new_trace],
            "pass_count": len(new_trace),
            "requirement_satisfaction": satisfaction,
            "assurance": "HASH_BOUND_FAILURE_EVIDENCE__OWNER_BLOCK_REQUIRED",
        }
        working["stage_receipts"].append({
            **receipt_body, "receipt_sha256": _payload_sha256(receipt_body),
        })

    else:
        target = str(revision_target)
        revised_shared, revised_products, revised_interaction = _invalidate_portfolio_outputs_for_revision(
            target=target,
            seed_inputs=working["seed_inputs"],
            shared=deepcopy(shared),
            products=deepcopy(products),
            interaction=deepcopy(interaction),
        )
        working["shared"] = revised_shared
        working["products"] = revised_products
        working["interaction"] = revised_interaction
        working["current_stage"] = target
        working["initial_stage"] = target
        working["generation"] += 1
        working["execution_status"] = "ACTIVE"
        working["blocked_stage"] = None
        working["stage_receipts"] = []
        output_context_sha = _portfolio_context_sha256(working)
        receipt_body = {
            "receipt_version": PORTFOLIO_STAGE_RECEIPT_VERSION,
            "task_id": working["task_id"],
            "requirement_digest": working["requirement_digest"],
            "stage": stage,
            "next_stage": target,
            "status": "REVISE",
            "revision_target": target,
            "previous_stage_receipt_sha256": previous_stage_sha,
            "input_context_sha256": input_context_sha,
            "output_context_sha256": output_context_sha,
            "pass_receipt_sha256s": [item["receipt_sha256"] for item in new_trace],
            "pass_count": len(new_trace),
            "requirement_satisfaction": satisfaction,
            "assurance": "HASH_BOUND_REVISION_ROUTE__OWNER_ADMISSION_REQUIRED",
        }
        stage_receipt = {
            **receipt_body, "receipt_sha256": _payload_sha256(receipt_body),
        }
        _append_revision_history(working, {
            "record_type": "REVISION",
            "from_stage": stage,
            "target_stage": target,
            "from_generation": working["generation"] - 1,
            "to_generation": working["generation"],
            "stage_receipt": stage_receipt,
        })
        working["initial_context_sha256"] = _portfolio_context_sha256(working)

    validate_portfolio_context(working)
    return working

def execute_portfolio_writing(
    seed_inputs: Mapping[str, Any],
    *,
    required_outputs: list[str],
    execute_pass: Callable[[WritingPass, Mapping[str, Any]], Mapping[str, Any]],
    research_audit: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> dict[str, Any]:
    """In-memory end-to-end replay wrapper; production resumes one persisted stage at a time.

    This compatibility helper deliberately does not claim that owner state, stage
    artifacts or external provider readbacks were persisted. Production callers
    must use start_portfolio_context + execute_portfolio_stage and the authenticated
    standalone Financial owner runtime between every stage.
    """
    task_id = seed_inputs.get("task_id")
    requirement_digest = seed_inputs.get("requirement_digest")
    external_inputs = {
        key: value for key, value in seed_inputs.items()
        if key not in {"task_id", "requirement_digest"}
    }
    context = start_portfolio_context(
        external_inputs,
        required_outputs=required_outputs,
        task_id=task_id,
        requirement_digest=requirement_digest,
    )
    for stage in INTERNAL_PORTFOLIO_STAGE_SEQUENCE:
        context = execute_portfolio_stage(
            context,
            stage=stage,
            execute_pass=execute_pass,
            research_audit=research_audit if stage == "RESEARCH_AUDIT" else None,
        )

    products = context["products"]
    longform_products = {
        mode: {
            **item,
            "product_mode": mode,
            "trace": [
                record for record in context["trace"]
                if record.get("product_scope") == mode
            ],
        }
        for mode, item in products.items()
    }
    interaction = context["interaction"]
    interaction_product = None if interaction is None else {
        **interaction,
        "trace": [
            record for record in context["trace"]
            if record.get("product_scope") == "PLATFORM_INTERACTION"
        ],
    }
    modes = list(products)
    interaction_required = interaction_product is not None
    if len(longform_products) > 1:
        texts = [
            "".join(_publication_text(item["publication_candidate"]).split())
            for item in longform_products.values()
        ]
        if len(set(texts)) != len(texts):
            raise WritingPassExecutionError("PORTFOLIO_LONGFORM_BODY_CLONED")
    stage_barriers = [
        {
            "business_stage": receipt["stage"],
            "completed_product_scopes": (
                ["SHARED"]
                if receipt["stage"] in {"RESEARCH", "RESEARCH_AUDIT"}
                else [
                    *modes,
                    *(
                        ["PLATFORM_INTERACTION"]
                        if interaction_required and receipt["stage"] in {"DRAFT", "EDITORIAL_AUDIT"}
                        else []
                    ),
                ]
            ),
            "assurance": "HASH_BOUND_CALLBACK_OUTPUTS__OWNER_STATE_ADMISSION_OPEN",
            "stage_receipt_sha256": receipt["receipt_sha256"],
        }
        for receipt in context["stage_receipts"]
    ]
    return {
        "schema_version": "3.0",
        "execution_scope": "FINANCIAL_PRODUCT_PORTFOLIO",
        "required_output_kinds": context["required_output_kinds"],
        "shared_research_pass_count": len(SHARED_RESEARCH_PASSES),
        "longform_product_modes": modes,
        "longform_products": longform_products,
        "platform_interaction": interaction_product,
        "pass_count": sum(
            1 for item in context["trace"]
            if item["pass"] != "RESEARCH_AUDIT_BOUNDARY"
        ),
        "research_audit_boundary_reached": RESEARCH_AUDIT_BOUNDARY_INPUT in context["shared"],
        "stage_barriers": stage_barriers,
        "stage_receipts": context["stage_receipts"],
        "trace": context["trace"],
        "assurance": (
            "HASH_BOUND_IN_MEMORY_CALLBACK_STAGE_REPLAY"
            "__NOT_PROVIDER_PERSISTENCE_OR_SEMANTIC_QUALITY_OR_INDEPENDENT_EDITORIAL_ACCEPTANCE"
        ),
    }

