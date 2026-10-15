from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class WritingPass(str, Enum):
    KNOWLEDGE_RECALL = "KNOWLEDGE_RECALL"
    RESEARCH_DISCOVERY = "RESEARCH_DISCOVERY"
    RESEARCH_ADVERSARIAL = "RESEARCH_ADVERSARIAL"
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
        outputs=("value_chain_map", "company_universe", "evidence_ledger", "candidate_hypotheses"),
    ),
    WritingPass.RESEARCH_ADVERSARIAL: PassContract(
        purpose="search for contradictions, missing chain nodes, disconfirming companies and alternative causal explanations",
        required_inputs=("discovery_package",),
        forbidden_jobs=("protect preferred thesis", "publication prose"),
        outputs=("counterevidence", "rejected_hypotheses", "search_saturation_evidence"),
    ),
    WritingPass.THESIS_ADJUDICATION: PassContract(
        purpose="compare credible candidate explanations and select or merge the best evidence-bounded thesis",
        required_inputs=("discovery_package", "adversarial_package", "decision_envelope"),
        forbidden_jobs=("invent evidence", "draft paragraphs"),
        outputs=("selected_thesis", "company_decision_map", "change_conditions"),
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
    WritingPass.THESIS_ADJUDICATION: (WritingPass.RESEARCH_DISCOVERY, WritingPass.RESEARCH_ADVERSARIAL),
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
    return errors
