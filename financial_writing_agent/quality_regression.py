from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping


EvidenceVerifier = Callable[[str], bool]


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


_ALLOWED_SOURCE_KINDS = {
    "REAL_USER_REJECTION",
    "REAL_USER_ACCEPTANCE",
    "POST_PUBLICATION_PERFORMANCE",
    "EXTERNAL_BENCHMARK",
}
_ALLOWED_SPLITS = {"CALIBRATION", "REGRESSION", "HELD_OUT"}
_ALLOWED_EVIDENCE_STATUS = {"PARTIAL", "COMPLETE"}
_ALLOWED_PROMOTION_SCOPES = {"GENERAL_EDITORIAL_QUALITY", "PERSONALIZED_WRITING_DNA"}
_ALLOWED_CONTENT_MODES = {"FINANCE_DEEP", "FINANCE_BROAD"}


def evaluate_corpus_readiness(
    corpus: Mapping[str, Any],
    *,
    promotion_scope: str = "GENERAL_EDITORIAL_QUALITY",
) -> CorpusReadinessResult:
    """Validate owner-local quality evidence without making the user the maintenance operator.

    GENERAL_EDITORIAL_QUALITY may improve from real failures plus diverse held-out evidence without
    waiting for a personalized positive label. PERSONALIZED_WRITING_DNA is stricter: claiming a
    user-specific preference additionally requires real acceptance or post-publication performance.
    """

    if promotion_scope not in _ALLOWED_PROMOTION_SCOPES:
        return CorpusReadinessResult(
            "FAIL", promotion_scope, (), (), (), (f"invalid_promotion_scope:{promotion_scope}",)
        )

    raw_cases = corpus.get("cases")
    if not isinstance(raw_cases, list):
        return CorpusReadinessResult("FAIL", promotion_scope, (), (), (), ("missing_or_invalid_cases",))

    errors: list[str] = []
    case_ids: list[str] = []
    complete_case_ids: list[str] = []
    seen_ids: set[str] = set()
    complete_cases: list[Mapping[str, Any]] = []

    for index, raw in enumerate(raw_cases):
        if not isinstance(raw, Mapping):
            errors.append(f"case_not_object:{index}")
            continue

        case_id = str(raw.get("case_id", "")).strip()
        if not case_id:
            errors.append(f"missing_case_id:{index}")
            continue
        if case_id in seen_ids:
            errors.append(f"duplicate_case_id:{case_id}")
            continue
        seen_ids.add(case_id)
        case_ids.append(case_id)

        source_kind = str(raw.get("source_kind", "")).strip()
        split = str(raw.get("split", "")).strip()
        evidence_status = str(raw.get("evidence_status", "")).strip()
        topic_family = str(raw.get("topic_family", "")).strip()
        artifact_refs = raw.get("artifact_refs")

        if source_kind not in _ALLOWED_SOURCE_KINDS:
            errors.append(f"invalid_source_kind:{case_id}:{source_kind}")
        if split not in _ALLOWED_SPLITS:
            errors.append(f"invalid_split:{case_id}:{split}")
        if evidence_status not in _ALLOWED_EVIDENCE_STATUS:
            errors.append(f"invalid_evidence_status:{case_id}:{evidence_status}")
        if not topic_family:
            errors.append(f"missing_topic_family:{case_id}")
        if not isinstance(artifact_refs, list):
            errors.append(f"invalid_artifact_refs:{case_id}")
            artifact_refs = []

        if evidence_status == "COMPLETE":
            if not artifact_refs or not all(isinstance(ref, str) and ref.strip() for ref in artifact_refs):
                errors.append(f"complete_case_missing_artifact_refs:{case_id}")
            else:
                complete_case_ids.append(case_id)
                complete_cases.append(raw)

    if errors:
        return CorpusReadinessResult(
            "FAIL",
            promotion_scope,
            tuple(case_ids),
            tuple(complete_case_ids),
            (),
            tuple(errors),
        )

    missing: list[str] = []
    complete_rejections = [c for c in complete_cases if c.get("source_kind") == "REAL_USER_REJECTION"]
    complete_positive = [
        c
        for c in complete_cases
        if c.get("source_kind") in {"REAL_USER_ACCEPTANCE", "POST_PUBLICATION_PERFORMANCE"}
    ]
    complete_heldout = [c for c in complete_cases if c.get("split") == "HELD_OUT"]
    topic_families = {str(c.get("topic_family", "")).strip() for c in complete_cases}

    if not complete_rejections:
        missing.append("complete_real_user_rejection_case")
    if not complete_heldout:
        missing.append("complete_held_out_case")
    if len(topic_families) < 2:
        missing.append("at_least_two_complete_topic_families")
    if promotion_scope == "PERSONALIZED_WRITING_DNA" and not complete_positive:
        missing.append("complete_positive_anchor_or_performance_case")

    return CorpusReadinessResult(
        "PROMOTION_READY" if not missing else "NOT_READY",
        promotion_scope,
        tuple(case_ids),
        tuple(complete_case_ids),
        tuple(missing),
        (),
    )


def _verify_ref(ref: str, evidence_verifier: EvidenceVerifier, errors: list[str], label: str) -> None:
    try:
        verified = bool(evidence_verifier(ref))
    except Exception:
        verified = False
    if not verified:
        errors.append(f"unverified_{label}:{ref}")


def evaluate_candidate_distillation(
    corpus: Mapping[str, Any],
    package: Mapping[str, Any] | None,
    *,
    evidence_verifier: EvidenceVerifier | None,
    promotion_scope: str = "GENERAL_EDITORIAL_QUALITY",
) -> CandidateDistillationResult:
    """Validate that a quality candidate was distilled rather than directly canonicalized.

    The package is process evidence, not prose guidance. It must connect a real failure to a
    root-cause hypothesis, compare at least two mechanisms, search failure modes/counterexamples,
    choose a bounded authority surface, and provide independently verifiable refs. Promotion is
    additionally scoped to content modes that have both real-rejection and held-out coverage so a
    FINANCE_DEEP fix cannot silently claim FINANCE_BROAD improvement.
    """

    if package is None:
        return CandidateDistillationResult("FAIL", None, (), ("missing_candidate_distillation",))
    if not isinstance(package, Mapping):
        return CandidateDistillationResult("FAIL", None, (), ("invalid_candidate_distillation",))
    if evidence_verifier is None:
        return CandidateDistillationResult("FAIL", None, (), ("independent_evidence_verifier_required",))

    errors: list[str] = []
    candidate_id = str(package.get("candidate_id", "")).strip()
    if not candidate_id:
        errors.append("missing_candidate_id")

    observed_scope = str(package.get("promotion_scope", "")).strip()
    if observed_scope != promotion_scope:
        errors.append(f"candidate_promotion_scope_mismatch:observed={observed_scope or 'MISSING'}:expected={promotion_scope}")

    for field in ("problem_statement", "root_cause_hypothesis", "selection_rationale", "superseded_mechanism_disposition"):
        if not str(package.get(field, "")).strip():
            errors.append(f"missing_{field}")

    raw_modes = package.get("target_content_modes")
    target_modes = (
        tuple(dict.fromkeys(str(mode).strip() for mode in raw_modes if isinstance(mode, str) and str(mode).strip()))
        if isinstance(raw_modes, list)
        else ()
    )
    if not target_modes:
        errors.append("missing_target_content_modes")
    for mode in target_modes:
        if mode not in _ALLOWED_CONTENT_MODES:
            errors.append(f"invalid_target_content_mode:{mode}")

    raw_source_case_ids = package.get("source_case_ids")
    source_case_ids = (
        tuple(dict.fromkeys(str(case_id).strip() for case_id in raw_source_case_ids if isinstance(case_id, str) and str(case_id).strip()))
        if isinstance(raw_source_case_ids, list)
        else ()
    )
    if not source_case_ids:
        errors.append("missing_source_case_ids")

    raw_cases = corpus.get("cases")
    complete_cases: dict[str, Mapping[str, Any]] = {}
    if isinstance(raw_cases, list):
        for raw in raw_cases:
            if isinstance(raw, Mapping) and raw.get("evidence_status") == "COMPLETE":
                case_id = str(raw.get("case_id", "")).strip()
                if case_id:
                    complete_cases[case_id] = raw
    else:
        errors.append("missing_or_invalid_cases")

    for case_id in source_case_ids:
        if case_id not in complete_cases:
            errors.append(f"source_case_not_complete_or_unknown:{case_id}")
    if source_case_ids and not any(
        complete_cases.get(case_id, {}).get("source_kind") == "REAL_USER_REJECTION"
        for case_id in source_case_ids
    ):
        errors.append("source_cases_require_real_user_rejection")

    alternatives_raw = package.get("alternatives")
    alternatives = alternatives_raw if isinstance(alternatives_raw, list) else []
    if len(alternatives) < 2:
        errors.append("at_least_two_candidate_mechanisms_required")
    alternative_ids: list[str] = []
    for index, alternative in enumerate(alternatives):
        if not isinstance(alternative, Mapping):
            errors.append(f"candidate_mechanism_not_object:{index}")
            continue
        alternative_id = str(alternative.get("candidate_id", "")).strip()
        mechanism = str(alternative.get("mechanism", "")).strip()
        failure_modes = alternative.get("failure_modes")
        if not alternative_id:
            errors.append(f"candidate_mechanism_missing_id:{index}")
        elif alternative_id in alternative_ids:
            errors.append(f"duplicate_candidate_mechanism_id:{alternative_id}")
        else:
            alternative_ids.append(alternative_id)
        if not mechanism:
            errors.append(f"candidate_mechanism_missing_description:{alternative_id or index}")
        if not isinstance(failure_modes, list) or not any(isinstance(item, str) and item.strip() for item in failure_modes):
            errors.append(f"candidate_mechanism_missing_failure_mode:{alternative_id or index}")

    selected_candidate_id = str(package.get("selected_candidate_id", "")).strip()
    if not selected_candidate_id:
        errors.append("missing_selected_candidate_id")
    elif selected_candidate_id not in alternative_ids:
        errors.append(f"selected_candidate_not_in_alternatives:{selected_candidate_id}")
    if candidate_id and selected_candidate_id and candidate_id != selected_candidate_id:
        errors.append(f"candidate_id_selected_candidate_mismatch:{candidate_id}:{selected_candidate_id}")

    authority_surfaces = package.get("authority_surfaces")
    if not isinstance(authority_surfaces, list) or not any(
        isinstance(surface, str) and surface.strip() for surface in authority_surfaces
    ):
        errors.append("missing_authority_surfaces")

    candidate_change_ref = str(package.get("candidate_change_ref", "")).strip()
    if not candidate_change_ref:
        errors.append("missing_candidate_change_ref")
    else:
        _verify_ref(candidate_change_ref, evidence_verifier, errors, "candidate_change_ref")

    counterexample_refs = package.get("counterexample_evidence_refs")
    if not isinstance(counterexample_refs, list) or not any(
        isinstance(ref, str) and ref.strip() for ref in counterexample_refs
    ):
        errors.append("missing_counterexample_evidence_refs")
    else:
        for raw_ref in counterexample_refs:
            if isinstance(raw_ref, str) and raw_ref.strip():
                _verify_ref(raw_ref.strip(), evidence_verifier, errors, "counterexample_ref")

    # Mode-scoped negative-space: a candidate can only claim modes that have both a real failure
    # and held-out evidence. This prevents a FINANCE_DEEP regression corpus from silently
    # authorizing a FINANCE_BROAD quality claim.
    for mode in target_modes:
        mode_cases = [case for case in complete_cases.values() if str(case.get("content_mode", "")).strip() == mode]
        if not any(case.get("source_kind") == "REAL_USER_REJECTION" for case in mode_cases):
            errors.append(f"target_mode_missing_real_rejection:{mode}")
        if not any(case.get("split") == "HELD_OUT" for case in mode_cases):
            errors.append(f"target_mode_missing_heldout:{mode}")

    return CandidateDistillationResult(
        "PASS" if not errors else "FAIL",
        candidate_id or None,
        target_modes,
        tuple(errors),
    )


def _normalize_preference(candidate_position: str, preference: str) -> str:
    candidate_position = candidate_position.upper()
    preference = preference.upper()
    if candidate_position not in {"A", "B"}:
        return "INVALID"
    if preference == "TIE":
        return "TIE"
    if preference not in {"A", "B"}:
        return "INVALID"
    return "CANDIDATE" if preference == candidate_position else "BASELINE"


def evaluate_quality_promotion(
    corpus: Mapping[str, Any],
    evidence_bundle: Mapping[str, Any] | None,
    *,
    evidence_verifier: EvidenceVerifier | None,
    promotion_scope: str = "GENERAL_EDITORIAL_QUALITY",
) -> QualityPromotionResult:
    """Fail-closed promotion gate for writing-quality changes.

    This function validates a distilled candidate plus externally produced blind pairwise evidence;
    it does not judge prose itself. Personalized claims require user-specific positive evidence,
    while general editorial improvements do not wait for the user to act as optimizer or maintainer.
    """

    readiness = evaluate_corpus_readiness(corpus, promotion_scope=promotion_scope)
    if readiness.status == "FAIL":
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), readiness.errors)
    if readiness.status != "PROMOTION_READY":
        return QualityPromotionResult(
            "BLOCKED_NOT_READY",
            promotion_scope,
            (),
            (),
            (),
            (),
            tuple(f"missing_corpus_requirement:{item}" for item in readiness.missing_requirements),
        )
    if evidence_bundle is None:
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), ("missing_quality_evidence_bundle",))
    if evidence_verifier is None:
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), ("independent_evidence_verifier_required",))

    distillation = evaluate_candidate_distillation(
        corpus,
        evidence_bundle.get("candidate_distillation"),
        evidence_verifier=evidence_verifier,
        promotion_scope=promotion_scope,
    )
    if distillation.status != "PASS":
        return QualityPromotionResult(
            "FAIL",
            promotion_scope,
            (),
            (),
            (),
            (),
            tuple(f"candidate_distillation:{error}" for error in distillation.errors),
        )

    hard_regressions = evidence_bundle.get("hard_invariant_regressions")
    if not isinstance(hard_regressions, list):
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), ("invalid_hard_invariant_regressions",))
    if hard_regressions:
        return QualityPromotionResult(
            "FAIL",
            promotion_scope,
            (),
            (),
            (),
            (),
            tuple(f"hard_invariant_regression:{item}" for item in hard_regressions),
        )

    judge_runs = evidence_bundle.get("judge_runs")
    if not isinstance(judge_runs, list):
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), ("missing_or_invalid_judge_runs",))

    target_modes = set(distillation.target_content_modes)
    complete_cases = {
        str(case["case_id"]): case
        for case in corpus["cases"]
        if case.get("evidence_status") == "COMPLETE"
        and case.get("split") in {"REGRESSION", "HELD_OUT"}
        and str(case.get("content_mode", "")).strip() in target_modes
    }
    grouped: dict[str, dict[str, str]] = {case_id: {} for case_id in complete_cases}
    errors: list[str] = []

    for index, run in enumerate(judge_runs):
        if not isinstance(run, Mapping):
            errors.append(f"judge_run_not_object:{index}")
            continue
        case_id = str(run.get("case_id", "")).strip()
        if case_id not in complete_cases:
            errors.append(f"unknown_or_nonpromotion_case:{case_id or index}")
            continue
        if run.get("blind") is not True:
            errors.append(f"judge_run_not_blind:{case_id}")
        judge_identity = str(run.get("judge_identity", "")).strip()
        execution_ref = str(run.get("execution_ref", "")).strip()
        if not judge_identity:
            errors.append(f"missing_judge_identity:{case_id}")
        if not execution_ref:
            errors.append(f"missing_execution_ref:{case_id}")

        refs = run.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"missing_evidence_refs:{case_id}")
        else:
            for ref in refs:
                if not isinstance(ref, str) or not ref.strip() or not evidence_verifier(ref):
                    errors.append(f"unverified_evidence_ref:{case_id}:{ref}")

        candidate_position = str(run.get("candidate_position", "")).upper()
        normalized = _normalize_preference(candidate_position, str(run.get("preference", "")))
        if normalized == "INVALID":
            errors.append(f"invalid_pairwise_preference:{case_id}:{candidate_position}:{run.get('preference')}")
            continue
        if candidate_position in grouped[case_id]:
            errors.append(f"duplicate_candidate_position:{case_id}:{candidate_position}")
        else:
            grouped[case_id][candidate_position] = normalized

    if errors:
        return QualityPromotionResult("FAIL", promotion_scope, (), (), (), (), tuple(errors))

    candidate_wins: list[str] = []
    ties: list[str] = []
    baseline_wins: list[str] = []
    evaluated: list[str] = []

    for case_id, case in complete_cases.items():
        outcomes = grouped.get(case_id, {})
        if set(outcomes) != {"A", "B"}:
            errors.append(f"position_swap_required:{case_id}")
            continue
        if outcomes["A"] != outcomes["B"]:
            errors.append(f"position_swap_instability:{case_id}:{outcomes['A']}:{outcomes['B']}")
            continue

        outcome = outcomes["A"]
        evaluated.append(case_id)
        if outcome == "CANDIDATE":
            candidate_wins.append(case_id)
        elif outcome == "BASELINE":
            baseline_wins.append(case_id)
        else:
            ties.append(case_id)

        source_kind = case.get("source_kind")
        split = case.get("split")
        if source_kind == "REAL_USER_REJECTION" and outcome != "CANDIDATE":
            errors.append(f"known_rejection_not_improved:{case_id}:{outcome}")
        if source_kind in {"REAL_USER_ACCEPTANCE", "POST_PUBLICATION_PERFORMANCE"} and outcome == "BASELINE":
            errors.append(f"positive_anchor_regressed:{case_id}")
        if split == "HELD_OUT" and outcome == "BASELINE":
            errors.append(f"held_out_regression:{case_id}")

    heldout_ids = {case_id for case_id, case in complete_cases.items() if case.get("split") == "HELD_OUT"}
    if heldout_ids and not heldout_ids.intersection(candidate_wins):
        errors.append("held_out_has_no_candidate_win")

    return QualityPromotionResult(
        "PASS" if not errors else "FAIL",
        promotion_scope,
        tuple(evaluated),
        tuple(candidate_wins),
        tuple(ties),
        tuple(baseline_wins),
        tuple(errors),
    )
