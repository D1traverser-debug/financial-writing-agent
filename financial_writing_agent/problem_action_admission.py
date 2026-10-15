from __future__ import annotations

from enum import Enum
from typing import Iterable

from .cognition_governance import DecisionEnvelope, EvolutionDisposition, OperationClass, admission_errors


class ProblemActionAdmissionError(RuntimeError):
    pass


class ProblemClosureDecision(str, Enum):
    CLEAN_NO_PROBLEM = "CLEAN_NO_PROBLEM"
    REPAIR_EXECUTED = "REPAIR_EXECUTED"
    BLOCKED_WITH_REASON = "BLOCKED_WITH_REASON"
    NO_CHANGE_WITH_EVIDENCE = "NO_CHANGE_WITH_EVIDENCE"
    PARENT_GUIDANCE_REQUIRED = "PARENT_GUIDANCE_REQUIRED"


def _clean(values: Iterable[str] | None) -> tuple[str, ...]:
    return tuple(value.strip() for value in (values or ()) if isinstance(value, str) and value.strip())


def finalize_problem_action(
    envelope: DecisionEnvelope,
    *,
    repair_path_available: bool,
    owner_authorized: bool,
    explicit_user_choice_required: bool,
    repair_attempted: bool,
    repair_verified: bool,
    blocker_reason: str | None = None,
    no_change_evidence: Iterable[str] | None = None,
    parent_upcall_ref: str | None = None,
) -> ProblemClosureDecision:
    """Enforce DecisionEnvelope -> RootScopeReceipt -> EvolutionDisposition -> action.

    Financial keeps one causal model in ``cognition_governance``.  This module is a thin
    action gate only; it must not introduce a second hypothesis/root-scope representation.
    """

    if not envelope.problem_triggered:
        return ProblemClosureDecision.CLEAN_NO_PROBLEM

    blocker = blocker_reason.strip() if isinstance(blocker_reason, str) else ""
    no_change = _clean(no_change_evidence)

    # A genuinely user-controlled decision can block without pretending root cause is known.
    if explicit_user_choice_required and blocker:
        return ProblemClosureDecision.BLOCKED_WITH_REASON

    errors = admission_errors(envelope)
    if errors:
        raise ProblemActionAdmissionError(
            "problem action denied: DecisionEnvelope admission failed: " + "; ".join(errors)
        )

    root_scope = envelope.root_scope_receipt()
    if root_scope is None:
        raise ProblemActionAdmissionError("problem action denied: root-scope receipt is missing")
    if not isinstance(envelope.evolution_disposition, EvolutionDisposition):
        raise ProblemActionAdmissionError("problem action denied: typed evolution disposition is missing")

    durable_required = bool(
        envelope.operation_class is OperationClass.MATERIAL_JUDGMENT
        or envelope.systemic_problem_signal
        or envelope.architecture_or_governance_change
        or envelope.evolution_disposition
        in {EvolutionDisposition.DOMAIN_CANDIDATE, EvolutionDisposition.PARENT_UPCALL}
    )
    if durable_required and not (
        isinstance(envelope.problem_record_ref, str) and envelope.problem_record_ref.strip()
    ):
        raise ProblemActionAdmissionError(
            "problem action denied: material/evolution-relevant problem requires durable problem_record_ref"
        )

    if envelope.evolution_disposition is EvolutionDisposition.PARENT_UPCALL:
        if repair_path_available and owner_authorized:
            raise ProblemActionAdmissionError(
                "problem action denied: parent upcall cannot bypass an admitted owner-authorized repair"
            )
        if not (isinstance(parent_upcall_ref, str) and parent_upcall_ref.strip()):
            raise ProblemActionAdmissionError(
                "problem action denied: PARENT_UPCALL requires a structured parent-upcall reference"
            )
        return ProblemClosureDecision.PARENT_GUIDANCE_REQUIRED

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
        "problem action denied: no verified repair, concrete blocker, evidence-backed no-change, or governed parent upcall"
    )
