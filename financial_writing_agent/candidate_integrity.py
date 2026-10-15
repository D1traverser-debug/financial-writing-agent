from __future__ import annotations

from typing import Any, Mapping

from .authoritative_state import _json_type_strict_equal
from .workflow_spec import REVIEW_STAGE_NAMES, invalidated_stage_names_from


class CandidateIntegrityError(ValueError):
    pass


TRANSITION_MUTABLE_TOP_LEVEL = frozenset(
    {
        "status",
        "current_stage",
        "next_action",
        "stage_artifacts",
        "review_decisions",
        "delivery_artifacts",
        "quality_evidence",
        "execution_receipts",
        "updated_at",
    }
)

FEEDBACK_MUTABLE_TOP_LEVEL = frozenset(
    {
        "learning_evidence",
        "open_system_impact",
        "execution_receipts",
        "updated_at",
    }
)

LEGACY_MIGRATION_MUTABLE_TOP_LEVEL = frozenset(
    {
        "schema_version",
        "state_ref",
        "target_platforms",
        "distribution_mode_source",
        "delivery_channel",
        "required_outputs",
        "delivery_artifacts",
    }
)

KNOWN_QUALITY_KEYS = frozenset(
    {
        "research_decision",
        "story_blueprints",
        "publication_fitnesses",
    }
)

QUALITY_KEY_BY_STAGE = {
    "RESEARCH": "research_decision",
    "EDITORIAL": "story_blueprints",
    "EDITORIAL_AUDIT": "publication_fitnesses",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise CandidateIntegrityError(message)


def _strict_equal(left: Any, right: Any, message: str) -> None:
    _require(_json_type_strict_equal(left, right), message)


def _mapping(value: Any, *, label: str) -> Mapping[str, Any]:
    _require(isinstance(value, Mapping), f"{label} must be a mapping")
    return value


def _list(value: Any, *, label: str) -> list[Any]:
    _require(isinstance(value, list), f"{label} must be a list")
    return value


def _validate_immutable_by_default(
    before: Mapping[str, Any],
    after: Mapping[str, Any],
    *,
    mutable_fields: frozenset[str],
    action_label: str,
) -> None:
    """Require every field not owned by this action to remain type-strictly identical."""
    if before.get("schema_version") == "1.1":
        mutable_fields = mutable_fields | LEGACY_MIGRATION_MUTABLE_TOP_LEVEL
    all_fields = set(before) | set(after)
    for field in sorted(all_fields - mutable_fields):
        _require(field in before, f"{action_label} cannot inject unowned state field: {field}")
        _require(field in after, f"{action_label} cannot delete immutable state field: {field}")
        _strict_equal(
            before[field],
            after[field],
            f"{action_label} cannot mutate immutable state field: {field}",
        )


def _validate_mapping_delta(
    before_value: Any,
    after_value: Any,
    *,
    mutable_keys: set[str],
    label: str,
) -> None:
    before = _mapping(before_value, label=f"before.{label}")
    after = _mapping(after_value, label=f"after.{label}")
    all_keys = set(before) | set(after)
    for key in sorted(all_keys - mutable_keys):
        _require(key in before, f"{label} cannot inject unowned key: {key}")
        _require(key in after, f"{label} cannot delete immutable key: {key}")
        _strict_equal(before[key], after[key], f"{label} cannot rewrite immutable key: {key}")
    for key in set(after) - set(before):
        _require(key in mutable_keys, f"{label} cannot inject unowned key: {key}")
    for key in set(before) - set(after):
        _require(key in mutable_keys, f"{label} cannot delete immutable key: {key}")


def _last_receipt(after: Mapping[str, Any]) -> Mapping[str, Any]:
    receipts = _list(after.get("execution_receipts"), label="after.execution_receipts")
    _require(bool(receipts), "transition candidate requires an execution receipt")
    return _mapping(receipts[-1], label="after.execution_receipts[-1]")


def _transition_context(before: Mapping[str, Any], after: Mapping[str, Any]) -> tuple[str, str | None, str | None]:
    stage = str(before.get("current_stage", ""))
    receipt = _last_receipt(after)
    bindings = _mapping(receipt.get("input_bindings"), label="transition receipt input_bindings")
    review_status = bindings.get("review_status")
    revision_target = bindings.get("revision_target")
    return (
        stage,
        str(review_status) if review_status is not None else None,
        str(revision_target) if revision_target is not None else None,
    )


def _invalidated_names(revision_target: str | None) -> set[str]:
    if not revision_target:
        return set()
    try:
        return set(invalidated_stage_names_from(revision_target))
    except ValueError as exc:
        raise CandidateIntegrityError(str(exc)) from exc


def _validate_stage_artifact_delta(
    before: Mapping[str, Any], after: Mapping[str, Any], *, stage: str, review_status: str | None, revision_target: str | None
) -> None:
    before_artifacts = _mapping(before.get("stage_artifacts", {}), label="before.stage_artifacts")
    after_artifacts = _mapping(after.get("stage_artifacts", {}), label="after.stage_artifacts")
    if review_status == "REVISE" and revision_target:
        invalidated = _invalidated_names(revision_target)
        expected = {key: value for key, value in before_artifacts.items() if key not in invalidated}
        _strict_equal(expected, dict(after_artifacts), "stage_artifacts must equal the canonical revision invalidation result")
        return
    mutable = {stage} if stage != "INTAKE" else set()
    _validate_mapping_delta(before_artifacts, after_artifacts, mutable_keys=mutable, label="stage_artifacts")


def _validate_review_delta(
    before: Mapping[str, Any], after: Mapping[str, Any], *, stage: str, review_status: str | None, revision_target: str | None
) -> None:
    before_reviews = _mapping(before.get("review_decisions", {}), label="before.review_decisions")
    after_reviews = _mapping(after.get("review_decisions", {}), label="after.review_decisions")
    if stage not in REVIEW_STAGE_NAMES:
        _strict_equal(dict(before_reviews), dict(after_reviews), "non-review transition cannot mutate review_decisions")
        return
    if review_status == "REVISE" and revision_target:
        invalidated = _invalidated_names(revision_target)
        expected = {key: value for key, value in before_reviews.items() if key not in invalidated}
        _strict_equal(expected, dict(after_reviews), "review_decisions must equal the canonical revision invalidation result")
        return
    _validate_mapping_delta(before_reviews, after_reviews, mutable_keys={stage}, label="review_decisions")


def _apply_quality_invalidation(value: Mapping[str, Any], revision_target: str) -> dict[str, Any]:
    expected = dict(value)
    if revision_target == "RESEARCH":
        expected.clear()
    elif revision_target == "EDITORIAL":
        expected.pop("story_blueprints", None)
        expected.pop("publication_fitnesses", None)
    elif revision_target in {"TITLE", "DRAFT"}:
        expected.pop("publication_fitnesses", None)
    return expected


def _validate_quality_delta(
    before: Mapping[str, Any], after: Mapping[str, Any], *, stage: str, review_status: str | None, revision_target: str | None
) -> None:
    if before.get("schema_version") != "1.3":
        _strict_equal(before.get("quality_evidence"), after.get("quality_evidence"), "historical transition cannot mutate quality_evidence")
        return
    before_quality = _mapping(before.get("quality_evidence", {}), label="before.quality_evidence")
    after_quality = _mapping(after.get("quality_evidence", {}), label="after.quality_evidence")
    unknown_before = set(before_quality) - KNOWN_QUALITY_KEYS
    unknown_after = set(after_quality) - KNOWN_QUALITY_KEYS
    _require(not unknown_before, f"before.quality_evidence contains unknown keys: {sorted(unknown_before)}")
    _require(not unknown_after, f"after.quality_evidence contains unknown keys: {sorted(unknown_after)}")
    if review_status == "REVISE" and revision_target:
        expected = _apply_quality_invalidation(before_quality, revision_target)
        _strict_equal(expected, dict(after_quality), "quality_evidence must equal the canonical revision invalidation result")
        return
    mutable: set[str] = set()
    if stage == "RESEARCH":
        mutable.add("research_decision")
    elif stage == "EDITORIAL":
        mutable.add("story_blueprints")
    elif stage == "EDITORIAL_AUDIT" and review_status == "PASS":
        mutable.add("publication_fitnesses")
    _validate_mapping_delta(before_quality, after_quality, mutable_keys=mutable, label="quality_evidence")


def _validate_delivery_delta(
    before: Mapping[str, Any], after: Mapping[str, Any], *, stage: str, review_status: str | None, revision_target: str | None
) -> None:
    before_delivery = _mapping(before.get("delivery_artifacts", {}), label="before.delivery_artifacts")
    after_delivery = _mapping(after.get("delivery_artifacts", {}), label="after.delivery_artifacts")
    if review_status == "REVISE" and revision_target and "DELIVERY" in _invalidated_names(revision_target):
        _strict_equal({}, dict(after_delivery), "delivery_artifacts must clear when revision invalidates DELIVERY")
        return
    if stage == "DELIVERY":
        return  # Owner core validates the exact required article-output contract.
    if stage == "FINAL_AUDIT" and review_status == "PASS":
        _validate_mapping_delta(before_delivery, after_delivery, mutable_keys={"AUDIT_DOCX"}, label="delivery_artifacts")
        return
    _strict_equal(dict(before_delivery), dict(after_delivery), "transition cannot mutate delivery_artifacts at this stage")


def validate_transition_candidate_isolation(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    _validate_immutable_by_default(
        before,
        after,
        mutable_fields=TRANSITION_MUTABLE_TOP_LEVEL,
        action_label="transition candidate",
    )
    stage, review_status, revision_target = _transition_context(before, after)
    _validate_stage_artifact_delta(
        before,
        after,
        stage=stage,
        review_status=review_status,
        revision_target=revision_target,
    )
    _validate_review_delta(
        before,
        after,
        stage=stage,
        review_status=review_status,
        revision_target=revision_target,
    )
    _validate_quality_delta(
        before,
        after,
        stage=stage,
        review_status=review_status,
        revision_target=revision_target,
    )
    _validate_delivery_delta(
        before,
        after,
        stage=stage,
        review_status=review_status,
        revision_target=revision_target,
    )


def _validate_append_one(before_value: Any, after_value: Any, *, label: str) -> tuple[Any, Any]:
    before = _list(before_value, label=f"before.{label}")
    after = _list(after_value, label=f"after.{label}")
    _require(len(after) == len(before) + 1, f"{label} mutation must append exactly one item")
    _strict_equal(before, after[:-1], f"{label} mutation cannot rewrite prior history")
    return after[-1], before


def _validate_feedback_append_semantics(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    sample, _ = _validate_append_one(
        before.get("learning_evidence", []),
        after.get("learning_evidence", []),
        label="learning_evidence",
    )
    impact, _ = _validate_append_one(
        before.get("open_system_impact", []),
        after.get("open_system_impact", []),
        label="open_system_impact",
    )
    sample_map = _mapping(sample, label="appended learning_evidence")
    impact_map = _mapping(impact, label="appended open_system_impact")
    sample_type = sample_map.get("sample_type")
    _require(sample_type in {"USER_EDIT", "USER_FEEDBACK", "USER_REJECTION"}, "appended learning sample_type is invalid")
    summary = sample_map.get("summary")
    _require(isinstance(summary, str) and bool(summary.strip()), "appended learning summary is required")
    signal_id = impact_map.get("signal_id")
    _require(isinstance(signal_id, str) and bool(signal_id.strip()), "appended system-impact signal_id is required")
    _require(impact_map.get("status") == "OPEN", "appended system-impact status must be OPEN")
    _require(impact_map.get("trigger_sample_type") == sample_type, "appended system-impact trigger_sample_type mismatch")

    receipt = _last_receipt(after)
    subject = _mapping(receipt.get("subject_bindings"), label="feedback receipt subject_bindings")
    bindings = _mapping(receipt.get("input_bindings"), label="feedback receipt input_bindings")
    _require(subject.get("sample_type") == sample_type, "feedback receipt sample_type does not bind appended sample")
    _require(subject.get("signal_id") == signal_id, "feedback receipt signal_id does not bind appended system-impact")
    _require(bindings.get("feedback_summary") == summary, "feedback receipt summary does not bind appended sample")
    _require(bindings.get("signal_status") == "OPEN", "feedback receipt signal_status does not bind appended system-impact")


def validate_feedback_candidate_isolation(before: Mapping[str, Any], after: Mapping[str, Any]) -> None:
    _validate_immutable_by_default(
        before,
        after,
        mutable_fields=FEEDBACK_MUTABLE_TOP_LEVEL,
        action_label="feedback mutation",
    )
    _validate_feedback_append_semantics(before, after)
