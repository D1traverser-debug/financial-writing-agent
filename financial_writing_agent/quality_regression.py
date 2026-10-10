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

    This function validates externally produced blind pairwise evidence; it does not judge prose
    itself. Personalized claims require user-specific positive evidence, while general editorial
    improvements do not wait for the user to act as the optimizer or maintenance operator.
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

    complete_cases = {
        str(case["case_id"]): case
        for case in corpus["cases"]
        if case.get("evidence_status") == "COMPLETE"
        and case.get("split") in {"REGRESSION", "HELD_OUT"}
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
