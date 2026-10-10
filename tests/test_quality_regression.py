import json
from pathlib import Path

from financial_writing_agent.quality_regression import (
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
                "evidence_status": "COMPLETE",
                "artifact_refs": ["artifact://rejected-1/baseline", "artifact://rejected-1/input"],
            },
            {
                "case_id": "accepted-1",
                "source_kind": "REAL_USER_ACCEPTANCE",
                "split": "REGRESSION",
                "topic_family": "company-deep-dive",
                "evidence_status": "COMPLETE",
                "artifact_refs": ["artifact://accepted-1/baseline", "artifact://accepted-1/input"],
            },
            {
                "case_id": "heldout-1",
                "source_kind": "EXTERNAL_BENCHMARK",
                "split": "HELD_OUT",
                "topic_family": "macro-policy",
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
                "evidence_status": "COMPLETE",
                "artifact_refs": ["artifact://rejected-1/baseline"],
            },
            {
                "case_id": "heldout-1",
                "source_kind": "EXTERNAL_BENCHMARK",
                "split": "HELD_OUT",
                "topic_family": "macro-policy",
                "evidence_status": "COMPLETE",
                "artifact_refs": ["artifact://heldout-1/input"],
            },
        ]
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
    return {"hard_invariant_regressions": [], "judge_runs": runs}


def general_passing_bundle():
    return {
        "hard_invariant_regressions": [],
        "judge_runs": [
            pairwise_run("rejected-1", "A", "A"),
            pairwise_run("rejected-1", "B", "B"),
            pairwise_run("heldout-1", "A", "A"),
            pairwise_run("heldout-1", "B", "B"),
        ],
    }


def test_real_offshore_wind_rejection_is_complete_but_general_corpus_still_needs_heldout_diversity():
    corpus = load_seed_corpus()
    result = evaluate_corpus_readiness(corpus)

    case_id = "offshore-wind-2026-10-10-real-user-rejection-01"
    assert result.status == "NOT_READY"
    assert result.promotion_scope == "GENERAL_EDITORIAL_QUALITY"
    assert result.complete_case_ids == (case_id,)
    assert "complete_real_user_rejection_case" not in result.missing_requirements
    assert "complete_positive_anchor_or_performance_case" not in result.missing_requirements
    assert "complete_held_out_case" in result.missing_requirements
    assert "at_least_two_complete_topic_families" in result.missing_requirements


def test_personalized_writing_dna_still_requires_real_positive_user_evidence():
    result = evaluate_corpus_readiness(
        general_ready_without_user_positive(),
        promotion_scope="PERSONALIZED_WRITING_DNA",
    )

    assert result.status == "NOT_READY"
    assert "complete_positive_anchor_or_performance_case" in result.missing_requirements


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


def test_quality_promotion_is_blocked_while_real_general_corpus_is_incomplete():
    result = evaluate_quality_promotion(
        load_seed_corpus(),
        {"hard_invariant_regressions": [], "judge_runs": []},
        evidence_verifier=lambda ref: True,
    )

    assert result.status == "BLOCKED_NOT_READY"
    assert any(error.startswith("missing_corpus_requirement:") for error in result.errors)


def test_general_quality_promotion_does_not_wait_for_user_positive_label():
    result = evaluate_quality_promotion(
        general_ready_without_user_positive(),
        general_passing_bundle(),
        evidence_verifier=lambda ref: ref.startswith("trace://"),
    )

    assert result.status == "PASS"
    assert result.promotion_scope == "GENERAL_EDITORIAL_QUALITY"


def test_self_reported_pairwise_receipt_without_verifier_cannot_promote():
    result = evaluate_quality_promotion(ready_corpus(), passing_bundle(), evidence_verifier=None)

    assert result.status == "FAIL"
    assert result.errors == ("independent_evidence_verifier_required",)


def test_position_swap_is_required_to_reduce_judge_position_bias():
    bundle = passing_bundle()
    bundle["judge_runs"] = [
        run
        for run in bundle["judge_runs"]
        if not (run["case_id"] == "heldout-1" and run["candidate_position"] == "B")
    ]

    result = evaluate_quality_promotion(ready_corpus(), bundle, evidence_verifier=lambda ref: ref.startswith("trace://"))

    assert result.status == "FAIL"
    assert "position_swap_required:heldout-1" in result.errors


def test_position_instability_fails_closed():
    bundle = passing_bundle()
    for run in bundle["judge_runs"]:
        if run["case_id"] == "rejected-1" and run["candidate_position"] == "B":
            run["preference"] = "A"

    result = evaluate_quality_promotion(ready_corpus(), bundle, evidence_verifier=lambda ref: ref.startswith("trace://"))

    assert result.status == "FAIL"
    assert any(error.startswith("position_swap_instability:rejected-1") for error in result.errors)


def test_hard_invariant_regression_blocks_quality_promotion_even_if_judges_prefer_candidate():
    bundle = passing_bundle()
    bundle["hard_invariant_regressions"] = ["unsupported factual claim"]

    result = evaluate_quality_promotion(ready_corpus(), bundle, evidence_verifier=lambda ref: ref.startswith("trace://"))

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
    )

    assert result.status == "FAIL"
    assert any(error.startswith("unverified_evidence_ref:") for error in result.errors)
