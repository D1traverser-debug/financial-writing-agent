from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping

EvidenceVerifier = Callable[[str], bool]
CaseBindingVerifier = Callable[[Mapping[str, Any], Mapping[str, Any]], bool]
CandidateEvidenceVerifier = Callable[[Mapping[str, Any], Mapping[str, Any]], bool]
JudgeRunVerifier = Callable[[Mapping[str, Any], Mapping[str, Any], Mapping[str, Any]], bool]
RegressionRunVerifier = Callable[[Mapping[str, Any], Mapping[str, Any]], bool]


@dataclass(frozen=True)
class CorpusReadinessResult:
    status: str
    promotion_scope: str
    case_ids: tuple[str, ...]
    complete_case_ids: tuple[str, ...]
    missing_requirements: tuple[str, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class CandidateDistillationResult:
    status: str
    candidate_id: str | None
    target_content_modes: tuple[str, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class QualityPromotionResult:
    status: str
    promotion_scope: str
    evaluated_case_ids: tuple[str, ...]
    candidate_wins: tuple[str, ...]
    ties: tuple[str, ...]
    baseline_wins: tuple[str, ...]
    errors: tuple[str, ...]


_SOURCE = {"REAL_USER_REJECTION", "REAL_USER_ACCEPTANCE", "POST_PUBLICATION_PERFORMANCE", "EXTERNAL_BENCHMARK"}
_SPLITS = {"CALIBRATION", "REGRESSION", "HELD_OUT"}
_STATUS = {"PARTIAL", "COMPLETE"}
_SCOPES = {"GENERAL_EDITORIAL_QUALITY", "PERSONALIZED_WRITING_DNA"}
_MODES = {"FINANCE_DEEP", "FINANCE_BROAD"}
_BINDING_TYPES = {"GIT_BLOB_SHA", "PROVIDER_IMMUTABLE_VERSION", "CONTENT_SHA256"}
_MIN_HELDOUT_FAMILIES = 2


def _verified(ref: str, verifier: EvidenceVerifier) -> bool:
    try:
        return bool(verifier(ref))
    except Exception:
        return False


def _semantic_verified(verifier, *args) -> bool:
    try:
        return bool(verifier(*args))
    except Exception:
        return False


def _complete_cases(corpus: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    cases = corpus.get("cases")
    if not isinstance(cases, list):
        return []
    return [c for c in cases if isinstance(c, Mapping) and c.get("evidence_status") == "COMPLETE"]


def _binding_shape_errors(case: Mapping[str, Any], case_id: str) -> list[str]:
    bindings = case.get("artifact_bindings")
    if not isinstance(bindings, list) or not bindings:
        return [f"complete_case_missing_artifact_bindings:{case_id}"]
    errors: list[str] = []
    seen: set[tuple[str, str, str]] = set()
    for i, binding in enumerate(bindings):
        if not isinstance(binding, Mapping):
            errors.append(f"artifact_binding_not_object:{case_id}:{i}")
            continue
        ref = str(binding.get("ref", "")).strip()
        identity_type = str(binding.get("identity_type", "")).strip()
        identity = str(binding.get("identity", "")).strip()
        if not ref:
            errors.append(f"artifact_binding_missing_ref:{case_id}:{i}")
        if identity_type not in _BINDING_TYPES:
            errors.append(f"artifact_binding_invalid_identity_type:{case_id}:{i}:{identity_type or 'MISSING'}")
        if not identity:
            errors.append(f"artifact_binding_missing_identity:{case_id}:{i}")
        key = (ref, identity_type, identity)
        if all(key) and key in seen:
            errors.append(f"duplicate_artifact_binding:{case_id}:{i}")
        seen.add(key)
    return errors


def evaluate_corpus_readiness(corpus: Mapping[str, Any], *, promotion_scope: str = "GENERAL_EDITORIAL_QUALITY") -> CorpusReadinessResult:
    if promotion_scope not in _SCOPES:
        return CorpusReadinessResult("FAIL", promotion_scope, (), (), (), (f"invalid_promotion_scope:{promotion_scope}",))
    raw = corpus.get("cases")
    if not isinstance(raw, list):
        return CorpusReadinessResult("FAIL", promotion_scope, (), (), (), ("missing_or_invalid_cases",))

    errors: list[str] = []
    ids: list[str] = []
    complete_ids: list[str] = []
    complete: list[Mapping[str, Any]] = []
    seen: set[str] = set()
    for i, case in enumerate(raw):
        if not isinstance(case, Mapping):
            errors.append(f"case_not_object:{i}")
            continue
        cid = str(case.get("case_id", "")).strip()
        if not cid:
            errors.append(f"missing_case_id:{i}")
            continue
        if cid in seen:
            errors.append(f"duplicate_case_id:{cid}")
            continue
        seen.add(cid)
        ids.append(cid)
        source = str(case.get("source_kind", "")).strip()
        split = str(case.get("split", "")).strip()
        status = str(case.get("evidence_status", "")).strip()
        family = str(case.get("topic_family", "")).strip()
        mode = str(case.get("content_mode", "")).strip()
        refs = case.get("artifact_refs")
        if source not in _SOURCE:
            errors.append(f"invalid_source_kind:{cid}:{source}")
        if split not in _SPLITS:
            errors.append(f"invalid_split:{cid}:{split}")
        if status not in _STATUS:
            errors.append(f"invalid_evidence_status:{cid}:{status}")
        if not family:
            errors.append(f"missing_topic_family:{cid}")
        if mode not in _MODES:
            errors.append(f"invalid_content_mode:{cid}:{mode or 'MISSING'}")
        if not isinstance(refs, list):
            errors.append(f"invalid_artifact_refs:{cid}")
            refs = []
        if status == "COMPLETE":
            if not refs or not all(isinstance(x, str) and x.strip() for x in refs):
                errors.append(f"complete_case_missing_artifact_refs:{cid}")
            errors.extend(_binding_shape_errors(case, cid))
            if not any(error.endswith(f":{cid}") or f":{cid}:" in error for error in errors):
                complete_ids.append(cid)
                complete.append(case)
    if errors:
        return CorpusReadinessResult("FAIL", promotion_scope, tuple(ids), tuple(complete_ids), (), tuple(errors))

    missing: list[str] = []
    if not any(c.get("source_kind") == "REAL_USER_REJECTION" for c in complete):
        missing.append("complete_real_user_rejection_case")
    heldout = [c for c in complete if c.get("split") == "HELD_OUT"]
    if not heldout:
        missing.append("complete_held_out_case")
    heldout_families = {str(c.get("topic_family", "")).strip() for c in heldout if str(c.get("topic_family", "")).strip()}
    if len(heldout_families) < _MIN_HELDOUT_FAMILIES:
        missing.append("at_least_two_complete_heldout_topic_families")
    if promotion_scope == "PERSONALIZED_WRITING_DNA" and not any(
        c.get("source_kind") in {"REAL_USER_ACCEPTANCE", "POST_PUBLICATION_PERFORMANCE"} for c in complete
    ):
        missing.append("complete_positive_anchor_or_performance_case")
    return CorpusReadinessResult("PROMOTION_READY" if not missing else "NOT_READY", promotion_scope, tuple(ids), tuple(complete_ids), tuple(missing), ())


def evaluate_candidate_distillation(
    corpus: Mapping[str, Any],
    package: Mapping[str, Any] | None,
    *,
    evidence_verifier: EvidenceVerifier | None,
    candidate_evidence_verifier: CandidateEvidenceVerifier | None,
    promotion_scope: str = "GENERAL_EDITORIAL_QUALITY",
) -> CandidateDistillationResult:
    if package is None:
        return CandidateDistillationResult("FAIL", None, (), ("missing_candidate_distillation",))
    if not isinstance(package, Mapping):
        return CandidateDistillationResult("FAIL", None, (), ("invalid_candidate_distillation",))
    if evidence_verifier is None:
        return CandidateDistillationResult("FAIL", None, (), ("evidence_verifier_required",))
    if candidate_evidence_verifier is None:
        return CandidateDistillationResult("FAIL", None, (), ("candidate_evidence_semantic_verifier_required",))

    errors: list[str] = []
    cid = str(package.get("candidate_id", "")).strip()
    if not cid:
        errors.append("missing_candidate_id")
    observed_scope = str(package.get("promotion_scope", "")).strip()
    if observed_scope != promotion_scope:
        errors.append(f"candidate_promotion_scope_mismatch:observed={observed_scope or 'MISSING'}:expected={promotion_scope}")
    for field in ("problem_statement", "root_cause_hypothesis", "selection_rationale", "superseded_mechanism_disposition"):
        if not str(package.get(field, "")).strip():
            errors.append(f"missing_{field}")

    raw_modes = package.get("target_content_modes")
    modes = tuple(dict.fromkeys(str(x).strip() for x in raw_modes if isinstance(x, str) and x.strip())) if isinstance(raw_modes, list) else ()
    if not modes:
        errors.append("missing_target_content_modes")
    for mode in modes:
        if mode not in _MODES:
            errors.append(f"invalid_target_content_mode:{mode}")

    raw_sources = package.get("source_case_ids")
    source_ids = tuple(dict.fromkeys(str(x).strip() for x in raw_sources if isinstance(x, str) and x.strip())) if isinstance(raw_sources, list) else ()
    if not source_ids:
        errors.append("missing_source_case_ids")
    complete = {str(c.get("case_id", "")).strip(): c for c in _complete_cases(corpus) if str(c.get("case_id", "")).strip()}
    for source_id in source_ids:
        if source_id not in complete:
            errors.append(f"source_case_not_complete_or_unknown:{source_id}")
    if source_ids and not any(complete.get(x, {}).get("source_kind") == "REAL_USER_REJECTION" for x in source_ids):
        errors.append("source_cases_require_real_user_rejection")

    alts = package.get("alternatives") if isinstance(package.get("alternatives"), list) else []
    if len(alts) < 2:
        errors.append("at_least_two_candidate_mechanisms_required")
    alt_ids: list[str] = []
    for i, alt in enumerate(alts):
        if not isinstance(alt, Mapping):
            errors.append(f"candidate_mechanism_not_object:{i}")
            continue
        aid = str(alt.get("candidate_id", "")).strip()
        if not aid:
            errors.append(f"candidate_mechanism_missing_id:{i}")
        elif aid in alt_ids:
            errors.append(f"duplicate_candidate_mechanism_id:{aid}")
        else:
            alt_ids.append(aid)
        if not str(alt.get("mechanism", "")).strip():
            errors.append(f"candidate_mechanism_missing_description:{aid or i}")
        fm = alt.get("failure_modes")
        if not isinstance(fm, list) or not any(isinstance(x, str) and x.strip() for x in fm):
            errors.append(f"candidate_mechanism_missing_failure_mode:{aid or i}")
    selected = str(package.get("selected_candidate_id", "")).strip()
    if not selected:
        errors.append("missing_selected_candidate_id")
    elif selected not in alt_ids:
        errors.append(f"selected_candidate_not_in_alternatives:{selected}")
    if cid and selected and cid != selected:
        errors.append(f"candidate_id_selected_candidate_mismatch:{cid}:{selected}")

    surfaces = package.get("authority_surfaces")
    if not isinstance(surfaces, list) or not any(isinstance(x, str) and x.strip() for x in surfaces):
        errors.append("missing_authority_surfaces")
    change_ref = str(package.get("candidate_change_ref", "")).strip()
    if not change_ref:
        errors.append("missing_candidate_change_ref")
    elif not _verified(change_ref, evidence_verifier):
        errors.append(f"unverified_candidate_change_ref:{change_ref}")
    counter = package.get("counterexample_evidence_refs")
    if not isinstance(counter, list) or not any(isinstance(x, str) and x.strip() for x in counter):
        errors.append("missing_counterexample_evidence_refs")
    else:
        for ref in counter:
            if isinstance(ref, str) and ref.strip() and not _verified(ref.strip(), evidence_verifier):
                errors.append(f"unverified_counterexample_ref:{ref.strip()}")

    for mode in modes:
        mode_cases = [c for c in complete.values() if str(c.get("content_mode", "")).strip() == mode]
        if not any(c.get("source_kind") == "REAL_USER_REJECTION" for c in mode_cases):
            errors.append(f"target_mode_missing_real_rejection:{mode}")
        heldout = [c for c in mode_cases if c.get("split") == "HELD_OUT"]
        if not heldout:
            errors.append(f"target_mode_missing_heldout:{mode}")
        families = {str(c.get("topic_family", "")).strip() for c in heldout if str(c.get("topic_family", "")).strip()}
        if len(families) < _MIN_HELDOUT_FAMILIES:
            errors.append(f"target_mode_requires_two_heldout_topic_families:{mode}")

    if not errors and not _semantic_verified(candidate_evidence_verifier, package, corpus):
        errors.append("candidate_evidence_semantics_not_verified")
    return CandidateDistillationResult("PASS" if not errors else "FAIL", cid or None, modes, tuple(errors))


def _normalized(position: str, preference: str) -> str:
    p, pref = position.upper(), preference.upper()
    if p not in {"A", "B"}:
        return "INVALID"
    if pref == "TIE":
        return "TIE"
    if pref not in {"A", "B"}:
        return "INVALID"
    return "CANDIDATE" if pref == p else "BASELINE"


def evaluate_quality_promotion(
    corpus: Mapping[str, Any],
    evidence_bundle: Mapping[str, Any] | None,
    *,
    evidence_verifier: EvidenceVerifier | None,
    case_binding_verifier: CaseBindingVerifier | None = None,
    candidate_evidence_verifier: CandidateEvidenceVerifier | None = None,
    judge_run_verifier: JudgeRunVerifier | None = None,
    regression_run_verifier: RegressionRunVerifier | None = None,
    promotion_scope: str = "GENERAL_EDITORIAL_QUALITY",
) -> QualityPromotionResult:
    readiness = evaluate_corpus_readiness(corpus, promotion_scope=promotion_scope)
    if readiness.status == "FAIL":
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), readiness.errors)
    if readiness.status != "PROMOTION_READY":
        return QualityPromotionResult("BLOCKED_NOT_READY", promotion_scope, (), (), (), (), tuple(f"missing_corpus_requirement:{x}" for x in readiness.missing_requirements))
    if evidence_bundle is None:
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), ("missing_quality_evidence_bundle",))
    required_verifiers = [
        (evidence_verifier, "evidence_verifier_required"),
        (case_binding_verifier, "case_binding_verifier_required"),
        (candidate_evidence_verifier, "candidate_evidence_semantic_verifier_required"),
        (judge_run_verifier, "judge_run_semantic_verifier_required"),
        (regression_run_verifier, "hard_regression_run_verifier_required"),
    ]
    missing_verifiers = tuple(error for verifier, error in required_verifiers if verifier is None)
    if missing_verifiers:
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), missing_verifiers)
    assert evidence_verifier is not None
    assert case_binding_verifier is not None
    assert candidate_evidence_verifier is not None
    assert judge_run_verifier is not None
    assert regression_run_verifier is not None

    package = evidence_bundle.get("candidate_distillation")
    distilled = evaluate_candidate_distillation(
        corpus,
        package,
        evidence_verifier=evidence_verifier,
        candidate_evidence_verifier=candidate_evidence_verifier,
        promotion_scope=promotion_scope,
    )
    if distilled.status != "PASS":
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), tuple(f"candidate_distillation:{x}" for x in distilled.errors))
    assert isinstance(package, Mapping)

    modes = set(distilled.target_content_modes)
    cases = {
        str(c["case_id"]): c
        for c in corpus["cases"]
        if c.get("evidence_status") == "COMPLETE"
        and c.get("split") in {"REGRESSION", "HELD_OUT"}
        and str(c.get("content_mode", "")).strip() in modes
    }
    errors: list[str] = []
    for case_id, case in cases.items():
        bindings = case.get("artifact_bindings")
        if not isinstance(bindings, list) or not bindings:
            errors.append(f"promotion_case_missing_artifact_bindings:{case_id}")
            continue
        for binding in bindings:
            if not isinstance(binding, Mapping) or not _semantic_verified(case_binding_verifier, case, binding):
                errors.append(f"unverified_case_artifact_binding:{case_id}")

    hard = evidence_bundle.get("hard_invariant_regressions")
    if not isinstance(hard, list):
        errors.append("invalid_hard_invariant_regressions")
    elif hard:
        errors.extend(f"hard_invariant_regression:{x}" for x in hard)

    regression = evidence_bundle.get("hard_invariant_regression_run")
    expected_id = distilled.candidate_id or ""
    expected_change = str(package.get("candidate_change_ref", "")).strip()
    if not isinstance(regression, Mapping):
        errors.append("missing_hard_invariant_regression_run")
    else:
        if str(regression.get("candidate_id", "")).strip() != expected_id:
            errors.append("hard_regression_candidate_mismatch")
        if str(regression.get("candidate_change_ref", "")).strip() != expected_change:
            errors.append("hard_regression_candidate_change_ref_mismatch")
        if str(regression.get("result", "")).strip() != "PASS":
            errors.append("hard_regression_result_not_pass")
        for field in ("execution_ref", "suite_ref"):
            ref = str(regression.get(field, "")).strip()
            if not ref:
                errors.append(f"hard_regression_missing_{field}")
            elif not _verified(ref, evidence_verifier):
                errors.append(f"hard_regression_unverified_{field}:{ref}")
        refs = regression.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            errors.append("hard_regression_missing_evidence_refs")
        else:
            for ref in refs:
                if not isinstance(ref, str) or not ref.strip() or not _verified(ref.strip(), evidence_verifier):
                    errors.append(f"hard_regression_unverified_evidence_ref:{ref}")
        if not errors and not _semantic_verified(regression_run_verifier, regression, package):
            errors.append("hard_regression_run_semantics_not_verified")

    runs = evidence_bundle.get("judge_runs")
    if not isinstance(runs, list):
        errors.append("missing_or_invalid_judge_runs")
        runs = []
    grouped: dict[str, dict[str, str]] = {cid: {} for cid in cases}
    seen_exec: set[str] = set()

    for i, run in enumerate(runs):
        if not isinstance(run, Mapping):
            errors.append(f"judge_run_not_object:{i}")
            continue
        case_id = str(run.get("case_id", "")).strip()
        if case_id not in cases:
            errors.append(f"unknown_or_nonpromotion_case:{case_id or i}")
            continue
        if run.get("blind") is not True:
            errors.append(f"judge_run_not_blind:{case_id}")
        if not str(run.get("judge_identity", "")).strip():
            errors.append(f"missing_judge_identity:{case_id}")
        exec_ref = str(run.get("execution_ref", "")).strip()
        if not exec_ref:
            errors.append(f"missing_execution_ref:{case_id}")
        else:
            if not _verified(exec_ref, evidence_verifier):
                errors.append(f"unverified_execution_ref:{exec_ref}")
            if exec_ref in seen_exec:
                errors.append(f"duplicate_execution_ref:{case_id}:{exec_ref}")
            seen_exec.add(exec_ref)
        run_id = str(run.get("candidate_id", "")).strip()
        run_change = str(run.get("candidate_change_ref", "")).strip()
        if run_id != expected_id:
            errors.append(f"judge_run_candidate_mismatch:{case_id}:observed={run_id or 'MISSING'}:expected={expected_id or 'MISSING'}")
        if run_change != expected_change:
            errors.append(f"judge_run_candidate_change_ref_mismatch:{case_id}:observed={run_change or 'MISSING'}:expected={expected_change or 'MISSING'}")
        refs = run.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"missing_evidence_refs:{case_id}")
        else:
            for ref in refs:
                if not isinstance(ref, str) or not ref.strip() or not _verified(ref.strip(), evidence_verifier):
                    errors.append(f"unverified_evidence_ref:{case_id}:{ref}")
        position = str(run.get("candidate_position", "")).upper()
        outcome = _normalized(position, str(run.get("preference", "")))
        if outcome == "INVALID":
            errors.append(f"invalid_pairwise_preference:{case_id}:{position}:{run.get('preference')}")
            continue
        if not _semantic_verified(judge_run_verifier, run, package, cases[case_id]):
            errors.append(f"unverified_judge_run_semantics:{case_id}:{position or i}")
        if position in grouped[case_id]:
            errors.append(f"duplicate_candidate_position:{case_id}:{position}")
        else:
            grouped[case_id][position] = outcome
    if errors:
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), tuple(errors))

    wins: list[str] = []
    ties: list[str] = []
    losses: list[str] = []
    evaluated: list[str] = []
    for case_id, case in cases.items():
        outcomes = grouped.get(case_id, {})
        if set(outcomes) != {"A", "B"}:
            errors.append(f"position_swap_required:{case_id}")
            continue
        if outcomes["A"] != outcomes["B"]:
            errors.append(f"position_swap_instability:{case_id}:{outcomes['A']}:{outcomes['B']}")
            continue
        outcome = outcomes["A"]
        evaluated.append(case_id)
        (wins if outcome == "CANDIDATE" else losses if outcome == "BASELINE" else ties).append(case_id)
        if case.get("source_kind") == "REAL_USER_REJECTION" and outcome != "CANDIDATE":
            errors.append(f"known_rejection_not_improved:{case_id}:{outcome}")
        if case.get("source_kind") in {"REAL_USER_ACCEPTANCE", "POST_PUBLICATION_PERFORMANCE"} and outcome == "BASELINE":
            errors.append(f"positive_anchor_regressed:{case_id}")
        if case.get("split") == "HELD_OUT" and outcome == "BASELINE":
            errors.append(f"held_out_regression:{case_id}")
    heldout = {cid for cid, case in cases.items() if case.get("split") == "HELD_OUT"}
    if heldout and not heldout.intersection(wins):
        errors.append("held_out_has_no_candidate_win")
    return QualityPromotionResult("PASS" if not errors else "FAIL", promotion_scope, tuple(evaluated), tuple(wins), tuple(ties), tuple(losses), tuple(errors))
