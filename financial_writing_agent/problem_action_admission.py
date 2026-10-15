from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .cognition_governance import (
    DecisionEnvelope,
    EvolutionDisposition,
    OperationClass,
    admission_errors,
)


class ProblemActionAdmissionError(RuntimeError):
    pass


class ProblemLayer(str, Enum):
    LOCAL_ARTICLE_OR_TOOL = "LOCAL_ARTICLE_OR_TOOL"
    ARTICLE_WORKFLOW = "ARTICLE_WORKFLOW"
    DOMAIN_ARCHITECTURE = "DOMAIN_ARCHITECTURE"
    COMMON_CAPABILITY = "COMMON_CAPABILITY"
    PARENT_CONTROL_PLANE = "PARENT_CONTROL_PLANE"
    HOST = "HOST"
    REQUIREMENT_OR_GOAL = "REQUIREMENT_OR_GOAL"


class HypothesisDisposition(str, Enum):
    PLAUSIBLE = "PLAUSIBLE"
    SELECTED = "SELECTED"
    REJECTED = "REJECTED"


class ProblemClosureDecision(str, Enum):
    CLEAN_NO_PROBLEM = "CLEAN_NO_PROBLEM"
    REPAIR_EXECUTED = "REPAIR_EXECUTED"
    BLOCKED_WITH_REASON = "BLOCKED_WITH_REASON"
    NO_CHANGE_WITH_EVIDENCE = "NO_CHANGE_WITH_EVIDENCE"


@dataclass(frozen=True, slots=True)
class RootScopeHypothesis:
    hypothesis_id: str
    layer: ProblemLayer
    statement: str
    disposition: HypothesisDisposition
    supporting_envelope_evidence_refs: tuple[str, ...]
    falsification_or_rejection_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.hypothesis_id.strip() or not self.statement.strip():
            raise ValueError("root-scope hypothesis requires identity and statement")
        if not self.supporting_envelope_evidence_refs:
            raise ValueError("root-scope hypothesis requires DecisionEnvelope evidence refs")
        if not self.falsification_or_rejection_refs:
            raise ValueError("root-scope hypothesis requires falsification/rejection evidence")


@dataclass(frozen=True, slots=True)
class RootScopeReceipt:
    decision_id: str
    selected_hypothesis_id: str
    selected_layer: ProblemLayer
    compared_layers: tuple[ProblemLayer, ...]
    hypothesis_count: int
    decision_envelope_admitted: bool
    architecture_reassessment_performed: bool
    durable_problem_record_required: bool
    evidence_refs: tuple[str, ...]


_UPSTREAM_LAYERS = {
    ProblemLayer.DOMAIN_ARCHITECTURE,
    ProblemLayer.COMMON_CAPABILITY,
    ProblemLayer.PARENT_CONTROL_PLANE,
    ProblemLayer.HOST,
    ProblemLayer.REQUIREMENT_OR_GOAL,
}


def _clean(values: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(value.strip() for value in (values or ()) if isinstance(value, str) and value.strip())


def require_root_scope_admission(
    envelope: DecisionEnvelope,
    *,
    hypotheses: tuple[RootScopeHypothesis, ...],
    selected_hypothesis_id: str,
    repeated_failure: bool = False,
    cross_subsystem: bool = False,
    complexity_growth: bool = False,
    scope_expansion: bool = False,
    architecture_reassessment_refs: Iterable[str] | None = None,
    direct_user_or_external_claim_promoted_without_test: bool = False,
) -> RootScopeReceipt:
    """Bridge an admitted Financial DecisionEnvelope into a causal root-scope receipt.

    DecisionEnvelope proves research/challenge/alternatives/counterexamples/search saturation.
    This gate answers the separate question: which layer actually owns the problem?
    """

    if not envelope.problem_triggered:
        raise ProblemActionAdmissionError("root-scope admission requires a problem-triggered DecisionEnvelope")
    envelope_errors = admission_errors(envelope)
    if envelope_errors:
        raise ProblemActionAdmissionError(
            "DecisionEnvelope is not admitted: " + "; ".join(envelope_errors)
        )
    if direct_user_or_external_claim_promoted_without_test:
        raise ProblemActionAdmissionError(
            "root-scope admission denied: user/external framing was promoted without falsification"
        )
    if not hypotheses:
        raise ProblemActionAdmissionError("root-scope admission requires hypotheses")
    if len({item.hypothesis_id for item in hypotheses}) != len(hypotheses):
        raise ProblemActionAdmissionError("root-scope hypothesis identifiers must be unique")

    selected = [item for item in hypotheses if item.hypothesis_id == selected_hypothesis_id]
    if len(selected) != 1 or selected[0].disposition is not HypothesisDisposition.SELECTED:
        raise ProblemActionAdmissionError(
            "exactly one SELECTED hypothesis must match selected_hypothesis_id"
        )
    if sum(item.disposition is HypothesisDisposition.SELECTED for item in hypotheses) != 1:
        raise ProblemActionAdmissionError("exactly one root-scope hypothesis may be SELECTED")

    envelope_refs = {item.ref for item in envelope.evidence}
    for item in hypotheses:
        if not envelope_refs.intersection(item.supporting_envelope_evidence_refs):
            raise ProblemActionAdmissionError(
                f"hypothesis {item.hypothesis_id} is not grounded in DecisionEnvelope evidence"
            )

    architecture_refs = _clean(architecture_reassessment_refs)
    systemic = any(
        (
            envelope.operation_class is OperationClass.MATERIAL_JUDGMENT,
            envelope.architecture_or_governance_change,
            repeated_failure,
            cross_subsystem,
            complexity_growth,
            scope_expansion,
        )
    )
    compared_layers = tuple(sorted({item.layer for item in hypotheses}, key=lambda layer: layer.value))
    if systemic:
        if len(hypotheses) < 2 or len(compared_layers) < 2:
            raise ProblemActionAdmissionError(
                "systemic/material problem requires competing hypotheses across at least two layers"
            )
        if not any(item.disposition is HypothesisDisposition.REJECTED for item in hypotheses):
            raise ProblemActionAdmissionError(
                "systemic/material problem requires at least one evidence-rejected alternative"
            )
        if not any(item.layer in _UPSTREAM_LAYERS for item in hypotheses):
            raise ProblemActionAdmissionError(
                "systemic/material problem must test an architecture/upstream hypothesis"
            )
        if not architecture_refs:
            raise ProblemActionAdmissionError(
                "systemic/material problem requires architecture/upstream reassessment evidence"
            )

    chosen = selected[0]
    durable = bool(
        systemic
        or envelope.evolution_disposition
        in {EvolutionDisposition.DOMAIN_CANDIDATE, EvolutionDisposition.PARENT_UPCALL}
    )
    refs = tuple(
        sorted(
            {
                *chosen.supporting_envelope_evidence_refs,
                *chosen.falsification_or_rejection_refs,
                *architecture_refs,
            }
        )
    )
    return RootScopeReceipt(
        decision_id=envelope.decision_id,
        selected_hypothesis_id=chosen.hypothesis_id,
        selected_layer=chosen.layer,
        compared_layers=compared_layers,
        hypothesis_count=len(hypotheses),
        decision_envelope_admitted=True,
        architecture_reassessment_performed=bool(architecture_refs),
        durable_problem_record_required=durable,
        evidence_refs=refs,
    )


def finalize_problem_action(
    envelope: DecisionEnvelope,
    *,
    root_scope_receipt: RootScopeReceipt | None,
    repair_path_available: bool,
    owner_authorized: bool,
    explicit_user_choice_required: bool,
    repair_attempted: bool,
    repair_verified: bool,
    blocker_reason: str | None = None,
    no_change_evidence: Iterable[str] | None = None,
    durable_problem_ref: str | None = None,
    parent_upcall_ref: str | None = None,
) -> ProblemClosureDecision:
    """Enforce cognition -> root scope -> evolution disposition -> action ordering."""

    if not envelope.problem_triggered:
        return ProblemClosureDecision.CLEAN_NO_PROBLEM

    blocker = blocker_reason.strip() if isinstance(blocker_reason, str) else ""
    no_change = _clean(no_change_evidence)
    if explicit_user_choice_required and blocker:
        return ProblemClosureDecision.BLOCKED_WITH_REASON

    if root_scope_receipt is None:
        raise ProblemActionAdmissionError("problem action denied: root-scope receipt is missing")
    if root_scope_receipt.decision_id != envelope.decision_id:
        raise ProblemActionAdmissionError("root-scope receipt is bound to a different DecisionEnvelope")
    if not isinstance(envelope.evolution_disposition, EvolutionDisposition):
        raise ProblemActionAdmissionError("problem action denied: typed evolution disposition is missing")

    durable_required = bool(
        root_scope_receipt.durable_problem_record_required
        or envelope.evolution_disposition
        in {EvolutionDisposition.DOMAIN_CANDIDATE, EvolutionDisposition.PARENT_UPCALL}
    )
    if durable_required and not (isinstance(durable_problem_ref, str) and durable_problem_ref.strip()):
        raise ProblemActionAdmissionError(
            "problem action denied: material/evolution-relevant problem requires durable causal evidence"
        )
    if envelope.evolution_disposition is EvolutionDisposition.PARENT_UPCALL and not (
        isinstance(parent_upcall_ref, str) and parent_upcall_ref.strip()
    ):
        raise ProblemActionAdmissionError(
            "problem action denied: PARENT_UPCALL requires a structured parent-upcall reference"
        )

    if repair_path_available and owner_authorized:
        if not repair_attempted:
            raise ProblemActionAdmissionError(
                "problem action denied: admitted owner-authorized repair exists but was not attempted"
            )
        if repair_verified:
            return ProblemClosureDecision.REPAIR_EXECUTED
        if blocker:
            return ProblemClosureDecision.BLOCKED_WITH_REASON
        raise ProblemActionAdmissionError(
            "problem action denied: attempted repair is unverified and has no concrete blocker"
        )

    if blocker:
        return ProblemClosureDecision.BLOCKED_WITH_REASON
    if no_change:
        return ProblemClosureDecision.NO_CHANGE_WITH_EVIDENCE
    raise ProblemActionAdmissionError(
        "problem action denied: no verified repair, blocker, or evidence-backed no-change terminal"
    )
