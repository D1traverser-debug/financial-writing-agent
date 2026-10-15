from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class OperationClass(str, Enum):
    MECHANICAL = "MECHANICAL"
    MATERIAL_JUDGMENT = "MATERIAL_JUDGMENT"


class EvidenceKind(str, Enum):
    USER_FEEDBACK = "USER_FEEDBACK"
    CURRENT_FACT = "CURRENT_FACT"
    PRIOR_KNOWLEDGE = "PRIOR_KNOWLEDGE"
    EXTERNAL_METHOD = "EXTERNAL_METHOD"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    RUN_RESULT = "RUN_RESULT"
    MECHANICAL_RESULT = "MECHANICAL_RESULT"


class KnowledgeKind(str, Enum):
    STRUCTURAL = "STRUCTURAL"
    OPERATING = "OPERATING"
    EPHEMERAL = "EPHEMERAL"
    METHOD = "METHOD"
    FAILURE_PATTERN = "FAILURE_PATTERN"


class KnowledgeStatus(str, Enum):
    RAW = "RAW"
    CANDIDATE = "CANDIDATE"
    VALIDATED = "VALIDATED"
    CONFLICTED = "CONFLICTED"
    RETIRED = "RETIRED"


class EvolutionDisposition(str, Enum):
    NO_EVOLUTION = "NO_EVOLUTION"
    EVIDENCE_ONLY = "EVIDENCE_ONLY"
    DOMAIN_CANDIDATE = "DOMAIN_CANDIDATE"
    PARENT_UPCALL = "PARENT_UPCALL"


class ProblemLayer(str, Enum):
    LOCAL_IMPLEMENTATION = "LOCAL_IMPLEMENTATION"
    DOMAIN_WORKFLOW = "DOMAIN_WORKFLOW"
    DOMAIN_ARCHITECTURE = "DOMAIN_ARCHITECTURE"
    COMMON_CAPABILITY = "COMMON_CAPABILITY"
    CONTROL_PLANE = "CONTROL_PLANE"
    HOST = "HOST"
    REQUIREMENT_OR_GOAL = "REQUIREMENT_OR_GOAL"


class HypothesisDisposition(str, Enum):
    PLAUSIBLE = "PLAUSIBLE"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


class EvidenceRef(StrictModel):
    ref: str = Field(min_length=1)
    kind: EvidenceKind
    summary: str = Field(min_length=1)
    source_family: str = Field(min_length=1)
    observed_at: str | None = None


class SearchSweep(StrictModel):
    sweep_no: int = Field(ge=1)
    query_or_scope: str = Field(min_length=1)
    source_families: list[str] = Field(min_length=1)
    new_material_candidates: list[str] = Field(default_factory=list)
    new_failure_modes: list[str] = Field(default_factory=list)
    new_counterexamples: list[str] = Field(default_factory=list)
    changed_decision: bool = False

    @model_validator(mode="after")
    def validate_source_families(self):
        normalized = [family.casefold().strip() for family in self.source_families]
        if any(not family for family in normalized):
            raise ValueError("search source_families cannot contain blank values")
        if len(normalized) != len(set(normalized)):
            raise ValueError("search source_families must be unique after normalization")
        return self

    @property
    def material_delta(self) -> bool:
        return bool(
            self.new_material_candidates
            or self.new_failure_modes
            or self.new_counterexamples
            or self.changed_decision
        )


class SearchSaturation(StrictModel):
    sweeps: list[SearchSweep] = Field(min_length=2)
    stop_reason: str = Field(min_length=1)
    unresolved_search_gaps: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_two_stable_sweeps(self):
        ordered = sorted(self.sweeps, key=lambda x: x.sweep_no)
        if [s.sweep_no for s in ordered] != list(range(1, len(ordered) + 1)):
            raise ValueError("search sweep numbers must be contiguous from 1")
        final_pair = ordered[-2:]
        if any(sweep.material_delta for sweep in final_pair):
            raise ValueError(
                "material search may stop only after two consecutive sweeps add no decision-changing "
                "candidate, failure mode, counterexample, or changed decision"
            )
        final_scopes = {sweep.query_or_scope.casefold().strip() for sweep in final_pair}
        if len(final_scopes) < 2:
            raise ValueError(
                "the final two stable search sweeps must use different query/scope definitions; "
                "repeating the same search does not establish saturation"
            )
        final_family_sets = {
            tuple(sorted({family.casefold().strip() for family in sweep.source_families}))
            for sweep in final_pair
        }
        if len(final_family_sets) < 2:
            raise ValueError(
                "the final two stable search sweeps must use different source-family sets; "
                "renaming the query while repeating the same source mix does not establish saturation"
            )
        families = {family.casefold().strip() for sweep in ordered for family in sweep.source_families}
        if len(families) < 2:
            raise ValueError("material search requires at least two materially different source families")
        return self


class CandidateOption(StrictModel):
    candidate_id: str = Field(min_length=1)
    mechanism: str = Field(min_length=1)
    advantages: list[str] = Field(min_length=1)
    failure_modes: list[str] = Field(min_length=1)
    fit_conditions: list[str] = Field(min_length=1)
    misfit_conditions: list[str] = Field(min_length=1)


class RootScopeHypothesis(StrictModel):
    hypothesis_id: str = Field(min_length=1)
    layer: ProblemLayer
    statement: str = Field(min_length=1)
    disposition: HypothesisDisposition
    supporting_evidence_refs: list[str] = Field(min_length=1)
    falsification_or_rejection_refs: list[str] = Field(min_length=1)


class RootScopeReceipt(StrictModel):
    selected_hypothesis_id: str = Field(min_length=1)
    selected_layer: ProblemLayer
    compared_layers: list[ProblemLayer] = Field(min_length=1)
    rejected_hypothesis_ids: list[str] = Field(default_factory=list)
    architecture_reassessment_refs: list[str] = Field(default_factory=list)
    evidence_refs: list[str] = Field(min_length=1)


class KnowledgeRecord(StrictModel):
    knowledge_id: str = Field(min_length=1)
    kind: KnowledgeKind
    status: KnowledgeStatus
    claim_or_method: str = Field(min_length=1)
    scope: str = Field(min_length=1)
    evidence_refs: list[str] = Field(min_length=1)
    confidence: Literal["high", "medium", "low"]
    learned_at: str
    revalidation_trigger: str = Field(min_length=1)
    conflicts: list[str] = Field(default_factory=list)
    supersedes: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def conflict_status_matches(self):
        if self.conflicts and self.status == KnowledgeStatus.VALIDATED:
            raise ValueError("knowledge with unresolved conflicts cannot be VALIDATED")
        return self


class DecisionEnvelope(StrictModel):
    decision_id: str = Field(min_length=1)
    operation: str = Field(min_length=1)
    objective: str = Field(min_length=1)
    operation_class: OperationClass
    problem_triggered: bool = False
    architecture_or_governance_change: bool = False
    systemic_problem_signal: bool = False
    evidence: list[EvidenceRef] = Field(min_length=1)
    learned_items: list[str] = Field(default_factory=list)
    categories_or_models_used: list[str] = Field(default_factory=list)
    assumptions_challenged: list[str] = Field(default_factory=list)
    root_scope_hypotheses: list[RootScopeHypothesis] = Field(default_factory=list)
    selected_root_hypothesis_id: str | None = None
    architecture_reassessment_refs: list[str] = Field(default_factory=list)
    direct_user_or_external_claim_promoted_without_test: bool = False
    problem_record_ref: str | None = None
    alternatives: list[CandidateOption] = Field(default_factory=list)
    counterexamples: list[str] = Field(default_factory=list)
    rejected_paths: list[str] = Field(default_factory=list)
    selected_candidate_id: str | None = None
    selection_rationale: str = ""
    saturation: SearchSaturation | None = None
    verification_plan: list[str] = Field(default_factory=list)
    knowledge_writeback_candidates: list[KnowledgeRecord] = Field(default_factory=list)
    evolution_disposition: EvolutionDisposition = EvolutionDisposition.NO_EVOLUTION
    remaining_unknowns: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def material_decision_is_fail_closed(self):
        if self.operation_class == OperationClass.MECHANICAL:
            if self.selected_candidate_id and self.alternatives:
                ids = {a.candidate_id for a in self.alternatives}
                if self.selected_candidate_id not in ids:
                    raise ValueError("selected_candidate_id must identify a declared alternative")
            return self

        kinds = {item.kind for item in self.evidence}
        non_user_kinds = kinds - {EvidenceKind.USER_FEEDBACK}
        if not non_user_kinds:
            raise ValueError("material judgment requires evidence beyond user feedback")
        if (self.problem_triggered or self.architecture_or_governance_change) and EvidenceKind.EXTERNAL_METHOD not in kinds:
            raise ValueError("problem-triggered or architecture/governance judgment requires EXTERNAL_METHOD evidence")
        if len(self.alternatives) < 2:
            raise ValueError("material judgment requires at least two credible alternatives")
        ids = [item.candidate_id for item in self.alternatives]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate ids must be unique")
        if not self.selected_candidate_id or self.selected_candidate_id not in set(ids):
            raise ValueError("material judgment must select one declared candidate")
        if not self.selection_rationale:
            raise ValueError("material judgment requires selection rationale")
        if not self.assumptions_challenged:
            raise ValueError("material judgment requires at least one challenged assumption")
        if not self.counterexamples:
            raise ValueError("material judgment requires counterexample/adversarial evidence")
        if not self.rejected_paths:
            raise ValueError("material judgment requires explicit rejected paths")
        if self.saturation is None:
            raise ValueError("material judgment requires search saturation evidence")
        if not self.verification_plan:
            raise ValueError("material judgment requires a verification plan")

        if self.problem_triggered:
            if self.direct_user_or_external_claim_promoted_without_test:
                raise ValueError("problem root scope cannot promote user/external framing without falsification")
            if not self.root_scope_hypotheses or not self.selected_root_hypothesis_id:
                raise ValueError("problem-triggered material judgment requires root-scope hypotheses and selection")
            root_ids = [item.hypothesis_id for item in self.root_scope_hypotheses]
            if len(root_ids) != len(set(root_ids)):
                raise ValueError("root-scope hypothesis ids must be unique")
            selected_roots = [
                item for item in self.root_scope_hypotheses
                if item.hypothesis_id == self.selected_root_hypothesis_id
            ]
            if len(selected_roots) != 1 or selected_roots[0].disposition != HypothesisDisposition.SELECTED:
                raise ValueError("selected_root_hypothesis_id must identify the one SELECTED root hypothesis")
            if sum(item.disposition == HypothesisDisposition.SELECTED for item in self.root_scope_hypotheses) != 1:
                raise ValueError("exactly one root-scope hypothesis may be SELECTED")

            systemic = self.systemic_problem_signal or self.architecture_or_governance_change
            if systemic:
                layers = {item.layer for item in self.root_scope_hypotheses}
                if len(self.root_scope_hypotheses) < 2 or len(layers) < 2:
                    raise ValueError("systemic problem requires root hypotheses across at least two problem layers")
                if not any(item.disposition == HypothesisDisposition.REJECTED for item in self.root_scope_hypotheses):
                    raise ValueError("systemic problem requires an evidence-rejected root hypothesis")
                upstream = {
                    ProblemLayer.DOMAIN_ARCHITECTURE,
                    ProblemLayer.COMMON_CAPABILITY,
                    ProblemLayer.CONTROL_PLANE,
                    ProblemLayer.HOST,
                    ProblemLayer.REQUIREMENT_OR_GOAL,
                }
                if not any(item.layer in upstream for item in self.root_scope_hypotheses):
                    raise ValueError("systemic problem requires an architecture/upstream root hypothesis")
                if not self.architecture_reassessment_refs:
                    raise ValueError("systemic problem requires architecture reassessment evidence")

            if self.evolution_disposition in {EvolutionDisposition.DOMAIN_CANDIDATE, EvolutionDisposition.PARENT_UPCALL} and not self.problem_record_ref:
                raise ValueError("evolution-relevant problem requires a durable problem_record_ref")
        return self

    def root_scope_receipt(self) -> RootScopeReceipt | None:
        if not self.problem_triggered or not self.selected_root_hypothesis_id:
            return None
        selected = next(
            item for item in self.root_scope_hypotheses
            if item.hypothesis_id == self.selected_root_hypothesis_id
        )
        layers = sorted({item.layer for item in self.root_scope_hypotheses}, key=lambda item: item.value)
        rejected = sorted(
            item.hypothesis_id
            for item in self.root_scope_hypotheses
            if item.disposition == HypothesisDisposition.REJECTED
        )
        refs = sorted({
            *selected.supporting_evidence_refs,
            *selected.falsification_or_rejection_refs,
            *self.architecture_reassessment_refs,
        })
        return RootScopeReceipt(
            selected_hypothesis_id=selected.hypothesis_id,
            selected_layer=selected.layer,
            compared_layers=layers,
            rejected_hypothesis_ids=rejected,
            architecture_reassessment_refs=self.architecture_reassessment_refs,
            evidence_refs=refs,
        )


def admission_errors(envelope: DecisionEnvelope) -> list[str]:
    """Semantic warnings beyond shape validation; does not overstate independence."""
    errors: list[str] = []
    if envelope.operation_class == OperationClass.MATERIAL_JUDGMENT:
        families = {e.source_family.casefold().strip() for e in envelope.evidence}
        if len(families) < 2:
            errors.append("material judgment evidence is single-family")
        if all(e.kind == EvidenceKind.USER_FEEDBACK for e in envelope.evidence):
            errors.append("user feedback cannot be the sole evidence for a material judgment")
        if (envelope.problem_triggered or envelope.architecture_or_governance_change) and not any(
            e.kind == EvidenceKind.EXTERNAL_METHOD for e in envelope.evidence
        ):
            errors.append("triggered problem/architecture decision lacks required external method evidence")
        if envelope.problem_triggered and envelope.root_scope_receipt() is None:
            errors.append("problem-triggered decision lacks an admitted root-scope receipt")
        if envelope.evolution_disposition in {
            EvolutionDisposition.DOMAIN_CANDIDATE,
            EvolutionDisposition.PARENT_UPCALL,
        } and not envelope.knowledge_writeback_candidates:
            errors.append("evolution-relevant decision needs durable learning/writeback candidate evidence")
    return errors
