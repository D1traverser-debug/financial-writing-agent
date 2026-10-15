import pytest
from pydantic import ValidationError

from financial_writing_agent.cognition_governance import (
    CandidateOption,
    DecisionEnvelope,
    EvidenceKind,
    EvidenceRef,
    EvolutionDisposition,
    KnowledgeKind,
    KnowledgeRecord,
    KnowledgeStatus,
    OperationClass,
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


def test_search_saturation_needs_two_consecutive_no_delta_sweeps():
    with pytest.raises(ValidationError):
        SearchSaturation(
            sweeps=[
                SearchSweep(sweep_no=1, query_or_scope="one", source_families=["a", "b"]),
                SearchSweep(
                    sweep_no=2,
                    query_or_scope="two",
                    source_families=["a", "b"],
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
