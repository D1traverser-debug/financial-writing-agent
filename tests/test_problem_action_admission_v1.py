import pytest

from financial_writing_agent.cognition_governance import (
    CandidateOption,
    DecisionEnvelope,
    EvidenceKind,
    EvidenceRef,
    EvolutionDisposition,
    OperationClass,
    SearchSaturation,
    SearchSweep,
)
from financial_writing_agent.problem_action_admission import (
    HypothesisDisposition,
    ProblemActionAdmissionError,
    ProblemClosureDecision,
    ProblemLayer,
    RootScopeHypothesis,
    finalize_problem_action,
    require_root_scope_admission,
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
                source_families=["repository", "external-method"],
                new_failure_modes=["premature repair"],
                changed_decision=True,
            ),
            SearchSweep(
                sweep_no=2,
                query_or_scope="counterexample scan",
                source_families=["agent-evals", "architecture"],
            ),
            SearchSweep(
                sweep_no=3,
                query_or_scope="saturation scan",
                source_families=["sre", "writing-system"],
            ),
        ],
        stop_reason="two stable heterogeneous sweeps",
    )


def _envelope(*, architecture=False, evolution=EvolutionDisposition.NO_EVOLUTION) -> DecisionEnvelope:
    return DecisionEnvelope(
        decision_id="PROBLEM-1",
        operation="diagnose and repair problem",
        objective="repair the correct causal layer without overfitting",
        operation_class=OperationClass.MATERIAL_JUDGMENT,
        problem_triggered=True,
        architecture_or_governance_change=architecture,
        evidence=[
            EvidenceRef(
                ref="repo-failure",
                kind=EvidenceKind.CURRENT_FACT,
                summary="current repository behavior reproduces the failure",
                source_family="repository",
            ),
            EvidenceRef(
                ref="external-method",
                kind=EvidenceKind.EXTERNAL_METHOD,
                summary="root cause before repair; falsify alternatives",
                source_family="engineering-method",
            ),
            EvidenceRef(
                ref="counterexample",
                kind=EvidenceKind.COUNTEREXAMPLE,
                summary="same symptom can have a different causal layer",
                source_family="trajectory-eval",
            ),
        ],
        assumptions_challenged=["first repairable symptom is the root cause"],
        alternatives=[_alt("LOCAL_FIX"), _alt("ARCH_REPAIR")],
        counterexamples=["local repair can pass while upstream cause remains"],
        rejected_paths=["patch first and explain later"],
        selected_candidate_id="LOCAL_FIX",
        selection_rationale="local cause survives falsification after upstream check",
        saturation=_saturation(),
        verification_plan=["trajectory regression", "production reread"],
        evolution_disposition=evolution,
    )


def _hypothesis(hid, layer, disposition, support="repo-failure"):
    return RootScopeHypothesis(
        hypothesis_id=hid,
        layer=layer,
        statement=f"candidate cause at {layer.value}",
        disposition=disposition,
        supporting_envelope_evidence_refs=(support,),
        falsification_or_rejection_refs=(f"probe:{hid}",),
    )


def _root():
    return require_root_scope_admission(
        _envelope(),
        hypotheses=(
            _hypothesis("local", ProblemLayer.ARTICLE_WORKFLOW, HypothesisDisposition.SELECTED),
            _hypothesis("architecture", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.REJECTED, "external-method"),
        ),
        selected_hypothesis_id="local",
        architecture_reassessment_refs=("docs/architecture.md#reassessed",),
    )


def test_material_financial_problem_requires_cross_layer_root_scope():
    with pytest.raises(ProblemActionAdmissionError, match="at least two layers"):
        require_root_scope_admission(
            _envelope(),
            hypotheses=(
                _hypothesis("local", ProblemLayer.ARTICLE_WORKFLOW, HypothesisDisposition.SELECTED),
                _hypothesis("local2", ProblemLayer.ARTICLE_WORKFLOW, HypothesisDisposition.REJECTED),
            ),
            selected_hypothesis_id="local",
            architecture_reassessment_refs=("docs/architecture.md#reassessed",),
        )


def test_user_or_external_framing_cannot_be_promoted_directly():
    with pytest.raises(ProblemActionAdmissionError, match="promoted without falsification"):
        require_root_scope_admission(
            _envelope(architecture=True),
            hypotheses=(
                _hypothesis("architecture", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.SELECTED),
                _hypothesis("local", ProblemLayer.ARTICLE_WORKFLOW, HypothesisDisposition.REJECTED),
            ),
            selected_hypothesis_id="architecture",
            architecture_reassessment_refs=("docs/architecture.md#reassessed",),
            direct_user_or_external_claim_promoted_without_test=True,
        )


def test_root_hypotheses_must_be_grounded_in_decision_envelope_evidence():
    with pytest.raises(ProblemActionAdmissionError, match="not grounded"):
        require_root_scope_admission(
            _envelope(),
            hypotheses=(
                _hypothesis("local", ProblemLayer.ARTICLE_WORKFLOW, HypothesisDisposition.SELECTED, "invented-ref"),
                _hypothesis("architecture", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.REJECTED, "external-method"),
            ),
            selected_hypothesis_id="local",
            architecture_reassessment_refs=("docs/architecture.md#reassessed",),
        )


def test_repairable_problem_cannot_skip_root_scope():
    with pytest.raises(ProblemActionAdmissionError, match="root-scope receipt"):
        finalize_problem_action(
            _envelope(),
            root_scope_receipt=None,
            repair_path_available=True,
            owner_authorized=True,
            explicit_user_choice_required=False,
            repair_attempted=True,
            repair_verified=True,
        )


def test_material_problem_requires_durable_problem_evidence():
    with pytest.raises(ProblemActionAdmissionError, match="durable causal evidence"):
        finalize_problem_action(
            _envelope(),
            root_scope_receipt=_root(),
            repair_path_available=True,
            owner_authorized=True,
            explicit_user_choice_required=False,
            repair_attempted=True,
            repair_verified=True,
        )


def test_admitted_owner_repair_must_execute_and_verify():
    envelope = _envelope()
    root = _root()
    with pytest.raises(ProblemActionAdmissionError, match="was not attempted"):
        finalize_problem_action(
            envelope,
            root_scope_receipt=root,
            repair_path_available=True,
            owner_authorized=True,
            explicit_user_choice_required=False,
            repair_attempted=False,
            repair_verified=False,
            durable_problem_ref="evals/EVOLUTION_INDEX.json#F-20261016-CB13",
        )

    assert finalize_problem_action(
        envelope,
        root_scope_receipt=root,
        repair_path_available=True,
        owner_authorized=True,
        explicit_user_choice_required=False,
        repair_attempted=True,
        repair_verified=True,
        durable_problem_ref="evals/EVOLUTION_INDEX.json#F-20261016-CB13",
    ) is ProblemClosureDecision.REPAIR_EXECUTED


def test_real_user_choice_can_block_without_fake_root_cause_claim():
    assert finalize_problem_action(
        _envelope(),
        root_scope_receipt=None,
        repair_path_available=False,
        owner_authorized=False,
        explicit_user_choice_required=True,
        repair_attempted=False,
        repair_verified=False,
        blocker_reason="explicit publication approval is required",
    ) is ProblemClosureDecision.BLOCKED_WITH_REASON
