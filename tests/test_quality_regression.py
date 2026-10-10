import json
from pathlib import Path

from financial_writing_agent.quality_regression import (
    evaluate_candidate_distillation,
    evaluate_corpus_readiness,
    evaluate_quality_promotion,
)


ROOT = Path(__file__).resolve().parents[1]


def load_seed_corpus():
    return json.loads((ROOT / "evals/quality_regression.json").read_text(encoding="utf-8"))


def ready_corpus():
    return {
        "cases": [
            {
                "case_id": "rejected-1",
                "source_kind": "REAL_USER_REJECTION",
                "split": "REGRESSION",
                "topic_family": "sector-event",
                "content_mode": "FINANCE_DEEP",
                "evidence_status": "COMPLETE",
                "artifact_refs": ["artifact://rejected-1/baseline", "artifact://rejected-1/input"],
            },
            {
                "case_id": "accepted-1",
                "source_kind": "REAL_USER_ACCEPTANCE",
                "split": "REGRESSION",
                "topic_family": "company-deep-dive",
                "content_mode": "FINANCE_DEEP",
                "evidence_status": "COMPLETE",
                "artifact_refs": ["artifact://accepted-1/baseline", "artifact://accepted-1/input"],
            },
            {
                "case_id": "heldout-1",
                "source_kind": "EXTERNAL_BENCHMARK",
                "split": "HELD_OUT",
                "topic_family": "macro-policy",
                "content_mode": "FINANCE_DEEP",
                "evidence_status": "COMPLETE",
                "artifact_refs": ["artifact://heldout-1/input"],
            },
        ]
    }


def general_ready_without_user_positive():
    return {
        "cases": [
            {
                "case_id": "rejected-1",
                "source_kind": "REAL_USER_REJECTION",
                "split": "REGRESSION",
                "topic_family": "sector-event",
                "content_mode": "FINANCE_DEEP",
                "evidence_status": "COMPLETE",
                "artifact_refs": ["artifact://rejected-1/baseline"],
            },
            {
                "case_id": "heldout-1",
                "source_kind": "EXTERNAL_BENCHMARK",
                "split": "HELD_OUT",
                "topic_family": "macro-policy",
                "content_mode": "FINANCE_DEEP",
                "evidence_status": "COMPLETE",
                "artifact_refs": ["artifact://heldout-1/input"],
            },
        ]
    }


def candidate_distillation(*, promotion_scope="GENERAL_EDITORIAL_QUALITY", target_modes=None):
    return {
        "candidate_id": "quality-candidate-1",
        "promotion_scope": promotion_scope,
        "problem_statement": "rule compliance can pass while actual editorial quality remains poor",
        "root_cause_hypothesis": "the system over-optimizes checklist compliance and under-tests holistic reading quality",
        "source_case_ids": ["rejected-1"],
        "target_content_modes": target_modes or ["FINANCE_DEEP"],
        "alternatives": [
            {
                "candidate_id": "quality-candidate-1",
                "mechanism": "change the smallest owner evaluation/generation mechanism and verify it by blind replay",
                "failure_modes": ["candidate overfits the known rejection"],
            },
            {
                "candidate_id": "quality-candidate-2",
                "mechanism": "add more deterministic prose rules and phrase checks",
                "failure_modes": ["Goodhart pressure increases mechanical writing"],
            },
        ],
        "selected_candidate_id": "quality-candidate-1",
        "selection_rationale": "it addresses the evaluation/generation loop without adding another article-rule checklist",
        "authority_surfaces": ["financial_writing_agent/quality_regression.py"],
        "superseded_mechanism_disposition": "do not add a new prose-rule layer; keep existing factual/compliance hard floors",
        "candidate_change_ref": "trace://distillation/candidate-change",
        "counterexample_evidence_refs": ["trace://distillation/counterexample"],
    }


def pairwise_run(case_id, candidate_position, preference):
    return {
        "case_id": case_id,
        "blind": True,
        "judge_identity": "independent-quality-judge",
        "execution_ref": f"judge://{case_id}/{candidate_position}",
        "evidence_refs": [f"trace://{case_id}/{candidate_position}"],
        "candidate_position": candidate_position,
        "preference": preference,
    }


def passing_bundle():
    runs = []
    runs += [pairwise_run("rejected-1", "A", "A"), pairwise_run("rejected-1", "B", "B")]
    runs += [pairwise_run("accepted-1", "A", "TIE"), pairwise_run("accepted-1", "B", "TIE")]
    runs += [pairwise_run("heldout-1", "A", "A"), pairwise_run("heldout-1", "B", "B")]
    return {
        "candidate_distillation": candidate_distillation(promotion_scope="PERSONALIZED_WRITING_DNA"),
        "hard_invariant_regressions": [],
        "judge_runs": runs,
    }


def general_passing_bundle():
    return {
        "candidate_distillation": candidate_distillation(),
        "hard_invariant_regressions": [],
        "judge_runs": [
            pairwise_run("rejected-1", "A", "A"),
            pairwise_run("rejected-1", "B", "B"),
            pairwise_run("heldout-1", "A", "A"),
            pairwise_run("heldout-1", "B", "B"),
        ],
    }


def test_real_seed_corpus_is_ready_for_general_quality_but_not_personalized_dna():
    corpus = load_seed_corpus()
    general = evaluate_corpus_readiness(corpus)
    personalized = evaluate_corpus_readiness(corpus, promotion_scope="PERSONALIZED_WRITING_DNA")

    assert general.status == "PROMOTION_READY"
    assert general.promotion_scope == "GENERAL_EDITORIAL_QUALITY"
    assert set(general.complete_case_ids) == {
        "offshore-wind-2026-10-10-real-user-rejection-01",
        "rutile-2026-10-06-cross-topic-heldout-01",
    }
    assert general.missing_requirements == ()

    assert personalized.status == "NOT_READY"
    assert "complete_positive_anchor_or_performance_case" in personalized.missing_requirements


def test_general_quality_can_be_promotion_ready_without_user_positive_anchor():
    result = evaluate_corpus_readiness(general_ready_without_user_positive())

    assert result.status == "PROMOTION_READY"
    assert "complete_positive_anchor_or_performance_case" not in result.missing_requirements


def test_offshore_wind_snapshot_is_durable_and_contains_rejected_text():
    artifact = ROOT / "evals" / "artifacts" / "offshore-wind-2026-10-10-rejected-deep-v071.md"
    text = artifact.read_text(encoding="utf-8")

    assert "海风订单开始密集落地" in text
    assert "16 家公司放在一起看，研究顺序应该怎么排" in text
    assert "把 16 家公司都列出来只是完成了覆盖" in text
    assert "（2）轴承：新强联" in text


def test_cross_topic_heldout_snapshot_is_durable_and_not_labeled_user_acceptance():
    artifact = ROOT / "evals" / "artifacts" / "rutile-2026-10-06-heldout-baseline.md"
    text = artifact.read_text(encoding="utf-8")

    assert "力量发展金红石项目" in text
    assert "not a positive user-preference label" in text
    assert "33—36 万吨" in text


def test_distillation_requires_real_failure_alternative_failure_mode_and_bounded_surface():
    result = evaluate_candidate_distillation(
        ready_corpus(),
        candidate_distillation(),
        evidence_verifier=lambda ref: ref.startswith("trace://"),
    )

    assert result.status == "PASS"
    assert result.candidate_id == "quality-candidate-1"
    assert result.target_content_modes == ("FINANCE_DEEP",)


def test_candidate_cannot_jump_directly_from_failure_to_promotion_without_distillation():
    bundle = general_passing_bundle()
    bundle.pop("candidate_distillation")

    result = evaluate_quality_promotion(
        general_ready_without_user_positive(),
        bundle,
        evidence_verifier=lambda ref: ref.startswith("trace://"),
    )

    assert result.status == "FAIL"
    assert result.errors == ("candidate_distillation:missing_candidate_distillation",)


def test_distillation_rejects_single_mechanism_without_credible_alternative():
    package = candidate_distillation()
    package["alternatives"] = package["alternatives"][:1]

    result = evaluate_candidate_distillation(
        ready_corpus(),
        package,
        evidence_verifier=lambda ref: ref.startswith("trace://"),
    )

    assert result.status == "FAIL"
    assert "at_least_two_candidate_mechanisms_required" in result.errors


def test_distillation_rejects_unverified_counterexample_evidence():
    package = candidate_distillation()

    result = evaluate_candidate_distillation(
        ready_corpus(),
        package,
        evidence_verifier=lambda ref: not ref.endswith("counterexample"),
    )

    assert result.status == "FAIL"
    assert any(error.startswith("unverified_counterexample_ref:") for error in result.errors)


def test_finance_deep_evidence_cannot_silently_authorize_finance_broad_quality_claim():
    package = candidate_distillation(target_modes=["FINANCE_DEEP", "FINANCE_BROAD"])

    result = evaluate_candidate_distillation(
        ready_corpus(),
        package,
        evidence_verifier=lambda ref: ref.startswith("trace://"),
    )

    assert result.status == "FAIL"
    assert "target_mode_missing_real_rejection:FINANCE_BROAD" in result.errors
    assert "target_mode_missing_heldout:FINANCE_BROAD" in result.errors


def test_ready_corpus_still_cannot_promote_without_concrete_judge_evidence():
    result = evaluate_quality_promotion(
        load_seed_corpus(),
        None,
        evidence_verifier=lambda ref: True,
    )

    assert result.status == "FAIL"
    assert result.errors == ("missing_quality_evidence_bundle",)


def test_general_quality_promotion_does_not_wait_for_user_positive_label():
    result = evaluate_quality_promotion(
        general_ready_without_user_positive(),
        general_passing_bundle(),
        evidence_verifier=lambda ref: ref.startswith("trace://"),
    )

    assert result.status == "PASS"
    assert result.promotion_scope == "GENERAL_EDITORIAL_QUALITY"


def test_self_reported_pairwise_receipt_without_verifier_cannot_promote():
    result = evaluate_quality_promotion(ready_corpus(), passing_bundle(), evidence_verifier=None, promotion_scope="PERSONALIZED_WRITING_DNA")

    assert result.status == "FAIL"
    assert result.errors == ("independent_evidence_verifier_required",)


def test_position_swap_is_required_to_reduce_judge_position_bias():
    bundle = passing_bundle()
    bundle["judge_runs"] = [
        run
        for run in bundle["judge_runs"]
        if not (run["case_id"] == "heldout-1" and run["candidate_position"] == "B")
    ]

    result = evaluate_quality_promotion(
        ready_corpus(),
        bundle,
        evidence_verifier=lambda ref: ref.startswith("trace://"),
        promotion_scope="PERSONALIZED_WRITING_DNA",
    )

    assert result.status == "FAIL"
    assert "position_swap_required:heldout-1" in result.errors


def test_position_instability_fails_closed():
    bundle = passing_bundle()
    for run in bundle["judge_runs"]:
        if run["case_id"] == "rejected-1" and run["candidate_position"] == "B":
            run["preference"] = "A"

    result = evaluate_quality_promotion(
        ready_corpus(),
        bundle,
        evidence_verifier=lambda ref: ref.startswith("trace://"),
        promotion_scope="PERSONALIZED_WRITING_DNA",
    )

    assert result.status == "FAIL"
    assert any(error.startswith("position_swap_instability:rejected-1") for error in result.errors)


def test_hard_invariant_regression_blocks_quality_promotion_even_if_judges_prefer_candidate():
    bundle = passing_bundle()
    bundle["hard_invariant_regressions"] = ["unsupported factual claim"]

    result = evaluate_quality_promotion(
        ready_corpus(),
        bundle,
        evidence_verifier=lambda ref: ref.startswith("trace://"),
        promotion_scope="PERSONALIZED_WRITING_DNA",
    )

    assert result.status == "FAIL"
    assert "hard_invariant_regression:unsupported factual claim" in result.errors


def test_candidate_must_improve_known_rejection_preserve_positive_anchor_and_win_heldout():
    result = evaluate_quality_promotion(
        ready_corpus(),
        passing_bundle(),
        evidence_verifier=lambda ref: ref.startswith("trace://"),
        promotion_scope="PERSONALIZED_WRITING_DNA",
    )

    assert result.status == "PASS"
    assert set(result.candidate_wins) == {"rejected-1", "heldout-1"}
    assert result.ties == ("accepted-1",)
    assert result.baseline_wins == ()


def test_unverified_judge_trace_cannot_promote():
    result = evaluate_quality_promotion(
        ready_corpus(),
        passing_bundle(),
        evidence_verifier=lambda ref: not ref.endswith("/B"),
        promotion_scope="PERSONALIZED_WRITING_DNA",
    )

    assert result.status == "FAIL"
    assert any(error.startswith("unverified_evidence_ref:") for error in result.errors)
