from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from collections.abc import Callable, Mapping
from typing import Any


class WritingPass(str, Enum):
    KNOWLEDGE_RECALL = "KNOWLEDGE_RECALL"
    RESEARCH_DISCOVERY = "RESEARCH_DISCOVERY"
    RESEARCH_ADVERSARIAL = "RESEARCH_ADVERSARIAL"
    PRIVATE_RESEARCH_SYNTHESIS = "PRIVATE_RESEARCH_SYNTHESIS"
    THESIS_ADJUDICATION = "THESIS_ADJUDICATION"
    STORY_ARCHITECTURE = "STORY_ARCHITECTURE"
    DRAFT_GENERATION = "DRAFT_GENERATION"
    READER_RETENTION_AUDIT = "READER_RETENTION_AUDIT"
    EDITORIAL_TRIM = "EDITORIAL_TRIM"
    ORIGINALITY_AUDIT = "ORIGINALITY_AUDIT"
    FACT_INTEGRITY_AUDIT = "FACT_INTEGRITY_AUDIT"
    STYLE_AUDIT = "STYLE_AUDIT"
    FINAL_SYNTHESIS = "FINAL_SYNTHESIS"


@dataclass(frozen=True)
class PassContract:
    purpose: str
    required_inputs: tuple[str, ...]
    forbidden_jobs: tuple[str, ...]
    outputs: tuple[str, ...]


PASS_CONTRACTS: dict[WritingPass, PassContract] = {
    WritingPass.KNOWLEDGE_RECALL: PassContract(
        purpose="recover prior structural/method/company cognition without treating memory as current fact",
        required_inputs=("topic_or_task", "knowledge_sources"),
        forbidden_jobs=("select final thesis", "draft publication prose"),
        outputs=("recalled_knowledge", "revalidation_queue"),
    ),
    WritingPass.RESEARCH_DISCOVERY: PassContract(
        purpose="map the full material value chain, company universe, chronology and evidence before thesis convergence",
        required_inputs=("topic", "recalled_knowledge", "current_sources"),
        forbidden_jobs=("premature thesis lock", "publication prose"),
        outputs=("value_chain_map", "company_universe", "evidence_ledger", "candidate_hypotheses",
                 "discovery_package", "source_evidence_ledger"),
    ),
    WritingPass.RESEARCH_ADVERSARIAL: PassContract(
        purpose="search for contradictions, missing chain nodes, disconfirming companies and alternative causal explanations",
        required_inputs=("discovery_package",),
        forbidden_jobs=("protect preferred thesis", "publication prose"),
        outputs=("counterevidence", "rejected_hypotheses", "search_saturation_evidence",
                 "adversarial_package"),
    ),
    WritingPass.PRIVATE_RESEARCH_SYNTHESIS: PassContract(
        purpose="assemble all required evidence-bound PrivateResearchBrief 1.1 modules from full discovery and disconfirming research before selecting a publishable thesis",
        required_inputs=("discovery_package", "adversarial_package", "source_evidence_ledger", "research_requirements"),
        forbidden_jobs=("publish private research scores", "draft publication prose", "hide unresolved material evidence gaps", "select final thesis before module synthesis"),
        outputs=("private_research_brief", "unresolved_research_gaps", "publication_distillation"),
    ),
    WritingPass.THESIS_ADJUDICATION: PassContract(
        purpose="compare credible candidate explanations and select or merge the best evidence-bounded thesis",
        required_inputs=("discovery_package", "adversarial_package", "private_research_brief"),
        forbidden_jobs=("invent evidence", "draft paragraphs"),
        outputs=("selected_thesis", "company_decision_map", "change_conditions", "decision_envelope"),
    ),
    WritingPass.STORY_ARCHITECTURE: PassContract(
        purpose="turn the selected evidence into a reader journey with explicit hook, progressive payoff, company anchors and numbered structure",
        required_inputs=("selected_thesis", "audited_evidence", "reader_job", "voice_evidence"),
        forbidden_jobs=("full prose drafting", "new factual research except explicit gap repair"),
        outputs=("story_blueprint",),
    ),
    WritingPass.DRAFT_GENERATION: PassContract(
        purpose="write from the story blueprint and evidence in the intended author voice",
        required_inputs=("story_blueprint", "audited_evidence", "voice_evidence"),
        forbidden_jobs=("self-certify quality", "change governing thesis without returning upstream", "expose governance scaffolding"),
        outputs=("draft",),
    ),
    WritingPass.READER_RETENTION_AUDIT: PassContract(
        purpose="locate where a cold reader would stop, skip, feel repetition, or lose the promised payoff",
        required_inputs=("draft", "story_blueprint"),
        forbidden_jobs=("defend author intent", "rubric-only PASS without excerpts"),
        outputs=("retention_findings",),
    ),
    WritingPass.EDITORIAL_TRIM: PassContract(
        purpose="remove throat-clearing, repeated conclusions, detached exposition and weak transitions while preserving evidence",
        required_inputs=("draft", "retention_findings"),
        forbidden_jobs=("generic humanizer rewrite", "fabricate anecdotes", "weaken factual boundaries"),
        outputs=("edited_draft",),
    ),
    WritingPass.ORIGINALITY_AUDIT: PassContract(
        purpose="check distinctive wording/structure against material sources and reject patchwriting or suspiciously close paraphrase",
        required_inputs=("edited_draft", "material_sources"),
        forbidden_jobs=("declare zero plagiarism without evidence",),
        outputs=("originality_findings",),
    ),
    WritingPass.FACT_INTEGRITY_AUDIT: PassContract(
        purpose="recheck every material current claim, number, causal boundary and company comparison against evidence",
        required_inputs=("edited_draft", "evidence_ledger"),
        forbidden_jobs=("style editing that changes meaning",),
        outputs=("fact_findings",),
    ),
    WritingPass.STYLE_AUDIT: PassContract(
        purpose="find generic model scaffolding, register drift, abstraction without evidence and author-voice violations using text excerpts",
        required_inputs=("edited_draft", "voice_evidence"),
        forbidden_jobs=("AI-detector scoring", "phrase blacklist as authorship proof"),
        outputs=("style_findings",),
    ),
    WritingPass.FINAL_SYNTHESIS: PassContract(
        purpose="apply only evidence-backed repairs, resolve gate findings and produce the publication candidate",
        required_inputs=("edited_draft", "retention_findings", "originality_findings", "fact_findings", "style_findings"),
        forbidden_jobs=("ignore unresolved MAJOR/CRITICAL findings", "silently change thesis"),
        outputs=("publication_candidate", "publication_fitness"),
    ),
}


PASS_DEPENDENCIES: dict[WritingPass, tuple[WritingPass, ...]] = {
    WritingPass.KNOWLEDGE_RECALL: (),
    WritingPass.RESEARCH_DISCOVERY: (WritingPass.KNOWLEDGE_RECALL,),
    WritingPass.RESEARCH_ADVERSARIAL: (WritingPass.RESEARCH_DISCOVERY,),
    WritingPass.PRIVATE_RESEARCH_SYNTHESIS: (WritingPass.RESEARCH_DISCOVERY, WritingPass.RESEARCH_ADVERSARIAL),
    WritingPass.THESIS_ADJUDICATION: (WritingPass.RESEARCH_ADVERSARIAL, WritingPass.PRIVATE_RESEARCH_SYNTHESIS),
    WritingPass.STORY_ARCHITECTURE: (WritingPass.THESIS_ADJUDICATION,),
    WritingPass.DRAFT_GENERATION: (WritingPass.STORY_ARCHITECTURE,),
    WritingPass.READER_RETENTION_AUDIT: (WritingPass.DRAFT_GENERATION,),
    WritingPass.EDITORIAL_TRIM: (WritingPass.DRAFT_GENERATION, WritingPass.READER_RETENTION_AUDIT),
    WritingPass.ORIGINALITY_AUDIT: (WritingPass.EDITORIAL_TRIM,),
    WritingPass.FACT_INTEGRITY_AUDIT: (WritingPass.EDITORIAL_TRIM,),
    WritingPass.STYLE_AUDIT: (WritingPass.EDITORIAL_TRIM,),
    WritingPass.FINAL_SYNTHESIS: (
        WritingPass.ORIGINALITY_AUDIT,
        WritingPass.FACT_INTEGRITY_AUDIT,
        WritingPass.STYLE_AUDIT,
        WritingPass.READER_RETENTION_AUDIT,
    ),
}


def validate_kernel() -> list[str]:
    errors: list[str] = []
    nodes = set(PASS_CONTRACTS)
    if set(PASS_DEPENDENCIES) != nodes:
        errors.append("pass contracts and dependency graph must have identical nodes")
    for node, deps in PASS_DEPENDENCIES.items():
        unknown = set(deps) - nodes
        if unknown:
            errors.append(f"unknown dependencies for {node.value}: {sorted(x.value for x in unknown)}")

    visiting: set[WritingPass] = set()
    visited: set[WritingPass] = set()

    def walk(node: WritingPass) -> None:
        if node in visiting:
            errors.append(f"cycle detected at {node.value}")
            return
        if node in visited:
            return
        visiting.add(node)
        for dep in PASS_DEPENDENCIES.get(node, ()):
            walk(dep)
        visiting.remove(node)
        visited.add(node)

    for node in nodes:
        walk(node)
    if not errors:
        errors.extend(validate_pass_dataflow())
    return errors


# Inputs are external *work* and source boundary objects. They are never
# inferred from the fact that a Python stage has advanced. In particular
# audited_evidence MUST come from an actual Research Audit boundary after thesis
# adjudication; it cannot be preseeded as the result of the writer's own pass.
PRE_RESEARCH_EXTERNAL_INPUTS = frozenset({
    "topic_or_task", "knowledge_sources", "topic", "current_sources",
    "research_requirements", "reader_job", "voice_evidence", "material_sources",
})
RESEARCH_AUDIT_BOUNDARY_INPUT = "audited_evidence"


class WritingPassExecutionError(ValueError):
    """One claimed pass could not consume its inputs or produce its outputs."""


def execution_order() -> tuple[WritingPass, ...]:
    """Stable topological order; never iterate an unordered set of passes."""
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
            visit(dep)
        visiting.remove(node)
        visited.add(node)
        ordered.append(node)

    for node in WritingPass:
        visit(node)
    return tuple(ordered)


def validate_pass_dataflow() -> list[str]:
    """Check producers/consumers, *not just* DAG cycles and node count.

    Boundary-owned inputs are declared explicitly. A missing intermediate
    product must be fixed at its actual producer; do not synthesize it in the
    receiving pass or make every value a global, implicit input.
    """
    errors: list[str] = []
    if set(PASS_CONTRACTS) != set(WritingPass) or set(PASS_DEPENDENCIES) != set(WritingPass):
        return ["WRITING_PASS_NODE_SET_MISMATCH"]
    available = set(PRE_RESEARCH_EXTERNAL_INPUTS)
    produced: set[str] = set()
    for node in execution_order():
        if node == WritingPass.STORY_ARCHITECTURE:
            available.add(RESEARCH_AUDIT_BOUNDARY_INPUT)
        contract = PASS_CONTRACTS[node]
        for required in contract.required_inputs:
            if required not in available:
                errors.append(f"{node.value}:UNPRODUCED_INPUT:{required}")
        for output in contract.outputs:
            if output in produced or output in PRE_RESEARCH_EXTERNAL_INPUTS:
                errors.append(f"{node.value}:DUPLICATE_OR_SHADOWED_OUTPUT:{output}")
            available.add(output)
            produced.add(output)
    return errors


def execute_writing_passes(
    seed_inputs: Mapping[str, Any],
    *,
    execute_pass: Callable[[WritingPass, Mapping[str, Any]], Mapping[str, Any]],
    research_audit: Callable[[Mapping[str, Any]], Mapping[str, Any]],
) -> dict[str, Any]:
    """Invoke all thirteen passes against their actual dependency products.

    This is a synchronous execution adapter, not an LLM or a source-of-truth
    article state. The host is responsible for real research, writing, exact
    artifact persistence, user instruction evidence and qualified review. A
    callback's arbitrary return values cannot become editorial certification.

    Missing inputs, passes, output keys or failed Research Audit stop execution.
    There is no fake default output and no automatic PASS on a callback.
    """
    issues = validate_pass_dataflow()
    if issues:
        raise WritingPassExecutionError("WRITING_PASS_DATAFLOW_INVALID:" + ";".join(issues))
    if not callable(execute_pass) or not callable(research_audit):
        raise WritingPassExecutionError("WRITING_PASS_EXECUTOR_AND_RESEARCH_AUDIT_REQUIRED")
    initial = dict(seed_inputs)
    missing = PRE_RESEARCH_EXTERNAL_INPUTS - set(initial)
    if missing:
        raise WritingPassExecutionError(
            "WRITING_PASS_EXTERNAL_INPUTS_MISSING:" + ",".join(sorted(missing))
        )
    if RESEARCH_AUDIT_BOUNDARY_INPUT in initial:
        raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_PRESEED_FORBIDDEN")
    current = dict(initial)
    trace: list[dict[str, Any]] = []
    for node in execution_order():
        if node == WritingPass.STORY_ARCHITECTURE:
            envelope = research_audit(dict(current))
            if (not isinstance(envelope, Mapping) or envelope.get("status") != "PASS"
                    or not isinstance(envelope.get("evidence_refs"), list)
                    or not envelope["evidence_refs"]
                    or not envelope.get(RESEARCH_AUDIT_BOUNDARY_INPUT)):
                raise WritingPassExecutionError("WRITING_RESEARCH_AUDIT_NOT_ADMITTED")
            current[RESEARCH_AUDIT_BOUNDARY_INPUT] = envelope[RESEARCH_AUDIT_BOUNDARY_INPUT]
            trace.append({
                "pass": "RESEARCH_AUDIT_BOUNDARY",
                "status": "CALLBACK_ADMITTED__REAL_SEMANTIC_SUPPORT_NOT_SELF_CERTIFIED",
                "evidence_refs": list(envelope["evidence_refs"]),
            })
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
                f"WRITING_PASS_EXECUTION_FAILED:{node.value}"
            ) from exc
        if not isinstance(outcome, Mapping):
            raise WritingPassExecutionError(f"WRITING_PASS_OUTPUT_INVALID:{node.value}")
        absent = [name for name in contract.outputs if name not in outcome
                  or outcome[name] is None]
        if absent:
            raise WritingPassExecutionError(
                f"WRITING_PASS_OUTPUT_MISSING:{node.value}:{','.join(absent)}"
            )
        unexpected = set(outcome) - set(contract.outputs)
        if unexpected:
            raise WritingPassExecutionError(
                f"WRITING_PASS_UNDECLARED_OUTPUT:{node.value}:{','.join(sorted(unexpected))}"
            )
        current.update(outcome)
        trace.append({
            "pass": node.value,
            "status": "EXECUTOR_CALLBACK_RETURNED_REQUIRED_OUTPUTS__SEMANTIC_QUALITY_OPEN",
            "outputs": list(contract.outputs),
        })
    return {
        "schema_version": "1.0",
        "pass_count": len(PASS_CONTRACTS),
        "research_audit_boundary_reached": True,
        "trace": trace,
        "products": current,
        "assurance": "PASS_CALLBACK_DATAFLOW_EXECUTED__NOT_INDEPENDENT_EDITORIAL_OR_FACT_ACCEPTANCE",
    }
