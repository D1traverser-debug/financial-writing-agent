import json
from pathlib import Path

from financial_writing_agent.quality_regression import evaluate_candidate_distillation, evaluate_corpus_readiness, evaluate_quality_promotion

ROOT = Path(__file__).resolve().parents[1]


def seed():
    return json.loads((ROOT / "evals/quality_regression.json").read_text(encoding="utf-8"))


def _case(case_id, source_kind, split, family):
    return {
        "case_id": case_id,
        "source_kind": source_kind,
        "split": split,
        "topic_family": family,
        "content_mode": "FINANCE_DEEP",
        "evidence_status": "COMPLETE",
        "artifact_refs": [f"artifact://{case_id}"],
        "artifact_bindings": [
            {
                "ref": f"artifact://{case_id}",
                "identity_type": "CONTENT_SHA256",
                "identity": f"sha-{case_id}",
            }
        ],
    }


def cases(include_positive=True, two_heldout=True):
    out = [
        _case("rejected-1", "REAL_USER_REJECTION", "REGRESSION", "sector-event"),
        _case("heldout-1", "EXTERNAL_BENCHMARK", "HELD_OUT", "macro-policy"),
    ]
    if two_heldout:
        out.append(_case("heldout-2", "EXTERNAL_BENCHMARK", "HELD_OUT", "supply-chain-cycle"))
    if include_positive:
        out.append(_case("accepted-1", "REAL_USER_ACCEPTANCE", "REGRESSION", "company-deep-dive"))
    return {"cases": out}


def distillation(scope="GENERAL_EDITORIAL_QUALITY", modes=None):
    return {
        "candidate_id":"quality-candidate-1","promotion_scope":scope,
        "problem_statement":"compliance can pass while editorial quality fails",
        "root_cause_hypothesis":"evaluation overweights checklist compliance",
        "source_case_ids":["rejected-1"],"target_content_modes":modes or ["FINANCE_DEEP"],
        "alternatives":[
            {"candidate_id":"quality-candidate-1","mechanism":"harden holistic quality evaluation","failure_modes":["overfit rejection"]},
            {"candidate_id":"quality-candidate-2","mechanism":"add prose rules","failure_modes":["Goodhart"]},
        ],
        "selected_candidate_id":"quality-candidate-1","selection_rationale":"smallest authority change",
        "authority_surfaces":["financial_writing_agent/quality_regression.py"],
        "superseded_mechanism_disposition":"do not add a prose-rule layer",
        "candidate_change_ref":"trace://candidate-change","counterexample_evidence_refs":["trace://counterexample"],
    }


def run(case_id, pos, preference):
    return {"case_id":case_id,"blind":True,"judge_identity":"quality-judge","execution_ref":f"judge://{case_id}/{pos}","evidence_refs":[f"trace://{case_id}/{pos}"],"candidate_id":"quality-candidate-1","candidate_change_ref":"trace://candidate-change","candidate_position":pos,"preference":preference}


def verify_ref(ref):
    return isinstance(ref, str) and ref.startswith(("trace://", "judge://"))


def verify_case_binding(case, binding):
    return binding.get("ref") in case.get("artifact_refs", []) and binding.get("identity") == f"sha-{case.get('case_id')}"


def verify_candidate(package, corpus):
    return package.get("candidate_change_ref") == "trace://candidate-change" and "trace://counterexample" in package.get("counterexample_evidence_refs", [])


def verify_semantics(run_obj, package, case):
    return run_obj.get("case_id") == case.get("case_id") and run_obj.get("candidate_id") == package.get("candidate_id") and run_obj.get("candidate_change_ref") == package.get("candidate_change_ref")


def verify_regression(regression, package):
    return regression.get("candidate_id") == package.get("candidate_id") and regression.get("candidate_change_ref") == package.get("candidate_change_ref") and regression.get("result") == "PASS"


def bundle(personal=False):
    rows = [run("rejected-1","A","A"),run("rejected-1","B","B"),run("heldout-1","A","A"),run("heldout-1","B","B"),run("heldout-2","A","TIE"),run("heldout-2","B","TIE")]
    if personal:
        rows += [run("accepted-1","A","TIE"),run("accepted-1","B","TIE")]
    return {
        "candidate_distillation":distillation("PERSONALIZED_WRITING_DNA" if personal else "GENERAL_EDITORIAL_QUALITY"),
        "hard_invariant_regressions":[],
        "hard_invariant_regression_run":{
            "candidate_id":"quality-candidate-1",
            "candidate_change_ref":"trace://candidate-change",
            "execution_ref":"trace://hard-regression-run",
            "suite_ref":"trace://hard-regression-suite",
            "result":"PASS",
            "evidence_refs":["trace://hard-regression-evidence"],
        },
        "judge_runs":rows,
    }


def promote(corpus, evidence, *, personal=False, ref=verify_ref, case_verifier=verify_case_binding, candidate_verifier=verify_candidate, semantic=verify_semantics, regression=verify_regression):
    return evaluate_quality_promotion(
        corpus,
        evidence,
        evidence_verifier=ref,
        case_binding_verifier=case_verifier,
        candidate_evidence_verifier=candidate_verifier,
        judge_run_verifier=semantic,
        regression_run_verifier=regression,
        promotion_scope="PERSONALIZED_WRITING_DNA" if personal else "GENERAL_EDITORIAL_QUALITY",
    )


def test_real_seed_is_diagnostic_only_until_second_heldout_family_exists():
    general = evaluate_corpus_readiness(seed())
    personal = evaluate_corpus_readiness(seed(), promotion_scope="PERSONALIZED_WRITING_DNA")
    assert general.status == "NOT_READY"
    assert "at_least_two_complete_heldout_topic_families" in general.missing_requirements
    assert personal.status == "NOT_READY"
    assert "complete_positive_anchor_or_performance_case" in personal.missing_requirements


def test_complete_case_requires_immutable_artifact_binding():
    corpus = cases()
    corpus["cases"][0].pop("artifact_bindings")
    result = evaluate_corpus_readiness(corpus)
    assert result.status == "FAIL"
    assert "complete_case_missing_artifact_bindings:rejected-1" in result.errors


def test_two_distinct_heldout_families_are_required():
    assert evaluate_corpus_readiness(cases(include_positive=False, two_heldout=False)).status == "NOT_READY"
    assert evaluate_corpus_readiness(cases(include_positive=False, two_heldout=True)).status == "PROMOTION_READY"


def test_snapshot_artifacts_remain_durable():
    offshore = (ROOT / "evals/artifacts/offshore-wind-2026-10-10-rejected-deep-v071.md").read_text(encoding="utf-8")
    rutile = (ROOT / "evals/artifacts/rutile-2026-10-06-heldout-baseline.md").read_text(encoding="utf-8")
    assert "海风订单开始密集落地" in offshore and "把 16 家公司都列出来只是完成了覆盖" in offshore
    assert "力量发展金红石项目" in rutile and "not a positive user-preference label" in rutile


def test_distillation_requires_alternative_and_mode_specific_heldout_diversity():
    pkg = distillation(); pkg["alternatives"] = pkg["alternatives"][:1]
    assert "at_least_two_candidate_mechanisms_required" in evaluate_candidate_distillation(cases(), pkg, evidence_verifier=verify_ref, candidate_evidence_verifier=verify_candidate).errors
    one = evaluate_candidate_distillation(cases(two_heldout=False), distillation(), evidence_verifier=verify_ref, candidate_evidence_verifier=verify_candidate)
    assert "target_mode_requires_two_heldout_topic_families:FINANCE_DEEP" in one.errors


def test_candidate_distillation_requires_semantic_evidence_verifier():
    result = evaluate_candidate_distillation(cases(), distillation(), evidence_verifier=verify_ref, candidate_evidence_verifier=lambda *_: False)
    assert "candidate_evidence_semantics_not_verified" in result.errors


def test_finance_deep_does_not_authorize_finance_broad():
    result = evaluate_candidate_distillation(cases(), distillation(modes=["FINANCE_DEEP","FINANCE_BROAD"]), evidence_verifier=verify_ref, candidate_evidence_verifier=verify_candidate)
    assert "target_mode_missing_real_rejection:FINANCE_BROAD" in result.errors
    assert "target_mode_requires_two_heldout_topic_families:FINANCE_BROAD" in result.errors


def test_general_promotion_can_pass_without_user_positive_after_all_other_evidence_passes():
    result = promote(cases(include_positive=False), bundle())
    assert result.status == "PASS"
    assert set(result.candidate_wins) == {"rejected-1","heldout-1"}
    assert result.baseline_wins == ()


def test_personalized_scope_requires_positive_anchor():
    not_ready = evaluate_corpus_readiness(cases(include_positive=False), promotion_scope="PERSONALIZED_WRITING_DNA")
    assert "complete_positive_anchor_or_performance_case" in not_ready.missing_requirements
    assert promote(cases(), bundle(personal=True), personal=True).status == "PASS"


def test_missing_verifier_contracts_fail_closed():
    result = evaluate_quality_promotion(cases(), bundle(personal=True), evidence_verifier=verify_ref, promotion_scope="PERSONALIZED_WRITING_DNA")
    assert result.status == "FAIL"
    assert set(result.errors) == {
        "case_binding_verifier_required",
        "candidate_evidence_semantic_verifier_required",
        "judge_run_semantic_verifier_required",
        "hard_regression_run_verifier_required",
    }


def test_stale_candidate_binding_cannot_replay_valid_refs():
    b = bundle(personal=True); b["judge_runs"][0]["candidate_id"] = "stale"
    result = promote(cases(), b, personal=True)
    assert result.status == "FAIL"
    assert any(x.startswith("judge_run_candidate_mismatch:") for x in result.errors)


def test_case_binding_verifier_can_reject_replaced_baseline():
    result = promote(cases(), bundle(), case_verifier=lambda *_: False)
    assert any(x.startswith("unverified_case_artifact_binding:") for x in result.errors)


def test_hard_regression_requires_verified_execution_bound_to_candidate():
    b = bundle(); b.pop("hard_invariant_regression_run")
    assert "missing_hard_invariant_regression_run" in promote(cases(), b).errors
    b = bundle(); b["hard_invariant_regression_run"]["candidate_id"] = "stale"
    assert "hard_regression_candidate_mismatch" in promote(cases(), b).errors
    b = bundle()
    assert "hard_regression_run_semantics_not_verified" in promote(cases(), b, regression=lambda *_: False).errors


def test_execution_ref_must_verify_and_be_unique():
    b = bundle(personal=True); b["judge_runs"][0]["execution_ref"] = "untrusted://run"
    assert any(x.startswith("unverified_execution_ref:") for x in promote(cases(), b, personal=True).errors)
    b = bundle(personal=True); b["judge_runs"][1]["execution_ref"] = b["judge_runs"][0]["execution_ref"]
    assert any(x.startswith("duplicate_execution_ref:") for x in promote(cases(), b, personal=True).errors)


def test_semantic_verifier_can_reject_real_but_irrelevant_refs():
    result = promote(cases(), bundle(personal=True), personal=True, semantic=lambda *_: False)
    assert any(x.startswith("unverified_judge_run_semantics:") for x in result.errors)


def test_position_swap_and_instability_fail_closed():
    b = bundle(personal=True); b["judge_runs"] = [r for r in b["judge_runs"] if not (r["case_id"] == "heldout-1" and r["candidate_position"] == "B")]
    assert "position_swap_required:heldout-1" in promote(cases(), b, personal=True).errors
    b = bundle(personal=True)
    for r in b["judge_runs"]:
        if r["case_id"] == "rejected-1" and r["candidate_position"] == "B": r["preference"] = "A"
    assert any(x.startswith("position_swap_instability:rejected-1") for x in promote(cases(), b, personal=True).errors)


def test_hard_invariant_regression_blocks_promotion():
    b = bundle(personal=True); b["hard_invariant_regressions"] = ["unsupported factual claim"]
    result = promote(cases(), b, personal=True)
    assert result.status == "FAIL"
    assert "hard_invariant_regression:unsupported factual claim" in result.errors


def test_unverified_trace_blocks_promotion():
    result = promote(cases(), bundle(personal=True), personal=True, ref=lambda ref: verify_ref(ref) and ref != "trace://heldout-1/B")
    assert any(x.startswith("unverified_evidence_ref:") for x in result.errors)
