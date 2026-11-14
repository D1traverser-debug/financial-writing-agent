from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .models import DistributionMode, TaskContract
from .schemas import PlatformInteractionPack
from .story_quality import AuditStatus, PublicationFitness


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
        outputs=("selected_thesis", "company_decision_map", "change_conditions", "decision_envelope"),
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
        purpose="apply evidence-backed repairs, resolve gate findings and produce one product-specific publication candidate",
        required_inputs=("edited_draft", "retention_findings", "originality_findings",
                         "fact_findings", "style_findings", "product_mode"),
        forbidden_jobs=("ignore unresolved MAJOR/CRITICAL findings", "silently change thesis",
                        "certify another product's draft"),
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
    WritingPass.READER_RETENTION_AUDIT: "EDITORIAL_AUDIT",
    WritingPass.EDITORIAL_TRIM: "EDITORIAL_AUDIT",
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
    trace.append({
        "pass": node.value,
        "business_stage": PASS_STAGE_OWNERSHIP[node],
        "product_scope": scope,
        "status": "EXECUTOR_CALLBACK_RETURNED_REQUIRED_OUTPUTS__SEMANTIC_QUALITY_OPEN",
        "outputs": list(contract.outputs),
    })


def _admit_research_audit(
    current: dict[str, Any],
    *,
    research_audit: Callable[[Mapping[str, Any]], Mapping[str, Any]],
    trace: list[dict[str, Any]],
) -> None:
    try:
        envelope = research_audit(dict(current))
    except Exception as exc:
        raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_EXECUTION_FAILED") from exc
    if (
        not isinstance(envelope, Mapping)
        or envelope.get("status") != "PASS"
        or not isinstance(envelope.get("evidence_refs"), list)
        or not envelope["evidence_refs"]
        or envelope.get(RESEARCH_AUDIT_BOUNDARY_INPUT) is None
    ):
        raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_NOT_ADMITTED")
    current[RESEARCH_AUDIT_BOUNDARY_INPUT] = envelope[RESEARCH_AUDIT_BOUNDARY_INPUT]
    trace.append({
        "pass": "RESEARCH_AUDIT_BOUNDARY",
        "business_stage": "RESEARCH_AUDIT",
        "product_scope": "SHARED",
        "status": "CALLBACK_ADMITTED__REAL_SEMANTIC_SUPPORT_NOT_SELF_CERTIFIED",
        "evidence_refs": list(envelope["evidence_refs"]),
    })


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


def _admit_longform_result(current: Mapping[str, Any], *, mode: str) -> None:
    _require_product_scope(
        current, mode=mode,
        keys=("story_blueprint", "headline_decision", "publication_fitness"),
    )
    for key in ("draft", "publication_candidate"):
        if not _publication_text(current.get(key)):
            raise WritingPassExecutionError(
                f"PORTFOLIO_PRODUCT_TEXT_MISSING:{mode}:{key}"
            )
    try:
        fitness = PublicationFitness.model_validate(current["publication_fitness"])
    except Exception as exc:
        raise WritingPassExecutionError(
            f"PORTFOLIO_PUBLICATION_FITNESS_INVALID:{mode}"
        ) from exc
    if fitness.final_status != AuditStatus.PASS:
        raise WritingPassExecutionError(
            f"PORTFOLIO_PUBLICATION_FITNESS_REVISE:{mode}"
        )
    # This is schema/gate admission only. Independent publication proof and
    # exact persisted draft readback remain external owner-stage obligations.


def _admit_interaction_result(current: Mapping[str, Any]) -> None:
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
        or result.get("status") != "PASS"
        or not isinstance(result.get("evidence_refs"), list)
        or not result["evidence_refs"]
    ):
        raise WritingPassExecutionError(
            "PORTFOLIO_INTERACTION_AUDIT_NOT_ADMITTED"
        )
    if not pack.independent_rewrite_from_long_form:
        raise WritingPassExecutionError(
            "PORTFOLIO_INTERACTION_NOT_INDEPENDENT"
        )


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


def execute_portfolio_writing(
    seed_inputs: Mapping[str, Any],
    *,
    required_outputs: list[str],
    execute_pass: Callable[[WritingPass, Mapping[str, Any]], Mapping[str, Any]],
    research_audit: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> dict[str, Any]:
    """Execute the shared research spine once, then every required product branch.

    The 10-stage Article Graph remains the sole business state machine. This
    orchestrator creates no task identity, state, receipt or persistence route.
    Its callbacks execute work; returned values are not independent acceptance.
    """
    if not callable(execute_pass) or not callable(research_audit):
        raise WritingPassExecutionError("PORTFOLIO_EXECUTOR_AND_RESEARCH_AUDIT_REQUIRED")
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
        raise WritingPassExecutionError("PORTFOLIO_PASS_DATAFLOW_INVALID:" + ";".join(issues))

    shared = dict(seed_inputs)
    required_shared = {
        "topic_or_task", "knowledge_sources", "topic", "current_sources",
        "research_requirements", "reader_job", "voice_evidence", "material_sources",
    }
    missing_shared = required_shared - set(shared)
    if missing_shared:
        raise WritingPassExecutionError(
            "PORTFOLIO_SHARED_INPUTS_MISSING:" + ",".join(sorted(missing_shared))
        )
    if modes and "headline_search_evidence" not in shared:
        raise WritingPassExecutionError("PORTFOLIO_HEADLINE_SEARCH_EVIDENCE_REQUIRED")
    if interaction_required and "platform_context" not in shared:
        raise WritingPassExecutionError("PORTFOLIO_PLATFORM_CONTEXT_REQUIRED")
    if RESEARCH_AUDIT_BOUNDARY_INPUT in shared:
        raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_PRESEED_FORBIDDEN")

    trace: list[dict[str, Any]] = []
    for node in SHARED_RESEARCH_PASSES:
        _invoke_pass(node, shared, execute_pass=execute_pass, trace=trace, scope="SHARED")
        if node == WritingPass.THESIS_ADJUDICATION:
            _admit_research_audit(shared, research_audit=research_audit, trace=trace)

    if RESEARCH_AUDIT_BOUNDARY_INPUT not in shared:
        raise WritingPassExecutionError("PORTFOLIO_RESEARCH_AUDIT_BOUNDARY_NOT_REACHED")

    longform_products: dict[str, dict[str, Any]] = {}
    for mode in modes:
        branch = dict(shared)
        branch["product_mode"] = mode
        branch_trace_start = len(trace)
        for node in LONGFORM_PRODUCT_PASSES:
            _invoke_pass(node, branch, execute_pass=execute_pass, trace=trace, scope=mode)
        _admit_longform_result(branch, mode=mode)
        longform_products[mode] = {
            "product_mode": mode,
            "story_blueprint": branch["story_blueprint"],
            "headline_decision": branch["headline_decision"],
            "draft": branch["draft"],
            "publication_candidate": branch["publication_candidate"],
            "publication_fitness": branch["publication_fitness"],
            "trace": trace[branch_trace_start:],
        }

    interaction_product = None
    if interaction_required:
        branch = dict(shared)
        branch["product_scope"] = "PLATFORM_INTERACTION"
        branch_trace_start = len(trace)
        for node in INTERACTION_PRODUCT_PASSES:
            _invoke_pass(
                node, branch, execute_pass=execute_pass,
                trace=trace, scope="PLATFORM_INTERACTION",
            )
        _admit_interaction_result(branch)
        interaction_product = {
            "platform_interaction_pack": branch["platform_interaction_pack"],
            "platform_interaction_fitness": branch["platform_interaction_fitness"],
            "trace": trace[branch_trace_start:],
        }

    # A copied final body is not an independently composed acquisition product.
    # Semantic near-clones still require independent editorial review.
    if len(longform_products) > 1:
        texts = [
            "".join(_publication_text(item["publication_candidate"]).split())
            for item in longform_products.values()
        ]
        if len(set(texts)) != len(texts):
            raise WritingPassExecutionError("PORTFOLIO_LONGFORM_BODY_CLONED")

    expected_modes = set(modes)
    if set(longform_products) != expected_modes:
        raise WritingPassExecutionError("PORTFOLIO_LONGFORM_PRODUCT_SET_MISMATCH")
    if interaction_required != (interaction_product is not None):
        raise WritingPassExecutionError("PORTFOLIO_INTERACTION_PRODUCT_SET_MISMATCH")

    return {
        "schema_version": "2.0",
        "execution_scope": "FINANCIAL_PRODUCT_PORTFOLIO",
        "required_output_kinds": sorted(requested),
        "shared_research_pass_count": len(SHARED_RESEARCH_PASSES),
        "longform_product_modes": modes,
        "longform_products": longform_products,
        "platform_interaction": interaction_product,
        "pass_count": (
            len(SHARED_RESEARCH_PASSES)
            + len(modes) * len(LONGFORM_PRODUCT_PASSES)
            + (len(INTERACTION_PRODUCT_PASSES) if interaction_required else 0)
        ),
        "research_audit_boundary_reached": True,
        "trace": trace,
        "assurance": (
            "PORTFOLIO_CALLBACK_DATAFLOW_EXECUTED"
            "__NOT_SEMANTIC_QUALITY_OR_INDEPENDENT_EDITORIAL_ACCEPTANCE"
        ),
    }
