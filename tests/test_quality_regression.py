import json
from pathlib import Path

from financial_writing_agent.quality_regression import evaluate_candidate_distillation, evaluate_corpus_readiness, evaluate_quality_promotion

ROOT = Path(__file__).resolve().parents[1]


def seed():
    return json.loads((ROOT / "evals/quality_regression.json").read_text(encoding="utf-8"))


def cases(include_positive=True, two_heldout=True):
    out = [
        {"case_id":"rejected-1","source_kind":"REAL_USER_REJECTION","split":"REGRESSION","topic_family":"sector-event","content_mode":"FINANCE_DEEP","evidence_status":"COMPLETE","artifact_refs":["artifact://rejected"]},
        {"case_id":"heldout-1","source_kind":"EXTERNAL_BENCHMARK","split":"HELD_OUT","topic_family":"macro-policy","content_mode":"FINANCE_DEEP","evidence_status":"COMPLETE","artifact_refs":["artifact://heldout-1"]},
    ]
    if two_heldout:
        out.append({"case_id":"heldout-2","source_kind":"EXTERNAL_BENCHMARK","split":"HELD_OUT","topic_family":"supply-chain-cycle","content_mode":"FINANCE_DEEP","evidence_status":"COMPLETE","artifact_refs":["artifact://heldout-2"]})
    if include_positive:
        out.append({"case_id":"accepted-1","source_kind":"REAL_USER_ACCEPTANCE","split":"REGRESSION","topic_family":"company-deep-dive","content_mode":"FINANCE_DEEP","evidence_status":"COMPLETE","artifact_refs":["artifact://accepted"]})
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
    return {"case_id":case_id,"blind":True,"judge_identity":"independent-quality-judge","execution_ref":f"judge://{case_id}/{pos}","evidence_refs":[f"trace://{case_id}/{pos}"],"candidate_id":"quality-candidate-1","candidate_change_ref":"trace://candidate-change","candidate_position":pos,"preference":preference}


def verify_ref(ref):
    return isinstance(ref, str) and ref.startswith(("trace://", "judge://"))


def verify_semantics(run_obj, package, case):
    return run_obj.get("case_id") == case.get("case_id") and run_obj.get("candidate_id") == package.get("candidate_id") and run_obj.get("candidate_change_ref") == package.get("candidate_change_ref")


def bundle(personal=False):
    rows = [run("rejected-1","A","A"),run("rejected-1","B","B"),run("heldout-1","A","A"),run("heldout-1","B","B"),run("heldout-2","A","TIE"),run("heldout-2","B","TIE")]
    if personal: rows += [run("accepted-1","A","TIE"),run("accepted-1","B","TIE")]
    return {"candidate_distillation":distillation("PERSONALIZED_WRITING_DNA" if personal else "GENERAL_EDITORIAL_QUALITY"),"hard_invariant_regressions":[],"judge_runs":rows}


def promote(corpus, evidence, *, personal=False, ref=verify_ref, semantic=verify_semantics):
    return evaluate_quality_promotion(corpus, evidence, evidence_verifier=ref, judge_run_verifier=semantic, promotion_scope="PERSONALIZED_WRITING_DNA" if personal else "GENERAL_EDITORIAL_QUALITY")


def test_real_seed_is_diagnostic_only_until_second_heldout_family_exists():
    general = evaluate_corpus_readiness(seed())
    personal = evaluate_corpus_readiness(seed(), promotion_scope="PERSONALIZED_WRITING_DNA")
    assert general.status == "NOT_READY"
    assert "at_least_two_complete_heldout_topic_families" in general.missing_requirements
    assert personal.status == "NOT_READY"
    assert "complete_positive_anchor_or_performance_case" in personal.missing_requirements


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
    assert "at_least_two_candidate_mechanisms_required" in evaluate_candidate_distillation(cases(), pkg, evidence_verifier=verify_ref).errors
    one = evaluate_candidate_distillation(cases(two_heldout=False), distillation(), evidence_verifier=verify_ref)
    assert "target_mode_requires_two_heldout_topic_families:FINANCE_DEEP" in one.errors


def test_finance_deep_does_not_authorize_finance_broad():
    result = evaluate_candidate_distillation(cases(), distillation(modes=["FINANCE_DEEP","FINANCE_BROAD"]), evidence_verifier=verify_ref)
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


def test_missing_ref_or_semantic_verifier_fails_closed():
    assert evaluate_quality_promotion(cases(), bundle(personal=True), evidence_verifier=None, judge_run_verifier=verify_semantics, promotion_scope="PERSONALIZED_WRITING_DNA").errors == ("independent_evidence_verifier_required",)
    assert evaluate_quality_promotion(cases(), bundle(personal=True), evidence_verifier=verify_ref, judge_run_verifier=None, promotion_scope="PERSONALIZED_WRITING_DNA").errors == ("independent_judge_run_verifier_required",)


def test_stale_candidate_binding_cannot_replay_valid_refs():
    b = bundle(personal=True); b["judge_runs"][0]["candidate_id"] = "stale"
    result = promote(cases(), b, personal=True)
    assert result.status == "FAIL"
    assert any(x.startswith("judge_run_candidate_mismatch:") for x in result.errors)


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
