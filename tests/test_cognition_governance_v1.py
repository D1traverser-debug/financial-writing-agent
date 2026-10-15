import pytest
from pydantic import ValidationError

from financial_writing_agent.cognition_governance import (
    CandidateOption,
    DecisionEnvelope,
    EvidenceKind,
    EvidenceRef,
    EvolutionDisposition,
    HypothesisDisposition,
    KnowledgeKind,
    KnowledgeRecord,
    KnowledgeStatus,
    OperationClass,
    ProblemLayer,
    RootScopeHypothesis,
    SearchSaturation,
    SearchSweep,
    admission_errors,
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


def _root(hid: str, layer: ProblemLayer, disposition: HypothesisDisposition) -> RootScopeHypothesis:
    return RootScopeHypothesis(
        hypothesis_id=hid,
        layer=layer,
        statement=f"candidate root {hid}",
        disposition=disposition,
        supporting_evidence_refs=[f"support:{hid}"],
        falsification_or_rejection_refs=[f"probe:{hid}"],
    )


def _saturation() -> SearchSaturation:
    return SearchSaturation(
        sweeps=[
            SearchSweep(
                sweep_no=1,
                query_or_scope="initial architecture scan",
                source_families=["uaos", "external-engineering"],
                new_material_candidates=["single-owner multi-pass"],
                new_failure_modes=["soft self-pass"],
                changed_decision=True,
            ),
            SearchSweep(
                sweep_no=2,
                query_or_scope="counterexample scan",
                source_families=["journalism", "agent-systems"],
            ),
            SearchSweep(
                sweep_no=3,
                query_or_scope="saturation scan",
                source_families=["software-architecture", "writing-research"],
            ),
        ],
        stop_reason="two consecutive sweeps produced no decision-changing delta",
    )


def test_problem_triggered_architecture_judgment_requires_external_method_evidence():
    with pytest.raises(ValidationError):
        DecisionEnvelope(
            decision_id="D1",
            operation="rebuild writing architecture",
            objective="improve reader value",
            operation_class=OperationClass.MATERIAL_JUDGMENT,
            problem_triggered=True,
            architecture_or_governance_change=True,
            evidence=[
                EvidenceRef(
                    ref="user-feedback",
                    kind=EvidenceKind.USER_FEEDBACK,
                    summary="article rejected",
                    source_family="user",
                ),
                EvidenceRef(
                    ref="current-audit",
                    kind=EvidenceKind.CURRENT_FACT,
                    summary="audit self-passed the rejected output",
                    source_family="repository",
                ),
            ],
            alternatives=[_alt("A"), _alt("B")],
            selected_candidate_id="A",
            selection_rationale="A fits",
            assumptions_challenged=["more rules fix writing"],
            counterexamples=["existing rules existed but audit still passed"],
            rejected_paths=["add more prose rules"],
            saturation=_saturation(),
            verification_plan=["regression"],
        )


def test_ordinary_material_thesis_decision_needs_non_user_evidence_but_not_architecture_research():
    envelope = DecisionEnvelope(
        decision_id="TOPIC-1",
        operation="choose article thesis",
        objective="select the strongest evidence-bounded explanation",
        operation_class=OperationClass.MATERIAL_JUDGMENT,
        evidence=[
            EvidenceRef(
                ref="company-report-A",
                kind=EvidenceKind.CURRENT_FACT,
                summary="company evidence",
                source_family="company-filing",
            ),
            EvidenceRef(
                ref="policy-source-B",
                kind=EvidenceKind.CURRENT_FACT,
                summary="policy evidence",
                source_family="government",
            ),
        ],
        assumptions_challenged=["largest macro growth means largest company beneficiary"],
        alternatives=[_alt("THESIS_A"), _alt("THESIS_B")],
        counterexamples=["company-level revenue diverges from macro volume"],
        rejected_paths=["THESIS_A lacks company-level transmission evidence"],
        selected_candidate_id="THESIS_B",
        selection_rationale="THESIS_B survives the company-level counterexample",
        saturation=_saturation(),
        verification_plan=["research audit", "company decision map"],
    )
    assert admission_errors(envelope) == []


def test_search_sweep_rejects_blank_and_normalized_duplicate_source_families():
    with pytest.raises(ValidationError):
        SearchSweep(sweep_no=1, query_or_scope="blank family", source_families=["industry", "   "])
    with pytest.raises(ValidationError):
        SearchSweep(sweep_no=1, query_or_scope="duplicate family", source_families=["Industry", " industry "])


def test_search_saturation_needs_two_consecutive_no_delta_sweeps():
    with pytest.raises(ValidationError):
        SearchSaturation(
            sweeps=[
                SearchSweep(sweep_no=1, query_or_scope="one", source_families=["a", "b"]),
                SearchSweep(
                    sweep_no=2,
                    query_or_scope="two",
                    source_families=["a", "c"],
                    new_failure_modes=["new issue"],
                ),
            ],
            stop_reason="too early",
        )


def test_search_saturation_rejects_repeated_identical_final_sweeps_even_if_earlier_sources_are_diverse():
    with pytest.raises(ValidationError):
        SearchSaturation(
            sweeps=[
                SearchSweep(
                    sweep_no=1,
                    query_or_scope="broad discovery",
                    source_families=["government", "company-filing"],
                    new_material_candidates=["candidate-a"],
                    changed_decision=True,
                ),
                SearchSweep(
                    sweep_no=2,
                    query_or_scope="same terminal search",
                    source_families=["industry"],
                ),
                SearchSweep(
                    sweep_no=3,
                    query_or_scope="same terminal search",
                    source_families=["industry"],
                ),
            ],
            stop_reason="incorrect duplicate terminal sweeps",
        )


def test_search_saturation_rejects_renamed_terminal_sweeps_over_same_source_mix():
    with pytest.raises(ValidationError):
        SearchSaturation(
            sweeps=[
                SearchSweep(
                    sweep_no=1,
                    query_or_scope="broad discovery",
                    source_families=["government", "company-filing"],
                    new_material_candidates=["candidate-a"],
                    changed_decision=True,
                ),
                SearchSweep(
                    sweep_no=2,
                    query_or_scope="counterexample angle",
                    source_families=["industry", "company-filing"],
                ),
                SearchSweep(
                    sweep_no=3,
                    query_or_scope="renamed second angle",
                    source_families=["company-filing", "industry"],
                ),
            ],
            stop_reason="renaming the query is not source diversity",
        )


def test_problem_triggered_material_decision_requires_root_scope_hypotheses():
    with pytest.raises(ValidationError, match="root-scope hypotheses"):
        DecisionEnvelope(
            decision_id="ROOT-MISSING",
            operation="repair systemic writing failure",
            objective="fix the root cause rather than the first symptom",
            operation_class=OperationClass.MATERIAL_JUDGMENT,
            problem_triggered=True,
            evidence=[
                EvidenceRef(ref="current", kind=EvidenceKind.CURRENT_FACT, summary="repeat failure", source_family="repo"),
                EvidenceRef(ref="method", kind=EvidenceKind.EXTERNAL_METHOD, summary="root-cause method", source_family="engineering"),
            ],
            alternatives=[_alt("PATCH"), _alt("REDESIGN")],
            selected_candidate_id="PATCH",
            selection_rationale="candidate selection is not root-scope proof",
            assumptions_challenged=["first fix is root fix"],
            counterexamples=["prior patches did not prevent recurrence"],
            rejected_paths=["blind patching"],
            saturation=_saturation(),
            verification_plan=["replay"],
        )


def test_systemic_problem_requires_cross_layer_root_scope_and_rejected_upstream_alternative():
    with pytest.raises(ValidationError, match="at least two problem layers"):
        DecisionEnvelope(
            decision_id="ROOT-SAME-LAYER",
            operation="repair repeated failure",
            objective="select actual root scope",
            operation_class=OperationClass.MATERIAL_JUDGMENT,
            problem_triggered=True,
            systemic_problem_signal=True,
            evidence=[
                EvidenceRef(ref="current", kind=EvidenceKind.CURRENT_FACT, summary="repeat failure", source_family="repo"),
                EvidenceRef(ref="method", kind=EvidenceKind.EXTERNAL_METHOD, summary="root cause", source_family="engineering"),
            ],
            root_scope_hypotheses=[
                _root("h1", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.SELECTED),
                _root("h2", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.REJECTED),
            ],
            selected_root_hypothesis_id="h1",
            architecture_reassessment_refs=["audit:architecture"],
            alternatives=[_alt("PATCH"), _alt("REDESIGN")],
            selected_candidate_id="PATCH",
            selection_rationale="local workflow selected after evidence",
            assumptions_challenged=["repeat means architecture"],
            counterexamples=["architecture can be healthy while local cursor is wrong"],
            rejected_paths=["whole-system rebuild"],
            saturation=_saturation(),
            verification_plan=["replay"],
        )


def test_user_or_external_claim_cannot_be_promoted_directly_to_root_cause():
    with pytest.raises(ValidationError, match="cannot promote user/external framing"):
        DecisionEnvelope(
            decision_id="ROOT-ANCHOR",
            operation="accept user architecture theory",
            objective="avoid anchoring",
            operation_class=OperationClass.MATERIAL_JUDGMENT,
            problem_triggered=True,
            evidence=[
                EvidenceRef(ref="user", kind=EvidenceKind.USER_FEEDBACK, summary="maybe architecture", source_family="user"),
                EvidenceRef(ref="method", kind=EvidenceKind.EXTERNAL_METHOD, summary="architecture review", source_family="engineering"),
            ],
            root_scope_hypotheses=[_root("arch", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.SELECTED)],
            selected_root_hypothesis_id="arch",
            direct_user_or_external_claim_promoted_without_test=True,
            alternatives=[_alt("PATCH"), _alt("REDESIGN")],
            selected_candidate_id="REDESIGN",
            selection_rationale="invalid anchored selection",
            assumptions_challenged=["user framing is authority"],
            counterexamples=["same symptom can have workflow root"],
            rejected_paths=["local patch"],
            saturation=_saturation(),
            verification_plan=["architecture scenario"],
        )


def test_valid_material_architecture_decision_and_evolution_learning_are_admitted():
    record = KnowledgeRecord(
        knowledge_id="K1",
        kind=KnowledgeKind.METHOD,
        status=KnowledgeStatus.CANDIDATE,
        claim_or_method="fitness functions beat prose-only governance for enforceable invariants",
        scope="Financial writing architecture",
        evidence_refs=["thoughtworks-fitness-functions"],
        confidence="high",
        learned_at="2026-10-15",
        revalidation_trigger="architecture changes materially",
    )
    envelope = DecisionEnvelope(
        decision_id="D2",
        operation="select writing execution topology",
        objective="separate cognition, writing, and verification without controller sprawl",
        operation_class=OperationClass.MATERIAL_JUDGMENT,
        problem_triggered=True,
        architecture_or_governance_change=True,
        systemic_problem_signal=True,
        evidence=[
            EvidenceRef(
                ref="user-feedback",
                kind=EvidenceKind.USER_FEEDBACK,
                summary="soft audit missed visible defects",
                source_family="user",
            ),
            EvidenceRef(
                ref="openai-evals",
                kind=EvidenceKind.EXTERNAL_METHOD,
                summary="multi-agent complexity should be justified by evals",
                source_family="agent-engineering",
            ),
            EvidenceRef(
                ref="current-audit",
                kind=EvidenceKind.CURRENT_FACT,
                summary="all rubric fields passed despite rejected output",
                source_family="repository",
            ),
        ],
        root_scope_hypotheses=[
            _root("LOCAL_AUDIT", ProblemLayer.DOMAIN_WORKFLOW, HypothesisDisposition.REJECTED),
            _root("ARCH_TOPOLOGY", ProblemLayer.DOMAIN_ARCHITECTURE, HypothesisDisposition.SELECTED),
        ],
        selected_root_hypothesis_id="ARCH_TOPOLOGY",
        architecture_reassessment_refs=["audit:current-writing-topology", "scenario:rejection-replay"],
        problem_record_ref="references/maintenance.md#D2",
        learned_items=["pass labels are not evidence"],
        categories_or_models_used=["single-owner", "multi-pass", "multi-agent"],
        assumptions_challenged=["more rules improve prose", "same-session PASS is sufficient acceptance"],
        alternatives=[_alt("PATCH_RULES"), _alt("MULTI_AGENT"), _alt("SINGLE_OWNER_MULTI_PASS")],
        counterexamples=["current rule-rich system still produced rejected article"],
        rejected_paths=["PATCH_RULES because it increases prompt load", "MULTI_AGENT because responsibilities do not require separate owners"],
        selected_candidate_id="SINGLE_OWNER_MULTI_PASS",
        selection_rationale="keeps one business owner while separating cognition, drafting and evidence-backed fitness gates",
        saturation=_saturation(),
        verification_plan=["unit tests", "cross-border rejection replay", "held-out article eval"],
        knowledge_writeback_candidates=[record],
        evolution_disposition=EvolutionDisposition.DOMAIN_CANDIDATE,
    )
    assert admission_errors(envelope) == []
    root = envelope.root_scope_receipt()
    assert root is not None
    assert root.selected_layer == ProblemLayer.DOMAIN_ARCHITECTURE
    assert "LOCAL_AUDIT" in root.rejected_hypothesis_ids


def test_conflicted_knowledge_cannot_be_marked_validated():
    with pytest.raises(ValidationError):
        KnowledgeRecord(
            knowledge_id="K2",
            kind=KnowledgeKind.OPERATING,
            status=KnowledgeStatus.VALIDATED,
            claim_or_method="platform A is always best",
            scope="all topics",
            evidence_refs=["x"],
            confidence="high",
            learned_at="2026-10-15",
            revalidation_trigger="new evidence",
            conflicts=["counterexample"],
        )
