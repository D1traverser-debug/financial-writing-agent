import pytest

from financial_writing_agent.cognition_governance import (
    CandidateOption,
    DecisionEnvelope,
    EvidenceKind,
    EvidenceRef,
    EvolutionDisposition,
    HypothesisDisposition,
    OperationClass,
    ProblemLayer,
    RootScopeHypothesis,
    SearchSaturation,
    SearchSweep,
)
from financial_writing_agent.problem_action_admission import (
    ProblemActionAdmissionError,
    ProblemClosureDecision,
    finalize_problem_action,
)


def _alt(cid: str) -> CandidateOption:
    return CandidateOption(
        candidate_id=cid,
        mechanism=f"mechanism {cid}",
        advantages=["advantage"],
        failure_modes=["failure"],
        fit_conditions=["fit"],
        misfit_conditions=["misfit"],
    )


def _saturation() -> SearchSaturation:
    return SearchSaturation(
        sweeps=[
            SearchSweep(
                sweep_no=1,
                query_or_scope="broad problem scan",
                source_families=["repository", "engineering-method"],
                new_failure_modes=["premature repair"],
                changed_decision=True,
            ),
            SearchSweep(
                sweep_no=2,
                query_or_scope="counterexample scan",
                source_families=["trajectory-eval", "architecture"],
            ),
            SearchSweep(
                sweep_no=3,
                query_or_scope="saturation scan",
                source_families=["sre", "writing-system"],
            ),
        ],
        stop_reason="two stable heterogeneous sweeps",
    )


def _root(hid: str, layer: ProblemLayer, disposition: HypothesisDisposition, *, support: str, probe: str) -> RootScopeHypothesis:
    return RootScopeHypothesis(
        hypothesis_id=hid,
        layer=layer,
        statement=f"candidate root {hid}",
        disposition=disposition,
        supporting_evidence_refs=[support],
        falsification_or_rejection_refs=[probe],
    )


def _envelope(*, selected_support: str = "repo-failure") -> DecisionEnvelope:
    return DecisionEnvelope(
        decision_id="FIN-CB13-1",
        operation="diagnose and repair repeated writing-system failure",
        objective="repair the causal layer rather than the first symptom",
        operation_class=OperationClass.MATERIAL_JUDGMENT,
        problem_triggered=True,
        systemic_problem_signal=True,
        evidence=[
            EvidenceRef(
                ref="repo-failure",
                kind=EvidenceKind.CURRENT_FACT,
                summary="current owner path reproduces the failure",
                source_family="repository",
            ),
            EvidenceRef(
                ref="method",
                kind=EvidenceKind.EXTERNAL_METHOD,
                summary="root-cause method requires falsification before repair",
                source_family="engineering-method",
            ),
            EvidenceRef(
                ref="counterexample",
                kind=EvidenceKind.COUNTEREXAMPLE,
                summary="same symptom can arise from another layer",
                source_family="trajectory-eval",
            ),
        ],
        assumptions_challenged=["first repairable symptom is the root cause"],
        root_scope_hypotheses=[
            _root(
                "workflow",
                ProblemLayer.DOMAIN_WORKFLOW,
                HypothesisDisposition.SELECTED,
                support=selected_support,
                probe="counterexample",
            ),
            _root(
                "architecture",
                ProblemLayer.DOMAIN_ARCHITECTURE,
                HypothesisDisposition.REJECTED,
                support="method",
                probe="counterexample",
            ),
        ],
        selected_root_hypothesis_id="workflow",
        architecture_reassessment_refs=["docs/architecture.md#reassessed"],
        problem_record_ref="evals/EVOLUTION_INDEX.json#FIN-CB13",
        alternatives=[_alt("LOCAL_REPAIR"), _alt("ARCH_REPAIR")],
        counterexamples=["local repair can pass while an upstream cause remains"],
        rejected_paths=["patch first and explain later"],
        selected_candidate_id="LOCAL_REPAIR",
        selection_rationale="workflow cause survived falsification after architecture check",
        saturation=_saturation(),
        verification_plan=["trajectory regression", "production reread"],
        evolution_disposition=EvolutionDisposition.NO_EVOLUTION,
    )


def test_grounded_owner_repair_executes_only_after_full_admission():
    result = finalize_problem_action(
        _envelope(),
        repair_path_available=True,
        owner_authorized=True,
        explicit_user_choice_required=False,
        repair_attempted=True,
        repair_verified=True,
    )
    assert result is ProblemClosureDecision.REPAIR_EXECUTED


def test_root_hypothesis_cannot_cite_evidence_absent_from_decision_envelope():
    with pytest.raises(ProblemActionAdmissionError, match="absent from DecisionEnvelope"):
        finalize_problem_action(
            _envelope(selected_support="invented-ref"),
            repair_path_available=True,
            owner_authorized=True,
            explicit_user_choice_required=False,
            repair_attempted=True,
            repair_verified=True,
        )


def test_selected_root_cause_cannot_rely_only_on_external_method_or_user_framing():
    with pytest.raises(ProblemActionAdmissionError, match="observed or testable evidence"):
        finalize_problem_action(
            _envelope(selected_support="method"),
            repair_path_available=True,
            owner_authorized=True,
            explicit_user_choice_required=False,
            repair_attempted=True,
            repair_verified=True,
        )


def test_owner_authorized_repair_cannot_be_recommendation_only():
    with pytest.raises(ProblemActionAdmissionError, match="was not attempted"):
        finalize_problem_action(
            _envelope(),
            repair_path_available=True,
            owner_authorized=True,
            explicit_user_choice_required=False,
            repair_attempted=False,
            repair_verified=False,
        )


def test_real_user_choice_can_block_without_fabricating_root_cause_completion():
    result = finalize_problem_action(
        _envelope(),
        repair_path_available=False,
        owner_authorized=False,
        explicit_user_choice_required=True,
        repair_attempted=False,
        repair_verified=False,
        blocker_reason="explicit publication approval is required",
    )
    assert result is ProblemClosureDecision.BLOCKED_WITH_REASON
